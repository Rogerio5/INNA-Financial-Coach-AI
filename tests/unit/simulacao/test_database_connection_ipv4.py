from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2
import pytest

from src.database import connection as database


FAKE_DATABASE_URL = (
    "postgresql://user:super-secret@"
    "db.example:5432/inna?sslmode=require"
)


@pytest.fixture(autouse=True)
def clear_ipv4_cache(
    monkeypatch,
):
    database._limpar_cache_ipv4()

    monkeypatch.setenv(
        "INNA_POSTGRES_NETWORK_FAMILY",
        "ipv4",
    )

    monkeypatch.setenv(
        "INNA_POSTGRES_CONNECT_TIMEOUT_SECONDS",
        "8",
    )

    monkeypatch.setenv(
        "INNA_POSTGRES_DNS_CACHE_TTL_SECONDS",
        "60",
    )

    monkeypatch.setattr(
        database,
        "obter_database_url",
        lambda obrigatoria=True: (
            FAKE_DATABASE_URL
        ),
    )

    yield

    database._limpar_cache_ipv4()


def _dns_result(
    *addresses: str,
):
    return [
        (
            database.socket.AF_INET,
            database.socket.SOCK_STREAM,
            6,
            "",
            (
                address,
                5432,
            ),
        )
        for address in addresses
    ]


def test_resolver_uses_only_ipv4_and_deduplicates(
    monkeypatch,
):
    getaddrinfo = MagicMock(
        return_value=_dns_result(
            "203.0.113.10",
            "203.0.113.10",
            "203.0.113.11",
        )
    )

    monkeypatch.setattr(
        database.socket,
        "getaddrinfo",
        getaddrinfo,
    )

    addresses = (
        database._resolver_enderecos_ipv4(
            "db.example",
            5432,
        )
    )

    assert addresses == (
        "203.0.113.10",
        "203.0.113.11",
    )

    getaddrinfo.assert_called_once_with(
        "db.example",
        5432,
        family=database.socket.AF_INET,
        type=database.socket.SOCK_STREAM,
    )


def test_dns_result_is_cached(
    monkeypatch,
):
    getaddrinfo = MagicMock(
        return_value=_dns_result(
            "203.0.113.10",
        )
    )

    monkeypatch.setattr(
        database.socket,
        "getaddrinfo",
        getaddrinfo,
    )

    first = (
        database._resolver_enderecos_ipv4(
            "db.example",
            5432,
        )
    )

    second = (
        database._resolver_enderecos_ipv4(
            "db.example",
            5432,
        )
    )

    assert first == second
    assert getaddrinfo.call_count == 1


def test_connection_preserves_hostname_and_uses_hostaddr(
    monkeypatch,
):
    monkeypatch.setattr(
        database.socket,
        "getaddrinfo",
        lambda *args, **kwargs: (
            _dns_result(
                "203.0.113.10",
            )
        ),
    )

    fake_connection = (
        SimpleNamespace(
            autocommit=None,
        )
    )

    connect = MagicMock(
        return_value=fake_connection
    )

    monkeypatch.setattr(
        psycopg2,
        "connect",
        connect,
    )

    result = database.criar_conexao(
        autocommit=True,
        connect_timeout=8,
    )

    assert result is fake_connection
    assert result.autocommit is True

    _, kwargs = connect.call_args

    assert kwargs["host"] == (
        "db.example"
    )

    assert kwargs["hostaddr"] == (
        "203.0.113.10"
    )

    assert kwargs["port"] == 5432

    assert (
        1
        <= kwargs["connect_timeout"]
        <= 3
    )


def test_connection_falls_back_to_next_ipv4(
    monkeypatch,
):
    monkeypatch.setattr(
        database.socket,
        "getaddrinfo",
        lambda *args, **kwargs: (
            _dns_result(
                "203.0.113.10",
                "203.0.113.11",
            )
        ),
    )

    fake_connection = (
        SimpleNamespace(
            autocommit=None,
        )
    )

    attempted_addresses = []

    def fake_connect(
        database_url,
        **kwargs,
    ):
        attempted_addresses.append(
            kwargs["hostaddr"]
        )

        if (
            kwargs["hostaddr"]
            == "203.0.113.10"
        ):
            raise RuntimeError(
                "primeiro endereço indisponível"
            )

        return fake_connection

    monkeypatch.setattr(
        psycopg2,
        "connect",
        fake_connect,
    )

    result = database.criar_conexao(
        connect_timeout=8,
    )

    assert result is fake_connection

    assert attempted_addresses == [
        "203.0.113.10",
        "203.0.113.11",
    ]


def test_system_policy_uses_default_libpq_resolution(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_POSTGRES_NETWORK_FAMILY",
        "system",
    )

    fake_connection = (
        SimpleNamespace(
            autocommit=None,
        )
    )

    connect = MagicMock(
        return_value=fake_connection
    )

    monkeypatch.setattr(
        psycopg2,
        "connect",
        connect,
    )

    result = database.criar_conexao(
        connect_timeout=8,
    )

    assert result is fake_connection

    _, kwargs = connect.call_args

    assert "hostaddr" not in kwargs
    assert kwargs["connect_timeout"] == 8


def test_connection_error_does_not_expose_credentials(
    monkeypatch,
):
    monkeypatch.setattr(
        database.socket,
        "getaddrinfo",
        lambda *args, **kwargs: (
            _dns_result(
                "203.0.113.10",
            )
        ),
    )

    monkeypatch.setattr(
        psycopg2,
        "connect",
        MagicMock(
            side_effect=RuntimeError(
                FAKE_DATABASE_URL
            )
        ),
    )

    with pytest.raises(
        database.DatabaseConnectionError
    ) as exc_info:
        database.criar_conexao(
            connect_timeout=2,
        )

    message = str(
        exc_info.value
    )

    assert "super-secret" not in message
    assert "postgresql://" not in message
    assert "db.example" not in message


def test_invalid_network_policy_is_rejected(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_POSTGRES_NETWORK_FAMILY",
        "invalid",
    )

    with pytest.raises(
        database.DatabaseConfigurationError
    ):
        database.criar_conexao()


def test_source_has_no_hardcoded_neon_ip():
    source = Path(
        "src/database/connection.py"
    ).read_text(
        encoding="utf-8",
    )

    assert "18.229.40.57" not in source
    assert "54.232.181.76" not in source
    assert "18.230.255.48" not in source

    assert (
        "ep-square-mode-"
        not in source
    )

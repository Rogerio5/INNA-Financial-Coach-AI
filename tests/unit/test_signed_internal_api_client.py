from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    verificar_requisicao_interna,
)
from src import api_client


SECRET = (
    "0123456789abcdef"
    "0123456789abcdef"
    "signed-client-test-secret"
)


class FakeResponse:
    status_code = 200
    content = b""

    def raise_for_status(
        self,
    ):
        return None

    def json(
        self,
    ):
        return {
            "id": 123,
            "status": "created",
        }


def test_prepared_body_is_canonical_and_signed(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    payload = {
        "z": 1,
        "texto": "olá",
        "a": 2,
    }

    body, headers, request_id = (
        api_client
        .preparar_requisicao_interna_json(
            method="POST",
            path="/diagnostico",
            payload=payload,
            usuario_id_confiavel=(
                "usuario@example.com"
            ),
            request_id=(
                "web-request-12345678"
            ),
            timestamp=1_700_000_000,
        )
    )

    assert body == (
        '{"a":2,"texto":"olá","z":1}'
        .encode(
            "utf-8"
        )
    )

    assert request_id == (
        "web-request-12345678"
    )

    assert headers[HEADER_USER_ID] == (
        "usuario@example.com"
    )

    context = verificar_requisicao_interna(
        method="POST",
        path="/diagnostico",
        user_id=headers[
            HEADER_USER_ID
        ],
        request_id=headers[
            HEADER_REQUEST_ID
        ],
        timestamp=headers[
            HEADER_TIMESTAMP
        ],
        signature=headers[
            HEADER_SIGNATURE
        ],
        body=body,
        secret=SECRET,
        now=1_700_000_000,
    )

    assert context.user_id == (
        "usuario@example.com"
    )


def test_generated_request_id_is_valid_and_unique():
    first = (
        api_client
        .gerar_request_id_interno()
    )

    second = (
        api_client
        .gerar_request_id_interno()
    )

    assert first != second

    assert re.fullmatch(
        r"web-[0-9a-f]{32}",
        first,
    )


def test_diagnosis_client_posts_exact_signed_body(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    captured = {}

    def fake_post(
        url,
        **kwargs,
    ):
        captured["url"] = url
        captured.update(
            kwargs
        )

        return FakeResponse()

    monkeypatch.setattr(
        api_client.requests,
        "post",
        fake_post,
    )

    result = (
        api_client
        .gerar_diagnostico_api(
            {
                "nome": "Teste",
                "renda_mensal": 3000,
            },
            usuario_id_confiavel=(
                "usuario@example.com"
            ),
            request_id=(
                "web-request-12345678"
            ),
        )
    )

    assert result["id"] == 123

    assert captured["url"].endswith(
        "/diagnostico"
    )

    assert "data" in captured
    assert "json" not in captured

    body = captured["data"]

    assert json.loads(
        body.decode(
            "utf-8"
        )
    ) == {
        "nome": "Teste",
        "renda_mensal": 3000,
    }

    assert captured["headers"][
        HEADER_USER_ID
    ] == "usuario@example.com"

    assert captured["headers"][
        HEADER_REQUEST_ID
    ] == "web-request-12345678"

    assert captured["timeout"] == 60


def test_diagnosis_client_does_not_mutate_payload(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    monkeypatch.setattr(
        api_client.requests,
        "post",
        MagicMock(
            return_value=FakeResponse()
        ),
    )

    payload = {
        "nome": "Teste",
        "renda_mensal": 3000,
    }

    original = dict(
        payload
    )

    api_client.gerar_diagnostico_api(
        payload,
        usuario_id_confiavel=(
            "usuario@example.com"
        ),
        request_id=(
            "web-request-12345678"
        ),
    )

    assert payload == original


def test_invalid_identity_prevents_network_call(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    post = MagicMock()

    monkeypatch.setattr(
        api_client.requests,
        "post",
        post,
    )

    with pytest.raises(
        api_client.InternalApiClientError
    ):
        api_client.gerar_diagnostico_api(
            {
                "nome": "Teste",
            },
            usuario_id_confiavel=(
                "identidade com espaços"
            ),
        )

    post.assert_not_called()


def test_missing_secret_is_sanitized(
    monkeypatch,
):
    monkeypatch.delenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        raising=False,
    )

    with pytest.raises(
        api_client.InternalApiClientError
    ) as exc_info:
        (
            api_client
            .preparar_requisicao_interna_json(
                method="POST",
                path="/diagnostico",
                payload={
                    "nome": "Teste",
                },
                usuario_id_confiavel=(
                    "usuario@example.com"
                ),
                request_id=(
                    "web-request-12345678"
                ),
                timestamp=1_700_000_000,
            )
        )

    message = str(
        exc_info.value
    )

    assert "secret" not in message.lower()
    assert "assinatura interna" not in message


def test_non_finite_payload_is_rejected(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    with pytest.raises(
        api_client.InternalApiClientError
    ):
        (
            api_client
            .preparar_requisicao_interna_json(
                method="POST",
                path="/diagnostico",
                payload={
                    "renda_mensal": (
                        float("nan")
                    ),
                },
                usuario_id_confiavel=(
                    "usuario@example.com"
                ),
            )
        )


def test_app_passes_authenticated_session_identity():
    source = Path(
        "src/app.py"
    ).read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source
    )

    calls = [
        node
        for node
        in ast.walk(
            tree
        )
        if isinstance(
            node,
            ast.Call,
        )
        and isinstance(
            node.func,
            ast.Name,
        )
        and node.func.id
        == "gerar_diagnostico_api"
    ]

    assert len(calls) == 1

    keyword_names = {
        keyword.arg
        for keyword
        in calls[0].keywords
    }

    assert (
        "usuario_id_confiavel"
        in keyword_names
    )


def test_app_has_no_unsigned_diagnosis_call():
    source = Path(
        "src/app.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "gerar_diagnostico_api(payload)"
        not in source
    )

    assert (
        'st.session_state.get(\n'
        '            "usuario"'
        in source
    )

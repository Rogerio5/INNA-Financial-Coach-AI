from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime

import pytest

from src.services.financial_diagnosis import (
    FinancialDiagnosisPersistenceCommand,
    FinancialDiagnosisRecord,
    TrustedDiagnosisPersistenceContext,
)
from src.services.financial_diagnosis import (
    repository,
)


FINGERPRINT_OTHER = "b" * 64


class FakeCursor:
    def __init__(
        self,
        *,
        fetchone_results=None,
        fail_on_execute: int | None = None,
        failure: Exception | None = None,
    ):
        self.fetchone_results = list(fetchone_results or [])

        self.fail_on_execute = fail_on_execute

        self.failure = failure or RuntimeError("database failure")

        self.calls = []

    def execute(
        self,
        sql,
        parameters=None,
    ):
        self.calls.append(
            (
                sql,
                parameters,
            )
        )

        if self.fail_on_execute == len(self.calls):
            raise self.failure

    def fetchone(
        self,
    ):
        if not self.fetchone_results:
            return None

        return self.fetchone_results.pop(0)


def _command(
    **diagnosis_overrides,
):
    diagnosis = {
        "nome": "Usuário Teste",
        "renda_mensal": 4000,
        "gastos_fixos": 1800,
        "gastos_variaveis": 700,
        "dividas_mensais": 300,
        "reserva_atual": 2000,
        "objetivo": "Organizar as finanças",
        "idioma": "pt",
        "moeda": "BRL",
        "simbolo_moeda": "R$",
        "saldo_estimado": 1200,
        ("comprometimento_renda_percentual"): 70,
        "meses_reserva_estimados": 0.714286,
        "score_financeiro": 70,
        "nivel_risco": "Medio",
        "diagnostico": ("Diagnóstico financeiro validado."),
        "plano_30_dias": ("Plano financeiro de trinta dias."),
    }

    diagnosis.update(diagnosis_overrides)

    return FinancialDiagnosisPersistenceCommand(
        context=(
            TrustedDiagnosisPersistenceContext(
                usuario_id="user-123",
                idempotency_key=("diagnosis:request-123456"),
            )
        ),
        diagnosis=FinancialDiagnosisRecord(**diagnosis),
    )


def _install_fake_cursor(
    monkeypatch,
    cursor,
):
    captured = {}

    @contextmanager
    def fake_cursor_postgres(
        **kwargs,
    ):
        captured["kwargs"] = kwargs
        yield cursor

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    return captured


def _row(
    fingerprint: str,
    *,
    identifier: int = 101,
):
    return {
        "id": identifier,
        "data_hora": datetime(
            2026,
            7,
            18,
            3,
            30,
        ),
        "request_fingerprint": (fingerprint),
    }


def _normalized_sql(
    sql: str,
) -> str:
    return " ".join(sql.lower().split())


def test_repository_creates_new_diagnosis(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(fetchone_results=[_row(command.request_fingerprint)])

    captured = _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.salvar_diagnostico_financeiro(command)

    assert result.id == 101
    assert result.status == "created"
    assert result.created is True

    assert captured["kwargs"] == {
        "dict_cursor": True,
        "commit_automatico": True,
    }


def test_insert_uses_explicit_columns_and_parameters(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(fetchone_results=[_row(command.request_fingerprint)])

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    repository.salvar_diagnostico_financeiro(command)

    assert len(cursor.calls) == 3

    sql, parameters = cursor.calls[2]
    normalized = _normalized_sql(sql)

    assert "insert into public.diagnosticos_financeiros" in normalized

    assert "select *" not in normalized
    assert "now()" in normalized

    assert "on conflict ( usuario_id, idempotency_key )" in normalized

    assert "returning id, data_hora, request_fingerprint" in normalized

    assert parameters["usuario_id"] == ("user-123")

    assert parameters["idempotency_key"] == ("diagnosis:request-123456")

    assert parameters["request_fingerprint"] == command.request_fingerprint

    assert "id" not in parameters
    assert "data_hora" not in parameters


def test_repository_returns_existing_for_same_request(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(
        fetchone_results=[
            None,
            _row(
                command.request_fingerprint,
                identifier=77,
            ),
        ]
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.salvar_diagnostico_financeiro(command)

    assert result.id == 77
    assert result.status == "existing"
    assert result.created is False
    assert len(cursor.calls) == 4


def test_existing_lookup_uses_only_trusted_identity(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(
        fetchone_results=[
            None,
            _row(command.request_fingerprint),
        ]
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    repository.salvar_diagnostico_financeiro(command)

    sql, parameters = cursor.calls[3]
    normalized = _normalized_sql(sql)

    assert "where usuario_id = %(usuario_id)s" in normalized

    assert "and idempotency_key = %(idempotency_key)s" in normalized

    assert "nome =" not in normalized

    assert parameters == {
        "usuario_id": "user-123",
        "idempotency_key": ("diagnosis:request-123456"),
    }


def test_reused_key_with_different_content_conflicts(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(
        fetchone_results=[
            None,
            _row(FINGERPRINT_OTHER),
        ]
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(repository.IdempotencyConflictError):
        repository.salvar_diagnostico_financeiro(command)


def test_missing_row_after_conflict_is_error(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_results=[
            None,
            None,
        ]
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(repository.FinancialDiagnosisRepositoryError):
        repository.salvar_diagnostico_financeiro(_command())


def test_database_error_is_sanitized(
    monkeypatch,
):
    secret = "postgresql://user:super-secret@db.example/inna"

    cursor = FakeCursor(
        fail_on_execute=3,
        failure=RuntimeError(secret),
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(repository.FinancialDiagnosisRepositoryError) as exc_info:
        repository.salvar_diagnostico_financeiro(_command())

    message = str(exc_info.value)

    assert "super-secret" not in message
    assert "postgresql://" not in message
    assert "db.example" not in message


def test_repository_rejects_arbitrary_dict():
    with pytest.raises(TypeError):
        repository.salvar_diagnostico_financeiro(
            {
                "usuario_id": "attacker",
            }
        )


def test_repository_configures_short_timeouts(
    monkeypatch,
):
    command = _command()

    cursor = FakeCursor(fetchone_results=[_row(command.request_fingerprint)])

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    repository.salvar_diagnostico_financeiro(command)

    lock_sql = _normalized_sql(cursor.calls[0][0])

    statement_sql = _normalized_sql(cursor.calls[1][0])

    assert "set local lock_timeout = '3000ms'" in lock_sql

    assert "set local statement_timeout = '5000ms'" in statement_sql


def test_created_row_with_wrong_fingerprint_is_error(
    monkeypatch,
):
    cursor = FakeCursor(fetchone_results=[_row(FINGERPRINT_OTHER)])

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(repository.FinancialDiagnosisRepositoryError):
        repository.salvar_diagnostico_financeiro(_command())


def test_result_is_minimal_and_serializable():
    result = repository.FinancialDiagnosisWriteResult(
        id=10,
        status="existing",
        data_hora=datetime(
            2026,
            7,
            18,
            3,
            30,
        ),
    )

    assert result.to_dict() == {
        "id": 10,
        "status": "existing",
        "created": False,
        "data_hora": datetime(
            2026,
            7,
            18,
            3,
            30,
        ),
    }

    assert "request_fingerprint" not in result.to_dict()

    assert "usuario_id" not in (result.to_dict())


def test_repository_source_has_no_name_lookup():
    source = repository.SQL_CONSULTAR_IDEMPOTENCIA.lower()

    assert "select *" not in source
    assert "nome" not in source
    assert "usuario_id" in source
    assert "idempotency_key" in source

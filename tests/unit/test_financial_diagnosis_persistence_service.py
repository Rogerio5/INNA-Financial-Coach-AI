from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.services.financial_diagnosis import (
    FinancialDiagnosisRecord,
)
from src.services.financial_diagnosis import (
    repository,
    service,
)


def _diagnosis(
    **overrides,
) -> dict:
    values = {
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

    values.update(overrides)

    return values


def _repository_result(
    *,
    status="created",
    identifier=101,
):
    return repository.FinancialDiagnosisWriteResult(
        id=identifier,
        status=status,
        data_hora=datetime(
            2026,
            7,
            18,
            4,
            0,
        ),
    )


def test_generated_key_is_deterministic_and_private():
    first = service.gerar_chave_idempotencia(
        origem="web-app",
        request_id=("sensitive-request-123"),
    )

    second = service.gerar_chave_idempotencia(
        origem="web-app",
        request_id=("sensitive-request-123"),
    )

    assert first == second

    assert first.startswith("diagnosis:web-app:")

    assert "sensitive-request-123" not in first

    assert 16 <= len(first) <= 160


def test_generated_key_changes_with_request():
    first = service.gerar_chave_idempotencia(
        origem="telegram",
        request_id="request-1",
    )

    second = service.gerar_chave_idempotencia(
        origem="telegram",
        request_id="request-2",
    )

    assert first != second


@pytest.mark.parametrize(
    (
        "origem",
        "request_id",
    ),
    [
        ("", "request-1"),
        ("web app", "request-1"),
        ("WEB@APP", "request-1"),
        ("web-app", ""),
        ("web-app", " " * 3),
    ],
)
def test_generated_key_rejects_invalid_input(
    origem,
    request_id,
):
    with pytest.raises(service.TrustedDiagnosisIdentityError):
        service.gerar_chave_idempotencia(
            origem=origem,
            request_id=request_id,
        )


def test_service_separates_identity_from_diagnosis(
    monkeypatch,
):
    captured = {}

    def fake_save(
        command,
    ):
        captured["command"] = command

        return _repository_result()

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        fake_save,
    )

    outcome = service.persistir_diagnostico_financeiro(
        usuario_id_confiavel=("trusted-user-123"),
        idempotency_key=("diagnosis:web-app:1234567890abcdef"),
        diagnostico=_diagnosis(),
    )

    command = captured["command"]

    assert command.context.usuario_id == "trusted-user-123"

    assert command.context.idempotency_key == "diagnosis:web-app:1234567890abcdef"

    assert not hasattr(
        command.diagnosis,
        "usuario_id",
    )

    assert outcome.id == 101
    assert outcome.status == "created"


def test_service_accepts_validated_record(
    monkeypatch,
):
    save = MagicMock(return_value=_repository_result())

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        save,
    )

    record = FinancialDiagnosisRecord(**_diagnosis())

    service.persistir_diagnostico_financeiro(
        usuario_id_confiavel="user-123",
        idempotency_key=("diagnosis:graph:1234567890abcdef"),
        diagnostico=record,
    )

    command = save.call_args.args[0]

    assert command.diagnosis is record


@pytest.mark.parametrize(
    "forbidden_field",
    [
        "usuario_id",
        "user_id",
        "idempotency_key",
        "request_fingerprint",
        "id",
        "data_hora",
    ],
)
def test_service_rejects_controlled_fields(
    monkeypatch,
    forbidden_field,
):
    save = MagicMock()

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        save,
    )

    payload = _diagnosis()
    payload[forbidden_field] = "attacker"

    with pytest.raises(service.FinancialDiagnosisValidationError):
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel="user-123",
            idempotency_key=("diagnosis:web-app:1234567890abcdef"),
            diagnostico=payload,
        )

    save.assert_not_called()


def test_service_does_not_default_missing_values_to_zero(
    monkeypatch,
):
    save = MagicMock()

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        save,
    )

    payload = _diagnosis()
    payload.pop("renda_mensal")

    with pytest.raises(service.FinancialDiagnosisValidationError):
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel="user-123",
            idempotency_key=("diagnosis:web-app:1234567890abcdef"),
            diagnostico=payload,
        )

    save.assert_not_called()


def test_service_rejects_blank_trusted_identity(
    monkeypatch,
):
    save = MagicMock()

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        save,
    )

    with pytest.raises(service.TrustedDiagnosisIdentityError):
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel=" ",
            idempotency_key=("diagnosis:web-app:1234567890abcdef"),
            diagnostico=_diagnosis(),
        )

    save.assert_not_called()


def test_service_rejects_invalid_idempotency_key(
    monkeypatch,
):
    save = MagicMock()

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        save,
    )

    with pytest.raises(service.TrustedDiagnosisIdentityError):
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel="user-123",
            idempotency_key="short",
            diagnostico=_diagnosis(),
        )

    save.assert_not_called()


@pytest.mark.parametrize(
    (
        "status",
        "created",
    ),
    [
        ("created", True),
        ("existing", False),
    ],
)
def test_service_maps_repository_result(
    monkeypatch,
    status,
    created,
):
    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        MagicMock(
            return_value=(
                _repository_result(
                    status=status,
                    identifier=77,
                )
            )
        ),
    )

    outcome = service.persistir_diagnostico_financeiro(
        usuario_id_confiavel="user-123",
        idempotency_key=("diagnosis:telegram:1234567890abcdef"),
        diagnostico=_diagnosis(),
    )

    assert outcome.id == 77
    assert outcome.status == status
    assert outcome.created is created


def test_service_maps_idempotency_conflict(
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        MagicMock(
            side_effect=(repository.IdempotencyConflictError("internal details"))
        ),
    )

    with pytest.raises(service.FinancialDiagnosisIdempotencyConflictError) as exc_info:
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel="user-123",
            idempotency_key=("diagnosis:web-app:1234567890abcdef"),
            diagnostico=_diagnosis(),
        )

    assert "internal details" not in str(exc_info.value)


def test_service_sanitizes_repository_failure(
    monkeypatch,
):
    secret = "postgresql://user:super-secret@db.example/inna"

    monkeypatch.setattr(
        repository,
        "salvar_diagnostico_financeiro",
        MagicMock(side_effect=(repository.FinancialDiagnosisRepositoryError(secret))),
    )

    with pytest.raises(service.FinancialDiagnosisServiceError) as exc_info:
        service.persistir_diagnostico_financeiro(
            usuario_id_confiavel="user-123",
            idempotency_key=("diagnosis:web-app:1234567890abcdef"),
            diagnostico=_diagnosis(),
        )

    message = str(exc_info.value)

    assert "super-secret" not in message
    assert "postgresql://" not in message
    assert "db.example" not in message


def test_service_outcome_is_compact():
    outcome = service.FinancialDiagnosisPersistenceOutcome(
        id=10,
        status="existing",
        data_hora=datetime(
            2026,
            7,
            18,
            4,
            0,
        ),
    )

    result = outcome.to_dict()

    assert result == {
        "id": 10,
        "status": "existing",
        "created": False,
        "data_hora": ("2026-07-18T04:00:00"),
    }

    assert "usuario_id" not in result
    assert "idempotency_key" not in result
    assert "request_fingerprint" not in result
    assert "diagnostico" not in result

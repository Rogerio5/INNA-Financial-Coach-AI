from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from api.schemas import FinancialInput
from src.models import (
    DiagnosticoFinanceiro,
)
from src.services.financial_diagnosis import (
    FinancialDiagnosisPersistenceCommand,
    FinancialDiagnosisRecord,
    TrustedDiagnosisPersistenceContext,
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
        "objetivo": (
            "Organizar as finanças"
        ),
        "idioma": "pt",
        "moeda": "BRL",
        "simbolo_moeda": "R$",
        "saldo_estimado": 1200,
        (
            "comprometimento_"
            "renda_percentual"
        ): 70,
        "meses_reserva_estimados": (
            0.714286
        ),
        "score_financeiro": 70,
        "nivel_risco": "Medio",
        "diagnostico": (
            "Diagnóstico financeiro validado."
        ),
        "plano_30_dias": (
            "Plano financeiro de trinta dias."
        ),
    }

    values.update(
        overrides
    )

    return values


def test_sqlalchemy_model_contains_identity_columns():
    columns = (
        DiagnosticoFinanceiro
        .__table__
        .columns
    )

    assert "usuario_id" in columns
    assert "idempotency_key" in columns
    assert "request_fingerprint" in columns

    assert (
        columns["usuario_id"].nullable
        is True
    )

    assert (
        columns["idempotency_key"].nullable
        is True
    )

    assert (
        columns[
            "request_fingerprint"
        ].nullable
        is True
    )

    assert (
        columns[
            "idempotency_key"
        ].type.length
        == 160
    )

    assert (
        columns[
            "request_fingerprint"
        ].type.length
        == 64
    )


def test_legacy_model_keeps_schema_parity():
    source = Path(
        "src/models/legacy.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "usuario_id = Column("
        "String(160), nullable=True)"
        in source
    )

    assert (
        "idempotency_key = Column("
        "String(160), nullable=True)"
        in source
    )

    assert (
        "request_fingerprint = Column("
        "String(64), nullable=True)"
        in source
    )


def test_public_financial_input_does_not_accept_identity():
    public_fields = set(
        FinancialInput.model_fields
    )

    forbidden = {
        "usuario_id",
        "user_id",
        "idempotency_key",
        "request_fingerprint",
    }

    assert public_fields.isdisjoint(
        forbidden
    )


def test_record_requires_financial_fields():
    payload = _diagnosis()

    payload.pop(
        "renda_mensal"
    )

    with pytest.raises(
        ValidationError
    ):
        FinancialDiagnosisRecord(
            **payload
        )


def test_record_rejects_negative_financial_values():
    with pytest.raises(
        ValidationError
    ):
        FinancialDiagnosisRecord(
            **_diagnosis(
                gastos_fixos=-1,
            )
        )


def test_record_rejects_unknown_fields():
    with pytest.raises(
        ValidationError
    ):
        FinancialDiagnosisRecord(
            **_diagnosis(
                usuario_id="untrusted-user",
            )
        )


def test_trusted_context_validates_identity_and_key():
    with pytest.raises(
        ValidationError
    ):
        TrustedDiagnosisPersistenceContext(
            usuario_id="",
            idempotency_key=(
                "diagnosis:1234567890"
            ),
        )

    with pytest.raises(
        ValidationError
    ):
        TrustedDiagnosisPersistenceContext(
            usuario_id="user-123",
            idempotency_key="curta",
        )

    with pytest.raises(
        ValidationError
    ):
        TrustedDiagnosisPersistenceContext(
            usuario_id="user-123",
            idempotency_key=(
                "diagnosis chave invalida"
            ),
        )


def test_record_normalizes_locale_fields():
    record = FinancialDiagnosisRecord(
        **_diagnosis(
            idioma=" PT-BR ",
            moeda=" brl ",
        )
    )

    assert record.idioma == "pt_br"
    assert record.moeda == "BRL"


def test_fingerprint_is_deterministic():
    first = FinancialDiagnosisRecord(
        **_diagnosis(
            renda_mensal=4000,
        )
    )

    second = FinancialDiagnosisRecord(
        **_diagnosis(
            renda_mensal=4000.0,
        )
    )

    assert (
        first.request_fingerprint()
        == second.request_fingerprint()
    )

    assert (
        len(
            first.request_fingerprint()
        )
        == 64
    )


def test_fingerprint_changes_with_content():
    first = FinancialDiagnosisRecord(
        **_diagnosis(
            renda_mensal=4000,
        )
    )

    second = FinancialDiagnosisRecord(
        **_diagnosis(
            renda_mensal=4001,
        )
    )

    assert (
        first.request_fingerprint()
        != second.request_fingerprint()
    )


def test_command_creates_allowlisted_repository_payload():
    command = (
        FinancialDiagnosisPersistenceCommand(
            context=(
                TrustedDiagnosisPersistenceContext(
                    usuario_id="user-123",
                    idempotency_key=(
                        "diagnosis:request-123456"
                    ),
                )
            ),
            diagnosis=(
                FinancialDiagnosisRecord(
                    **_diagnosis()
                )
            ),
        )
    )

    payload = (
        command.to_repository_payload()
    )

    assert payload["usuario_id"] == (
        "user-123"
    )

    assert payload["idempotency_key"] == (
        "diagnosis:request-123456"
    )

    assert (
        payload["request_fingerprint"]
        == command.request_fingerprint
    )

    assert len(
        payload["request_fingerprint"]
    ) == 64

    assert "id" not in payload
    assert "data_hora" not in payload


def test_record_rejects_non_finite_numbers():
    with pytest.raises(
        ValidationError
    ):
        FinancialDiagnosisRecord(
            **_diagnosis(
                saldo_estimado=float(
                    "nan"
                ),
            )
        )

    with pytest.raises(
        ValidationError
    ):
        FinancialDiagnosisRecord(
            **_diagnosis(
                renda_mensal=float(
                    "inf"
                ),
            )
        )

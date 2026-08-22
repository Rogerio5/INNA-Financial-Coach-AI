from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api import main
from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    assinar_requisicao_interna,
)
from src.services.financial_diagnosis import (
    FinancialDiagnosisIdempotencyConflictError,
    FinancialDiagnosisPersistenceOutcome,
    FinancialDiagnosisServiceError,
    gerar_chave_idempotencia,
)


SECRET = (
    "0123456789abcdef"
    "0123456789abcdef"
    "secure-web-route-test"
)

USER_ID = "usuario@example.com"

REQUEST_ID = (
    "web-request-12345678"
)


client = TestClient(
    main.app
)


def _payload() -> dict:
    return {
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
    }


def _body(
    payload: dict | None = None,
) -> bytes:
    return json.dumps(
        payload or _payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        allow_nan=False,
    ).encode(
        "utf-8"
    )


def _headers(
    *,
    body: bytes,
    timestamp: int,
    signature: str | None = None,
) -> dict[str, str]:
    calculated_signature = (
        signature
        or assinar_requisicao_interna(
            method="POST",
            path="/diagnostico",
            user_id=USER_ID,
            request_id=REQUEST_ID,
            timestamp=timestamp,
            body=body,
            secret=SECRET,
        )
    )

    return {
        "Content-Type": (
            "application/json; charset=utf-8"
        ),
        HEADER_USER_ID: USER_ID,
        HEADER_REQUEST_ID: REQUEST_ID,
        HEADER_TIMESTAMP: str(
            timestamp
        ),
        HEADER_SIGNATURE: (
            calculated_signature
        ),
    }


def _install_financial_pipeline(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "build_financial_diagnosis",
        MagicMock(
            return_value={
                "saldo_estimado": 1200,
                (
                    "comprometimento_"
                    "renda_percentual"
                ): 70,
                (
                    "meses_reserva_"
                    "estimados"
                ): 0.714286,
                "score_financeiro": 70,
                "nivel_risco": "Medio",
                "situacao": (
                    "saldo_positivo"
                ),
            }
        ),
    )

    monkeypatch.setattr(
        main,
        "build_localized_diagnosis_text",
        MagicMock(
            return_value=(
                "Diagnóstico financeiro "
                "validado."
            )
        ),
    )

    monkeypatch.setattr(
        main,
        "generate_ai_plan",
        MagicMock(
            return_value=(
                "Plano financeiro de "
                "trinta dias."
            )
        ),
    )


@pytest.fixture(
    autouse=True,
)
def configure_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )


def test_unsigned_request_is_rejected(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    persistence = MagicMock()

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        persistence,
    )

    response = client.post(
        "/diagnostico",
        json=_payload(),
    )

    assert response.status_code == 401

    persistence.assert_not_called()


def test_tampered_body_is_rejected(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    persistence = MagicMock()

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        persistence,
    )

    original_body = _body()

    tampered_payload = _payload()
    tampered_payload[
        "renda_mensal"
    ] = 9999

    tampered_body = _body(
        tampered_payload
    )

    timestamp = int(
        time.time()
    )

    response = client.post(
        "/diagnostico",
        content=tampered_body,
        headers=_headers(
            body=original_body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 401

    persistence.assert_not_called()


def test_signed_request_persists_with_trusted_user(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    captured = {}

    def fake_persist(
        *,
        usuario_id_confiavel,
        idempotency_key,
        diagnostico,
    ):
        captured[
            "usuario_id_confiavel"
        ] = usuario_id_confiavel

        captured[
            "idempotency_key"
        ] = idempotency_key

        captured[
            "diagnostico"
        ] = diagnostico

        return (
            FinancialDiagnosisPersistenceOutcome(
                id=321,
                status="created",
                data_hora=datetime(
                    2026,
                    7,
                    18,
                    4,
                    45,
                ),
            )
        )

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        fake_persist,
    )

    events = []

    monkeypatch.setattr(
        main,
        "safe_record_event",
        lambda **kwargs: events.append(
            kwargs
        ),
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    response = client.post(
        "/diagnostico",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == 321

    assert captured[
        "usuario_id_confiavel"
    ] == USER_ID

    assert captured[
        "idempotency_key"
    ] == gerar_chave_idempotencia(
        origem="web-app",
        request_id=REQUEST_ID,
    )

    diagnosis = captured[
        "diagnostico"
    ]

    assert "usuario_id" not in diagnosis
    assert "user_id" not in diagnosis
    assert "idempotency_key" not in diagnosis
    assert "request_fingerprint" not in diagnosis

    assert events[-1][
        "diagnostico_id"
    ] == 321


def test_success_event_is_compact(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        MagicMock(
            return_value=(
                FinancialDiagnosisPersistenceOutcome(
                    id=100,
                    status="existing",
                    data_hora=datetime(
                        2026,
                        7,
                        18,
                        4,
                        45,
                    ),
                )
            )
        ),
    )

    events = []

    monkeypatch.setattr(
        main,
        "safe_record_event",
        lambda **kwargs: events.append(
            kwargs
        ),
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    response = client.post(
        "/diagnostico",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 200

    event = events[-1]

    assert "pergunta" not in event
    assert "resposta" not in event

    metadata = event[
        "metadata"
    ]

    assert metadata[
        "persistence_status"
    ] == "existing"

    assert metadata[
        "created"
    ] is False

    serialized = str(
        event
    )

    assert (
        "Diagnóstico financeiro validado."
        not in serialized
    )

    assert (
        "Plano financeiro de trinta dias."
        not in serialized
    )


def test_idempotency_conflict_returns_409(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        MagicMock(
            side_effect=(
                FinancialDiagnosisIdempotencyConflictError(
                    "internal conflict details"
                )
            )
        ),
    )

    monkeypatch.setattr(
        main,
        "safe_record_event",
        MagicMock(),
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    response = client.post(
        "/diagnostico",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 409

    assert (
        "internal conflict details"
        not in response.text
    )


def test_repository_failure_is_sanitized(
    monkeypatch,
):
    _install_financial_pipeline(
        monkeypatch
    )

    secret_error = (
        "postgresql://user:"
        "super-secret@db.example/inna"
    )

    monkeypatch.setattr(
        main,
        "persistir_diagnostico_financeiro",
        MagicMock(
            side_effect=(
                FinancialDiagnosisServiceError(
                    secret_error
                )
            )
        ),
    )

    monkeypatch.setattr(
        main,
        "safe_record_event",
        MagicMock(),
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    response = client.post(
        "/diagnostico",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 503

    assert "super-secret" not in response.text
    assert "postgresql://" not in response.text
    assert "db.example" not in response.text


def test_web_route_no_longer_uses_legacy_save():
    source = Path(
        "api/main.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "save_diagnostico_db"
        not in source
    )

    assert (
        "persistir_diagnostico_financeiro"
        in source
    )

    assert (
        "require_trusted_request_context"
        in source
    )

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import telegram_webhook
from api.security.telegram_webhook import (
    TELEGRAM_SECRET_HEADER,
)
from src.channels.telegram_context import (
    TelegramUpdateContextError,
    extrair_contexto_confiavel_telegram,
    normalizar_update_id_telegram,
)
from src.services.financial_diagnosis import (
    FinancialDiagnosisPersistenceOutcome,
    gerar_chave_idempotencia,
)


class _DurableTestSession:
    def __init__(
        self,
        *,
        telegram_user_id,
        chat_id,
        state=None,
        language="pt",
        version=1,
    ):
        self.telegram_user_id = telegram_user_id
        self.chat_id = chat_id
        self.state = dict(state or {})
        self.language = language
        self.version = version

    def to_processing_state(self):
        return dict(self.state)


class _DurableTestBridge:
    def __init__(self):
        self.sessions = {}

    def load_or_open_session(
        self,
        telegram_user_id,
        chat_id,
        initial_state,
        *,
        language,
    ):
        key = (
            telegram_user_id,
            chat_id,
        )

        session = self.sessions.get(key)

        if session is None:
            session = _DurableTestSession(
                telegram_user_id=telegram_user_id,
                chat_id=chat_id,
                state=initial_state,
                language=language,
            )

            self.sessions[key] = session

        return session

    def save_session(
        self,
        session,
        **kwargs,
    ):
        state = kwargs.get(
            "state",
            kwargs.get(
                "processing_state",
                session.state,
            ),
        )

        language = kwargs.get(
            "language",
            session.language,
        )

        session.state = dict(state)
        session.language = language
        session.version += 1

        return session

    def reload_session(
        self,
        session,
        **kwargs,
    ):
        return session

    def delete_session(
        self,
        session,
        **kwargs,
    ):
        self.sessions.pop(
            (
                session.telegram_user_id,
                session.chat_id,
            ),
            None,
        )

    def resolve_language(
        self,
        *,
        telegram_user_id,
        chat_id,
        default_language="pt",
        **kwargs,
    ):
        session = self.sessions.get(
            (
                telegram_user_id,
                chat_id,
            )
        )

        if session is not None and session.language:
            return session.language

        return default_language


SECRET = "Telegram_Webhook_Secret_0123456789abcdef0123456789"


def _payload() -> dict:
    return {
        "nome": "Usuário Telegram",
        "renda_mensal": 4000,
        "gastos_fixos": 1800,
        "gastos_variaveis": 700,
        "dividas_mensais": 300,
        "reserva_atual": 2000,
        "objetivo": ("Criar uma reserva financeira"),
        "idioma": "pt",
        "moeda": "BRL",
        "simbolo_moeda": "R$",
    }


def _update(
    *,
    update_id=9001,
    chat_id=123456,
    message_id=77,
    text="Criar reserva",
) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": message_id,
            "chat": {
                "id": chat_id,
            },
            "text": text,
        },
    }


def _install_pipeline(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "build_financial_diagnosis",
        MagicMock(
            return_value={
                "saldo_estimado": 1200,
                ("comprometimento_renda_percentual"): 70,
                ("meses_reserva_estimados"): 0.714286,
                "score_financeiro": 70,
                "nivel_risco": "Medio",
                "diagnostico": ("Diagnóstico financeiro validado."),
            }
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "generate_ai_plan",
        MagicMock(return_value=("Plano financeiro de trinta dias.")),
    )


def test_extracts_trusted_telegram_context():
    context = extrair_contexto_confiavel_telegram(_update())

    assert context.update_id == 9001
    assert context.chat_id == 123456
    assert context.message_id == 77

    assert context.usuario_id == ("telegram:123456")

    assert context.request_id == ("telegram-update:9001")


def test_negative_group_chat_id_is_supported():
    context = extrair_contexto_confiavel_telegram(
        _update(
            chat_id=-100123456,
        )
    )

    assert context.usuario_id == ("telegram:-100123456")


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        -1,
        "9001",
    ],
)
def test_invalid_update_id_is_rejected(
    value,
):
    with pytest.raises(TelegramUpdateContextError):
        normalizar_update_id_telegram(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        0,
        "123456",
    ],
)
def test_invalid_chat_id_is_rejected(
    value,
):
    with pytest.raises(TelegramUpdateContextError):
        extrair_contexto_confiavel_telegram(
            _update(
                chat_id=value,
            )
        )


def test_generation_uses_secure_persistence(
    monkeypatch,
):
    _install_pipeline(monkeypatch)

    captured = {}

    def fake_persist(
        *,
        usuario_id_confiavel,
        idempotency_key,
        diagnostico,
    ):
        captured["usuario_id_confiavel"] = usuario_id_confiavel

        captured["idempotency_key"] = idempotency_key

        captured["diagnostico"] = diagnostico

        return FinancialDiagnosisPersistenceOutcome(
            id=501,
            status="created",
            data_hora=datetime(
                2026,
                7,
                18,
                5,
                30,
            ),
        )

    monkeypatch.setattr(
        telegram_webhook,
        "persistir_diagnostico_financeiro",
        fake_persist,
    )

    result = telegram_webhook.gerar_diagnostico_pelo_payload(
        _payload(),
        "pt",
        usuario_id_confiavel=("telegram:123456"),
        request_id=("telegram-update:9001"),
    )

    assert result["id"] == 501
    assert result["created"] is True
    assert result["persistence_status"] == "created"

    assert captured["usuario_id_confiavel"] == "telegram:123456"

    assert captured["idempotency_key"] == gerar_chave_idempotencia(
        origem="telegram",
        request_id=("telegram-update:9001"),
    )

    persisted = captured["diagnostico"]

    assert "usuario_id" not in persisted
    assert "chat_id" not in persisted
    assert "update_id" not in persisted
    assert "idempotency_key" not in persisted


def test_repeated_request_can_return_existing(
    monkeypatch,
):
    _install_pipeline(monkeypatch)

    monkeypatch.setattr(
        telegram_webhook,
        "persistir_diagnostico_financeiro",
        MagicMock(
            return_value=(
                FinancialDiagnosisPersistenceOutcome(
                    id=501,
                    status="existing",
                    data_hora=datetime(
                        2026,
                        7,
                        18,
                        5,
                        30,
                    ),
                )
            )
        ),
    )

    result = telegram_webhook.gerar_diagnostico_pelo_payload(
        _payload(),
        "pt",
        usuario_id_confiavel=("telegram:123456"),
        request_id=("telegram-update:9001"),
    )

    assert result["id"] == 501
    assert result["created"] is False

    assert result["persistence_status"] == "existing"


def test_process_derives_identity_from_update(
    monkeypatch,
):
    chat_id = 123456

    update = _update(
        update_id=9010,
        chat_id=chat_id,
        text="Criar reserva",
    )

    trusted_update = telegram_webhook.extrair_contexto_confiavel_telegram(update)

    bridge = _DurableTestBridge()

    bridge.sessions[
        (
            trusted_update.usuario_id,
            trusted_update.chat_id,
        )
    ] = _DurableTestSession(
        telegram_user_id=(trusted_update.usuario_id),
        chat_id=trusted_update.chat_id,
        state={
            "step": "objetivo",
            "lang": "pt",
            "nome": "Usuário Telegram",
            "renda_mensal": 4000,
            "gastos_fixos": 1800,
            "gastos_variaveis": 700,
            "dividas_mensais": 300,
            "reserva_atual": 2000,
        },
        language="pt",
    )

    generation = MagicMock(
        return_value={
            "id": 501,
            "nome": "Usuário Telegram",
            "saldo_estimado": 1200,
            "score_financeiro": 70,
            "nivel_risco": "Medio",
            "persistence_status": ("created"),
            "created": True,
        }
    )

    monkeypatch.setattr(
        telegram_webhook,
        "gerar_diagnostico_pelo_payload",
        generation,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "send_telegram_message",
        MagicMock(),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "resposta_curta",
        MagicMock(return_value=("Resposta financeira.")),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "safe_record_telegram_event",
        MagicMock(),
    )

    telegram_webhook.process_telegram_update(
        update,
        conversation_bridge=bridge,
    )

    assert generation.call_count == 1

    call = generation.call_args

    assert call.kwargs["usuario_id_confiavel"] == "telegram:123456"

    assert call.kwargs["request_id"] == "telegram-update:9010"


def test_invalid_update_never_generates_diagnosis(
    monkeypatch,
):
    generation = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "gerar_diagnostico_pelo_payload",
        generation,
    )

    telegram_webhook.process_telegram_update(
        {"update_id": "invalid"},
        conversation_bridge=_DurableTestBridge(),
    )

    generation.assert_not_called()


def test_event_log_is_compact(
    monkeypatch,
):
    events = []

    monkeypatch.setattr(
        telegram_webhook,
        "record_event",
        lambda **kwargs: events.append(kwargs),
    )

    telegram_webhook.safe_record_telegram_event(
        chat_id=123456,
        lang="pt",
        payload=_payload(),
        resultado={
            "id": 501,
            "score_financeiro": 70,
            "nivel_risco": "Medio",
            "saldo_estimado": 1200,
            "persistence_status": ("created"),
            "created": True,
        },
        resposta=("Resposta financeira sensível."),
    )

    event = events[0]

    assert event["usuario_id"] == "telegram:123456"

    assert "pergunta" not in event
    assert "resposta" not in event

    metadata = event["metadata"]

    assert "saldo_estimado" not in metadata

    assert "Resposta financeira sensível." not in str(event)


def test_webhook_rejects_invalid_update_id(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    process = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        process,
    )

    app = FastAPI()

    app.include_router(telegram_webhook.router)

    route = next(
        route
        for route in telegram_webhook.router.routes
        if route.name == "telegram_webhook"
    )

    response = TestClient(app).post(
        route.path,
        json={
            "update_id": "invalid",
        },
        headers={
            TELEGRAM_SECRET_HEADER: SECRET,
        },
    )

    assert response.status_code == 400

    process.assert_not_called()


def test_legacy_save_was_removed():
    source = Path("api/telegram_webhook.py").read_text(
        encoding="utf-8",
    )

    assert "save_diagnostico_db" not in source

    assert "persistir_diagnostico_financeiro" in source

    assert "extrair_contexto_confiavel_telegram" in source

from __future__ import annotations

import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

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
from src import api_client
from src.channels import telegram_bot
from src.channels.telegram_context import (
    construir_contexto_confiavel_telegram,
)


SECRET = "0123456789abcdef0123456789abcdeftelegram-polling-test-secret"


def _payload():
    return {
        "nome": "Usuário Telegram",
        "renda_mensal": 4000,
        "gastos_fixos": 1800,
        "gastos_variaveis": 700,
        "dividas_mensais": 300,
        "reserva_atual": 2000,
        "objetivo": "Criar reserva",
        "idioma": "pt",
    }


def _body():
    return json.dumps(
        _payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode("utf-8")


def _headers(
    body: bytes,
):
    timestamp = int(time.time())

    user_id = "telegram:123456"

    request_id = "telegram-update:9001"

    signature = assinar_requisicao_interna(
        method="POST",
        path=("/internal/telegram/diagnostico"),
        user_id=user_id,
        request_id=request_id,
        timestamp=timestamp,
        body=body,
        secret=SECRET,
    )

    return {
        "Content-Type": ("application/json"),
        HEADER_USER_ID: user_id,
        HEADER_REQUEST_ID: request_id,
        HEADER_TIMESTAMP: str(timestamp),
        HEADER_SIGNATURE: signature,
    }


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


def test_context_factory_derives_channel_identity():
    context = construir_contexto_confiavel_telegram(
        update_id=9001,
        chat_id=123456,
        message_id=77,
    )

    assert context.usuario_id == ("telegram:123456")

    assert context.request_id == ("telegram-update:9001")


def test_internal_route_rejects_unsigned():
    response = TestClient(main.app).post(
        "/internal/telegram/diagnostico",
        json=_payload(),
    )

    assert response.status_code == 401


def test_internal_route_rejects_non_telegram_user():
    body = _body()

    timestamp = int(time.time())

    signature = assinar_requisicao_interna(
        method="POST",
        path=("/internal/telegram/diagnostico"),
        user_id="web-user",
        request_id=("telegram-update:9001"),
        timestamp=timestamp,
        body=body,
        secret=SECRET,
    )

    response = TestClient(main.app).post(
        "/internal/telegram/diagnostico",
        content=body,
        headers={
            "Content-Type": ("application/json"),
            HEADER_USER_ID: "web-user",
            HEADER_REQUEST_ID: ("telegram-update:9001"),
            HEADER_TIMESTAMP: str(timestamp),
            HEADER_SIGNATURE: signature,
        },
    )

    assert response.status_code == 403


def test_internal_route_uses_telegram_channel(
    monkeypatch,
):
    captured = {}

    def fake_core(
        **kwargs,
    ):
        captured.update(kwargs)

        return {
            "id": 100,
            "nome": "Usuário Telegram",
            "saldo_estimado": 1200,
            ("comprometimento_renda_percentual"): 70,
            ("meses_reserva_estimados"): 0.7,
            "score_financeiro": 70,
            "nivel_risco": "Medio",
            "diagnostico": "Diagnóstico.",
            "plano_30_dias": "Plano.",
        }

    monkeypatch.setattr(
        main,
        "_gerar_e_persistir_diagnostico_canal",
        fake_core,
    )

    body = _body()

    response = TestClient(main.app).post(
        "/internal/telegram/diagnostico",
        content=body,
        headers=_headers(body),
    )

    assert response.status_code == 200

    assert captured["canal"] == "telegram"

    assert captured["origem_idempotencia"] == "telegram"

    assert captured["origem_evento"] == "telegram_polling"


def test_client_posts_to_dedicated_signed_path(
    monkeypatch,
):
    captured = {}

    response = MagicMock()

    response.raise_for_status.return_value = None

    response.json.return_value = {
        "id": 100,
    }

    def fake_post(
        url,
        **kwargs,
    ):
        captured["url"] = url

        captured.update(kwargs)

        return response

    monkeypatch.setattr(
        api_client.requests,
        "post",
        fake_post,
    )

    result = api_client.gerar_diagnostico_telegram_api(
        _payload(),
        usuario_id_confiavel=("telegram:123456"),
        request_id=("telegram-update:9001"),
    )

    assert result["id"] == 100

    assert captured["url"].endswith("/internal/telegram/diagnostico")

    assert "data" in captured
    assert "json" not in captured

    assert captured["headers"][HEADER_USER_ID] == "telegram:123456"


def test_polling_handler_uses_update_identity(
    monkeypatch,
):
    message = SimpleNamespace(
        text="Criar reserva",
        message_id=77,
        reply_text=AsyncMock(),
    )

    update = SimpleNamespace(
        update_id=9001,
        effective_chat=SimpleNamespace(
            id=123456,
        ),
        effective_message=message,
    )

    context = SimpleNamespace(
        user_data={
            "lang": "pt",
            "nome": "Usuário Telegram",
            "renda_mensal": 4000,
            "gastos_fixos": 1800,
            "gastos_variaveis": 700,
            "dividas_mensais": 300,
            "reserva_atual": 2000,
        }
    )

    captured = {}

    def fake_generate(
        payload,
        *,
        usuario_id_confiavel,
        request_id,
    ):
        captured["usuario_id_confiavel"] = usuario_id_confiavel

        captured["request_id"] = request_id

        return {
            "id": 100,
        }

    async def fake_to_thread(
        function,
        *args,
        **kwargs,
    ):
        return function(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        telegram_bot,
        "gerar_diagnostico",
        fake_generate,
    )

    monkeypatch.setattr(
        telegram_bot.asyncio,
        "to_thread",
        fake_to_thread,
    )

    monkeypatch.setattr(
        telegram_bot,
        "formatar_resposta",
        MagicMock(return_value=("Resposta segura.")),
    )

    asyncio.run(
        telegram_bot.receber_objetivo(
            update,
            context,
        )
    )

    assert captured["usuario_id_confiavel"] == "telegram:123456"

    assert captured["request_id"] == "telegram-update:9001"

    assert context.user_data == {}


def test_polling_error_is_sanitized(
    monkeypatch,
):
    message = SimpleNamespace(
        text="Criar reserva",
        message_id=77,
        reply_text=AsyncMock(),
    )

    update = SimpleNamespace(
        update_id=9001,
        effective_chat=SimpleNamespace(
            id=123456,
        ),
        effective_message=message,
    )

    context = SimpleNamespace(
        user_data={
            "lang": "pt",
            "nome": "Usuário Telegram",
            "renda_mensal": 4000,
            "gastos_fixos": 1800,
            "gastos_variaveis": 700,
            "dividas_mensais": 300,
            "reserva_atual": 2000,
        }
    )

    def fail(
        *_args,
        **_kwargs,
    ):
        raise RuntimeError("super-secret database error")

    async def fake_to_thread(
        function,
        *args,
        **kwargs,
    ):
        return function(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        telegram_bot,
        "gerar_diagnostico",
        fail,
    )

    monkeypatch.setattr(
        telegram_bot.asyncio,
        "to_thread",
        fake_to_thread,
    )

    asyncio.run(
        telegram_bot.receber_objetivo(
            update,
            context,
        )
    )

    responses = [str(call.args[0]) for call in (message.reply_text.await_args_list)]

    assert all("super-secret" not in response for response in responses)


def test_polling_source_has_no_unsigned_post():
    source = (
        __import__("pathlib")
        .Path("src/channels/telegram_bot.py")
        .read_text(
            encoding="utf-8",
        )
    )

    assert "requests.post" not in source
    assert "json=payload" not in source
    assert 'f"Erro: {error}"' not in source

    assert "gerar_diagnostico_telegram_api" in source

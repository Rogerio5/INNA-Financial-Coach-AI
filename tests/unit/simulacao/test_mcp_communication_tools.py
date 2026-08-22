from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.agent_tools.catalog import (
    criar_registro_ferramentas_inna,
)
from src.agent_tools.communication_tools import (
    PrepararEmailFinanceiroInput,
    PrepararMensagemTelegramInput,
)
from src.mcp_server.server import server


def _structured_content(result):
    content = getattr(
        result,
        "structured_content",
        None,
    )

    if content is None:
        content = getattr(
            result,
            "structuredContent",
            None,
        )

    assert content is not None
    return content


def test_catalogo_registra_ferramentas_comunicacao():
    registry = criar_registro_ferramentas_inna()

    names = {definition.name for definition in registry.list_definitions()}

    assert "preparar_email_financeiro" in names
    assert "preparar_mensagem_telegram" in names


def test_email_invalido_e_rejeitado():
    with pytest.raises(ValidationError):
        PrepararEmailFinanceiroInput(
            destinatario="email-invalido",
            assunto="Diagnóstico financeiro",
            corpo="Conteúdo de teste.",
        )


def test_chat_id_invalido_e_rejeitado():
    with pytest.raises(ValidationError):
        PrepararMensagemTelegramInput(
            chat_id="usuario-publico",
            mensagem="Conteúdo de teste.",
        )


@pytest.mark.asyncio
async def test_mcp_prepara_email_sem_enviar(
    monkeypatch,
):
    persisted_payloads = []

    monkeypatch.setattr(
        "src.agent_tools.communication_tools.registrar_revisao_pendente",
        lambda payload: persisted_payloads.append(payload),
    )
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )

    result = await server.call_tool(
        name="preparar_email_financeiro",
        arguments={
            "destinatario": "usuario@example.com",
            "assunto": "Seu diagnóstico INNA",
            "corpo": "Relatório preparado para revisão.",
            "idioma": "pt",
        },
    )

    content = _structured_content(result)

    assert content["channel"] == "email"
    assert content["status"] == "pending_approval"
    assert content["requires_human_approval"] is True
    assert content["sent"] is False
    assert content["review_persisted"] is True
    assert content["review_id"].startswith("email-")
    assert len(persisted_payloads) == 1
    assert persisted_payloads[0]["type"] == ("human_review")
    assert persisted_payloads[0]["status"] == "pending"
    assert persisted_payloads[0]["payload"]["sent"] is False
    assert content["recipient_masked"] != ("usuario@example.com")
    assert content["_mcp"]["status"] == "success"


@pytest.mark.asyncio
async def test_mcp_prepara_telegram_sem_enviar(
    monkeypatch,
):
    persisted_payloads = []

    monkeypatch.setattr(
        "src.agent_tools.communication_tools.registrar_revisao_pendente",
        lambda payload: persisted_payloads.append(payload),
    )
    monkeypatch.setenv(
        "INNA_INTERNAL_OPERATIONS_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "INNA_MCP_CLIENT_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "INNA_MCP_DB_AUDIT_ENABLED",
        "false",
    )

    result = await server.call_tool(
        name="preparar_mensagem_telegram",
        arguments={
            "chat_id": "123456789",
            "mensagem": ("Mensagem preparada para revisão."),
            "idioma": "pt",
        },
    )

    content = _structured_content(result)

    assert content["channel"] == "telegram"
    assert content["status"] == "pending_approval"
    assert content["requires_human_approval"] is True
    assert content["sent"] is False
    assert content["review_persisted"] is True
    assert content["review_id"].startswith("telegram-")
    assert len(persisted_payloads) == 1
    assert persisted_payloads[0]["type"] == ("human_review")
    assert persisted_payloads[0]["status"] == "pending"
    assert persisted_payloads[0]["payload"]["sent"] is False
    assert content["recipient_masked"] != "123456789"
    assert content["_mcp"]["status"] == "success"

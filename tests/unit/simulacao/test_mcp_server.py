from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

import pytest

module = importlib.import_module("src.mcp_server.server")


@pytest.mark.anyio
async def test_mcp_server_registers_expected_tools() -> None:
    server = module.criar_servidor_mcp_inna()
    tools = await server.list_tools()

    assert {tool.name for tool in tools} == {
        "buscar_conhecimento_rag",
        "calcular_diagnostico_financeiro",
        "preparar_email_financeiro",
        "preparar_mensagem_telegram",
    }


def test_financial_tool_uses_governed_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_runtime(call):
        captured["call"] = call

        return SimpleNamespace(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=SimpleNamespace(value="success"),
            output={
                "saldo_estimado": 500.0,
                "score_financeiro": 60,
                "nivel_risco": "Medio",
            },
            error=None,
            duration_ms=7.5,
        )

    monkeypatch.setattr(
        module,
        "executar_ferramenta_inna",
        fake_runtime,
    )

    result = module.calcular_diagnostico_financeiro(
        renda_mensal=3000,
        gastos_fixos=1500,
        gastos_variaveis=700,
        dividas_mensais=300,
    )

    call = captured["call"]

    assert call.tool_name == "calcular_diagnostico_financeiro"

    assert call.context.requested_by == "financial_agent"

    assert call.context.metadata["source"] == "mcp"
    assert result["saldo_estimado"] == 500.0
    assert result["_mcp"]["status"] == "success"
    assert result["_mcp"]["duration_ms"] == 7.5


def test_rag_tool_uses_authorized_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_runtime(call):
        captured["call"] = call

        return SimpleNamespace(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=SimpleNamespace(value="success"),
            output={
                "resposta": "Resposta fundamentada.",
                "fontes": ["base_inna"],
            },
            error=None,
            duration_ms=12.0,
        )

    monkeypatch.setattr(
        module,
        "executar_ferramenta_inna",
        fake_runtime,
    )

    result = module.buscar_conhecimento_rag(
        pergunta="Como montar uma reserva financeira?",
        idioma="pt",
        top_k=4,
    )

    call = captured["call"]

    assert call.tool_name == "buscar_conhecimento_rag"
    assert call.context.requested_by == "rag_agent"
    assert call.arguments["top_k"] == 4
    assert result["resposta"] == "Resposta fundamentada."
    assert result["_mcp"]["trace_id"].startswith("mcp-")


def test_unmapped_tool_is_denied() -> None:
    with pytest.raises(
        module.MCPToolExecutionError,
        match="não autorizada",
    ):
        module._executar_tool_governada(
            tool_name="excluir_todos_os_dados",
            arguments={},
        )


def test_runtime_error_is_converted_to_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_runtime(call):
        return SimpleNamespace(
            call_id=call.call_id,
            tool_name=call.tool_name,
            status=SimpleNamespace(value="error"),
            output=None,
            error=SimpleNamespace(
                code="tool_permission_denied",
                message="Ferramenta não autorizada.",
            ),
            duration_ms=1.0,
        )

    monkeypatch.setattr(
        module,
        "executar_ferramenta_inna",
        fake_runtime,
    )

    with pytest.raises(
        module.MCPToolExecutionError,
        match="tool_permission_denied",
    ):
        module.calcular_diagnostico_financeiro(
            renda_mensal=3000,
            gastos_fixos=1500,
            gastos_variaveis=700,
        )


@pytest.fixture(autouse=True)
def _configure_internal_mcp_auth_for_server_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configura autenticação MCP fictícia apenas neste módulo."""

    from src.mcp_server import security as mcp_security

    test_token = "inna-mcp-test-token-not-a-real-secret"

    monkeypatch.setenv(
        mcp_security.EXPECTED_TOKEN_ENV,
        test_token,
    )

    monkeypatch.setenv(
        mcp_security.CLIENT_TOKEN_ENV,
        test_token,
    )

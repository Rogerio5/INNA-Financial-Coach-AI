from __future__ import annotations

from unittest.mock import patch

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.agents.nodes import (
    rag_agent_node,
)


def _state() -> dict:
    return {
        "user_message": ("Como criar uma reserva financeira?"),
        "language": "pt",
        "user_id": "user-test",
        "thread_id": "thread-test",
        "trace_id": "trace-test",
        "intent": "consulta_rag",
        "confidence": 0.88,
        "trace": [],
        "errors": [],
        "tool_results": [],
        "structured_response": {},
    }


def _success_result() -> ToolResult:
    return ToolResult(
        call_id="call-success",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.SUCCESS,
        output={
            "pergunta": ("Como criar uma reserva financeira?"),
            "idioma": "pt",
            "resposta": ("Comece definindo uma meta e guardando parte da renda."),
            "fontes": [
                "guia_reserva.md",
            ],
            "modo": ("rag_hibrido_pgvector_text_neon_rerank"),
            "documentos_recuperados": 3,
            "duracao_rag_ms": 120,
        },
        duration_ms=135.5,
    )


def test_rag_node_uses_formal_tool_call():
    captured = {}

    def fake_execute(call):
        captured["call"] = call
        return _success_result()

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        side_effect=fake_execute,
    ):
        result = rag_agent_node(_state())

    call = captured["call"]

    assert call.tool_name == (RAG_TOOL_NAME)

    assert call.context.requested_by == "rag_agent"

    assert call.context.user_id == "user-test"

    assert call.context.session_id == "thread-test"

    assert call.arguments == {
        "pergunta": ("Como criar uma reserva financeira?"),
        "idioma": "pt",
        "top_k": 4,
    }

    assert result["response"].startswith("Comece definindo")

    assert "tool:buscar_conhecimento_rag:success" in result["trace"]

    assert "agent:rag_agent" in result["trace"]


def test_rag_node_keeps_compact_tool_result():
    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=_success_result(),
    ):
        result = rag_agent_node(_state())

    stored_result = result["tool_results"][0]

    assert stored_result["tool"] == (RAG_TOOL_NAME)

    assert stored_result["status"] == ("success")

    assert stored_result["ok"] is True

    # A resposta longa não é duplicada no histórico
    # técnico da ferramenta, economizando contexto.
    assert "output" not in stored_result
    assert "resposta" not in stored_result

    rag_execution = result["structured_response"]["rag_execution"]

    assert rag_execution["retrieved_documents"] == 3

    assert rag_execution["sources"] == ["guia_reserva.md"]


def test_rag_node_handles_safe_tool_error():
    failure = ToolResult(
        call_id="call-error",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.ERROR,
        output=None,
        error=ToolError(
            code="tool_execution_error",
            message=("A ferramenta falhou durante a execução."),
            retryable=False,
        ),
        duration_ms=15.0,
    )

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=failure,
    ):
        result = rag_agent_node(_state())

    assert result["response"] == (
        "Não foi possível consultar a base de conhecimento neste momento."
    )

    assert result["tool_results"][0]["error_code"] == "tool_execution_error"

    assert "tool:buscar_conhecimento_rag:error" in result["trace"]

    assert "agent:rag_agent:error" in result["trace"]

    assert result["errors"] == [("A ferramenta falhou durante a execução.")]

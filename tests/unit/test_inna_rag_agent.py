from __future__ import annotations

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)

from unittest.mock import patch

from src.agent_tools.rag_tools import (
    RagToolResult,
    _normalizar_fontes,
    consultar_rag_inna,
)
from src.agents.nodes import rag_agent_node


def test_normalizar_fontes_remove_duplicadas():
    fontes = _normalizar_fontes(
        [
            "guia-reserva",
            {"source": "manual-inna"},
            {"titulo": "guia-reserva"},
        ]
    )

    assert fontes == [
        "guia-reserva",
        "manual-inna",
    ]


def test_consultar_rag_rejeita_pergunta_curta():
    resultado = consultar_rag_inna(
        "oi",
        idioma="pt",
    )

    assert resultado.ok is False
    assert resultado.error_type == "ValidationError"


def test_rag_agent_node_sucesso():
    tool_result = ToolResult(
        call_id="call-rag-success",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.SUCCESS,
        output={
            "pergunta": ("Como criar uma reserva?"),
            "idioma": "pt",
            "resposta": ("Comece reservando uma parte da renda todos os meses."),
            "fontes": [
                "reserva_financeira.md",
            ],
            "modo": ("rag_hibrido_pgvector_text_neon_rerank"),
            "documentos_recuperados": 3,
            "duracao_rag_ms": 120,
        },
        duration_ms=135.0,
    )

    state = {
        "user_message": ("Como criar uma reserva?"),
        "language": "pt",
        "user_id": "user-test",
        "thread_id": "thread-test",
        "trace_id": "trace-test",
        "intent": "consulta_rag",
        "confidence": 0.90,
        "trace": [],
        "errors": [],
        "tool_results": [],
        "structured_response": {},
    }

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=tool_result,
    ) as mock_execute:
        result = rag_agent_node(state)

    mock_execute.assert_called_once()

    call = mock_execute.call_args.args[0]

    assert call.tool_name == (RAG_TOOL_NAME)

    assert call.context.requested_by == "rag_agent"

    assert result["response"] == (
        "Comece reservando uma parte da renda todos os meses."
    )

    assert result["structured_response"]["rag_execution"]["retrieved_documents"] == 3

    assert "tool:buscar_conhecimento_rag:success" in result["trace"]

    assert "agent:rag_agent" in result["trace"]


def test_rag_agent_node_falha_controlada():
    tool_result = ToolResult(
        call_id="call-rag-error",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.ERROR,
        output=None,
        error=ToolError(
            code="tool_execution_error",
            message=("A ferramenta falhou durante a execução."),
            retryable=False,
        ),
        duration_ms=20.0,
    )

    state = {
        "user_message": ("Como organizar minhas finanças?"),
        "language": "pt",
        "user_id": "user-test",
        "thread_id": "thread-test",
        "trace_id": "trace-test",
        "intent": "consulta_rag",
        "confidence": 0.80,
        "trace": [],
        "errors": [],
        "tool_results": [],
        "structured_response": {},
    }

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=tool_result,
    ) as mock_execute:
        result = rag_agent_node(state)

    mock_execute.assert_called_once()

    assert result["response"] == (
        "Não foi possível consultar a base de conhecimento neste momento."
    )

    assert result["errors"] == [("A ferramenta falhou durante a execução.")]

    assert result["tool_results"][0]["error_code"] == "tool_execution_error"

    assert "tool:buscar_conhecimento_rag:error" in result["trace"]

    assert "agent:rag_agent:error" in result["trace"]

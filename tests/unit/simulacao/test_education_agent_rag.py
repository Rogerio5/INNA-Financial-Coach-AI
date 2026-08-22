from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from src.agent_tools.core import (
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.agents.nodes import (
    education_agent_node,
)


def _success_tool_result():
    return SimpleNamespace(
        call_id="education-rag-success",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.SUCCESS,
        ok=True,
        duration_ms=125,
        error=None,
        output={
            "pergunta": ("Explique gastos fixos e variáveis."),
            "idioma": "pt",
            "resposta": (
                "Gastos fixos são despesas recorrentes, "
                "enquanto gastos variáveis mudam ao longo "
                "do mês. A reserva de emergência protege "
                "o orçamento contra imprevistos."
            ),
            "fontes": [
                "guia-educacao-financeira.md",
            ],
            "modo": "rag_hibrido",
            "documentos_recuperados": 3,
            "duracao_rag_ms": 110,
        },
    )


def test_education_agent_executes_formal_rag():
    state = {
        "user_message": (
            "Explique gastos fixos, gastos variáveis e reserva de emergência."
        ),
        "language": "pt",
        "intent": "educacao_financeira",
        "confidence": 0.95,
        "thread_id": "education-test-thread",
        "tool_results": [],
        "structured_response": {},
        "trace": [],
        "errors": [],
    }

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=_success_tool_result(),
    ) as mocked_execute:
        result = education_agent_node(state)

    mocked_execute.assert_called_once()

    call = mocked_execute.call_args.args[0]

    assert call.tool_name == RAG_TOOL_NAME
    assert call.context.requested_by == "education_agent"

    assert result["response"].startswith("Gastos fixos")

    assert result["structured_response"]["agent_response"]["agent"] == "education_agent"

    assert result["structured_response"]["rag_execution"]["retrieved_documents"] == 3

    assert result["structured_response"]["rag_execution"]["sources"] == [
        "guia-educacao-financeira.md",
    ]

    assert "tool:buscar_conhecimento_rag:success" in result["trace"]

    assert "agent:education_agent" in result["trace"]

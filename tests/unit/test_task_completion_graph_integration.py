from __future__ import annotations

from unittest.mock import patch

from src.agent_tools.core import (
    ToolResult,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.agents.graph import (
    executar_nucleo_inna,
)


def test_complete_financial_response_has_task_completion():
    result = executar_nucleo_inna(
        (
            "Minha renda mensal é 5000 reais, "
            "meus gastos fixos são 2000 reais, "
            "meus gastos variáveis são 800 reais, "
            "minhas dívidas mensais são 300 reais "
            "e minha reserva atual é 1000 reais."
        ),
        usuario_id="task-completion-user",
        idioma="pt",
        moeda="BRL",
    )

    assert result["current_agent"] == (
        "financial_agent"
    )

    assert result["task_status"] == (
        "completed"
    )

    assert result[
        "task_completion_score"
    ] == 1.0

    assert result[
        "missing_requirements"
    ] == []

    assert any(
        item.startswith(
            "task_completion:completed:"
        )
        for item in result["trace"]
    )

    assert result["trace"][-1].startswith(
        "conversation_summary_node:"
    )


def test_incomplete_financial_request_needs_user_input():
    result = executar_nucleo_inna(
        "Minha renda mensal é 5000 reais.",
        usuario_id="task-input-user",
        idioma="pt",
        moeda="BRL",
    )

    assert result["current_agent"] == (
        "financial_agent"
    )

    assert result["task_status"] == (
        "needs_user_input"
    )

    assert result["task_block_reason"]

    assert (
        result["task_completion_score"]
        < 1.0
    )

    assert (
        "financial_inputs_resolved"
        in result["missing_requirements"]
    )

    assert (
        "financial_calculation_executed"
        in result["missing_requirements"]
    )

    assert any(
        item.startswith(
            "task_completion:needs_user_input:"
        )
        for item in result["trace"]
    )


def test_educational_response_is_completed():
    tool_result = ToolResult(
        call_id="task-education-rag",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.SUCCESS,
        output={
            "pergunta": (
                "Explique de forma educativa "
                "o que é uma reserva de emergência."
            ),
            "idioma": "pt",
            "resposta": (
                "A reserva de emergência é um valor "
                "guardado para despesas inesperadas "
                "e ajuda a proteger o orçamento."
            ),
            "fontes": [
                "Financeiro Basico",
            ],
            "modo": "rag_hibrido_test",
            "documentos_recuperados": 1,
            "contexto_recuperado": [
                (
                    "Reserva financeira é o dinheiro "
                    "separado para emergências e "
                    "imprevistos."
                ),
            ],
            "duracao_rag_ms": 10,
        },
        duration_ms=12.0,
    )

    with patch(
        "src.agents.nodes."
        "executar_ferramenta_inna",
        return_value=tool_result,
    ) as mocked_execute:
        result = executar_nucleo_inna(
            (
                "Explique de forma educativa "
                "o que é uma reserva de emergência."
            ),
            usuario_id="task-education-user",
            idioma="pt",
            moeda="BRL",
        )

    mocked_execute.assert_called_once()

    assert result["current_agent"] == (
        "education_agent"
    )

    assert result["intent"] == (
        "educacao_financeira"
    )

    assert result["task_status"] == (
        "completed"
    )

    assert result[
        "task_completion_score"
    ] == 1.0

    assert result[
        "missing_requirements"
    ] == []

    assert (
        "agent_execution"
        in result[
            "completed_requirements"
        ]
    )

    assert (
        "rag_retrieval_executed"
        in result[
            "completed_requirements"
        ]
    )

    assert (
        "response_generation"
        in result[
            "completed_requirements"
        ]
    )

    assert any(
        item.get("tool")
        == RAG_TOOL_NAME
        and item.get("status")
        == "success"
        for item in result[
            "tool_results"
        ]
        if isinstance(item, dict)
    )

    rag_execution = result[
        "structured_response"
    ]["rag_execution"]

    assert (
        rag_execution[
            "retrieved_documents"
        ]
        == 1
    )

    assert rag_execution[
        "retrieval_context"
    ]

    assert (
        "task_completion:completed:1.0"
        in result["trace"]
    )



def test_task_completion_evidence_is_exposed():
    result = executar_nucleo_inna(
        (
            "Explique a diferença entre "
            "gastos fixos e variáveis."
        ),
        usuario_id="task-evidence-user",
        idioma="pt",
        moeda="BRL",
    )

    evidence = result[
        "task_completion_evidence"
    ]

    assert evidence["intent"]
    assert evidence["agent"]
    assert evidence["has_response"] is True

    assert isinstance(
        evidence["tool_results_count"],
        int,
    )

from __future__ import annotations

from src.agents.task_completion_node import (
    task_completion_node,
)


def test_financial_task_is_completed():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": ("Seu diagnóstico financeiro foi calculado."),
            "structured_response": {
                "agent_response": "ok",
                "financial_input_resolution": {
                    "ready": True,
                    "missing_fields": [],
                },
            },
            "tool_results": [
                {
                    "tool": ("calcular_diagnostico_financeiro"),
                    "status": "success",
                    "ok": True,
                }
            ],
            "errors": [],
            "trace": [],
        }
    )

    assert result["task_status"] == "completed"
    assert result["task_completion_score"] == 1.0

    assert result["completed_requirements"] == [
        "agent_execution",
        "financial_inputs_resolved",
        "financial_calculation_executed",
        "response_generation",
    ]


def test_task_requires_user_input():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": ("Para continuar, preciso que você informe os gastos fixos."),
            "structured_response": {},
            "tool_results": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["task_status"] == "needs_user_input"

    assert result["task_block_reason"]


def test_task_fails_when_state_has_errors():
    result = task_completion_node(
        {
            "intent": "consulta_rag",
            "current_agent": "rag_agent",
            "response": "",
            "structured_response": {},
            "tool_results": [],
            "errors": ["Falha ao recuperar documentos."],
            "trace": [],
        }
    )

    assert result["task_status"] == "failed"

    assert "falha" in result["task_block_reason"].lower()


def test_report_task_requires_report_generation():
    result = task_completion_node(
        {
            "intent": "relatorio",
            "current_agent": "report_agent",
            "response": "Relatório preparado.",
            "structured_response": {
                "report": {
                    "status": "ready",
                }
            },
            "tool_results": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["task_status"] == "completed"

    assert "report_generation" in result["completed_requirements"]


def test_task_completion_adds_trace():
    result = task_completion_node(
        {
            "intent": "educacao_financeira",
            "current_agent": "education_agent",
            "response": (
                "A reserva de emergência protege "
                "o orçamento contra despesas inesperadas "
                "e reduz a necessidade de dívidas."
            ),
            "structured_response": {
                "rag_execution": {
                    "retrieved_documents": 2,
                    "sources": [
                        "guia-reserva.md",
                    ],
                }
            },
            "tool_results": [
                {
                    "tool": ("buscar_conhecimento_rag"),
                    "status": "success",
                    "ok": True,
                }
            ],
            "errors": [],
            "trace": [
                "agent:education_agent",
            ],
        }
    )

    assert result["trace"][0] == ("agent:education_agent")

    assert result["trace"][-1].startswith("task_completion:completed:")


def test_current_agent_is_inferred_from_next_node():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "response": "Diagnóstico concluído.",
            "structured_response": {},
            "tool_results": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["current_agent"] == ("financial_agent")

    assert result["task_completion_evidence"]["agent"] == "financial_agent"

    assert result["task_status"] == "partially_completed"

    assert result["task_completion_score"] == 0.5

    assert result["completed_requirements"] == [
        "agent_execution",
        "response_generation",
    ]

    assert result["missing_requirements"] == [
        "financial_inputs_resolved",
        "financial_calculation_executed",
    ]


def test_current_agent_is_inferred_from_trace():
    result = task_completion_node(
        {
            "intent": "educacao_financeira",
            "response": "Resposta educativa.",
            "structured_response": {},
            "tool_results": [],
            "errors": [],
            "trace": [
                "context_builder:0_messages",
                "agent:education_agent",
            ],
        }
    )

    assert result["current_agent"] == ("education_agent")

    assert result["task_completion_evidence"]["agent"] == "education_agent"


def test_explicit_current_agent_has_priority():
    result = task_completion_node(
        {
            "intent": "consulta_rag",
            "current_agent": "rag_agent",
            "next_node": "financial_agent",
            "response": "Resposta baseada na base.",
            "structured_response": {},
            "tool_results": [],
            "errors": [],
            "trace": [
                "agent:financial_agent",
            ],
        }
    )

    assert result["current_agent"] == ("rag_agent")


def test_incomplete_financial_task_has_partial_score():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": ("Preciso que você informe os gastos fixos."),
            "structured_response": {
                "financial_input_resolution": {
                    "ready": False,
                    "missing_fields": [
                        "gastos_fixos",
                    ],
                },
            },
            "tool_results": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["task_status"] == "needs_user_input"

    assert result["task_completion_score"] == 0.5

    assert result["completed_requirements"] == [
        "agent_execution",
        "response_generation",
    ]

    assert result["missing_requirements"] == [
        "financial_inputs_resolved",
        "financial_calculation_executed",
    ]


def test_financial_inputs_without_calculation_are_partial():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": ("Os dados foram recebidos, mas o cálculo não foi executado."),
            "structured_response": {
                "financial_input_resolution": {
                    "ready": True,
                    "missing_fields": [],
                },
            },
            "tool_results": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["task_status"] == "partially_completed"

    assert result["task_completion_score"] == 0.75

    assert result["missing_requirements"] == ["financial_calculation_executed"]


def test_failed_financial_tool_is_not_completion_evidence():
    result = task_completion_node(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": "Não foi possível calcular.",
            "structured_response": {
                "financial_input_resolution": {
                    "ready": True,
                    "missing_fields": [],
                },
            },
            "tool_results": [
                {
                    "tool": ("calcular_diagnostico_financeiro"),
                    "status": "failed",
                    "ok": False,
                }
            ],
            "errors": [],
            "trace": [],
        }
    )

    assert "financial_calculation_executed" not in result["completed_requirements"]

    assert result["task_completion_score"] == 0.75

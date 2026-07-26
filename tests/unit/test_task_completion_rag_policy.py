from src.agents.task_completion_node import (
    task_completion_node,
)


def _base_state():
    return {
        "intent": "educacao_financeira",
        "current_agent": "education_agent",
        "response": "",
        "tool_results": [],
        "structured_response": {},
        "trace": [],
        "errors": [],
    }


def test_placeholder_is_not_a_completed_response():
    state = _base_state()
    state["response"] = (
        "A solicitação foi encaminhada para o agente de educação financeira."
    )

    result = task_completion_node(state)

    assert result["task_status"] != "completed"

    assert "response_generation" in (result["missing_requirements"])

    assert "rag_retrieval_executed" in (result["missing_requirements"])


def test_education_requires_rag_evidence():
    state = _base_state()
    state["response"] = (
        "Gastos fixos são recorrentes e gastos "
        "variáveis mudam conforme o consumo mensal."
    )

    result = task_completion_node(state)

    assert result["task_status"] != "completed"

    assert "rag_retrieval_executed" in (result["missing_requirements"])


def test_education_completes_with_real_rag_evidence():
    state = _base_state()

    state["response"] = (
        "Gastos fixos são despesas recorrentes, "
        "enquanto gastos variáveis mudam ao longo "
        "do mês. A reserva de emergência protege "
        "o orçamento em situações inesperadas."
    )

    state["tool_results"] = [
        {
            "tool": "buscar_conhecimento_rag",
            "status": "success",
            "ok": True,
            "duration_ms": 100,
        }
    ]

    state["structured_response"] = {
        "rag_execution": {
            "status": "success",
            "ok": True,
            "retrieved_documents": 2,
            "sources": [
                "guia-financeiro.md",
            ],
        }
    }

    result = task_completion_node(state)

    assert result["task_status"] == "completed"
    assert result["task_completion_score"] == 1.0
    assert not result["missing_requirements"]

from src.agents.adaptive_gateway_node import (
    adaptive_gateway_node,
)
from src.agents.execution_governance import (
    apply_execution_governance,
)


def test_simple_budget_limits_execution_to_one_agent():
    adaptive = adaptive_gateway_node(
        {
            "user_message": (
                "Explique reserva de emergência."
            ),
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.89,
            "use_rag": True,
        }
    )

    assert (
        adaptive["adaptive_route_type"]
        == "simple"
    )
    assert adaptive["max_execution_steps"] == 1
    assert adaptive["max_handoffs"] == 1

    state = {
        "next_node": "rag_agent",
        "route_history": [],
        "execution_steps": 0,
        "max_execution_steps": (
            adaptive["max_execution_steps"]
        ),
        "max_same_agent_visits": 2,
    }

    first = apply_execution_governance(
        state
    )

    assert first["next_node"] == "rag_agent"
    assert first["execution_steps"] == 1
    assert (
        first["execution_budget_exceeded"]
        is False
    )


def test_simple_budget_blocks_second_agent_execution():
    adaptive = adaptive_gateway_node(
        {
            "user_message": (
                "Explique reserva de emergência."
            ),
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "confidence": 0.89,
            "use_rag": True,
        }
    )

    state = {
        "next_node": "education_agent",
        "route_history": [],
        "execution_steps": 1,
        "max_execution_steps": (
            adaptive["max_execution_steps"]
        ),
        "max_same_agent_visits": 2,
    }

    blocked = apply_execution_governance(
        state
    )

    assert (
        blocked["next_node"]
        == "fallback_agent"
    )
    assert (
        blocked["execution_budget_exceeded"]
        is True
    )
    assert (
        blocked["governance_reason"]
        == "execution_step_budget_exceeded"
    )


def test_complex_budget_allows_multiple_agents():
    adaptive = adaptive_gateway_node(
        {
            "user_message": (
                "Analise minhas finanças e depois "
                "gere um relatório."
            ),
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "confidence": 0.97,
            "use_database": True,
            "generate_report": True,
        }
    )

    assert (
        adaptive["adaptive_route_type"]
        == "complex"
    )
    assert adaptive["max_execution_steps"] == 5
    assert adaptive["max_handoffs"] == 3

    state = {
        "next_node": "report_agent",
        "route_history": [],
        "execution_steps": 1,
        "max_execution_steps": (
            adaptive["max_execution_steps"]
        ),
        "max_same_agent_visits": 2,
    }

    result = apply_execution_governance(
        state
    )

    assert result["next_node"] == "report_agent"
    assert result["execution_steps"] == 2
    assert (
        result["execution_budget_exceeded"]
        is False
    )


def test_complex_budget_blocks_after_five_executions():
    adaptive = adaptive_gateway_node(
        {
            "user_message": (
                "Analise minhas finanças e depois "
                "gere um relatório."
            ),
            "intent": "diagnostico_financeiro",
            "next_node": "financial_agent",
            "confidence": 0.97,
            "use_database": True,
            "generate_report": True,
        }
    )

    state = {
        "next_node": "report_agent",
        "route_history": [],
        "execution_steps": 5,
        "max_execution_steps": (
            adaptive["max_execution_steps"]
        ),
        "max_same_agent_visits": 2,
    }

    result = apply_execution_governance(
        state
    )

    assert (
        result["next_node"]
        == "fallback_agent"
    )
    assert (
        result["execution_budget_exceeded"]
        is True
    )

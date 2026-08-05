from __future__ import annotations

from src.agents.graph import (
    _criar_estado_inicial,
    criar_builder_inna,
)
from src.agents.execution_governance import (
    DEFAULT_MAX_EXECUTION_STEPS,
    DEFAULT_MAX_SAME_AGENT_VISITS,
)


def test_graph_contains_governance_node():
    builder = criar_builder_inna()

    assert "execution_governance" in builder.nodes


def test_supervisor_routes_through_governance():
    builder = criar_builder_inna()

    graph = builder.compile()

    representation = str(graph.get_graph().to_json())

    assert "supervisor" in representation
    assert "execution_governance" in representation


def test_initial_state_contains_governance_fields():
    state = _criar_estado_inicial(
        "Preciso organizar meu orçamento",
        thread_id="thread-test",
        usuario_id="user-test",
        idioma="pt",
        moeda="BRL",
    )

    assert state["execution_steps"] == 0

    assert state["max_execution_steps"] == DEFAULT_MAX_EXECUTION_STEPS

    assert state["max_same_agent_visits"] == DEFAULT_MAX_SAME_AGENT_VISITS

    assert not state["loop_detected"]

    assert not state["execution_budget_exceeded"]

    assert state["governance_reason"] == ""
    assert state["governance_decision"] == {}


def test_governance_routes_allowed_agent():
    builder = criar_builder_inna()
    graph = builder.compile()

    result = graph.invoke(
        {
            "user_message": "Quero educação financeira",
            "user_id": "user-test",
            "language": "pt",
            "currency": "BRL",
            "thread_id": "thread-test",
            "conversation_history": [],
            "context": {},
            "tool_results": [],
            "errors": [],
            "route_history": [],
            "execution_steps": 0,
            "max_execution_steps": 8,
            "max_same_agent_visits": 2,
            "loop_detected": False,
            "execution_budget_exceeded": False,
            "governance_reason": "",
            "governance_decision": {},
            "trace": [],
        }
    )

    assert result["execution_steps"] == 1

    assert result["governance_reason"] == "route_allowed"

    assert result["governance_decision"]

    assert any(str(item).startswith("governance:") for item in result["trace"])


def test_governance_blocks_exhausted_budget():
    from src.agents.execution_governance import (
        apply_execution_governance,
    )

    update = apply_execution_governance(
        {
            "next_node": "rag_agent",
            "route_history": [],
            "execution_steps": 3,
            "max_execution_steps": 3,
            "max_same_agent_visits": 2,
            "trace": [],
            "errors": [],
        }
    )

    assert update["next_node"] == "fallback_agent"

    assert update["execution_budget_exceeded"]

    assert update["governance_reason"] == "execution_step_budget_exceeded"

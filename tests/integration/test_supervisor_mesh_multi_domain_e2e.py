from __future__ import annotations

from src.agents.supervisor_mesh_node import (
    supervisor_mesh_node,
)
from src.agents.team_router import (
    team_router_node,
)
from src.agents.team_supervisor import (
    financial_team_supervisor_node,
    knowledge_team_supervisor_node,
)


def _base_state():
    return {
        "intent": "diagnostico_financeiro",
        "adaptive_multi_domain": True,
        "adaptive_target_agent": "financial_agent",
        "adaptive_budget": {
            "max_supervisors": 3,
            "max_agents": 5,
            "max_a2a_messages": 6,
            "max_handoffs": 3,
            "max_rounds": 2,
        },
        "use_database": True,
        "use_rag": True,
        "generate_report": False,
        "next_node": "financial_agent",
        "current_team": "",
        "team_requested_agent": "",
        "supervisor_mesh_history": [],
        "supervisor_mesh_visited_supervisors": [],
        "supervisor_mesh_visit_history": [],
        "root_supervisor_visits": 0,
        "max_root_supervisor_visits": 3,
        "structured_response": {},
        "trace": [],
    }


def test_financial_and_knowledge_supervisors_collaborate():
    state = _base_state()

    state.update(
        supervisor_mesh_node(
            state
        )
    )

    assert (
        state["supervisor_mesh_active"]
        is True
    )

    assert state[
        "supervisor_mesh_supervisors"
    ] == [
        "financial_team_supervisor",
        "knowledge_team_supervisor",
    ]

    # Primeira etapa: domínio financeiro.
    state.update(
        team_router_node(
            state
        )
    )

    assert (
        state["team_supervisor"]
        == "financial_team_supervisor"
    )

    assert state[
        "supervisor_mesh_visited_supervisors"
    ] == [
        "financial_team_supervisor",
    ]

    state.update(
        financial_team_supervisor_node(
            state
        )
    )

    assert (
        state["next_node"]
        == "financial_agent"
    )

    # Segunda etapa: handoff governado para conhecimento.
    state["handoff_current"] = {
        "status": "requested",
        "from_agent": "financial_agent",
        "to_agent": "rag_agent",
    }

    state.update(
        team_router_node(
            state
        )
    )

    assert (
        state["team_supervisor"]
        == "knowledge_team_supervisor"
    )

    assert state[
        "supervisor_mesh_visited_supervisors"
    ] == [
        "financial_team_supervisor",
        "knowledge_team_supervisor",
    ]

    assert (
        state["supervisor_mesh_visited_count"]
        == 2
    )

    state.update(
        knowledge_team_supervisor_node(
            state
        )
    )

    assert (
        state["next_node"]
        == "rag_agent"
    )

    assert (
        state["team_requires_root_supervisor"]
        is False
    )


def test_unplanned_third_supervisor_is_blocked():
    state = _base_state()

    state.update(
        supervisor_mesh_node(
            state
        )
    )

    state.update(
        team_router_node(
            state
        )
    )

    state["handoff_current"] = {
        "status": "requested",
        "from_agent": "financial_agent",
        "to_agent": "fallback_agent",
    }

    result = team_router_node(
        state
    )

    assert (
        result["supervisor_mesh_status"]
        == "blocked"
    )

    assert (
        result["team_requested_agent"]
        == "fallback_agent"
    )

    assert (
        result["team_routing_reason"]
        == "supervisor_mesh_unplanned_supervisor"
    )


def test_mesh_history_contains_only_operational_metadata():
    state = _base_state()

    state["user_message"] = (
        "informacao privada do usuario"
    )

    state.update(
        supervisor_mesh_node(
            state
        )
    )

    state.update(
        team_router_node(
            state
        )
    )

    serialized = str(
        state[
            "supervisor_mesh_history"
        ]
    ) + str(
        state[
            "supervisor_mesh_visit_history"
        ]
    )

    assert (
        "informacao privada do usuario"
        not in serialized
    )

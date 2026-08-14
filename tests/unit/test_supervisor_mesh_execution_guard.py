from __future__ import annotations

from src.agents.supervisor_mesh_node import (
    evaluate_supervisor_mesh_visit,
)
from src.agents.team_router import (
    team_router_node,
)


def _mesh_state():
    return {
        "supervisor_mesh_active": True,
        "supervisor_mesh_status": "planned",
        "supervisor_mesh_plan": {
            "participant_supervisors": [
                "financial_team_supervisor",
                "knowledge_team_supervisor",
            ],
            "max_supervisors": 2,
        },
        "supervisor_mesh_visited_supervisors": [],
        "supervisor_mesh_visit_history": [],
    }


def test_inactive_mesh_does_not_restrict_router():
    result = evaluate_supervisor_mesh_visit(
        {
            "supervisor_mesh_active": False,
        },
        "support_team_supervisor",
    )

    assert result["allowed"] is True
    assert (
        result["reason"]
        == "supervisor_mesh_inactive"
    )


def test_first_planned_supervisor_consumes_one_slot():
    result = evaluate_supervisor_mesh_visit(
        _mesh_state(),
        "financial_team_supervisor",
    )

    assert result["allowed"] is True
    assert result[
        "visited_supervisors"
    ] == [
        "financial_team_supervisor",
    ]
    assert result["visited_count"] == 1


def test_second_planned_supervisor_consumes_second_slot():
    state = _mesh_state()
    state[
        "supervisor_mesh_visited_supervisors"
    ] = [
        "financial_team_supervisor",
    ]

    result = evaluate_supervisor_mesh_visit(
        state,
        "knowledge_team_supervisor",
    )

    assert result["allowed"] is True
    assert result["visited_count"] == 2


def test_revisit_does_not_consume_new_supervisor_slot():
    state = _mesh_state()
    state[
        "supervisor_mesh_visited_supervisors"
    ] = [
        "financial_team_supervisor",
    ]

    result = evaluate_supervisor_mesh_visit(
        state,
        "financial_team_supervisor",
    )

    assert result["allowed"] is True
    assert result["visited_count"] == 1
    assert (
        result["reason"]
        == "supervisor_mesh_supervisor_revisit"
    )


def test_unplanned_supervisor_is_denied():
    result = evaluate_supervisor_mesh_visit(
        _mesh_state(),
        "support_team_supervisor",
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "supervisor_mesh_unplanned_supervisor"
    )


def test_active_mesh_without_plan_fails_closed():
    result = evaluate_supervisor_mesh_visit(
        {
            "supervisor_mesh_active": True,
        },
        "financial_team_supervisor",
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "supervisor_mesh_plan_missing"
    )


def test_execution_budget_is_enforced_again():
    state = _mesh_state()

    state["supervisor_mesh_plan"] = {
        "participant_supervisors": [
            "financial_team_supervisor",
            "knowledge_team_supervisor",
        ],
        "max_supervisors": 1,
    }

    state[
        "supervisor_mesh_visited_supervisors"
    ] = [
        "financial_team_supervisor",
    ]

    result = evaluate_supervisor_mesh_visit(
        state,
        "knowledge_team_supervisor",
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "supervisor_mesh_execution_budget_exceeded"
    )


def test_team_router_records_financial_mesh_visit():
    state = _mesh_state()

    state.update(
        {
            "next_node": "financial_agent",
            "structured_response": {},
            "trace": [],
        }
    )

    result = team_router_node(
        state
    )

    assert result[
        "team_supervisor"
    ] == "financial_team_supervisor"

    assert result[
        "supervisor_mesh_visited_supervisors"
    ] == [
        "financial_team_supervisor",
    ]


def test_team_router_allows_cross_team_planned_visit():
    state = _mesh_state()

    state.update(
        {
            "team_requested_agent": (
                "rag_agent"
            ),
            "supervisor_mesh_visited_supervisors": [
                "financial_team_supervisor",
            ],
            "structured_response": {},
            "trace": [],
        }
    )

    result = team_router_node(
        state
    )

    assert result[
        "team_supervisor"
    ] == "knowledge_team_supervisor"

    assert result[
        "supervisor_mesh_visited_count"
    ] == 2


def test_team_router_blocks_unplanned_team():
    state = _mesh_state()

    state.update(
        {
            "team_requested_agent": (
                "fallback_agent"
            ),
            "structured_response": {},
            "trace": [],
        }
    )

    result = team_router_node(
        state
    )

    assert (
        result["supervisor_mesh_status"]
        == "blocked"
    )

    assert result[
        "team_requested_agent"
    ] == "fallback_agent"

    assert (
        result["team_routing_reason"]
        == "supervisor_mesh_unplanned_supervisor"
    )


def test_visit_history_does_not_copy_user_message():
    state = _mesh_state()

    state["user_message"] = (
        "segredo que nao deve ser copiado"
    )

    result = evaluate_supervisor_mesh_visit(
        state,
        "financial_team_supervisor",
    )

    assert (
        "segredo que nao deve ser copiado"
        not in str(
            result["visit_history"]
        )
    )

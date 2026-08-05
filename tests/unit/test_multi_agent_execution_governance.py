from __future__ import annotations

from src.agents.execution_governance import (
    SAFE_FALLBACK_AGENT,
    apply_execution_governance,
    count_agent_visits,
    evaluate_execution_governance,
)


def test_counts_routes_from_dict_records():
    history = [
        {
            "next_node": "rag_agent",
        },
        {
            "next_node": "financial_agent",
        },
        {
            "next_node": "rag_agent",
        },
    ]

    assert (
        count_agent_visits(
            history,
            "rag_agent",
        )
        == 2
    )


def test_counts_routes_from_string_records():
    history = [
        "rag_agent",
        "financial_agent",
        "rag_agent",
    ]

    assert (
        count_agent_visits(
            history,
            "rag_agent",
        )
        == 2
    )


def test_allows_route_inside_limits():
    decision = evaluate_execution_governance(
        requested_agent="rag_agent",
        route_history=[],
        execution_steps=0,
        max_execution_steps=5,
        max_same_agent_visits=2,
    )

    assert decision.allowed
    assert decision.selected_agent == "rag_agent"
    assert decision.current_step == 1
    assert not decision.loop_detected
    assert not decision.budget_exceeded
    assert decision.reason == "route_allowed"


def test_blocks_execution_step_budget():
    decision = evaluate_execution_governance(
        requested_agent="financial_agent",
        route_history=[],
        execution_steps=3,
        max_execution_steps=3,
    )

    assert not decision.allowed
    assert decision.selected_agent == SAFE_FALLBACK_AGENT
    assert decision.current_step == 4
    assert decision.budget_exceeded
    assert not decision.loop_detected
    assert decision.reason == "execution_step_budget_exceeded"


def test_detects_repeated_agent_route():
    history = [
        {
            "next_node": "report_agent",
        },
        {
            "next_node": "report_agent",
        },
    ]

    decision = evaluate_execution_governance(
        requested_agent="report_agent",
        route_history=history,
        execution_steps=2,
        max_execution_steps=8,
        max_same_agent_visits=2,
    )

    assert not decision.allowed
    assert decision.loop_detected
    assert not decision.budget_exceeded
    assert decision.selected_agent == SAFE_FALLBACK_AGENT
    assert decision.repeated_visits == 3


def test_fallback_route_does_not_trigger_loop():
    history = [
        {
            "next_node": SAFE_FALLBACK_AGENT,
        },
        {
            "next_node": SAFE_FALLBACK_AGENT,
        },
        {
            "next_node": SAFE_FALLBACK_AGENT,
        },
    ]

    decision = evaluate_execution_governance(
        requested_agent=SAFE_FALLBACK_AGENT,
        route_history=history,
        execution_steps=1,
        max_execution_steps=8,
        max_same_agent_visits=1,
    )

    assert decision.allowed
    assert not decision.loop_detected


def test_invalid_limits_use_safe_defaults():
    decision = evaluate_execution_governance(
        requested_agent="rag_agent",
        execution_steps=0,
        max_execution_steps="invalid",
        max_same_agent_visits=None,
    )

    assert decision.allowed
    assert decision.max_steps >= 1
    assert decision.max_same_agent_visits >= 1


def test_apply_governance_updates_state_fields():
    update = apply_execution_governance(
        {
            "next_node": "financial_agent",
            "route_history": [],
            "execution_steps": 0,
            "trace": [],
            "errors": [],
        }
    )

    assert update["next_node"] == "financial_agent"
    assert update["execution_steps"] == 1
    assert not update["loop_detected"]
    assert not update["execution_budget_exceeded"]
    assert update["governance_reason"] == "route_allowed"
    assert update["governance_decision"]
    assert update["trace"] == [
        ("governance:route_allowed:financial_agent->financial_agent")
    ]


def test_apply_governance_blocks_loop_safely():
    update = apply_execution_governance(
        {
            "next_node": "rag_agent",
            "route_history": [
                {
                    "next_node": "rag_agent",
                },
                {
                    "next_node": "rag_agent",
                },
            ],
            "execution_steps": 2,
            "max_same_agent_visits": 2,
            "trace": [],
            "errors": [],
        }
    )

    assert update["next_node"] == SAFE_FALLBACK_AGENT
    assert update["loop_detected"]
    assert update["errors"]
    assert update["governance_reason"] == "repeated_agent_route_detected"

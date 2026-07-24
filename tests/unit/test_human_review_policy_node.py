from __future__ import annotations

import pytest

from src.agents.human_review_policy_node import (
    human_review_policy_node,
    select_route_after_human_review_policy,
)


def _base_state(
    **overrides,
):
    state = {
        "thread_id": "thread-node-001",
        "user_id": "user-node-001",
        "current_agent": "financial_agent",
        "intent": "diagnostico_financeiro",
        "task_status": "completed",
        "task_completion_score": 0.95,
        "confidence": 0.95,
        "nivel_risco": "Baixo",
        "missing_requirements": [],
        "structured_response": {},
        "trace": [],
        "human_review_enabled": True,
        "human_review_required": False,
        "human_review_current": {},
        "human_review_history": [],
        "human_review_policy_decision": {},
        "human_review_resume_payload": {},
        "human_review_status": "",
        "human_review_count": 0,
        "max_human_reviews": 3,
        "human_review_limit_exceeded": False,
    }

    state.update(
        overrides
    )

    return state


def test_safe_state_does_not_create_review():
    result = human_review_policy_node(
        _base_state()
    )

    assert (
        result["human_review_required"]
        is False
    )

    assert result[
        "human_review_policy_decision"
    ]["trigger"] == "not_required"

    assert result["trace"][-1] == (
        "human_review_policy:"
        "not_required:not_required"
    )


def test_high_risk_creates_review():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Alto"
        )
    )

    review = result[
        "human_review_current"
    ]

    assert (
        result["human_review_required"]
        is True
    )

    assert (
        result["human_review_status"]
        == "requested"
    )

    assert review["status"] == "requested"
    assert review["risk_level"] == "high"
    assert review["trigger"] == (
        "high_financial_risk"
    )

    assert (
        result["human_review_count"]
        == 1
    )


def test_created_review_is_added_to_history():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Crítico"
        )
    )

    history = result[
        "human_review_history"
    ]

    assert len(history) == 1

    assert (
        history[0]["review_id"]
        == result[
            "human_review_current"
        ]["review_id"]
    )


def test_existing_pending_review_is_not_duplicated():
    current = {
        "review_id": "review-existing",
        "status": "waiting",
        "trigger": "high_financial_risk",
    }

    result = human_review_policy_node(
        _base_state(
            nivel_risco="Crítico",
            human_review_required=True,
            human_review_current=current,
            human_review_status="waiting",
            human_review_count=1,
        )
    )

    assert result[
        "human_review_current"
    ] == current

    assert (
        result["human_review_required"]
        is True
    )

    assert (
        "human_review_count"
        not in result
    )


def test_resolved_review_is_not_recreated():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Crítico",
            human_review_current={
                "review_id": "review-approved",
                "status": "approved",
            },
            human_review_status="approved",
            human_review_count=1,
        )
    )

    assert (
        result["human_review_required"]
        is False
    )

    assert result[
        "human_review_policy_decision"
    ]["trigger"] == (
        "review_already_resolved"
    )


def test_review_limit_blocks_new_request():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Crítico",
            human_review_count=3,
            max_human_reviews=3,
        )
    )

    assert (
        result["human_review_required"]
        is False
    )

    assert (
        result[
            "human_review_limit_exceeded"
        ]
        is True
    )

    assert (
        result["human_review_status"]
        == "failed"
    )


def test_invalid_max_reviews_uses_default():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Alto",
            max_human_reviews="invalid",
        )
    )

    assert (
        result["human_review_count"]
        == 1
    )

    assert result[
        "human_review_current"
    ]["metadata"][
        "max_human_reviews"
    ] == 3


def test_review_metadata_contains_sequence():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Alto",
            human_review_count=1,
            max_human_reviews=4,
        )
    )

    metadata = result[
        "human_review_current"
    ]["metadata"]

    assert metadata[
        "review_number"
    ] == 2

    assert metadata[
        "max_human_reviews"
    ] == 4


def test_structured_response_contains_policy():
    result = human_review_policy_node(
        _base_state(
            nivel_risco="Alto",
            structured_response={
                "existing": True,
            },
        )
    )

    structured = result[
        "structured_response"
    ]

    assert structured[
        "existing"
    ] is True

    assert (
        "human_review_policy_decision"
        in structured
    )

    assert (
        "human_review_request"
        in structured
    )


def test_original_state_is_not_mutated():
    state = _base_state(
        nivel_risco="Alto"
    )

    result = human_review_policy_node(
        state
    )

    assert state[
        "human_review_history"
    ] == []

    assert state[
        "human_review_current"
    ] == {}

    assert result[
        "human_review_current"
    ]


def test_missing_thread_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="thread_id",
    ):
        human_review_policy_node(
            _base_state(
                thread_id="",
                nivel_risco="Alto",
            )
        )


def test_route_to_interrupt_when_review_required():
    assert (
        select_route_after_human_review_policy({
            "human_review_required": True,
        })
        == "human_review_interrupt"
    )


def test_route_to_handoff_when_review_not_required():
    assert (
        select_route_after_human_review_policy({
            "human_review_required": False,
        })
        == "handoff_coordinator"
    )
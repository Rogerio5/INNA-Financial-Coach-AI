from __future__ import annotations

from src.agents.adaptive_gateway_node import (
    adaptive_gateway_node,
)
from src.agents.human_review_policy_node import (
    human_review_policy_node,
    select_route_after_human_review_policy,
)


def _base_state(
    **overrides,
):
    state = {
        "thread_id": (
            "thread-week5-security-001"
        ),
        "user_id": (
            "user-week5-security-001"
        ),
        "user_message": (
            "Analise minha situação financeira."
        ),
        "intent": (
            "diagnostico_financeiro"
        ),
        "next_node": "financial_agent",
        "current_agent": "financial_agent",
        "confidence": 0.95,

        "adaptive_risk": "low",
        "adaptive_multi_domain": False,
        "handoff_required": False,

        "task_status": "completed",
        "task_completion_score": 0.95,
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


def _run_adaptive_gateway(
    state,
):
    updated = dict(
        state
    )

    updated.update(
        adaptive_gateway_node(
            updated
        )
    )

    return updated


def test_adaptive_critical_risk_forces_hitl_even_when_disabled():
    state = _run_adaptive_gateway(
        _base_state(
            adaptive_risk="critical",
            nivel_risco="Baixo",
            human_review_enabled=False,
        )
    )

    assert (
        state["adaptive_risk"]
        == "critical"
    )

    result = human_review_policy_node(
        state
    )

    assert (
        result["human_review_required"]
        is True
    )

    assert (
        result["human_review_status"]
        == "requested"
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["trigger"]
        == "critical_financial_risk"
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["risk_level"]
        == "critical"
    )

    assert (
        select_route_after_human_review_policy(
            result
        )
        == "human_review_interrupt"
    )


def test_critical_review_limit_fails_closed():
    state = _run_adaptive_gateway(
        _base_state(
            adaptive_risk="critical",
            human_review_enabled=False,
            human_review_count=3,
            max_human_reviews=3,
        )
    )

    result = human_review_policy_node(
        state
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

    assert (
        result[
            "human_review_policy_decision"
        ]["requires_review"]
        is True
    )

    assert (
        select_route_after_human_review_policy(
            result
        )
        == "conversation_summary"
    )


def test_low_risk_disabled_policy_keeps_normal_flow():
    state = _run_adaptive_gateway(
        _base_state(
            adaptive_risk="low",
            nivel_risco="Baixo",
            human_review_enabled=False,
        )
    )

    result = human_review_policy_node(
        state
    )

    assert (
        result["human_review_required"]
        is False
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["trigger"]
        == "policy_disabled"
    )

    assert (
        select_route_after_human_review_policy(
            result
        )
        == "handoff_coordinator"
    )


def test_highest_risk_signal_controls_review():
    state = _run_adaptive_gateway(
        _base_state(
            adaptive_risk="medium",
            nivel_risco="Alto",
        )
    )

    result = human_review_policy_node(
        state
    )

    assert (
        result["human_review_required"]
        is True
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["risk_level"]
        == "high"
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["trigger"]
        == "high_financial_risk"
    )


def test_external_confirmation_is_mandatory_even_when_disabled():
    state = _base_state(
        adaptive_risk="low",
        nivel_risco="Baixo",
        human_review_enabled=False,
        approval_required=True,
    )

    result = human_review_policy_node(
        state
    )

    assert (
        result["human_review_required"]
        is True
    )

    assert (
        result[
            "human_review_policy_decision"
        ]["trigger"]
        == "external_action_confirmation"
    )

    assert (
        select_route_after_human_review_policy(
            result
        )
        == "human_review_interrupt"
    )


def test_human_review_payload_does_not_copy_raw_user_message():
    marker = (
        "PRIVATE_USER_MESSAGE_WEEK5_8"
    )

    state = _base_state(
        user_message=marker,
        adaptive_risk="critical",
    )

    result = human_review_policy_node(
        state
    )

    assert (
        marker
        not in str(
            result[
                "human_review_current"
            ]
        )
    )

    assert (
        marker
        not in str(
            result[
                "human_review_policy_decision"
            ]
        )
    )

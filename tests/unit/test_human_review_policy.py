from __future__ import annotations

import math

import pytest

from src.agents.human_review_policy import (
    HumanReviewPolicyError,
    evaluate_human_review_policy,
    human_review_required,
)


def _base_state(
    **overrides,
):
    state = {
        "thread_id": "thread-policy-001",
        "user_id": "user-policy-001",
        "current_agent": "financial_agent",
        "intent": "diagnostico_financeiro",
        "task_status": "completed",
        "task_completion_score": 0.95,
        "confidence": 0.95,
        "nivel_risco": "Baixo",
        "missing_requirements": [],
        "structured_response": {},
    }

    state.update(overrides)

    return state


def test_safe_state_does_not_require_review():
    decision = evaluate_human_review_policy(_base_state())

    assert decision.requires_review is False
    assert decision.trigger == "not_required"
    assert decision.risk_level == "low"


def test_helper_returns_boolean():
    assert human_review_required(_base_state(nivel_risco="Alto")) is True

    assert human_review_required(_base_state()) is False


def test_decision_as_dict_copies_payload():
    decision = evaluate_human_review_policy(_base_state())

    first = decision.as_dict()
    second = decision.as_dict()

    first["payload"]["intent"] = "changed"

    assert second["payload"]["intent"] == ("diagnostico_financeiro")


@pytest.mark.parametrize(
    "risk_value, expected",
    [
        ("Baixo", "low"),
        ("baixo", "low"),
        ("LOW", "low"),
        ("Médio", "medium"),
        ("media", "medium"),
        ("moderate", "medium"),
        ("Alto", "high"),
        ("alta", "high"),
        ("HIGH", "high"),
        ("Crítico", "critical"),
        ("critica", "critical"),
        ("severe", "critical"),
    ],
)
def test_risk_aliases_are_normalized(
    risk_value,
    expected,
):
    decision = evaluate_human_review_policy(_base_state(nivel_risco=risk_value))

    assert decision.risk_level == expected


def test_high_risk_requires_review():
    decision = evaluate_human_review_policy(_base_state(nivel_risco="Alto"))

    assert decision.requires_review is True
    assert decision.trigger == ("high_financial_risk")
    assert decision.risk_level == "high"


def test_critical_risk_requires_review():
    decision = evaluate_human_review_policy(_base_state(nivel_risco="Crítico"))

    assert decision.requires_review is True
    assert decision.trigger == ("critical_financial_risk")
    assert decision.risk_level == "critical"


def test_medium_risk_alone_does_not_require_review():
    decision = evaluate_human_review_policy(_base_state(nivel_risco="Médio"))

    assert decision.requires_review is False
    assert decision.risk_level == "medium"


def test_forced_review_has_highest_priority():
    decision = evaluate_human_review_policy(
        _base_state(
            human_review_force_required=True,
            nivel_risco="Crítico",
            external_action_requires_confirmation=True,
        )
    )

    assert decision.requires_review is True
    assert decision.trigger == "forced_review"


@pytest.mark.parametrize(
    "value",
    [
        True,
        1,
        "true",
        "sim",
        "required",
        "necessário",
    ],
)
def test_force_review_boolean_aliases(
    value,
):
    decision = evaluate_human_review_policy(
        _base_state(human_review_force_required=value)
    )

    assert decision.trigger == "forced_review"


def test_external_action_requires_confirmation():
    decision = evaluate_human_review_policy(
        _base_state(external_action_requires_confirmation=True)
    )

    assert decision.requires_review is True
    assert decision.trigger == ("external_action_confirmation")
    assert decision.risk_level == "high"


def test_tool_confirmation_nested_in_structured_response():
    decision = evaluate_human_review_policy(
        _base_state(
            structured_response={
                "tool_requires_confirmation": True,
            }
        )
    )

    assert decision.trigger == ("external_action_confirmation")


def test_explicit_data_inconsistency_requires_review():
    decision = evaluate_human_review_policy(
        _base_state(financial_data_inconsistent=True)
    )

    assert decision.requires_review is True
    assert decision.trigger == ("financial_data_inconsistency")
    assert decision.metadata["inconsistency_count"] == 1


def test_inconsistency_list_is_preserved_in_payload():
    decision = evaluate_human_review_policy(
        _base_state(
            data_inconsistencies=[
                "Renda menor que zero.",
                "Gastos duplicados.",
            ]
        )
    )

    assert decision.payload["data_inconsistencies"] == [
        "Renda menor que zero.",
        "Gastos duplicados.",
    ]


def test_missing_requirements_require_review():
    decision = evaluate_human_review_policy(
        _base_state(
            missing_requirements=[
                "renda",
                "gastos_fixos",
            ]
        )
    )

    assert decision.requires_review is True
    assert decision.trigger == ("missing_required_financial_data")
    assert decision.risk_level == "medium"
    assert decision.metadata["missing_requirement_count"] == 2


def test_missing_fields_inside_structured_response():
    decision = evaluate_human_review_policy(
        _base_state(
            structured_response={
                "missing_fields": [
                    "dividas",
                ],
            }
        )
    )

    assert decision.trigger == ("missing_required_financial_data")


@pytest.mark.parametrize(
    "confidence",
    [
        0.0,
        0.20,
        0.59,
        20,
        59,
    ],
)
def test_low_confidence_requires_review(
    confidence,
):
    decision = evaluate_human_review_policy(_base_state(confidence=confidence))

    assert decision.requires_review is True
    assert decision.trigger == "low_confidence"


@pytest.mark.parametrize(
    "confidence",
    [
        0.60,
        0.75,
        1.0,
        60,
        95,
        100,
    ],
)
def test_acceptable_confidence_does_not_require_review(
    confidence,
):
    decision = evaluate_human_review_policy(_base_state(confidence=confidence))

    assert decision.requires_review is False


def test_custom_minimum_confidence():
    decision = evaluate_human_review_policy(
        _base_state(
            confidence=0.79,
            human_review_minimum_confidence=0.80,
        )
    )

    assert decision.trigger == "low_confidence"
    assert decision.metadata["minimum_confidence"] == 0.80


@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        1.1,
        math.inf,
        math.nan,
        "invalid",
    ],
)
def test_invalid_minimum_confidence(
    value,
):
    with pytest.raises(
        HumanReviewPolicyError,
        match="human_review_minimum_confidence",
    ):
        evaluate_human_review_policy(_base_state(human_review_minimum_confidence=value))


def test_invalid_confidence_is_ignored():
    decision = evaluate_human_review_policy(_base_state(confidence="unknown"))

    assert decision.requires_review is False
    assert decision.trigger == "not_required"


def test_policy_can_be_disabled():
    decision = evaluate_human_review_policy(
        _base_state(
            human_review_enabled=False,
            nivel_risco="Crítico",
        )
    )

    assert decision.requires_review is False
    assert decision.trigger == "policy_disabled"


def test_pending_review_is_not_duplicated():
    decision = evaluate_human_review_policy(
        _base_state(
            nivel_risco="Crítico",
            human_review_current={
                "status": "waiting",
            },
        )
    )

    assert decision.requires_review is False
    assert decision.trigger == ("review_already_pending")


@pytest.mark.parametrize(
    "status",
    [
        "approved",
        "corrected",
        "rejected",
        "cancelled",
        "expired",
        "failed",
    ],
)
def test_resolved_review_is_not_duplicated(
    status,
):
    decision = evaluate_human_review_policy(
        _base_state(
            nivel_risco="Crítico",
            human_review_current={
                "status": status,
            },
        )
    )

    assert decision.requires_review is False
    assert decision.trigger == ("review_already_resolved")


def test_requested_by_uses_current_agent():
    decision = evaluate_human_review_policy(
        _base_state(
            current_agent="report_agent",
            nivel_risco="Alto",
        )
    )

    assert decision.requested_by == ("report_agent")


def test_requested_by_falls_back_to_last_agent():
    state = _base_state(
        nivel_risco="Alto",
        last_agent="rag_agent",
    )

    state.pop("current_agent")

    decision = evaluate_human_review_policy(state)

    assert decision.requested_by == "rag_agent"


def test_risk_can_be_read_from_structured_response():
    decision = evaluate_human_review_policy(
        _base_state(
            nivel_risco="",
            structured_response={
                "nivel_risco": "Alto",
            },
        )
    )

    assert decision.trigger == ("high_financial_risk")


def test_risk_can_be_read_from_financial_diagnosis():
    decision = evaluate_human_review_policy(
        _base_state(
            nivel_risco="",
            financial_diagnosis={
                "risk_level": "critical",
            },
        )
    )

    assert decision.trigger == ("critical_financial_risk")


def test_confidence_can_be_read_from_task_score():
    state = _base_state(
        confidence=None,
        task_completion_score=0.40,
    )

    decision = evaluate_human_review_policy(state)

    assert decision.trigger == "low_confidence"


def test_payload_contains_auditable_context():
    decision = evaluate_human_review_policy(_base_state(nivel_risco="Alto"))

    assert decision.payload["thread_id"] == "thread-policy-001"

    assert decision.payload["user_id"] == "user-policy-001"

    assert decision.payload["current_agent"] == "financial_agent"

    assert decision.metadata["policy_version"] == "1.0"


def test_state_must_be_mapping():
    with pytest.raises(
        HumanReviewPolicyError,
        match="Mapping",
    ):
        evaluate_human_review_policy(None)

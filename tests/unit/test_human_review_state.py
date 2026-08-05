from __future__ import annotations

from src.agents.graph import (
    _criar_estado_inicial,
)
from src.agents.state import (
    InnaAgentState,
)


def _state():
    return _criar_estado_inicial(
        "Preciso analisar minha situação financeira.",
        thread_id="thread-human-review-state",
        usuario_id="user-human-review-state",
        idioma="pt-BR",
        moeda="BRL",
    )


def test_initial_state_enables_human_review():
    state = _state()

    assert state["human_review_enabled"] is True

    assert state["human_review_required"] is False


def test_initial_state_has_empty_review_contract():
    state = _state()

    assert state["human_review_current"] == {}

    assert state["human_review_history"] == []

    assert state["human_review_policy_decision"] == {}

    assert state["human_review_resume_payload"] == {}


def test_initial_review_status_is_empty():
    state = _state()

    assert state["human_review_status"] == ""


def test_initial_review_count_is_zero():
    state = _state()

    assert state["human_review_count"] == 0

    assert state["max_human_reviews"] == 3


def test_initial_limit_is_not_exceeded():
    state = _state()

    assert state["human_review_limit_exceeded"] is False


def test_review_lists_are_independent():
    first = _state()
    second = _state()

    first["human_review_history"].append(
        {
            "review_id": "review-001",
        }
    )

    assert second["human_review_history"] == []


def test_state_annotations_include_review_fields():
    annotations = InnaAgentState.__annotations__

    expected = {
        "human_review_enabled",
        "human_review_required",
        "human_review_current",
        "human_review_history",
        "human_review_policy_decision",
        "human_review_resume_payload",
        "human_review_decision_action",
        "human_review_corrections",
        "human_review_resume_route",
        "human_review_status",
        "human_review_count",
        "max_human_reviews",
        "human_review_limit_exceeded",
    }

    assert expected.issubset(annotations)

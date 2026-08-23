from __future__ import annotations

from copy import deepcopy

import pytest

import src.agents.human_review_interrupt_node as module
from src.agents.human_review import (
    HumanReviewError,
    create_human_review_request,
)
from src.agents.human_review_interrupt_node import (
    human_review_interrupt_node,
    select_route_after_human_review_interrupt,
)


def _review(
    *,
    status="requested",
):
    review = create_human_review_request(
        review_id="review-interrupt-001",
        thread_id="thread-interrupt-001",
        requested_by="financial_agent",
        reason="Risco financeiro elevado.",
        trigger="high_financial_risk",
        risk_level="high",
        payload={
            "income": 3000,
            "expenses": 4500,
        },
        timestamp="2026-07-23T15:00:00+00:00",
    )

    review["status"] = status

    return review


def _state(
    **overrides,
):
    review = _review()

    state = {
        "thread_id": "thread-interrupt-001",
        "current_agent": "financial_agent",
        "structured_response": {
            "existing": True,
        },
        "trace": [],
        "human_review_required": True,
        "human_review_current": review,
        "human_review_history": [
            deepcopy(
                review
            )
        ],
        "human_review_status": "requested",
        "human_review_resume_payload": {},
        "human_review_decision_action": "",
        "human_review_corrections": {},
        "human_review_resume_route": "",
    }

    state.update(
        overrides
    )

    return state


def _set_resume(
    monkeypatch,
    payload,
):
    captured = {}

    def fake_interrupt(
        interrupt_payload,
    ):
        captured[
            "payload"
        ] = interrupt_payload

        return deepcopy(
            payload
        )

    monkeypatch.setattr(
        module,
        "interrupt",
        fake_interrupt,
    )

    return captured


def test_approve_review(
    monkeypatch,
):
    captured = _set_resume(
        monkeypatch,
        {
            "action": "approve",
            "reviewer_id": "user-001",
            "comment": "Dados confirmados.",
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    assert result[
        "human_review_status"
    ] == "approved"

    assert result[
        "human_review_required"
    ] is False

    assert result[
        "human_review_decision_action"
    ] == "approve"

    assert result[
        "human_review_resume_route"
    ] == "handoff_coordinator"

    assert captured[
        "payload"
    ]["review_id"] == (
        "review-interrupt-001"
    )


def test_interrupt_payload_is_auditable(
    monkeypatch,
):
    captured = _set_resume(
        monkeypatch,
        {
            "action": "approve",
            "reviewer_id": "user-001",
        },
    )

    human_review_interrupt_node(
        _state()
    )

    payload = captured[
        "payload"
    ]

    assert payload[
        "type"
    ] == "human_review"

    assert payload[
        "version"
    ] == "1.0"

    assert payload[
        "thread_id"
    ] == "thread-interrupt-001"

    assert payload[
        "risk_level"
    ] == "high"

    assert payload[
        "allowed_actions"
    ] == [
        "approve",
        "correct",
        "reject",
        "cancel",
    ]


def test_correct_review_routes_to_team_router(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "correct",
            "reviewer_id": "user-001",
            "comment": "Corrigir os gastos.",
            "corrections": {
                "expenses": 3500,
            },
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    assert result[
        "human_review_status"
    ] == "corrected"

    assert result[
        "human_review_corrections"
    ] == {
        "expenses": 3500,
    }

    assert result[
        "human_review_resume_route"
    ] == "team_router"


def test_reject_review_routes_to_summary(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "reject",
            "reviewer_id": "reviewer-001",
            "reason": "Dados não confirmados.",
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    assert result[
        "human_review_status"
    ] == "rejected"

    assert result[
        "human_review_resume_route"
    ] == "conversation_summary"


def test_cancel_review_routes_to_summary(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "cancel",
            "reviewer_id": "user-001",
            "reason": "Usuário cancelou.",
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    assert result[
        "human_review_status"
    ] == "cancelled"

    assert result[
        "human_review_resume_route"
    ] == "conversation_summary"


def test_history_is_updated_in_place(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "approve",
            "reviewer_id": "user-001",
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    history = result[
        "human_review_history"
    ]

    assert len(history) == 1

    assert history[0][
        "review_id"
    ] == "review-interrupt-001"

    assert history[0][
        "status"
    ] == "approved"


def test_original_state_is_not_mutated(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "approve",
            "reviewer_id": "user-001",
        },
    )

    state = _state()

    human_review_interrupt_node(
        state
    )

    assert state[
        "human_review_current"
    ]["status"] == "requested"

    assert state[
        "human_review_history"
    ][0]["status"] == "requested"


def test_structured_response_is_preserved(
    monkeypatch,
):
    _set_resume(
        monkeypatch,
        {
            "action": "approve",
            "reviewer_id": "user-001",
        },
    )

    result = human_review_interrupt_node(
        _state()
    )

    structured = result[
        "structured_response"
    ]

    assert structured[
        "existing"
    ] is True

    assert structured[
        "human_review_result"
    ]["status"] == "approved"


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        (
            "approve",
            "objeto",
        ),
        (
            {
                "action": "unknown",
                "reviewer_id": "user-001",
            },
            "Ação de revisão humana inválida",
        ),
        (
            {
                "action": "approve",
                "reviewer_id": "",
            },
            "reviewer_id",
        ),
        (
            {
                "action": "correct",
                "reviewer_id": "user-001",
                "corrections": {},
            },
            "pelo menos uma correção",
        ),
        (
            {
                "action": "reject",
                "reviewer_id": "user-001",
                "reason": "",
            },
            "exige reason",
        ),
    ],
)
def test_invalid_resume_payloads(
    monkeypatch,
    payload,
    expected_message,
):
    _set_resume(
        monkeypatch,
        payload,
    )

    with pytest.raises(
        HumanReviewError,
        match=expected_message,
    ):
        human_review_interrupt_node(
            _state()
        )


def test_missing_current_review_is_rejected():
    with pytest.raises(
        HumanReviewError,
        match="Não existe revisão",
    ):
        human_review_interrupt_node(
            _state(
                human_review_current={},
            )
        )


def test_invalid_pending_status_is_rejected():
    with pytest.raises(
        HumanReviewError,
        match="Status inválido",
    ):
        human_review_interrupt_node(
            _state(
                human_review_current=_review(
                    status="unknown"
                ),
            )
        )


@pytest.mark.parametrize(
    "status, expected_route",
    [
        (
            "approved",
            "handoff_coordinator",
        ),
        (
            "corrected",
            "team_router",
        ),
        (
            "rejected",
            "conversation_summary",
        ),
        (
            "cancelled",
            "conversation_summary",
        ),
        (
            "expired",
            "conversation_summary",
        ),
        (
            "failed",
            "conversation_summary",
        ),
    ],
)
def test_already_resolved_review_does_not_interrupt(
    monkeypatch,
    status,
    expected_route,
):
    def fail_interrupt(
        payload,
    ):
        raise AssertionError(
            "interrupt não deveria ser chamado."
        )

    monkeypatch.setattr(
        module,
        "interrupt",
        fail_interrupt,
    )

    result = human_review_interrupt_node(
        _state(
            human_review_current=_review(
                status=status
            ),
        )
    )

    assert result[
        "human_review_resume_route"
    ] == expected_route


@pytest.mark.parametrize(
    "route",
    [
        "handoff_coordinator",
        "team_router",
        "conversation_summary",
    ],
)
def test_route_selector_accepts_known_routes(
    route,
):
    assert (
        select_route_after_human_review_interrupt({
            "human_review_resume_route": route,
        })
        == route
    )


def test_route_selector_rejects_unknown_route():
    with pytest.raises(
        HumanReviewError,
        match="Rota de retomada",
    ):
        select_route_after_human_review_interrupt({
            "human_review_resume_route": "unknown",
        })
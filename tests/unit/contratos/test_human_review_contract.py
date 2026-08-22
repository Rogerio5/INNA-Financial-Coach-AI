from __future__ import annotations

import pytest

from src.agents.human_review import (
    HumanReviewError,
    approve_human_review,
    cancel_human_review,
    correct_human_review,
    create_human_review_request,
    expire_human_review,
    fail_human_review,
    is_terminal_human_review_status,
    mark_human_review_waiting,
    reject_human_review,
    transition_human_review,
)


def _review():
    return create_human_review_request(
        review_id="review-001",
        thread_id="thread-001",
        requested_by="financial_agent",
        reason="Risco financeiro elevado.",
        trigger="high_financial_risk",
        risk_level="high",
        payload={
            "income": 3000,
            "expenses": 4200,
        },
        metadata={
            "source": "unit_test",
        },
        timestamp="2026-07-23T12:00:00+00:00",
    )


def test_create_review_request():
    review = _review()

    assert review["review_id"] == "review-001"
    assert review["thread_id"] == "thread-001"
    assert review["status"] == "requested"
    assert review["risk_level"] == "high"
    assert review["decision"] is None
    assert review["resolved_at"] is None


def test_create_review_copies_payload():
    payload = {
        "values": [1, 2],
    }

    review = create_human_review_request(
        thread_id="thread-copy",
        requested_by="financial_agent",
        reason="Validação necessária.",
        trigger="data_validation",
        risk_level="medium",
        payload=payload,
    )

    payload["values"].append(3)

    assert review["payload"] == {
        "values": [1, 2],
    }


@pytest.mark.parametrize(
    "field_name, kwargs",
    [
        (
            "thread_id",
            {"thread_id": ""},
        ),
        (
            "requested_by",
            {"requested_by": ""},
        ),
        (
            "reason",
            {"reason": ""},
        ),
        (
            "trigger",
            {"trigger": ""},
        ),
    ],
)
def test_required_fields_are_validated(
    field_name,
    kwargs,
):
    arguments = {
        "thread_id": "thread",
        "requested_by": "financial_agent",
        "reason": "Revisão necessária.",
        "trigger": "risk",
        "risk_level": "high",
    }

    arguments.update(kwargs)

    with pytest.raises(
        HumanReviewError,
        match=field_name,
    ):
        create_human_review_request(
            **arguments
        )


def test_invalid_risk_level_is_rejected():
    with pytest.raises(
        HumanReviewError,
        match="Nível de risco inválido",
    ):
        create_human_review_request(
            thread_id="thread",
            requested_by="financial_agent",
            reason="Revisão necessária.",
            trigger="risk",
            risk_level="unknown",
        )


def test_mark_review_waiting():
    waiting = mark_human_review_waiting(
        _review(),
        timestamp="2026-07-23T12:01:00+00:00",
    )

    assert waiting["status"] == "waiting"
    assert waiting["resolved_at"] is None


def test_approve_requested_review():
    approved = approve_human_review(
        _review(),
        reviewer_id="user-001",
        comment="Dados confirmados.",
        timestamp="2026-07-23T12:02:00+00:00",
    )

    assert approved["status"] == "approved"
    assert approved["resolved_at"] is not None
    assert approved["decision"]["action"] == "approve"
    assert (
        approved["decision"]["reviewer_id"]
        == "user-001"
    )


def test_approve_waiting_review():
    waiting = mark_human_review_waiting(
        _review()
    )

    approved = approve_human_review(
        waiting,
        reviewer_id="reviewer-001",
    )

    assert approved["status"] == "approved"


def test_correct_review():
    corrected = correct_human_review(
        _review(),
        reviewer_id="user-001",
        corrections={
            "expenses": 3200,
        },
        comment="Valor de gastos corrigido.",
    )

    assert corrected["status"] == "corrected"
    assert (
        corrected["decision"]["corrections"]
        == {"expenses": 3200}
    )


def test_empty_corrections_are_rejected():
    with pytest.raises(
        HumanReviewError,
        match="corrections",
    ):
        correct_human_review(
            _review(),
            reviewer_id="user-001",
            corrections={},
        )


def test_reject_review():
    rejected = reject_human_review(
        _review(),
        reviewer_id="reviewer-001",
        reason="Dados inconsistentes.",
    )

    assert rejected["status"] == "rejected"
    assert rejected["error"] == (
        "Dados inconsistentes."
    )


def test_cancel_review():
    cancelled = cancel_human_review(
        _review(),
        reviewer_id="user-001",
        reason="Usuário cancelou.",
    )

    assert cancelled["status"] == "cancelled"
    assert (
        cancelled["decision"]["action"]
        == "cancel"
    )


def test_expire_review():
    expired = expire_human_review(
        _review()
    )

    assert expired["status"] == "expired"
    assert expired["resolved_at"] is not None


def test_fail_review():
    failed = fail_human_review(
        _review(),
        error="Falha ao persistir revisão.",
    )

    assert failed["status"] == "failed"
    assert failed["error"] == (
        "Falha ao persistir revisão."
    )


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
def test_terminal_statuses(
    status,
):
    assert is_terminal_human_review_status(
        status
    )


@pytest.mark.parametrize(
    "status",
    [
        "requested",
        "waiting",
    ],
)
def test_non_terminal_statuses(
    status,
):
    assert not is_terminal_human_review_status(
        status
    )


def test_terminal_review_cannot_transition_again():
    approved = approve_human_review(
        _review(),
        reviewer_id="user-001",
    )

    with pytest.raises(
        HumanReviewError,
        match="Transição de revisão humana inválida",
    ):
        transition_human_review(
            approved,
            status="rejected",
        )


def test_invalid_transition_is_rejected():
    waiting = mark_human_review_waiting(
        _review()
    )

    with pytest.raises(
        HumanReviewError,
        match="Transição de revisão humana inválida",
    ):
        mark_human_review_waiting(
            waiting
        )


def test_original_review_is_not_mutated():
    original = _review()

    approved = approve_human_review(
        original,
        reviewer_id="user-001",
    )

    assert original["status"] == "requested"
    assert original["decision"] is None
    assert approved["status"] == "approved"
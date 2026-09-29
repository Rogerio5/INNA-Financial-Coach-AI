from __future__ import annotations

from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
)


WORKFLOW_VERSION = (
    "reimbursement-2b8a"
)


ALLOWED_TRANSITIONS: dict[
    ReimbursementStatus,
    frozenset[ReimbursementStatus],
] = {

    ReimbursementStatus.DRAFT:
        frozenset({
            ReimbursementStatus.SUBMITTED,
            ReimbursementStatus.CANCELLED,
        }),

    ReimbursementStatus.SUBMITTED:
        frozenset({
            ReimbursementStatus.ANALYZING,
            ReimbursementStatus.CANCELLED,
        }),

    ReimbursementStatus.ANALYZING:
        frozenset({
            ReimbursementStatus.NEEDS_INFORMATION,
            ReimbursementStatus.AWAITING_HUMAN_REVIEW,
        }),

    ReimbursementStatus.NEEDS_INFORMATION:
        frozenset({
            ReimbursementStatus.SUBMITTED,
            ReimbursementStatus.CANCELLED,
        }),

    ReimbursementStatus.AWAITING_HUMAN_REVIEW:
        frozenset({
            ReimbursementStatus.APPROVED,
            ReimbursementStatus.REJECTED,
            ReimbursementStatus.NEEDS_INFORMATION,
            ReimbursementStatus.CANCELLED,
        }),

    ReimbursementStatus.APPROVED:
        frozenset({
            ReimbursementStatus.PAYMENT_PENDING,
        }),

    ReimbursementStatus.PAYMENT_PENDING:
        frozenset({
            ReimbursementStatus.PAID,
        }),

    ReimbursementStatus.REJECTED:
        frozenset(),

    ReimbursementStatus.PAID:
        frozenset(),

    ReimbursementStatus.CANCELLED:
        frozenset(),
}


TERMINAL_STATUSES = frozenset({
    ReimbursementStatus.REJECTED,
    ReimbursementStatus.PAID,
    ReimbursementStatus.CANCELLED,
})


class ReimbursementTransitionError(
    ValueError
):
    pass


def allowed_targets(
    status: ReimbursementStatus,
) -> frozenset[ReimbursementStatus]:

    return ALLOWED_TRANSITIONS.get(
        status,
        frozenset(),
    )


def can_transition(
    *,
    current_status: ReimbursementStatus,
    target_status: ReimbursementStatus,
) -> bool:

    return (
        target_status
        in allowed_targets(
            current_status
        )
    )


def assert_transition(
    *,
    current_status: ReimbursementStatus,
    target_status: ReimbursementStatus,
) -> None:

    if can_transition(
        current_status=current_status,
        target_status=target_status,
    ):
        return

    raise ReimbursementTransitionError(
        "REIMBURSEMENT_TRANSITION_NOT_ALLOWED:"
        f"{current_status.value}"
        "->"
        f"{target_status.value}"
    )


def transition_reimbursement(
    *,
    reimbursement: ReimbursementRequest,
    target_status: ReimbursementStatus,
) -> ReimbursementRequest:

    assert_transition(
        current_status=
            reimbursement.status,

        target_status=
            target_status,
    )

    reimbursement.status = (
        target_status
    )

    reimbursement.touch()

    return reimbursement


def workflow_capabilities() -> dict:

    return {
        "version":
            WORKFLOW_VERSION,

        "deterministic_state_machine":
            True,

        "draft_to_submitted":
            True,

        "needs_information_to_submitted":
            True,

        "approved_to_payment_pending":
            True,

        "payment_pending_to_paid":
            True,

        "cancellation_before_final_decision":
            True,

        "terminal_rejected":
            True,

        "terminal_paid":
            True,

        "terminal_cancelled":
            True,

        "transition_guards":
            True,

        "human_review_required":
            True,

        "automatic_approval":
            False,

        "document_ai_deferred":
            True,

        "gemini_enabled":
            False,
    }

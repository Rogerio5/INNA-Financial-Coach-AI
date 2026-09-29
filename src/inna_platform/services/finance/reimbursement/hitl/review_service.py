from __future__ import annotations

from ..audit.audit_service import (
    ReimbursementAuditService,
)
from ..models import ReimbursementStatus
from ..repository import ReimbursementRepository
from ..schemas import HumanReviewInput

from ..workflow import (
    ReimbursementTransitionError,
)

from ..workflow_persistence import (
    persist_workflow_transition,
)


class HumanReviewService:

    def __init__(
        self,
        *,
        repository: ReimbursementRepository,
        audit: ReimbursementAuditService,
    ) -> None:

        self.repository = repository
        self.audit = audit


    def review(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        payload: HumanReviewInput,
        idempotency_key: str | None = None,
    ):

        reimbursement = self.repository.get(
            tenant_id=tenant_id,
            reimbursement_id=reimbursement_id,
        )

        if reimbursement is None:
            raise LookupError(
                "REIMBURSEMENT_NOT_FOUND"
            )


        #
        # Without Idempotency-Key, preserve the legacy
        # early validation exactly as before.
        #
        if (
            idempotency_key is None
            and
            reimbursement.status
            !=
            ReimbursementStatus.AWAITING_HUMAN_REVIEW
        ):
            raise ValueError(
                "REIMBURSEMENT_NOT_AWAITING_HUMAN_REVIEW"
            )


        if payload.decision == "approve":

            target_status = (
                ReimbursementStatus.APPROVED
            )

        elif payload.decision == "reject":

            target_status = (
                ReimbursementStatus.REJECTED
            )

        else:

            target_status = (
                ReimbursementStatus.NEEDS_INFORMATION
            )


        details = {
            "decision":
                payload.decision,

            "reason":
                payload.reason,
        }


        try:

            return persist_workflow_transition(
                repository=
                    self.repository,

                audit=
                    self.audit,

                tenant_id=
                    tenant_id,

                reimbursement_id=
                    reimbursement_id,

                actor_id=
                    payload.reviewer_user_id,

                target_status=
                    target_status,

                details=
                    details,

                idempotency_key=
                    idempotency_key,

                idempotency_operation=
                    "review",

                idempotency_payload=
                    details,
            )

        except ReimbursementTransitionError as exc:

            raise ValueError(
                "REIMBURSEMENT_NOT_AWAITING_HUMAN_REVIEW"
            ) from exc

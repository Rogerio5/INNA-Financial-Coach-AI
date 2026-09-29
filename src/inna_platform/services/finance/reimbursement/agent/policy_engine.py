from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from ..models import (
    ReimbursementRequest,
)

from ..policy.repository import (
    ReimbursementPolicyRepository,
)


@dataclass
class PolicyResult:
    allowed: bool | None

    findings: list[str] = field(
        default_factory=list
    )

    policy_id: str | None = None
    policy_version: int | None = None


class ReimbursementPolicyEngine:

    def __init__(
        self,
        repository:
            ReimbursementPolicyRepository
            |
            None
            =
            None,
    ) -> None:

        self.repository = repository

    def evaluate(
        self,
        reimbursement:
            ReimbursementRequest
            |
            None
            =
            None,
        *,
        persisted_receipt_present: bool = False,
    ) -> PolicyResult:

        #
        # Backward-compatible placeholder behavior.
        #
        if (
            reimbursement is None
            or
            self.repository is None
        ):

            return PolicyResult(
                allowed=None,
                findings=[
                    "POLICY_NOT_CONFIGURED"
                ],
            )

        policy = (
            self.repository.get_active(
                organization_id=
                    reimbursement.tenant_id,
            )
        )

        if policy is None:

            return PolicyResult(
                allowed=None,
                findings=[
                    "POLICY_NOT_CONFIGURED"
                ],
            )

        findings: list[str] = []

        category = str(
            reimbursement.category
            or
            ""
        ).strip().lower()

        currency = str(
            reimbursement.currency
            or
            ""
        ).strip().upper()

        if (
            policy.allowed_categories
            and
            category
            not in
            policy.allowed_categories
        ):

            findings.append(
                "CATEGORY_NOT_ALLOWED"
            )

        if (
            policy.allowed_currencies
            and
            currency
            not in
            policy.allowed_currencies
        ):

            findings.append(
                "CURRENCY_NOT_ALLOWED"
            )

        if (
            policy.amount_limit_minor
            is not None
            and
            reimbursement.amount
            >
            policy.amount_limit_minor
        ):

            findings.append(
                "AMOUNT_LIMIT_EXCEEDED"
            )

        category_limit = (
            policy.category_limits_minor.get(
                category
            )
        )

        if (
            category_limit
            is not None
            and
            reimbursement.amount
            >
            category_limit
        ):

            findings.append(
                "CATEGORY_LIMIT_EXCEEDED"
            )

        if (
            policy.receipt_required
            and
            not persisted_receipt_present
        ):

            findings.append(
                "RECEIPT_REQUIRED"
            )

        if (
            policy.submission_deadline_days
            is not None
            and
            reimbursement.expense_date
        ):

            try:

                expense_date = (
                    date.fromisoformat(
                        reimbursement.expense_date
                    )
                )

                reference_date = (
                    reimbursement.submitted_at.date()
                    if reimbursement.submitted_at
                    is not None
                    else
                    reimbursement.created_at.date()
                )

                age_days = (
                    reference_date
                    -
                    expense_date
                ).days

                if (
                    age_days
                    >
                    policy.submission_deadline_days
                ):

                    findings.append(
                        "SUBMISSION_DEADLINE_EXCEEDED"
                    )

            except ValueError:

                findings.append(
                    "POLICY_EXPENSE_DATE_INVALID"
                )

        return PolicyResult(
            allowed=
                not findings,

            findings=
                findings,

            policy_id=
                policy.policy_id,

            policy_version=
                policy.version,
        )

from __future__ import annotations

from ..models import ReimbursementRequest
from ..schemas import ReimbursementAnalysis
from .guardrails import validate_reimbursement_input
from .policy_engine import ReimbursementPolicyEngine


class ReimbursementAgent:
    """
    Foundation agent.

    No LLM is called in Phase 1A.
    The contract is already prepared for Gemini in Phase 2.
    """

    def __init__(
        self,
        *,
        policy_engine:
            ReimbursementPolicyEngine
            |
            None
            =
            None,
    ) -> None:

        self.policy_engine = (
            policy_engine
        )


    def analyze(
        self,
        reimbursement: ReimbursementRequest,
        *,
        persisted_receipt_present: bool = False,
    ) -> ReimbursementAnalysis:

        guardrail = validate_reimbursement_input(
            description=reimbursement.description,
            amount=reimbursement.amount,
            currency=reimbursement.currency,
        )

        if not guardrail.allowed:

            return ReimbursementAnalysis(
                recommendation="human_review",
                confidence=0.0,
                extracted={},
                missing_fields=[],
                policy_findings=[],
                risk_flags=guardrail.flags,
                evidence=[],
                requires_human_review=True,
            )

        policy_findings: list[str] = []
        policy_id: str | None = None
        policy_version: int | None = None

        if self.policy_engine is not None:

            policy_result = (
                self.policy_engine.evaluate(
                    reimbursement,
                    persisted_receipt_present=
                        persisted_receipt_present,
                )
            )

            policy_findings = list(
                policy_result.findings
            )

            policy_id = (
                policy_result.policy_id
            )

            policy_version = (
                policy_result.policy_version
            )

        missing: list[str] = []

        if not reimbursement.receipt_reference:
            missing.append(
                "receipt_reference"
            )

        if not reimbursement.expense_date:
            missing.append(
                "expense_date"
            )

        if missing:

            return ReimbursementAnalysis(
                recommendation="request_information",
                confidence=1.0,
                extracted={
                    "amount": reimbursement.amount,
                    "currency": reimbursement.currency,
                    "category": reimbursement.category,
                },
                missing_fields=missing,
                policy_findings=policy_findings,
                policy_id=policy_id,
                policy_version=policy_version,
                risk_flags=[],
                evidence=[],
                requires_human_review=True,
            )

        return ReimbursementAnalysis(
            recommendation="human_review",
            confidence=1.0,
            extracted={
                "amount": reimbursement.amount,
                "currency": reimbursement.currency,
                "category": reimbursement.category,
                "merchant": reimbursement.merchant,
                "expense_date": reimbursement.expense_date,
            },
            missing_fields=[],
            policy_findings=policy_findings,
            policy_id=policy_id,
            policy_version=policy_version,
            risk_flags=[],
            evidence=[],
            requires_human_review=True,
        )
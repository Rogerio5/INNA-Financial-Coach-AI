from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AutoApprovalEligibilityResult:
    eligible_for_auto_approval: bool

    automatic_approval: bool

    requires_human_review: bool

    persisted_receipt_present: bool

    document_verified: bool

    policy_compliant: bool

    blocking_reasons: tuple[str, ...]

    evidence: tuple[str, ...]

    version: str = "2b10b-v1"

    def as_dict(self) -> dict[str, Any]:
        return {
            "eligible_for_auto_approval":
                self.eligible_for_auto_approval,

            "automatic_approval":
                self.automatic_approval,

            "requires_human_review":
                self.requires_human_review,

            "persisted_receipt_present":
                self.persisted_receipt_present,

            "document_verified":
                self.document_verified,

            "policy_compliant":
                self.policy_compliant,

            "blocking_reasons":
                list(
                    self.blocking_reasons
                ),

            "evidence":
                list(
                    self.evidence
                ),

            "version":
                self.version,
        }


def _append_unique(
    items: list[str],
    value: str,
) -> None:

    if value not in items:
        items.append(
            value
        )


def _safe_strings(
    values: Sequence[str] | None,
) -> list[str]:

    if values is None:
        return []

    return [
        str(value)
        for value in values
        if str(value).strip()
    ]


def evaluate_auto_approval_eligibility(
    *,
    persisted_receipt_present: bool,

    document_verification:
        Mapping[str, Any]
        |
        None,

    policy_id: str | None,

    policy_version: int | None,

    policy_findings:
        Sequence[str]
        |
        None,

    risk_flags:
        Sequence[str]
        |
        None,

    missing_fields:
        Sequence[str]
        |
        None,
) -> AutoApprovalEligibilityResult:
    """
    Phase 2B10B.

    This function computes eligibility only.

    Security invariants:
    - it NEVER approves a reimbursement;
    - automatic_approval always remains False;
    - human review always remains required;
    - document content remains untrusted.
    """

    blocking: list[str] = []
    evidence: list[str] = []


    # --------------------------------------------------------
    # Persisted receipt
    # --------------------------------------------------------

    if persisted_receipt_present:

        _append_unique(
            evidence,
            "PERSISTED_RECEIPT_PRESENT",
        )

    else:

        _append_unique(
            blocking,
            "PERSISTED_RECEIPT_REQUIRED",
        )


    # --------------------------------------------------------
    # Document verification
    # --------------------------------------------------------

    document_verified = False

    if not isinstance(
        document_verification,
        Mapping,
    ):

        _append_unique(
            blocking,
            "DOCUMENT_VERIFICATION_REQUIRED",
        )

    else:

        document_verified = (
            document_verification.get(
                "document_verified"
            )
            is True
        )

        verification_status = str(
            document_verification.get(
                "status",
                "",
            )
            or
            ""
        ).strip().lower()


        if (
            document_verification.get(
                "document_content_trusted"
            )
            is not False
        ):

            _append_unique(
                blocking,
                "DOCUMENT_TRUST_BOUNDARY_INVALID",
            )


        if not document_verified:

            _append_unique(
                blocking,
                "DOCUMENT_NOT_VERIFIED",
            )


        if (
            verification_status
            !=
            "verified"
        ):

            _append_unique(
                blocking,
                "DOCUMENT_STATUS_NOT_VERIFIED",
            )


        document_blocking = (
            document_verification.get(
                "blocking_reasons",
                [],
            )
        )

        if isinstance(
            document_blocking,
            list,
        ):

            for reason in document_blocking:

                reason_text = str(
                    reason
                ).strip()

                if not reason_text:
                    continue

                _append_unique(
                    blocking,
                    (
                        "DOCUMENT_BLOCK:"
                        + reason_text
                    ),
                )


        if document_verified:

            _append_unique(
                evidence,
                "DOCUMENT_VERIFIED",
            )


    # --------------------------------------------------------
    # Policy evidence / compliance
    # --------------------------------------------------------

    valid_policy_identity = (
        bool(
            str(
                policy_id
                or
                ""
            ).strip()
        )
        and
        isinstance(
            policy_version,
            int,
        )
        and
        policy_version >= 1
    )

    normalized_policy_findings = (
        _safe_strings(
            policy_findings
        )
    )


    if not valid_policy_identity:

        _append_unique(
            blocking,
            "POLICY_EVIDENCE_REQUIRED",
        )


    for finding in normalized_policy_findings:

        _append_unique(
            blocking,
            (
                "POLICY_FINDING:"
                + finding
            ),
        )


    policy_compliant = (
        valid_policy_identity
        and
        not normalized_policy_findings
    )


    if policy_compliant:

        _append_unique(
            evidence,
            "POLICY_COMPLIANT",
        )


    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    for risk_flag in _safe_strings(
        risk_flags
    ):

        _append_unique(
            blocking,
            (
                "RISK_FLAG:"
                + risk_flag
            ),
        )


    # --------------------------------------------------------
    # Required data
    # --------------------------------------------------------

    for missing_field in _safe_strings(
        missing_fields
    ):

        _append_unique(
            blocking,
            (
                "MISSING_FIELD:"
                + missing_field
            ),
        )


    # --------------------------------------------------------
    # Eligibility
    # --------------------------------------------------------

    eligible = (
        persisted_receipt_present
        and
        document_verified
        and
        policy_compliant
        and
        not blocking
    )


    if eligible:

        _append_unique(
            evidence,
            "AUTO_APPROVAL_ELIGIBILITY_CRITERIA_MET",
        )


    return AutoApprovalEligibilityResult(
        eligible_for_auto_approval=
            eligible,

        automatic_approval=False,

        requires_human_review=True,

        persisted_receipt_present=
            persisted_receipt_present,

        document_verified=
            document_verified,

        policy_compliant=
            policy_compliant,

        blocking_reasons=
            tuple(blocking),

        evidence=
            tuple(evidence),
    )
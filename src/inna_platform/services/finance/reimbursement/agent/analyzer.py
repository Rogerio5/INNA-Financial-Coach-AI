from __future__ import annotations

from typing import Any

from ..schemas import (
    ReimbursementAnalysis,
)


KNOWN_INCONSISTENCIES = {
    "AMOUNT_MISMATCH",
    "CURRENCY_MISMATCH",
    "DATE_MISMATCH",
    "MERCHANT_MISMATCH",
}


KNOWN_WARNING_RISK_FLAGS = {
    "UNTRUSTED_DOCUMENT_INSTRUCTION",
    "PDF_TEXT_EXTRACTION_FAILED",
    "PDF_TEXT_NOT_AVAILABLE",
    "VISION_REQUIRED",
    "IMAGE_REQUIRES_VISION",
    "STRUCTURED_FIELDS_NOT_FOUND",
    "EXTRACTION_TOTAL_MISSING",
    "EXTRACTION_CURRENCY_MISSING",
    "EXTRACTION_DATE_MISSING",
    "EXTRACTION_MERCHANT_MISSING",
    "CLAIM_DATE_INVALID",
}


KNOWN_EXTRACTION_STATUSES = {
    "pending",
    "extracted",
    "needs_review",
    "failed",
}


def _append_unique(
    items: list[str],
    value: str,
) -> None:

    if value not in items:
        items.append(
            value
        )


def _safe_string_list(
    value: Any,
) -> list[str]:

    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        str(item)
        for item
        in value
        if isinstance(
            item,
            str,
        )
    ]


def enrich_analysis_with_receipt_validation(
    *,
    analysis: ReimbursementAnalysis,
    reimbursement_metadata: dict[str, Any] | None,
) -> ReimbursementAnalysis:

    if not isinstance(
        reimbursement_metadata,
        dict,
    ):
        return analysis

    validation = (
        reimbursement_metadata.get(
            "receipt_validation"
        )
    )

    if not isinstance(
        validation,
        dict,
    ):
        return analysis

    risk_flags = list(
        analysis.risk_flags
    )

    evidence = list(
        analysis.evidence
    )

    policy_findings = list(
        analysis.policy_findings
    )

    _append_unique(
        evidence,
        "RECEIPT_VALIDATION_PRESENT",
    )

    extraction_status = str(
        validation.get(
            "extraction_status",
            "",
        )
    ).strip()

    if (
        extraction_status
        in
        KNOWN_EXTRACTION_STATUSES
    ):

        _append_unique(
            evidence,
            (
                "RECEIPT_EXTRACTION_STATUS:"
                + extraction_status
            ),
        )

    inconsistencies = (
        _safe_string_list(
            validation.get(
                "inconsistencies"
            )
        )
    )

    warnings = (
        _safe_string_list(
            validation.get(
                "warnings"
            )
        )
    )

    accepted_signal = False

    for code in inconsistencies:

        if code not in KNOWN_INCONSISTENCIES:
            continue

        accepted_signal = True

        _append_unique(
            risk_flags,
            code,
        )

    for code in warnings:

        if (
            code
            not in
            KNOWN_WARNING_RISK_FLAGS
        ):
            continue

        accepted_signal = True

        _append_unique(
            risk_flags,
            code,
        )

    if accepted_signal:

        _append_unique(
            policy_findings,
            "RECEIPT_VALIDATION_REQUIRES_REVIEW",
        )

    return analysis.model_copy(
        update={
            "risk_flags":
                risk_flags,

            "evidence":
                evidence,

            "policy_findings":
                policy_findings,

            "requires_human_review":
                True,
        }
    )
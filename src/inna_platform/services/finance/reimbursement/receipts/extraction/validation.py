from __future__ import annotations

import re
import unicodedata

from dataclasses import replace
from datetime import date

from ...models import (
    ReimbursementRequest,
)

from .models import (
    ReceiptExtractionRecord,
    ReceiptExtractionStatus,
)


def _append_unique(
    items: list[str],
    value: str,
) -> None:

    if value not in items:
        items.append(
            value
        )


def _parse_claim_date(
    value: str | None,
) -> date | None:

    if value is None:
        return None

    normalized = str(
        value
    ).strip()

    if not normalized:
        return None

    try:

        return date.fromisoformat(
            normalized
        )

    except ValueError:

        return None


def _normalize_merchant(
    value: str | None,
) -> str:

    if not value:
        return ""

    normalized = unicodedata.normalize(
        "NFKD",
        str(value),
    )

    normalized = "".join(
        char
        for char
        in normalized
        if not unicodedata.combining(
            char
        )
    )

    normalized = normalized.lower()

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )

    tokens = [
        token
        for token
        in normalized.split()
        if token not in {
            "ltda",
            "me",
            "eireli",
            "sa",
        }
    ]

    return " ".join(
        tokens
    ).strip()


def _merchant_matches(
    claim: str | None,
    extracted: str | None,
) -> bool:

    claim_normalized = (
        _normalize_merchant(
            claim
        )
    )

    extracted_normalized = (
        _normalize_merchant(
            extracted
        )
    )

    if (
        not claim_normalized
        or
        not extracted_normalized
    ):

        return False

    if (
        claim_normalized
        ==
        extracted_normalized
    ):

        return True

    if (
        len(claim_normalized) >= 4
        and
        claim_normalized
        in extracted_normalized
    ):

        return True

    if (
        len(extracted_normalized) >= 4
        and
        extracted_normalized
        in claim_normalized
    ):

        return True

    return False


def validate_extraction_against_reimbursement(
    *,
    reimbursement: ReimbursementRequest,
    extraction: ReceiptExtractionRecord,
) -> ReceiptExtractionRecord:

    if (
        extraction.tenant_id
        !=
        reimbursement.tenant_id
    ):

        raise ValueError(
            "EXTRACTION_TENANT_MISMATCH"
        )

    if (
        extraction.reimbursement_id
        !=
        reimbursement.id
    ):

        raise ValueError(
            "EXTRACTION_REIMBURSEMENT_MISMATCH"
        )

    warnings = list(
        extraction.warnings
    )

    inconsistencies = list(
        extraction.inconsistencies
    )


    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    if (
        extraction.total_minor
        is None
    ):

        _append_unique(
            warnings,
            "EXTRACTION_TOTAL_MISSING",
        )

    elif (
        extraction.total_minor
        !=
        reimbursement.amount
    ):

        _append_unique(
            inconsistencies,
            "AMOUNT_MISMATCH",
        )


    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    claim_currency = str(
        reimbursement.currency
        or
        ""
    ).strip().upper()

    if extraction.currency is None:

        _append_unique(
            warnings,
            "EXTRACTION_CURRENCY_MISSING",
        )

    elif (
        claim_currency
        and
        extraction.currency.upper()
        !=
        claim_currency
    ):

        _append_unique(
            inconsistencies,
            "CURRENCY_MISMATCH",
        )


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    claim_date = _parse_claim_date(
        reimbursement.expense_date
    )

    if reimbursement.expense_date:

        if claim_date is None:

            _append_unique(
                warnings,
                "CLAIM_DATE_INVALID",
            )

        elif extraction.expense_date is None:

            _append_unique(
                warnings,
                "EXTRACTION_DATE_MISSING",
            )

        elif (
            extraction.expense_date
            !=
            claim_date
        ):

            _append_unique(
                inconsistencies,
                "DATE_MISMATCH",
            )


    # --------------------------------------------------------
    # MERCHANT
    # --------------------------------------------------------

    if reimbursement.merchant:

        if not extraction.merchant_name:

            _append_unique(
                warnings,
                "EXTRACTION_MERCHANT_MISSING",
            )

        elif not _merchant_matches(
            reimbursement.merchant,
            extraction.merchant_name,
        ):

            _append_unique(
                inconsistencies,
                "MERCHANT_MISMATCH",
            )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    new_status = (
        extraction.extraction_status
    )

    if (
        new_status
        !=
        ReceiptExtractionStatus.FAILED
        and
        inconsistencies
    ):

        new_status = (
            ReceiptExtractionStatus
            .NEEDS_REVIEW
        )

    validated = replace(
        extraction,

        warnings=
            warnings,

        inconsistencies=
            inconsistencies,

        extraction_status=
            new_status,

        document_content_trusted=
            False,

        human_review_required=
            True,
    )

    validated.touch()

    return validated


def build_validation_metadata(
    extraction: ReceiptExtractionRecord,
) -> dict:

    return {
        "receipt_id":
            extraction.receipt_id,

        "extraction_id":
            extraction.extraction_id,

        "extraction_status":
            extraction.extraction_status.value,

        "extractor":
            extraction.extractor,

        "extractor_version":
            extraction.extractor_version,

        "confidence":
            extraction.confidence,

        "warnings":
            list(
                extraction.warnings
            ),

        "inconsistencies":
            list(
                extraction.inconsistencies
            ),

        "has_inconsistencies":
            bool(
                extraction.inconsistencies
            ),

        "human_review_required":
            True,

        "document_content_trusted":
            False,

        "automatic_approval":
            False,
    }
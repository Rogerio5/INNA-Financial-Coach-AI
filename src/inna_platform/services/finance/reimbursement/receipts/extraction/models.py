from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from enum import Enum
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReceiptExtractionStatus(str, Enum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


@dataclass
class ReceiptExtractionRecord:
    tenant_id: str
    reimbursement_id: str
    receipt_id: str

    extractor: str
    extractor_version: str

    extraction_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    merchant_name: str | None = None
    merchant_tax_id: str | None = None
    document_number: str | None = None

    expense_date: date | None = None
    expense_time: time | None = None

    currency: str | None = None

    subtotal_minor: int | None = None
    tax_minor: int | None = None
    total_minor: int | None = None

    payment_method: str | None = None

    confidence: float = 0.0

    warnings: list[str] = field(
        default_factory=list
    )

    inconsistencies: list[str] = field(
        default_factory=list
    )

    extraction_status: ReceiptExtractionStatus = (
        ReceiptExtractionStatus.PENDING
    )

    document_content_trusted: bool = False
    human_review_required: bool = True

    created_at: datetime = field(
        default_factory=utc_now
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )

    def __post_init__(self) -> None:

        self.tenant_id = str(
            self.tenant_id or ""
        ).strip()

        self.reimbursement_id = str(
            self.reimbursement_id or ""
        ).strip()

        self.receipt_id = str(
            self.receipt_id or ""
        ).strip()

        self.extractor = str(
            self.extractor or ""
        ).strip()

        self.extractor_version = str(
            self.extractor_version or ""
        ).strip()

        if not self.tenant_id:
            raise ValueError(
                "EXTRACTION_TENANT_REQUIRED"
            )

        if not self.reimbursement_id:
            raise ValueError(
                "EXTRACTION_REIMBURSEMENT_REQUIRED"
            )

        if not self.receipt_id:
            raise ValueError(
                "EXTRACTION_RECEIPT_REQUIRED"
            )

        if not self.extractor:
            raise ValueError(
                "EXTRACTION_EXTRACTOR_REQUIRED"
            )

        if not self.extractor_version:
            raise ValueError(
                "EXTRACTION_VERSION_REQUIRED"
            )

        self.confidence = float(
            self.confidence
        )

        if not (
            0.0 <= self.confidence <= 1.0
        ):
            raise ValueError(
                "EXTRACTION_CONFIDENCE_INVALID"
            )

        if self.currency is not None:

            normalized_currency = str(
                self.currency
            ).strip().upper()

            if (
                len(normalized_currency) != 3
                or
                not normalized_currency.isalpha()
            ):
                raise ValueError(
                    "EXTRACTION_CURRENCY_INVALID"
                )

            self.currency = normalized_currency

        for value in (
            self.subtotal_minor,
            self.tax_minor,
            self.total_minor,
        ):

            if (
                value is not None
                and
                int(value) < 0
            ):
                raise ValueError(
                    "EXTRACTION_AMOUNT_INVALID"
                )

        if self.document_content_trusted:
            raise ValueError(
                "DOCUMENT_CONTENT_CANNOT_BE_TRUSTED"
            )

        if not self.human_review_required:
            raise ValueError(
                "HUMAN_REVIEW_REQUIRED"
            )

    def touch(self) -> None:
        self.updated_at = utc_now()
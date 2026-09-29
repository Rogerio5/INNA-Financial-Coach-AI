from __future__ import annotations

from datetime import date, datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from .models import ReceiptExtractionStatus


class ReceiptExtractionContent(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    merchant_name: str | None = Field(
        default=None,
        max_length=255,
    )

    merchant_tax_id: str | None = Field(
        default=None,
        max_length=64,
    )

    document_number: str | None = Field(
        default=None,
        max_length=128,
    )

    expense_date: date | None = None
    expense_time: time | None = None

    currency: str | None = None

    subtotal_minor: int | None = Field(
        default=None,
        ge=0,
    )

    tax_minor: int | None = Field(
        default=None,
        ge=0,
    )

    total_minor: int | None = Field(
        default=None,
        ge=0,
    )

    payment_method: str | None = Field(
        default=None,
        max_length=128,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    warnings: list[str] = Field(
        default_factory=list,
        max_length=100,
    )

    inconsistencies: list[str] = Field(
        default_factory=list,
        max_length=100,
    )

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        normalized = str(
            value
        ).strip().upper()

        if (
            len(normalized) != 3
            or
            not normalized.isalpha()
        ):
            raise ValueError(
                "EXTRACTION_CURRENCY_INVALID"
            )

        return normalized


class ReceiptExtractionView(
    ReceiptExtractionContent
):

    extraction_id: str
    tenant_id: str
    reimbursement_id: str
    receipt_id: str

    extraction_status: ReceiptExtractionStatus

    extractor: str
    extractor_version: str

    document_content_trusted: bool = False
    human_review_required: bool = True

    created_at: datetime
    updated_at: datetime
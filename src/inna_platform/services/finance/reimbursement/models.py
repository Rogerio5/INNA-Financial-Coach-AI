from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReimbursementStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    NEEDS_INFORMATION = "needs_information"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class ReimbursementDecision(str, Enum):
    HUMAN_REVIEW = "human_review"
    REQUEST_INFORMATION = "request_information"
    RECOMMEND_APPROVAL = "recommend_approval"
    RECOMMEND_REJECTION = "recommend_rejection"


@dataclass
class ReimbursementRequest:
    tenant_id: str
    user_id: str
    amount: int
    currency: str
    category: str
    description: str

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: ReimbursementStatus = (
        ReimbursementStatus.DRAFT
    )

    merchant: str | None = None
    expense_date: str | None = None
    receipt_reference: str | None = None

    source_type: str = "finance"
    source_reference: str | None = None

    requires_human_review: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    submitted_at: datetime | None = None

    created_at: datetime = field(
        default_factory=utc_now
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )

    def touch(self) -> None:
        self.updated_at = utc_now()
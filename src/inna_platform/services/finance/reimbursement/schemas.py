from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .models import (
    ReimbursementDecision,
    ReimbursementStatus,
)


class ReimbursementCreate(BaseModel):
    tenant_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)

    amount: int = Field(
        ge=1,
        description="Amount in minor units. Example: R$ 10,50 = 1050.",
    )

    currency: str = Field(
        default="BRL",
        min_length=3,
        max_length=3,
    )

    category: str = Field(min_length=1)
    description: str = Field(min_length=1)

    merchant: str | None = None
    expense_date: str | None = None
    receipt_reference: str | None = None

    source_type: str = "finance"
    source_reference: str | None = None


class ReimbursementAnalysis(BaseModel):
    recommendation: ReimbursementDecision

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    extracted: dict[str, Any] = Field(
        default_factory=dict
    )

    missing_fields: list[str] = Field(
        default_factory=list
    )

    policy_findings: list[str] = Field(
        default_factory=list
    )

    policy_id: str | None = None
    policy_version: int | None = None

    risk_flags: list[str] = Field(
        default_factory=list
    )

    evidence: list[str] = Field(
        default_factory=list
    )

    requires_human_review: bool = True

    eligible_for_auto_approval: bool = False
    auto_approval_permitted: bool = False
    automatic_approval: bool = False


class HumanReviewInput(BaseModel):
    reviewer_user_id: str = Field(min_length=1)

    decision: str = Field(
        pattern="^(approve|reject|request_information)$"
    )

    reason: str = Field(min_length=1)


class ReimbursementResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str

    amount: int
    currency: str
    category: str
    description: str

    status: ReimbursementStatus
    requires_human_review: bool
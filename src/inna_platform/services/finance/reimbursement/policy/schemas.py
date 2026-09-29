from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ReimbursementPolicyCreateRequest(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
    )

    allowed_categories: list[str] = Field(
        default_factory=list,
        max_length=100,
    )

    amount_limit_minor: int | None = Field(
        default=None,
        ge=1,
    )

    category_limits_minor: dict[
        str,
        int,
    ] = Field(
        default_factory=dict,
        max_length=100,
    )

    receipt_required: bool = True

    submission_deadline_days: int | None = Field(
        default=None,
        ge=0,
        le=3650,
    )

    allowed_currencies: list[str] = Field(
        default_factory=lambda: [
            "BRL"
        ],
        max_length=20,
    )

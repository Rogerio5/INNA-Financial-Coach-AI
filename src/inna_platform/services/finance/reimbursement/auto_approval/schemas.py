from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class AutoApprovalConfigurationUpdateRequest(
    BaseModel
):
    enabled: bool = False

    amount_limit_minor: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Maximum reimbursement amount "
            "eligible for controlled "
            "auto-approval, in minor units."
        ),
    )

    expected_version: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Optional optimistic concurrency guard. "
            "Use 0 when expecting no existing "
            "configuration."
        ),
    )
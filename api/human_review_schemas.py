from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


HumanReviewActionApi = Literal[
    "approve",
    "correct",
    "reject",
    "cancel",
]


class HumanReviewRegisterRequest(
    BaseModel
):
    """
    Payload de interrupção produzido pelo LangGraph.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    type: Literal["human_review"]
    version: str = Field(
        default="1.0",
        max_length=20,
    )

    review_id: str = Field(
        min_length=1,
        max_length=255,
    )

    thread_id: str = Field(
        min_length=1,
        max_length=255,
    )

    status: Literal[
        "pending",
        "requested",
        "waiting",
    ] = "pending"

    requested_by: str = Field(
        default="",
        max_length=160,
    )

    reason: str = Field(
        default="",
        max_length=10_000,
    )

    trigger: str = Field(
        default="",
        max_length=160,
    )

    risk_level: str = Field(
        default="",
        max_length=40,
    )

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    allowed_actions: list[
        HumanReviewActionApi
    ] = Field(
        default_factory=lambda: [
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
        min_length=1,
        max_length=4,
    )

    created_at: datetime | None = None


class HumanReviewDecisionRequest(
    BaseModel
):
    """
    Decisão enviada ao endpoint de resolução.

    reviewer_id não é aceito no body. A identidade
    vem da autenticação HMAC da requisição.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    thread_id: str = Field(
        min_length=1,
        max_length=255,
    )

    action: HumanReviewActionApi

    comment: str = Field(
        default="",
        max_length=10_000,
    )

    reason: str = Field(
        default="",
        max_length=10_000,
    )

    corrections: dict[str, Any] = Field(
        default_factory=dict,
    )

    @model_validator(
        mode="after",
    )
    def validar_decisao(
        self,
    ) -> "HumanReviewDecisionRequest":
        if (
            self.action == "correct"
            and not self.corrections
        ):
            raise ValueError(
                "A ação correct exige pelo menos "
                "uma correção."
            )

        if (
            self.action == "reject"
            and not self.reason
        ):
            raise ValueError(
                "A ação reject exige reason."
            )

        return self


class HumanReviewRecordResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
    )

    id: int
    review_id: str
    thread_id: str
    status: str

    requested_by: str = ""
    reason: str = ""
    trigger: str = ""
    risk_level: str = ""

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    decision_action: str = ""
    reviewer_id: str = ""
    reviewer_comment: str = ""
    rejection_reason: str = ""

    corrections: dict[str, Any] = Field(
        default_factory=dict,
    )

    resume_route: str = ""
    failure_reason: str = ""

    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None


class HumanReviewWriteResponse(
    BaseModel
):
    status: Literal[
        "created",
        "existing",
    ]

    created: bool
    review: HumanReviewRecordResponse


class HumanReviewListResponse(
    BaseModel
):
    items: list[
        HumanReviewRecordResponse
    ]

    count: int
    limit: int
    offset: int


class HumanReviewResolutionResponse(
    BaseModel
):
    review_id: str
    thread_id: str
    status: str
    decision_action: str
    reviewer_id: str
    resume_route: str
    resolved_at: str | None = None


class HumanReviewRecoveryRequest(
    BaseModel
):
    timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=86_400,
    )


class HumanReviewRecoveryResponse(
    BaseModel
):
    recovered_review_ids: list[str]
    recovered_count: int


class HumanReviewAdminPageResponse(
    BaseModel
):
    items: list[HumanReviewRecordResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class HumanReviewAdminMetricsResponse(
    BaseModel
):
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    processing: int = Field(ge=0)
    approved: int = Field(ge=0)
    corrected: int = Field(ge=0)
    rejected: int = Field(ge=0)
    cancelled: int = Field(ge=0)
    resume_failed: int = Field(ge=0)

    average_wait_seconds: float | None = None
    average_resolution_seconds: float | None = None

    approval_rate: float = Field(
        ge=0.0,
        le=1.0,
    )
    correction_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    by_risk: dict[str, int] = Field(
        default_factory=dict
    )
    by_agent: dict[str, int] = Field(
        default_factory=dict
    )
    by_reviewer: dict[str, int] = Field(
        default_factory=dict
    )


__all__ = [
    "HumanReviewActionApi",
    "HumanReviewAdminMetricsResponse",
    "HumanReviewAdminPageResponse",
    "HumanReviewDecisionRequest",
    "HumanReviewListResponse",
    "HumanReviewRecordResponse",
    "HumanReviewRecoveryRequest",
    "HumanReviewRecoveryResponse",
    "HumanReviewRegisterRequest",
    "HumanReviewResolutionResponse",
    "HumanReviewWriteResponse",
]

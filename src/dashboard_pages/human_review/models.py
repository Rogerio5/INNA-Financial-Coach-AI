from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardRecord:
    review_id: str
    thread_id: str
    status: str
    requested_by: str = ""
    reason: str = ""
    trigger: str = ""
    risk_level: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    allowed_actions: tuple[str, ...] = ()
    decision_action: str = ""
    reviewer_id: str = ""
    reviewer_comment: str = ""
    rejection_reason: str = ""
    corrections: dict[str, Any] = field(default_factory=dict)
    resume_route: str = ""
    processing_request_id: str = ""
    processing_started_at: datetime | None = None
    failure_reason: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
    ) -> "HumanReviewDashboardRecord":
        if not isinstance(value, dict):
            raise TypeError("Registro de revisão inválido.")

        def parse_datetime(
            field_name: str,
        ) -> datetime | None:
            raw_value = value.get(field_name)

            if raw_value in (
                None,
                "",
            ):
                return None

            if isinstance(
                raw_value,
                datetime,
            ):
                return raw_value

            try:
                return datetime.fromisoformat(
                    str(raw_value).replace(
                        "Z",
                        "+00:00",
                    )
                )
            except ValueError:
                return None

        return cls(
            review_id=str(value.get("review_id") or ""),
            thread_id=str(value.get("thread_id") or ""),
            status=str(value.get("status") or ""),
            requested_by=str(value.get("requested_by") or ""),
            reason=str(value.get("reason") or ""),
            trigger=str(value.get("trigger") or ""),
            risk_level=str(value.get("risk_level") or ""),
            payload=dict(value.get("payload") or {}),
            allowed_actions=tuple(value.get("allowed_actions") or ()),
            decision_action=str(value.get("decision_action") or ""),
            reviewer_id=str(value.get("reviewer_id") or ""),
            reviewer_comment=str(value.get("reviewer_comment") or ""),
            rejection_reason=str(value.get("rejection_reason") or ""),
            corrections=dict(value.get("corrections") or {}),
            resume_route=str(value.get("resume_route") or ""),
            processing_request_id=str(value.get("processing_request_id") or ""),
            processing_started_at=parse_datetime("processing_started_at"),
            failure_reason=str(value.get("failure_reason") or ""),
            created_at=parse_datetime("created_at"),
            updated_at=parse_datetime("updated_at"),
            resolved_at=parse_datetime("resolved_at"),
        )


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardPage:
    items: tuple[
        HumanReviewDashboardRecord,
        ...,
    ]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
    ) -> "HumanReviewDashboardPage":
        if not isinstance(value, dict):
            raise TypeError("Página de revisões inválida.")

        items = tuple(
            HumanReviewDashboardRecord.from_dict(item)
            for item in (value.get("items") or [])
        )

        return cls(
            items=items,
            total=int(value.get("total") or 0),
            limit=int(value.get("limit") or 50),
            offset=int(value.get("offset") or 0),
            has_next=bool(value.get("has_next")),
            has_previous=bool(value.get("has_previous")),
        )


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardMetrics:
    total: int = 0
    pending: int = 0
    processing: int = 0
    approved: int = 0
    corrected: int = 0
    rejected: int = 0
    cancelled: int = 0
    resume_failed: int = 0
    average_wait_seconds: float | None = None
    average_resolution_seconds: float | None = None
    approval_rate: float = 0.0
    correction_rate: float = 0.0
    by_risk: dict[str, int] = field(default_factory=dict)
    by_agent: dict[str, int] = field(default_factory=dict)
    by_reviewer: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
    ) -> "HumanReviewDashboardMetrics":
        if not isinstance(value, dict):
            raise TypeError("Métricas HITL inválidas.")

        def optional_float(
            field_name: str,
        ) -> float | None:
            raw_value = value.get(field_name)

            if raw_value is None:
                return None

            return float(raw_value)

        return cls(
            total=int(value.get("total") or 0),
            pending=int(value.get("pending") or 0),
            processing=int(value.get("processing") or 0),
            approved=int(value.get("approved") or 0),
            corrected=int(value.get("corrected") or 0),
            rejected=int(value.get("rejected") or 0),
            cancelled=int(value.get("cancelled") or 0),
            resume_failed=int(value.get("resume_failed") or 0),
            average_wait_seconds=optional_float("average_wait_seconds"),
            average_resolution_seconds=(optional_float("average_resolution_seconds")),
            approval_rate=float(value.get("approval_rate") or 0.0),
            correction_rate=float(value.get("correction_rate") or 0.0),
            by_risk=dict(value.get("by_risk") or {}),
            by_agent=dict(value.get("by_agent") or {}),
            by_reviewer=dict(value.get("by_reviewer") or {}),
        )


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardResolution:
    review_id: str
    thread_id: str
    status: str
    decision_action: str
    reviewer_id: str
    resume_route: str = ""
    resolved_at: datetime | None = None

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
    ) -> "HumanReviewDashboardResolution":
        if not isinstance(value, dict):
            raise TypeError("Resultado da decisão HITL inválido.")

        raw_resolved_at = value.get("resolved_at")

        resolved_at: datetime | None = None

        if isinstance(
            raw_resolved_at,
            datetime,
        ):
            resolved_at = raw_resolved_at

        elif raw_resolved_at:
            try:
                resolved_at = datetime.fromisoformat(
                    str(raw_resolved_at).replace(
                        "Z",
                        "+00:00",
                    )
                )
            except ValueError:
                resolved_at = None

        return cls(
            review_id=str(value.get("review_id") or ""),
            thread_id=str(value.get("thread_id") or ""),
            status=str(value.get("status") or ""),
            decision_action=str(value.get("decision_action") or ""),
            reviewer_id=str(value.get("reviewer_id") or ""),
            resume_route=str(value.get("resume_route") or ""),
            resolved_at=resolved_at,
        )


__all__ = [
    "HumanReviewDashboardMetrics",
    "HumanReviewDashboardPage",
    "HumanReviewDashboardRecord",
    "HumanReviewDashboardResolution",
]

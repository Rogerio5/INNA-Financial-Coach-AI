from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


ALLOWED_ADMIN_STATUSES = frozenset({
    "pending",
    "processing",
    "approved",
    "corrected",
    "rejected",
    "cancelled",
    "resume_failed",
})

ALLOWED_RISK_LEVELS = frozenset({
    "",
    "low",
    "medium",
    "high",
    "critical",
})


@dataclass(frozen=True, slots=True)
class HumanReviewAdminFilters:
    statuses: tuple[str, ...] = ()
    risk_levels: tuple[str, ...] = ()
    requested_by: str = ""
    reviewer_id: str = ""
    thread_id: str = ""
    created_from: datetime | None = None
    created_to: datetime | None = None
    search: str = ""
    limit: int = 50
    offset: int = 0

    def __post_init__(self) -> None:
        invalid_statuses = (
            set(self.statuses)
            - ALLOWED_ADMIN_STATUSES
        )

        if invalid_statuses:
            raise ValueError(
                "Status administrativos inválidos: "
                f"{sorted(invalid_statuses)}"
            )

        invalid_risks = (
            set(self.risk_levels)
            - ALLOWED_RISK_LEVELS
        )

        if invalid_risks:
            raise ValueError(
                "Níveis de risco inválidos: "
                f"{sorted(invalid_risks)}"
            )

        if not 1 <= self.limit <= 200:
            raise ValueError(
                "limit deve estar entre 1 e 200."
            )

        if self.offset < 0:
            raise ValueError(
                "offset não pode ser negativo."
            )

        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError(
                "created_from não pode ser "
                "posterior a created_to."
            )


@dataclass(frozen=True, slots=True)
class HumanReviewAdminPage:
    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return (
            self.offset + len(self.items)
            < self.total
        )

    @property
    def has_previous(self) -> bool:
        return self.offset > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": self.items,
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


@dataclass(frozen=True, slots=True)
class HumanReviewAdminMetrics:
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
    by_risk: dict[str, int] = field(
        default_factory=dict
    )
    by_agent: dict[str, int] = field(
        default_factory=dict
    )
    by_reviewer: dict[str, int] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    "ALLOWED_ADMIN_STATUSES",
    "ALLOWED_RISK_LEVELS",
    "HumanReviewAdminFilters",
    "HumanReviewAdminMetrics",
    "HumanReviewAdminPage",
]

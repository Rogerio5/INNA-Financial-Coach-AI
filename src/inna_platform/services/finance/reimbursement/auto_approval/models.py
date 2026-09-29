from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


@dataclass
class AutoApprovalConfiguration:
    organization_id: str

    enabled: bool = False

    amount_limit_minor: int | None = None

    version: int = 1

    updated_by_user_id: str | None = None

    created_at: datetime = field(
        default_factory=utc_now
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )

    def __post_init__(self) -> None:

        self.organization_id = str(
            self.organization_id or ""
        ).strip()

        if not self.organization_id:
            raise ValueError(
                "AUTO_APPROVAL_ORGANIZATION_REQUIRED"
            )

        if self.version < 1:
            raise ValueError(
                "AUTO_APPROVAL_VERSION_INVALID"
            )

        if (
            self.amount_limit_minor
            is not None
            and
            self.amount_limit_minor < 1
        ):
            raise ValueError(
                "AUTO_APPROVAL_LIMIT_INVALID"
            )

        if (
            self.enabled
            and
            self.amount_limit_minor
            is None
        ):
            raise ValueError(
                "AUTO_APPROVAL_LIMIT_REQUIRED"
            )

        if self.updated_by_user_id is not None:

            self.updated_by_user_id = str(
                self.updated_by_user_id
            ).strip()

            if not self.updated_by_user_id:
                self.updated_by_user_id = None
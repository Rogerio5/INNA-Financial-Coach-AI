from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


@dataclass
class ReimbursementPolicy:

    organization_id: str

    allowed_categories: list[str] = field(
        default_factory=list
    )

    amount_limit_minor: int | None = None

    category_limits_minor: dict[str, int] = field(
        default_factory=dict
    )

    receipt_required: bool = True

    submission_deadline_days: int | None = None

    allowed_currencies: list[str] = field(
        default_factory=lambda: ["BRL"]
    )

    policy_id: str = field(
        default_factory=lambda:
            "rpol_" + uuid4().hex
    )

    version: int = 1
    active: bool = True

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
                "POLICY_ORGANIZATION_REQUIRED"
            )

        if self.version < 1:
            raise ValueError(
                "POLICY_VERSION_INVALID"
            )

        if (
            self.amount_limit_minor
            is not None
            and
            self.amount_limit_minor < 1
        ):
            raise ValueError(
                "POLICY_AMOUNT_LIMIT_INVALID"
            )

        if (
            self.submission_deadline_days
            is not None
            and
            self.submission_deadline_days < 0
        ):
            raise ValueError(
                "POLICY_DEADLINE_INVALID"
            )

        normalized_categories = []

        for item in self.allowed_categories:

            category = str(
                item or ""
            ).strip().lower()

            if (
                category
                and
                category
                not in normalized_categories
            ):
                normalized_categories.append(
                    category
                )

        self.allowed_categories = (
            normalized_categories
        )

        normalized_limits = {}

        for key, value in (
            self.category_limits_minor.items()
        ):

            category = str(
                key or ""
            ).strip().lower()

            limit = int(
                value
            )

            if not category:
                continue

            if limit < 1:
                raise ValueError(
                    "POLICY_CATEGORY_LIMIT_INVALID"
                )

            normalized_limits[
                category
            ] = limit

        self.category_limits_minor = (
            normalized_limits
        )

        normalized_currencies = []

        for item in self.allowed_currencies:

            currency = str(
                item or ""
            ).strip().upper()

            if (
                currency
                and
                currency
                not in normalized_currencies
            ):
                normalized_currencies.append(
                    currency
                )

        self.allowed_currencies = (
            normalized_currencies
        )

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from typing import Any, Mapping


ALLOWED_STATUSES = frozenset({
    "pending",
    "processing",
    "approved",
    "corrected",
    "rejected",
    "cancelled",
    "resume_failed",
})

ALLOWED_RISK_LEVELS = frozenset({
    "low",
    "medium",
    "high",
    "critical",
})

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 200


def _normalized_text(
    value: Any,
    *,
    max_length: int,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    return normalized[:max_length]


def _normalized_values(
    values: Any,
    *,
    allowed: frozenset[str],
) -> tuple[str, ...]:
    if values is None:
        return ()

    if isinstance(
        values,
        str,
    ):
        source = [
            values,
        ]
    else:
        try:
            source = list(values)
        except TypeError:
            source = []

    normalized: list[str] = []

    for item in source:
        value = str(
            item or ""
        ).strip().lower()

        if (
            value in allowed
            and value not in normalized
        ):
            normalized.append(
                value
            )

    return tuple(normalized)


def _normalized_date(
    value: Any,
) -> date | None:
    if value in (
        None,
        "",
    ):
        return None

    if isinstance(
        value,
        date,
    ):
        return value

    try:
        return date.fromisoformat(
            str(value)
        )
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardFilters:
    statuses: tuple[str, ...] = (
        "pending",
        "processing",
    )
    risk_levels: tuple[str, ...] = ()
    requested_by: str = ""
    reviewer_id: str = ""
    thread_id: str = ""
    search: str = ""
    created_from: date | None = None
    created_to: date | None = None
    limit: int = DEFAULT_PAGE_SIZE
    offset: int = 0

    def __post_init__(
        self,
    ) -> None:
        normalized_statuses = (
            _normalized_values(
                self.statuses,
                allowed=ALLOWED_STATUSES,
            )
        )

        normalized_risks = (
            _normalized_values(
                self.risk_levels,
                allowed=ALLOWED_RISK_LEVELS,
            )
        )

        try:
            normalized_limit = int(
                self.limit
            )
        except (
            TypeError,
            ValueError,
        ):
            normalized_limit = (
                DEFAULT_PAGE_SIZE
            )

        normalized_limit = min(
            MAX_PAGE_SIZE,
            max(
                1,
                normalized_limit,
            ),
        )

        try:
            normalized_offset = max(
                0,
                int(self.offset),
            )
        except (
            TypeError,
            ValueError,
        ):
            normalized_offset = 0

        normalized_from = (
            _normalized_date(
                self.created_from
            )
        )

        normalized_to = (
            _normalized_date(
                self.created_to
            )
        )

        if (
            normalized_from
            and normalized_to
            and normalized_from
            > normalized_to
        ):
            normalized_from, normalized_to = (
                normalized_to,
                normalized_from,
            )

        object.__setattr__(
            self,
            "statuses",
            normalized_statuses,
        )

        object.__setattr__(
            self,
            "risk_levels",
            normalized_risks,
        )

        object.__setattr__(
            self,
            "requested_by",
            _normalized_text(
                self.requested_by,
                max_length=160,
            ),
        )

        object.__setattr__(
            self,
            "reviewer_id",
            _normalized_text(
                self.reviewer_id,
                max_length=160,
            ),
        )

        object.__setattr__(
            self,
            "thread_id",
            _normalized_text(
                self.thread_id,
                max_length=200,
            ),
        )

        object.__setattr__(
            self,
            "search",
            _normalized_text(
                self.search,
                max_length=300,
            ),
        )

        object.__setattr__(
            self,
            "created_from",
            normalized_from,
        )

        object.__setattr__(
            self,
            "created_to",
            normalized_to,
        )

        object.__setattr__(
            self,
            "limit",
            normalized_limit,
        )

        object.__setattr__(
            self,
            "offset",
            normalized_offset,
        )

    @property
    def page_number(
        self,
    ) -> int:
        return (
            self.offset // self.limit
        ) + 1

    def to_api_kwargs(
        self,
    ) -> dict[str, Any]:
        return {
            "statuses": self.statuses,
            "risk_levels": (
                self.risk_levels
            ),
            "requested_by": (
                self.requested_by
            ),
            "reviewer_id": (
                self.reviewer_id
            ),
            "thread_id": self.thread_id,
            "search": self.search,
            "created_from": (
                self.created_from.isoformat()
                if self.created_from
                else ""
            ),
            "created_to": (
                self.created_to.isoformat()
                if self.created_to
                else ""
            ),
            "limit": self.limit,
            "offset": self.offset,
        }

    def reset_pagination(
        self,
    ) -> "HumanReviewDashboardFilters":
        return replace(
            self,
            offset=0,
        )

    def next_page(
        self,
        *,
        has_next: bool,
    ) -> "HumanReviewDashboardFilters":
        if not has_next:
            return self

        return replace(
            self,
            offset=(
                self.offset
                + self.limit
            ),
        )

    def previous_page(
        self,
    ) -> "HumanReviewDashboardFilters":
        return replace(
            self,
            offset=max(
                0,
                self.offset
                - self.limit,
            ),
        )


@dataclass(frozen=True, slots=True)
class HumanReviewDashboardState:
    filters: HumanReviewDashboardFilters
    selected_review_id: str = ""
    active_tab: str = "overview"
    refresh_token: int = 0

    def select_review(
        self,
        review_id: str,
    ) -> "HumanReviewDashboardState":
        return replace(
            self,
            selected_review_id=(
                _normalized_text(
                    review_id,
                    max_length=200,
                )
            ),
        )

    def clear_selection(
        self,
    ) -> "HumanReviewDashboardState":
        return replace(
            self,
            selected_review_id="",
        )

    def refresh(
        self,
    ) -> "HumanReviewDashboardState":
        return replace(
            self,
            refresh_token=(
                self.refresh_token + 1
            ),
        )

    def with_filters(
        self,
        filters: HumanReviewDashboardFilters,
    ) -> "HumanReviewDashboardState":
        return replace(
            self,
            filters=filters,
        )


def dashboard_state_from_mapping(
    value: Mapping[str, Any] | None,
) -> HumanReviewDashboardState:
    source = dict(
        value or {}
    )

    filters_source = source.get(
        "filters"
    )

    if not isinstance(
        filters_source,
        Mapping,
    ):
        filters_source = {}

    filters = HumanReviewDashboardFilters(
        statuses=filters_source.get(
            "statuses",
            (
                "pending",
                "processing",
            ),
        ),
        risk_levels=filters_source.get(
            "risk_levels",
            (),
        ),
        requested_by=filters_source.get(
            "requested_by",
            "",
        ),
        reviewer_id=filters_source.get(
            "reviewer_id",
            "",
        ),
        thread_id=filters_source.get(
            "thread_id",
            "",
        ),
        search=filters_source.get(
            "search",
            "",
        ),
        created_from=filters_source.get(
            "created_from"
        ),
        created_to=filters_source.get(
            "created_to"
        ),
        limit=filters_source.get(
            "limit",
            DEFAULT_PAGE_SIZE,
        ),
        offset=filters_source.get(
            "offset",
            0,
        ),
    )

    return HumanReviewDashboardState(
        filters=filters,
        selected_review_id=_normalized_text(
            source.get(
                "selected_review_id",
                "",
            ),
            max_length=200,
        ),
        active_tab=_normalized_text(
            source.get(
                "active_tab",
                "overview",
            ),
            max_length=40,
        )
        or "overview",
        refresh_token=max(
            0,
            int(
                source.get(
                    "refresh_token",
                    0,
                )
                or 0
            ),
        ),
    )


def dashboard_state_to_dict(
    state: HumanReviewDashboardState,
) -> dict[str, Any]:
    return {
        "filters": {
            **state.filters.to_api_kwargs(),
            "created_from": (
                state.filters.created_from
                .isoformat()
                if state.filters.created_from
                else ""
            ),
            "created_to": (
                state.filters.created_to
                .isoformat()
                if state.filters.created_to
                else ""
            ),
        },
        "selected_review_id": (
            state.selected_review_id
        ),
        "active_tab": state.active_tab,
        "refresh_token": (
            state.refresh_token
        ),
    }


__all__ = [
    "ALLOWED_RISK_LEVELS",
    "ALLOWED_STATUSES",
    "DEFAULT_PAGE_SIZE",
    "HumanReviewDashboardFilters",
    "HumanReviewDashboardState",
    "dashboard_state_from_mapping",
    "dashboard_state_to_dict",
]

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.services.human_review.admin_contracts import (
    HumanReviewAdminFilters,
    HumanReviewAdminMetrics,
    HumanReviewAdminPage,
)


def test_admin_filters_accept_valid_values() -> None:
    filters = HumanReviewAdminFilters(
        statuses=(
            "pending",
            "processing",
        ),
        risk_levels=(
            "high",
            "critical",
        ),
        limit=100,
        offset=20,
    )

    assert filters.limit == 100
    assert filters.offset == 20


@pytest.mark.parametrize(
    "status",
    [
        "unknown",
        "requested",
        "waiting",
    ],
)
def test_admin_filters_reject_invalid_status(
    status: str,
) -> None:
    with pytest.raises(ValueError):
        HumanReviewAdminFilters(
            statuses=(status,),
        )


def test_admin_filters_reject_invalid_period() -> None:
    with pytest.raises(ValueError):
        HumanReviewAdminFilters(
            created_from=datetime(
                2026,
                7,
                25,
                tzinfo=UTC,
            ),
            created_to=datetime(
                2026,
                7,
                24,
                tzinfo=UTC,
            ),
        )


def test_admin_page_pagination_flags() -> None:
    page = HumanReviewAdminPage(
        items=[
            {
                "review_id": "review-1",
            },
        ],
        total=3,
        limit=1,
        offset=1,
    )

    assert page.has_previous is True
    assert page.has_next is True


def test_admin_metrics_serialization() -> None:
    metrics = HumanReviewAdminMetrics(
        total=10,
        pending=2,
        approved=5,
        approval_rate=0.625,
        by_risk={
            "high": 3,
        },
    )

    result = metrics.to_dict()

    assert result["total"] == 10
    assert result["pending"] == 2
    assert result["by_risk"] == {
        "high": 3,
    }

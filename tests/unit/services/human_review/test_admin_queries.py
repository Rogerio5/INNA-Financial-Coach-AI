from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from src.services.human_review.admin_contracts import (
    HumanReviewAdminFilters,
)
from src.services.human_review.admin_queries import (
    _build_where,
    _normalize_row,
    listar_revisoes_admin,
    obter_metricas_admin,
)


def test_build_where_without_filters() -> None:
    where_sql, parameters = _build_where(HumanReviewAdminFilters())

    assert where_sql == ""
    assert parameters == {}


def test_build_where_with_operational_filters() -> None:
    filters = HumanReviewAdminFilters(
        statuses=(
            "pending",
            "processing",
        ),
        risk_levels=("high",),
        requested_by="financial_agent",
        reviewer_id="admin-1",
        thread_id="thread-1",
        search="cartão",
        limit=25,
        offset=50,
    )

    where_sql, parameters = _build_where(filters)

    assert "status = ANY" in where_sql
    assert "risk_level = ANY" in where_sql
    assert "requested_by =" in where_sql
    assert "reviewer_id =" in where_sql
    assert "thread_id =" in where_sql
    assert "ILIKE" in where_sql

    assert parameters["statuses"] == [
        "pending",
        "processing",
    ]

    assert parameters["risk_levels"] == [
        "high",
    ]

    assert parameters["search"] == "%cartão%"


def test_normalize_row_serializes_dates_and_json() -> None:
    created_at = datetime(
        2026,
        7,
        24,
        15,
        30,
        tzinfo=UTC,
    )

    result = _normalize_row(
        {
            "review_id": "review-1",
            "created_at": created_at,
            "updated_at": created_at,
            "resolved_at": None,
            "processing_started_at": None,
            "payload": {
                "amount": 100,
            },
            "corrections": None,
            "allowed_actions": [
                "approve",
                "reject",
            ],
        }
    )

    assert result["created_at"] == (created_at.isoformat())

    assert result["payload"] == {
        "amount": 100,
    }

    assert result["corrections"] == {}

    assert result["allowed_actions"] == [
        "approve",
        "reject",
    ]


def _cursor_context(
    cursor: Mock,
):
    @contextmanager
    def factory(**_: object):
        yield cursor

    return factory


def test_listar_revisoes_admin_returns_page() -> None:
    cursor = Mock()

    cursor.fetchone.return_value = {
        "total": 2,
    }

    cursor.fetchall.return_value = [
        {
            "id": 1,
            "review_id": "review-1",
            "thread_id": "thread-1",
            "status": "pending",
            "requested_by": "financial_agent",
            "reason": "Risco elevado",
            "trigger": "high_risk",
            "risk_level": "high",
            "payload": {},
            "allowed_actions": ["approve"],
            "decision_action": "",
            "reviewer_id": "",
            "reviewer_comment": "",
            "rejection_reason": "",
            "corrections": {},
            "resume_route": "",
            "processing_request_id": "",
            "processing_started_at": None,
            "failure_reason": "",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "resolved_at": None,
        },
    ]

    with patch(
        "src.services.human_review.admin_queries.cursor_postgres",
        _cursor_context(cursor),
    ):
        page = listar_revisoes_admin(
            HumanReviewAdminFilters(
                statuses=("pending",),
                limit=10,
            )
        )

    assert page.total == 2
    assert page.limit == 10
    assert len(page.items) == 1

    assert page.items[0]["status"] == ("pending")

    assert page.has_next is True
    assert cursor.execute.call_count == 2


def test_obter_metricas_admin_calculates_rates() -> None:
    cursor = Mock()

    cursor.fetchone.return_value = {
        "total": 10,
        "pending": 2,
        "processing": 1,
        "approved": 4,
        "corrected": 2,
        "rejected": 1,
        "cancelled": 1,
        "resume_failed": 0,
        "average_wait_seconds": 30.5,
        "average_resolution_seconds": 120.0,
    }

    cursor.fetchall.side_effect = [
        [
            {
                "dimension": "high",
                "total": 6,
            },
            {
                "dimension": "medium",
                "total": 4,
            },
        ],
        [
            {
                "dimension": "financial_agent",
                "total": 10,
            },
        ],
        [
            {
                "dimension": "admin-1",
                "total": 8,
            },
            {
                "dimension": "unassigned",
                "total": 2,
            },
        ],
    ]

    with patch(
        "src.services.human_review.admin_queries.cursor_postgres",
        _cursor_context(cursor),
    ):
        metrics = obter_metricas_admin()

    assert metrics.total == 10
    assert metrics.pending == 2
    assert metrics.approved == 4
    assert metrics.approval_rate == 0.5
    assert metrics.correction_rate == 0.25
    assert metrics.average_wait_seconds == 30.5
    assert metrics.by_risk["high"] == 6

    assert metrics.by_reviewer["admin-1"] == 8


@pytest.mark.parametrize(
    "invalid_filters",
    [
        None,
        {},
        "pending",
    ],
)
def test_listar_revisoes_admin_rejects_invalid_type(
    invalid_filters: object,
) -> None:
    with pytest.raises(TypeError):
        listar_revisoes_admin(
            invalid_filters  # type: ignore[arg-type]
        )

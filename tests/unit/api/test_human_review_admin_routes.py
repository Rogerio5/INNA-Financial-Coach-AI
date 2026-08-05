from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from api.security.human_review_admin import (
    require_human_review_admin_context,
)
from src.services.human_review.admin_contracts import (
    HumanReviewAdminMetrics,
    HumanReviewAdminPage,
)
from src.services.human_review.contracts import (
    HumanReviewRecord,
)
from src.services.human_review.exceptions import (
    HumanReviewRepositoryError,
)


ADMIN_PREFIX = "/internal/human-reviews/admin"


def _admin_context():
    return SimpleNamespace(
        user_id="admin-local",
        request_id="request-admin-123456",
    )


def _record() -> HumanReviewRecord:
    now = datetime.now(UTC)

    return HumanReviewRecord(
        id=1,
        review_id="review-1",
        thread_id="thread-1",
        status="pending",
        requested_by="financial_agent",
        reason="Operação de alto risco",
        trigger="high_risk",
        risk_level="high",
        payload={
            "amount": 1000,
        },
        allowed_actions=[
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
        decision_action="",
        reviewer_id="",
        reviewer_comment="",
        rejection_reason="",
        corrections={},
        resume_route="",
        processing_request_id="",
        processing_started_at=None,
        failure_reason="",
        created_at=now,
        updated_at=now,
        resolved_at=None,
    )


def _record_dict() -> dict:
    return _record().model_dump(mode="json")


def _client() -> TestClient:
    app.dependency_overrides[require_human_review_admin_context] = _admin_context

    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_admin_list_reviews_returns_page() -> None:
    page = HumanReviewAdminPage(
        items=[_record_dict()],
        total=3,
        limit=1,
        offset=0,
    )

    with patch(
        "api.human_review_admin_routes.listar_revisoes_admin",
        return_value=page,
    ) as mocked:
        response = _client().get(
            f"{ADMIN_PREFIX}/reviews",
            params=[
                (
                    "statuses",
                    "pending",
                ),
                (
                    "risk_levels",
                    "high",
                ),
                (
                    "limit",
                    "1",
                ),
                (
                    "offset",
                    "0",
                ),
            ],
        )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["limit"] == 1
    assert body["has_next"] is True
    assert len(body["items"]) == 1
    assert body["items"][0]["review_id"] == "review-1"

    filters = mocked.call_args.args[0]

    assert filters.statuses == ("pending",)
    assert filters.risk_levels == ("high",)


def test_admin_list_reviews_rejects_invalid_status() -> None:
    response = _client().get(
        f"{ADMIN_PREFIX}/reviews",
        params={
            "statuses": "unknown",
        },
    )

    assert response.status_code == 422


def test_admin_list_reviews_validates_limit() -> None:
    response = _client().get(
        f"{ADMIN_PREFIX}/reviews",
        params={
            "limit": 500,
        },
    )

    assert response.status_code == 422


def test_admin_get_review_returns_record() -> None:
    with patch(
        "api.human_review_admin_routes.service.consultar_revisao",
        return_value=_record(),
    ):
        response = _client().get(f"{ADMIN_PREFIX}/reviews/review-1")

    assert response.status_code == 200

    body = response.json()

    assert body["review_id"] == "review-1"
    assert body["status"] == "pending"


def test_admin_metrics_returns_aggregates() -> None:
    metrics = HumanReviewAdminMetrics(
        total=10,
        pending=2,
        processing=1,
        approved=4,
        corrected=2,
        rejected=1,
        cancelled=0,
        resume_failed=0,
        average_wait_seconds=45.0,
        average_resolution_seconds=180.0,
        approval_rate=0.5714,
        correction_rate=0.2857,
        by_risk={
            "high": 6,
            "medium": 4,
        },
        by_agent={
            "financial_agent": 10,
        },
        by_reviewer={
            "admin-local": 8,
            "unassigned": 2,
        },
    )

    with patch(
        "api.human_review_admin_routes.obter_metricas_admin",
        return_value=metrics,
    ):
        response = _client().get(f"{ADMIN_PREFIX}/metrics")

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 10
    assert body["approved"] == 4
    assert body["by_risk"]["high"] == 6


def test_admin_recover_stale_claims() -> None:
    with patch(
        "api.human_review_admin_routes.service.recuperar_claims_expirados",
        return_value=[
            "review-1",
            "review-2",
        ],
    ):
        response = _client().post(
            f"{ADMIN_PREFIX}/recover-stale",
            json={
                "timeout_seconds": 300,
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["recovered_count"] == 2

    assert body["recovered_review_ids"] == [
        "review-1",
        "review-2",
    ]


def test_admin_recover_rejects_short_timeout() -> None:
    response = _client().post(
        f"{ADMIN_PREFIX}/recover-stale",
        json={
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 422


def test_admin_repository_failure_is_sanitized() -> None:
    with patch(
        "api.human_review_admin_routes.listar_revisoes_admin",
        side_effect=(HumanReviewRepositoryError("database-password-secret")),
    ):
        response = _client().get(f"{ADMIN_PREFIX}/reviews")

    assert response.status_code == 503

    body = response.json()

    assert "database-password-secret" not in body["detail"]

    assert "temporariamente indisponível" in body["detail"]

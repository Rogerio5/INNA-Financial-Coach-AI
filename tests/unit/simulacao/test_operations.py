from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.dashboard_pages.human_review.api_client import (
    HumanReviewDashboardApiError,
    resolver_revisao_hitl_api,
)
from src.dashboard_pages.human_review.components import (
    parse_corrections_json_hitl,
    preparar_tabela_revisoes_hitl,
)
from src.dashboard_pages.human_review.models import (
    HumanReviewDashboardPage,
    HumanReviewDashboardRecord,
)


def _resolution_response() -> Mock:
    response = Mock()
    response.ok = True
    response.status_code = 200
    response.json.return_value = {
        "review_id": "review-1",
        "thread_id": "thread-1",
        "status": "approved",
        "decision_action": "approve",
        "reviewer_id": "admin@inna.ai",
        "resume_route": "summary",
        "resolved_at": (
            "2026-07-24T19:00:00+00:00"
        ),
    }
    return response


def test_resolve_review_calls_signed_endpoint(
) -> None:
    with (
        patch(
            "src.dashboard_pages.human_review."
            "api_client.assinar_requisicao_interna",
            return_value="f" * 64,
        ),
        patch(
            "src.dashboard_pages.human_review."
            "api_client.requests.post",
            return_value=(
                _resolution_response()
            ),
        ) as request,
    ):
        result = resolver_revisao_hitl_api(
            admin_user_id="admin@inna.ai",
            review_id="review-1",
            thread_id="thread-1",
            action="approve",
            comment="Validado.",
        )

    assert result.status == "approved"

    assert request.call_args.args[0].endswith(
        "/internal/human-reviews/"
        "review-1/resolve"
    )


def test_correction_requires_payload(
) -> None:
    with pytest.raises(
        HumanReviewDashboardApiError
    ):
        resolver_revisao_hitl_api(
            admin_user_id="admin@inna.ai",
            review_id="review-1",
            thread_id="thread-1",
            action="correct",
            corrections={},
        )


def test_rejection_requires_reason(
) -> None:
    with pytest.raises(
        HumanReviewDashboardApiError
    ):
        resolver_revisao_hitl_api(
            admin_user_id="admin@inna.ai",
            review_id="review-1",
            thread_id="thread-1",
            action="reject",
        )


def test_parse_corrections_json() -> None:
    result = parse_corrections_json_hitl(
        '{"valor": 1000}'
    )

    assert result == {
        "valor": 1000,
    }


def test_parse_corrections_rejects_array(
) -> None:
    with pytest.raises(
        ValueError
    ):
        parse_corrections_json_hitl(
            '["valor"]'
        )


def test_prepare_review_table() -> None:
    page = HumanReviewDashboardPage(
        items=(
            HumanReviewDashboardRecord(
                review_id="review-1",
                thread_id="thread-1",
                status="pending",
                risk_level="high",
                requested_by=(
                    "financial_agent"
                ),
            ),
        ),
        total=1,
        limit=25,
        offset=0,
        has_next=False,
        has_previous=False,
    )

    rows = preparar_tabela_revisoes_hitl(
        page
    )

    assert rows[0]["Status"] == "Pendente"
    assert rows[0]["Risco"] == "Alto"

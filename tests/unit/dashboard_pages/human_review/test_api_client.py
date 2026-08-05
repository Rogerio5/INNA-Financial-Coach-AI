from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from api.security.internal_request import (
    HEADER_SIGNATURE,
)
from src.dashboard_pages.human_review.api_client import (
    HumanReviewDashboardApiError,
    _get_json,
    _post_json,
    listar_revisoes_hitl_api,
    recuperar_claims_hitl_api,
)


def _response(
    payload: dict,
    *,
    status_code: int = 200,
) -> Mock:
    response = Mock()
    response.ok = 200 <= status_code < 400
    response.status_code = status_code
    response.json.return_value = payload
    return response


def test_get_signs_empty_body() -> None:
    response = _response(
        {
            "items": [],
        }
    )

    with (
        patch(
            "src.dashboard_pages.human_review.api_client.assinar_requisicao_interna",
            return_value="a" * 64,
        ) as signer,
        patch(
            "src.dashboard_pages.human_review.api_client.requests.get",
            return_value=response,
        ) as request,
    ):
        result = _get_json(
            path=("/internal/human-reviews/admin/reviews"),
            admin_user_id="admin@inna.ai",
        )

    assert result == {
        "items": [],
    }

    assert signer.call_args.kwargs["body"] == b""

    assert HEADER_SIGNATURE in (request.call_args.kwargs["headers"])


def test_post_sends_exact_signed_bytes() -> None:
    response = _response(
        {
            "recovered_review_ids": [],
            "recovered_count": 0,
        }
    )

    with (
        patch(
            "src.dashboard_pages.human_review.api_client.assinar_requisicao_interna",
            return_value="b" * 64,
        ) as signer,
        patch(
            "src.dashboard_pages.human_review.api_client.requests.post",
            return_value=response,
        ) as request,
    ):
        _post_json(
            path=("/internal/human-reviews/admin/recover-stale"),
            admin_user_id="admin@inna.ai",
            payload={
                "timeout_seconds": 300,
            },
        )

    signed_body = signer.call_args.kwargs["body"]

    sent_body = request.call_args.kwargs["data"]

    assert sent_body == signed_body

    assert json.loads(sent_body.decode("utf-8")) == {
        "timeout_seconds": 300,
    }


def test_list_builds_repeated_filters() -> None:
    response = _response(
        {
            "items": [],
            "total": 0,
            "limit": 25,
            "offset": 0,
            "has_next": False,
            "has_previous": False,
        }
    )

    with (
        patch(
            "src.dashboard_pages.human_review.api_client.assinar_requisicao_interna",
            return_value="c" * 64,
        ),
        patch(
            "src.dashboard_pages.human_review.api_client.requests.get",
            return_value=response,
        ) as request,
    ):
        page = listar_revisoes_hitl_api(
            admin_user_id="admin@inna.ai",
            statuses=[
                "pending",
                "processing",
            ],
            risk_levels=[
                "high",
                "critical",
            ],
            limit=25,
        )

    params = request.call_args.kwargs["params"]

    assert (
        "statuses",
        "pending",
    ) in params

    assert (
        "statuses",
        "processing",
    ) in params

    assert (
        "risk_levels",
        "critical",
    ) in params

    assert page.total == 0


def test_recover_returns_ids() -> None:
    response = _response(
        {
            "recovered_review_ids": [
                "review-1",
                "review-2",
            ],
            "recovered_count": 2,
        }
    )

    with (
        patch(
            "src.dashboard_pages.human_review.api_client.assinar_requisicao_interna",
            return_value="d" * 64,
        ),
        patch(
            "src.dashboard_pages.human_review.api_client.requests.post",
            return_value=response,
        ),
    ):
        recovered = recuperar_claims_hitl_api(
            admin_user_id="admin@inna.ai",
            timeout_seconds=300,
        )

    assert recovered == (
        "review-1",
        "review-2",
    )


@pytest.mark.parametrize(
    ("status_code", "expected_text"),
    [
        (401, "autenticação"),
        (403, "permissão"),
        (409, "outro administrador"),
        (503, "indisponível"),
    ],
)
def test_http_errors_are_sanitized(
    status_code: int,
    expected_text: str,
) -> None:
    response = _response(
        {
            "detail": ("segredo-banco-interno"),
        },
        status_code=status_code,
    )

    with (
        patch(
            "src.dashboard_pages.human_review.api_client.assinar_requisicao_interna",
            return_value="e" * 64,
        ),
        patch(
            "src.dashboard_pages.human_review.api_client.requests.get",
            return_value=response,
        ),
    ):
        with pytest.raises(HumanReviewDashboardApiError) as exc_info:
            _get_json(
                path=("/internal/human-reviews/admin/reviews"),
                admin_user_id=("admin@inna.ai"),
            )

    message = str(exc_info.value)

    assert expected_text in message.lower()
    assert "segredo-banco-interno" not in message

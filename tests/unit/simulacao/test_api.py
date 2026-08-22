from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.human_review_routes import router
from api.security.internal_request import (
    TrustedRequestContext,
    require_trusted_request_context,
)

from src.services.human_review import (
    repository,
    service,
)
from src.services.human_review.contracts import (
    HumanReviewRecord,
)
from src.services.human_review.exceptions import (
    HumanReviewConflictError,
    HumanReviewNotFoundError,
)


def _record(
    *,
    status: str = "pending",
) -> HumanReviewRecord:
    now = datetime.now(timezone.utc)

    return HumanReviewRecord(
        id=1,
        review_id="review-001",
        thread_id="thread-001",
        status=status,
        requested_by="policy",
        reason="Risco elevado.",
        trigger="high_risk",
        risk_level="high",
        payload={},
        decision_action=(
            "approve"
            if status == "approved"
            else ""
        ),
        reviewer_id=(
            "admin-001"
            if status == "approved"
            else ""
        ),
        reviewer_comment="",
        rejection_reason="",
        corrections={},
        resume_route=(
            "handoff_coordinator"
            if status == "approved"
            else ""
        ),
        processing_request_id="",
        processing_started_at=None,
        failure_reason="",
        created_at=now,
        updated_at=now,
        resolved_at=(
            now
            if status == "approved"
            else None
        ),
    )


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(
        router
    )

    def trusted_context():
        return TrustedRequestContext(
            user_id="admin-001",
            request_id=(
                "request-00000001"
            ),
            timestamp=1_700_000_000,
        )

    app.dependency_overrides[
        require_trusted_request_context
    ] = trusted_context

    return TestClient(
        app
    )


def test_register_human_review(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "registrar_revisao_pendente",
        lambda payload: (
            repository
            .HumanReviewWriteResult(
                record=_record(),
                status="created",
            )
        ),
    )

    response = client.post(
        "/internal/human-reviews/register",
        json={
            "type": "human_review",
            "version": "1.0",
            "review_id": "review-001",
            "thread_id": "thread-001",
            "status": "pending",
            "requested_by": "policy",
            "reason": "Risco elevado.",
            "trigger": "high_risk",
            "risk_level": "high",
            "payload": {},
            "allowed_actions": [
                "approve",
                "correct",
                "reject",
                "cancel",
            ],
        },
    )

    assert response.status_code == 201
    assert response.json()[
        "created"
    ] is True


def test_list_pending_human_reviews(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "listar_revisoes_pendentes",
        lambda **_: [
            _record(),
        ],
    )

    response = client.get(
        "/internal/human-reviews/pending"
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_get_human_review_not_found(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_not_found(
        review_id,
    ):
        raise HumanReviewNotFoundError(
            "A revisão humana não foi encontrada."
        )

    monkeypatch.setattr(
        service,
        "consultar_revisao",
        raise_not_found,
    )

    response = client.get(
        "/internal/human-reviews/review-404"
    )

    assert response.status_code == 404


def test_resolve_human_review(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    outcome = (
        service
        .HumanReviewResolutionOutcome(
            review=_record(
                status="approved"
            ),
            graph_status="approved",
            resume_route=(
                "handoff_coordinator"
            ),
        )
    )

    captured = {}

    def fake_resolve(**kwargs):
        captured.update(
            kwargs
        )
        return outcome

    monkeypatch.setattr(
        service,
        "resolver_revisao_humana",
        fake_resolve,
    )

    response = client.post(
        (
            "/internal/human-reviews/"
            "review-001/resolve"
        ),
        json={
            "thread_id": "thread-001",
            "action": "approve",
            "comment": "Aprovado.",
        },
    )

    assert response.status_code == 200

    assert (
        captured[
            "trusted_reviewer_id"
        ]
        == "admin-001"
    )

    assert (
        "reviewer_id"
        not in captured[
            "decision_payload"
        ]
    )


def test_resolve_conflict_returns_409(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_conflict(**_):
        raise HumanReviewConflictError(
            "A revisão já foi processada."
        )

    monkeypatch.setattr(
        service,
        "resolver_revisao_humana",
        raise_conflict,
    )

    response = client.post(
        (
            "/internal/human-reviews/"
            "review-001/resolve"
        ),
        json={
            "thread_id": "thread-001",
            "action": "approve",
        },
    )

    assert response.status_code == 409


def test_reject_requires_reason(
    client: TestClient,
) -> None:
    response = client.post(
        (
            "/internal/human-reviews/"
            "review-001/resolve"
        ),
        json={
            "thread_id": "thread-001",
            "action": "reject",
        },
    )

    assert response.status_code == 422


def test_reviewer_id_is_forbidden_in_body(
    client: TestClient,
) -> None:
    response = client.post(
        (
            "/internal/human-reviews/"
            "review-001/resolve"
        ),
        json={
            "thread_id": "thread-001",
            "action": "approve",
            "reviewer_id": "fake-user",
        },
    )

    assert response.status_code == 422


def test_recover_stale_claims(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "recuperar_claims_expirados",
        lambda **_: [
            "review-001",
            "review-002",
        ],
    )

    response = client.post(
        (
            "/internal/human-reviews/"
            "recover-stale"
        ),
        json={
            "timeout_seconds": 300,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()[
            "recovered_count"
        ]
        == 2
    )

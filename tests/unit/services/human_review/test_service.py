from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from src.services.human_review import (
    repository,
    service,
)
from src.services.human_review.contracts import (
    HumanReviewRecord,
)
from src.services.human_review.exceptions import (
    HumanReviewResumeError,
    HumanReviewValidationError,
)


def _record(
    *,
    status: str,
    action: str = "",
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
        decision_action=action,
        reviewer_id="admin-001",
        reviewer_comment="",
        rejection_reason="",
        corrections={},
        resume_route="handoff_coordinator",
        processing_request_id="",
        processing_started_at=None,
        failure_reason="",
        created_at=now,
        updated_at=now,
        resolved_at=(
            now
            if status in {
                "approved",
                "corrected",
                "rejected",
                "cancelled",
            }
            else None
        ),
    )


def test_resolver_revisao_approve(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    claimed: list[Any] = []
    finalized: list[Any] = []

    def fake_claim(command):
        claimed.append(command)
        return _record(status="processing")

    def fake_finalize(
        command,
        *,
        status,
        resume_route,
    ):
        finalized.append(
            (
                command,
                status,
                resume_route,
            )
        )

        return _record(
            status="approved",
            action="approve",
        )

    monkeypatch.setattr(
        repository,
        "reivindicar_revisao",
        fake_claim,
    )

    monkeypatch.setattr(
        repository,
        "finalizar_revisao",
        fake_finalize,
    )

    def fake_resume(
        *,
        thread_id,
        decisao,
    ):
        assert thread_id == "thread-001"
        assert decisao["action"] == "approve"
        assert decisao["reviewer_id"] == "admin-001"

        return {
            "human_review_current": {
                "review_id": "review-001",
                "thread_id": "thread-001",
                "status": "approved",
            },
            "human_review_status": "approved",
            "human_review_resume_route": (
                "handoff_coordinator"
            ),
        }

    outcome = service.resolver_revisao_humana(
        review_id="review-001",
        thread_id="thread-001",
        trusted_reviewer_id="admin-001",
        request_id="request-00000001",
        decision_payload={
            "action": "approve",
            "comment": "Aprovado.",
        },
        resume_function=fake_resume,
    )

    assert len(claimed) == 1
    assert len(finalized) == 1
    assert outcome.review.status == "approved"
    assert (
        outcome.resume_route
        == "handoff_coordinator"
    )


def test_reviewer_body_nao_pode_trocar_identidade(
) -> None:
    with pytest.raises(
        HumanReviewValidationError
    ):
        service.resolver_revisao_humana(
            review_id="review-001",
            thread_id="thread-001",
            trusted_reviewer_id="admin-001",
            request_id="request-00000001",
            decision_payload={
                "action": "approve",
                "reviewer_id": "outro-usuario",
            },
            resume_function=lambda **_: {},
        )


def test_correct_exige_corrections() -> None:
    with pytest.raises(
        HumanReviewValidationError
    ):
        service.resolver_revisao_humana(
            review_id="review-001",
            thread_id="thread-001",
            trusted_reviewer_id="admin-001",
            request_id="request-00000001",
            decision_payload={
                "action": "correct",
            },
            resume_function=lambda **_: {},
        )


def test_status_do_grafo_deve_corresponder_acao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure_calls: list[Any] = []

    monkeypatch.setattr(
        repository,
        "reivindicar_revisao",
        lambda command: _record(
            status="processing"
        ),
    )

    def fake_failure(
        command,
        *,
        failure_reason,
    ):
        failure_calls.append(
            (
                command,
                failure_reason,
            )
        )

        return _record(
            status="resume_failed"
        )

    monkeypatch.setattr(
        repository,
        "registrar_falha_retomada",
        fake_failure,
    )

    def fake_resume(**_):
        return {
            "human_review_current": {
                "review_id": "review-001",
                "thread_id": "thread-001",
                "status": "rejected",
            },
            "human_review_status": "rejected",
            "human_review_resume_route": (
                "conversation_summary"
            ),
        }

    with pytest.raises(
        HumanReviewResumeError
    ):
        service.resolver_revisao_humana(
            review_id="review-001",
            thread_id="thread-001",
            trusted_reviewer_id="admin-001",
            request_id="request-00000001",
            decision_payload={
                "action": "approve",
            },
            resume_function=fake_resume,
        )

    assert len(failure_calls) == 1


def test_falha_no_langgraph_marca_resume_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure_calls: list[Any] = []

    monkeypatch.setattr(
        repository,
        "reivindicar_revisao",
        lambda command: _record(
            status="processing"
        ),
    )

    def fake_failure(
        command,
        *,
        failure_reason,
    ):
        failure_calls.append(
            failure_reason
        )

        return _record(
            status="resume_failed"
        )

    monkeypatch.setattr(
        repository,
        "registrar_falha_retomada",
        fake_failure,
    )

    def fake_resume(**_):
        raise RuntimeError(
            "erro interno sensível"
        )

    with pytest.raises(
        HumanReviewResumeError
    ):
        service.resolver_revisao_humana(
            review_id="review-001",
            thread_id="thread-001",
            trusted_reviewer_id="admin-001",
            request_id="request-00000001",
            decision_payload={
                "action": "approve",
            },
            resume_function=fake_resume,
        )

    assert len(failure_calls) == 1
    assert (
        "erro interno sensível"
        not in failure_calls[0]
    )


def test_registrar_payload_de_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Any] = []

    def fake_create(record):
        captured.append(record)

        return repository.HumanReviewWriteResult(
            record=_record(status="pending"),
            status="created",
        )

    monkeypatch.setattr(
        repository,
        "criar_revisao_pendente",
        fake_create,
    )

    result = service.registrar_revisao_pendente({
        "type": "human_review",
        "version": "1.0",
        "review_id": "review-001",
        "thread_id": "thread-001",
        "status": "pending",
        "requested_by": "policy",
        "reason": "Risco elevado.",
        "trigger": "high_risk",
        "risk_level": "high",
        "payload": {
            "resposta": "Em revisão",
        },
        "allowed_actions": [
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
    })

    assert result.created is True
    assert len(captured) == 1
    assert captured[0].review_id == "review-001"


@pytest.mark.parametrize(
    "interrupt_status",
    [
        "requested",
        "waiting",
    ],
)
def test_registrar_interrupt_normaliza_status_pendente(
    monkeypatch: pytest.MonkeyPatch,
    interrupt_status: str,
) -> None:
    captured: list[Any] = []

    def fake_create(record):
        captured.append(record)

        return repository.HumanReviewWriteResult(
            record=_record(status="pending"),
            status="created",
        )

    monkeypatch.setattr(
        repository,
        "criar_revisao_pendente",
        fake_create,
    )

    result = service.registrar_revisao_pendente({
        "type": "human_review",
        "version": "1.0",
        "review_id": "review-status-test",
        "thread_id": "thread-status-test",
        "status": interrupt_status,
        "requested_by": "human_review_policy",
        "reason": "Revisão forçada.",
        "trigger": "forced_review",
        "risk_level": "medium",
        "payload": {},
        "allowed_actions": [
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
    })

    assert result.created is True
    assert len(captured) == 1
    assert captured[0].status == "pending"


def test_registrar_interrupt_rejeita_status_desconhecido(
) -> None:
    with pytest.raises(
        HumanReviewValidationError
    ):
        service.registrar_revisao_pendente({
            "type": "human_review",
            "review_id": "review-invalid-status",
            "thread_id": "thread-invalid-status",
            "status": "completed",
            "payload": {},
        })

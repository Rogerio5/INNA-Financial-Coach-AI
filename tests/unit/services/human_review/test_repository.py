from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

import pytest

from src.services.human_review import repository
from src.services.human_review.contracts import (
    HumanReviewDecision,
    HumanReviewPendingRecord,
    HumanReviewResolutionCommand,
    TrustedHumanReviewContext,
)
from src.services.human_review.exceptions import (
    HumanReviewConflictError,
    HumanReviewNotFoundError,
)


def _database_row(
    *,
    review_id: str = "review-001",
    thread_id: str = "thread-001",
    status: str = "pending",
    processing_request_id: str = "",
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    return {
        "id": 1,
        "review_id": review_id,
        "thread_id": thread_id,
        "status": status,
        "requested_by": "human_review_policy",
        "reason": "Risco elevado.",
        "trigger": "high_risk",
        "risk_level": "high",
        "payload": {
            "resposta": "Conteúdo em revisão.",
        },
        "allowed_actions": [
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
        "decision_action": "",
        "reviewer_id": "",
        "reviewer_comment": "",
        "rejection_reason": "",
        "corrections": {},
        "resume_route": "",
        "processing_request_id": (processing_request_id),
        "processing_started_at": None,
        "failure_reason": "",
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
    }


def _pending_record() -> HumanReviewPendingRecord:
    return HumanReviewPendingRecord(
        review_id="review-001",
        thread_id="thread-001",
        status="pending",
        requested_by="human_review_policy",
        reason="Risco elevado.",
        trigger="high_risk",
        risk_level="high",
        payload={
            "resposta": "Conteúdo em revisão.",
        },
    )


def _resolution_command(
    *,
    action: str = "approve",
    request_id: str = "request-00000001",
) -> HumanReviewResolutionCommand:
    decision_data: dict[str, Any] = {
        "action": action,
        "reviewer_id": "admin-001",
    }

    if action == "correct":
        decision_data["corrections"] = {
            "resposta": "Resposta corrigida.",
        }

    if action == "reject":
        decision_data["reason"] = "Resposta não aprovada."

    return HumanReviewResolutionCommand(
        review_id="review-001",
        thread_id="thread-001",
        context=TrustedHumanReviewContext(
            reviewer_id="admin-001",
            request_id=request_id,
        ),
        decision=HumanReviewDecision(**decision_data),
    )


class FakeCursor:
    def __init__(
        self,
        *,
        fetchone_values: list[Any] | None = None,
        fetchall_value: list[Any] | None = None,
    ) -> None:
        self.fetchone_values = list(fetchone_values or [])

        self.fetchall_value = list(fetchall_value or [])

        self.executions: list[tuple[str, Any]] = []

    def execute(
        self,
        sql: str,
        parameters: Any = None,
    ) -> None:
        self.executions.append(
            (
                sql,
                parameters,
            )
        )

    def fetchone(
        self,
    ) -> Any:
        if not self.fetchone_values:
            return None

        return self.fetchone_values.pop(0)

    def fetchall(
        self,
    ) -> list[Any]:
        return list(self.fetchall_value)


def _install_fake_cursor(
    monkeypatch: pytest.MonkeyPatch,
    fake_cursor: FakeCursor,
) -> None:
    @contextmanager
    def fake_cursor_postgres(
        **_: Any,
    ):
        yield fake_cursor

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        fake_cursor_postgres,
    )


def test_criar_revisao_pendente_created(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = _database_row()

    cursor = FakeCursor(
        fetchone_values=[
            row,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.criar_revisao_pendente(_pending_record())

    assert result.created is True
    assert result.status == "created"
    assert result.record.review_id == "review-001"
    assert result.record.thread_id == "thread-001"


def test_criar_revisao_pendente_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = _database_row()

    cursor = FakeCursor(
        fetchone_values=[
            None,
            row,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.criar_revisao_pendente(_pending_record())

    assert result.created is False
    assert result.status == "existing"


def test_criar_revisao_conflita_com_outro_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = _database_row(
        thread_id="thread-diferente",
    )

    cursor = FakeCursor(
        fetchone_values=[
            None,
            existing,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(HumanReviewConflictError):
        repository.criar_revisao_pendente(_pending_record())


def test_obter_revisao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        fetchone_values=[
            _database_row(),
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.obter_revisao("review-001")

    assert result is not None
    assert result.review_id == "review-001"
    assert result.status == "pending"


def test_listar_revisoes_pendentes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        fetchall_value=[
            _database_row(review_id="review-001"),
            _database_row(
                review_id="review-002",
                thread_id="thread-002",
                status="resume_failed",
            ),
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    results = repository.listar_revisoes_pendentes(
        limit=20,
        offset=0,
    )

    assert len(results) == 2
    assert results[0].review_id == "review-001"
    assert results[1].status == "resume_failed"


def test_reivindicar_revisao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = _resolution_command()

    row = _database_row(
        status="processing",
        processing_request_id=(command.context.request_id),
    )

    cursor = FakeCursor(
        fetchone_values=[
            row,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.reivindicar_revisao(command)

    assert result.status == "processing"
    assert result.processing_request_id == command.context.request_id


def test_reivindicar_revisao_inexistente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        fetchone_values=[
            None,
            None,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(HumanReviewNotFoundError):
        repository.reivindicar_revisao(_resolution_command())


def test_finalizar_revisao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = _resolution_command(
        action="approve",
    )

    row = _database_row(
        status="approved",
    )

    row.update(
        {
            "decision_action": "approve",
            "reviewer_id": "admin-001",
            "resolved_at": datetime.now(timezone.utc),
        }
    )

    cursor = FakeCursor(
        fetchone_values=[
            row,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.finalizar_revisao(
        command,
        status="approved",
        resume_route="handoff_coordinator",
    )

    assert result.status == "approved"
    assert result.decision_action == "approve"
    assert result.reviewer_id == "admin-001"


def test_registrar_falha_retomada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = _resolution_command()

    row = _database_row(
        status="resume_failed",
    )

    row["failure_reason"] = "Falha controlada no LangGraph."

    cursor = FakeCursor(
        fetchone_values=[
            row,
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.registrar_falha_retomada(
        command,
        failure_reason=("Falha controlada no LangGraph."),
    )

    assert result.status == "resume_failed"
    assert result.failure_reason != ""


def test_liberar_claims_expirados(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        fetchall_value=[
            {
                "review_id": "review-001",
            },
            {
                "review_id": "review-002",
            },
        ],
    )

    _install_fake_cursor(
        monkeypatch,
        cursor,
    )

    result = repository.liberar_claims_expirados(timeout_seconds=300)

    assert result == [
        "review-001",
        "review-002",
    ]

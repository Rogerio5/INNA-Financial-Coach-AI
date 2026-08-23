from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime

import pytest

from src.reliability import repository
from src.resilience import (
    ResilienceEvent,
    ResilienceEventType,
)


class FakeCursor:
    def __init__(
        self,
        *,
        rows=None,
    ):
        self.executions = []
        self.rows = list(
            rows or []
        )

    def execute(
        self,
        sql,
        parameters=None,
    ):
        self.executions.append(
            (
                sql,
                parameters,
            )
        )

    def fetchone(self):
        if not self.rows:
            return None

        return self.rows.pop(0)


def _cursor_factory(
    cursor,
):
    @contextmanager
    def fake_cursor_postgres(
        **_,
    ):
        yield cursor

    return fake_cursor_postgres


def _event(
    event_type=(
        ResilienceEventType
        .OPERATION_SUCCEEDED
    ),
    *,
    operation="gemini.embedding",
    event_id="event-001",
):
    return ResilienceEvent(
        operation=operation,
        event_type=event_type,
        attempt_number=1,
        max_attempts=2,
        event_id=event_id,
        occurred_at=datetime(
            2026,
            8,
            15,
            4,
            0,
            tzinfo=UTC,
        ),
    )


def test_schema_contains_real_postgres_invariants():
    sql = repository.SQL_CREATE_TABLE

    assert (
        "TIMESTAMPTZ"
        in sql
    )

    assert (
        "event_id VARCHAR(128) PRIMARY KEY"
        in sql
    )

    assert (
        "'gemini.embedding'"
        in sql
    )

    assert (
        "'gemini.generate.supervisor'"
        in sql
    )

    assert (
        "'gemini.generate.text_service'"
        in sql
    )

    assert (
        "'rag.agentic.planner'"
        in sql
    )

    assert (
        "circuit_rejected"
        in sql
    )


def test_schema_indexes_operation_and_time():
    assert (
        "operation"
        in (
            repository
            .SQL_CREATE_OPERATION_TIME_INDEX
        )
    )

    assert (
        "occurred_at DESC"
        in (
            repository
            .SQL_CREATE_OPERATION_TIME_INDEX
        )
    )

    assert (
        "WHERE outcome = 'failed'"
        in (
            repository
            .SQL_CREATE_FAILURE_TIME_INDEX
        )
    )


def test_schema_initialization_executes_all_ddl(
    monkeypatch,
):
    cursor = FakeCursor()

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    (
        repository
        .initialize_production_reliability_schema()
    )

    assert len(
        cursor.executions
    ) == 3


def test_success_event_is_persisted_idempotently(
    monkeypatch,
):
    recorded_at = datetime(
        2026,
        8,
        15,
        4,
        0,
        1,
        tzinfo=UTC,
    )

    cursor = FakeCursor(
        rows=[
            {
                "event_id": "event-001",
                "recorded_at": recorded_at,
            }
        ]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    result = (
        repository
        .persist_production_reliability_event(
            _event()
        )
    )

    assert result.inserted
    assert result.event_id == "event-001"

    _, parameters = (
        cursor.executions[0]
    )

    assert (
        parameters["outcome"]
        == "succeeded"
    )

    assert (
        parameters["circuit_rejected"]
        is False
    )


def test_failure_event_is_persisted_as_failed(
    monkeypatch,
):
    cursor = FakeCursor(
        rows=[
            {
                "event_id": "failure-001",
                "recorded_at": datetime.now(
                    UTC
                ),
            }
        ]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    (
        repository
        .persist_production_reliability_event(
            _event(
                ResilienceEventType
                .OPERATION_FAILED,
                event_id="failure-001",
            )
        )
    )

    _, parameters = (
        cursor.executions[0]
    )

    assert (
        parameters["outcome"]
        == "failed"
    )

    assert (
        parameters["circuit_rejected"]
        is False
    )


def test_circuit_rejection_is_failed_unavailability(
    monkeypatch,
):
    cursor = FakeCursor(
        rows=[
            {
                "event_id": "circuit-001",
                "recorded_at": datetime.now(
                    UTC
                ),
            }
        ]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    (
        repository
        .persist_production_reliability_event(
            _event(
                ResilienceEventType
                .CIRCUIT_REJECTED,
                event_id="circuit-001",
            )
        )
    )

    _, parameters = (
        cursor.executions[0]
    )

    assert (
        parameters["outcome"]
        == "failed"
    )

    assert (
        parameters["circuit_rejected"]
        is True
    )


def test_duplicate_event_is_not_inserted_twice(
    monkeypatch,
):
    cursor = FakeCursor(
        rows=[]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    result = (
        repository
        .persist_production_reliability_event(
            _event()
        )
    )

    assert not result.inserted

    assert (
        "ON CONFLICT (event_id)"
        in cursor.executions[0][0]
    )

    assert (
        "DO NOTHING"
        in cursor.executions[0][0]
    )


@pytest.mark.parametrize(
    "event_type",
    [
        ResilienceEventType
        .ATTEMPT_STARTED,
        ResilienceEventType
        .ATTEMPT_FAILED,
        ResilienceEventType
        .RETRY_SCHEDULED,
    ],
)
def test_nonterminal_events_cannot_enter_ledger(
    event_type,
):
    with pytest.raises(
        ValueError,
        match="terminal",
    ):
        (
            repository
            .persist_production_reliability_event(
                _event(
                    event_type
                )
            )
        )


def test_unknown_operation_cannot_enter_ledger():
    with pytest.raises(
        ValueError,
        match="tracked",
    ):
        (
            repository
            .persist_production_reliability_event(
                _event(
                    operation=(
                        "unknown.service"
                    )
                )
            )
        )


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def broken_cursor(
        **_,
    ):
        raise RuntimeError(
            "postgres://secret@private-host/"
            "provider-detail"
        )

        yield

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        broken_cursor,
    )

    with pytest.raises(
        repository
        .ProductionReliabilityRepositoryError
    ) as captured:
        (
            repository
            .persist_production_reliability_event(
                _event()
            )
        )

    public_message = str(
        captured.value
    ).lower()

    assert "secret" not in public_message
    assert "private-host" not in public_message
    assert "provider-detail" not in public_message


def test_window_query_uses_database_clock(
    monkeypatch,
):
    cursor = FakeCursor(
        rows=[
            {
                "total_operations": 200,
                "successful_operations": 198,
                "failed_operations": 2,
                "circuit_rejections": 1,
                "first_occurred_at": (
                    datetime.now(
                        UTC
                    )
                ),
                "last_occurred_at": (
                    datetime.now(
                        UTC
                    )
                ),
            }
        ]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    window = (
        repository
        .load_production_reliability_window(
            operation=(
                "gemini.embedding"
            ),
            window_seconds=900,
        )
    )

    assert (
        window.total_operations
        == 200
    )

    assert (
        window.successful_operations
        == 198
    )

    assert (
        window.failed_operations
        == 2
    )

    assert (
        window.circuit_rejections
        == 1
    )

    assert (
        window.observed_failure_ratio
        == pytest.approx(0.01)
    )

    sql, parameters = (
        cursor.executions[0]
    )

    assert "NOW()" in sql

    assert (
        parameters[
            "window_seconds"
        ]
        == 900.0
    )


@pytest.mark.parametrize(
    "window",
    [
        0,
        -1,
        float("nan"),
        float("inf"),
        (31 * 24 * 60 * 60) + 1,
    ],
)
def test_invalid_window_is_rejected(
    window,
):
    with pytest.raises(ValueError):
        (
            repository
            .load_production_reliability_window(
                operation=(
                    "gemini.embedding"
                ),
                window_seconds=window,
            )
        )


def test_inconsistent_database_aggregate_is_rejected(
    monkeypatch,
):
    cursor = FakeCursor(
        rows=[
            {
                "total_operations": 100,
                "successful_operations": 90,
                "failed_operations": 5,
                "circuit_rejections": 0,
                "first_occurred_at": None,
                "last_occurred_at": None,
            }
        ]
    )

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        _cursor_factory(
            cursor
        ),
    )

    with pytest.raises(
        repository
        .ProductionReliabilityRepositoryError,
        match="inconsistent",
    ):
        (
            repository
            .load_production_reliability_window(
                operation=(
                    "gemini.embedding"
                )
            )
        )


def test_ledger_sql_has_no_user_content_fields():
    rendered = " ".join(
        (
            repository.SQL_CREATE_TABLE,
            repository.SQL_INSERT_EVENT,
            repository.SQL_WINDOW_AGGREGATE,
        )
    ).lower()

    forbidden = {
        "prompt",
        "response",
        "api_key",
        "password",
        "user_id",
        "chat_id",
        "provider_error",
        "error_message",
    }

    for field in forbidden:
        assert field not in rendered

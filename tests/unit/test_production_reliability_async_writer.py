from __future__ import annotations

import threading
from datetime import UTC, datetime

from src.reliability.async_writer import (
    ProductionReliabilityAsyncWriter,
)
from src.reliability.repository import (
    ProductionReliabilityLedgerWrite,
)
from src.resilience import (
    ResilienceEvent,
    ResilienceEventType,
)


def _event(
    *,
    event_id="event-001",
    operation="gemini.embedding",
    event_type=(
        ResilienceEventType
        .OPERATION_SUCCEEDED
    ),
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


def _inserted(
    event,
):
    return ProductionReliabilityLedgerWrite(
        event_id=event.event_id,
        inserted=True,
        recorded_at=datetime.now(
            UTC
        ),
    )


def test_disabled_writer_never_starts_worker():
    persisted = []

    writer = ProductionReliabilityAsyncWriter(
        enabled=False,
        persist_event=lambda event: (
            persisted.append(event)
            or _inserted(event)
        ),
        initialize_schema=lambda: None,
    )

    assert not writer.enqueue(
        _event()
    )

    snapshot = writer.snapshot()

    assert not snapshot.worker_running
    assert snapshot.worker_starts == 0
    assert persisted == []


def test_nonterminal_event_is_not_persisted():
    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=_inserted,
        initialize_schema=lambda: None,
    )

    assert not writer.enqueue(
        _event(
            event_type=(
                ResilienceEventType
                .ATTEMPT_FAILED
            )
        )
    )

    snapshot = writer.snapshot()

    assert (
        snapshot.ignored_nonterminal_events
        == 1
    )

    assert snapshot.worker_starts == 0


def test_untracked_operation_is_not_persisted():
    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=_inserted,
        initialize_schema=lambda: None,
    )

    assert not writer.enqueue(
        _event(
            operation="other.operation"
        )
    )

    assert (
        writer.snapshot()
        .ignored_untracked_events
        == 1
    )


def test_worker_starts_lazily_on_first_real_event():
    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=_inserted,
        initialize_schema=lambda: None,
        retry_base_delay_seconds=0,
    )

    assert writer.snapshot().worker_starts == 0

    assert writer.enqueue(
        _event()
    )

    assert writer.flush(
        timeout_seconds=2
    )

    snapshot = writer.snapshot()

    assert snapshot.worker_starts == 1
    assert snapshot.persisted_events == 1

    assert writer.shutdown(
        timeout_seconds=2
    )


def test_schema_initializes_once_per_writer():
    initialized = []

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=_inserted,
        initialize_schema=lambda: (
            initialized.append(True)
        ),
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event(
            event_id="one"
        )
    )

    assert writer.enqueue(
        _event(
            event_id="two"
        )
    )

    assert writer.flush(
        timeout_seconds=2
    )

    assert len(initialized) == 1

    assert (
        writer.snapshot()
        .persisted_events
        == 2
    )

    writer.shutdown(
        timeout_seconds=2
    )


def test_duplicate_is_counted_without_failure():
    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        initialize_schema=lambda: None,
        persist_event=lambda event: (
            ProductionReliabilityLedgerWrite(
                event_id=event.event_id,
                inserted=False,
                recorded_at=None,
            )
        ),
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event()
    )

    assert writer.flush(
        timeout_seconds=2
    )

    snapshot = writer.snapshot()

    assert snapshot.duplicate_events == 1
    assert snapshot.persistence_failures == 0

    writer.shutdown(
        timeout_seconds=2
    )


def test_database_failure_never_escapes_enqueue():
    attempts = []

    def fail(_):
        attempts.append(True)

        raise RuntimeError(
            "postgres://secret@private-host/"
        )

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        initialize_schema=lambda: None,
        persist_event=fail,
        max_persist_attempts=2,
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event()
    )

    assert writer.flush(
        timeout_seconds=2
    )

    snapshot = writer.snapshot()

    assert len(attempts) == 2
    assert snapshot.retry_attempts == 1
    assert snapshot.persistence_failures == 1

    writer.shutdown(
        timeout_seconds=2
    )


def test_retry_then_success():
    attempts = []

    def persist(event):
        attempts.append(True)

        if len(attempts) == 1:
            raise RuntimeError(
                "temporary database failure"
            )

        return _inserted(event)

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        initialize_schema=lambda: None,
        persist_event=persist,
        max_persist_attempts=3,
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event()
    )

    assert writer.flush(
        timeout_seconds=2
    )

    snapshot = writer.snapshot()

    assert len(attempts) == 2
    assert snapshot.retry_attempts == 1
    assert snapshot.persisted_events == 1
    assert snapshot.persistence_failures == 0

    writer.shutdown(
        timeout_seconds=2
    )


def test_queue_is_bounded_and_drops_instead_of_blocking():
    started = threading.Event()
    release = threading.Event()

    def persist(event):
        started.set()

        release.wait(
            timeout=2
        )

        return _inserted(event)

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        max_queue_size=1,
        persist_event=persist,
        initialize_schema=lambda: None,
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event(
            event_id="first"
        )
    )

    assert started.wait(
        timeout=2
    )

    assert writer.enqueue(
        _event(
            event_id="second"
        )
    )

    assert not writer.enqueue(
        _event(
            event_id="third"
        )
    )

    assert (
        writer.snapshot()
        .queue_full_drops
        == 1
    )

    release.set()

    assert writer.flush(
        timeout_seconds=2
    )

    writer.shutdown(
        timeout_seconds=2
    )


def test_flush_timeout_does_not_block_forever():
    started = threading.Event()
    release = threading.Event()

    def persist(event):
        started.set()

        release.wait(
            timeout=2
        )

        return _inserted(event)

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=persist,
        initialize_schema=lambda: None,
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event()
    )

    assert started.wait(
        timeout=2
    )

    assert not writer.flush(
        timeout_seconds=0.01
    )

    release.set()

    assert writer.flush(
        timeout_seconds=2
    )

    writer.shutdown(
        timeout_seconds=2
    )


def test_writer_snapshot_contains_no_content_fields():
    writer = ProductionReliabilityAsyncWriter(
        enabled=False
    )

    payload = repr(
        writer.snapshot()
        .to_safe_dict()
    ).lower()

    forbidden = {
        "prompt",
        "response",
        "payload",
        "api_key",
        "password",
        "user_id",
        "chat_id",
        "database_url",
    }

    for field in forbidden:
        assert field not in payload



def test_shutdown_drains_and_rejects_new_events():
    persisted = []

    def persist(event):
        persisted.append(
            event.event_id
        )

        return _inserted(
            event
        )

    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=persist,
        initialize_schema=lambda: None,
        retry_base_delay_seconds=0,
    )

    assert writer.enqueue(
        _event(
            event_id="accepted-before-shutdown"
        )
    )

    assert writer.shutdown(
        timeout_seconds=2
    )

    snapshot = writer.snapshot()

    assert (
        "accepted-before-shutdown"
        in persisted
    )

    assert snapshot.pending_events == 0

    assert not writer.enqueue(
        _event(
            event_id="rejected-after-shutdown"
        )
    )

    assert (
        "rejected-after-shutdown"
        not in persisted
    )


def test_fast_writer_leaves_no_phantom_pending_events():
    writer = ProductionReliabilityAsyncWriter(
        enabled=True,
        persist_event=_inserted,
        initialize_schema=lambda: None,
        retry_base_delay_seconds=0,
    )

    for number in range(200):
        assert writer.enqueue(
            _event(
                event_id=(
                    f"fast-{number}"
                )
            )
        )

    assert writer.flush(
        timeout_seconds=3
    )

    snapshot = writer.snapshot()

    assert snapshot.pending_events == 0

    assert (
        snapshot.persisted_events
        == 200
    )

    assert writer.shutdown(
        timeout_seconds=2
    )

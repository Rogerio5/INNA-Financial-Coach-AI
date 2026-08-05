from __future__ import annotations

from src.services.telegram_observability import (
    InMemoryTelegramOperationalEventSink,
    NoOpTelegramOperationalEventSink,
    TelegramOperationalEvent,
)


def _event(
    *,
    name="telegram_session_save_completed",
    outcome="success",
):
    return TelegramOperationalEvent(
        name=name,
        level="info",
        component="bridge",
        outcome=outcome,
        fields={
            "duration_ms": 10,
        },
    )


def test_noop_event_sink_accepts_event():
    sink = NoOpTelegramOperationalEventSink()

    sink.emit(_event())


def test_in_memory_sink_records_event():
    sink = InMemoryTelegramOperationalEventSink()

    sink.emit(_event())

    assert len(sink.snapshot()) == 1


def test_in_memory_sink_filters_events():
    sink = InMemoryTelegramOperationalEventSink()

    sink.emit(_event())

    sink.emit(
        TelegramOperationalEvent(
            name="telegram_worker_update_failed",
            level="error",
            component="worker",
            outcome="error",
            fields={
                "error_category": "unknown",
            },
        )
    )

    assert (
        sink.count(
            component="bridge",
            outcome="success",
        )
        == 1
    )

    assert (
        sink.count(
            name="telegram_worker_update_failed",
            level="error",
        )
        == 1
    )


def test_in_memory_sink_clear():
    sink = InMemoryTelegramOperationalEventSink()

    sink.emit(_event())

    sink.clear()

    assert sink.snapshot() == ()

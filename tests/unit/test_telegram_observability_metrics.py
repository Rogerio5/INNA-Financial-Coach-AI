from __future__ import annotations

from src.services.telegram_observability import (
    InMemoryTelegramConversationMetrics,
    NoOpTelegramConversationMetrics,
    TelegramConversationMetricRecord,
)


def _record(
    *,
    operation="save_session",
    outcome="success",
    duration_ms=10,
    error_category=None,
):
    return TelegramConversationMetricRecord(
        operation=operation,
        component="bridge",
        outcome=outcome,
        duration_ms=duration_ms,
        error_category=error_category,
    )


def test_noop_metrics_accepts_record():
    metrics = (
        NoOpTelegramConversationMetrics()
    )

    metrics.record_operation(
        _record()
    )


def test_in_memory_metrics_records_snapshot():
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    metrics.record_operation(
        _record()
    )

    snapshot = metrics.snapshot()

    assert len(snapshot) == 1
    assert snapshot[0].operation == "save_session"


def test_in_memory_metrics_filters_counts():
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    metrics.record_operation(
        _record()
    )

    metrics.record_operation(
        _record(
            operation="reload_session",
            outcome="error",
            error_category="persistence",
        )
    )

    assert metrics.count(
        operation="save_session",
        outcome="success",
    ) == 1

    assert metrics.count(
        outcome="error",
        error_category="persistence",
    ) == 1


def test_in_memory_metrics_preserves_durations():
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    metrics.record_operation(
        _record(
            duration_ms=8.5
        )
    )

    metrics.record_operation(
        _record(
            duration_ms=11.5
        )
    )

    assert metrics.durations_ms(
        operation="save_session"
    ) == (
        8.5,
        11.5,
    )


def test_in_memory_metrics_clear():
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    metrics.record_operation(
        _record()
    )

    metrics.clear()

    assert metrics.snapshot() == ()

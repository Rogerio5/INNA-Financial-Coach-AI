from __future__ import annotations

from unittest.mock import MagicMock

from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    NoOpTelegramProductiveOperations,
    SafeTelegramProductiveOperations,
    TelegramProductiveOperationsRecorder,
)


def total_for(
    snapshot,
    metric_name,
):
    return sum(
        snapshot.counters[
            metric_name
        ].values()
    )


def test_records_worker_cycle():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_worker_cycle(
        result="processed",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        "inna_telegram_worker_cycles_total",
    ) == 1.0


def test_records_worker_update_success():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_worker_update(
        outcome="success",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        "inna_telegram_worker_updates_total",
    ) == 1.0

    assert (
        "inna_telegram_failures_total"
        not in snapshot.counters
    )


def test_worker_error_records_failure():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_worker_update(
        outcome="error",
        error_category="dependency",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        "inna_telegram_worker_updates_total",
    ) == 1.0

    assert total_for(
        snapshot,
        "inna_telegram_failures_total",
    ) == 1.0


def test_records_completed_receipt():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_receipt(
        status="completed",
        outcome="success",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        "inna_telegram_receipts_total",
    ) == 1.0


def test_receipt_failure_records_aggregate_failure():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_receipt(
        status="failed",
        outcome="error",
        error_category="persistence",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        "inna_telegram_receipts_total",
    ) == 1.0

    assert total_for(
        snapshot,
        "inna_telegram_failures_total",
    ) == 1.0


def test_records_queue_operation():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_queue_operation(
        operation="enqueue",
        outcome="success",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        (
            "inna_telegram_"
            "queue_operations_total"
        ),
    ) == 1.0


def test_queue_error_records_failure():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_queue_operation(
        operation="claim",
        outcome="error",
        error_category="persistence",
    )

    snapshot = registry.snapshot()

    assert total_for(
        snapshot,
        (
            "inna_telegram_"
            "queue_operations_total"
        ),
    ) == 1.0

    assert total_for(
        snapshot,
        "inna_telegram_failures_total",
    ) == 1.0


def test_unknown_values_do_not_increase_cardinality():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    for value in range(100):
        recorder.record_worker_cycle(
            result=f"dynamic-{value}",
        )

    snapshot = registry.snapshot()

    series = snapshot.counters[
        "inna_telegram_worker_cycles_total"
    ]

    assert len(series) == 1

    labels, total = next(
        iter(series.items())
    )

    assert dict(labels) == {
        "worker_result": "unknown",
    }

    assert total == 100.0


def test_private_error_text_is_normalized():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    recorder = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    recorder.record_worker_update(
        outcome="error",
        error_category=(
            "private-financial-message"
        ),
    )

    snapshot = registry.snapshot()

    rendered = repr(
        snapshot
    )

    assert (
        "private-financial-message"
        not in rendered
    )

    assert "unknown" in rendered


def test_noop_accepts_all_operations():
    recorder = (
        NoOpTelegramProductiveOperations()
    )

    recorder.record_worker_cycle(
        result="anything"
    )

    recorder.record_worker_update(
        outcome="anything"
    )

    recorder.record_receipt(
        status="anything",
        outcome="anything",
    )

    recorder.record_queue_operation(
        operation="anything",
        outcome="anything",
    )


def test_safe_operations_swallow_failures():
    broken = MagicMock()

    broken.record_worker_cycle.side_effect = (
        RuntimeError("private")
    )

    broken.record_worker_update.side_effect = (
        RuntimeError("private")
    )

    broken.record_receipt.side_effect = (
        RuntimeError("private")
    )

    broken.record_queue_operation.side_effect = (
        RuntimeError("private")
    )

    recorder = (
        SafeTelegramProductiveOperations(
            broken
        )
    )

    assert recorder.record_worker_cycle(
        result="processed",
    ) is None

    assert recorder.record_worker_update(
        outcome="error",
    ) is None

    assert recorder.record_receipt(
        status="failed",
        outcome="error",
    ) is None

    assert recorder.record_queue_operation(
        operation="fail",
        outcome="error",
    ) is None

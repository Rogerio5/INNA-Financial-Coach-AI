from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.services.telegram_observability import (
    CompositeTelegramConversationMetrics,
    InMemoryTelegramProductiveMetrics,
    ProductiveTelegramConversationMetricsAdapter,
    TelegramConversationMetricRecord,
)


def metric_record(
    *,
    outcome: str = "success",
    error_category: str | None = None,
    conflict_recovered: bool | None = None,
):
    return TelegramConversationMetricRecord(
        operation="save_session",
        component="bridge",
        outcome=outcome,
        duration_ms=250.0,
        error_category=error_category,
        conflict_recovered=conflict_recovered,
    )


def test_adapter_records_operation_and_duration():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    adapter = (
        ProductiveTelegramConversationMetricsAdapter(
            registry
        )
    )

    adapter.record_operation(
        metric_record()
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_operations_total"
        in snapshot.counters
    )

    assert (
        "inna_telegram_operation_duration_seconds"
        in snapshot.histograms
    )

    operation_value = next(
        iter(
            snapshot.counters[
                "inna_telegram_operations_total"
            ].values()
        )
    )

    assert operation_value == 1.0

    histogram = next(
        iter(
            snapshot.histograms[
                (
                    "inna_telegram_"
                    "operation_duration_seconds"
                )
            ].values()
        )
    )

    assert histogram.count == 1
    assert histogram.sum == pytest.approx(
        0.25
    )


def test_adapter_records_failure():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    adapter = (
        ProductiveTelegramConversationMetricsAdapter(
            registry
        )
    )

    adapter.record_operation(
        metric_record(
            outcome="error",
            error_category="persistence",
        )
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_failures_total"
        in snapshot.counters
    )


def test_adapter_records_conflict():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    adapter = (
        ProductiveTelegramConversationMetricsAdapter(
            registry
        )
    )

    adapter.record_operation(
        metric_record(
            outcome="conflict",
            error_category=(
                "optimistic_conflict"
            ),
        )
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_conflicts_total"
        in snapshot.counters
    )


def test_adapter_records_recovered_conflict():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    adapter = (
        ProductiveTelegramConversationMetricsAdapter(
            registry
        )
    )

    adapter.record_operation(
        metric_record(
            outcome="recovered",
            error_category=(
                "optimistic_conflict"
            ),
            conflict_recovered=True,
        )
    )

    snapshot = registry.snapshot()

    values = snapshot.counters[
        "inna_telegram_conflicts_total"
    ]

    labels, value = next(
        iter(values.items())
    )

    assert dict(labels)[
        "outcome"
    ] == "recovered"

    assert value == 1.0


def test_composite_sends_same_record_to_all():
    first = MagicMock()
    second = MagicMock()

    composite = (
        CompositeTelegramConversationMetrics(
            [
                first,
                second,
            ]
        )
    )

    metric = metric_record()

    composite.record_operation(
        metric
    )

    first.record_operation\
        .assert_called_once_with(
            metric
        )

    second.record_operation\
        .assert_called_once_with(
            metric
        )


def test_composite_isolates_failure_between_sinks():
    broken = MagicMock()

    broken.record_operation.side_effect = (
        RuntimeError(
            "private failure"
        )
    )

    healthy = MagicMock()

    composite = (
        CompositeTelegramConversationMetrics(
            [
                broken,
                healthy,
            ]
        )
    )

    metric = metric_record()

    result = composite.record_operation(
        metric
    )

    assert result is None

    broken.record_operation\
        .assert_called_once_with(
            metric
        )

    healthy.record_operation\
        .assert_called_once_with(
            metric
        )


def test_empty_composite_is_noop():
    composite = (
        CompositeTelegramConversationMetrics(
            []
        )
    )

    assert composite.record_operation(
        metric_record()
    ) is None


def test_adapter_does_not_copy_exception_messages():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    adapter = (
        ProductiveTelegramConversationMetricsAdapter(
            registry
        )
    )

    external_invalid_record = SimpleNamespace(
        operation="save_session",
        component="bridge",
        outcome="error",
        duration_ms=10.0,
        error_category=(
            "private-financial-message"
        ),
        conflict_recovered=None,
    )

    adapter.record_operation(
        external_invalid_record
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

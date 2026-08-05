from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)
from types import MappingProxyType

import pytest

from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    NoOpTelegramProductiveMetrics,
    SafeTelegramProductiveMetrics,
    TelegramConversationMetricRecord,
    normalize_metric_labels,
)


def labels_to_dict(
    labels,
):
    return dict(labels)


def test_normalizes_registered_labels():
    normalized = normalize_metric_labels(
        metric_name=("inna_telegram_operations_total"),
        labels={
            "component": "WEBHOOK",
            "operation": "PROCESS_UPDATE",
            "outcome": "SUCCESS",
            "error_category": None,
        },
    )

    assert labels_to_dict(normalized) == {
        "component": "webhook",
        "operation": "process_update",
        "outcome": "success",
        "error_category": "none",
    }


def test_unknown_value_is_normalized_when_supported():
    normalized = normalize_metric_labels(
        metric_name=("inna_telegram_operations_total"),
        labels={
            "component": "new-component",
            "operation": "new-operation",
            "outcome": "new-outcome",
            "error_category": "new-error",
        },
    )

    assert labels_to_dict(normalized) == {
        "component": "unknown",
        "operation": "unknown",
        "outcome": "unknown",
        "error_category": "unknown",
    }


@pytest.mark.parametrize(
    "forbidden_label",
    [
        "telegram_user_id",
        "chat_id",
        "update_id",
        "message_text",
        "payload",
        "financial_data",
        "token",
        "exception_message",
        "traceback",
    ],
)
def test_rejects_forbidden_label_names(
    forbidden_label,
):
    with pytest.raises(
        ValueError,
        match="Label proibida",
    ):
        normalize_metric_labels(
            metric_name=("inna_telegram_operations_total"),
            labels={
                "component": "webhook",
                "operation": "process_update",
                "outcome": "success",
                forbidden_label: "private",
            },
        )


def test_rejects_missing_labels():
    with pytest.raises(
        ValueError,
        match="Conjunto de labels inválido",
    ):
        normalize_metric_labels(
            metric_name=("inna_telegram_operations_total"),
            labels={
                "component": "webhook",
                "operation": "process_update",
                "outcome": "success",
            },
        )


def test_rejects_unregistered_metric():
    with pytest.raises(
        ValueError,
        match="Família de métrica",
    ):
        normalize_metric_labels(
            metric_name=("inna_unknown_metric_total"),
            labels={},
        )


def test_counter_accumulates_values():
    metrics = InMemoryTelegramProductiveMetrics()

    labels = {
        "worker_result": "processed",
    }

    metrics.increment(
        "inna_telegram_worker_cycles_total",
        labels=labels,
    )

    metrics.increment(
        "inna_telegram_worker_cycles_total",
        labels=labels,
        value=2,
    )

    snapshot = metrics.snapshot()

    values = snapshot.counters["inna_telegram_worker_cycles_total"]

    assert next(iter(values.values())) == 3.0


def test_counter_rejects_negative_value():
    metrics = InMemoryTelegramProductiveMetrics()

    with pytest.raises(
        ValueError,
        match="não negativo",
    ):
        metrics.increment(
            ("inna_telegram_worker_cycles_total"),
            labels={
                "worker_result": "processed",
            },
            value=-1,
        )


def test_histogram_tracks_count_sum_and_buckets():
    metrics = InMemoryTelegramProductiveMetrics(
        histogram_buckets=(
            0.1,
            0.5,
            1.0,
        )
    )

    labels = {
        "component": "worker",
        "operation": "process_update",
        "outcome": "success",
    }

    metrics.observe(
        ("inna_telegram_operation_duration_seconds"),
        0.25,
        labels=labels,
    )

    metrics.observe(
        ("inna_telegram_operation_duration_seconds"),
        0.75,
        labels=labels,
    )

    snapshot = metrics.snapshot()

    values = snapshot.histograms[("inna_telegram_operation_duration_seconds")]

    histogram = next(iter(values.values()))

    assert histogram.count == 2
    assert histogram.sum == pytest.approx(1.0)

    assert dict(histogram.buckets) == {
        0.1: 0,
        0.5: 1,
        1.0: 2,
    }


def test_record_conversation_operation_exports_core_metrics():
    metrics = InMemoryTelegramProductiveMetrics()

    metrics.record_conversation_operation(
        TelegramConversationMetricRecord(
            operation="save_session",
            component="webhook",
            outcome="success",
            duration_ms=250.0,
            error_category=None,
            conflict_recovered=None,
        )
    )

    snapshot = metrics.snapshot()

    assert "inna_telegram_operations_total" in snapshot.counters

    assert "inna_telegram_operation_duration_seconds" in snapshot.histograms

    histogram = next(
        iter(snapshot.histograms[("inna_telegram_operation_duration_seconds")].values())
    )

    assert histogram.sum == pytest.approx(0.25)


def test_record_error_increments_failure_counter():
    metrics = InMemoryTelegramProductiveMetrics()

    metrics.record_conversation_operation(
        TelegramConversationMetricRecord(
            operation="save_session",
            component="bridge",
            outcome="error",
            duration_ms=10.0,
            error_category="persistence",
            conflict_recovered=None,
        )
    )

    snapshot = metrics.snapshot()

    assert "inna_telegram_failures_total" in snapshot.counters


def test_record_conflict_increments_conflict_counter():
    metrics = InMemoryTelegramProductiveMetrics()

    metrics.record_conversation_operation(
        TelegramConversationMetricRecord(
            operation="save_session",
            component="webhook",
            outcome="recovered",
            duration_ms=25.0,
            error_category=("optimistic_conflict"),
            conflict_recovered=True,
        )
    )

    snapshot = metrics.snapshot()

    assert "inna_telegram_conflicts_total" in snapshot.counters


def test_snapshot_is_immutable():
    metrics = InMemoryTelegramProductiveMetrics()

    metrics.increment(
        "inna_telegram_worker_cycles_total",
        labels={
            "worker_result": "processed",
        },
    )

    snapshot = metrics.snapshot()

    assert isinstance(
        snapshot.counters,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        snapshot.counters["new"] = {}


def test_reset_clears_all_metrics():
    metrics = InMemoryTelegramProductiveMetrics()

    metrics.increment(
        "inna_telegram_worker_cycles_total",
        labels={
            "worker_result": "processed",
        },
    )

    metrics.reset()

    snapshot = metrics.snapshot()

    assert dict(snapshot.counters) == {}

    assert dict(snapshot.histograms) == {}


def test_noop_accepts_operations():
    metrics = NoOpTelegramProductiveMetrics()

    metrics.increment(
        "anything",
        labels={
            "anything": "anything",
        },
    )

    metrics.observe(
        "anything",
        1.0,
        labels={
            "anything": "anything",
        },
    )


def test_safe_wrapper_swallows_delegate_failures():
    class BrokenMetrics:
        def increment(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError("private error")

        def observe(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError("private error")

    metrics = SafeTelegramProductiveMetrics(BrokenMetrics())

    assert (
        metrics.increment(
            "anything",
            labels={},
        )
        is None
    )

    assert (
        metrics.observe(
            "anything",
            1.0,
            labels={},
        )
        is None
    )


def test_registry_is_thread_safe():
    metrics = InMemoryTelegramProductiveMetrics()

    def increment_many():
        for _ in range(500):
            metrics.increment(
                ("inna_telegram_worker_cycles_total"),
                labels={
                    "worker_result": "processed",
                },
            )

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(increment_many) for _ in range(8)]

        for future in futures:
            future.result()

    snapshot = metrics.snapshot()

    values = snapshot.counters["inna_telegram_worker_cycles_total"]

    assert next(iter(values.values())) == 4000.0

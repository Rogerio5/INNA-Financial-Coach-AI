from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    TelegramPrometheusMetricsExporter,
)
from src.services.telegram_observability.productive_operations import (
    TelegramProductiveOperationsRecorder,
)


BINDINGS_PATH = Path(
    "docs/audits/"
    "telegram_prometheus_semantic_bindings.json"
)

LABELS_PATH = Path(
    "docs/audits/"
    "telegram_prometheus_label_bindings.json"
)


def load_json(
    path: Path,
) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def export_worker_update(
    *,
    outcome: str,
    error_category: str | None,
) -> str:
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    operations.record_worker_cycle(
        result=(
            "failed"
            if outcome == "error"
            else "processed"
        )
    )

    operations.record_worker_update(
        outcome=outcome,
        error_category=error_category,
    )

    return (
        TelegramPrometheusMetricsExporter()
        .export(
            registry.snapshot()
        )
        .body
    )


def export_queue_conflict() -> str:
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    operations.record_queue_operation(
        operation="claim",
        outcome="conflict",
        error_category=(
            "optimistic_conflict"
        ),
    )

    return (
        TelegramPrometheusMetricsExporter()
        .export(
            registry.snapshot()
        )
        .body
    )


def export_receipt_failure() -> str:
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    operations.record_receipt(
        status="failed",
        outcome="error",
        error_category="persistence",
    )

    return (
        TelegramPrometheusMetricsExporter()
        .export(
            registry.snapshot()
        )
        .body
    )


def test_audit_files_exist():
    assert BINDINGS_PATH.is_file()
    assert LABELS_PATH.is_file()


def test_required_semantic_bindings_are_resolved():
    bindings = load_json(
        BINDINGS_PATH
    )["bindings"]

    unresolved = {
        name: binding["status"]
        for name, binding in (
            bindings.items()
        )
        if (
            binding["required"]
            and binding["status"]
            != "resolved"
        )
    }

    assert not unresolved


@pytest.mark.parametrize(
    (
        "semantic_name",
        "metric_name",
    ),
    [
        (
            "operation_total",
            "inna_telegram_operations_total",
        ),
        (
            "duration_histogram",
            (
                "inna_telegram_"
                "operation_duration_seconds"
            ),
        ),
        (
            "error_total",
            "inna_telegram_failures_total",
        ),
    ],
)
def test_core_metric_binding(
    semantic_name,
    metric_name,
):
    bindings = load_json(
        BINDINGS_PATH
    )["bindings"]

    assert (
        bindings[
            semantic_name
        ]["selected_metric"]
        == metric_name
    )


@pytest.mark.parametrize(
    "semantic_name",
    [
        "retry_total",
        "dead_letter_total",
        "backlog",
        "freshness_timestamp",
    ],
)
def test_absent_optional_metrics_are_not_invented(
    semantic_name,
):
    binding = load_json(
        BINDINGS_PATH
    )["bindings"][
        semantic_name
    ]

    if binding["status"] == "missing":
        assert (
            binding["selected_metric"]
            is None
        )


def test_low_cardinality_labels_are_mapped():
    labels = set(
        load_json(
            LABELS_PATH
        )["labels"]
    )

    assert {
        "component",
        "operation",
        "outcome",
        "error_category",
        "le",
    }.issubset(
        labels
    )


def test_private_labels_are_not_mapped():
    labels = {
        value.lower()
        for value in load_json(
            LABELS_PATH
        )["labels"]
    }

    forbidden = {
        "chat_id",
        "telegram_user_id",
        "user_id",
        "update_id",
        "claim_token",
        "payload",
        "email",
        "username",
        "message",
    }

    assert labels.isdisjoint(
        forbidden
    )


def test_worker_failure_series_semantics():
    body = export_worker_update(
        outcome="error",
        error_category="persistence",
    )

    assert (
        "inna_telegram_worker_cycles_total"
        in body
    )

    assert (
        "inna_telegram_worker_updates_total"
        in body
    )

    assert (
        "inna_telegram_failures_total"
        in body
    )

    assert 'worker_result="failed"' in body
    assert 'outcome="error"' in body

    assert (
        'error_category="persistence"'
        in body
    )

    assert 'component="worker"' in body

    assert (
        'operation="process_update"'
        in body
    )


def test_queue_conflict_series_semantics():
    body = export_queue_conflict()

    assert (
        "inna_telegram_queue_operations_total"
        in body
    )

    assert (
        "inna_telegram_failures_total"
        in body
    )

    assert 'queue_operation="claim"' in body
    assert 'outcome="conflict"' in body

    assert (
        'error_category="optimistic_conflict"'
        in body
    )

    assert 'component="queue"' in body

    assert (
        'operation="dequeue_update"'
        in body
    )


def test_receipt_failure_series_semantics():
    body = export_receipt_failure()

    assert (
        "inna_telegram_receipts_total"
        in body
    )

    assert (
        "inna_telegram_failures_total"
        in body
    )

    assert 'receipt_status="failed"' in body
    assert 'outcome="error"' in body

    assert (
        'error_category="persistence"'
        in body
    )

    assert 'component="receipt"' in body

    assert (
        'operation="fail_receipt"'
        in body
    )


def test_exports_do_not_contain_private_identifiers():
    body = "\n".join(
        [
            export_worker_update(
                outcome="error",
                error_category="persistence",
            ),
            export_queue_conflict(),
            export_receipt_failure(),
        ]
    ).lower()

    forbidden = {
        "chat_id",
        "telegram_user_id",
        "user_id",
        "update_id",
        "claim_token",
        "payload",
        "email",
        "username",
    }

    for value in forbidden:
        assert value not in body

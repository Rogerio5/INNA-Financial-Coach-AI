from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.channels import (
    telegram_update_worker as entrypoint,
)
from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    TelegramProductiveOperationsRecorder,
)


def result(
    *,
    decision,
    stage,
    update_id=1,
    job_status=None,
    error_code=None,
    idempotent_replay=False,
):
    return SimpleNamespace(
        decision=decision,
        stage=stage,
        update_id=update_id,
        job_status=job_status,
        error_code=error_code,
        idempotent_replay=idempotent_replay,
    )


def series_labels(
    snapshot,
    metric_name,
):
    return [dict(labels) for labels in snapshot.counters[metric_name]]


@pytest.mark.parametrize(
    (
        "decision",
        "stage",
        "queue_operation",
    ),
    [
        (
            "completed",
            "complete",
            "acknowledge",
        ),
        (
            "retry_scheduled",
            "failure",
            "release",
        ),
        (
            "dead_lettered",
            "failure",
            "fail",
        ),
    ],
)
def test_idempotent_replay_maps_to_duplicate(
    decision,
    stage,
    queue_operation,
):
    replay = result(
        decision=decision,
        stage=stage,
        idempotent_replay=True,
    )

    assert entrypoint._productive_update_outcome_for_runner_result(replay) == (
        "duplicate",
        None,
    )

    assert entrypoint._productive_receipt_for_runner_result(replay) == (
        "duplicate",
        "duplicate",
        None,
    )

    queue = entrypoint._productive_queue_for_runner_result(replay)

    assert queue == (
        queue_operation,
        "duplicate",
        None,
    )


def test_recovery_does_not_create_receipt():
    recovery = result(
        decision="unavailable",
        stage="recovery",
        update_id=None,
        error_code=("telegram.recovery_unavailable"),
    )

    assert entrypoint._productive_receipt_for_runner_result(recovery) is None


def test_recovery_creates_only_cycle_and_queue():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    recovery = result(
        decision="unavailable",
        stage="recovery",
        update_id=None,
        error_code=("telegram.recovery_unavailable"),
    )

    entrypoint.record_productive_runner_result(
        recovery,
        operations=operations,
    )

    entrypoint.record_productive_receipt_and_queue_result(
        recovery,
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert "inna_telegram_worker_cycles_total" in snapshot.counters

    assert "inna_telegram_worker_updates_total" not in snapshot.counters

    assert "inna_telegram_receipts_total" not in snapshot.counters

    assert "inna_telegram_queue_operations_total" in snapshot.counters

    queue_labels = series_labels(
        snapshot,
        "inna_telegram_queue_operations_total",
    )

    assert queue_labels == [
        {
            "queue_operation": "recover",
            "outcome": "error",
            "error_category": "dependency",
        }
    ]


def test_replay_records_one_series_per_family():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    replay = result(
        decision="completed",
        stage="complete",
        job_status="completed",
        idempotent_replay=True,
    )

    entrypoint.record_productive_runner_result(
        replay,
        operations=operations,
    )

    entrypoint.record_productive_receipt_and_queue_result(
        replay,
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert len(snapshot.counters["inna_telegram_worker_cycles_total"]) == 1

    assert len(snapshot.counters["inna_telegram_worker_updates_total"]) == 1

    assert len(snapshot.counters["inna_telegram_receipts_total"]) == 1

    assert len(snapshot.counters["inna_telegram_queue_operations_total"]) == 1

    update_labels = series_labels(
        snapshot,
        "inna_telegram_worker_updates_total",
    )

    assert update_labels == [
        {
            "outcome": "duplicate",
            "error_category": "none",
        }
    ]


def test_callback_records_each_family_once(
    monkeypatch,
):
    operations = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "emit_runner_result",
        MagicMock(),
    )

    replay = result(
        decision="completed",
        stage="complete",
        idempotent_replay=True,
    )

    entrypoint.handle_productive_runner_result(
        replay,
        stream=MagicMock(),
        operations=operations,
    )

    operations.record_worker_cycle.assert_called_once_with(
        result="processed",
    )

    operations.record_worker_update.assert_called_once_with(
        outcome="duplicate",
        error_category=None,
    )

    operations.record_receipt.assert_called_once_with(
        status="duplicate",
        outcome="duplicate",
        error_category=None,
    )

    operations.record_queue_operation.assert_called_once_with(
        operation="acknowledge",
        outcome="duplicate",
        error_category=None,
    )


def test_two_callback_invocations_count_two_events():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    original = result(
        decision="completed",
        stage="complete",
        idempotent_replay=False,
    )

    replay = result(
        decision="completed",
        stage="complete",
        idempotent_replay=True,
    )

    for runner_result in (
        original,
        replay,
    ):
        entrypoint.record_productive_runner_result(
            runner_result,
            operations=operations,
        )

        entrypoint.record_productive_receipt_and_queue_result(
            runner_result,
            operations=operations,
        )

    snapshot = registry.snapshot()

    assert sum(snapshot.counters["inna_telegram_worker_cycles_total"].values()) == 2.0

    assert sum(snapshot.counters["inna_telegram_worker_updates_total"].values()) == 2.0

    assert sum(snapshot.counters["inna_telegram_receipts_total"].values()) == 2.0

    assert (
        sum(snapshot.counters["inna_telegram_queue_operations_total"].values()) == 2.0
    )

    update_series = snapshot.counters["inna_telegram_worker_updates_total"]

    assert len(update_series) == 2

    outcomes = {dict(labels)["outcome"] for labels in update_series}

    assert outcomes == {
        "success",
        "duplicate",
    }

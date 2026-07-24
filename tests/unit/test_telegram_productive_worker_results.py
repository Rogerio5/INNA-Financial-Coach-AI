from __future__ import annotations

import io
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


def runner_result(
    *,
    decision,
    stage="process",
    error_code=None,
):
    return SimpleNamespace(
        decision=decision,
        stage=stage,
        error_code=error_code,
        to_safe_dict=lambda: {
            "decision": decision,
            "stage": stage,
        },
    )


@pytest.mark.parametrize(
    (
        "decision",
        "expected",
    ),
    [
        ("idle", "empty"),
        ("completed", "processed"),
        ("retry_scheduled", "processed"),
        ("dead_lettered", "processed"),
        ("ownership_lost", "failed"),
        ("unavailable", "failed"),
        ("consistency_error", "failed"),
        ("future-value", "unknown"),
    ],
)
def test_classifies_worker_cycle(
    decision,
    expected,
):
    result = runner_result(
        decision=decision,
    )

    assert (
        entrypoint
        ._productive_cycle_result_for_runner_result(
            result
        )
        == expected
    )


def test_idle_records_cycle_but_not_update():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    entrypoint.record_productive_runner_result(
        runner_result(
            decision="idle",
            stage="idle",
        ),
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_worker_cycles_total"
        in snapshot.counters
    )

    assert (
        "inna_telegram_worker_updates_total"
        not in snapshot.counters
    )


def test_completed_records_successful_update():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    entrypoint.record_productive_runner_result(
        runner_result(
            decision="completed",
            stage="complete",
        ),
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert sum(
        snapshot.counters[
            "inna_telegram_worker_cycles_total"
        ].values()
    ) == 1.0

    assert sum(
        snapshot.counters[
            "inna_telegram_worker_updates_total"
        ].values()
    ) == 1.0

    series = snapshot.counters[
        "inna_telegram_worker_updates_total"
    ]

    labels = dict(
        next(
            iter(series)
        )
    )

    assert labels == {
        "outcome": "success",
        "error_category": "none",
    }


def test_unavailable_records_failure():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    entrypoint.record_productive_runner_result(
        runner_result(
            decision="unavailable",
            stage="claim",
            error_code=(
                "telegram.claim_unavailable"
            ),
        ),
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_worker_updates_total"
        in snapshot.counters
    )

    assert (
        "inna_telegram_failures_total"
        in snapshot.counters
    )

    rendered = repr(
        snapshot
    )

    assert "dependency" in rendered


def test_consistency_error_maps_to_persistence():
    result = runner_result(
        decision="consistency_error",
        stage="complete",
        error_code=(
            "telegram.completion_inconsistent"
        ),
    )

    assert (
        entrypoint
        ._productive_error_category_for_result(
            result
        )
        == "persistence"
    )


def test_keyring_error_maps_to_encryption():
    result = runner_result(
        decision="retry_scheduled",
        stage="decrypt",
        error_code=(
            "telegram.keyring_unavailable"
        ),
    )

    assert (
        entrypoint
        ._productive_error_category_for_result(
            result
        )
        == "dependency"
    )


def test_recovery_result_does_not_count_update():
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    entrypoint.record_productive_runner_result(
        runner_result(
            decision="unavailable",
            stage="recovery",
            error_code=(
                "telegram.recovery_unavailable"
            ),
        ),
        operations=operations,
    )

    snapshot = registry.snapshot()

    assert (
        "inna_telegram_worker_cycles_total"
        in snapshot.counters
    )

    assert (
        "inna_telegram_worker_updates_total"
        not in snapshot.counters
    )


def test_callback_emits_log_and_metrics(
    monkeypatch,
):
    stream = io.StringIO()
    operations = MagicMock()

    emitted = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "emit_runner_result",
        emitted,
    )

    result = runner_result(
        decision="completed",
        stage="complete",
    )

    entrypoint.handle_productive_runner_result(
        result,
        stream=stream,
        operations=operations,
    )

    emitted.assert_called_once_with(
        result,
        stream=stream,
    )

    operations.record_worker_cycle\
        .assert_called_once_with(
            result="processed",
        )

    operations.record_worker_update\
        .assert_called_once_with(
            outcome="success",
            error_category=None,
        )


def test_callback_isolates_logging_failure(
    monkeypatch,
):
    operations = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "emit_runner_result",
        MagicMock(
            side_effect=RuntimeError(
                "private-log-error"
            )
        ),
    )

    result = runner_result(
        decision="completed",
    )

    assert (
        entrypoint
        .handle_productive_runner_result(
            result,
            stream=io.StringIO(),
            operations=operations,
        )
        is None
    )

    operations.record_worker_cycle\
        .assert_called_once()


def test_callback_isolates_metrics_failure(
    monkeypatch,
):
    emitted = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "emit_runner_result",
        emitted,
    )

    operations = MagicMock()

    operations.record_worker_cycle.side_effect = (
        RuntimeError(
            "private-metrics-error"
        )
    )

    result = runner_result(
        decision="completed",
    )

    assert (
        entrypoint
        .handle_productive_runner_result(
            result,
            stream=io.StringIO(),
            operations=operations,
        )
        is None
    )

    emitted.assert_called_once()

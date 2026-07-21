from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from src.channels import (
    telegram_update_worker as entrypoint,
)
from src.services.telegram_observability import (
    InMemoryTelegramProductiveMetrics,
    TelegramProductiveOperationsRecorder,
)


@dataclass(frozen=True)
class ExpectedTotals:
    cycles: float
    updates: float
    receipts: float
    queue: float


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


def counter_total(
    snapshot,
    metric_name,
):
    values = snapshot.counters.get(
        metric_name,
        {},
    )

    return sum(
        values.values()
    )


@pytest.mark.parametrize(
    (
        "runner_result",
        "expected",
    ),
    [
        (
            result(
                decision="idle",
                stage="idle",
                update_id=None,
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=0.0,
                receipts=0.0,
                queue=0.0,
            ),
        ),
        (
            result(
                decision="completed",
                stage="complete",
                job_status="completed",
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="completed",
                stage="complete",
                job_status="completed",
                idempotent_replay=True,
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="retry_scheduled",
                stage="failure",
                job_status="queued",
                error_code=(
                    "telegram.processing_failed"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="dead_lettered",
                stage="failure",
                job_status="dead_letter",
                error_code=(
                    "telegram.processing_failed"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="ownership_lost",
                stage="complete",
                error_code=(
                    "telegram.completion_ownership_lost"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="unavailable",
                stage="claim",
                update_id=None,
                error_code=(
                    "telegram.claim_unavailable"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="consistency_error",
                stage="claim",
                update_id=None,
                error_code=(
                    "telegram.claim_inconsistent"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=1.0,
                receipts=1.0,
                queue=1.0,
            ),
        ),
        (
            result(
                decision="unavailable",
                stage="recovery",
                update_id=None,
                error_code=(
                    "telegram.recovery_unavailable"
                ),
            ),
            ExpectedTotals(
                cycles=1.0,
                updates=0.0,
                receipts=0.0,
                queue=1.0,
            ),
        ),
    ],
)
def test_each_callback_has_expected_counts(
    runner_result,
    expected,
):
    registry = (
        InMemoryTelegramProductiveMetrics()
    )

    operations = (
        TelegramProductiveOperationsRecorder(
            registry
        )
    )

    entrypoint.record_productive_runner_result(
        runner_result,
        operations=operations,
    )

    entrypoint\
        .record_productive_receipt_and_queue_result(
            runner_result,
            operations=operations,
        )

    snapshot = registry.snapshot()

    assert counter_total(
        snapshot,
        "inna_telegram_worker_cycles_total",
    ) == expected.cycles

    assert counter_total(
        snapshot,
        "inna_telegram_worker_updates_total",
    ) == expected.updates

    assert counter_total(
        snapshot,
        "inna_telegram_receipts_total",
    ) == expected.receipts

    assert counter_total(
        snapshot,
        "inna_telegram_queue_operations_total",
    ) == expected.queue


def test_callback_does_not_call_same_method_twice(
    monkeypatch,
):
    operations = SimpleNamespace(
        record_worker_cycle=(
            __import__(
                "unittest.mock"
            ).mock.MagicMock()
        ),
        record_worker_update=(
            __import__(
                "unittest.mock"
            ).mock.MagicMock()
        ),
        record_receipt=(
            __import__(
                "unittest.mock"
            ).mock.MagicMock()
        ),
        record_queue_operation=(
            __import__(
                "unittest.mock"
            ).mock.MagicMock()
        ),
    )

    monkeypatch.setattr(
        entrypoint,
        "emit_runner_result",
        lambda *args, **kwargs: None,
    )

    entrypoint.handle_productive_runner_result(
        result(
            decision="completed",
            stage="complete",
            job_status="completed",
        ),
        stream=SimpleNamespace(),
        operations=operations,
    )

    assert (
        operations
        .record_worker_cycle
        .call_count
        == 1
    )

    assert (
        operations
        .record_worker_update
        .call_count
        == 1
    )

    assert (
        operations
        .record_receipt
        .call_count
        == 1
    )

    assert (
        operations
        .record_queue_operation
        .call_count
        == 1
    )

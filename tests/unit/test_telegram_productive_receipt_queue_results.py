from __future__ import annotations

from types import SimpleNamespace

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
    update_id=123,
    error_code=None,
    job_status=None,
    idempotent_replay=False,
):
    return SimpleNamespace(
        decision=decision,
        stage=stage,
        update_id=update_id,
        error_code=error_code,
        job_status=job_status,
        idempotent_replay=idempotent_replay,
    )


@pytest.mark.parametrize(
    (
        "runner_result",
        "expected",
    ),
    [
        (
            result(
                decision="completed",
                stage="complete",
                job_status="completed",
            ),
            (
                "completed",
                "success",
                None,
            ),
        ),
        (
            result(
                decision="retry_scheduled",
                stage="failure",
                job_status="queued",
                error_code="telegram.process_failed",
            ),
            (
                "failed",
                "error",
                "unknown",
            ),
        ),
        (
            result(
                decision="dead_lettered",
                stage="failure",
                job_status="dead_letter",
                error_code="telegram.process_failed",
            ),
            (
                "failed",
                "error",
                "unknown",
            ),
        ),
        (
            result(
                decision="ownership_lost",
                stage="complete",
                error_code=("telegram.completion_ownership_lost"),
            ),
            (
                "released",
                "conflict",
                "optimistic_conflict",
            ),
        ),
        (
            result(
                decision="consistency_error",
                stage="claim",
                update_id=None,
                error_code=("telegram.claim_inconsistent"),
            ),
            (
                "claimed",
                "conflict",
                "persistence",
            ),
        ),
    ],
)
def test_receipt_mapping(
    runner_result,
    expected,
):
    assert entrypoint._productive_receipt_for_runner_result(runner_result) == expected


@pytest.mark.parametrize(
    (
        "runner_result",
        "expected_operation",
        "expected_outcome",
    ),
    [
        (
            result(
                decision="completed",
                stage="complete",
            ),
            "acknowledge",
            "success",
        ),
        (
            result(
                decision="retry_scheduled",
                stage="failure",
            ),
            "release",
            "success",
        ),
        (
            result(
                decision="dead_lettered",
                stage="failure",
            ),
            "fail",
            "success",
        ),
        (
            result(
                decision="ownership_lost",
                stage="complete",
                error_code=("telegram.completion_ownership_lost"),
            ),
            "release",
            "conflict",
        ),
        (
            result(
                decision="unavailable",
                stage="recovery",
                update_id=None,
                error_code=("telegram.recovery_unavailable"),
            ),
            "recover",
            "error",
        ),
        (
            result(
                decision="unavailable",
                stage="claim",
                update_id=None,
                error_code=("telegram.claim_unavailable"),
            ),
            "claim",
            "error",
        ),
    ],
)
def test_queue_mapping(
    runner_result,
    expected_operation,
    expected_outcome,
):
    mapped = entrypoint._productive_queue_for_runner_result(runner_result)

    assert mapped is not None

    operation, outcome, _ = mapped

    assert operation == (expected_operation)

    assert outcome == (expected_outcome)


def test_idle_does_not_record_receipt_or_queue():
    idle = result(
        decision="idle",
        stage="idle",
        update_id=None,
    )

    assert entrypoint._productive_receipt_for_runner_result(idle) is None

    assert entrypoint._productive_queue_for_runner_result(idle) is None


def test_records_receipt_and_queue_once():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    runner_result = result(
        decision="completed",
        stage="complete",
        job_status="completed",
    )

    entrypoint.record_productive_receipt_and_queue_result(
        runner_result,
        operations=operations,
    )

    snapshot = registry.snapshot()

    receipt_total = sum(snapshot.counters["inna_telegram_receipts_total"].values())

    queue_total = sum(
        snapshot.counters[("inna_telegram_queue_operations_total")].values()
    )

    assert receipt_total == 1.0
    assert queue_total == 1.0


def test_dynamic_error_code_is_not_exported():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    runner_result = result(
        decision="unavailable",
        stage="failure",
        error_code=("private-user-financial-data"),
    )

    entrypoint.record_productive_receipt_and_queue_result(
        runner_result,
        operations=operations,
    )

    rendered = repr(registry.snapshot())

    assert "private-user-financial-data" not in rendered

    assert "unknown" in rendered


def test_idempotent_replay_has_bounded_series():
    registry = InMemoryTelegramProductiveMetrics()

    operations = TelegramProductiveOperationsRecorder(registry)

    for replay in (
        False,
        True,
    ):
        entrypoint.record_productive_receipt_and_queue_result(
            result(
                decision="completed",
                stage="complete",
                idempotent_replay=replay,
            ),
            operations=operations,
        )

    snapshot = registry.snapshot()

    receipts = snapshot.counters["inna_telegram_receipts_total"]

    queue = snapshot.counters[("inna_telegram_queue_operations_total")]

    assert len(receipts) == 2
    assert len(queue) == 2

    assert sum(receipts.values()) == 2.0

    assert sum(queue.values()) == 2.0

    receipt_outcomes = {dict(labels)["outcome"] for labels in receipts}

    queue_outcomes = {dict(labels)["outcome"] for labels in queue}

    assert receipt_outcomes == {
        "success",
        "duplicate",
    }

    assert queue_outcomes == {
        "success",
        "duplicate",
    }

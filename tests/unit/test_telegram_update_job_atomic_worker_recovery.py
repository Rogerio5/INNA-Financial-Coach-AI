from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.services.telegram_update_jobs import (
    worker,
)

from src.services.telegram_update_jobs import (
    repository as job_repository,
)


def recovery_record(
    *,
    update_id=94001,
    status="queued",
    attempt_count=2,
    max_attempts=5,
    receipt_attempt_count=2,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "receipt_attempt_count": (receipt_attempt_count),
        "payload_version": 1,
        "last_error_code": (worker.RECOVERY_ERROR_CODE),
        "payload_retained": True,
        "ownership_cleared": True,
        "completed_at_cleared": True,
        "failed_at_set": True,
        "lease_closed": True,
    }


def summary_row(
    records,
    *,
    candidate_count=None,
    job_count=None,
    receipt_count=None,
):
    total = len(records)

    return {
        "records": records,
        "candidate_count": (total if candidate_count is None else candidate_count),
        "job_count": (total if job_count is None else job_count),
        "receipt_count": (total if receipt_count is None else receipt_count),
    }


class FakeCursor:
    def __init__(
        self,
        row,
    ):
        self.row = row
        self.executions = []

    def execute(
        self,
        sql,
        parameters=None,
    ):
        self.executions.append(
            (
                sql,
                parameters,
            )
        )

    def fetchone(self):
        return self.row


class Tracker:
    def __init__(self):
        self.committed = 0
        self.rolled_back = 0


def install_cursor(
    monkeypatch,
    row,
):
    cursor = FakeCursor(row)
    tracker = Tracker()

    @contextmanager
    def fake_cursor_postgres(
        *,
        dict_cursor,
        commit_automatico,
    ):
        assert dict_cursor is True
        assert commit_automatico is True

        try:
            yield cursor

        except Exception:
            tracker.rolled_back += 1
            raise

        else:
            tracker.committed += 1

    monkeypatch.setattr(
        worker,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    return cursor, tracker


def test_recovers_retry_and_dead_letter(
    monkeypatch,
):
    rows = [
        recovery_record(),
        recovery_record(
            update_id=94002,
            status="dead_letter",
            attempt_count=5,
            max_attempts=5,
            receipt_attempt_count=5,
        ),
    ]

    _, tracker = install_cursor(
        monkeypatch,
        summary_row(rows),
    )

    batch = worker.recover_expired_authenticated_telegram_update_jobs_atomic(limit=50)

    assert batch.total == 2
    assert batch.retried == 1
    assert batch.dead_lettered == 1

    assert tracker.committed == 1
    assert tracker.rolled_back == 0


def test_empty_recovery_is_valid(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        summary_row([]),
    )

    batch = worker.recover_expired_authenticated_telegram_update_jobs_atomic()

    assert batch.total == 0
    assert batch.records == ()


def test_limit_is_forwarded(
    monkeypatch,
):
    cursor, _ = install_cursor(
        monkeypatch,
        summary_row([]),
    )

    (worker.recover_expired_authenticated_telegram_update_jobs_atomic(limit=25))

    business = [
        item for item in cursor.executions if not str(item[0]).startswith("SET LOCAL")
    ]

    assert business[0][1]["limit"] == 25


def test_mismatched_counts_roll_back(
    monkeypatch,
):
    _, tracker = install_cursor(
        monkeypatch,
        summary_row(
            [recovery_record()],
            candidate_count=1,
            job_count=1,
            receipt_count=0,
        ),
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())

    assert tracker.rolled_back == 1


def test_record_count_mismatch_rolls_back(
    monkeypatch,
):
    _, tracker = install_cursor(
        monkeypatch,
        summary_row(
            [],
            candidate_count=1,
            job_count=1,
            receipt_count=1,
        ),
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())

    assert tracker.rolled_back == 1


@pytest.mark.parametrize(
    "field_name",
    [
        "payload_retained",
        "ownership_cleared",
        "completed_at_cleared",
        "failed_at_set",
        "lease_closed",
    ],
)
def test_incomplete_recovery_is_rejected(
    monkeypatch,
    field_name,
):
    row = recovery_record()
    row[field_name] = False

    _, tracker = install_cursor(
        monkeypatch,
        summary_row([row]),
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())

    assert tracker.rolled_back == 1


def test_receipt_attempt_cannot_trail_job(
    monkeypatch,
):
    row = recovery_record(
        attempt_count=3,
        receipt_attempt_count=2,
    )

    install_cursor(
        monkeypatch,
        summary_row([row]),
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())


def test_invalid_error_code_is_rejected(
    monkeypatch,
):
    row = recovery_record()

    row["last_error_code"] = "telegram.other_error"

    install_cursor(
        monkeypatch,
        summary_row([row]),
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(**_kwargs):
        raise RuntimeError("postgresql://user:secret@host/database")

        yield

    monkeypatch.setattr(
        worker,
        "cursor_postgres",
        failing_cursor,
    )

    with pytest.raises(worker.TelegramUpdateWorkerUnavailableError) as captured:
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic())

    assert "secret" not in str(captured.value)


def test_maximum_recovery_limit_is_accepted(
    monkeypatch,
):
    cursor, tracker = install_cursor(
        monkeypatch,
        summary_row([]),
    )

    batch = worker.recover_expired_authenticated_telegram_update_jobs_atomic(
        limit=(job_repository.MAX_RECOVERY_BATCH)
    )

    assert batch.total == 0
    assert tracker.committed == 1
    assert tracker.rolled_back == 0

    business = [
        item for item in cursor.executions if not str(item[0]).startswith("SET LOCAL")
    ]

    assert len(business) == 1

    assert business[0][1]["limit"] == job_repository.MAX_RECOVERY_BATCH


@pytest.mark.parametrize(
    "value",
    [
        0,
        job_repository.MAX_RECOVERY_BATCH + 1,
        True,
        "10",
    ],
)
def test_invalid_limit_is_rejected(
    value,
):
    with pytest.raises(worker.TelegramUpdateWorkerValidationError):
        (worker.recover_expired_authenticated_telegram_update_jobs_atomic(limit=value))


def test_sql_locks_receipt_first():
    sql = worker.SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS

    assert "FOR UPDATE OF receipt SKIP LOCKED" in sql


def test_sql_updates_job_and_receipt():
    sql = worker.SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS

    assert "UPDATE public.telegram_update_jobs" in sql

    assert "public.telegram_update_receipts" in sql

    assert "receipt.claim_token =" in sql

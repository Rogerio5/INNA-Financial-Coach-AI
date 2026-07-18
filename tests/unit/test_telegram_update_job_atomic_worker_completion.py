from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace

import pytest

from src.services.telegram_update_jobs import (
    worker,
)


UPDATE_ID = 92001
LOCK_TOKEN = "a" * 64
OTHER_TOKEN = "b" * 64

CIPHERTEXT = b"c" * 32
NONCE = b"n" * 12
KEY_ID = "inna.telegram.v1"


def make_lease():
    return worker.TelegramUpdateWorkerLease(
        update_id=UPDATE_ID,
        job_status="processing",
        receipt_status="processing",
        job_attempt_count=2,
        job_max_attempts=5,
        receipt_attempt_count=2,
        payload_version=1,
        payload_key_id=KEY_ID,
        payload_ciphertext=CIPHERTEXT,
        payload_nonce=NONCE,
        lock_token=LOCK_TOKEN,
    )


def locked_receipt_row(
    *,
    update_id=UPDATE_ID,
    status="processing",
    attempt_count=2,
    claim_token=LOCK_TOKEN,
    lease_active=True,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "claim_token": claim_token,
        "lease_active": lease_active,
    }


def completed_job_row(
    *,
    update_id=UPDATE_ID,
    status="completed",
    attempt_count=2,
    max_attempts=5,
    payload_version=1,
    payload_cleared=True,
    ownership_cleared=True,
    completed_at_set=True,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "payload_version": payload_version,
        "payload_cleared": payload_cleared,
        "ownership_cleared": (
            ownership_cleared
        ),
        "completed_at_set": (
            completed_at_set
        ),
    }


def completed_receipt_row(
    *,
    update_id=UPDATE_ID,
    status="completed",
    attempt_count=2,
    completed_at_set=True,
    lease_closed=True,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "completed_at_set": (
            completed_at_set
        ),
        "lease_closed": lease_closed,
    }


class FakeCursor:
    def __init__(
        self,
        rows,
    ):
        self.rows = list(
            rows
        )

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

    def fetchone(
        self,
    ):
        if not self.rows:
            return None

        return self.rows.pop(
            0
        )


class TransactionTracker:
    def __init__(
        self,
    ):
        self.entered = 0
        self.committed = 0
        self.rolled_back = 0


def install_transaction(
    monkeypatch,
    rows,
):
    cursor = FakeCursor(
        rows
    )

    tracker = TransactionTracker()

    @contextmanager
    def fake_cursor_postgres(
        *,
        dict_cursor,
        commit_automatico,
    ):
        assert dict_cursor is True
        assert commit_automatico is True

        tracker.entered += 1

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


def complete(
    monkeypatch,
    rows,
    *,
    lease=None,
):
    cursor, tracker = (
        install_transaction(
            monkeypatch,
            rows,
        )
    )

    outcome = (
        worker
        .complete_authenticated_telegram_update_job_atomic(
            lease=(
                lease
                if lease is not None
                else make_lease()
            )
        )
    )

    return outcome, cursor, tracker


def business_executions(
    cursor,
):
    return [
        (
            str(sql),
            parameters,
        )
        for sql, parameters
        in cursor.executions
        if not str(sql).startswith(
            "SET LOCAL"
        )
    ]


def test_completes_job_and_receipt_atomically(
    monkeypatch,
):
    outcome, _, tracker = complete(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            completed_receipt_row(),
        ],
    )

    assert outcome.decision == "completed"
    assert outcome.completed is True

    assert outcome.job_status == "completed"

    assert (
        outcome.receipt_status
        == "completed"
    )

    assert outcome.payload_cleared is True
    assert outcome.ownership_cleared is True

    assert tracker.entered == 1
    assert tracker.committed == 1
    assert tracker.rolled_back == 0


def test_receipt_is_locked_before_job_update(
    monkeypatch,
):
    _, cursor, _ = complete(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            completed_receipt_row(),
        ],
    )

    executions = business_executions(
        cursor
    )

    assert len(executions) == 3

    assert (
        "FOR UPDATE"
        in executions[0][0]
    )

    assert (
        "UPDATE public.telegram_update_jobs"
        in executions[1][0]
    )

    assert (
        "UPDATE public.telegram_update_receipts"
        in executions[2][0]
    )


def test_same_token_is_used_for_both_updates(
    monkeypatch,
):
    _, cursor, _ = complete(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            completed_receipt_row(),
        ],
    )

    executions = business_executions(
        cursor
    )

    assert (
        executions[1][1]["lock_token"]
        == LOCK_TOKEN
    )

    assert (
        executions[2][1]["lock_token"]
        == LOCK_TOKEN
    )


def test_payload_and_ownership_are_cleared():
    sql = (
        worker.SQL_COMPLETE_OWNED_JOB
    )

    assert "payload_ciphertext = NULL" in sql
    assert "payload_nonce = NULL" in sql
    assert "payload_key_id = NULL" in sql

    assert "locked_at = NULL" in sql
    assert "lock_expires_at = NULL" in sql
    assert "lock_token = NULL" in sql


def test_completion_requires_active_job_lease():
    assert (
        "job.lock_expires_at > NOW()"
        in worker.SQL_COMPLETE_OWNED_JOB
    )


def test_completion_requires_active_receipt_lease():
    assert (
        "receipt.lease_expires_at > NOW()"
        in worker.SQL_COMPLETE_OWNED_RECEIPT
    )


def test_idempotent_replay_returns_already_completed(
    monkeypatch,
):
    outcome, cursor, tracker = complete(
        monkeypatch,
        [
            locked_receipt_row(
                status="completed",
                lease_active=False,
            ),
            completed_job_row(),
        ],
    )

    assert (
        outcome.decision
        == "already_completed"
    )

    assert outcome.idempotent_replay is True
    assert outcome.completed is True

    assert tracker.committed == 1
    assert tracker.rolled_back == 0

    executions = business_executions(
        cursor
    )

    assert len(executions) == 2

    assert (
        "UPDATE public.telegram_update_jobs"
        not in executions[1][0]
    )

    assert (
        "SELECT"
        in executions[1][0]
    )


def test_idempotent_replay_requires_same_token(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                status="completed",
                claim_token=OTHER_TOKEN,
                lease_active=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_missing_receipt_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            None,
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_expired_receipt_lease_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                lease_active=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_failed_receipt_cannot_be_completed(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                status="failed",
                lease_active=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_wrong_receipt_owner_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                claim_token=OTHER_TOKEN,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_job_completion_failure_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            None,
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_receipt_completion_failure_rolls_back_job(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            None,
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_mismatched_receipt_update_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                update_id=UPDATE_ID + 1,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_mismatched_job_update_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(
                update_id=UPDATE_ID + 1,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_wrong_job_attempt_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(
                attempt_count=1,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1



def test_wrong_job_max_attempts_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(
                max_attempts=6,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_wrong_job_payload_version_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(
                payload_version=2,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1

@pytest.mark.parametrize(
    "field_name",
    [
        "payload_cleared",
        "ownership_cleared",
        "completed_at_set",
    ],
)
def test_incomplete_job_state_is_rejected(
    monkeypatch,
    field_name,
):
    values = {
        field_name: False,
    }

    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(
                **values
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_incomplete_receipt_state_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            completed_receipt_row(
                completed_at_set=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    assert tracker.rolled_back == 1


def test_safe_outcome_hides_tokens_and_payload(
    monkeypatch,
):
    outcome, _, _ = complete(
        monkeypatch,
        [
            locked_receipt_row(),
            completed_job_row(),
            completed_receipt_row(),
        ],
    )

    safe = outcome.to_safe_dict()
    representation = repr(
        outcome
    )

    assert "lock_token" not in safe
    assert "claim_token" not in safe
    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe

    assert LOCK_TOKEN not in representation
    assert repr(CIPHERTEXT) not in representation


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(
        **_kwargs,
    ):
        raise RuntimeError(
            "postgresql://user:"
            "secret-value@host/database"
        )

        yield

    monkeypatch.setattr(
        worker,
        "cursor_postgres",
        failing_cursor,
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerUnavailableError
    ) as captured:
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                make_lease()
            )
        )

    message = str(
        captured.value
    )

    assert "secret-value" not in message
    assert "postgresql://" not in message


def test_wrong_lease_type_is_rejected():
    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                {
                    "update_id": UPDATE_ID,
                }
            )
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    [
        ("job_status", "queued"),
        ("receipt_status", "failed"),
        ("job_attempt_count", 0),
        ("job_max_attempts", 0),
        ("receipt_attempt_count", 0),
        ("payload_version", 0),
        ("payload_key_id", "invalid key"),
        ("lock_token", "short"),
    ],
    ids=[
        "job-status",
        "receipt-status",
        "job-attempt",
        "job-max-attempts",
        "receipt-attempt",
        "payload-version",
        "key-id",
        "lock-token",
    ],
)
def test_invalid_lease_is_rejected(
    field_name,
    invalid_value,
):
    invalid_lease = replace(
        make_lease(),
        **{
            field_name: invalid_value,
        },
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                invalid_lease
            )
        )


def test_receipt_attempts_cannot_trail_job():
    invalid_lease = replace(
        make_lease(),
        job_attempt_count=3,
        receipt_attempt_count=2,
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .complete_authenticated_telegram_update_job_atomic(
                invalid_lease
            )
        )


def test_sql_keeps_receipt_first_lock_order():
    assert (
        "FOR UPDATE"
        in worker
        .SQL_LOCK_RECEIPT_FOR_COMPLETION
    )


def test_job_completion_is_ownership_guarded():
    sql = worker.SQL_COMPLETE_OWNED_JOB

    assert (
        "job.status = 'processing'"
        in sql
    )

    assert (
        "job.lock_token = %(lock_token)s"
        in sql
    )


def test_receipt_completion_is_ownership_guarded():
    sql = (
        worker
        .SQL_COMPLETE_OWNED_RECEIPT
    )

    assert (
        "receipt.status = 'processing'"
        in sql
    )

    assert (
        "receipt.claim_token = %(lock_token)s"
        in sql
    )

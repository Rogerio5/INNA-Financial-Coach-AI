from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace

import pytest

from src.services.telegram_update_jobs import (
    worker,
)


UPDATE_ID = 93001
LOCK_TOKEN = "a" * 64
OTHER_TOKEN = "b" * 64

ERROR_CODE = "telegram.processing_failed"

CIPHERTEXT = b"c" * 32
NONCE = b"n" * 12
KEY_ID = "inna.telegram.v1"


def make_lease(
    *,
    attempt_count=2,
    max_attempts=5,
):
    return worker.TelegramUpdateWorkerLease(
        update_id=UPDATE_ID,
        job_status="processing",
        receipt_status="processing",
        job_attempt_count=attempt_count,
        job_max_attempts=max_attempts,
        receipt_attempt_count=attempt_count,
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
    last_error_code=None,
    lease_active=True,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "claim_token": claim_token,
        "last_error_code": (
            last_error_code
        ),
        "lease_active": lease_active,
    }


def failed_job_row(
    *,
    update_id=UPDATE_ID,
    status="queued",
    attempt_count=2,
    max_attempts=5,
    payload_version=1,
    last_error_code=ERROR_CODE,
    payload_retained=True,
    ownership_cleared=True,
    completed_at_cleared=True,
    retry_state_valid=None,
    dead_letter_state_valid=None,
):
    if retry_state_valid is None:
        retry_state_valid = (
            status == "queued"
        )

    if dead_letter_state_valid is None:
        dead_letter_state_valid = (
            status == "dead_letter"
        )

    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "payload_version": payload_version,
        "last_error_code": (
            last_error_code
        ),
        "payload_retained": (
            payload_retained
        ),
        "ownership_cleared": (
            ownership_cleared
        ),
        "completed_at_cleared": (
            completed_at_cleared
        ),
        "retry_state_valid": (
            retry_state_valid
        ),
        "dead_letter_state_valid": (
            dead_letter_state_valid
        ),
    }


def failed_receipt_row(
    *,
    update_id=UPDATE_ID,
    attempt_count=2,
    last_error_code=ERROR_CODE,
    completed_at_cleared=True,
    failed_at_set=True,
    lease_closed=True,
):
    return {
        "update_id": update_id,
        "status": "failed",
        "attempt_count": attempt_count,
        "last_error_code": (
            last_error_code
        ),
        "completed_at_cleared": (
            completed_at_cleared
        ),
        "failed_at_set": failed_at_set,
        "lease_closed": lease_closed,
    }


class FakeCursor:
    def __init__(
        self,
        rows,
    ):
        self.rows = list(rows)
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
        if not self.rows:
            return None

        return self.rows.pop(0)


class TransactionTracker:
    def __init__(self):
        self.entered = 0
        self.committed = 0
        self.rolled_back = 0


def install_transaction(
    monkeypatch,
    rows,
):
    cursor = FakeCursor(rows)
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


def finalize_failure(
    monkeypatch,
    rows,
    *,
    lease=None,
    error_code=ERROR_CODE,
    retry_delay_seconds=60,
    force_dead_letter=False,
):
    cursor, tracker = (
        install_transaction(
            monkeypatch,
            rows,
        )
    )

    outcome = (
        worker
        .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
            (
                lease
                if lease is not None
                else make_lease()
            ),
            error_code=error_code,
            retry_delay_seconds=(
                retry_delay_seconds
            ),
            force_dead_letter=(
                force_dead_letter
            ),
        )
    )

    return outcome, cursor, tracker


def business_executions(cursor):
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


def test_schedules_retry_atomically(
    monkeypatch,
):
    outcome, _, tracker = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(),
        ],
    )

    assert (
        outcome.decision
        == "retry_scheduled"
    )

    assert outcome.job_status == "queued"
    assert outcome.receipt_status == "failed"

    assert outcome.retry_scheduled is True
    assert outcome.dead_lettered is False
    assert outcome.terminal is False

    assert outcome.retry_delay_seconds == 60
    assert outcome.payload_retained is True
    assert outcome.ownership_cleared is True

    assert tracker.entered == 1
    assert tracker.committed == 1
    assert tracker.rolled_back == 0


def test_dead_letters_when_attempts_exhausted(
    monkeypatch,
):
    lease = make_lease(
        attempt_count=5,
        max_attempts=5,
    )

    outcome, _, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(
                attempt_count=5,
            ),
            failed_job_row(
                status="dead_letter",
                attempt_count=5,
                max_attempts=5,
            ),
            failed_receipt_row(
                attempt_count=5,
            ),
        ],
        lease=lease,
    )

    assert outcome.decision == "dead_lettered"
    assert outcome.job_status == "dead_letter"
    assert outcome.dead_lettered is True
    assert outcome.terminal is True
    assert outcome.retry_delay_seconds is None


def test_force_dead_letter_before_max_attempts(
    monkeypatch,
):
    outcome, cursor, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(
                status="dead_letter",
            ),
            failed_receipt_row(),
        ],
        force_dead_letter=True,
    )

    assert outcome.dead_lettered is True

    executions = business_executions(
        cursor
    )

    assert (
        executions[1][1][
            "force_dead_letter"
        ]
        is True
    )


def test_receipt_is_locked_before_job(
    monkeypatch,
):
    _, cursor, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(),
        ],
    )

    executions = business_executions(
        cursor
    )

    assert len(executions) == 3
    assert "FOR UPDATE" in executions[0][0]

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
    _, cursor, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(),
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


def test_payload_is_preserved_for_retry():
    sql = (
        worker
        .SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB
    )

    assert "payload_ciphertext = NULL" not in sql
    assert "payload_nonce = NULL" not in sql
    assert "payload_key_id = NULL" not in sql

    assert (
        "payload_ciphertext IS NOT NULL"
        in sql
    )


def test_payload_is_preserved_for_dead_letter():
    sql = (
        worker
        .SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB
    )

    assert "payload_retained" in sql


def test_retry_uses_requested_backoff(
    monkeypatch,
):
    _, cursor, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(),
        ],
        retry_delay_seconds=900,
    )

    executions = business_executions(
        cursor
    )

    assert (
        executions[1][1][
            "retry_delay_seconds"
        ]
        == 900
    )


def test_job_update_requires_active_lease():
    sql = (
        worker
        .SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB
    )

    assert (
        "job.status = 'processing'"
        in sql
    )

    assert (
        "job.lock_token = %(lock_token)s"
        in sql
    )

    assert (
        "job.lock_expires_at > NOW()"
        in sql
    )


def test_receipt_update_requires_active_lease():
    sql = worker.SQL_FAIL_OWNED_RECEIPT

    assert (
        "receipt.status = 'processing'"
        in sql
    )

    assert (
        "receipt.claim_token = %(lock_token)s"
        in sql
    )

    assert (
        "receipt.lease_expires_at > NOW()"
        in sql
    )


def test_retry_idempotent_replay(
    monkeypatch,
):
    outcome, cursor, tracker = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(
                status="failed",
                last_error_code=ERROR_CODE,
                lease_active=False,
            ),
            failed_job_row(),
        ],
    )

    assert (
        outcome.decision
        == "already_retry_scheduled"
    )

    assert outcome.idempotent_replay is True
    assert outcome.retry_delay_seconds is None

    assert tracker.committed == 1
    assert tracker.rolled_back == 0

    executions = business_executions(
        cursor
    )

    assert len(executions) == 2
    assert "SELECT" in executions[1][0]


def test_dead_letter_idempotent_replay(
    monkeypatch,
):
    outcome, _, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(
                status="failed",
                last_error_code=ERROR_CODE,
                lease_active=False,
            ),
            failed_job_row(
                status="dead_letter",
            ),
        ],
    )

    assert (
        outcome.decision
        == "already_dead_lettered"
    )

    assert outcome.idempotent_replay is True
    assert outcome.dead_lettered is True


def test_replay_requires_same_token(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                status="failed",
                claim_token=OTHER_TOKEN,
                last_error_code=ERROR_CODE,
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_replay_rejects_different_error_code(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                status="failed",
                last_error_code=(
                    "telegram.other_error"
                ),
                lease_active=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_missing_receipt_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [None],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_expired_receipt_rolls_back(
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_completed_receipt_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(
                status="completed",
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_job_update_failure_rolls_back(
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_receipt_update_failure_rolls_back_job(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            None,
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerOwnershipError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    [
        ("update_id", UPDATE_ID + 1),
        ("attempt_count", 1),
        ("max_attempts", 6),
        ("payload_version", 2),
    ],
)
def test_job_metadata_mismatch_is_rejected(
    monkeypatch,
    field_name,
    invalid_value,
):
    values = {
        field_name: invalid_value,
    }

    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


@pytest.mark.parametrize(
    "field_name",
    [
        "payload_retained",
        "ownership_cleared",
        "completed_at_cleared",
    ],
)
def test_incomplete_job_state_is_rejected(
    monkeypatch,
    field_name,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(
                **{
                    field_name: False,
                }
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_invalid_retry_state_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(
                status="queued",
                retry_state_valid=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_invalid_dead_letter_state_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(
                status="dead_letter",
                dead_letter_state_valid=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_invalid_receipt_result_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(
                failed_at_set=False,
            ),
        ],
    )

    with pytest.raises(
        worker
        .TelegramUpdateWorkerConsistencyError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    assert tracker.rolled_back == 1


def test_safe_outcome_hides_sensitive_values(
    monkeypatch,
):
    outcome, _, _ = finalize_failure(
        monkeypatch,
        [
            locked_receipt_row(),
            failed_job_row(),
            failed_receipt_row(),
        ],
    )

    safe = outcome.to_safe_dict()
    representation = repr(outcome)

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
    def failing_cursor(**_kwargs):
        raise RuntimeError(
            "postgresql://user:"
            "secret-password@host/database"
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
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )

    message = str(captured.value)

    assert "secret-password" not in message
    assert "postgresql://" not in message


@pytest.mark.parametrize(
    "value",
    [
        "",
        "UPPERCASE",
        "com espaço",
        "a" * 65,
        " telegram.error",
    ],
)
def test_invalid_error_code_is_rejected(
    value,
):
    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=value,
                retry_delay_seconds=60,
            )
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        86401,
        True,
        "60",
    ],
)
def test_invalid_retry_delay_is_rejected(
    value,
):
    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=value,
            )
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        "true",
        None,
    ],
)
def test_force_dead_letter_requires_boolean(
    value,
):
    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                make_lease(),
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
                force_dead_letter=value,
            )
        )


def test_wrong_lease_type_is_rejected():
    with pytest.raises(
        worker
        .TelegramUpdateWorkerValidationError
    ):
        (
            worker
            .retry_or_dead_letter_authenticated_telegram_update_job_atomic(
                {
                    "update_id": UPDATE_ID,
                },
                error_code=ERROR_CODE,
                retry_delay_seconds=60,
            )
        )


def test_sql_has_explicit_dead_letter_transition():
    sql = (
        worker
        .SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB
    )

    assert "THEN 'dead_letter'" in sql
    assert "ELSE 'queued'" in sql

    assert (
        "job.attempt_count >= job.max_attempts"
        in sql
    )

    assert "%(force_dead_letter)s" in sql


def test_sql_clears_ownership():
    sql = (
        worker
        .SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB
    )

    assert "locked_at = NULL" in sql
    assert "lock_expires_at = NULL" in sql
    assert "lock_token = NULL" in sql

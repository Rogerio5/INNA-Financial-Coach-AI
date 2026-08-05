from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.services.telegram_update_jobs import (
    worker,
)


UPDATE_ID = 81001
LOCK_TOKEN = "a" * 64

CIPHERTEXT = b"c" * 32
NONCE = b"n" * 12
KEY_ID = "inna.telegram.v1"


def candidate_row(
    *,
    status="processing",
    attempt_count=1,
):
    return {
        "update_id": UPDATE_ID,
        "receipt_status": status,
        "receipt_attempt_count": (attempt_count),
    }


def claimed_job_row(
    *,
    update_id=UPDATE_ID,
    attempt_count=1,
    max_attempts=5,
    payload_version=1,
    lock_token=LOCK_TOKEN,
):
    return {
        "update_id": update_id,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "payload_version": payload_version,
        "payload_ciphertext": CIPHERTEXT,
        "payload_nonce": NONCE,
        "payload_key_id": KEY_ID,
        "lock_token": lock_token,
    }


def owned_receipt_row(
    *,
    update_id=UPDATE_ID,
    status="processing",
    attempt_count=1,
    claim_token=LOCK_TOKEN,
):
    return {
        "update_id": update_id,
        "status": status,
        "attempt_count": attempt_count,
        "claim_token": claim_token,
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

    def fetchone(
        self,
    ):
        if not self.rows:
            return None

        return self.rows.pop(0)


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

    monkeypatch.setattr(
        worker.crypto_service,
        ("generate_telegram_update_job_lock_token"),
        lambda: LOCK_TOKEN,
    )

    return cursor, tracker


def claim(
    monkeypatch,
    rows,
    *,
    lease_seconds=120,
):
    cursor, tracker = install_transaction(
        monkeypatch,
        rows,
    )

    lease = worker.claim_next_authenticated_telegram_update_job_atomic(
        lease_seconds=lease_seconds,
    )

    return lease, cursor, tracker


def business_executions(
    cursor,
):
    return [
        (
            str(sql),
            parameters,
        )
        for sql, parameters in cursor.executions
        if not str(sql).startswith("SET LOCAL")
    ]


def test_claim_returns_worker_lease(
    monkeypatch,
):
    lease, _, tracker = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
    )

    assert lease is not None
    assert lease.update_id == UPDATE_ID

    assert lease.job_status == "processing"
    assert lease.receipt_status == "processing"

    assert lease.job_attempt_count == 1
    assert lease.job_max_attempts == 5

    assert tracker.entered == 1
    assert tracker.committed == 1
    assert tracker.rolled_back == 0


def test_receipt_is_locked_before_job(
    monkeypatch,
):
    _, cursor, _ = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
    )

    executions = business_executions(cursor)

    assert len(executions) == 3

    assert "FOR UPDATE OF receipt SKIP LOCKED" in executions[0][0]

    assert "UPDATE public.telegram_update_jobs" in executions[1][0]

    assert "UPDATE public.telegram_update_receipts" in executions[2][0]


def test_same_token_is_used_for_job_and_receipt(
    monkeypatch,
):
    lease, cursor, _ = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
    )

    executions = business_executions(cursor)

    job_parameters = executions[1][1]
    receipt_parameters = executions[2][1]

    assert job_parameters["lock_token"] == LOCK_TOKEN

    assert receipt_parameters["lock_token"] == LOCK_TOKEN

    assert lease.lock_token == LOCK_TOKEN


def test_same_lease_is_used_for_both_records(
    monkeypatch,
):
    _, cursor, _ = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
        lease_seconds=240,
    )

    executions = business_executions(cursor)

    assert executions[1][1]["lease_seconds"] == 240

    assert executions[2][1]["lease_seconds"] == 240


def test_failed_receipt_can_be_transferred(
    monkeypatch,
):
    lease, _, _ = claim(
        monkeypatch,
        [
            candidate_row(
                status="failed",
                attempt_count=1,
            ),
            claimed_job_row(
                attempt_count=2,
            ),
            owned_receipt_row(
                attempt_count=2,
            ),
        ],
    )

    assert lease is not None
    assert lease.job_attempt_count == 2
    assert lease.receipt_attempt_count == 2


def test_no_available_job_returns_none(
    monkeypatch,
):
    lease, _, tracker = claim(
        monkeypatch,
        [
            None,
        ],
    )

    assert lease is None
    assert tracker.committed == 1
    assert tracker.rolled_back == 0


def test_claim_uses_single_transaction(
    monkeypatch,
):
    _, _, tracker = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
    )

    assert tracker.entered == 1
    assert tracker.committed == 1


def test_job_disappearing_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            None,
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_receipt_transfer_failure_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            None,
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_mismatched_update_ids_are_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(
                update_id=UPDATE_ID + 1,
            ),
            owned_receipt_row(),
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.rolled_back == 1


def test_mismatched_ownership_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(
                claim_token="b" * 64,
            ),
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.rolled_back == 1


def test_receipt_attempts_cannot_trail_job(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(
                attempt_count=3,
            ),
            owned_receipt_row(
                attempt_count=2,
            ),
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.rolled_back == 1


def test_invalid_ciphertext_is_rejected(
    monkeypatch,
):
    invalid_job = claimed_job_row()

    invalid_job["payload_ciphertext"] = b"x"

    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            invalid_job,
            owned_receipt_row(),
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.rolled_back == 1


def test_invalid_nonce_is_rejected(
    monkeypatch,
):
    invalid_job = claimed_job_row()

    invalid_job["payload_nonce"] = b"short"

    _, tracker = install_transaction(
        monkeypatch,
        [
            candidate_row(),
            invalid_job,
            owned_receipt_row(),
        ],
    )

    with pytest.raises(worker.TelegramUpdateWorkerConsistencyError):
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert tracker.rolled_back == 1


def test_safe_output_hides_sensitive_values(
    monkeypatch,
):
    lease, _, _ = claim(
        monkeypatch,
        [
            candidate_row(),
            claimed_job_row(),
            owned_receipt_row(),
        ],
    )

    assert lease is not None

    safe = lease.to_safe_dict()

    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe
    assert "lock_token" not in safe

    representation = repr(lease)

    assert repr(CIPHERTEXT) not in representation
    assert repr(NONCE) not in representation
    assert LOCK_TOKEN not in representation


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(
        **_kwargs,
    ):
        raise RuntimeError("postgresql://user:secret-password@host/database")

        yield

    monkeypatch.setattr(
        worker,
        "cursor_postgres",
        failing_cursor,
    )

    monkeypatch.setattr(
        worker.crypto_service,
        ("generate_telegram_update_job_lock_token"),
        lambda: LOCK_TOKEN,
    )

    with pytest.raises(worker.TelegramUpdateWorkerUnavailableError) as captured:
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    message = str(captured.value)

    assert "secret-password" not in message
    assert "postgresql://" not in message


def test_token_generation_failure_is_sanitized(
    monkeypatch,
):
    def fail_token():
        raise RuntimeError("sensitive entropy error")

    monkeypatch.setattr(
        worker.crypto_service,
        ("generate_telegram_update_job_lock_token"),
        fail_token,
    )

    with pytest.raises(worker.TelegramUpdateWorkerUnavailableError) as captured:
        (worker.claim_next_authenticated_telegram_update_job_atomic())

    assert "sensitive" not in str(captured.value)


@pytest.mark.parametrize(
    "value",
    [
        4,
        3601,
        True,
        "120",
    ],
    ids=[
        "too-low",
        "too-high",
        "boolean",
        "string",
    ],
)
def test_invalid_lease_is_rejected(
    value,
):
    with pytest.raises(worker.TelegramUpdateWorkerValidationError):
        (
            worker.claim_next_authenticated_telegram_update_job_atomic(
                lease_seconds=value,
            )
        )


def test_sql_contract_uses_skip_locked():
    assert "FOR UPDATE OF receipt SKIP LOCKED" in worker.SQL_SELECT_CLAIMABLE_RECEIPT


def test_sql_contract_limits_to_one_job():
    assert "LIMIT 1" in worker.SQL_SELECT_CLAIMABLE_RECEIPT


def test_job_claim_is_conditional():
    sql = worker.SQL_CLAIM_JOB_BY_UPDATE_ID

    assert "job.status = 'queued'" in sql

    assert "job.attempt_count < job.max_attempts" in sql


def test_receipt_transfer_accepts_failed_state():
    assert "'failed'" in worker.SQL_TRANSFER_RECEIPT_TO_WORKER


def test_receipt_attempt_count_tracks_job():
    assert "GREATEST" in worker.SQL_TRANSFER_RECEIPT_TO_WORKER

from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.services.telegram_update_jobs import (
    repository,
)


LOCK_TOKEN = "a" * 64
OTHER_LOCK_TOKEN = "b" * 64

CIPHERTEXT = b"x" * 32
NONCE = b"n" * 12
KEY_ID = "inna.telegram.v1"


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

    def fetchall(
        self,
    ):
        rows = list(self.rows)
        self.rows.clear()
        return rows


def install_cursor(
    monkeypatch,
    rows,
):
    cursor = FakeCursor(rows)

    @contextmanager
    def fake_cursor_postgres(
        *,
        dict_cursor,
        commit_automatico,
    ):
        assert dict_cursor is True
        assert commit_automatico is True
        yield cursor

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    return cursor


def job_row(
    *,
    status="queued",
    attempt_count=0,
    max_attempts=5,
):
    return {
        "update_id": 1001,
        "status": status,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "payload_version": 1,
    }


def lease_row():
    return {
        "update_id": 1001,
        "attempt_count": 1,
        "max_attempts": 5,
        "payload_version": 1,
        "payload_ciphertext": CIPHERTEXT,
        "payload_nonce": NONCE,
        "payload_key_id": KEY_ID,
        "lock_token": LOCK_TOKEN,
    }


def test_safe_lease_hides_payload_and_token():
    lease = repository.TelegramUpdateJobLease(
        update_id=1001,
        attempt_count=1,
        max_attempts=5,
        payload_version=1,
        payload_ciphertext=CIPHERTEXT,
        payload_nonce=NONCE,
        payload_key_id=KEY_ID,
        lock_token=LOCK_TOKEN,
    )

    safe = lease.to_safe_dict()

    assert "lock_token" not in safe
    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe
    assert "payload_key_id" not in safe

    representation = repr(lease)

    assert LOCK_TOKEN not in representation
    assert KEY_ID not in representation


def test_enqueue_new_job(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            job_row(),
        ],
    )

    result = repository.enqueue_telegram_update_job(
        update_id=1001,
        payload_ciphertext=CIPHERTEXT,
        payload_nonce=NONCE,
        payload_key_id=KEY_ID,
    )

    assert result.status == "queued"
    assert result.attempt_count == 0

    assert any("ON CONFLICT" in sql for sql, _ in cursor.executions)


def test_enqueue_existing_job_is_idempotent(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            None,
            job_row(
                status="processing",
                attempt_count=1,
            ),
        ],
    )

    result = repository.enqueue_telegram_update_job(
        update_id=1001,
        payload_ciphertext=CIPHERTEXT,
        payload_nonce=NONCE,
        payload_key_id=KEY_ID,
    )

    assert result.status == "processing"

    assert any("FOR UPDATE" in sql for sql, _ in cursor.executions)


def test_claim_returns_none_when_queue_empty(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
        ],
    )

    result = repository.claim_next_telegram_update_job(
        lock_token=LOCK_TOKEN,
    )

    assert result is None


def test_claim_returns_secure_lease(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            lease_row(),
        ],
    )

    result = repository.claim_next_telegram_update_job(
        lock_token=LOCK_TOKEN,
    )

    assert result is not None
    assert result.update_id == 1001
    assert result.attempt_count == 1
    assert result.lock_token == LOCK_TOKEN
    assert result.payload_nonce == NONCE


def test_renew_active_lease(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            job_row(
                status="processing",
                attempt_count=1,
            ),
        ],
    )

    result = repository.renew_telegram_update_job_lease(
        update_id=1001,
        lock_token=LOCK_TOKEN,
    )

    assert result.status == "processing"


def test_renew_rejects_lost_lease(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
        ],
    )

    with pytest.raises(repository.TelegramUpdateJobOwnershipError):
        repository.renew_telegram_update_job_lease(
            update_id=1001,
            lock_token=LOCK_TOKEN,
        )


def test_complete_job(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            job_row(
                status="completed",
                attempt_count=1,
            ),
        ],
    )

    result = repository.complete_telegram_update_job(
        update_id=1001,
        lock_token=LOCK_TOKEN,
    )

    assert result.status == "completed"


def test_complete_rejects_old_worker(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
        ],
    )

    with pytest.raises(repository.TelegramUpdateJobOwnershipError):
        repository.complete_telegram_update_job(
            update_id=1001,
            lock_token=LOCK_TOKEN,
        )


def test_retry_queues_job(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            job_row(
                status="queued",
                attempt_count=1,
            ),
        ],
    )

    result = repository.retry_or_dead_letter_telegram_update_job(
        update_id=1001,
        lock_token=LOCK_TOKEN,
        error_code=("telegram.processing_failed"),
        retry_delay_seconds=30,
    )

    assert result.status == "queued"


def test_retry_dead_letters_exhausted_job(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            job_row(
                status="dead_letter",
                attempt_count=5,
            ),
        ],
    )

    result = repository.retry_or_dead_letter_telegram_update_job(
        update_id=1001,
        lock_token=LOCK_TOKEN,
        error_code=("telegram.processing_failed"),
        retry_delay_seconds=30,
    )

    assert result.status == "dead_letter"


def test_retry_rejects_old_worker(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
        ],
    )

    with pytest.raises(repository.TelegramUpdateJobOwnershipError):
        repository.retry_or_dead_letter_telegram_update_job(
            update_id=1001,
            lock_token=LOCK_TOKEN,
            error_code=("telegram.processing_failed"),
            retry_delay_seconds=30,
        )


def test_recover_expired_jobs(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            job_row(
                status="queued",
                attempt_count=1,
            ),
            {
                **job_row(
                    status="dead_letter",
                    attempt_count=5,
                ),
                "update_id": 1002,
            },
        ],
    )

    results = repository.recover_expired_telegram_update_jobs(limit=25)

    assert len(results) == 2
    assert results[0].status == "queued"
    assert results[1].status == "dead_letter"


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(
        **_kwargs,
    ):
        raise RuntimeError("postgresql://user:super-secret@database/inna")

        yield

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        failing_cursor,
    )

    with pytest.raises(repository.TelegramUpdateJobRepositoryError) as captured:
        repository.claim_next_telegram_update_job(
            lock_token=LOCK_TOKEN,
        )

    message = str(captured.value)

    assert "super-secret" not in message
    assert "postgresql://" not in message


def test_claim_sql_uses_skip_locked():
    sql = repository.SQL_CLAIM_NEXT_JOB

    assert "FOR UPDATE SKIP LOCKED" in sql
    assert "available_at <= NOW()" in sql
    assert "attempt_count < max_attempts" in sql


def test_ownership_sql_requires_active_lease():
    for sql in (
        repository.SQL_RENEW_JOB_LEASE,
        repository.SQL_COMPLETE_JOB,
        repository.SQL_RETRY_OR_DEAD_LETTER_JOB,
    ):
        assert "lock_token = %(lock_token)s" in sql

        assert "lock_expires_at > NOW()" in sql


def test_complete_clears_sensitive_payload():
    sql = repository.SQL_COMPLETE_JOB

    assert "payload_ciphertext = NULL" in sql
    assert "payload_nonce = NULL" in sql
    assert "payload_key_id = NULL" in sql
    assert "lock_token = NULL" in sql


def test_retry_uses_available_at():
    sql = repository.SQL_RETRY_OR_DEAD_LETTER_JOB

    assert "retry_delay_seconds" in sql
    assert "available_at = CASE" in sql
    assert "'dead_letter'" in sql


def test_recovery_handles_retry_and_dead_letter():
    sql = repository.SQL_RECOVER_EXPIRED_JOBS

    assert "FOR UPDATE SKIP LOCKED" in sql
    assert "lock_expires_at <= NOW()" in sql

    assert "'telegram.worker_lease_expired'" in sql

    assert "'dead_letter'" in sql
    assert "'queued'" in sql


@pytest.mark.parametrize(
    "value",
    [
        -1,
        True,
        "1001",
        None,
    ],
)
def test_invalid_update_id_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.enqueue_telegram_update_job(
            update_id=value,
            payload_ciphertext=CIPHERTEXT,
            payload_nonce=NONCE,
            payload_key_id=KEY_ID,
        )


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"x" * 15,
        b"x" * 1_048_577,
        "plaintext",
    ],
    ids=[
        "empty",
        "too-short",
        "too-large",
        "wrong-type",
    ],
)
def test_invalid_ciphertext_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.enqueue_telegram_update_job(
            update_id=1001,
            payload_ciphertext=value,
            payload_nonce=NONCE,
            payload_key_id=KEY_ID,
        )


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"n" * 11,
        b"n" * 13,
        "nonce",
    ],
)
def test_invalid_nonce_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.enqueue_telegram_update_job(
            update_id=1001,
            payload_ciphertext=CIPHERTEXT,
            payload_nonce=value,
            payload_key_id=KEY_ID,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "contains space",
        "a" * 65,
        None,
    ],
)
def test_invalid_key_id_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.enqueue_telegram_update_job(
            update_id=1001,
            payload_ciphertext=CIPHERTEXT,
            payload_nonce=NONCE,
            payload_key_id=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "x" * 64,
        "a" * 63,
        None,
    ],
)
def test_invalid_lock_token_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.claim_next_telegram_update_job(
            lock_token=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        4,
        3601,
        True,
    ],
)
def test_invalid_lease_seconds_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.claim_next_telegram_update_job(
            lock_token=LOCK_TOKEN,
            lease_seconds=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        21,
        True,
        "5",
    ],
)
def test_invalid_max_attempts_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.enqueue_telegram_update_job(
            update_id=1001,
            payload_ciphertext=CIPHERTEXT,
            payload_nonce=NONCE,
            payload_key_id=KEY_ID,
            max_attempts=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "UPPERCASE",
        "contains space",
        "a" * 65,
    ],
)
def test_invalid_error_code_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.retry_or_dead_letter_telegram_update_job(
            update_id=1001,
            lock_token=LOCK_TOKEN,
            error_code=value,
            retry_delay_seconds=10,
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        86_401,
        True,
    ],
)
def test_invalid_retry_delay_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.retry_or_dead_letter_telegram_update_job(
            update_id=1001,
            lock_token=LOCK_TOKEN,
            error_code=("telegram.processing_failed"),
            retry_delay_seconds=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        501,
        True,
    ],
)
def test_invalid_recovery_limit_is_rejected(
    value,
):
    with pytest.raises(repository.TelegramUpdateJobValidationError):
        repository.recover_expired_telegram_update_jobs(limit=value)

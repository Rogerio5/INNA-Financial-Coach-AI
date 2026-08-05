from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.services.telegram_update_jobs import (
    ingress,
)

from src.services.telegram_update_jobs import (
    service as crypto_service,
)

from src.services.telegram_update_receipts import (
    service as receipt_service,
)


UPDATE_ID = 7001

UPDATE = {
    "update_id": UPDATE_ID,
    "message": {
        "message_id": 55,
        "chat": {
            "id": 123456,
        },
        "text": "Quero organizar as finanças.",
    },
}

KEYRING = crypto_service.TelegramUpdateEncryptionKeyring(
    active_key_id="inna.telegram.v1",
    keys={
        "inna.telegram.v1": (b"k" * 32),
    },
)

FINGERPRINT = receipt_service.fingerprint_telegram_update(UPDATE)

OTHER_FINGERPRINT = "f" * 64


def receipt_row(
    *,
    status="processing",
    attempt_count=1,
    fingerprint=FINGERPRINT,
    lease_active=False,
):
    return {
        "update_id": UPDATE_ID,
        "update_fingerprint": (fingerprint),
        "status": status,
        "attempt_count": attempt_count,
        "lease_active": lease_active,
    }


def job_row(
    *,
    status="queued",
    attempt_count=0,
    max_attempts=5,
    payload_version=1,
):
    return {
        "update_id": UPDATE_ID,
        "status": status,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "payload_version": payload_version,
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
        ingress,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    return cursor, tracker


def enqueue(
    monkeypatch,
    rows,
):
    cursor, tracker = install_transaction(
        monkeypatch,
        rows,
    )

    outcome = ingress.enqueue_authenticated_telegram_update_atomic(
        UPDATE,
        keyring=KEYRING,
    )

    return (
        outcome,
        cursor,
        tracker,
    )


def test_new_update_creates_receipt_and_job(
    monkeypatch,
):
    outcome, cursor, tracker = enqueue(
        monkeypatch,
        [
            receipt_row(),
            job_row(),
        ],
    )

    assert outcome.decision == "enqueued"
    assert outcome.receipt_state == "claimed"
    assert outcome.job_state == "queued"
    assert outcome.job_created is True
    assert outcome.accepted is True

    assert tracker.entered == 1
    assert tracker.committed == 1
    assert tracker.rolled_back == 0

    sql_text = "\n".join(str(sql) for sql, _ in cursor.executions)

    assert "telegram_update_receipts" in sql_text

    assert "telegram_update_jobs" in sql_text


def test_single_transaction_is_used(
    monkeypatch,
):
    _, _, tracker = enqueue(
        monkeypatch,
        [
            receipt_row(),
            job_row(),
        ],
    )

    assert tracker.entered == 1
    assert tracker.committed == 1


def test_payload_is_encrypted_before_job_insert(
    monkeypatch,
):
    _, cursor, _ = enqueue(
        monkeypatch,
        [
            receipt_row(),
            job_row(),
        ],
    )

    job_execution = next(
        (
            sql,
            parameters,
        )
        for sql, parameters in cursor.executions
        if ("telegram_update_jobs" in str(sql) and "INSERT INTO" in str(sql))
    )

    parameters = job_execution[1]

    assert isinstance(
        parameters["payload_ciphertext"],
        bytes,
    )

    assert isinstance(
        parameters["payload_nonce"],
        bytes,
    )

    assert parameters["payload_ciphertext"] != str(UPDATE).encode("utf-8")

    assert len(parameters["payload_nonce"]) == 12


def test_completed_receipt_without_job_is_duplicate(
    monkeypatch,
):
    outcome, _, tracker = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="completed",
            ),
            None,
        ],
    )

    assert outcome.decision == "duplicate"
    assert outcome.duplicate is True
    assert outcome.job_state is None

    assert tracker.committed == 1


def test_completed_receipt_with_completed_job_is_duplicate(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="completed",
            ),
            job_row(
                status="completed",
                attempt_count=1,
            ),
        ],
    )

    assert outcome.decision == "duplicate"
    assert outcome.job_state == "completed"


def test_completed_receipt_with_active_job_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            None,
            receipt_row(
                status="completed",
            ),
            job_row(
                status="queued",
            ),
        ],
    )

    with pytest.raises(ingress.TelegramUpdateIngressConsistencyError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_active_receipt_repairs_missing_job(
    monkeypatch,
):
    outcome, _, tracker = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="processing",
                lease_active=True,
            ),
            job_row(),
        ],
    )

    assert outcome.decision == "enqueued"
    assert outcome.receipt_state == "processing"
    assert outcome.job_created is True

    assert tracker.committed == 1


def test_existing_queued_job_is_not_duplicated(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="processing",
                lease_active=True,
            ),
            None,
            job_row(
                status="queued",
            ),
        ],
    )

    assert outcome.decision == "already_enqueued"

    assert outcome.job_created is False
    assert outcome.job_state == "queued"


def test_existing_processing_job_returns_in_progress(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="processing",
                lease_active=True,
            ),
            None,
            job_row(
                status="processing",
                attempt_count=1,
            ),
        ],
    )

    assert outcome.decision == "in_progress"
    assert outcome.job_state == "processing"
    assert outcome.job_created is False


def test_failed_receipt_is_reclaimed_and_enqueued(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="failed",
                attempt_count=2,
            ),
            receipt_row(
                status="processing",
                attempt_count=3,
            ),
            job_row(),
        ],
    )

    assert outcome.receipt_state == "reclaimed"
    assert outcome.receipt_attempt_count == 3
    assert outcome.decision == "enqueued"


def test_expired_receipt_is_reclaimed(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            None,
            receipt_row(
                status="processing",
                attempt_count=1,
                lease_active=False,
            ),
            receipt_row(
                status="processing",
                attempt_count=2,
            ),
            job_row(),
        ],
    )

    assert outcome.receipt_state == "reclaimed"
    assert outcome.receipt_attempt_count == 2


def test_fingerprint_conflict_rolls_back(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            None,
            receipt_row(
                fingerprint=(OTHER_FINGERPRINT),
            ),
        ],
    )

    with pytest.raises(ingress.TelegramUpdateIngressConflictError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_dead_letter_job_is_not_automatically_requeued(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            None,
            receipt_row(
                status="failed",
                attempt_count=5,
            ),
            receipt_row(
                status="processing",
                attempt_count=6,
            ),
            None,
            job_row(
                status="dead_letter",
                attempt_count=5,
            ),
        ],
    )

    with pytest.raises(ingress.TelegramUpdateIngressConsistencyError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    assert tracker.rolled_back == 1


def test_completed_job_with_pending_receipt_is_rejected(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            None,
            receipt_row(
                status="processing",
                lease_active=True,
            ),
            None,
            job_row(
                status="completed",
                attempt_count=1,
            ),
        ],
    )

    with pytest.raises(ingress.TelegramUpdateIngressConsistencyError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    assert tracker.rolled_back == 1


def test_encryption_failure_rolls_back_receipt(
    monkeypatch,
):
    _, tracker = install_transaction(
        monkeypatch,
        [
            receipt_row(),
        ],
    )

    def fail_encryption(
        *_args,
        **_kwargs,
    ):
        raise (crypto_service.TelegramUpdateJobEncryptionError("segredo interno"))

    monkeypatch.setattr(
        ingress.crypto_service,
        ("encrypt_authenticated_telegram_update"),
        fail_encryption,
    )

    with pytest.raises(ingress.TelegramUpdateIngressUnavailableError) as captured:
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    assert "segredo interno" not in str(captured.value)

    assert tracker.committed == 0
    assert tracker.rolled_back == 1


def test_database_failure_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(
        **_kwargs,
    ):
        raise RuntimeError("postgresql://user:super-secret@host/database")

        yield

    monkeypatch.setattr(
        ingress,
        "cursor_postgres",
        failing_cursor,
    )

    with pytest.raises(ingress.TelegramUpdateIngressUnavailableError) as captured:
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                keyring=KEYRING,
            )
        )

    message = str(captured.value)

    assert "super-secret" not in message
    assert "postgresql://" not in message


def test_outcome_never_exposes_sensitive_values(
    monkeypatch,
):
    outcome, _, _ = enqueue(
        monkeypatch,
        [
            receipt_row(),
            job_row(),
        ],
    )

    safe = outcome.to_safe_dict()
    representation = repr(outcome)

    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe
    assert "claim_token" not in safe
    assert "update_fingerprint" not in safe

    assert FINGERPRINT not in representation
    assert repr(KEYRING.keys) not in representation


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        "telegram",
    ],
    ids=[
        "none",
        "list",
        "string",
    ],
)
def test_invalid_update_container_is_rejected(
    value,
):
    with pytest.raises(ingress.TelegramUpdateIngressValidationError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                value,
                keyring=KEYRING,
            )
        )


@pytest.mark.parametrize(
    "value",
    [
        4,
        901,
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
def test_invalid_receipt_lease_is_rejected(
    value,
):
    with pytest.raises(ingress.TelegramUpdateIngressValidationError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                receipt_lease_seconds=value,
                keyring=KEYRING,
            )
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        21,
        True,
        "5",
    ],
    ids=[
        "zero",
        "too-high",
        "boolean",
        "string",
    ],
)
def test_invalid_max_attempts_is_rejected(
    value,
):
    with pytest.raises(ingress.TelegramUpdateIngressValidationError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                UPDATE,
                max_attempts=value,
                keyring=KEYRING,
            )
        )


def test_invalid_update_id_does_not_open_transaction(
    monkeypatch,
):
    opened = False

    @contextmanager
    def fake_cursor(
        **_kwargs,
    ):
        nonlocal opened
        opened = True
        yield FakeCursor([])

    monkeypatch.setattr(
        ingress,
        "cursor_postgres",
        fake_cursor,
    )

    with pytest.raises(ingress.TelegramUpdateIngressValidationError):
        (
            ingress.enqueue_authenticated_telegram_update_atomic(
                {
                    "update_id": "invalid",
                },
                keyring=KEYRING,
            )
        )

    assert opened is False


def test_sql_uses_row_lock_and_idempotent_insert():
    assert "FOR UPDATE" in ingress.receipt_repository.SQL_LOCK_EXISTING_RECEIPT

    assert "ON CONFLICT" in ingress.receipt_repository.SQL_INSERT_RECEIPT

    assert "ON CONFLICT" in ingress.job_repository.SQL_INSERT_JOB

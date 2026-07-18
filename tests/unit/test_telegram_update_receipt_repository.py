from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.services.telegram_update_receipts import (
    repository,
)


FINGERPRINT = "a" * 64
OTHER_FINGERPRINT = "b" * 64
CLAIM_TOKEN = "c" * 64
OTHER_CLAIM_TOKEN = "d" * 64


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


def install_cursor(
    monkeypatch,
    rows,
):
    cursor = FakeCursor(
        rows
    )

    @contextmanager
    def fake_cursor_postgres(
        *,
        dict_cursor,
        commit_automatico,
    ):
        assert dict_cursor is True

        assert (
            commit_automatico
            is True
        )

        yield cursor

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    return cursor


def test_new_update_is_claimed(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            {
                "update_id": 1001,
                "status": "processing",
                "attempt_count": 1,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
            lease_seconds=120,
        )
    )

    assert result.status == "claimed"
    assert result.should_process is True
    assert result.claim_token == CLAIM_TOKEN
    assert result.attempt_count == 1

    assert any(
        "ON CONFLICT" in sql
        for sql, _ in cursor.executions
    )


def test_completed_update_is_duplicate(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            None,
            {
                "update_id": 1001,
                "update_fingerprint": (
                    FINGERPRINT
                ),
                "claim_token": (
                    OTHER_CLAIM_TOKEN
                ),
                "status": "completed",
                "attempt_count": 1,
                "lease_active": False,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )
    )

    assert result.status == "duplicate"
    assert result.should_process is False
    assert result.claim_token is None

    assert any(
        "last_received_at = NOW()"
        in sql
        for sql, _ in cursor.executions
    )


def test_active_processing_update_is_in_progress(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
            {
                "update_id": 1001,
                "update_fingerprint": (
                    FINGERPRINT
                ),
                "claim_token": (
                    OTHER_CLAIM_TOKEN
                ),
                "status": "processing",
                "attempt_count": 1,
                "lease_active": True,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )
    )

    assert result.status == "in_progress"
    assert result.should_process is False
    assert result.claim_token is None


def test_expired_processing_update_is_reclaimed(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
            {
                "update_id": 1001,
                "update_fingerprint": (
                    FINGERPRINT
                ),
                "claim_token": (
                    OTHER_CLAIM_TOKEN
                ),
                "status": "processing",
                "attempt_count": 1,
                "lease_active": False,
            },
            {
                "update_id": 1001,
                "status": "processing",
                "attempt_count": 2,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )
    )

    assert result.status == "reclaimed"
    assert result.should_process is True
    assert result.claim_token == CLAIM_TOKEN
    assert result.attempt_count == 2


def test_failed_update_is_reclaimed(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
            {
                "update_id": 1001,
                "update_fingerprint": (
                    FINGERPRINT
                ),
                "claim_token": (
                    OTHER_CLAIM_TOKEN
                ),
                "status": "failed",
                "attempt_count": 2,
                "lease_active": False,
            },
            {
                "update_id": 1001,
                "status": "processing",
                "attempt_count": 3,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )
    )

    assert result.status == "reclaimed"
    assert result.attempt_count == 3


def test_fingerprint_conflict_is_rejected(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
            {
                "update_id": 1001,
                "update_fingerprint": (
                    OTHER_FINGERPRINT
                ),
                "claim_token": (
                    OTHER_CLAIM_TOKEN
                ),
                "status": "completed",
                "attempt_count": 1,
                "lease_active": False,
            },
        ],
    )

    with pytest.raises(
        repository
        .TelegramUpdateFingerprintConflictError
    ):
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )


def test_complete_requires_current_claim(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            None,
        ],
    )

    with pytest.raises(
        repository
        .TelegramUpdateClaimOwnershipError
    ):
        repository.complete_telegram_update(
            update_id=1001,
            claim_token=CLAIM_TOKEN,
        )


def test_complete_marks_receipt_completed(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            {
                "update_id": 1001,
                "status": "completed",
                "attempt_count": 2,
            },
        ],
    )

    result = (
        repository.complete_telegram_update(
            update_id=1001,
            claim_token=CLAIM_TOKEN,
        )
    )

    assert result.status == "completed"
    assert result.attempt_count == 2

    update_parameters = (
        cursor.executions[-1][1]
    )

    assert update_parameters[
        "claim_token"
    ] == CLAIM_TOKEN


def test_fail_marks_receipt_failed(
    monkeypatch,
):
    cursor = install_cursor(
        monkeypatch,
        [
            {
                "update_id": 1001,
                "status": "failed",
                "attempt_count": 2,
            },
        ],
    )

    result = (
        repository.fail_telegram_update(
            update_id=1001,
            claim_token=CLAIM_TOKEN,
            error_code=(
                "telegram.processing_failed"
            ),
        )
    )

    assert result.status == "failed"

    update_parameters = (
        cursor.executions[-1][1]
    )

    assert update_parameters[
        "error_code"
    ] == "telegram.processing_failed"


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        -1,
        "1001",
    ],
)
def test_invalid_update_id_is_rejected(
    value,
):
    with pytest.raises(
        ValueError
    ):
        repository.claim_telegram_update(
            update_id=value,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "short",
        "A" * 64,
        "g" * 64,
    ],
)
def test_invalid_fingerprint_is_rejected(
    value,
):
    with pytest.raises(
        ValueError
    ):
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=value,
            claim_token=CLAIM_TOKEN,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "short",
        "C" * 64,
        "x" * 64,
    ],
)
def test_invalid_claim_token_is_rejected(
    value,
):
    with pytest.raises(
        ValueError
    ):
        repository.complete_telegram_update(
            update_id=1001,
            claim_token=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        4,
        901,
        True,
        120.0,
    ],
)
def test_invalid_lease_is_rejected(
    value,
):
    with pytest.raises(
        ValueError
    ):
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
            lease_seconds=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "contains spaces",
        "UPPERCASE",
        "a" * 65,
        "error@provider",
    ],
)
def test_error_code_must_be_sanitized(
    value,
):
    with pytest.raises(
        ValueError
    ):
        repository.fail_telegram_update(
            update_id=1001,
            claim_token=CLAIM_TOKEN,
            error_code=value,
        )


def test_safe_result_never_contains_claim_token(
    monkeypatch,
):
    install_cursor(
        monkeypatch,
        [
            {
                "update_id": 1001,
                "status": "processing",
                "attempt_count": 1,
            },
        ],
    )

    result = (
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )
    )

    safe = result.to_safe_dict()

    assert "claim_token" not in safe
    assert CLAIM_TOKEN not in str(
        safe
    )


def test_database_error_is_sanitized(
    monkeypatch,
):
    @contextmanager
    def failing_cursor(
        **_kwargs,
    ):
        raise RuntimeError(
            "postgresql://user:"
            "super-secret@database/inna"
        )

        yield

    monkeypatch.setattr(
        repository,
        "cursor_postgres",
        failing_cursor,
    )

    with pytest.raises(
        repository
        .TelegramUpdateReceiptRepositoryError
    ) as captured:
        repository.claim_telegram_update(
            update_id=1001,
            update_fingerprint=(
                FINGERPRINT
            ),
            claim_token=CLAIM_TOKEN,
        )

    message = str(
        captured.value
    )

    assert "super-secret" not in message
    assert "postgresql://" not in message


def test_sql_uses_row_lock_and_claim_token():
    assert (
        "FOR UPDATE"
        in repository
        .SQL_LOCK_EXISTING_RECEIPT
    )

    assert (
        "claim_token = %(claim_token)s"
        in repository
        .SQL_COMPLETE_RECEIPT
    )

    assert (
        "claim_token = %(claim_token)s"
        in repository
        .SQL_FAIL_RECEIPT
    )

from __future__ import annotations

import re
from pathlib import Path

import pytest


UP_PATH = Path("migrations/20260718_004_create_telegram_update_jobs.sql")

DOWN_PATH = Path("migrations/20260718_004_create_telegram_update_jobs.down.sql")


def read_up() -> str:
    return UP_PATH.read_text(encoding="utf-8")


def read_down() -> str:
    return DOWN_PATH.read_text(encoding="utf-8")


def normalize(
    value: str,
) -> str:
    return " ".join(value.lower().split())


def test_migration_files_exist():
    assert UP_PATH.is_file()
    assert DOWN_PATH.is_file()


def test_up_migration_uses_transaction():
    sql = normalize(read_up())

    assert sql.startswith("begin;")

    assert sql.endswith("commit;")


def test_up_migration_uses_safe_timeouts():
    sql = normalize(read_up())

    assert "set local lock_timeout = '5s';" in sql

    assert "set local statement_timeout = '15s';" in sql


def test_table_and_required_columns_are_created():
    sql = normalize(read_up())

    assert "create table public.telegram_update_jobs" in sql

    required_columns = {
        "update_id",
        "status",
        "payload_ciphertext",
        "payload_nonce",
        "payload_key_id",
        "payload_version",
        "attempt_count",
        "max_attempts",
        "available_at",
        "locked_at",
        "lock_expires_at",
        "lock_token",
        "completed_at",
        "dead_lettered_at",
        "last_error_code",
        "created_at",
        "updated_at",
    }

    for column in required_columns:
        assert re.search(
            rf"\b{column}\b",
            sql,
        )


def test_primary_key_and_receipt_foreign_key():
    sql = normalize(read_up())

    assert "update_id bigint primary key" in sql

    assert (
        "references "
        "public.telegram_update_receipts "
        "( update_id ) on delete cascade" in sql
    )


def test_statuses_are_restricted():
    sql = normalize(read_up())

    for status in (
        "queued",
        "processing",
        "completed",
        "dead_letter",
    ):
        assert f"'{status}'" in sql

    assert "ck_telegram_update_jobs_status" in sql


def test_attempt_limits_are_restricted():
    sql = normalize(read_up())

    assert "attempt_count >= 0" in sql
    assert "max_attempts between 1 and 20" in sql
    assert "attempt_count <= max_attempts" in sql


def test_payload_is_stored_as_ciphertext():
    sql = normalize(read_up())

    assert "payload_ciphertext bytea" in sql
    assert "payload_nonce bytea" in sql

    assert "octet_length(payload_ciphertext)" in sql

    assert "1048576" in sql


def test_aes_gcm_nonce_has_twelve_bytes():
    sql = normalize(read_up())

    assert "octet_length(payload_nonce) = 12" in sql


def test_key_id_has_restricted_format():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_key_id" in sql

    assert "payload_key_id ~ '^[a-za-z0-9._:-]{1,64}$'" in sql


def test_lock_token_has_sha256_style_format():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_lock_token" in sql

    assert "lock_token ~ '^[0-9a-f]{64}$'" in sql


def test_error_code_has_restricted_format():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_error_code" in sql

    assert "last_error_code ~ '^[a-z0-9._:-]{1,64}$'" in sql


def test_payload_lifecycle_is_enforced():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_payload_lifecycle" in sql

    assert (
        "status = 'completed' "
        "and payload_ciphertext is null "
        "and payload_nonce is null "
        "and payload_key_id is null" in sql
    )


def test_worker_lock_lifecycle_is_enforced():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_lock_lifecycle" in sql

    assert (
        "status = 'processing' "
        "and locked_at is not null "
        "and lock_expires_at is not null "
        "and lock_token is not null" in sql
    )


def test_terminal_lifecycle_is_enforced():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_terminal_lifecycle" in sql

    assert (
        "status = 'completed' "
        "and completed_at is not null "
        "and dead_lettered_at is null" in sql
    )

    assert (
        "status = 'dead_letter' "
        "and completed_at is null "
        "and dead_lettered_at is not null" in sql
    )


def test_timestamp_order_is_enforced():
    sql = normalize(read_up())

    assert "ck_telegram_update_jobs_timestamp_order" in sql

    assert "updated_at >= created_at" in sql
    assert "available_at >= created_at" in sql
    assert "lock_expires_at > locked_at" in sql


@pytest.mark.parametrize(
    "index_name",
    [
        "ix_telegram_update_jobs_dequeue",
        "ix_telegram_update_jobs_processing_lease",
        "ix_telegram_update_jobs_completed_retention",
        "ix_telegram_update_jobs_dead_letter",
    ],
)
def test_required_indexes_are_created(
    index_name: str,
):
    sql = normalize(read_up())

    assert f"create index {index_name}" in sql


@pytest.mark.parametrize(
    "forbidden_column",
    [
        "chat_id",
        "user_id",
        "telegram_user_id",
        "message_text",
        "message_body",
        "update_payload",
        "raw_update",
        "payload_json",
    ],
)
def test_plaintext_or_identity_columns_are_absent(
    forbidden_column: str,
):
    sql = normalize(read_up())

    assert not re.search(
        rf"\b{forbidden_column}\b",
        sql,
    )


def test_down_migration_drops_only_jobs_table():
    sql = normalize(read_down())

    assert "drop table if exists public.telegram_update_jobs;" in sql

    assert "telegram_update_receipts" not in sql


def test_migration_does_not_drop_unrelated_objects():
    sql = normalize(read_up())

    assert "drop table" not in sql
    assert "truncate " not in sql
    assert "delete from" not in sql

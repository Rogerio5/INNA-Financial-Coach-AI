from __future__ import annotations

from pathlib import Path


UP_PATH = Path("migrations/20260718_003_create_telegram_update_receipts.sql")

DOWN_PATH = Path("migrations/20260718_003_create_telegram_update_receipts.down.sql")


def _normalized(
    path: Path,
) -> str:
    return " ".join(
        path.read_text(
            encoding="utf-8",
        )
        .lower()
        .split()
    )


def test_migration_files_exist():
    assert UP_PATH.exists()
    assert DOWN_PATH.exists()


def test_upgrade_is_transactional():
    sql = _normalized(UP_PATH)

    assert "begin;" in sql

    assert sql.endswith("commit;")


def test_upgrade_uses_operational_timeouts():
    sql = _normalized(UP_PATH)

    assert "set local lock_timeout = '5s'" in sql

    assert "set local statement_timeout = '30s'" in sql


def test_upgrade_uses_advisory_lock():
    sql = _normalized(UP_PATH)

    assert "pg_advisory_xact_lock" in sql

    assert "inna:20260718:create_telegram_update_receipts" in sql


def test_upgrade_creates_durable_receipt_table():
    sql = _normalized(UP_PATH)

    assert "create table if not exists public.telegram_update_receipts" in sql

    assert "update_id bigint primary key" in sql


def test_fingerprint_is_required_sha256():
    sql = _normalized(UP_PATH)

    assert "update_fingerprint varchar(64) not null" in sql

    assert (
        "char_length( update_fingerprint ) = 64" in sql
        or "char_length(update_fingerprint) = 64" in sql
    )

    assert "^[0-9a-f]{64}$" in sql


def test_claim_token_protects_lease_ownership():
    sql = _normalized(UP_PATH)

    assert "claim_token varchar(64) not null" in sql

    assert "ck_telegram_update_claim_token_sha256" in sql

    assert (
        "char_length( claim_token ) = 64" in sql
        or "char_length(claim_token) = 64" in sql
    )

    assert "claim_token ~ '^[0-9a-f]{64}$'" in sql


def test_lifecycle_status_is_constrained():
    sql = _normalized(UP_PATH)

    assert "status varchar(20) not null default 'processing'" in sql

    for status in (
        "'processing'",
        "'completed'",
        "'failed'",
    ):
        assert status in sql


def test_attempt_count_is_bounded():
    sql = _normalized(UP_PATH)

    assert "attempt_count integer not null default 1" in sql

    assert "between 1 and 1000000" in sql


def test_receipt_has_lease_and_lifecycle_dates():
    sql = _normalized(UP_PATH)

    required = (
        "first_received_at timestamptz",
        "last_received_at timestamptz",
        "claimed_at timestamptz",
        "lease_expires_at timestamptz",
        "completed_at timestamptz",
        "failed_at timestamptz",
    )

    for fragment in required:
        assert fragment in sql


def test_lifecycle_constraint_prevents_mixed_states():
    sql = _normalized(UP_PATH)

    assert "ck_telegram_update_lifecycle" in sql

    assert "status = 'processing'" in sql

    assert "status = 'completed'" in sql

    assert "status = 'failed'" in sql

    assert "completed_at is not null" in sql

    assert "failed_at is not null" in sql


def test_error_code_is_sanitized_by_schema():
    sql = _normalized(UP_PATH)

    assert "last_error_code varchar(64)" in sql

    assert "ck_telegram_update_error_code_format" in sql

    assert "^[a-z0-9][a-z0-9._:-]{0,63}$" in sql


def test_indexes_support_claim_and_cleanup():
    sql = _normalized(UP_PATH)

    assert "ix_telegram_update_receipts_status_lease" in sql

    assert "status, lease_expires_at, update_id" in sql

    assert "ix_telegram_update_receipts_last_received" in sql

    assert "last_received_at desc, update_id desc" in sql


def test_migration_does_not_store_sensitive_payload():
    sql = _normalized(UP_PATH)

    forbidden_columns = (
        "update_payload",
        "raw_update",
        "message_text",
        "financial_payload",
        "bot_token",
        "telegram_token",
        "email varchar",
        "nome varchar",
        "chat_id bigint",
    )

    for column in forbidden_columns:
        assert column not in sql


def test_downgrade_is_transactional_and_locked():
    sql = _normalized(DOWN_PATH)

    assert "begin;" in sql

    assert sql.endswith("commit;")

    assert "pg_advisory_xact_lock" in sql


def test_downgrade_removes_only_receipt_table():
    sql = _normalized(DOWN_PATH)

    assert "drop table if exists public.telegram_update_receipts" in sql

    assert "diagnosticos_financeiros" not in sql

    assert "drop database" not in sql

    assert "drop schema" not in sql

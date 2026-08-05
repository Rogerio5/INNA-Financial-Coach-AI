from __future__ import annotations

from pathlib import Path


UP_PATH = Path("migrations/20260718_002_add_idempotency_diagnosticos_financeiros.sql")

DOWN_PATH = Path(
    "migrations/20260718_002_add_idempotency_diagnosticos_financeiros.down.sql"
)


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


def test_upgrade_uses_transaction_and_advisory_lock():
    sql = _normalized(UP_PATH)

    assert sql.startswith("begin;")

    assert sql.endswith("commit;")

    assert "pg_advisory_xact_lock" in sql


def test_upgrade_adds_nullable_idempotency_columns():
    sql = _normalized(UP_PATH)

    assert "add column if not exists idempotency_key varchar(160)" in sql

    assert "add column if not exists request_fingerprint varchar(64)" in sql

    assert "idempotency_key varchar(160) not null" not in sql

    assert "request_fingerprint varchar(64) not null" not in sql


def test_upgrade_keeps_legacy_rows_compatible():
    sql = _normalized(UP_PATH)

    assert "idempotency_key is null and request_fingerprint is null" in sql

    assert "update public.diagnosticos_financeiros" not in sql

    assert "update diagnosticos_financeiros" not in sql


def test_idempotency_requires_trusted_user():
    sql = _normalized(UP_PATH)

    assert "usuario_id is not null" in sql

    assert "idempotency_key is not null" in sql

    assert "request_fingerprint is not null" in sql


def test_idempotency_key_has_length_and_format():
    sql = _normalized(UP_PATH)

    assert "char_length(idempotency_key) between 16 and 160" in sql

    assert "^[a-za-z0-9._:-]{16,160}$" in sql

    assert "btrim(idempotency_key) = idempotency_key" in sql


def test_fingerprint_must_be_lowercase_sha256():
    sql = _normalized(UP_PATH)

    assert (
        "char_length( request_fingerprint ) = 64" in sql
        or "char_length(request_fingerprint) = 64" in sql
    )

    assert "^[0-9a-f]{64}$" in sql


def test_upgrade_creates_partial_unique_index():
    sql = _normalized(UP_PATH)

    assert (
        "create unique index if not exists ux_diagnosticos_usuario_idempotency" in sql
    )

    assert "on public.diagnosticos_financeiros ( usuario_id, idempotency_key )" in sql

    assert "where usuario_id is not null and idempotency_key is not null" in sql


def test_upgrade_validates_constraint():
    sql = _normalized(UP_PATH)

    assert "not valid" in sql

    assert "validate constraint ck_diagnosticos_idempotency_consistencia" in sql


def test_downgrade_removes_only_new_structure():
    sql = _normalized(DOWN_PATH)

    assert sql.startswith("begin;")

    assert sql.endswith("commit;")

    assert "drop index if exists public.ux_diagnosticos_usuario_idempotency" in sql

    assert "drop constraint if exists ck_diagnosticos_idempotency_consistencia" in sql

    assert "drop column if exists request_fingerprint" in sql

    assert "drop column if exists idempotency_key" in sql

    assert "drop column if exists usuario_id" not in sql

    assert "drop table" not in sql

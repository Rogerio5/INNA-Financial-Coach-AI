from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MIGRATION_PATH = (
    ROOT / "migrations" / ("20260719_005_create_telegram_conversation_states.sql")
)


def _source() -> str:
    return MIGRATION_PATH.read_text(
        encoding="utf-8",
    )


def _normalized() -> str:
    return re.sub(
        r"\s+",
        " ",
        _source().lower(),
    ).strip()


def test_migration_file_exists():
    assert MIGRATION_PATH.is_file()


def test_migration_is_transactional():
    normalized = _normalized()

    assert normalized.startswith("begin;")

    assert normalized.endswith("commit;")

    assert "set local lock_timeout" in normalized

    assert "set local statement_timeout" in normalized


def test_creates_expected_table():
    normalized = _normalized()

    assert (
        "create table if not exists public.telegram_conversation_states" in normalized
    )


def test_has_required_columns():
    normalized = _normalized()

    required_fragments = (
        "telegram_user_id bigint not null",
        "chat_id bigint not null",
        "state jsonb not null",
        "language varchar(16)",
        "state_version bigint not null",
        "expires_at timestamptz not null",
        "created_at timestamptz not null",
        "updated_at timestamptz not null",
    )

    for fragment in required_fragments:
        assert fragment in normalized


def test_uses_composite_identity():
    normalized = _normalized()

    assert "primary key ( telegram_user_id, chat_id )" in normalized


def test_validates_trusted_identifiers():
    normalized = _normalized()

    assert "telegram_user_id > 0" in normalized

    assert "chat_id <> 0" in normalized


def test_state_must_be_json_object():
    normalized = _normalized()

    assert "jsonb_typeof(state) = 'object'" in normalized

    assert "default '{}'::jsonb" in normalized


def test_language_is_bounded_and_trimmed():
    normalized = _normalized()

    assert "language = btrim(language)" in normalized

    assert "char_length(language) between 2 and 16" in normalized


def test_state_version_supports_optimistic_locking():
    normalized = _normalized()

    assert "state_version bigint not null default 1" in normalized

    assert "state_version >= 1" in normalized


def test_timestamps_and_expiration_are_consistent():
    normalized = _normalized()

    assert "updated_at >= created_at" in normalized

    assert "expires_at > updated_at" in normalized


def test_has_cleanup_and_monitoring_indexes():
    normalized = _normalized()

    assert "idx_telegram_conversation_states_expires_at" in normalized

    assert "idx_telegram_conversation_states_updated_at" in normalized

    assert "on public.telegram_conversation_states ( expires_at )" in normalized


def test_does_not_store_raw_telegram_update():
    normalized = _normalized()

    forbidden_columns = (
        "raw_update",
        "update_payload",
        "message_text",
        "ciphertext",
        "bot_token",
        "webhook_secret",
    )

    for column in forbidden_columns:
        assert column not in normalized


def test_migration_contains_no_destructive_sql():
    normalized = _normalized()

    forbidden_statements = (
        "drop table",
        "truncate table",
        "delete from",
        "drop column",
        "grant all",
        "security definer",
    )

    for statement in forbidden_statements:
        assert statement not in normalized


def test_contract_names_are_explicit():
    normalized = _normalized()

    expected_constraints = (
        "pk_telegram_conversation_states",
        "ck_telegram_conversation_states_user_id",
        "ck_telegram_conversation_states_chat_id",
        "ck_telegram_conversation_states_state",
        "ck_telegram_conversation_states_language",
        "ck_telegram_conversation_states_version",
        "ck_telegram_conversation_states_timestamps",
        "ck_telegram_conversation_states_expiration",
    )

    for constraint_name in expected_constraints:
        assert constraint_name in normalized

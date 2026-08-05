from __future__ import annotations

from src.services.telegram_observability import (
    sanitize_error_category,
    sanitize_event_fields,
    sanitize_event_value,
)


def test_forbidden_fields_are_removed():
    sanitized = sanitize_event_fields(
        {
            "operation": "save_session",
            "chat_id": 123,
            "telegram_user_id": 456,
            "renda_mensal": 5000,
            "message_text": "segredo",
        }
    )

    assert sanitized == {
        "operation": "save_session",
    }


def test_secret_like_keys_are_removed():
    sanitized = sanitize_event_fields(
        {
            "api_token": "abc",
            "client_secret": "def",
            "database_password": "ghi",
            "outcome": "error",
        }
    )

    assert sanitized == {
        "outcome": "error",
    }


def test_database_url_is_redacted():
    sanitized = sanitize_event_value("postgresql://user:password@db/internal")

    assert sanitized == "[REDACTED_URL]"


def test_bearer_token_is_redacted():
    sanitized = sanitize_event_value("Authorization: Bearer abcdef123456")

    assert sanitized == ("Authorization: Bearer [REDACTED]")


def test_long_values_are_truncated():
    sanitized = sanitize_event_value("a" * 300)

    assert isinstance(
        sanitized,
        str,
    )

    assert sanitized.endswith("...")

    assert len(sanitized) == 203


def test_unknown_error_category_is_sanitized():
    assert sanitize_error_category("DatabaseSuperSecretError") == "unknown"


def test_bearer_token_is_redacted_case_insensitively():
    sanitized = sanitize_event_value("authorization: bearer token-ABC_123.xyz")

    assert sanitized == ("authorization: Bearer [REDACTED]")


def test_bearer_token_inside_message_is_redacted():
    sanitized = sanitize_event_value("Falha HTTP com Bearer secret-token-123 no header")

    assert sanitized == ("Falha HTTP com Bearer [REDACTED] no header")


def test_bearer_redaction_stops_before_comma():
    sanitized = sanitize_event_value("Bearer abc123, outcome=error")

    assert sanitized == ("Bearer [REDACTED], outcome=error")

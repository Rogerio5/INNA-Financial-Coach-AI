from __future__ import annotations

import math

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from src.services.telegram_conversation_state import (
    DEFAULT_STATE_TTL_SECONDS,
    MAX_CLEANUP_BATCH,
    MAX_STATE_JSON_BYTES,
    MAX_STATE_TTL_SECONDS,
    MIN_STATE_TTL_SECONDS,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateError,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_expected_version,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)


NOW = datetime(
    2026,
    7,
    19,
    12,
    0,
    tzinfo=timezone.utc,
)


def _record(
    *,
    state=None,
    language="pt-BR",
    state_version=1,
    created_at=None,
    updated_at=None,
    expires_at=None,
):
    resolved_created_at = (
        created_at
        or NOW
    )

    resolved_updated_at = (
        updated_at
        or (
            resolved_created_at
            + timedelta(
                seconds=1
            )
        )
    )

    resolved_expires_at = (
        expires_at
        or (
            resolved_updated_at
            + timedelta(
                hours=1
            )
        )
    )

    return TelegramConversationState(
        telegram_user_id=1001,
        chat_id=-2001,
        state=(
            state
            if state is not None
            else {
                "step": "language",
                "answers": [
                    1,
                    2,
                ],
            }
        ),
        language=language,
        state_version=state_version,
        created_at=resolved_created_at,
        updated_at=resolved_updated_at,
        expires_at=resolved_expires_at,
    )


def test_default_limits_are_bounded():
    assert (
        MIN_STATE_TTL_SECONDS
        == 60
    )

    assert (
        DEFAULT_STATE_TTL_SECONDS
        == 86_400
    )

    assert (
        MAX_STATE_TTL_SECONDS
        == 2_592_000
    )

    assert MAX_CLEANUP_BATCH == 1_000


def test_validates_telegram_identity():
    assert validate_telegram_identity(
        1001,
        -2001,
    ) == (
        1001,
        -2001,
    )


@pytest.mark.parametrize(
    (
        "telegram_user_id",
        "chat_id",
    ),
    [
        (
            0,
            1,
        ),
        (
            -1,
            1,
        ),
        (
            True,
            1,
        ),
        (
            "1001",
            1,
        ),
        (
            1001,
            0,
        ),
        (
            1001,
            False,
        ),
        (
            1001,
            "2001",
        ),
    ],
)
def test_rejects_invalid_identity(
    telegram_user_id,
    chat_id,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )


@pytest.mark.parametrize(
    (
        "raw_language",
        "expected",
    ),
    [
        (
            None,
            None,
        ),
        (
            "pt",
            "pt",
        ),
        (
            " pt-BR ",
            "pt-BR",
        ),
        (
            "en_US",
            "en_US",
        ),
        (
            "zh-Hant-TW",
            "zh-Hant-TW",
        ),
    ],
)
def test_normalizes_language(
    raw_language,
    expected,
):
    assert normalize_telegram_language(
        raw_language
    ) == expected


@pytest.mark.parametrize(
    "language",
    [
        "",
        "p",
        "invalid language",
        "pt@BR",
        123,
        True,
        "a" * 17,
    ],
)
def test_rejects_invalid_language(
    language,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        normalize_telegram_language(
            language
        )


def test_normalizes_state_with_defensive_copy():
    original = {
        "step": "language",
        "nested": {
            "items": [
                1,
                2,
            ],
        },
    }

    normalized = normalize_telegram_state(
        original
    )

    original["nested"]["items"].append(
        3
    )

    assert normalized == {
        "step": "language",
        "nested": {
            "items": [
                1,
                2,
            ],
        },
    }


@pytest.mark.parametrize(
    "state",
    [
        [],
        "invalid",
        100,
        None,
        {
            1: "invalid-key",
        },
        {
            "number": math.nan,
        },
        {
            "unsupported": {
                1,
                2,
            },
        },
    ],
)
def test_rejects_invalid_state(
    state,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        normalize_telegram_state(
            state
        )


def test_rejects_oversized_state():
    state = {
        "value": (
            "x"
            * MAX_STATE_JSON_BYTES
        ),
    }

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        normalize_telegram_state(
            state
        )


@pytest.mark.parametrize(
    "ttl_seconds",
    [
        MIN_STATE_TTL_SECONDS,
        DEFAULT_STATE_TTL_SECONDS,
        MAX_STATE_TTL_SECONDS,
    ],
)
def test_accepts_valid_ttl(
    ttl_seconds,
):
    assert (
        validate_state_ttl_seconds(
            ttl_seconds
        )
        == ttl_seconds
    )


@pytest.mark.parametrize(
    "ttl_seconds",
    [
        0,
        59,
        MAX_STATE_TTL_SECONDS + 1,
        True,
        60.0,
        "60",
    ],
)
def test_rejects_invalid_ttl(
    ttl_seconds,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        validate_state_ttl_seconds(
            ttl_seconds
        )


@pytest.mark.parametrize(
    "version",
    [
        1,
        2,
        100,
    ],
)
def test_accepts_expected_version(
    version,
):
    assert (
        validate_expected_version(
            version
        )
        == version
    )


@pytest.mark.parametrize(
    "version",
    [
        0,
        -1,
        True,
        1.0,
        "1",
    ],
)
def test_rejects_invalid_version(
    version,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        validate_expected_version(
            version
        )


@pytest.mark.parametrize(
    "limit",
    [
        1,
        100,
        MAX_CLEANUP_BATCH,
    ],
)
def test_accepts_cleanup_limit(
    limit,
):
    assert (
        validate_cleanup_limit(
            limit
        )
        == limit
    )


@pytest.mark.parametrize(
    "limit",
    [
        0,
        -1,
        MAX_CLEANUP_BATCH + 1,
        True,
        1.0,
        "1",
    ],
)
def test_rejects_cleanup_limit(
    limit,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        validate_cleanup_limit(
            limit
        )


def test_record_is_immutable_and_defensive():
    original = {
        "step": "language",
        "answers": [
            1,
            2,
        ],
    }

    record = _record(
        state=original
    )

    original["answers"].append(
        3
    )

    assert (
        record.to_processing_state()
        == {
            "step": "language",
            "answers": [
                1,
                2,
            ],
        }
    )

    processing_copy = (
        record.to_processing_state()
    )

    processing_copy["answers"].append(
        4
    )

    assert (
        record.to_processing_state()
        ["answers"]
        == [
            1,
            2,
        ]
    )

    with pytest.raises(
        TypeError
    ):
        record.state["step"] = (
            "changed"
        )

    with pytest.raises(
        FrozenInstanceError
    ):
        record.language = "en-US"


def test_record_repr_does_not_expose_state():
    secret_value = (
        "private-financial-message"
    )

    record = _record(
        state={
            "message": secret_value,
        }
    )

    assert secret_value not in repr(
        record
    )


def test_safe_dict_does_not_expose_state():
    secret_value = (
        "private-financial-message"
    )

    record = _record(
        state={
            "message": secret_value,
        }
    )

    safe = record.to_safe_dict()

    assert "state" not in safe

    assert secret_value not in str(
        safe
    )

    assert safe["telegram_user_id"] == 1001
    assert safe["chat_id"] == -2001
    assert safe["state_version"] == 1


def test_record_requires_timezone():
    naive = datetime(
        2026,
        7,
        19,
        12,
        0,
    )

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        _record(
            created_at=naive,
        )


def test_record_validates_timestamp_order():
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        _record(
            created_at=NOW,
            updated_at=(
                NOW
                - timedelta(
                    seconds=1
                )
            ),
        )

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        _record(
            created_at=NOW,
            updated_at=NOW,
            expires_at=NOW,
        )


def test_record_detects_expiration():
    record = _record(
        expires_at=(
            NOW
            + timedelta(
                hours=1
            )
        ),
    )

    assert record.is_expired(
        NOW
    ) is False

    assert record.is_expired(
        NOW
        + timedelta(
            hours=1
        )
    ) is True


def test_exception_hierarchy_is_explicit():
    exception_classes = (
        TelegramConversationStateValidationError,
        TelegramConversationStateConflictError,
        TelegramConversationStateConsistencyError,
        TelegramConversationStateUnavailableError,
    )

    for exception_class in exception_classes:
        assert issubclass(
            exception_class,
            TelegramConversationStateError,
        )

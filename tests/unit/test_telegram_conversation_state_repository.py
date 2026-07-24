from __future__ import annotations

import json

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

import src.services.telegram_conversation_state.repository as repository_module

from src.services.telegram_conversation_state import (
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    create_telegram_conversation_state,
    delete_expired_telegram_conversation_states,
    delete_telegram_conversation_state,
    load_telegram_conversation_state,
    save_telegram_conversation_state,
)


NOW = datetime(
    2026,
    7,
    19,
    13,
    0,
    tzinfo=timezone.utc,
)


_MISSING = object()


def _normalize_sql(
    sql: str,
) -> str:
    return " ".join(
        sql.lower().split()
    )


def _row(
    *,
    telegram_user_id=1001,
    chat_id=-2001,
    state=_MISSING,
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

    return {
        "telegram_user_id": (
            telegram_user_id
        ),
        "chat_id": chat_id,
        "state": (
            state
            if state is not _MISSING
            else {
                "step": "language",
            }
        ),
        "language": language,
        "state_version": state_version,
        "expires_at": (
            resolved_expires_at
        ),
        "created_at": (
            resolved_created_at
        ),
        "updated_at": (
            resolved_updated_at
        ),
    }


class FakeConnection:
    def __init__(
        self,
        *,
        commit_error=None,
        rollback_error=None,
    ):
        self.commit_calls = 0
        self.rollback_calls = 0
        self.commit_error = (
            commit_error
        )
        self.rollback_error = (
            rollback_error
        )

    def commit(
        self,
    ):
        self.commit_calls += 1

        if self.commit_error is not None:
            raise self.commit_error

    def rollback(
        self,
    ):
        self.rollback_calls += 1

        if self.rollback_error is not None:
            raise self.rollback_error


class FakeCursor:
    def __init__(
        self,
        *,
        fetchone_result=None,
        fetchall_result=None,
        execute_error=None,
        connection=None,
    ):
        self.connection = (
            connection
            if connection is not None
            else FakeConnection()
        )

        self.fetchone_result = (
            fetchone_result
        )

        self.fetchall_result = (
            []
            if fetchall_result is None
            else fetchall_result
        )

        self.execute_error = (
            execute_error
        )

        self.execute_calls = []

    def execute(
        self,
        sql,
        params=None,
    ):
        self.execute_calls.append(
            (
                sql,
                params,
            )
        )

        if self.execute_error is not None:
            raise self.execute_error

    def fetchone(
        self,
    ):
        return self.fetchone_result

    def fetchall(
        self,
    ):
        return self.fetchall_result


class FakeCursorContext:
    def __init__(
        self,
        cursor,
        *,
        enter_error=None,
        exit_error=None,
    ):
        self.cursor = cursor
        self.enter_error = (
            enter_error
        )
        self.exit_error = (
            exit_error
        )

    def __enter__(
        self,
    ):
        if self.enter_error is not None:
            raise self.enter_error

        return self.cursor

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        if self.exit_error is not None:
            raise self.exit_error

        return False


class FakeCursorFactory:
    def __init__(
        self,
        cursor,
        *,
        call_error=None,
        enter_error=None,
        exit_error=None,
    ):
        self.cursor = cursor
        self.call_error = (
            call_error
        )
        self.enter_error = (
            enter_error
        )
        self.exit_error = (
            exit_error
        )
        self.calls = []

    def __call__(
        self,
        **kwargs,
    ):
        self.calls.append(
            kwargs
        )

        if self.call_error is not None:
            raise self.call_error

        return FakeCursorContext(
            self.cursor,
            enter_error=(
                self.enter_error
            ),
            exit_error=(
                self.exit_error
            ),
        )


def _install_cursor(
    monkeypatch,
    cursor,
    **factory_kwargs,
):
    factory = FakeCursorFactory(
        cursor,
        **factory_kwargs,
    )

    monkeypatch.setattr(
        repository_module,
        "cursor_postgres",
        factory,
    )

    return factory


def test_load_returns_record(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=_row()
    )

    factory = _install_cursor(
        monkeypatch,
        cursor,
    )

    record = (
        load_telegram_conversation_state(
            1001,
            -2001,
        )
    )

    assert isinstance(
        record,
        TelegramConversationState,
    )

    assert (
        record.telegram_user_id
        == 1001
    )

    assert record.chat_id == -2001

    assert (
        record.to_processing_state()
        == {
            "step": "language",
        }
    )

    assert (
        cursor.connection.commit_calls
        == 0
    )

    assert (
        cursor.connection.rollback_calls
        == 1
    )

    assert factory.calls == [
        {
            "dict_cursor": True,
            "commit_automatico": False,
        }
    ]


def test_load_uses_fixed_parameterized_sql(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    result = (
        load_telegram_conversation_state(
            1001,
            -2001,
        )
    )

    assert result is None

    sql, params = (
        cursor.execute_calls[0]
    )

    assert params == (
        1001,
        -2001,
    )

    assert "telegram_user_id = %s" in sql
    assert "chat_id = %s" in sql

    assert (
        "expires_at > current_timestamp"
        in sql.lower()
    )

    assert "1001" not in sql
    assert "-2001" not in sql


def test_load_treats_missing_or_expired_as_absent(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    assert (
        load_telegram_conversation_state(
            1001,
            -2001,
        )
        is None
    )


@pytest.mark.parametrize(
    "persisted_state",
    [
        '{"step":"language"}',
        b'{"step":"language"}',
        bytearray(
            b'{"step":"language"}'
        ),
        memoryview(
            b'{"step":"language"}'
        ),
    ],
)
def test_load_deserializes_supported_json_forms(
    monkeypatch,
    persisted_state,
):
    cursor = FakeCursor(
        fetchone_result=_row(
            state=persisted_state
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    record = (
        load_telegram_conversation_state(
            1001,
            -2001,
        )
    )

    assert (
        record.to_processing_state()
        == {
            "step": "language",
        }
    )


@pytest.mark.parametrize(
    "persisted_state",
    [
        "not-json",
        b"\xff",
        [],
        None,
    ],
)
def test_load_rejects_invalid_persisted_state(
    monkeypatch,
    persisted_state,
):
    cursor = FakeCursor(
        fetchone_result=_row(
            state=persisted_state
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        load_telegram_conversation_state(
            1001,
            -2001,
        )


def test_load_rejects_incomplete_row(
    monkeypatch,
):
    invalid_row = _row()

    invalid_row.pop(
        "expires_at"
    )

    cursor = FakeCursor(
        fetchone_result=invalid_row
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        load_telegram_conversation_state(
            1001,
            -2001,
        )


@pytest.mark.parametrize(
    "row_override",
    [
        {
            "telegram_user_id": 9999,
        },
        {
            "chat_id": -9999,
        },
    ],
)
def test_load_rejects_identity_mismatch(
    monkeypatch,
    row_override,
):
    persisted_row = _row()
    persisted_row.update(
        row_override
    )

    cursor = FakeCursor(
        fetchone_result=persisted_row
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        load_telegram_conversation_state(
            1001,
            -2001,
        )


def test_create_inserts_and_commits(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=_row()
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    record = (
        create_telegram_conversation_state(
            telegram_user_id=1001,
            chat_id=-2001,
            state={
                "step": "language",
            },
            language=" pt-BR ",
            ttl_seconds=3600,
        )
    )

    assert isinstance(
        record,
        TelegramConversationState,
    )

    assert record.language == "pt-BR"

    assert (
        cursor.connection.commit_calls
        == 1
    )

    assert (
        cursor.connection.rollback_calls
        == 0
    )

    sql, params = (
        cursor.execute_calls[0]
    )

    assert params[0] == 1001
    assert params[1] == -2001

    assert json.loads(
        params[2]
    ) == {
        "step": "language",
    }

    assert params[3] == "pt-BR"
    assert params[4] == 3600

    assert "%s::jsonb" in sql


def test_create_can_revive_only_expired_state(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=_row(
            state_version=4
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    create_telegram_conversation_state(
        1001,
        -2001,
        {
            "step": "language",
        },
        "pt-BR",
        3600,
    )

    sql = (
        cursor.execute_calls[0][0]
        .lower()
    )

    assert "on conflict" in sql
    assert "do update" in sql

    assert (
        "expires_at <= current_timestamp"
        in sql
    )

    assert (
        "state_version + 1"
        in sql
    )


def test_create_active_state_raises_conflict(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateConflictError
    ):
        create_telegram_conversation_state(
            1001,
            -2001,
            {
                "step": "language",
            },
            "pt-BR",
            3600,
        )

    assert (
        cursor.connection.commit_calls
        == 0
    )

    assert (
        cursor.connection.rollback_calls
        >= 1
    )


def test_create_uses_defensive_state_copy(
    monkeypatch,
):
    source_state = {
        "nested": {
            "items": [
                1,
                2,
            ],
        },
    }

    cursor = FakeCursor(
        fetchone_result=_row(
            state=source_state
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    create_telegram_conversation_state(
        1001,
        -2001,
        source_state,
        "pt-BR",
        3600,
    )

    source_state[
        "nested"
    ]["items"].append(
        3
    )

    _, params = (
        cursor.execute_calls[0]
    )

    assert json.loads(
        params[2]
    ) == {
        "nested": {
            "items": [
                1,
                2,
            ],
        },
    }


def test_save_updates_with_optimistic_version(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=_row(
            state={
                "step": "financial_data",
            },
            language="en-US",
            state_version=2,
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    record = (
        save_telegram_conversation_state(
            telegram_user_id=1001,
            chat_id=-2001,
            state={
                "step": "financial_data",
            },
            language="en-US",
            expected_version=1,
            ttl_seconds=7200,
        )
    )

    assert record.state_version == 2
    assert record.language == "en-US"

    sql, params = (
        cursor.execute_calls[0]
    )

    assert json.loads(
        params[0]
    ) == {
        "step": "financial_data",
    }

    assert params == (
        params[0],
        "en-US",
        7200,
        1001,
        -2001,
        1,
    )

    normalized_sql = _normalize_sql(
        sql
    )

    assert (
        "state_version = state_version + 1"
        in normalized_sql
    )

    assert (
        "state_version = %s"
        in normalized_sql
    )

    assert (
        "expires_at > current_timestamp"
        in normalized_sql
    )

    assert (
        cursor.connection.commit_calls
        == 1
    )


def test_save_stale_version_raises_conflict(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateConflictError
    ):
        save_telegram_conversation_state(
            1001,
            -2001,
            {
                "step": "financial_data",
            },
            "pt-BR",
            expected_version=1,
            ttl_seconds=3600,
        )

    assert (
        cursor.connection.commit_calls
        == 0
    )

    assert (
        cursor.connection.rollback_calls
        >= 1
    )


@pytest.mark.parametrize(
    "invalid_version",
    [
        0,
        -1,
        True,
        "1",
    ],
)
def test_save_validates_version_before_database(
    monkeypatch,
    invalid_version,
):
    cursor = FakeCursor()

    factory = _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        save_telegram_conversation_state(
            1001,
            -2001,
            {},
            None,
            invalid_version,
            3600,
        )

    assert factory.calls == []


def test_delete_returns_true_and_commits(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result={
            "telegram_user_id": 1001,
        }
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    result = (
        delete_telegram_conversation_state(
            1001,
            -2001,
        )
    )

    assert result is True

    assert (
        cursor.connection.commit_calls
        == 1
    )

    sql, params = (
        cursor.execute_calls[0]
    )

    assert params == (
        1001,
        -2001,
    )

    assert (
        "delete from"
        in sql.lower()
    )


def test_delete_returns_false_when_absent(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    result = (
        delete_telegram_conversation_state(
            1001,
            -2001,
        )
    )

    assert result is False

    assert (
        cursor.connection.commit_calls
        == 1
    )


def test_cleanup_deletes_bounded_batch(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchall_result=[
            {
                "telegram_user_id": 1,
                "chat_id": 10,
            },
            {
                "telegram_user_id": 2,
                "chat_id": 20,
            },
        ]
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    deleted = (
        delete_expired_telegram_conversation_states(
            limit=100
        )
    )

    assert deleted == 2

    assert (
        cursor.connection.commit_calls
        == 1
    )

    sql, params = (
        cursor.execute_calls[0]
    )

    assert params == (
        100,
    )

    normalized_sql = _normalize_sql(
        sql
    )

    assert (
        "for update"
        in normalized_sql
    )

    assert (
        "skip locked"
        in normalized_sql
    )

    assert "limit %s" in normalized_sql

    assert (
        "expires_at <= current_timestamp"
        in normalized_sql
    )


@pytest.mark.parametrize(
    "invalid_limit",
    [
        0,
        -1,
        1001,
        True,
        "100",
    ],
)
def test_cleanup_validates_limit_before_database(
    monkeypatch,
    invalid_limit,
):
    cursor = FakeCursor()

    factory = _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        delete_expired_telegram_conversation_states(
            invalid_limit
        )

    assert factory.calls == []


@pytest.mark.parametrize(
    (
        "function_name",
        "arguments",
    ),
    [
        (
            "load",
            (
                0,
                -2001,
            ),
        ),
        (
            "create",
            (
                1001,
                0,
                {},
            ),
        ),
        (
            "save",
            (
                True,
                -2001,
                {},
                None,
                1,
            ),
        ),
        (
            "delete",
            (
                1001,
                False,
            ),
        ),
    ],
)
def test_identity_is_validated_before_database(
    monkeypatch,
    function_name,
    arguments,
):
    cursor = FakeCursor()

    factory = _install_cursor(
        monkeypatch,
        cursor,
    )

    functions = {
        "load": (
            load_telegram_conversation_state
        ),
        "create": (
            create_telegram_conversation_state
        ),
        "save": (
            save_telegram_conversation_state
        ),
        "delete": (
            delete_telegram_conversation_state
        ),
    }

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        functions[
            function_name
        ](
            *arguments
        )

    assert factory.calls == []


@pytest.mark.parametrize(
    "operation",
    [
        "load",
        "create",
        "save",
        "delete",
        "cleanup",
    ],
)
def test_database_errors_are_sanitized(
    monkeypatch,
    operation,
):
    secret = (
        "private-financial-message"
    )

    cursor = FakeCursor(
        execute_error=RuntimeError(
            secret
        )
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    calls = {
        "load": lambda: (
            load_telegram_conversation_state(
                1001,
                -2001,
            )
        ),
        "create": lambda: (
            create_telegram_conversation_state(
                1001,
                -2001,
                {
                    "secret": secret,
                },
                "pt-BR",
                3600,
            )
        ),
        "save": lambda: (
            save_telegram_conversation_state(
                1001,
                -2001,
                {
                    "secret": secret,
                },
                "pt-BR",
                1,
                3600,
            )
        ),
        "delete": lambda: (
            delete_telegram_conversation_state(
                1001,
                -2001,
            )
        ),
        "cleanup": lambda: (
            delete_expired_telegram_conversation_states(
                100
            )
        ),
    }

    with pytest.raises(
        TelegramConversationStateUnavailableError
    ) as captured:
        calls[
            operation
        ]()

    assert secret not in str(
        captured.value
    )

    assert (
        cursor.connection.rollback_calls
        >= 1
    )


def test_cursor_factory_errors_are_sanitized(
    monkeypatch,
):
    secret = "database-password"

    cursor = FakeCursor()

    _install_cursor(
        monkeypatch,
        cursor,
        call_error=RuntimeError(
            secret
        ),
    )

    with pytest.raises(
        TelegramConversationStateUnavailableError
    ) as captured:
        load_telegram_conversation_state(
            1001,
            -2001,
        )

    assert secret not in str(
        captured.value
    )


def test_commit_failure_rolls_back_and_is_sanitized(
    monkeypatch,
):
    secret = "commit-internal-error"

    connection = FakeConnection(
        commit_error=RuntimeError(
            secret
        )
    )

    cursor = FakeCursor(
        fetchone_result=_row(),
        connection=connection,
    )

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateUnavailableError
    ) as captured:
        create_telegram_conversation_state(
            1001,
            -2001,
            {},
            None,
            3600,
        )

    assert secret not in str(
        captured.value
    )

    assert connection.commit_calls == 1
    assert connection.rollback_calls >= 1


def test_missing_connection_is_unavailable(
    monkeypatch,
):
    cursor = FakeCursor(
        fetchone_result=None
    )

    cursor.connection = None

    _install_cursor(
        monkeypatch,
        cursor,
    )

    with pytest.raises(
        TelegramConversationStateUnavailableError
    ):
        load_telegram_conversation_state(
            1001,
            -2001,
        )


def test_repository_sql_contains_no_dynamic_identity():
    sql_statements = (
        repository_module._LOAD_STATE_SQL,
        repository_module._CREATE_STATE_SQL,
        repository_module._SAVE_STATE_SQL,
        repository_module._DELETE_STATE_SQL,
        repository_module._DELETE_EXPIRED_STATES_SQL,
    )

    for sql in sql_statements:
        assert "1001" not in sql
        assert "-2001" not in sql

        assert "{" not in sql
        assert "}" not in sql

        assert (
            "public.telegram_conversation_states"
            in sql
        )


def test_repository_has_no_raw_message_columns():
    combined_sql = " ".join(
        (
            repository_module._LOAD_STATE_SQL,
            repository_module._CREATE_STATE_SQL,
            repository_module._SAVE_STATE_SQL,
            repository_module._DELETE_STATE_SQL,
            repository_module._DELETE_EXPIRED_STATES_SQL,
        )
    ).lower()

    forbidden = (
        "raw_update",
        "message_text",
        "bot_token",
        "webhook_secret",
        "gemini_api_key",
    )

    for term in forbidden:
        assert term not in combined_sql

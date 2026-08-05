from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

import src.services.telegram_conversation_state.runtime as runtime_module

from src.services.telegram_conversation_state import (
    PostgresTelegramConversationStateStore,
    TelegramConversationSession,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateOpenResult,
    TelegramConversationStateRuntime,
    TelegramConversationStateStore,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    create_postgres_telegram_conversation_state_runtime,
)


NOW = datetime(
    2026,
    7,
    19,
    19,
    30,
    tzinfo=timezone.utc,
)


def _record(
    *,
    telegram_user_id=1001,
    chat_id=-2001,
    state=None,
    language="pt-BR",
    state_version=1,
):
    return TelegramConversationState(
        telegram_user_id=(telegram_user_id),
        chat_id=chat_id,
        state=(
            state
            if state is not None
            else {
                "step": "language",
            }
        ),
        language=language,
        state_version=state_version,
        created_at=NOW,
        updated_at=(NOW + timedelta(seconds=1)),
        expires_at=(NOW + timedelta(hours=1)),
    )


class FakeStore:
    def __init__(
        self,
    ):
        self.load_result = None
        self.open_result = None
        self.save_result = None
        self.delete_result = False
        self.cleanup_result = 0

        self.load_error = None
        self.open_error = None
        self.save_error = None
        self.delete_error = None
        self.cleanup_error = None

        self.load_calls = []
        self.open_calls = []
        self.save_calls = []
        self.delete_calls = []
        self.cleanup_calls = []

    def load(
        self,
        telegram_user_id,
        chat_id,
    ):
        self.load_calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        if self.load_error is not None:
            raise self.load_error

        return self.load_result

    def open(
        self,
        telegram_user_id,
        chat_id,
        initial_state,
        language=None,
        ttl_seconds=86_400,
    ):
        self.open_calls.append(
            {
                "telegram_user_id": (telegram_user_id),
                "chat_id": chat_id,
                "initial_state": initial_state,
                "language": language,
                "ttl_seconds": ttl_seconds,
            }
        )

        if self.open_error is not None:
            raise self.open_error

        return self.open_result

    def save(
        self,
        current,
        state,
        language,
        ttl_seconds=86_400,
    ):
        self.save_calls.append(
            {
                "current": current,
                "state": state,
                "language": language,
                "ttl_seconds": ttl_seconds,
            }
        )

        if self.save_error is not None:
            raise self.save_error

        return self.save_result

    def delete(
        self,
        telegram_user_id,
        chat_id,
    ):
        self.delete_calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        if self.delete_error is not None:
            raise self.delete_error

        return self.delete_result

    def cleanup_expired(
        self,
        limit=100,
    ):
        self.cleanup_calls.append(limit)

        if self.cleanup_error is not None:
            raise self.cleanup_error

        return self.cleanup_result


def _runtime(
    *,
    default_ttl_seconds=3600,
):
    store = FakeStore()

    runtime = TelegramConversationStateRuntime(
        store=store,
        default_ttl_seconds=(default_ttl_seconds),
    )

    return runtime, store


def _session(
    *,
    record=None,
    created=False,
    recovered=False,
):
    resolved_record = record if record is not None else _record()

    return TelegramConversationSession(
        current=resolved_record,
        state=(resolved_record.to_processing_state()),
        language=(resolved_record.language),
        created=created,
        recovered_from_conflict=(recovered),
    )


def test_fake_store_implements_protocol():
    store = FakeStore()

    assert isinstance(
        store,
        TelegramConversationStateStore,
    )


def test_runtime_accepts_injected_store():
    runtime, store = _runtime()

    assert runtime.store is store
    assert runtime.default_ttl_seconds == 3600


@pytest.mark.parametrize(
    "invalid_store",
    [
        None,
        {},
        object(),
        "store",
    ],
)
def test_runtime_rejects_invalid_store(
    invalid_store,
):
    with pytest.raises(TelegramConversationStateValidationError):
        TelegramConversationStateRuntime(
            store=invalid_store,
            default_ttl_seconds=3600,
        )


@pytest.mark.parametrize(
    "invalid_ttl",
    [
        0,
        59,
        True,
        "3600",
    ],
)
def test_runtime_rejects_invalid_default_ttl(
    invalid_ttl,
):
    store = FakeStore()

    with pytest.raises(TelegramConversationStateValidationError):
        TelegramConversationStateRuntime(
            store=store,
            default_ttl_seconds=invalid_ttl,
        )


def test_load_session_returns_none():
    runtime, store = _runtime()

    store.load_result = None

    result = runtime.load_session(
        1001,
        -2001,
    )

    assert result is None

    assert store.load_calls == [
        (
            1001,
            -2001,
        )
    ]


def test_load_session_returns_mutable_copy():
    runtime, store = _runtime()

    record = _record(
        state={
            "step": "language",
            "answers": [
                1,
                2,
            ],
        }
    )

    store.load_result = record

    session = runtime.load_session(
        1001,
        -2001,
    )

    assert isinstance(
        session,
        TelegramConversationSession,
    )

    session.state["answers"].append(3)

    assert record.to_processing_state()["answers"] == [
        1,
        2,
    ]

    assert session.is_dirty() is True


def test_open_session_uses_default_ttl():
    runtime, store = _runtime(default_ttl_seconds=7200)

    record = _record()

    store.open_result = TelegramConversationStateOpenResult(
        record=record,
        created=True,
    )

    session = runtime.open_session(
        telegram_user_id=1001,
        chat_id=-2001,
        initial_state={
            "step": "language",
        },
        language=" pt-BR ",
    )

    assert session.created is True

    assert session.recovered_from_conflict is False

    assert store.open_calls == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "initial_state": {
                "step": "language",
            },
            "language": "pt-BR",
            "ttl_seconds": 7200,
        }
    ]


def test_open_session_preserves_conflict_flag():
    runtime, store = _runtime()

    record = _record(state_version=4)

    store.open_result = TelegramConversationStateOpenResult(
        record=record,
        created=False,
        recovered_from_conflict=True,
    )

    session = runtime.open_session(
        1001,
        -2001,
        {
            "step": "initial",
        },
        "pt-BR",
        600,
    )

    assert session.created is False

    assert session.recovered_from_conflict is True

    assert session.state_version == 4


def test_open_rejects_invalid_store_result():
    runtime, store = _runtime()

    store.open_result = {
        "record": _record(),
    }

    with pytest.raises(TelegramConversationStateConsistencyError):
        runtime.open_session(
            1001,
            -2001,
            {},
            None,
            600,
        )


def test_session_repr_does_not_expose_state():
    secret = "private-financial-message"

    record = _record(
        state={
            "secret": secret,
        }
    )

    session = _session(record=record)

    assert secret not in repr(session)

    assert secret not in str(session.to_safe_dict())


def test_session_replace_state_is_defensive():
    session = _session()

    source = {
        "step": "financial_data",
        "items": [
            1,
            2,
        ],
    }

    session.replace_state(source)

    source["items"].append(3)

    assert session.state == {
        "step": "financial_data",
        "items": [
            1,
            2,
        ],
    }


def test_session_language_and_reset():
    session = _session()

    session.replace_state(
        {
            "step": "financial_data",
        }
    )

    session.set_language(" en-US ")

    assert session.is_dirty() is True
    assert session.language == "en-US"

    session.reset_to_persisted()

    assert session.is_dirty() is False
    assert session.language == "pt-BR"

    assert session.state == {
        "step": "language",
    }


def test_save_skips_clean_session_by_default():
    runtime, store = _runtime()

    session = _session()

    result = runtime.save_session(session)

    assert result is session
    assert store.save_calls == []


def test_save_can_force_clean_persistence():
    runtime, store = _runtime()

    current = _record(state_version=1)

    saved = _record(state_version=2)

    session = _session(record=current)

    store.save_result = saved

    result = runtime.save_session(
        session,
        ttl_seconds=600,
        only_if_changed=False,
    )

    assert result.state_version == 2

    assert len(store.save_calls) == 1


def test_save_dirty_session():
    runtime, store = _runtime()

    current = _record(state_version=3)

    saved = _record(
        state={
            "step": "financial_data",
        },
        language="en-US",
        state_version=4,
    )

    session = _session(
        record=current,
        created=True,
    )

    session.replace_state(
        {
            "step": "financial_data",
        }
    )

    session.set_language("en-US")

    store.save_result = saved

    result = runtime.save_session(
        session,
        ttl_seconds=900,
    )

    assert result.state_version == 4
    assert result.created is True
    assert result.is_dirty() is False

    assert store.save_calls == [
        {
            "current": current,
            "state": {
                "step": "financial_data",
            },
            "language": "en-US",
            "ttl_seconds": 900,
        }
    ]


@pytest.mark.parametrize(
    (
        "saved_user_id",
        "saved_chat_id",
        "saved_version",
    ),
    [
        (
            9999,
            -2001,
            2,
        ),
        (
            1001,
            -9999,
            2,
        ),
        (
            1001,
            -2001,
            1,
        ),
        (
            1001,
            -2001,
            3,
        ),
    ],
)
def test_save_rejects_invalid_returned_record(
    saved_user_id,
    saved_chat_id,
    saved_version,
):
    runtime, store = _runtime()

    current = _record(state_version=1)

    session = _session(record=current)

    session.replace_state(
        {
            "step": "changed",
        }
    )

    store.save_result = _record(
        telegram_user_id=(saved_user_id),
        chat_id=saved_chat_id,
        state={
            "step": "changed",
        },
        state_version=saved_version,
    )

    with pytest.raises(TelegramConversationStateConsistencyError):
        runtime.save_session(
            session,
            ttl_seconds=600,
        )


def test_save_conflict_propagates_without_mutating_session():
    runtime, store = _runtime()

    session = _session()

    session.replace_state(
        {
            "step": "changed",
        }
    )

    store.save_error = TelegramConversationStateConflictError("Versão divergente.")

    with pytest.raises(TelegramConversationStateConflictError):
        runtime.save_session(
            session,
            ttl_seconds=600,
        )

    assert session.state_version == 1
    assert session.deleted is False
    assert session.is_dirty() is True


def test_reload_uses_session_identity():
    runtime, store = _runtime()

    old_session = _session(record=_record(state_version=2))

    store.load_result = _record(
        state={
            "step": "reloaded",
        },
        state_version=3,
    )

    reloaded = runtime.reload_session(old_session)

    assert reloaded.state_version == 3

    assert store.load_calls == [
        (
            1001,
            -2001,
        )
    ]


def test_delete_session_marks_session_deleted():
    runtime, store = _runtime()

    store.delete_result = True

    session = _session()

    result = runtime.delete_session(session)

    assert result is True
    assert session.deleted is True

    assert store.delete_calls == [
        (
            1001,
            -2001,
        )
    ]

    with pytest.raises(TelegramConversationStateValidationError):
        session.is_dirty()

    with pytest.raises(TelegramConversationStateValidationError):
        runtime.save_session(session)


def test_delete_identity_without_loaded_session():
    runtime, store = _runtime()

    store.delete_result = False

    assert (
        runtime.delete_identity(
            1001,
            -2001,
        )
        is False
    )

    assert store.delete_calls == [
        (
            1001,
            -2001,
        )
    ]


@pytest.mark.parametrize(
    "invalid_delete_result",
    [
        None,
        0,
        1,
        "true",
    ],
)
def test_delete_rejects_invalid_store_result(
    invalid_delete_result,
):
    runtime, store = _runtime()

    store.delete_result = invalid_delete_result

    with pytest.raises(TelegramConversationStateConsistencyError):
        runtime.delete_identity(
            1001,
            -2001,
        )


def test_cleanup_expired():
    runtime, store = _runtime()

    store.cleanup_result = 3

    assert runtime.cleanup_expired(100) == 3

    assert store.cleanup_calls == [100]


@pytest.mark.parametrize(
    "invalid_cleanup_result",
    [
        -1,
        101,
        True,
        None,
        "3",
    ],
)
def test_cleanup_rejects_invalid_result(
    invalid_cleanup_result,
):
    runtime, store = _runtime()

    store.cleanup_result = invalid_cleanup_result

    with pytest.raises(TelegramConversationStateConsistencyError):
        runtime.cleanup_expired(100)


def test_database_errors_propagate_sanitized():
    runtime, store = _runtime()

    store.load_error = TelegramConversationStateUnavailableError(
        "Persistência temporariamente indisponível."
    )

    with pytest.raises(TelegramConversationStateUnavailableError) as captured:
        runtime.load_session(
            1001,
            -2001,
        )

    assert "database-password" not in str(captured.value)


def test_postgres_factory_is_lazy_and_injects_store(
    monkeypatch,
):
    calls = []

    class FakePostgresStore(FakeStore):
        def __init__(
            self,
        ):
            super().__init__()

            calls.append("created")

    monkeypatch.setattr(
        runtime_module,
        "PostgresTelegramConversationStateStore",
        FakePostgresStore,
    )

    assert calls == []

    runtime = create_postgres_telegram_conversation_state_runtime(
        default_ttl_seconds=600
    )

    assert calls == ["created"]

    assert isinstance(
        runtime.store,
        FakePostgresStore,
    )

    assert runtime.default_ttl_seconds == 600


def test_runtime_module_has_no_direct_sql_or_connection():
    source = runtime_module.__file__

    assert source is not None

    module_text = open(
        source,
        "r",
        encoding="utf-8",
    ).read()

    forbidden = (
        "cursor_postgres",
        "select ",
        "insert ",
        "update ",
        "delete from",
        "database_url",
        "psycopg",
    )

    lowered = module_text.lower()

    for term in forbidden:
        assert term not in lowered


@pytest.mark.parametrize(
    (
        "operation",
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
            "open",
            (
                1001,
                0,
                {},
            ),
        ),
        (
            "delete",
            (
                True,
                -2001,
            ),
        ),
        (
            "cleanup",
            (0,),
        ),
    ],
)
def test_validation_occurs_before_store(
    operation,
    arguments,
):
    runtime, store = _runtime()

    methods = {
        "load": runtime.load_session,
        "open": runtime.open_session,
        "delete": runtime.delete_identity,
        "cleanup": runtime.cleanup_expired,
    }

    with pytest.raises(TelegramConversationStateValidationError):
        methods[operation](*arguments)

    assert store.load_calls == []
    assert store.open_calls == []
    assert store.delete_calls == []
    assert store.cleanup_calls == []

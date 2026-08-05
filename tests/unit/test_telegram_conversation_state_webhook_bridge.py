from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

import src.services.telegram_conversation_state.webhook_bridge as bridge_module

from src.services.telegram_conversation_state import (
    TelegramConversationSession,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateRuntimePort,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    TelegramWebhookConversationBridge,
    create_postgres_telegram_webhook_conversation_bridge,
)


NOW = datetime(
    2026,
    7,
    19,
    20,
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


def _session(
    *,
    telegram_user_id=1001,
    chat_id=-2001,
    state=None,
    language="pt-BR",
    state_version=1,
    created=False,
):
    record = _record(
        telegram_user_id=(telegram_user_id),
        chat_id=chat_id,
        state=state,
        language=language,
        state_version=state_version,
    )

    return TelegramConversationSession(
        current=record,
        state=record.to_processing_state(),
        language=record.language,
        created=created,
    )


class FakeRuntime:
    def __init__(
        self,
    ):
        self.load_result = None
        self.open_result = None
        self.save_result = None
        self.reload_result = None
        self.delete_result = False
        self.delete_identity_result = False
        self.cleanup_result = 0

        self.load_error = None
        self.open_error = None
        self.save_error = None
        self.reload_error = None
        self.delete_error = None
        self.delete_identity_error = None
        self.cleanup_error = None

        self.invalidate_on_delete = True

        self.load_calls = []
        self.open_calls = []
        self.save_calls = []
        self.reload_calls = []
        self.delete_calls = []
        self.delete_identity_calls = []
        self.cleanup_calls = []

    def load_session(
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

    def open_session(
        self,
        telegram_user_id,
        chat_id,
        initial_state,
        language=None,
        ttl_seconds=None,
    ):
        self.open_calls.append(
            {
                "telegram_user_id": (telegram_user_id),
                "chat_id": chat_id,
                "initial_state": (initial_state),
                "language": language,
                "ttl_seconds": ttl_seconds,
            }
        )

        if self.open_error is not None:
            raise self.open_error

        return self.open_result

    def save_session(
        self,
        session,
        *,
        ttl_seconds=None,
        only_if_changed=True,
    ):
        self.save_calls.append(
            {
                "session": session,
                "ttl_seconds": ttl_seconds,
                "only_if_changed": (only_if_changed),
            }
        )

        if self.save_error is not None:
            raise self.save_error

        return self.save_result

    def reload_session(
        self,
        session,
    ):
        self.reload_calls.append(session)

        if self.reload_error is not None:
            raise self.reload_error

        return self.reload_result

    def delete_session(
        self,
        session,
    ):
        self.delete_calls.append(session)

        if self.delete_error is not None:
            raise self.delete_error

        if self.invalidate_on_delete:
            session.deleted = True

        return self.delete_result

    def delete_identity(
        self,
        telegram_user_id,
        chat_id,
    ):
        self.delete_identity_calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        if self.delete_identity_error is not None:
            raise self.delete_identity_error

        return self.delete_identity_result

    def cleanup_expired(
        self,
        limit=100,
    ):
        self.cleanup_calls.append(limit)

        if self.cleanup_error is not None:
            raise self.cleanup_error

        return self.cleanup_result


def _bridge(
    *,
    runtime=None,
    default_language="pt-BR",
):
    resolved_runtime = runtime if runtime is not None else FakeRuntime()

    calls = []

    def factory():
        calls.append("created")

        return resolved_runtime

    bridge = TelegramWebhookConversationBridge(
        runtime_factory=factory,
        default_language=(default_language),
    )

    return (
        bridge,
        resolved_runtime,
        calls,
    )


def test_fake_runtime_implements_port():
    runtime = FakeRuntime()

    assert isinstance(
        runtime,
        TelegramConversationStateRuntimePort,
    )


def test_bridge_is_lazy_and_creates_runtime_once():
    bridge, runtime, calls = _bridge()

    assert bridge.runtime_initialized is False
    assert calls == []

    runtime.load_result = None

    assert (
        bridge.load_session(
            1001,
            -2001,
        )
        is None
    )

    assert bridge.runtime_initialized is True

    assert (
        bridge.load_session(
            1001,
            -2001,
        )
        is None
    )

    assert calls == [
        "created",
    ]


@pytest.mark.parametrize(
    "invalid_factory",
    [
        None,
        {},
        object(),
        "factory",
    ],
)
def test_bridge_rejects_invalid_factory(
    invalid_factory,
):
    with pytest.raises(TelegramConversationStateValidationError):
        TelegramWebhookConversationBridge(
            runtime_factory=invalid_factory,
        )


def test_bridge_normalizes_default_language():
    bridge, _, _ = _bridge(default_language=" pt-BR ")

    assert bridge.default_language == "pt-BR"


@pytest.mark.parametrize(
    "invalid_language",
    [
        None,
        "",
        " ",
    ],
)
def test_bridge_rejects_invalid_default_language(
    invalid_language,
):
    with pytest.raises(TelegramConversationStateValidationError):
        TelegramWebhookConversationBridge(
            runtime_factory=FakeRuntime,
            default_language=invalid_language,
        )


def test_factory_invalid_runtime_is_rejected():
    bridge = TelegramWebhookConversationBridge(
        runtime_factory=lambda: object(),
    )

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.load_session(
            1001,
            -2001,
        )


def test_factory_unexpected_error_is_sanitized():
    secret = "database-password"

    def broken_factory():
        raise RuntimeError(secret)

    bridge = TelegramWebhookConversationBridge(
        runtime_factory=broken_factory,
    )

    with pytest.raises(TelegramConversationStateUnavailableError) as captured:
        bridge.load_session(
            1001,
            -2001,
        )

    assert secret not in str(captured.value)


def test_load_session_returns_none():
    bridge, runtime, _ = _bridge()

    runtime.load_result = None

    assert (
        bridge.load_session(
            1001,
            -2001,
        )
        is None
    )

    assert runtime.load_calls == [
        (
            1001,
            -2001,
        )
    ]


def test_load_session_returns_valid_session():
    bridge, runtime, _ = _bridge()

    expected = _session()

    runtime.load_result = expected

    result = bridge.load_session(
        1001,
        -2001,
    )

    assert result is expected


@pytest.mark.parametrize(
    (
        "returned_user_id",
        "returned_chat_id",
    ),
    [
        (
            9999,
            -2001,
        ),
        (
            1001,
            -9999,
        ),
    ],
)
def test_load_rejects_identity_change(
    returned_user_id,
    returned_chat_id,
):
    bridge, runtime, _ = _bridge()

    runtime.load_result = _session(
        telegram_user_id=(returned_user_id),
        chat_id=returned_chat_id,
    )

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.load_session(
            1001,
            -2001,
        )


def test_open_normalizes_and_delegates():
    bridge, runtime, _ = _bridge()

    expected = _session(
        state={
            "step": "language",
            "items": [
                1,
                2,
            ],
        },
        created=True,
    )

    runtime.open_result = expected

    source_state = {
        "step": "language",
        "items": [
            1,
            2,
        ],
    }

    result = bridge.open_session(
        telegram_user_id=1001,
        chat_id=-2001,
        initial_state=source_state,
        language=" pt-BR ",
        ttl_seconds=600,
    )

    source_state["items"].append(3)

    assert result is expected

    assert runtime.open_calls == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "initial_state": {
                "step": "language",
                "items": [
                    1,
                    2,
                ],
            },
            "language": "pt-BR",
            "ttl_seconds": 600,
        }
    ]


def test_load_or_open_returns_existing_without_open():
    bridge, runtime, _ = _bridge()

    existing = _session(state_version=3)

    runtime.load_result = existing

    result = bridge.load_or_open_session(
        1001,
        -2001,
        {
            "step": "new",
        },
        "pt-BR",
        600,
    )

    assert result is existing
    assert runtime.open_calls == []


def test_load_or_open_opens_when_absent():
    bridge, runtime, _ = _bridge()

    opened = _session(created=True)

    runtime.load_result = None
    runtime.open_result = opened

    result = bridge.load_or_open_session(
        1001,
        -2001,
        {
            "step": "language",
        },
        "pt-BR",
        600,
    )

    assert result is opened

    assert len(runtime.load_calls) == 1

    assert len(runtime.open_calls) == 1


def test_save_delegates_without_hidden_retry():
    bridge, runtime, _ = _bridge()

    current = _session(state_version=1)

    saved = _session(state_version=2)

    runtime.save_result = saved

    result = bridge.save_session(
        current,
        ttl_seconds=600,
        only_if_changed=False,
    )

    assert result is saved

    assert runtime.save_calls == [
        {
            "session": current,
            "ttl_seconds": 600,
            "only_if_changed": False,
        }
    ]


def test_save_conflict_propagates_once():
    bridge, runtime, _ = _bridge()

    current = _session()

    runtime.save_error = TelegramConversationStateConflictError("Versão divergente.")

    with pytest.raises(TelegramConversationStateConflictError):
        bridge.save_session(
            current,
            ttl_seconds=600,
        )

    assert len(runtime.save_calls) == 1

    assert runtime.reload_calls == []


def test_save_rejects_identity_change():
    bridge, runtime, _ = _bridge()

    current = _session()

    runtime.save_result = _session(
        telegram_user_id=9999,
        chat_id=-2001,
        state_version=2,
    )

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.save_session(
            current,
            ttl_seconds=600,
        )


def test_unexpected_runtime_error_is_sanitized():
    bridge, runtime, _ = _bridge()

    secret = "postgres-secret"

    runtime.load_error = RuntimeError(secret)

    with pytest.raises(TelegramConversationStateUnavailableError) as captured:
        bridge.load_session(
            1001,
            -2001,
        )

    assert secret not in str(captured.value)


def test_reload_session():
    bridge, runtime, _ = _bridge()

    current = _session(state_version=2)

    reloaded = _session(state_version=3)

    runtime.reload_result = reloaded

    result = bridge.reload_session(current)

    assert result is reloaded

    assert runtime.reload_calls == [current]


def test_reload_can_return_none():
    bridge, runtime, _ = _bridge()

    current = _session()

    runtime.reload_result = None

    assert bridge.reload_session(current) is None


def test_delete_session_requires_runtime_invalidation():
    bridge, runtime, _ = _bridge()

    current = _session()

    runtime.delete_result = True
    runtime.invalidate_on_delete = False

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.delete_session(current)


def test_delete_session():
    bridge, runtime, _ = _bridge()

    current = _session()

    runtime.delete_result = True

    result = bridge.delete_session(current)

    assert result is True
    assert current.deleted is True

    assert runtime.delete_calls == [current]


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        0,
        1,
        "true",
    ],
)
def test_delete_identity_rejects_invalid_result(
    invalid_result,
):
    bridge, runtime, _ = _bridge()

    runtime.delete_identity_result = invalid_result

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.delete_identity(
            1001,
            -2001,
        )


def test_delete_identity():
    bridge, runtime, _ = _bridge()

    runtime.delete_identity_result = False

    assert (
        bridge.delete_identity(
            1001,
            -2001,
        )
        is False
    )

    assert runtime.delete_identity_calls == [
        (
            1001,
            -2001,
        )
    ]


def test_resolve_language_uses_persisted_language():
    bridge, runtime, _ = _bridge()

    runtime.load_result = _session(language="en-US")

    assert (
        bridge.resolve_language(
            1001,
            -2001,
        )
        == "en-US"
    )


def test_resolve_language_uses_default_when_absent():
    bridge, runtime, _ = _bridge(default_language="pt-BR")

    runtime.load_result = None

    assert (
        bridge.resolve_language(
            1001,
            -2001,
        )
        == "pt-BR"
    )


def test_resolve_language_uses_explicit_fallback():
    bridge, runtime, _ = _bridge()

    runtime.load_result = _session(language=None)

    assert (
        bridge.resolve_language(
            1001,
            -2001,
            fallback_language=" es ",
        )
        == "es"
    )


def test_cleanup_expired():
    bridge, runtime, _ = _bridge()

    runtime.cleanup_result = 3

    assert bridge.cleanup_expired(100) == 3

    assert runtime.cleanup_calls == [100]


@pytest.mark.parametrize(
    "invalid_result",
    [
        -1,
        101,
        True,
        None,
        "3",
    ],
)
def test_cleanup_rejects_invalid_result(
    invalid_result,
):
    bridge, runtime, _ = _bridge()

    runtime.cleanup_result = invalid_result

    with pytest.raises(TelegramConversationStateConsistencyError):
        bridge.cleanup_expired(100)


def test_bridge_repr_and_safe_dict_are_safe():
    secret = "private-financial-state"

    runtime = FakeRuntime()

    def factory():
        if secret:
            return runtime

        raise AssertionError

    bridge = TelegramWebhookConversationBridge(
        runtime_factory=factory,
    )

    assert secret not in repr(bridge)

    assert secret not in str(bridge.to_safe_dict())


def test_postgres_bridge_factory_is_lazy(
    monkeypatch,
):
    calls = []

    fake_runtime = FakeRuntime()
    fake_runtime.load_result = None

    def fake_runtime_factory(
        *,
        default_ttl_seconds,
    ):
        calls.append(default_ttl_seconds)

        return fake_runtime

    monkeypatch.setattr(
        bridge_module,
        "create_postgres_telegram_conversation_state_runtime",
        fake_runtime_factory,
    )

    bridge = create_postgres_telegram_webhook_conversation_bridge(
        default_ttl_seconds=600,
        default_language="pt-BR",
    )

    assert calls == []
    assert bridge.runtime_initialized is False

    assert (
        bridge.load_session(
            1001,
            -2001,
        )
        is None
    )

    assert calls == [600]

    assert bridge.runtime_initialized is True


def test_bridge_module_has_no_sql_or_memory_fallback():
    module_path = bridge_module.__file__

    assert module_path is not None

    source = open(
        module_path,
        "r",
        encoding="utf-8",
    ).read()

    lowered = source.lower()

    forbidden = (
        "cursor_postgres",
        "psycopg",
        "database_url",
        "select ",
        "insert ",
        "delete from",
        "user_sessions",
        "user_last_lang",
    )

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
            "open",
            (
                1001,
                -2001,
                [],
            ),
        ),
        (
            "save",
            (object(),),
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
def test_validation_happens_before_runtime_creation(
    operation,
    arguments,
):
    bridge, runtime, calls = _bridge()

    methods = {
        "load": bridge.load_session,
        "open": bridge.open_session,
        "save": bridge.save_session,
        "delete": bridge.delete_identity,
        "cleanup": bridge.cleanup_expired,
    }

    with pytest.raises(TelegramConversationStateValidationError):
        methods[operation](*arguments)

    assert calls == []
    assert runtime.load_calls == []
    assert runtime.open_calls == []
    assert runtime.save_calls == []
    assert runtime.delete_identity_calls == []
    assert runtime.cleanup_calls == []

from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

import src.services.telegram_conversation_state.store as store_module

from src.services.telegram_conversation_state import (
    PostgresTelegramConversationStateStore,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateOpenResult,
    TelegramConversationStateStore,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
)


NOW = datetime(
    2026,
    7,
    19,
    18,
    0,
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
        telegram_user_id=(
            telegram_user_id
        ),
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
        updated_at=(
            NOW
            + timedelta(
                seconds=1
            )
        ),
        expires_at=(
            NOW
            + timedelta(
                hours=1
            )
        ),
    )


def test_postgres_store_implements_protocol():
    store = (
        PostgresTelegramConversationStateStore()
    )

    assert isinstance(
        store,
        TelegramConversationStateStore,
    )


def test_load_delegates_to_repository(
    monkeypatch,
):
    calls = []

    expected = _record()

    def fake_load(
        telegram_user_id,
        chat_id,
    ):
        calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        return expected

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        fake_load,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    result = store.load(
        1001,
        -2001,
    )

    assert result is expected

    assert calls == [
        (
            1001,
            -2001,
        )
    ]


def test_load_returns_none_when_absent(
    monkeypatch,
):
    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        lambda *_: None,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    assert store.load(
        1001,
        -2001,
    ) is None


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
def test_load_rejects_repository_identity_mismatch(
    monkeypatch,
    returned_user_id,
    returned_chat_id,
):
    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        lambda *_: _record(
            telegram_user_id=(
                returned_user_id
            ),
            chat_id=returned_chat_id,
        ),
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        store.load(
            1001,
            -2001,
        )


def test_open_returns_existing_without_create(
    monkeypatch,
):
    existing = _record(
        state_version=4
    )

    create_calls = []

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        lambda *_: existing,
    )

    def fake_create(
        **kwargs,
    ):
        create_calls.append(
            kwargs
        )

        raise AssertionError(
            "create não deveria ser chamado"
        )

    monkeypatch.setattr(
        store_module,
        "create_telegram_conversation_state",
        fake_create,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    result = store.open(
        telegram_user_id=1001,
        chat_id=-2001,
        initial_state={
            "step": "initial",
        },
        language="pt-BR",
        ttl_seconds=600,
    )

    assert result.record is existing
    assert result.created is False

    assert (
        result.recovered_from_conflict
        is False
    )

    assert create_calls == []


def test_open_creates_when_absent(
    monkeypatch,
):
    calls = {
        "load": 0,
        "create": [],
    }

    created = _record()

    def fake_load(
        *_,
    ):
        calls["load"] += 1
        return None

    def fake_create(
        **kwargs,
    ):
        calls["create"].append(
            kwargs
        )

        return created

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        fake_load,
    )

    monkeypatch.setattr(
        store_module,
        "create_telegram_conversation_state",
        fake_create,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    source_state = {
        "step": "language",
        "nested": {
            "items": [
                1,
                2,
            ],
        },
    }

    result = store.open(
        telegram_user_id=1001,
        chat_id=-2001,
        initial_state=source_state,
        language=" pt-BR ",
        ttl_seconds=600,
    )

    source_state[
        "nested"
    ]["items"].append(
        3
    )

    assert result.record is created
    assert result.created is True

    assert (
        result.recovered_from_conflict
        is False
    )

    assert calls["load"] == 1

    assert calls["create"] == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "state": {
                "step": "language",
                "nested": {
                    "items": [
                        1,
                        2,
                    ],
                },
            },
            "language": "pt-BR",
            "ttl_seconds": 600,
        }
    ]


def test_open_recovers_single_concurrent_create(
    monkeypatch,
):
    recovered = _record(
        state_version=3
    )

    load_results = iter(
        [
            None,
            recovered,
        ]
    )

    load_calls = []
    create_calls = []

    def fake_load(
        telegram_user_id,
        chat_id,
    ):
        load_calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        return next(
            load_results
        )

    def fake_create(
        **kwargs,
    ):
        create_calls.append(
            kwargs
        )

        raise TelegramConversationStateConflictError(
            "Estado ativo já existe."
        )

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        fake_load,
    )

    monkeypatch.setattr(
        store_module,
        "create_telegram_conversation_state",
        fake_create,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    result = store.open(
        1001,
        -2001,
        {
            "step": "language",
        },
        "pt-BR",
        600,
    )

    assert result.record is recovered
    assert result.created is False

    assert (
        result.recovered_from_conflict
        is True
    )

    assert len(
        load_calls
    ) == 2

    assert len(
        create_calls
    ) == 1


def test_open_does_not_loop_when_conflict_cannot_be_recovered(
    monkeypatch,
):
    load_calls = []
    create_calls = []

    def fake_load(
        *_,
    ):
        load_calls.append(
            True
        )

        return None

    def fake_create(
        **kwargs,
    ):
        create_calls.append(
            kwargs
        )

        raise TelegramConversationStateConflictError(
            "Conflito."
        )

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        fake_load,
    )

    monkeypatch.setattr(
        store_module,
        "create_telegram_conversation_state",
        fake_create,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConflictError
    ):
        store.open(
            1001,
            -2001,
            {},
            None,
            600,
        )

    assert len(
        load_calls
    ) == 2

    assert len(
        create_calls
    ) == 1


def test_open_result_repr_and_safe_dict_do_not_expose_state():
    secret = (
        "private-financial-message"
    )

    result = (
        TelegramConversationStateOpenResult(
            record=_record(
                state={
                    "secret": secret,
                }
            ),
            created=True,
        )
    )

    assert secret not in repr(
        result
    )

    safe = result.to_safe_dict()

    assert secret not in str(
        safe
    )

    assert "state" not in safe[
        "record"
    ]


@pytest.mark.parametrize(
    (
        "created",
        "recovered",
    ),
    [
        (
            True,
            True,
        ),
        (
            1,
            False,
        ),
        (
            False,
            0,
        ),
    ],
)
def test_open_result_rejects_invalid_flags(
    created,
    recovered,
):
    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        TelegramConversationStateOpenResult(
            record=_record(),
            created=created,
            recovered_from_conflict=(
                recovered
            ),
        )


def test_save_uses_identity_and_version_from_current_record(
    monkeypatch,
):
    current = _record(
        state_version=7
    )

    expected = _record(
        state={
            "step": "financial_data",
        },
        language="en-US",
        state_version=8,
    )

    calls = []

    def fake_save(
        **kwargs,
    ):
        calls.append(
            kwargs
        )

        return expected

    monkeypatch.setattr(
        store_module,
        "save_telegram_conversation_state",
        fake_save,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    state = {
        "step": "financial_data",
    }

    saved = store.save(
        current=current,
        state=state,
        language=" en-US ",
        ttl_seconds=900,
    )

    assert saved is expected

    assert calls == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "state": {
                "step": "financial_data",
            },
            "language": "en-US",
            "expected_version": 7,
            "ttl_seconds": 900,
        }
    ]


def test_save_rejects_invalid_current_before_repository(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        store_module,
        "save_telegram_conversation_state",
        lambda **kwargs: calls.append(
            kwargs
        ),
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        store.save(
            current={
                "state_version": 1,
            },
            state={},
            language=None,
            ttl_seconds=600,
        )

    assert calls == []


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
def test_save_rejects_identity_change(
    monkeypatch,
    returned_user_id,
    returned_chat_id,
):
    current = _record(
        state_version=1
    )

    monkeypatch.setattr(
        store_module,
        "save_telegram_conversation_state",
        lambda **_: _record(
            telegram_user_id=(
                returned_user_id
            ),
            chat_id=returned_chat_id,
            state_version=2,
        ),
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        store.save(
            current,
            {},
            None,
            600,
        )


@pytest.mark.parametrize(
    "returned_version",
    [
        1,
        3,
        100,
    ],
)
def test_save_requires_exact_next_version(
    monkeypatch,
    returned_version,
):
    current = _record(
        state_version=1
    )

    monkeypatch.setattr(
        store_module,
        "save_telegram_conversation_state",
        lambda **_: _record(
            state_version=(
                returned_version
            )
        ),
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        store.save(
            current,
            {},
            None,
            600,
        )


def test_delete_delegates_to_repository(
    monkeypatch,
):
    calls = []

    def fake_delete(
        telegram_user_id,
        chat_id,
    ):
        calls.append(
            (
                telegram_user_id,
                chat_id,
            )
        )

        return True

    monkeypatch.setattr(
        store_module,
        "delete_telegram_conversation_state",
        fake_delete,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    assert store.delete(
        1001,
        -2001,
    ) is True

    assert calls == [
        (
            1001,
            -2001,
        )
    ]


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        0,
        1,
        "true",
    ],
)
def test_delete_rejects_invalid_repository_result(
    monkeypatch,
    invalid_result,
):
    monkeypatch.setattr(
        store_module,
        "delete_telegram_conversation_state",
        lambda *_: invalid_result,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        store.delete(
            1001,
            -2001,
        )


def test_cleanup_delegates_bounded_limit(
    monkeypatch,
):
    calls = []

    def fake_cleanup(
        limit,
    ):
        calls.append(
            limit
        )

        return 3

    monkeypatch.setattr(
        store_module,
        "delete_expired_telegram_conversation_states",
        fake_cleanup,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    assert store.cleanup_expired(
        100
    ) == 3

    assert calls == [
        100
    ]


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
def test_cleanup_rejects_invalid_repository_result(
    monkeypatch,
    invalid_result,
):
    monkeypatch.setattr(
        store_module,
        "delete_expired_telegram_conversation_states",
        lambda *_: invalid_result,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateConsistencyError
    ):
        store.cleanup_expired(
            100
        )


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
                None,
                600,
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
            (
                0,
            ),
        ),
    ],
)
def test_validation_happens_before_repository(
    monkeypatch,
    operation,
    arguments,
):
    calls = []

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        lambda *_: calls.append(
            "load"
        ),
    )

    monkeypatch.setattr(
        store_module,
        "create_telegram_conversation_state",
        lambda **_: calls.append(
            "create"
        ),
    )

    monkeypatch.setattr(
        store_module,
        "delete_telegram_conversation_state",
        lambda *_: calls.append(
            "delete"
        ),
    )

    monkeypatch.setattr(
        store_module,
        "delete_expired_telegram_conversation_states",
        lambda *_: calls.append(
            "cleanup"
        ),
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    methods = {
        "load": store.load,
        "open": store.open,
        "delete": store.delete,
        "cleanup": store.cleanup_expired,
    }

    with pytest.raises(
        TelegramConversationStateValidationError
    ):
        methods[
            operation
        ](
            *arguments
        )

    assert calls == []


def test_repository_unavailable_error_propagates_safely(
    monkeypatch,
):
    secret = "database-password"

    def unavailable(
        *_,
        **__,
    ):
        raise TelegramConversationStateUnavailableError(
            "Persistência temporariamente indisponível."
        )

    monkeypatch.setattr(
        store_module,
        "load_telegram_conversation_state",
        unavailable,
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    with pytest.raises(
        TelegramConversationStateUnavailableError
    ) as captured:
        store.load(
            1001,
            -2001,
        )

    assert secret not in str(
        captured.value
    )

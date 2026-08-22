from __future__ import annotations

import pytest

from api import telegram_webhook


class FakeConflictError(Exception):
    pass


class FakeSession:
    def __init__(
        self,
        name,
    ):
        self.name = name
        self.state = {}
        self.language = None
        self.replace_calls = []
        self.language_calls = []

    def replace_state(
        self,
        state,
    ):
        self.state = dict(state)
        self.replace_calls.append(
            dict(state)
        )

    def set_language(
        self,
        language,
    ):
        self.language = language
        self.language_calls.append(
            language
        )


def test_conflict_reloads_reapplies_and_saves_once_more(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "TelegramConversationStateConflictError",
        FakeConflictError,
    )

    original = FakeSession(
        "original"
    )

    reloaded = FakeSession(
        "reloaded"
    )

    class Bridge:
        def __init__(self):
            self.save_calls = []
            self.reload_calls = []

        def save_session(
            self,
            session,
            *,
            only_if_changed=True,
        ):
            self.save_calls.append(
                session
            )

            if len(self.save_calls) == 1:
                raise FakeConflictError(
                    "version conflict"
                )

            return session

        def reload_session(
            self,
            session,
        ):
            self.reload_calls.append(
                session
            )
            return reloaded

    bridge = Bridge()

    state = {
        "step": "renda",
        "lang": "pt",
        "nome": "Rogerio",
    }

    result = (
        telegram_webhook
        ._sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=original,
            processing_state=state,
            language="pt",
        )
    )

    assert result is reloaded

    assert bridge.save_calls == [
        original,
        reloaded,
    ]

    assert bridge.reload_calls == [
        original
    ]

    assert reloaded.state == state
    assert reloaded.language == "pt"


def test_second_conflict_is_propagated(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "TelegramConversationStateConflictError",
        FakeConflictError,
    )

    original = FakeSession(
        "original"
    )

    reloaded = FakeSession(
        "reloaded"
    )

    class Bridge:
        def __init__(self):
            self.save_count = 0
            self.reload_count = 0

        def save_session(
            self,
            session,
            *,
            only_if_changed=True,
        ):
            self.save_count += 1

            raise FakeConflictError(
                f"conflict-{self.save_count}"
            )

        def reload_session(
            self,
            session,
        ):
            self.reload_count += 1
            return reloaded

    bridge = Bridge()

    with pytest.raises(
        FakeConflictError,
        match="conflict-2",
    ):
        (
            telegram_webhook
            ._sync_and_save_durable_telegram_session(
                conversation_bridge=bridge,
                durable_session=original,
                processing_state={
                    "step": "nome",
                    "lang": "pt",
                },
            )
        )

    assert bridge.save_count == 2
    assert bridge.reload_count == 1


def test_reload_none_propagates_original_conflict(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "TelegramConversationStateConflictError",
        FakeConflictError,
    )

    original = FakeSession(
        "original"
    )

    class Bridge:
        def save_session(
            self,
            session,
            *,
            only_if_changed=True,
        ):
            raise FakeConflictError(
                "original conflict"
            )

        def reload_session(
            self,
            session,
        ):
            return None

    with pytest.raises(
        FakeConflictError,
        match="original conflict",
    ):
        (
            telegram_webhook
            ._sync_and_save_durable_telegram_session(
                conversation_bridge=Bridge(),
                durable_session=original,
                processing_state={
                    "step": "nome",
                    "lang": "pt",
                },
            )
        )


def test_non_conflict_failure_is_not_retried(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "TelegramConversationStateConflictError",
        FakeConflictError,
    )

    original = FakeSession(
        "original"
    )

    class Bridge:
        def __init__(self):
            self.save_count = 0
            self.reload_count = 0

        def save_session(
            self,
            session,
            *,
            only_if_changed=True,
        ):
            self.save_count += 1

            raise RuntimeError(
                "database unavailable"
            )

        def reload_session(
            self,
            session,
        ):
            self.reload_count += 1
            return None

    bridge = Bridge()

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        (
            telegram_webhook
            ._sync_and_save_durable_telegram_session(
                conversation_bridge=bridge,
                durable_session=original,
                processing_state={
                    "step": "nome",
                    "lang": "pt",
                },
            )
        )

    assert bridge.save_count == 1
    assert bridge.reload_count == 0


def test_success_does_not_reload(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "TelegramConversationStateConflictError",
        FakeConflictError,
    )

    original = FakeSession(
        "original"
    )

    class Bridge:
        def __init__(self):
            self.save_count = 0
            self.reload_count = 0

        def save_session(
            self,
            session,
            *,
            only_if_changed=True,
        ):
            self.save_count += 1
            return session

        def reload_session(
            self,
            session,
        ):
            self.reload_count += 1
            return session

    bridge = Bridge()

    result = (
        telegram_webhook
        ._sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=original,
            processing_state={
                "step": "nome",
                "lang": "pt",
            },
        )
    )

    assert result is original
    assert bridge.save_count == 1
    assert bridge.reload_count == 0

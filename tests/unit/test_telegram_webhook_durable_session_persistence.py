from __future__ import annotations

import pytest

from api import telegram_webhook


class FakeDurableSession:
    def __init__(
        self,
        state=None,
        language=None,
    ):
        self.state = dict(state or {})
        self.language = language
        self.replace_calls = []
        self.language_calls = []

    def replace_state(
        self,
        state,
    ):
        self.replace_calls.append(dict(state))
        self.state = dict(state)

    def set_language(
        self,
        language,
    ):
        self.language_calls.append(language)
        self.language = language


class FakeBridge:
    def __init__(self):
        self.saved = []
        self.deleted = []
        self.save_result = object()
        self.delete_result = True

    def save_session(
        self,
        session,
        *,
        ttl_seconds=None,
        only_if_changed=True,
    ):
        self.saved.append(
            {
                "session": session,
                "ttl_seconds": ttl_seconds,
                "only_if_changed": (only_if_changed),
            }
        )

        return self.save_result

    def delete_session(
        self,
        session,
    ):
        self.deleted.append(session)
        return self.delete_result


def test_sync_replaces_state_sets_language_and_saves():
    bridge = FakeBridge()

    session = FakeDurableSession(
        {
            "step": "nome",
            "lang": "pt",
        },
        language="pt",
    )

    state = {
        "step": "renda",
        "lang": "es",
        "nome": "Rogerio",
    }

    result = telegram_webhook._sync_and_save_durable_telegram_session(
        conversation_bridge=bridge,
        durable_session=session,
        processing_state=state,
        language="es",
    )

    assert result is bridge.save_result

    assert session.replace_calls == [state]

    assert session.language_calls == ["es"]

    assert bridge.saved == [
        {
            "session": session,
            "ttl_seconds": None,
            "only_if_changed": True,
        }
    ]


def test_sync_uses_language_from_processing_state():
    bridge = FakeBridge()
    session = FakeDurableSession()

    state = {
        "step": "nome",
        "lang": "en_us",
    }

    (
        telegram_webhook._sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=session,
            processing_state=state,
        )
    )

    assert session.language == "en_us"


def test_sync_allows_language_absent():
    bridge = FakeBridge()
    session = FakeDurableSession()

    (
        telegram_webhook._sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=session,
            processing_state={
                "step": "idioma",
            },
        )
    )

    assert session.language is None


def test_sync_rejects_missing_bridge():
    with pytest.raises(
        ValueError,
        match="conversation_bridge é obrigatória",
    ):
        (
            telegram_webhook._sync_and_save_durable_telegram_session(
                conversation_bridge=None,
                durable_session=FakeDurableSession(),
                processing_state={},
            )
        )


def test_sync_rejects_missing_session():
    with pytest.raises(
        ValueError,
        match="durable_session é obrigatória",
    ):
        (
            telegram_webhook._sync_and_save_durable_telegram_session(
                conversation_bridge=FakeBridge(),
                durable_session=None,
                processing_state={},
            )
        )


def test_sync_rejects_invalid_state():
    with pytest.raises(
        TypeError,
        match="processing_state deve ser um dict",
    ):
        (
            telegram_webhook._sync_and_save_durable_telegram_session(
                conversation_bridge=FakeBridge(),
                durable_session=FakeDurableSession(),
                processing_state=[],
            )
        )


def test_sync_does_not_hide_save_failure():
    class FailingBridge(FakeBridge):
        def save_session(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError("database unavailable")

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        (
            telegram_webhook._sync_and_save_durable_telegram_session(
                conversation_bridge=FailingBridge(),
                durable_session=FakeDurableSession(),
                processing_state={
                    "step": "nome",
                    "lang": "pt",
                },
            )
        )


def test_delete_calls_bridge():
    bridge = FakeBridge()
    session = FakeDurableSession()

    result = telegram_webhook._delete_durable_telegram_session(
        conversation_bridge=bridge,
        durable_session=session,
    )

    assert result is True
    assert bridge.deleted == [session]


def test_delete_propagates_false_result():
    bridge = FakeBridge()
    bridge.delete_result = False

    session = FakeDurableSession()

    result = telegram_webhook._delete_durable_telegram_session(
        conversation_bridge=bridge,
        durable_session=session,
    )

    assert result is False


def test_delete_rejects_invalid_result():
    bridge = FakeBridge()
    bridge.delete_result = "yes"

    with pytest.raises(
        TypeError,
        match="Resultado de delete_session inválido",
    ):
        (
            telegram_webhook._delete_durable_telegram_session(
                conversation_bridge=bridge,
                durable_session=FakeDurableSession(),
            )
        )


def test_delete_does_not_hide_failure():
    class FailingBridge(FakeBridge):
        def delete_session(
            self,
            session,
        ):
            raise RuntimeError("storage unavailable")

    with pytest.raises(
        RuntimeError,
        match="storage unavailable",
    ):
        (
            telegram_webhook._delete_durable_telegram_session(
                conversation_bridge=FailingBridge(),
                durable_session=FakeDurableSession(),
            )
        )

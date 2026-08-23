from __future__ import annotations

import pytest

from api import telegram_webhook


class FakeDurableSession:
    def __init__(
        self,
        state,
        *,
        language=None,
    ):
        self._state = dict(state)
        self.language = language

    def to_processing_state(self):
        return dict(self._state)


class FakeBridge:
    def __init__(
        self,
        session,
    ):
        self.session = session
        self.calls = []

    def load_or_open_session(
        self,
        telegram_user_id,
        chat_id,
        initial_state,
        language=None,
        ttl_seconds=None,
    ):
        self.calls.append(
            {
                "telegram_user_id": telegram_user_id,
                "chat_id": chat_id,
                "initial_state": dict(initial_state),
                "language": language,
                "ttl_seconds": ttl_seconds,
            }
        )

        return self.session


def test_adapter_loads_session_with_trusted_identity():
    durable_session = FakeDurableSession(
        {
            "step": "nome",
            "lang": "pt",
        },
        language="pt",
    )

    bridge = FakeBridge(
        durable_session
    )

    loaded, processing_state = (
        telegram_webhook
        ._load_or_open_durable_telegram_session(
            conversation_bridge=bridge,
            telegram_user_id=1001,
            chat_id=-2001,
        )
    )

    assert loaded is durable_session

    assert processing_state == {
        "step": "nome",
        "lang": "pt",
    }

    assert bridge.calls == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "initial_state": {
                "step": "idioma",
                "lang": "pt",
            },
            "language": "pt",
            "ttl_seconds": None,
        }
    ]


def test_adapter_returns_mutable_copy():
    original_state = {
        "step": "nome",
        "lang": "pt",
    }

    durable_session = FakeDurableSession(
        original_state,
        language="pt",
    )

    bridge = FakeBridge(
        durable_session
    )

    _, processing_state = (
        telegram_webhook
        ._load_or_open_durable_telegram_session(
            conversation_bridge=bridge,
            telegram_user_id=1001,
            chat_id=2001,
        )
    )

    processing_state["step"] = "renda"

    assert original_state == {
        "step": "nome",
        "lang": "pt",
    }


def test_adapter_fills_missing_step_and_language():
    durable_session = FakeDurableSession(
        {},
        language="es",
    )

    bridge = FakeBridge(
        durable_session
    )

    _, processing_state = (
        telegram_webhook
        ._load_or_open_durable_telegram_session(
            conversation_bridge=bridge,
            telegram_user_id=1001,
            chat_id=2001,
        )
    )

    assert processing_state == {
        "step": "idioma",
        "lang": "es",
    }


def test_adapter_uses_pt_when_language_is_absent():
    durable_session = FakeDurableSession(
        {},
        language=None,
    )

    bridge = FakeBridge(
        durable_session
    )

    _, processing_state = (
        telegram_webhook
        ._load_or_open_durable_telegram_session(
            conversation_bridge=bridge,
            telegram_user_id=1001,
            chat_id=2001,
        )
    )

    assert processing_state == {
        "step": "idioma",
        "lang": "pt",
    }


def test_adapter_rejects_missing_bridge():
    with pytest.raises(
        ValueError,
        match="conversation_bridge é obrigatória",
    ):
        (
            telegram_webhook
            ._load_or_open_durable_telegram_session(
                conversation_bridge=None,
                telegram_user_id=1001,
                chat_id=2001,
            )
        )


def test_adapter_does_not_hide_bridge_failure():
    class FailingBridge:
        def load_or_open_session(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "state storage unavailable"
            )

    with pytest.raises(
        RuntimeError,
        match="state storage unavailable",
    ):
        (
            telegram_webhook
            ._load_or_open_durable_telegram_session(
                conversation_bridge=FailingBridge(),
                telegram_user_id=1001,
                chat_id=2001,
            )
        )


def test_adapter_rejects_invalid_processing_state():
    class InvalidSession:
        language = "pt"

        def to_processing_state(self):
            return []

    bridge = FakeBridge(
        InvalidSession()
    )

    with pytest.raises(
        TypeError,
        match=(
            "estado conversacional "
            "carregado é inválido"
        ),
    ):
        (
            telegram_webhook
            ._load_or_open_durable_telegram_session(
                conversation_bridge=bridge,
                telegram_user_id=1001,
                chat_id=2001,
            )
        )

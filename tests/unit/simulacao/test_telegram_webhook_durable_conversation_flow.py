from __future__ import annotations

from types import SimpleNamespace

from api import telegram_webhook


class FakeDurableSession:
    def __init__(
        self,
        state,
        *,
        language="pt",
    ):
        self.state = dict(state)
        self.language = language
        self.replace_calls = []
        self.language_calls = []

    def to_processing_state(self):
        return dict(self.state)

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


class FakeBridge:
    def __init__(
        self,
        session,
    ):
        self.session = session
        self.load_calls = []
        self.save_calls = []
        self.delete_calls = []

    def load_or_open_session(
        self,
        telegram_user_id,
        chat_id,
        initial_state,
        language=None,
        ttl_seconds=None,
    ):
        self.load_calls.append(
            {
                "telegram_user_id": telegram_user_id,
                "chat_id": chat_id,
                "initial_state": dict(initial_state),
                "language": language,
                "ttl_seconds": ttl_seconds,
            }
        )
        return self.session

    def save_session(
        self,
        session,
        *,
        ttl_seconds=None,
        only_if_changed=True,
    ):
        self.save_calls.append(
            {
                "state": dict(session.state),
                "language": session.language,
                "only_if_changed": only_if_changed,
            }
        )
        return session

    def delete_session(
        self,
        session,
    ):
        self.delete_calls.append(
            session
        )
        return True


def _install_common_fakes(
    monkeypatch,
    *,
    user_id=1001,
    chat_id=2001,
):
    sent = []

    monkeypatch.setattr(
        telegram_webhook,
        "extrair_contexto_confiavel_telegram",
        lambda update: SimpleNamespace(
            usuario_id=user_id,
            chat_id=chat_id,
            request_id="request-1",
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "send_telegram_message",
        lambda *args, **kwargs: sent.append(
            (
                args,
                kwargs,
            )
        ),
    )

    return sent


def test_start_loads_resets_and_saves_durable_session(
    monkeypatch,
):
    sent = _install_common_fakes(
        monkeypatch
    )

    session = FakeDurableSession(
        {
            "step": "renda",
            "lang": "pt",
            "nome": "Antigo",
        }
    )

    bridge = FakeBridge(
        session
    )


    result = (
        telegram_webhook.process_telegram_update(
            {
                "message": {
                    "text": "/start",
                }
            },
            conversation_bridge=bridge,
        )
    )

    assert result is None

    assert len(bridge.load_calls) == 1

    assert bridge.save_calls[-1]["state"] == {
        "step": "idioma",
        "lang": "pt",
    }

    assert sent


def test_name_transition_is_saved_durably(
    monkeypatch,
):
    _install_common_fakes(
        monkeypatch
    )

    session = FakeDurableSession(
        {
            "step": "nome",
            "lang": "pt",
        }
    )

    bridge = FakeBridge(
        session
    )

    result = (
        telegram_webhook.process_telegram_update(
            {
                "message": {
                    "text": "Rogerio",
                }
            },
            conversation_bridge=bridge,
        )
    )

    assert result is None

    assert bridge.save_calls[-1]["state"] == {
        "step": "renda",
        "lang": "pt",
        "nome": "Rogerio",
    }


def test_language_transition_is_saved_durably(
    monkeypatch,
):
    _install_common_fakes(
        monkeypatch
    )

    session = FakeDurableSession(
        {
            "step": "idioma",
            "lang": "pt",
        }
    )

    bridge = FakeBridge(
        session
    )

    label = next(
        key
        for key, value
        in telegram_webhook.LANGUAGE_OPTIONS.items()
        if value == "es"
    )

    telegram_webhook.process_telegram_update(
        {
            "message": {
                "text": label,
            }
        },
        conversation_bridge=bridge,
    )

    assert bridge.save_calls[-1]["state"] == {
        "step": "nome",
        "lang": "es",
    }

    assert bridge.save_calls[-1]["language"] == "es"


def test_cancel_deletes_durable_session_without_legacy_fallback(
    monkeypatch,
):
    _install_common_fakes(
        monkeypatch
    )

    session = FakeDurableSession(
        {
            "step": "renda",
            "lang": "pt",
        }
    )

    bridge = FakeBridge(
        session
    )


    telegram_webhook.process_telegram_update(
        {
            "message": {
                "text": "/cancelar",
            }
        },
        conversation_bridge=bridge,
    )

    assert bridge.delete_calls == [
        session
    ]



def test_save_failure_returns_false_inside_transition(
    monkeypatch,
):
    _install_common_fakes(
        monkeypatch
    )

    session = FakeDurableSession(
        {
            "step": "nome",
            "lang": "pt",
        }
    )

    class FailingBridge(FakeBridge):
        def save_session(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "state unavailable"
            )

    bridge = FailingBridge(
        session
    )

    result = (
        telegram_webhook.process_telegram_update(
            {
                "message": {
                    "text": "Rogerio",
                }
            },
            conversation_bridge=bridge,
        )
    )

    assert result is False


def test_load_failure_is_not_replaced_by_memory(
    monkeypatch,
):
    _install_common_fakes(
        monkeypatch
    )

    class FailingBridge:
        def load_or_open_session(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "state unavailable"
            )


    try:
        telegram_webhook.process_telegram_update(
            {
                "message": {
                    "text": "Rogerio",
                }
            },
            conversation_bridge=FailingBridge(),
        )

    except RuntimeError as error:
        assert str(error) == "state unavailable"

    else:
        raise AssertionError(
            "A falha durável deveria ser propagada."
        )

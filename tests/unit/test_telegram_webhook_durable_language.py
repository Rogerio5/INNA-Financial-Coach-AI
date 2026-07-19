from __future__ import annotations

from types import SimpleNamespace

from api import telegram_webhook


class FakeDurableSession:
    def __init__(
        self,
        *,
        language=None,
    ):
        self.language = language


class FakeBridge:
    def __init__(
        self,
        *,
        resolved_language="pt",
    ):
        self.resolved_language = (
            resolved_language
        )
        self.resolve_calls = []

    def resolve_language(
        self,
        telegram_user_id,
        chat_id,
        *,
        fallback_language=None,
    ):
        self.resolve_calls.append(
            {
                "telegram_user_id": telegram_user_id,
                "chat_id": chat_id,
                "fallback_language": fallback_language,
            }
        )

        return self.resolved_language


def test_state_language_has_highest_priority():
    bridge = FakeBridge(
        resolved_language="fr"
    )

    result = (
        telegram_webhook
        ._resolve_durable_telegram_language(
            chat_id=2001,
            telegram_user_id=1001,
            session={
                "step": "nome",
                "lang": "es",
            },
            conversation_bridge=bridge,
            durable_session=FakeDurableSession(
                language="en_us"
            ),
        )
    )

    assert result == "es"
    assert bridge.resolve_calls == []


def test_durable_session_language_has_second_priority():
    bridge = FakeBridge(
        resolved_language="fr"
    )

    result = (
        telegram_webhook
        ._resolve_durable_telegram_language(
            chat_id=2001,
            telegram_user_id=1001,
            session={
                "step": "idioma",
            },
            conversation_bridge=bridge,
            durable_session=FakeDurableSession(
                language="en_us"
            ),
        )
    )

    assert result == "en_us"
    assert bridge.resolve_calls == []


def test_bridge_resolves_language_when_state_is_absent():
    bridge = FakeBridge(
        resolved_language="de"
    )

    result = (
        telegram_webhook
        ._resolve_durable_telegram_language(
            chat_id=-2001,
            telegram_user_id=1001,
            session={
                "step": "idioma",
            },
            conversation_bridge=bridge,
            durable_session=FakeDurableSession(
                language=None
            ),
        )
    )

    assert result == "de"

    assert bridge.resolve_calls == [
        {
            "telegram_user_id": 1001,
            "chat_id": -2001,
            "fallback_language": "pt",
        }
    ]


def test_durable_path_does_not_use_user_last_lang():
    telegram_webhook.USER_LAST_LANG.clear()

    telegram_webhook.USER_LAST_LANG[
        2001
    ] = "ru"

    bridge = FakeBridge(
        resolved_language="it"
    )

    result = (
        telegram_webhook
        ._resolve_durable_telegram_language(
            chat_id=2001,
            telegram_user_id=1001,
            session=None,
            conversation_bridge=bridge,
            durable_session=None,
        )
    )

    assert result == "it"


def test_legacy_path_preserves_user_last_lang():
    telegram_webhook.USER_LAST_LANG.clear()

    telegram_webhook.USER_LAST_LANG[
        2001
    ] = "ro"

    result = (
        telegram_webhook
        ._resolve_durable_telegram_language(
            chat_id=2001,
            telegram_user_id=1001,
            session=None,
            conversation_bridge=None,
            durable_session=None,
        )
    )

    assert result == "ro"


def test_bridge_failure_is_not_replaced_by_legacy_memory():
    telegram_webhook.USER_LAST_LANG.clear()

    telegram_webhook.USER_LAST_LANG[
        2001
    ] = "es"

    class FailingBridge:
        def resolve_language(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "state unavailable"
            )

    try:
        (
            telegram_webhook
            ._resolve_durable_telegram_language(
                chat_id=2001,
                telegram_user_id=1001,
                session=None,
                conversation_bridge=FailingBridge(),
                durable_session=None,
            )
        )

    except RuntimeError as error:
        assert str(error) == "state unavailable"

    else:
        raise AssertionError(
            "A falha da bridge deveria ser propagada."
        )

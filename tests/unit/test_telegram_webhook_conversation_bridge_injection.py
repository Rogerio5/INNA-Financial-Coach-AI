from __future__ import annotations

import inspect

from api import telegram_webhook


def test_process_telegram_update_exposes_injectable_bridge():
    signature = inspect.signature(telegram_webhook.process_telegram_update)

    parameter = signature.parameters["conversation_bridge"]

    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


def test_process_telegram_update_accepts_fake_bridge_without_database():
    fake_bridge = object()

    result = telegram_webhook.process_telegram_update(
        {},
        conversation_bridge=fake_bridge,
    )

    assert result is False


def test_process_telegram_update_does_not_create_postgres_bridge_directly():
    source = inspect.getsource(telegram_webhook.process_telegram_update)

    forbidden_constructors = {
        "create_postgres_telegram_webhook_conversation_bridge(",
        "create_postgres_telegram_conversation_state_runtime(",
    }

    for forbidden_constructor in forbidden_constructors:
        assert forbidden_constructor not in source

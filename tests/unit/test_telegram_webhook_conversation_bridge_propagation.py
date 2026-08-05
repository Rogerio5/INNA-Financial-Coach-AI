from __future__ import annotations

import inspect

from api import telegram_webhook


def test_claimed_processor_exposes_keyword_only_conversation_bridge():
    signature = inspect.signature(telegram_webhook.process_claimed_telegram_update)

    parameter = signature.parameters["conversation_bridge"]

    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty

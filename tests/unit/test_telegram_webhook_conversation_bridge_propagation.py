from __future__ import annotations

import inspect

from api import telegram_webhook


def test_claimed_processor_exposes_keyword_only_conversation_bridge():
    signature = inspect.signature(
        telegram_webhook.process_claimed_telegram_update
    )

    parameter = signature.parameters[
        "conversation_bridge"
    ]

    assert (
        parameter.kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert parameter.default is None


def test_optional_bridge_helper_preserves_legacy_call(
    monkeypatch,
):
    calls = []

    def fake_process(
        update,
        *,
        conversation_bridge=None,
    ):
        calls.append(
            {
                "update": update,
                "conversation_bridge": (
                    conversation_bridge
                ),
            }
        )
        return "legacy-result"

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_process,
    )

    update = {
        "update_id": 101,
    }

    result = (
        telegram_webhook
        ._process_telegram_update_with_optional_bridge(
            update
        )
    )

    assert result == "legacy-result"
    assert calls == [
        {
            "update": update,
            "conversation_bridge": None,
        }
    ]


def test_optional_bridge_helper_forwards_bridge(
    monkeypatch,
):
    calls = []

    def fake_process(
        update,
        *,
        conversation_bridge=None,
    ):
        calls.append(
            (
                update,
                conversation_bridge,
            )
        )
        return "durable-result"

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_process,
    )

    update = {
        "update_id": 202,
    }

    fake_bridge = object()

    result = (
        telegram_webhook
        ._process_telegram_update_with_optional_bridge(
            update,
            conversation_bridge=fake_bridge,
        )
    )

    assert result == "durable-result"
    assert calls == [
        (
            update,
            fake_bridge,
        )
    ]


def test_claimed_processor_propagates_bridge_through_helper():
    source = inspect.getsource(
        telegram_webhook.process_claimed_telegram_update
    )

    assert (
        "_process_telegram_update_with_optional_bridge("
        in source
    )

    assert (
        "conversation_bridge=conversation_bridge"
        in source
    )

from __future__ import annotations

import pytest

from api import telegram_webhook


def test_public_processor_requires_bridge_argument():
    with pytest.raises(
        TypeError,
    ):
        telegram_webhook.process_telegram_update(
            {
                "update_id": 100,
            }
        )


def test_public_processor_rejects_explicit_none_bridge():
    with pytest.raises(
        telegram_webhook
        .TelegramUpdateIngressConfigurationError,
        match="conversation_bridge é obrigatória",
    ):
        telegram_webhook.process_telegram_update(
            {
                "update_id": 101,
            },
            conversation_bridge=None,
        )


def test_public_processor_delegates_to_core_with_bridge(
    monkeypatch,
):
    calls = []
    bridge = object()

    def fake_core(
        update,
        *,
        conversation_bridge=None,
    ):
        calls.append(
            {
                "update": update,
                "bridge": conversation_bridge,
            }
        )

        return "processed"

    monkeypatch.setattr(
        telegram_webhook,
        "_process_telegram_update_core",
        fake_core,
    )

    update = {
        "update_id": 102,
    }

    result = (
        telegram_webhook.process_telegram_update(
            update,
            conversation_bridge=bridge,
        )
    )

    assert result == "processed"

    assert calls == [
        {
            "update": update,
            "bridge": bridge,
        }
    ]


def test_legacy_processor_delegates_directly_to_core(
    monkeypatch,
):
    calls = []

    def fake_core(
        update,
        *,
        conversation_bridge=None,
    ):
        calls.append(
            {
                "update": update,
                "bridge": conversation_bridge,
            }
        )

        return "legacy"

    monkeypatch.setattr(
        telegram_webhook,
        "_process_telegram_update_core",
        fake_core,
    )

    update = {
        "update_id": 103,
    }

    result = (
        telegram_webhook
        ._process_legacy_telegram_update(
            update
        )
    )

    assert result == "legacy"

    assert calls == [
        {
            "update": update,
            "bridge": None,
        }
    ]


def test_legacy_processor_does_not_call_public_processor(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        lambda *args, **kwargs: (
            pytest.fail(
                "O legado não deve chamar "
                "o processador público."
            )
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "_process_telegram_update_core",
        lambda update, **kwargs: "legacy",
    )

    result = (
        telegram_webhook
        ._process_legacy_telegram_update(
            {
                "update_id": 104,
            }
        )
    )

    assert result == "legacy"

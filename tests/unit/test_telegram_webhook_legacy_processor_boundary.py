from __future__ import annotations

from api import telegram_webhook


def test_legacy_processor_calls_core_with_explicit_none(
    monkeypatch,
):
    calls = []

    def fake_processor(
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
        "_process_telegram_update_core",
        fake_processor,
    )

    update = {
        "message": {
            "text": "teste",
        }
    }

    result = (
        telegram_webhook
        ._process_legacy_telegram_update(
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


def test_optional_wrapper_uses_legacy_processor_when_bridge_is_none(
    monkeypatch,
):
    legacy_calls = []
    durable_calls = []

    def fake_legacy(
        update,
    ):
        legacy_calls.append(
            update
        )
        return "legacy"

    def fake_main(
        update,
        *,
        conversation_bridge=None,
    ):
        durable_calls.append(
            {
                "update": update,
                "bridge": conversation_bridge,
            }
        )
        return "durable"

    monkeypatch.setattr(
        telegram_webhook,
        "_process_legacy_telegram_update",
        fake_legacy,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_main,
    )

    update = {
        "update_id": 101,
    }

    result = (
        telegram_webhook
        ._process_telegram_update_with_optional_bridge(
            update,
            conversation_bridge=None,
        )
    )

    assert result == "legacy"
    assert legacy_calls == [update]
    assert durable_calls == []


def test_optional_wrapper_uses_main_processor_when_bridge_exists(
    monkeypatch,
):
    legacy_calls = []
    durable_calls = []

    bridge = object()

    def fake_legacy(
        update,
    ):
        legacy_calls.append(
            update
        )
        return "legacy"

    def fake_main(
        update,
        *,
        conversation_bridge=None,
    ):
        durable_calls.append(
            {
                "update": update,
                "bridge": conversation_bridge,
            }
        )
        return "durable"

    monkeypatch.setattr(
        telegram_webhook,
        "_process_legacy_telegram_update",
        fake_legacy,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_main,
    )

    update = {
        "update_id": 102,
    }

    result = (
        telegram_webhook
        ._process_telegram_update_with_optional_bridge(
            update,
            conversation_bridge=bridge,
        )
    )

    assert result == "durable"
    assert legacy_calls == []

    assert durable_calls == [
        {
            "update": update,
            "bridge": bridge,
        }
    ]


def test_production_worker_does_not_import_legacy_processor():
    from pathlib import Path

    worker_path = Path(
        "src/channels/telegram_update_worker.py"
    )

    source = worker_path.read_text(
        encoding="utf-8",
    )

    assert (
        "_process_legacy_telegram_update"
        not in source
    )

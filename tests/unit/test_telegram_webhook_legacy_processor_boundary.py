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

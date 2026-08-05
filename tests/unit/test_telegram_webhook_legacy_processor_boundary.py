from __future__ import annotations

from api import telegram_webhook


def test_production_worker_does_not_import_legacy_processor():
    from pathlib import Path

    worker_path = Path("src/channels/telegram_update_worker.py")

    source = worker_path.read_text(
        encoding="utf-8",
    )

    assert "_process_legacy_telegram_update" not in source

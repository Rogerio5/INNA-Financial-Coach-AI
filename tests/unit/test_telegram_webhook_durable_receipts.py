from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import telegram_webhook
from api.security.telegram_webhook import (
    TELEGRAM_SECRET_HEADER,
)


SECRET = "Webhook_Secret_0123456789abcdef0123456789abcdef"

CLAIM_TOKEN = "c" * 64
FINGERPRINT = "a" * 64


@pytest.fixture(
    autouse=True,
)
def configure_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )


def _client() -> TestClient:
    app = FastAPI()

    app.include_router(telegram_webhook.router)

    return TestClient(app)


def _path() -> str:
    route = next(
        route
        for route in telegram_webhook.router.routes
        if route.name == "telegram_webhook"
    )

    return route.path


def _update() -> dict:
    return {
        "update_id": 1001,
        "message": {
            "message_id": 77,
            "chat": {
                "id": 123456,
            },
            "text": "Olá",
        },
    }


def _lease():
    return telegram_webhook.TelegramUpdateProcessingLease(
        update_id=1001,
        attempt_count=1,
        claim_token=CLAIM_TOKEN,
        update_fingerprint=(FINGERPRINT),
    )


@pytest.mark.parametrize(
    "processing_result",
    [
        True,
        None,
    ],
)
def test_background_success_completes_receipt(
    monkeypatch,
    processing_result,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(return_value=(processing_result)),
    )

    complete = MagicMock()
    fail = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        complete,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        fail,
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
        conversation_bridge=object(),
    )

    complete.assert_called_once_with(lease)

    fail.assert_not_called()


def test_background_processing_failure_marks_failed(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(return_value=False),
    )

    complete = MagicMock()
    fail = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        complete,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        fail,
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
        conversation_bridge=object(),
    )

    complete.assert_not_called()

    fail.assert_called_once_with(
        lease,
        error_code=("telegram.processing_failed"),
    )


def test_background_exception_marks_failed(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(side_effect=RuntimeError("secret processing details")),
    )

    fail = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        fail,
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
        conversation_bridge=object(),
    )

    fail.assert_called_once()


def test_complete_failure_attempts_safe_fail(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        MagicMock(
            side_effect=(
                telegram_webhook.TelegramUpdateReceiptUnavailableError(
                    "database secret"
                )
            )
        ),
    )

    fail = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        fail,
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
        conversation_bridge=object(),
    )

    fail.assert_called_once()


def test_background_receipt_error_is_sanitized(
    monkeypatch,
    capsys,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(return_value=False),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        MagicMock(
            side_effect=(
                telegram_webhook.TelegramUpdateReceiptServiceError(
                    "postgresql://user:super-secret@database"
                )
            )
        ),
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
        conversation_bridge=object(),
    )

    output = capsys.readouterr().out

    assert "super-secret" not in output
    assert "postgresql://" not in output


def test_memory_cache_was_removed():
    source = Path("api/telegram_webhook.py").read_text(encoding="utf-8")

    assert "PROCESSED_UPDATES" not in source

    assert "claim_authenticated_telegram_update" in source

    assert "process_claimed_telegram_update" in source

    assert "complete_authenticated_telegram_update" in source

    assert "fail_authenticated_telegram_update" in source

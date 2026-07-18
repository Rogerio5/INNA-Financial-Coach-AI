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


SECRET = (
    "Webhook_Secret_"
    "0123456789abcdef0123456789abcdef"
)

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

    app.include_router(
        telegram_webhook.router
    )

    return TestClient(
        app
    )


def _path() -> str:
    route = next(
        route
        for route
        in telegram_webhook.router.routes
        if route.name
        == "telegram_webhook"
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
    return (
        telegram_webhook
        .TelegramUpdateProcessingLease(
            update_id=1001,
            attempt_count=1,
            claim_token=CLAIM_TOKEN,
            update_fingerprint=(
                FINGERPRINT
            ),
        )
    )


@pytest.mark.parametrize(
    (
        "status",
        "is_duplicate",
    ),
    [
        (
            "duplicate",
            True,
        ),
        (
            "in_progress",
            False,
        ),
    ],
)
def test_non_process_decision_does_not_schedule(
    monkeypatch,
    status,
    is_duplicate,
):
    claim = MagicMock(
        return_value=(
            telegram_webhook
            .TelegramUpdateClaimDecision(
                update_id=1001,
                status=status,
                attempt_count=2,
                lease=None,
            )
        )
    )

    process = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "claim_authenticated_telegram_update",
        claim,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_claimed_telegram_update",
        process,
    )

    response = _client().post(
        _path(),
        json=_update(),
        headers={
            TELEGRAM_SECRET_HEADER: SECRET,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ok": True,
        "accepted": False,
        "duplicate": is_duplicate,
        "status": status,
    }

    process.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        "claimed",
        "reclaimed",
    ],
)
def test_process_decision_schedules_owned_lease(
    monkeypatch,
    status,
):
    update = _update()
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "claim_authenticated_telegram_update",
        MagicMock(
            return_value=(
                telegram_webhook
                .TelegramUpdateClaimDecision(
                    update_id=1001,
                    status=status,
                    attempt_count=1,
                    lease=lease,
                )
            )
        ),
    )

    process = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "process_claimed_telegram_update",
        process,
    )

    response = _client().post(
        _path(),
        json=update,
        headers={
            TELEGRAM_SECRET_HEADER: SECRET,
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["status"] == status

    process.assert_called_once_with(
        update,
        lease,
    )


@pytest.mark.parametrize(
    (
        "error",
        "expected_status",
    ),
    [
        (
            telegram_webhook
            .TelegramUpdateReceiptValidationError(
                "sensitive validation"
            ),
            400,
        ),
        (
            telegram_webhook
            .TelegramUpdateReceiptConflictError(
                "sensitive conflict"
            ),
            409,
        ),
        (
            telegram_webhook
            .TelegramUpdateReceiptUnavailableError(
                "postgresql://secret"
            ),
            503,
        ),
    ],
)
def test_claim_errors_are_mapped_and_sanitized(
    monkeypatch,
    error,
    expected_status,
):
    monkeypatch.setattr(
        telegram_webhook,
        "claim_authenticated_telegram_update",
        MagicMock(
            side_effect=error
        ),
    )

    response = _client().post(
        _path(),
        json=_update(),
        headers={
            TELEGRAM_SECRET_HEADER: SECRET,
        },
    )

    assert (
        response.status_code
        == expected_status
    )

    body = response.text

    assert "sensitive" not in body
    assert "postgresql://" not in body


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
        MagicMock(
            return_value=(
                processing_result
            )
        ),
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
    )

    complete.assert_called_once_with(
        lease
    )

    fail.assert_not_called()


def test_background_processing_failure_marks_failed(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(
            return_value=False
        ),
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
    )

    complete.assert_not_called()

    fail.assert_called_once_with(
        lease,
        error_code=(
            "telegram.processing_failed"
        ),
    )


def test_background_exception_marks_failed(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(
            side_effect=RuntimeError(
                "secret processing details"
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
    )

    fail.assert_called_once()


def test_complete_failure_attempts_safe_fail(
    monkeypatch,
):
    lease = _lease()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        MagicMock(
            return_value=True
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        MagicMock(
            side_effect=(
                telegram_webhook
                .TelegramUpdateReceiptUnavailableError(
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
        MagicMock(
            return_value=False
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "fail_authenticated_telegram_update",
        MagicMock(
            side_effect=(
                telegram_webhook
                .TelegramUpdateReceiptServiceError(
                    "postgresql://user:"
                    "super-secret@database"
                )
            )
        ),
    )

    telegram_webhook.process_claimed_telegram_update(
        _update(),
        lease,
    )

    output = capsys.readouterr().out

    assert "super-secret" not in output
    assert "postgresql://" not in output


def test_memory_cache_was_removed():
    source = Path(
        "api/telegram_webhook.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "PROCESSED_UPDATES"
        not in source
    )

    assert (
        "claim_authenticated_telegram_update"
        in source
    )

    assert (
        "process_claimed_telegram_update"
        in source
    )

    assert (
        "complete_authenticated_telegram_update"
        in source
    )

    assert (
        "fail_authenticated_telegram_update"
        in source
    )

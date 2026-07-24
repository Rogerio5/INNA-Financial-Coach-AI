from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import telegram_webhook
from api.security.telegram_webhook import (
    TELEGRAM_SECRET_HEADER,
    TelegramWebhookConfigurationError,
    TelegramWebhookSecurityError,
    obter_segredo_webhook_telegram,
    verificar_segredo_webhook_telegram,
)


SECRET = (
    "Telegram_Webhook_Secret_"
    "0123456789abcdef0123456789"
)


def test_valid_secret_is_accepted():
    context = (
        verificar_segredo_webhook_telegram(
            SECRET,
            expected_secret=SECRET,
        )
    )

    assert context.authenticated is True

    assert (
        context.authentication_method
        == "telegram_secret_token"
    )


def test_wrong_secret_is_rejected():
    with pytest.raises(
        TelegramWebhookSecurityError
    ):
        verificar_segredo_webhook_telegram(
            "Wrong_Secret_0123456789abcdef0123456789",
            expected_secret=SECRET,
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "short",
        "invalid secret with spaces",
        "invalid@secret#characters",
    ],
)
def test_invalid_received_secret_is_rejected(
    value,
):
    with pytest.raises(
        TelegramWebhookSecurityError
    ):
        verificar_segredo_webhook_telegram(
            value,
            expected_secret=SECRET,
        )


def test_invalid_configuration_is_rejected():
    with pytest.raises(
        TelegramWebhookConfigurationError
    ):
        obter_segredo_webhook_telegram(
            "short"
        )


def test_environment_configuration(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    assert (
        obter_segredo_webhook_telegram()
        == SECRET
    )


def test_safe_context_does_not_expose_secret():
    context = (
        verificar_segredo_webhook_telegram(
            SECRET,
            expected_secret=SECRET,
        )
    )

    safe = context.to_safe_dict()

    assert "secret" not in safe
    assert SECRET not in str(safe)


def _build_client() -> TestClient:
    app = FastAPI()

    app.include_router(
        telegram_webhook.router
    )

    return TestClient(
        app
    )


def _webhook_path() -> str:
    route = next(
        route
        for route
        in telegram_webhook.router.routes
        if route.name == "telegram_webhook"
    )

    return route.path


def test_real_webhook_rejects_missing_header(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    process = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        process,
    )

    response = _build_client().post(
        _webhook_path(),
        json={
            "update_id": 1001,
        },
    )

    assert response.status_code == 401

    process.assert_not_called()


def test_real_webhook_rejects_wrong_header(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    process = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        process,
    )

    response = _build_client().post(
        _webhook_path(),
        json={
            "update_id": 1002,
        },
        headers={
            TELEGRAM_SECRET_HEADER: (
                "Wrong_Secret_"
                "0123456789abcdef0123456789"
            ),
        },
    )

    assert response.status_code == 401

    process.assert_not_called()


def test_real_webhook_accepts_valid_header(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    update = {
        "update_id": 1003,
    }

    outcome = MagicMock()
    outcome.accepted = True
    outcome.duplicate = False
    outcome.decision = "enqueued"

    enqueue = MagicMock(
        return_value=outcome,
    )

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _build_client().post(
        _webhook_path(),
        json=update,
        headers={
            TELEGRAM_SECRET_HEADER: SECRET,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ok": True,
        "accepted": True,
        "duplicate": False,
        "status": "enqueued",
    }

    enqueue.assert_called_once_with(
        update
    )


def test_route_declares_trusted_dependency():
    signature = inspect.signature(
        telegram_webhook.telegram_webhook
    )

    assert (
        "_trusted_webhook"
        in signature.parameters
    )


def test_error_response_does_not_expose_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    response = _build_client().post(
        _webhook_path(),
        json={
            "update_id": 1004,
        },
        headers={
            TELEGRAM_SECRET_HEADER: (
                "Wrong_Secret_"
                "0123456789abcdef0123456789"
            ),
        },
    )

    assert response.status_code == 401
    assert SECRET not in response.text

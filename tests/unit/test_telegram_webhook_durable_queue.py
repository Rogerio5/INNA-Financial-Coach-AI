from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import telegram_webhook
from api.security import (
    TELEGRAM_SECRET_HEADER,
)


SECRET = "q" * 64

WEBHOOK_PATH = next(
    route.path
    for route in telegram_webhook.router.routes
    if route.name == "telegram_webhook"
)


def _client() -> TestClient:
    app = FastAPI()

    app.include_router(
        telegram_webhook.router,
    )

    return TestClient(
        app
    )


def _headers() -> dict[str, str]:
    return {
        TELEGRAM_SECRET_HEADER: SECRET,
    }


def _update(
    update_id: int = 2001,
) -> dict[str, object]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": 1,
            "date": 1_700_000_000,
            "chat": {
                "id": 9001,
                "type": "private",
            },
            "from": {
                "id": 9001,
                "is_bot": False,
                "first_name": "Test",
            },
            "text": "Mensagem sintética",
        },
    }


def _outcome(
    *,
    decision: str,
    accepted: bool,
    duplicate: bool,
) -> SimpleNamespace:
    return SimpleNamespace(
        decision=decision,
        accepted=accepted,
        duplicate=duplicate,
    )


def test_route_no_longer_declares_background_tasks():
    function = (
        telegram_webhook
        .telegram_webhook
    )

    assert inspect.iscoroutinefunction(
        function
    )

    parameters = inspect.signature(
        function
    ).parameters

    assert "request" in parameters
    assert "_trusted_webhook" in parameters

    assert (
        "background_tasks"
        not in parameters
    )

    source = inspect.getsource(
        function
    )

    assert "BackgroundTasks" not in source
    assert ".add_task(" not in source

    assert (
        "claim_authenticated_"
        "telegram_update"
        not in source
    )

    assert (
        "process_claimed_"
        "telegram_update"
        not in source
    )

    assert (
        "enqueue_authenticated_"
        "telegram_update_atomic"
        in source
    )


@pytest.mark.parametrize(
    (
        "decision",
        "accepted",
        "duplicate",
    ),
    [
        (
            "enqueued",
            True,
            False,
        ),
        (
            "already_enqueued",
            True,
            False,
        ),
        (
            "in_progress",
            True,
            False,
        ),
        (
            "duplicate",
            False,
            True,
        ),
    ],
)
def test_authenticated_webhook_returns_safe_ingress_outcome(
    monkeypatch,
    decision,
    accepted,
    duplicate,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    update = _update()

    enqueue = MagicMock(
        return_value=_outcome(
            decision=decision,
            accepted=accepted,
            duplicate=duplicate,
        )
    )

    process_update = MagicMock()
    process_claimed = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        process_update,
    )

    monkeypatch.setattr(
        telegram_webhook,
        (
            "process_claimed_"
            "telegram_update"
        ),
        process_claimed,
    )

    response = _client().post(
        WEBHOOK_PATH,
        json=update,
        headers=_headers(),
    )

    assert response.status_code == 200

    assert response.json() == {
        "ok": True,
        "accepted": accepted,
        "duplicate": duplicate,
        "status": decision,
    }

    enqueue.assert_called_once_with(
        update
    )

    process_update.assert_not_called()
    process_claimed.assert_not_called()


def test_invalid_json_is_rejected_before_ingress(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    enqueue = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _client().post(
        WEBHOOK_PATH,
        content=b"{",
        headers={
            **_headers(),
            "content-type": (
                "application/json"
            ),
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Atualização Telegram inválida."
        ),
    }

    enqueue.assert_not_called()


@pytest.mark.parametrize(
    "invalid_update",
    [
        [],
        ["invalid"],
        "invalid",
        100,
        None,
    ],
)
def test_non_mapping_update_is_rejected(
    monkeypatch,
    invalid_update,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    enqueue = MagicMock()

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _client().post(
        WEBHOOK_PATH,
        json=invalid_update,
        headers=_headers(),
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Atualização Telegram inválida."
        ),
    }

    enqueue.assert_not_called()


@pytest.mark.parametrize(
    (
        "error",
        "expected_status",
        "expected_detail",
    ),
    [
        (
            telegram_webhook
            .TelegramUpdateIngressValidationError(
                "sensitive validation"
            ),
            400,
            "Atualização Telegram inválida.",
        ),
        (
            telegram_webhook
            .TelegramUpdateIngressConflictError(
                "sensitive conflict"
            ),
            409,
            "Conflito no update Telegram.",
        ),
        (
            telegram_webhook
            .TelegramUpdateIngressConfigurationError(
                "encryption-key-secret"
            ),
            503,
            (
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ),
        (
            telegram_webhook
            .TelegramUpdateIngressConsistencyError(
                "database-consistency-secret"
            ),
            503,
            (
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ),
        (
            telegram_webhook
            .TelegramUpdateIngressUnavailableError(
                "postgresql://secret"
            ),
            503,
            (
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ),
        (
            RuntimeError(
                "unexpected-sensitive-error"
            ),
            503,
            (
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ),
    ],
)
def test_ingress_errors_are_mapped_and_sanitized(
    monkeypatch,
    error,
    expected_status,
    expected_detail,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    enqueue = MagicMock(
        side_effect=error,
    )

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _client().post(
        WEBHOOK_PATH,
        json=_update(),
        headers=_headers(),
    )

    assert (
        response.status_code
        == expected_status
    )

    assert response.json() == {
        "detail": expected_detail,
    }

    response_text = response.text

    for sensitive_value in (
        "sensitive validation",
        "sensitive conflict",
        "encryption-key-secret",
        "database-consistency-secret",
        "postgresql://secret",
        "unexpected-sensitive-error",
    ):
        assert (
            sensitive_value
            not in response_text
        )


def test_webhook_response_does_not_expose_update_payload(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    sensitive_text = (
        "private-financial-message"
    )

    update = _update()

    update["message"]["text"] = (
        sensitive_text
    )

    enqueue = MagicMock(
        return_value=_outcome(
            decision="enqueued",
            accepted=True,
            duplicate=False,
        )
    )

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _client().post(
        WEBHOOK_PATH,
        json=update,
        headers=_headers(),
    )

    assert response.status_code == 200

    assert sensitive_text not in response.text

    assert set(
        response.json()
    ) == {
        "ok",
        "accepted",
        "duplicate",
        "status",
    }


def test_enqueue_finishes_before_http_response(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_WEBHOOK_SECRET",
        SECRET,
    )

    events: list[str] = []

    def enqueue(
        update,
    ):
        assert update == _update()

        events.append(
            "database_commit"
        )

        return _outcome(
            decision="enqueued",
            accepted=True,
            duplicate=False,
        )

    monkeypatch.setattr(
        telegram_webhook,
        (
            "enqueue_authenticated_"
            "telegram_update_atomic"
        ),
        enqueue,
    )

    response = _client().post(
        WEBHOOK_PATH,
        json=_update(),
        headers=_headers(),
    )

    events.append(
        "http_response"
    )

    assert response.status_code == 200

    assert events == [
        "database_commit",
        "http_response",
    ]

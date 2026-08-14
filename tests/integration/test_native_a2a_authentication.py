from __future__ import annotations

from typing import Any

from a2a.helpers import new_text_message
from a2a.types import Role
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.protobuf.json_format import MessageToDict

from src.a2a_server.adapter import (
    InnaNativeA2AAdapter,
)
from src.a2a_server.security import (
    A2A_AUTH_UNAVAILABLE_MESSAGE,
    A2A_UNAUTHORIZED_MESSAGE,
)
from src.a2a_server.server import (
    A2A_JSONRPC_PATH,
    InnaA2AExecutor,
    mount_a2a_app,
)

VALID_TOKEN = (
    "inna-a2a-test-token-"
    + ("x" * 40)
)


def _runtime(
    message: str,
    **kwargs: Any,
) -> dict[str, str]:
    del kwargs

    return {
        "response": (
            f"authenticated:{message}"
        ),
    }


def _payload(
    text: str = "teste seguro",
) -> dict[str, object]:
    message = new_text_message(
        text=text,
        role=Role.ROLE_USER,
    )

    return {
        "jsonrpc": "2.0",
        "id": "auth-test-1",
        "method": "SendMessage",
        "params": {
            "message": MessageToDict(
                message
            ),
        },
    }


def _app() -> FastAPI:
    host = FastAPI()

    adapter = InnaNativeA2AAdapter(
        runtime_executor=_runtime
    )

    mount_a2a_app(
        host,
        base_url=(
            "https://inna.example"
        ),
        executor=InnaA2AExecutor(
            adapter=adapter
        ),
    )

    return host


def test_agent_card_remains_public_without_token(
    monkeypatch,
):
    monkeypatch.delenv(
        "INNA_A2A_CLIENT_TOKEN",
        raising=False,
    )

    with TestClient(
        _app()
    ) as client:
        response = client.get(
            "/.well-known/"
            "agent-card.json"
        )

    assert response.status_code == 200
    assert (
        "INNA A2A Gateway"
        in response.text
    )


def test_jsonrpc_fails_closed_when_server_token_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "INNA_A2A_CLIENT_TOKEN",
        raising=False,
    )

    with TestClient(
        _app()
    ) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": (
            A2A_AUTH_UNAVAILABLE_MESSAGE
        ),
    }


def test_jsonrpc_rejects_missing_bearer_token(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_A2A_CLIENT_TOKEN",
        VALID_TOKEN,
    )

    with TestClient(
        _app()
    ) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 401
    assert response.json() == {
        "error": (
            A2A_UNAUTHORIZED_MESSAGE
        ),
    }

    assert (
        response.headers[
            "www-authenticate"
        ]
        == "Bearer"
    )


def test_jsonrpc_rejects_wrong_token_without_leak(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_A2A_CLIENT_TOKEN",
        VALID_TOKEN,
    )

    wrong_token = (
        "wrong-secret-token-"
        + ("z" * 40)
    )

    with TestClient(
        _app()
    ) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(),
            headers={
                "A2A-Version": "1.0",
                "Authorization": (
                    f"Bearer {wrong_token}"
                ),
            },
        )

    assert response.status_code == 401

    serialized = response.text

    assert VALID_TOKEN not in serialized
    assert wrong_token not in serialized


def test_jsonrpc_accepts_correct_bearer_token(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_A2A_CLIENT_TOKEN",
        VALID_TOKEN,
    )

    with TestClient(
        _app()
    ) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(
                "autenticado"
            ),
            headers={
                "A2A-Version": "1.0",
                "Authorization": (
                    f"Bearer {VALID_TOKEN}"
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert "error" not in payload

    response_text = payload[
        "result"
    ][
        "message"
    ][
        "parts"
    ][0]["text"]

    assert response_text == (
        "authenticated:"
        "autenticado"
    )


def test_production_mount_requires_auth_by_default():
    import inspect

    from src.a2a_server.server import (
        mount_a2a_app,
    )

    parameter = inspect.signature(
        mount_a2a_app
    ).parameters[
        "require_auth"
    ]

    assert parameter.default is True

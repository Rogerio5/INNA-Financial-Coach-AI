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
from src.a2a_server.server import (
    A2A_JSONRPC_PATH,
    InnaA2AExecutor,
    mount_a2a_app,
    resolve_a2a_public_base_url,
)


def _fake_runtime(
    message: str,
    **kwargs: Any,
) -> dict[str, str]:
    del kwargs

    return {
        "response": (
            f"INNA A2A mounted: {message}"
        ),
    }


def _payload(
    text: str,
) -> dict[str, object]:
    message = new_text_message(
        text=text,
        role=Role.ROLE_USER,
    )

    return {
        "jsonrpc": "2.0",
        "id": "mount-test-1",
        "method": "SendMessage",
        "params": {
            "message": MessageToDict(
                message
            ),
        },
    }


def _create_host() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
        }

    adapter = InnaNativeA2AAdapter(
        runtime_executor=_fake_runtime
    )

    mount_a2a_app(
        app,
        base_url=(
            "https://inna.example"
        ),
        executor=InnaA2AExecutor(
            adapter=adapter
        ),
        require_auth=False,
    )

    return app


def test_existing_fastapi_route_is_not_shadowed():
    app = _create_host()

    with TestClient(app) as client:
        response = client.get(
            "/health"
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_agent_card_is_exposed_at_standard_path():
    app = _create_host()

    with TestClient(app) as client:
        response = client.get(
            "/.well-known/agent-card.json"
        )

    assert response.status_code == 200

    serialized = response.text

    assert (
        "https://inna.example"
        "/a2a/jsonrpc/"
        in serialized
    )

    assert "127.0.0.1" not in serialized


def test_jsonrpc_runs_through_mounted_a2a_gateway():
    app = _create_host()

    with TestClient(app) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(
                "teste fastapi"
            ),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert "error" not in payload

    text = payload[
        "result"
    ][
        "message"
    ][
        "parts"
    ][0]["text"]

    assert text == (
        "INNA A2A mounted: "
        "teste fastapi"
    )


def test_public_base_url_can_come_from_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_A2A_PUBLIC_BASE_URL",
        "https://inna-api.example/",
    )

    assert (
        resolve_a2a_public_base_url()
        == "https://inna-api.example"
    )


def test_invalid_public_base_url_fails_closed(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_A2A_PUBLIC_BASE_URL",
        "not-a-url",
    )

    try:
        resolve_a2a_public_base_url()
    except ValueError:
        return

    raise AssertionError(
        "Invalid A2A URL should fail closed."
    )

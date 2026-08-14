"""Integração do protocolo A2A com o núcleo INNA."""

from __future__ import annotations

from typing import Any

import pytest
from a2a.helpers import new_text_message
from a2a.types import Role
from google.protobuf.json_format import MessageToDict
from starlette.testclient import TestClient

from src.a2a_server.adapter import (
    SAFE_RUNTIME_ERROR,
    InnaNativeA2AAdapter,
)
from src.a2a_server.server import (
    A2A_JSONRPC_PATH,
    InnaA2AExecutor,
    create_app,
)


def _payload(
    text: str,
) -> dict[str, Any]:
    message = new_text_message(
        text=text,
        role=Role.ROLE_USER,
    )

    return {
        "jsonrpc": "2.0",
        "id": "week5-5c-runtime",
        "method": "SendMessage",
        "params": {
            "message": MessageToDict(
                message
            ),
        },
    }


def _response_text(
    response,
) -> str:
    payload = response.json()

    assert "error" not in payload

    return payload[
        "result"
    ]["message"]["parts"][0]["text"]


def test_native_a2a_calls_existing_inna_runtime():
    calls: list[
        tuple[str, dict[str, Any]]
    ] = []

    def fake_runtime(
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        calls.append(
            (
                message,
                kwargs,
            )
        )

        return {
            "response": (
                "Resposta governada "
                "do núcleo INNA."
            ),
            "structured_response": {
                "internal": "not-exposed",
            },
        }

    adapter = InnaNativeA2AAdapter(
        runtime_executor=fake_runtime
    )

    executor = InnaA2AExecutor(
        adapter=adapter
    )

    app = create_app(
        executor=executor,
        require_auth=False,
    )

    user_input = (
        "Analise minha situação financeira."
    )

    with TestClient(app) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(
                user_input
            ),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 200

    assert _response_text(response) == (
        "Resposta governada "
        "do núcleo INNA."
    )

    assert len(calls) == 1

    message, kwargs = calls[0]

    assert message == user_input

    # Identidade A2A externa não é convertida
    # implicitamente em identidade de usuário.
    assert kwargs["usuario_id"] is None
    assert kwargs["idioma"] == "pt"
    assert kwargs["moeda"] == "BRL"

    serialized = response.text

    assert "not-exposed" not in serialized
    assert "structured_response" not in serialized


def test_runtime_failure_does_not_leak_internal_error(
    caplog: pytest.LogCaptureFixture,
):
    internal_secret = (
        "database-password-secret"
    )

    def failing_runtime(
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del message
        del kwargs

        raise RuntimeError(
            internal_secret
        )

    adapter = InnaNativeA2AAdapter(
        runtime_executor=failing_runtime
    )

    app = create_app(
        executor=InnaA2AExecutor(
            adapter=adapter
        ),
        require_auth=False,
    )

    with TestClient(app) as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_payload(
                "Teste seguro."
            ),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 200

    text = _response_text(
        response
    )

    assert text == SAFE_RUNTIME_ERROR
    assert internal_secret not in response.text
    assert internal_secret not in caplog.text
    assert (
        "inna_native_a2a_runtime_failed"
        in caplog.text
    )


def test_empty_runtime_response_fails_closed():
    def empty_runtime(
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del message
        del kwargs

        return {
            "response": "",
        }

    adapter = InnaNativeA2AAdapter(
        runtime_executor=empty_runtime
    )

    assert (
        adapter.execute(
            "teste"
        )
        == SAFE_RUNTIME_ERROR
    )

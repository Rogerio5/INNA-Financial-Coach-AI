"""Integração local com o protocolo A2A oficial."""

from __future__ import annotations

from a2a.helpers import new_text_message
from a2a.types import Role
from google.protobuf.json_format import (
    MessageToDict,
)
from starlette.testclient import TestClient

from src.a2a_server.adapter import (
    InnaNativeA2AAdapter,
)
from src.a2a_server.server import (
    A2A_JSONRPC_PATH,
    InnaA2AExecutor,
    build_agent_card,
    create_app,
)


def _protocol_runtime(
    message: str,
    **kwargs: object,
) -> dict[str, str]:
    del kwargs

    if message.strip():
        response = (
            "INNA native A2A gateway "
            "received a text request."
        )
    else:
        response = (
            "INNA native A2A gateway "
            "received a request."
        )

    return {
        "response": response,
    }


def _client() -> TestClient:
    adapter = InnaNativeA2AAdapter(
        runtime_executor=_protocol_runtime
    )

    executor = InnaA2AExecutor(
        adapter=adapter
    )

    return TestClient(
        create_app(
            executor=executor
        )
    )


def _send_message_payload(
    text: str,
) -> dict:
    message = new_text_message(
        text=text,
        role=Role.ROLE_USER,
    )

    return {
        "jsonrpc": "2.0",
        "id": "week5-5c-001",
        "method": "SendMessage",
        "params": {
            "message": MessageToDict(
                message
            ),
        },
    }


def test_agent_card_declares_jsonrpc_v1():
    card = build_agent_card()

    assert card.name == "INNA A2A Gateway"
    assert card.version == "1.0.0"

    assert len(
        card.supported_interfaces
    ) == 1

    interface = card.supported_interfaces[
        0
    ]

    assert (
        interface.protocol_binding
        == "JSONRPC"
    )

    assert (
        interface.protocol_version
        == "1.0"
    )


def test_well_known_agent_card_is_exposed():
    with _client() as client:
        response = client.get(
            "/.well-known/agent-card.json"
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["name"]
        == "INNA A2A Gateway"
    )

    assert (
        payload["supportedInterfaces"][0][
            "protocolBinding"
        ]
        == "JSONRPC"
    )


def test_native_jsonrpc_send_message():
    secret_marker = (
        "private-user-payload-123"
    )

    with _client() as client:
        response = client.post(
            A2A_JSONRPC_PATH,
            json=_send_message_payload(
                secret_marker
            ),
            headers={
                "A2A-Version": "1.0",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert "error" not in payload

    message = payload[
        "result"
    ]["message"]

    response_text = message[
        "parts"
    ][0]["text"]

    assert response_text == (
        "INNA native A2A gateway "
        "received a text request."
    )

    assert secret_marker not in response_text

"""A2A nativo real via HTTP e processo Uvicorn separado."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time

import httpx
from a2a.helpers import new_text_message
from a2a.types import Role
from google.protobuf.json_format import (
    MessageToDict,
)


def _free_port() -> int:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:
        sock.bind(
            ("127.0.0.1", 0)
        )

        return int(
            sock.getsockname()[1]
        )


def _payload(
    text: str,
) -> dict:
    message = new_text_message(
        text=text,
        role=Role.ROLE_USER,
    )

    return {
        "jsonrpc": "2.0",
        "id": "week5-5c-real-http",
        "method": "SendMessage",
        "params": {
            "message": MessageToDict(
                message
            ),
        },
    }


def _wait_until_ready(
    base_url: str,
) -> None:
    deadline = time.monotonic() + 15.0

    while time.monotonic() < deadline:
        try:
            response = httpx.get(
                (
                    base_url
                    + "/.well-known/"
                    "agent-card.json"
                ),
                timeout=1.0,
            )

            if response.status_code == 200:
                return

        except httpx.HTTPError:
            pass

        time.sleep(0.15)

    raise RuntimeError(
        "A2A Uvicorn server "
        "did not become ready."
    )


def test_native_a2a_over_real_http_process():
    port = _free_port()

    base_url = (
        f"http://127.0.0.1:{port}"
    )

    env = os.environ.copy()

    server_code = f"""
import uvicorn

from src.a2a_server.adapter import InnaNativeA2AAdapter
from src.a2a_server.server import (
    InnaA2AExecutor,
    create_app,
)


def protocol_runtime(
    message,
    **kwargs,
):
    del kwargs

    if str(message).strip():
        response = (
            "INNA native A2A gateway "
            "received a text request."
        )
    else:
        response = (
            "INNA native A2A gateway "
            "received a request."
        )

    return {{
        "response": response,
    }}


adapter = InnaNativeA2AAdapter(
    runtime_executor=protocol_runtime
)

executor = InnaA2AExecutor(
    adapter=adapter
)

app = create_app(
    base_url="http://127.0.0.1:{port}",
    executor=executor,
)

uvicorn.run(
    app,
    host="127.0.0.1",
    port={port},
    log_level="warning",
)
"""

    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            server_code,
        ],
        cwd=os.getcwd(),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_until_ready(
            base_url
        )

        card_response = httpx.get(
            (
                base_url
                + "/.well-known/"
                "agent-card.json"
            ),
            timeout=5.0,
        )

        assert (
            card_response.status_code
            == 200
        )

        card = card_response.json()

        assert (
            card["name"]
            == "INNA A2A Gateway"
        )

        assert (
            card[
                "supportedInterfaces"
            ][0]["protocolBinding"]
            == "JSONRPC"
        )

        secret_marker = (
            "real-private-a2a-"
            "payload-456"
        )

        response = httpx.post(
            (
                base_url
                + "/a2a/jsonrpc/"
            ),
            json=_payload(
                secret_marker
            ),
            headers={
                "A2A-Version": "1.0",
            },
            timeout=10.0,
        )

        assert response.status_code == 200

        payload = response.json()

        assert "error" not in payload

        assert payload[
            "jsonrpc"
        ] == "2.0"

        result = payload["result"]

        message = result["message"]

        assert (
            message["role"]
            == "ROLE_AGENT"
        )

        response_text = (
            message["parts"][0]["text"]
        )

        assert response_text == (
            "INNA native A2A gateway "
            "received a text request."
        )

        assert (
            secret_marker
            not in response_text
        )

    finally:
        process.terminate()

        try:
            process.wait(
                timeout=8
            )
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(
                timeout=5
            )

    assert process.poll() is not None

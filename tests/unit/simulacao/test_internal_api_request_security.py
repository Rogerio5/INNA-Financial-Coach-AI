from __future__ import annotations

import json
import time
from typing import Annotated

import pytest
from fastapi import (
    Depends,
    FastAPI,
)
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    InternalRequestConfigurationError,
    InternalRequestSecurityError,
    TrustedRequestContext,
    assinar_requisicao_interna,
    require_trusted_request_context,
    verificar_requisicao_interna,
)


SECRET = (
    "0123456789abcdef"
    "0123456789abcdef"
    "secure-test-secret"
)


def _body(
    value: int = 7,
) -> bytes:
    return json.dumps(
        {
            "value": value,
        },
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )


def _signature(
    *,
    body: bytes,
    timestamp: int,
    user_id: str = "user-123",
    request_id: str = (
        "request-12345678"
    ),
) -> str:
    return assinar_requisicao_interna(
        method="POST",
        path="/secure",
        user_id=user_id,
        request_id=request_id,
        timestamp=timestamp,
        body=body,
        secret=SECRET,
    )


def test_signature_is_deterministic():
    timestamp = 1_700_000_000
    body = _body()

    first = _signature(
        body=body,
        timestamp=timestamp,
    )

    second = _signature(
        body=body,
        timestamp=timestamp,
    )

    assert first == second
    assert len(first) == 64


def test_signature_changes_when_body_changes():
    timestamp = 1_700_000_000

    assert _signature(
        body=_body(7),
        timestamp=timestamp,
    ) != _signature(
        body=_body(8),
        timestamp=timestamp,
    )


def test_signature_changes_when_user_changes():
    timestamp = 1_700_000_000
    body = _body()

    assert _signature(
        body=body,
        timestamp=timestamp,
        user_id="user-123",
    ) != _signature(
        body=body,
        timestamp=timestamp,
        user_id="user-456",
    )


def test_valid_request_returns_trusted_context():
    now = 1_700_000_000
    body = _body()

    context = (
        verificar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id="user-123",
            request_id=(
                "request-12345678"
            ),
            timestamp=now,
            signature=_signature(
                body=body,
                timestamp=now,
            ),
            body=body,
            secret=SECRET,
            now=now,
        )
    )

    assert context.user_id == "user-123"

    assert context.request_id == (
        "request-12345678"
    )


def test_expired_request_is_rejected():
    now = 1_700_000_000
    timestamp = now - 301
    body = _body()

    with pytest.raises(
        InternalRequestSecurityError
    ):
        verificar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id="user-123",
            request_id=(
                "request-12345678"
            ),
            timestamp=timestamp,
            signature=_signature(
                body=body,
                timestamp=timestamp,
            ),
            body=body,
            secret=SECRET,
            now=now,
            max_clock_skew_seconds=300,
        )


def test_future_request_is_rejected():
    now = 1_700_000_000
    timestamp = now + 301
    body = _body()

    with pytest.raises(
        InternalRequestSecurityError
    ):
        verificar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id="user-123",
            request_id=(
                "request-12345678"
            ),
            timestamp=timestamp,
            signature=_signature(
                body=body,
                timestamp=timestamp,
            ),
            body=body,
            secret=SECRET,
            now=now,
            max_clock_skew_seconds=300,
        )


def test_tampered_signature_is_rejected():
    now = 1_700_000_000
    body = _body()

    with pytest.raises(
        InternalRequestSecurityError
    ):
        verificar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id="user-123",
            request_id=(
                "request-12345678"
            ),
            timestamp=now,
            signature="0" * 64,
            body=body,
            secret=SECRET,
            now=now,
        )


@pytest.mark.parametrize(
    "user_id",
    [
        "",
        "user with spaces",
        "user\nheader",
        "x" * 161,
    ],
)
def test_invalid_user_id_is_rejected(
    user_id,
):
    body = _body()

    with pytest.raises(
        InternalRequestSecurityError
    ):
        assinar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id=user_id,
            request_id=(
                "request-12345678"
            ),
            timestamp=1_700_000_000,
            body=body,
            secret=SECRET,
        )


def test_short_secret_is_rejected():
    with pytest.raises(
        InternalRequestConfigurationError
    ):
        assinar_requisicao_interna(
            method="POST",
            path="/secure",
            user_id="user-123",
            request_id=(
                "request-12345678"
            ),
            timestamp=1_700_000_000,
            body=_body(),
            secret="short-secret",
        )


class Payload(
    BaseModel
):
    value: int


app = FastAPI()


@app.post("/secure")
async def secure_route(
    payload: Payload,
    context: Annotated[
        TrustedRequestContext,
        Depends(
            require_trusted_request_context
        ),
    ],
):
    return {
        "value": payload.value,
        "trusted_user_id": (
            context.user_id
        ),
        "request_id": (
            context.request_id
        ),
    }


client = TestClient(
    app
)


def _headers(
    *,
    body: bytes,
    timestamp: int,
    signature: str | None = None,
):
    return {
        "Content-Type": "application/json",
        HEADER_USER_ID: "user-123",
        HEADER_REQUEST_ID: (
            "request-12345678"
        ),
        HEADER_TIMESTAMP: str(
            timestamp
        ),
        HEADER_SIGNATURE: (
            signature
            or _signature(
                body=body,
                timestamp=timestamp,
            )
        ),
    }


def test_fastapi_dependency_accepts_signed_request(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    response = client.post(
        "/secure",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 200

    assert response.json() == {
        "value": 7,
        "trusted_user_id": "user-123",
        "request_id": (
            "request-12345678"
        ),
    }


def test_fastapi_dependency_rejects_missing_headers(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    response = client.post(
        "/secure",
        json={
            "value": 7,
        },
    )

    assert response.status_code == 401


def test_fastapi_dependency_rejects_tampered_body(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    original_body = _body(7)
    tampered_body = _body(8)

    timestamp = int(
        time.time()
    )

    response = client.post(
        "/secure",
        content=tampered_body,
        headers=_headers(
            body=original_body,
            timestamp=timestamp,
        ),
    )

    assert response.status_code == 401


def test_error_does_not_expose_signature(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    body = _body()
    timestamp = int(
        time.time()
    )

    invalid_signature = "0" * 64

    response = client.post(
        "/secure",
        content=body,
        headers=_headers(
            body=body,
            timestamp=timestamp,
            signature=invalid_signature,
        ),
    )

    assert response.status_code == 401

    assert invalid_signature not in (
        response.text
    )

    assert SECRET not in response.text

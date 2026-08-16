from __future__ import annotations

import json
import time
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.reliability_diagnostic_routes as routes
from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    assinar_requisicao_interna,
)

SECRET = (
    "0123456789abcdef"
    "0123456789abcdef"
    "reliability-diagnostic-test"
)

PATH = (
    "/internal/reliability/"
    "shared-provider/refresh"
)


def _enum(
    value: str,
):
    return SimpleNamespace(
        value=value
    )


class FakeProvider:
    def refresh_now(
        self,
        operation: str,
    ) -> bool:
        assert operation == (
            "gemini.generate.text_service"
        )
        return True

    def snapshot(
        self,
        operation: str,
    ):
        assert operation == (
            "gemini.generate.text_service"
        )

        return SimpleNamespace(
            operation=operation,
        )


def _distributed_snapshot():
    return SimpleNamespace(
        source=_enum(
            "shared_cache"
        ),
        shared_data_used=True,
        provider_enabled=True,
        cache_stale=False,
        database_unavailable=False,
        refresh_in_flight=False,
        evaluation=SimpleNamespace(
            state=_enum(
                "insufficient_data"
            ),
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            circuit_rejections=0,
        ),
    )


def _app():
    app = FastAPI()
    app.include_router(
        routes.router
    )
    return app


def _body() -> bytes:
    payload = {
        "operation": (
            "gemini.generate.text_service"
        ),
    }

    return json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _headers(
    *,
    body: bytes,
):
    timestamp = int(
        time.time()
    )

    user_id = (
        "reliability-admin"
    )

    request_id = (
        "reliability-smoke-12345678"
    )

    signature = (
        assinar_requisicao_interna(
            method="POST",
            path=PATH,
            user_id=user_id,
            request_id=request_id,
            timestamp=timestamp,
            body=body,
            secret=SECRET,
        )
    )

    return {
        "Content-Type": (
            "application/json"
        ),
        HEADER_USER_ID: user_id,
        HEADER_REQUEST_ID: request_id,
        HEADER_TIMESTAMP: str(
            timestamp
        ),
        HEADER_SIGNATURE: signature,
    }


def test_route_rejects_unsigned_request(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    client = TestClient(
        _app()
    )

    response = client.post(
        PATH,
        json={
            "operation": (
                "gemini.generate.text_service"
            ),
        },
    )

    assert response.status_code == 401


def test_route_returns_privacy_safe_shared_cache(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    monkeypatch.setattr(
        routes,
        "get_shared_reliability_provider",
        lambda: FakeProvider(),
    )

    monkeypatch.setattr(
        routes,
        "evaluate_distributed_reliability",
        lambda snapshot: (
            _distributed_snapshot()
        ),
    )

    body = _body()

    client = TestClient(
        _app()
    )

    response = client.post(
        PATH,
        content=body,
        headers=_headers(
            body=body
        ),
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload == {
        "operation": (
            "gemini.generate.text_service"
        ),
        "provider_enabled": True,
        "refresh_succeeded": True,
        "source": "shared_cache",
        "shared_data_used": True,
        "state": "insufficient_data",
        "total_operations": 0,
        "successful_operations": 0,
        "failed_operations": 0,
        "circuit_rejections": 0,
        "cache_stale": False,
        "database_unavailable": False,
        "refresh_in_flight": False,
    }

    serialized = response.text.lower()

    for forbidden in (
        "database_url",
        "secret",
        "signature",
        "prompt",
        "request_id",
        "user_id",
        "api_key",
    ):
        assert forbidden not in serialized


def test_route_sanitizes_internal_failure(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    def fail_provider():
        raise RuntimeError(
            "postgresql-secret-detail"
        )

    monkeypatch.setattr(
        routes,
        "get_shared_reliability_provider",
        fail_provider,
    )

    body = _body()

    client = TestClient(
        _app()
    )

    response = client.post(
        PATH,
        content=body,
        headers=_headers(
            body=body
        ),
    )

    assert response.status_code == 503

    assert (
        "postgresql-secret-detail"
        not in response.text
    )


def test_route_is_mounted_in_main(
    monkeypatch,
):
    from api.main import app

    monkeypatch.setenv(
        "INNA_INTERNAL_API_SIGNING_SECRET",
        SECRET,
    )

    client = TestClient(
        app
    )

    response = client.post(
        PATH,
        json={
            "operation": (
                "gemini.generate.text_service"
            ),
        },
    )

    # 401 prova simultaneamente:
    # - rota existe no app principal;
    # - método POST foi resolvido;
    # - dependency de segurança foi executada.
    #
    # Uma rota ausente retornaria 404.
    assert response.status_code == 401

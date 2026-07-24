from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from api.telegram_operational_status import (
    create_process_health_http_response,
)


def test_process_health_adapter_is_healthy():
    response = (
        create_process_health_http_response()
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "X-INNA-Operational-Status"
        ]
        == "healthy"
    )


def test_real_health_route_uses_new_contract():
    client = TestClient(
        app
    )

    response = client.get(
        "/health"
    )

    payload = response.json()

    assert response.status_code == 200

    assert payload == {
        "probe": "health",
        "ready": True,
        "schema_version": (
            "telegram-operational-status.v1"
        ),
        "status": "healthy",
    }


def test_health_has_operational_headers():
    client = TestClient(
        app
    )

    response = client.get(
        "/health"
    )

    assert (
        response.headers[
            "cache-control"
        ]
        == "no-store"
    )

    assert (
        response.headers[
            "x-content-type-options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "x-inna-schema-version"
        ]
        == (
            "telegram-operational-status.v1"
        )
    )

    assert (
        response.headers[
            "x-inna-operational-status"
        ]
        == "healthy"
    )

    assert (
        response.headers[
            "content-type"
        ].startswith(
            "application/json"
        )
    )


def test_health_does_not_expose_checks():
    client = TestClient(
        app
    )

    payload = client.get(
        "/health"
    ).json()

    assert "checks" not in payload
    assert "operational" not in payload
    assert "runtime" not in payload


def test_health_route_is_unique():
    health_routes = [
        route
        for route in app.routes
        if getattr(
            route,
            "path",
            None,
        ) == "/health"
    ]

    assert len(
        health_routes
    ) == 1


def test_health_is_visible_in_openapi():
    client = TestClient(
        app
    )

    schema = client.get(
        "/openapi.json"
    ).json()

    assert "/health" in schema[
        "paths"
    ]

    assert (
        "get"
        in schema["paths"]["/health"]
    )


def test_health_source_has_no_productive_probe():
    path = Path(
        "api/main.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    health_function = next(
        node
        for node in tree.body
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == "health_check"
        )
    )

    health_source = ast.get_source_segment(
        source,
        health_function,
    )

    assert health_source is not None

    forbidden = {
        "cursor_postgres",
        "create_productive_telegram_worker_readiness_service",
        "load_telegram_update_keyring_from_env",
        "load_telegram_processor",
        "claim_authenticated_telegram_update",
        "claim_next_authenticated_telegram_update_job_atomic",
        "enqueue_authenticated_telegram_update_atomic",
        "Gemini",
        "gemini",
    }

    for name in forbidden:
        assert name not in health_source


def test_liveness_implementation_has_no_mutating_calls():
    path = Path(
        "api/"
        "telegram_operational_status.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    forbidden = {
        "enqueue_authenticated_telegram_update_atomic",
        "claim_authenticated_telegram_update",
        "claim_next_authenticated_telegram_update_job_atomic",
        "complete_authenticated_telegram_update",
        "complete_authenticated_telegram_update_job_atomic",
        "fail_authenticated_telegram_update",
        "recover_expired_authenticated_telegram_update_jobs_atomic",
    }

    for name in forbidden:
        assert name not in source

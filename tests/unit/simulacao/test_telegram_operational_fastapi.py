from __future__ import annotations

import ast
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.telegram_operational_status import (
    INTERNAL_OPERATIONS_HEADER,
    TelegramOperationalRuntimeContainer,
    create_telegram_operational_router,
)
from src.services.telegram_observability import (
    CallableTelegramProbe,
    TelegramOperationalStatusService,
    TelegramReadinessRuntime,
    TelegramReadinessRuntimePolicy,
    TelegramOperationalConfiguration,
)


def create_runtime(
    *,
    passed=True,
    severity="required",
):
    service = TelegramOperationalStatusService(
        probes=(
            CallableTelegramProbe(
                name="database",
                severity=severity,
                check=lambda: passed,
                error_category="database",
            ),
        )
    )

    return TelegramReadinessRuntime(
        service,
        policy=TelegramReadinessRuntimePolicy(
            cache_ttl_seconds=10,
            concurrent_wait_seconds=0.25,
            evaluation_budget_seconds=2,
        ),
    )


def create_client(
    *,
    runtime=None,
    expected_token="test-operations-token",
):
    runtime = (
        runtime
        or create_runtime()
    )

    container = (
        TelegramOperationalRuntimeContainer(
            readiness_runtime_factory=(
                lambda: runtime
            )
        )
    )

    app = FastAPI()

    app.include_router(
        create_telegram_operational_router(
            container=container,
            token_supplier=(
                lambda: expected_token
            ),
        )
    )

    return (
        TestClient(app),
        container,
    )


def test_ready_healthy_returns_200():
    client, _ = create_client()

    response = client.get(
        "/ready"
    )

    payload = response.json()

    assert response.status_code == 200

    assert payload[
        "probe"
    ] == "readiness"

    assert payload[
        "status"
    ] == "healthy"

    assert payload[
        "ready"
    ] is True


def test_ready_degraded_returns_200():
    client, _ = create_client(
        runtime=create_runtime(
            passed=False,
            severity="optional",
        )
    )

    response = client.get(
        "/ready"
    )

    assert response.status_code == 200

    assert response.json()[
        "status"
    ] == "degraded"


def test_ready_unready_returns_503():
    client, _ = create_client(
        runtime=create_runtime(
            passed=False,
        )
    )

    response = client.get(
        "/ready"
    )

    assert response.status_code == 503

    assert response.json()[
        "status"
    ] == "unready"


def test_public_ready_does_not_expose_checks():
    client, _ = create_client()

    payload = client.get(
        "/ready"
    ).json()

    assert "operational" not in payload
    assert "checks" not in payload


def test_internal_ready_requires_token():
    client, _ = create_client()

    response = client.get(
        "/internal/ready"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Unauthorized",
    }


def test_internal_ready_rejects_wrong_token():
    client, _ = create_client()

    response = client.get(
        "/internal/ready",
        headers={
            INTERNAL_OPERATIONS_HEADER: (
                "wrong-token"
            ),
        },
    )

    assert response.status_code == 401


def test_internal_ready_accepts_correct_token():
    client, _ = create_client()

    response = client.get(
        "/internal/ready",
        headers={
            INTERNAL_OPERATIONS_HEADER: (
                "test-operations-token"
            ),
        },
    )

    payload = response.json()

    assert response.status_code == 200

    assert "runtime" in payload
    assert "operational" in payload

    assert payload[
        "operational"
    ]["checks"]


def test_internal_route_is_hidden_from_openapi():
    client, _ = create_client()

    schema = client.get(
        "/openapi.json"
    ).json()

    assert "/ready" in schema[
        "paths"
    ]

    assert (
        "/internal/ready"
        not in schema["paths"]
    )


def test_operational_headers_are_preserved():
    client, _ = create_client()

    response = client.get(
        "/ready"
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
            "x-inna-operational-status"
        ]
        == "healthy"
    )

    assert (
        response.headers[
            "x-inna-schema-version"
        ]
        == (
            "telegram-operational-status.v1"
        )
    )


def test_runtime_is_singleton_per_container():
    calls = {
        "count": 0,
    }

    runtime = create_runtime()

    def factory():
        calls[
            "count"
        ] += 1

        return runtime

    container = (
        TelegramOperationalRuntimeContainer(
            readiness_runtime_factory=factory
        )
    )

    first = (
        container
        .get_readiness_runtime()
    )

    second = (
        container
        .get_readiness_runtime()
    )

    assert first is second
    assert calls["count"] == 1


def test_container_reset_recreates_runtime():
    calls = {
        "count": 0,
    }

    def factory():
        calls[
            "count"
        ] += 1

        return create_runtime()

    container = (
        TelegramOperationalRuntimeContainer(
            readiness_runtime_factory=factory
        )
    )

    first = (
        container
        .get_readiness_runtime()
    )

    container.reset()

    second = (
        container
        .get_readiness_runtime()
    )

    assert first is not second
    assert calls["count"] == 2


def test_runtime_factory_failure_fails_closed():
    def broken_factory():
        raise RuntimeError(
            "postgresql://user:password@private"
        )

    container = (
        TelegramOperationalRuntimeContainer(
            readiness_runtime_factory=(
                broken_factory
            )
        )
    )

    app = FastAPI()

    app.include_router(
        create_telegram_operational_router(
            container=container,
            token_supplier=(
                lambda: "token"
            ),
        )
    )

    client = TestClient(
        app
    )

    response = client.get(
        "/ready"
    )

    assert response.status_code == 503

    assert (
        response.json()["reason"]
        == "response_serialization_failure"
    )

    assert "password" not in response.text
    assert "postgresql://" not in response.text


def test_internal_token_is_not_exposed():
    private_token = (
        "private-operations-secret"
    )

    client, _ = create_client(
        expected_token=private_token
    )

    response = client.get(
        "/internal/ready",
        headers={
            INTERNAL_OPERATIONS_HEADER: (
                "incorrect"
            ),
        },
    )

    assert response.status_code == 401
    assert private_token not in response.text


def test_router_source_uses_constant_time_comparison():
    path = Path(
        "api/"
        "telegram_operational_status.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    calls = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if isinstance(
            node.func,
            ast.Attribute,
        ):
            calls.append(
                (
                    node.func.attr,
                    node.lineno,
                )
            )

    assert any(
        name == "compare_digest"
        for name, _ in calls
    )


def test_router_has_no_mutating_job_calls():
    path = Path(
        "api/"
        "telegram_operational_status.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    forbidden = {
        "claim_next_authenticated_telegram_update_job_atomic",
        "claim_authenticated_telegram_update",
        "enqueue_authenticated_telegram_update_atomic",
        "complete_authenticated_telegram_update_job_atomic",
        "complete_authenticated_telegram_update",
        "fail_authenticated_telegram_update",
        "recover_expired_authenticated_telegram_update_jobs_atomic",
    }

    for name in forbidden:
        assert name not in source

def test_internal_route_disabled_returns_404():
    runtime = create_runtime()

    container = (
        TelegramOperationalRuntimeContainer(
            readiness_runtime_factory=(
                lambda: runtime
            )
        )
    )

    app = FastAPI()

    app.include_router(
        create_telegram_operational_router(
            container=container,
            configuration_supplier=(
                lambda: (
                    TelegramOperationalConfiguration(
                        internal_route_enabled=False,
                    )
                )
            ),
        )
    )

    client = TestClient(
        app
    )

    response = client.get(
        "/internal/ready",
        headers={
            INTERNAL_OPERATIONS_HEADER: (
                "any-token"
            ),
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Not Found",
    }


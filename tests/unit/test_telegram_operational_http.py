from __future__ import annotations

import json
from types import MappingProxyType

import pytest

from src.services.telegram_observability import (
    TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE,
    TELEGRAM_OPERATIONAL_SCHEMA_VERSION,
    CallableTelegramProbe,
    TelegramOperationalHttpResponse,
    TelegramOperationalProbeKind,
    TelegramOperationalStatusService,
    TelegramOperationalVisibility,
    TelegramReadinessRuntime,
    create_runtime_http_response,
    create_safe_runtime_http_response,
    create_snapshot_http_response,
)


def runtime_result(
    *,
    passed=True,
    severity="required",
):
    service = (
        TelegramOperationalStatusService(
            probes=(
                CallableTelegramProbe(
                    name="database",
                    severity=severity,
                    check=lambda: passed,
                    error_category="database",
                ),
            )
        )
    )

    return (
        TelegramReadinessRuntime(
            service
        )
        .evaluate()
    )


def decode(
    response,
):
    return json.loads(
        response.body
    )


def test_healthy_response_is_200():
    response = (
        create_runtime_http_response(
            runtime_result()
        )
    )

    payload = decode(
        response
    )

    assert response.status_code == 200

    assert (
        response.content_type
        == TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE
    )

    assert (
        payload["schema_version"]
        == TELEGRAM_OPERATIONAL_SCHEMA_VERSION
    )

    assert payload[
        "status"
    ] == "healthy"

    assert payload[
        "ready"
    ] is True


def test_degraded_response_is_200():
    response = (
        create_runtime_http_response(
            runtime_result(
                passed=False,
                severity="optional",
            )
        )
    )

    payload = decode(
        response
    )

    assert response.status_code == 200

    assert payload[
        "status"
    ] == "degraded"

    assert payload[
        "ready"
    ] is True


def test_unready_response_is_503():
    response = (
        create_runtime_http_response(
            runtime_result(
                passed=False,
            )
        )
    )

    payload = decode(
        response
    )

    assert response.status_code == 503

    assert payload[
        "status"
    ] == "unready"

    assert payload[
        "ready"
    ] is False


def test_public_response_has_no_checks():
    response = (
        create_runtime_http_response(
            runtime_result()
        )
    )

    payload = decode(
        response
    )

    assert "operational" not in payload
    assert "checks" not in payload


def test_internal_response_contains_checks():
    response = (
        create_runtime_http_response(
            runtime_result(),
            visibility="internal",
        )
    )

    payload = decode(
        response
    )

    assert (
        payload["operational"][
            "checks"
        ]
    )

    assert (
        payload["runtime"][
            "sequence"
        ]
        == 1
    )


def test_health_probe_kind():
    response = (
        create_runtime_http_response(
            runtime_result(),
            probe="health",
        )
    )

    assert decode(
        response
    )["probe"] == "health"


def test_snapshot_response():
    result = runtime_result()

    response = (
        create_snapshot_http_response(
            result.snapshot,
            probe="health",
            visibility="internal",
        )
    )

    payload = decode(
        response
    )

    assert response.status_code == 200
    assert payload[
        "probe"
    ] == "health"

    assert "operational" in payload


def test_security_headers():
    response = (
        create_runtime_http_response(
            runtime_result()
        )
    )

    assert (
        response.headers[
            "Cache-Control"
        ]
        == "no-store"
    )

    assert (
        response.headers[
            "X-Content-Type-Options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "X-INNA-Schema-Version"
        ]
        == TELEGRAM_OPERATIONAL_SCHEMA_VERSION
    )

    assert (
        response.headers[
            "X-INNA-Operational-Status"
        ]
        == "healthy"
    )


def test_headers_are_immutable():
    response = (
        create_runtime_http_response(
            runtime_result()
        )
    )

    assert isinstance(
        response.headers,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError
    ):
        response.headers[
            "Cache-Control"
        ] = "public"


def test_json_is_deterministic():
    result = runtime_result()

    first = (
        create_runtime_http_response(
            result,
            visibility="internal",
        )
    )

    second = (
        create_runtime_http_response(
            result,
            visibility="internal",
        )
    )

    assert first.body == second.body


def test_json_ends_with_newline():
    response = (
        create_runtime_http_response(
            runtime_result()
        )
    )

    assert response.body.endswith(
        "\n"
    )


def test_exception_text_is_not_exposed():
    def broken():
        raise RuntimeError(
            "postgresql://user:password@private"
        )

    service = (
        TelegramOperationalStatusService(
            probes=(
                CallableTelegramProbe(
                    name="database",
                    severity="required",
                    check=broken,
                    error_category="database",
                ),
            )
        )
    )

    result = (
        TelegramReadinessRuntime(
            service
        )
        .evaluate()
    )

    response = (
        create_runtime_http_response(
            result,
            visibility="internal",
        )
    )

    assert "password" not in response.body
    assert "postgresql://" not in response.body
    assert "private" not in response.body


def test_safe_adapter_fails_closed():
    response = (
        create_safe_runtime_http_response(
            object()
        )
    )

    payload = decode(
        response
    )

    assert response.status_code == 503

    assert payload[
        "status"
    ] == "unready"

    assert payload[
        "ready"
    ] is False

    assert (
        payload["reason"]
        == "response_serialization_failure"
    )


def test_safe_adapter_does_not_expose_repr():
    class PrivateObject:
        def __repr__(
            self,
        ):
            return (
                "TELEGRAM_BOT_TOKEN="
                "private-secret"
            )

    response = (
        create_safe_runtime_http_response(
            PrivateObject()
        )
    )

    assert (
        "private-secret"
        not in response.body
    )

    assert (
        "TELEGRAM_BOT_TOKEN"
        not in response.body
    )


@pytest.mark.parametrize(
    "status_code",
    [
        0,
        99,
        600,
        999,
    ],
)
def test_invalid_http_status(
    status_code,
):
    with pytest.raises(
        ValueError
    ):
        TelegramOperationalHttpResponse(
            status_code=status_code,
            body="{}\n",
            content_type=(
                TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE
            ),
            headers={},
        )


@pytest.mark.parametrize(
    "probe",
    [
        "unknown",
        "",
        "metrics",
    ],
)
def test_unknown_probe(
    probe,
):
    with pytest.raises(
        ValueError
    ):
        create_runtime_http_response(
            runtime_result(),
            probe=probe,
        )


@pytest.mark.parametrize(
    "visibility",
    [
        "private",
        "admin",
        "",
    ],
)
def test_unknown_visibility(
    visibility,
):
    with pytest.raises(
        ValueError
    ):
        create_runtime_http_response(
            runtime_result(),
            visibility=visibility,
        )


def test_enum_contracts():
    assert (
        TelegramOperationalProbeKind
        .HEALTH.value
        == "health"
    )

    assert (
        TelegramOperationalProbeKind
        .READINESS.value
        == "readiness"
    )

    assert (
        TelegramOperationalVisibility
        .PUBLIC.value
        == "public"
    )

    assert (
        TelegramOperationalVisibility
        .INTERNAL.value
        == "internal"
    )

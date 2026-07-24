from __future__ import annotations

import hmac
import threading
from collections.abc import Callable

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
)
from starlette.responses import Response

from src.services.telegram_observability import (
    CallableTelegramProbe,
    TelegramOperationalConfiguration,
    TelegramOperationalHttpResponse,
    TelegramOperationalStatusService,
    TelegramReadinessRuntime,
    TelegramReadinessRuntimePolicy,
    create_productive_telegram_worker_readiness_service,
    create_runtime_http_response,
    create_safe_runtime_http_response,
    create_snapshot_http_response,
    load_telegram_operational_configuration,
)


INTERNAL_OPERATIONS_HEADER = (
    "X-INNA-Operations-Token"
)


ReadinessRuntimeFactory = Callable[
    [],
    TelegramReadinessRuntime,
]

ConfigurationSupplier = Callable[
    [],
    TelegramOperationalConfiguration,
]

TokenSupplier = Callable[
    [],
    str | None,
]


def _default_configuration_supplier(
) -> TelegramOperationalConfiguration:
    return (
        load_telegram_operational_configuration()
    )


def _default_readiness_runtime_factory(
) -> TelegramReadinessRuntime:
    configuration = (
        _default_configuration_supplier()
    )

    service = (
        create_productive_telegram_worker_readiness_service()
    )

    return TelegramReadinessRuntime(
        service,
        policy=TelegramReadinessRuntimePolicy(
            cache_ttl_seconds=(
                configuration
                .readiness_cache_ttl_seconds
            ),
            concurrent_wait_seconds=(
                configuration
                .readiness_concurrent_wait_seconds
            ),
            evaluation_budget_seconds=(
                configuration
                .readiness_evaluation_budget_seconds
            ),
        ),
    )


class TelegramOperationalRuntimeContainer:
    def __init__(
        self,
        *,
        readiness_runtime_factory: (
            ReadinessRuntimeFactory
        ) = (
            _default_readiness_runtime_factory
        ),
    ) -> None:
        self._readiness_runtime_factory = (
            readiness_runtime_factory
        )

        self._lock = threading.RLock()

        self._readiness_runtime: (
            TelegramReadinessRuntime
            | None
        ) = None

    def get_readiness_runtime(
        self,
    ) -> TelegramReadinessRuntime:
        with self._lock:
            if (
                self._readiness_runtime
                is None
            ):
                self._readiness_runtime = (
                    self
                    ._readiness_runtime_factory()
                )

            return self._readiness_runtime

    def reset(
        self,
    ) -> None:
        with self._lock:
            self._readiness_runtime = None


def _to_starlette_response(
    response: TelegramOperationalHttpResponse,
) -> Response:
    headers = dict(
        response.headers
    )

    headers[
        "Content-Type"
    ] = response.content_type

    return Response(
        content=response.body,
        status_code=response.status_code,
        headers=headers,
    )


def create_process_health_http_response(
) -> TelegramOperationalHttpResponse:
    try:
        service = (
            TelegramOperationalStatusService(
                probes=(
                    CallableTelegramProbe(
                        name="process",
                        severity="required",
                        check=lambda: {
                            "passed": True,
                            "process_alive": True,
                        },
                    ),
                )
            )
        )

        return create_snapshot_http_response(
            service.evaluate(),
            probe="health",
            visibility="public",
        )

    except Exception:
        return create_safe_runtime_http_response(
            object(),
            probe="health",
            visibility="public",
        )


def create_process_health_starlette_response(
) -> Response:
    return _to_starlette_response(
        create_process_health_http_response()
    )


def _normalized_token(
    value: str | None,
) -> str:
    return str(
        value
        or ""
    ).strip()


def _authorize_internal_request(
    *,
    route_enabled: bool,
    supplied_token: str | None,
    expected_token: str | None,
) -> None:
    if not route_enabled:
        raise HTTPException(
            status_code=404,
            detail="Not Found",
            headers={
                "Cache-Control": "no-store",
            },
        )

    supplied = _normalized_token(
        supplied_token
    )

    expected = _normalized_token(
        expected_token
    )

    authorized = (
        bool(expected)
        and bool(supplied)
        and hmac.compare_digest(
            supplied,
            expected,
        )
    )

    if not authorized:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={
                "Cache-Control": "no-store",
                "WWW-Authenticate": (
                    "INNA-Operations-Token"
                ),
            },
        )


def create_telegram_operational_router(
    *,
    container: (
        TelegramOperationalRuntimeContainer
        | None
    ) = None,
    configuration_supplier: (
        ConfigurationSupplier
        | None
    ) = None,
    token_supplier: (
        TokenSupplier
        | None
    ) = None,
) -> APIRouter:
    resolved_container = (
        container
        or TelegramOperationalRuntimeContainer()
    )

    resolved_configuration_supplier = (
        configuration_supplier
        or _default_configuration_supplier
    )

    injected_token_mode = (
        token_supplier is not None
        and configuration_supplier is None
    )

    router = APIRouter(
        tags=[
            "Operational Status",
        ],
    )

    @router.get(
        "/ready",
        include_in_schema=True,
        summary=(
            "Readiness público do worker Telegram"
        ),
        responses={
            200: {
                "description": (
                    "Worker saudável ou degradado."
                ),
            },
            503: {
                "description": (
                    "Worker indisponível."
                ),
            },
        },
    )
    def telegram_readiness(
    ) -> Response:
        try:
            runtime = (
                resolved_container
                .get_readiness_runtime()
            )

            response = (
                create_runtime_http_response(
                    runtime.evaluate(),
                    probe="readiness",
                    visibility="public",
                )
            )

        except Exception:
            response = (
                create_safe_runtime_http_response(
                    object(),
                    probe="readiness",
                    visibility="public",
                )
            )

        return _to_starlette_response(
            response
        )

    @router.get(
        "/internal/ready",
        include_in_schema=False,
    )
    def telegram_internal_readiness(
        x_inna_operations_token: (
            str | None
        ) = Header(
            default=None,
            alias=(
                INTERNAL_OPERATIONS_HEADER
            ),
        ),
    ) -> Response:
        if injected_token_mode:
            route_enabled = True

            expected_token = (
                token_supplier()
                if token_supplier is not None
                else None
            )

        else:
            try:
                configuration = (
                    resolved_configuration_supplier()
                )
            except Exception:
                raise HTTPException(
                    status_code=404,
                    detail="Not Found",
                    headers={
                        "Cache-Control": "no-store",
                    },
                )

            route_enabled = (
                configuration
                .internal_route_enabled
            )

            expected_token = (
                configuration
                .internal_operations_token
            )

        _authorize_internal_request(
            route_enabled=route_enabled,
            supplied_token=(
                x_inna_operations_token
            ),
            expected_token=expected_token,
        )

        try:
            runtime = (
                resolved_container
                .get_readiness_runtime()
            )

            response = (
                create_runtime_http_response(
                    runtime.evaluate(),
                    probe="readiness",
                    visibility="internal",
                )
            )

        except Exception:
            response = (
                create_safe_runtime_http_response(
                    object(),
                    probe="readiness",
                    visibility="internal",
                )
            )

        return _to_starlette_response(
            response
        )

    return router


operational_status_container = (
    TelegramOperationalRuntimeContainer()
)

router = create_telegram_operational_router(
    container=operational_status_container,
)


__all__ = [
    "INTERNAL_OPERATIONS_HEADER",
    "TelegramOperationalRuntimeContainer",
    "create_process_health_http_response",
    "create_process_health_starlette_response",
    "create_telegram_operational_router",
    "operational_status_container",
    "router",
]

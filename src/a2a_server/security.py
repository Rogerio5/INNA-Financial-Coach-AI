"""Segurança HTTP do gateway A2A nativo da INNA."""

from __future__ import annotations

import hmac
import os
from collections.abc import Callable

from starlette.responses import JSONResponse
from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)

INNA_A2A_CLIENT_TOKEN_ENV = (
    "INNA_A2A_CLIENT_TOKEN"
)

MIN_A2A_CLIENT_TOKEN_LENGTH = 32

A2A_AUTH_UNAVAILABLE_MESSAGE = (
    "A2A authentication unavailable."
)

A2A_UNAUTHORIZED_MESSAGE = (
    "Unauthorized."
)


def load_a2a_client_token() -> str | None:
    """Carrega token A2A sem expor seu conteúdo."""

    raw = os.getenv(
        INNA_A2A_CLIENT_TOKEN_ENV,
        "",
    )

    token = raw.strip()

    if (
        not token
        or len(token)
        < MIN_A2A_CLIENT_TOKEN_LENGTH
    ):
        return None

    return token


def _extract_bearer_token(
    scope: Scope,
) -> str | None:
    headers = dict(
        scope.get(
            "headers",
            [],
        )
    )

    raw_header = headers.get(
        b"authorization"
    )

    if raw_header is None:
        return None

    try:
        authorization = raw_header.decode(
            "latin-1"
        )
    except Exception:
        return None

    scheme, separator, value = (
        authorization.partition(" ")
    )

    if (
        not separator
        or scheme.lower() != "bearer"
    ):
        return None

    token = value.strip()

    if not token:
        return None

    return token


class A2AAuthenticationMiddleware:
    """Protege somente operações JSON-RPC A2A."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        protected_path: str,
        token_supplier: (
            Callable[[], str | None]
        ) = load_a2a_client_token,
    ) -> None:
        self._app = app
        self._protected_path = (
            protected_path
        )
        self._token_supplier = (
            token_supplier
        )

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope.get("path")
            != self._protected_path
        ):
            await self._app(
                scope,
                receive,
                send,
            )
            return

        expected_token = (
            self._token_supplier()
        )

        if expected_token is None:
            response = JSONResponse(
                {
                    "error": (
                        A2A_AUTH_UNAVAILABLE_MESSAGE
                    ),
                },
                status_code=503,
            )

            await response(
                scope,
                receive,
                send,
            )
            return

        provided_token = (
            _extract_bearer_token(
                scope
            )
        )

        if (
            provided_token is None
            or not hmac.compare_digest(
                provided_token,
                expected_token,
            )
        ):
            response = JSONResponse(
                {
                    "error": (
                        A2A_UNAUTHORIZED_MESSAGE
                    ),
                },
                status_code=401,
                headers={
                    "WWW-Authenticate": (
                        "Bearer"
                    ),
                },
            )

            await response(
                scope,
                receive,
                send,
            )
            return

        await self._app(
            scope,
            receive,
            send,
        )


__all__ = [
    "A2A_AUTH_UNAVAILABLE_MESSAGE",
    "A2A_UNAUTHORIZED_MESSAGE",
    "A2AAuthenticationMiddleware",
    "INNA_A2A_CLIENT_TOKEN_ENV",
    "MIN_A2A_CLIENT_TOKEN_LENGTH",
    "load_a2a_client_token",
]

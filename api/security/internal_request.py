from __future__ import annotations

import hashlib
import hmac
import os
import re
import time
from dataclasses import dataclass
from typing import Annotated

from fastapi import (
    Header,
    HTTPException,
    Request,
    status,
)


SIGNATURE_VERSION = "v1"

HEADER_USER_ID = "X-INNA-User-ID"
HEADER_REQUEST_ID = "X-INNA-Request-ID"
HEADER_TIMESTAMP = "X-INNA-Timestamp"
HEADER_SIGNATURE = "X-INNA-Signature"

DEFAULT_MAX_CLOCK_SKEW_SECONDS = 300

USER_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._:@-]{1,160}$"
)

REQUEST_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._:-]{8,200}$"
)

SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)


class InternalRequestSecurityError(
    RuntimeError
):
    """
    Requisição interna inválida ou não autenticada.
    """


class InternalRequestConfigurationError(
    RuntimeError
):
    """
    Configuração de assinatura ausente ou insegura.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TrustedRequestContext:
    user_id: str
    request_id: str
    timestamp: int

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "authenticated": True,
        }


def calcular_hash_corpo(
    body: bytes,
) -> str:
    if not isinstance(
        body,
        bytes,
    ):
        raise TypeError(
            "body deve ser bytes."
        )

    return hashlib.sha256(
        body
    ).hexdigest()


def _normalizar_metodo(
    method: str,
) -> str:
    normalized = str(
        method or ""
    ).strip().upper()

    if (
        not normalized
        or not normalized.isalpha()
    ):
        raise InternalRequestSecurityError(
            "Método HTTP inválido."
        )

    return normalized


def _normalizar_caminho(
    path: str,
) -> str:
    normalized = str(
        path or ""
    ).strip()

    if (
        not normalized.startswith("/")
        or "\n" in normalized
        or "\r" in normalized
    ):
        raise InternalRequestSecurityError(
            "Caminho da requisição inválido."
        )

    return normalized


def _normalizar_usuario_id(
    user_id: str,
) -> str:
    normalized = str(
        user_id or ""
    ).strip()

    if not USER_ID_PATTERN.fullmatch(
        normalized
    ):
        raise InternalRequestSecurityError(
            "Identidade interna inválida."
        )

    return normalized


def _normalizar_request_id(
    request_id: str,
) -> str:
    normalized = str(
        request_id or ""
    ).strip()

    if not REQUEST_ID_PATTERN.fullmatch(
        normalized
    ):
        raise InternalRequestSecurityError(
            "Identificador de requisição inválido."
        )

    return normalized


def _normalizar_timestamp(
    timestamp_value: str | int,
) -> int:
    try:
        timestamp = int(
            timestamp_value
        )
    except (
        TypeError,
        ValueError,
    ):
        raise InternalRequestSecurityError(
            "Timestamp da requisição inválido."
        ) from None

    if timestamp < 1:
        raise InternalRequestSecurityError(
            "Timestamp da requisição inválido."
        )

    return timestamp


def _normalizar_body_sha256(
    body_sha256: str,
) -> str:
    normalized = str(
        body_sha256 or ""
    ).strip().lower()

    if not SHA256_PATTERN.fullmatch(
        normalized
    ):
        raise InternalRequestSecurityError(
            "Hash do corpo inválido."
        )

    return normalized


def obter_segredo_assinatura(
    explicit_secret: str | None = None,
) -> bytes:
    raw_secret = (
        explicit_secret
        if explicit_secret is not None
        else os.getenv(
            "INNA_INTERNAL_API_SIGNING_SECRET",
            "",
        )
    )

    if not isinstance(
        raw_secret,
        str,
    ):
        raise InternalRequestConfigurationError(
            "Segredo de assinatura inválido."
        )

    secret = raw_secret.encode(
        "utf-8"
    )

    if len(secret) < 32:
        raise InternalRequestConfigurationError(
            "O segredo de assinatura interna "
            "deve possuir pelo menos 32 bytes."
        )

    return secret


def obter_clock_skew_maximo() -> int:
    raw_value = str(
        os.getenv(
            (
                "INNA_INTERNAL_API_MAX_"
                "CLOCK_SKEW_SECONDS"
            ),
            DEFAULT_MAX_CLOCK_SKEW_SECONDS,
        )
    ).strip()

    try:
        value = int(
            raw_value
        )
    except ValueError:
        return (
            DEFAULT_MAX_CLOCK_SKEW_SECONDS
        )

    if not 30 <= value <= 900:
        return (
            DEFAULT_MAX_CLOCK_SKEW_SECONDS
        )

    return value


def montar_mensagem_assinatura(
    *,
    method: str,
    path: str,
    user_id: str,
    request_id: str,
    timestamp: str | int,
    body_sha256: str,
) -> bytes:
    normalized_method = (
        _normalizar_metodo(
            method
        )
    )

    normalized_path = (
        _normalizar_caminho(
            path
        )
    )

    normalized_user_id = (
        _normalizar_usuario_id(
            user_id
        )
    )

    normalized_request_id = (
        _normalizar_request_id(
            request_id
        )
    )

    normalized_timestamp = (
        _normalizar_timestamp(
            timestamp
        )
    )

    normalized_body_hash = (
        _normalizar_body_sha256(
            body_sha256
        )
    )

    canonical = "\n".join([
        SIGNATURE_VERSION,
        normalized_method,
        normalized_path,
        normalized_user_id,
        normalized_request_id,
        str(
            normalized_timestamp
        ),
        normalized_body_hash,
    ])

    return canonical.encode(
        "utf-8"
    )


def assinar_requisicao_interna(
    *,
    method: str,
    path: str,
    user_id: str,
    request_id: str,
    timestamp: str | int,
    body: bytes,
    secret: str | None = None,
) -> str:
    key = obter_segredo_assinatura(
        secret
    )

    message = montar_mensagem_assinatura(
        method=method,
        path=path,
        user_id=user_id,
        request_id=request_id,
        timestamp=timestamp,
        body_sha256=calcular_hash_corpo(
            body
        ),
    )

    return hmac.new(
        key,
        message,
        hashlib.sha256,
    ).hexdigest()


def verificar_requisicao_interna(
    *,
    method: str,
    path: str,
    user_id: str,
    request_id: str,
    timestamp: str | int,
    signature: str,
    body: bytes,
    secret: str | None = None,
    now: int | None = None,
    max_clock_skew_seconds: int | None = None,
) -> TrustedRequestContext:
    normalized_timestamp = (
        _normalizar_timestamp(
            timestamp
        )
    )

    current_time = int(
        time.time()
        if now is None
        else now
    )

    max_skew = (
        obter_clock_skew_maximo()
        if max_clock_skew_seconds is None
        else int(
            max_clock_skew_seconds
        )
    )

    if max_skew < 1:
        raise InternalRequestSecurityError(
            "Janela de tempo inválida."
        )

    if abs(
        current_time
        - normalized_timestamp
    ) > max_skew:
        raise InternalRequestSecurityError(
            "Requisição interna expirada."
        )

    normalized_signature = str(
        signature or ""
    ).strip().lower()

    if not SHA256_PATTERN.fullmatch(
        normalized_signature
    ):
        raise InternalRequestSecurityError(
            "Assinatura interna inválida."
        )

    expected_signature = (
        assinar_requisicao_interna(
            method=method,
            path=path,
            user_id=user_id,
            request_id=request_id,
            timestamp=(
                normalized_timestamp
            ),
            body=body,
            secret=secret,
        )
    )

    if not hmac.compare_digest(
        normalized_signature,
        expected_signature,
    ):
        raise InternalRequestSecurityError(
            "Assinatura interna inválida."
        )

    return TrustedRequestContext(
        user_id=_normalizar_usuario_id(
            user_id
        ),
        request_id=(
            _normalizar_request_id(
                request_id
            )
        ),
        timestamp=(
            normalized_timestamp
        ),
    )


async def require_trusted_request_context(
    request: Request,
    user_id: Annotated[
        str | None,
        Header(
            alias=HEADER_USER_ID,
        ),
    ] = None,
    request_id: Annotated[
        str | None,
        Header(
            alias=HEADER_REQUEST_ID,
        ),
    ] = None,
    timestamp: Annotated[
        str | None,
        Header(
            alias=HEADER_TIMESTAMP,
        ),
    ] = None,
    signature: Annotated[
        str | None,
        Header(
            alias=HEADER_SIGNATURE,
        ),
    ] = None,
) -> TrustedRequestContext:
    if not all([
        user_id,
        request_id,
        timestamp,
        signature,
    ]):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Requisição interna não autenticada."
            ),
        )

    try:
        body = await request.body()

        context = (
            verificar_requisicao_interna(
                method=request.method,
                path=request.url.path,
                user_id=user_id,
                request_id=request_id,
                timestamp=timestamp,
                signature=signature,
                body=body,
            )
        )

    except InternalRequestConfigurationError:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Autenticação interna indisponível."
            ),
        ) from None

    except InternalRequestSecurityError:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Requisição interna não autenticada."
            ),
        ) from None

    request.state.trusted_context = (
        context
    )

    return context


__all__ = [
    "HEADER_REQUEST_ID",
    "HEADER_SIGNATURE",
    "HEADER_TIMESTAMP",
    "HEADER_USER_ID",
    "InternalRequestConfigurationError",
    "InternalRequestSecurityError",
    "TrustedRequestContext",
    "assinar_requisicao_interna",
    "calcular_hash_corpo",
    "montar_mensagem_assinatura",
    "require_trusted_request_context",
    "verificar_requisicao_interna",
]

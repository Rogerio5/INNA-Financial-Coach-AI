"""Cliente Redis compartilhado e fail-open da INNA."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import redis
from redis import Redis
from redis.exceptions import RedisError

log = logging.getLogger(__name__)

REDIS_URL_ENV = "INNA_REDIS_URL"

DEFAULT_SOCKET_CONNECT_TIMEOUT_SECONDS = 1.0
DEFAULT_SOCKET_TIMEOUT_SECONDS = 1.0


def _read_float_env(
    name: str,
    default: float,
    *,
    minimum: float,
    maximum: float,
) -> float:
    raw = str(os.getenv(name, "") or "").strip()

    if not raw:
        return default

    try:
        value = float(raw)
    except ValueError:
        return default

    return max(
        minimum,
        min(value, maximum),
    )


def is_redis_configured() -> bool:
    """Retorna True somente quando a URL Redis está configurada."""
    return bool(
        str(
            os.getenv(
                REDIS_URL_ENV,
                "",
            )
            or ""
        ).strip()
    )


@lru_cache(maxsize=1)
def get_redis_client() -> Redis | None:
    """
    Cria o cliente Redis compartilhado.

    Fail-open:
    ausência de configuração não impede a aplicação de iniciar.
    """
    redis_url = str(
        os.getenv(
            REDIS_URL_ENV,
            "",
        )
        or ""
    ).strip()

    if not redis_url:
        return None

    connect_timeout = _read_float_env(
        "INNA_REDIS_CONNECT_TIMEOUT_SECONDS",
        DEFAULT_SOCKET_CONNECT_TIMEOUT_SECONDS,
        minimum=0.1,
        maximum=10.0,
    )

    socket_timeout = _read_float_env(
        "INNA_REDIS_SOCKET_TIMEOUT_SECONDS",
        DEFAULT_SOCKET_TIMEOUT_SECONDS,
        minimum=0.1,
        maximum=10.0,
    )

    try:
        return redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=connect_timeout,
            socket_timeout=socket_timeout,
            health_check_interval=30,
        )
    except Exception:
        log.warning(
            "Falha ao criar cliente Redis; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return None


def ping_redis() -> bool:
    """
    Testa conectividade Redis sem derrubar a aplicação em caso de falha.
    """
    client = get_redis_client()

    if client is None:
        return False

    try:
        return bool(client.ping())
    except RedisError:
        log.warning(
            "Redis indisponível; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return False


def reset_redis_client() -> None:
    """Limpa o cliente em cache, principalmente para testes."""
    get_redis_client.cache_clear()

"""Infraestrutura compartilhada de cache Redis da INNA."""

from .redis_client import (
    get_redis_client,
    is_redis_configured,
    ping_redis,
    reset_redis_client,
)

__all__ = [
    "get_redis_client",
    "is_redis_configured",
    "ping_redis",
    "reset_redis_client",
]

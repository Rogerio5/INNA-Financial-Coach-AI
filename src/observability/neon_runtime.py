"""Monitoramento seguro do PostgreSQL/Neon da INNA."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from src.agents.persistence import obter_pool_postgres


@dataclass(frozen=True, slots=True)
class NeonRuntimeStatus:
    configured: bool
    available: bool
    latency_ms: float | None
    server_version: str
    pool_status: str
    pool_size: int | None
    pool_available: int | None
    pool_waiting: int | None
    error_type: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_integer(
    value: Any,
) -> int | None:
    try:
        if value is None:
            return None

        return int(value)
    except (TypeError, ValueError):
        return None


def _read_pool_stats(
    pool: Any,
) -> dict[str, int | None]:
    """
    Lê apenas métricas numéricas do pool.

    Nenhuma URL, senha, host ou credencial é retornada.
    """

    try:
        stats = pool.get_stats()
    except Exception:
        stats = {}

    return {
        "pool_size": _safe_integer(stats.get("pool_size")),
        "pool_available": _safe_integer(stats.get("pool_available")),
        "pool_waiting": _safe_integer(stats.get("requests_waiting")),
    }


def collect_neon_runtime_status(
    *,
    timeout_seconds: float = 5.0,
) -> NeonRuntimeStatus:
    """
    Executa uma consulta mínima no pool compartilhado.

    A falha do Neon nunca interrompe o dashboard.
    """

    started_at = perf_counter()

    try:
        pool = obter_pool_postgres()
    except Exception as exc:
        return NeonRuntimeStatus(
            configured=False,
            available=False,
            latency_ms=None,
            server_version="",
            pool_status="unavailable",
            pool_size=None,
            pool_available=None,
            pool_waiting=None,
            error_type=type(exc).__name__,
        )

    stats = _read_pool_stats(pool)

    try:
        with pool.connection(timeout=timeout_seconds) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        1,
                        current_setting(
                            'server_version'
                        )
                    """
                )

                result = cursor.fetchone()

        latency_ms = round(
            (perf_counter() - started_at) * 1000,
            3,
        )

        server_version = ""
        connection_ok = False

        if isinstance(result, dict):
            result_values = list(result.values())

            if result_values:
                connection_ok = result_values[0] == 1

            if len(result_values) > 1:
                server_version = str(result_values[1])

        elif isinstance(result, (tuple, list)):
            if result:
                connection_ok = result[0] == 1

            if len(result) > 1:
                server_version = str(result[1])

        return NeonRuntimeStatus(
            configured=True,
            available=connection_ok,
            latency_ms=latency_ms,
            server_version=server_version,
            pool_status="healthy",
            pool_size=stats["pool_size"],
            pool_available=stats["pool_available"],
            pool_waiting=stats["pool_waiting"],
            error_type=None,
        )

    except Exception as exc:
        latency_ms = round(
            (perf_counter() - started_at) * 1000,
            3,
        )

        return NeonRuntimeStatus(
            configured=True,
            available=False,
            latency_ms=latency_ms,
            server_version="",
            pool_status="degraded",
            pool_size=stats["pool_size"],
            pool_available=stats["pool_available"],
            pool_waiting=stats["pool_waiting"],
            error_type=type(exc).__name__,
        )


__all__ = [
    "NeonRuntimeStatus",
    "collect_neon_runtime_status",
]

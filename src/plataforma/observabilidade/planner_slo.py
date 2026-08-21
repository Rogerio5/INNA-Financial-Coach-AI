"""Agregacao operacional de SLO do Adaptive Planner."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import text

from src.plataforma.observabilidade import planner_metrics as metrics_repo


@dataclass(frozen=True)
class PlannerSloSnapshot:
    """Snapshot privacy-safe das metricas do Planner."""

    available: bool
    window_hours: int

    total_plans: int
    clean_success_count: int
    terminal_success_count: int
    fallback_count: int
    error_count: int

    deterministic_count: int
    gemini_count: int
    redis_hit_count: int
    complex_count: int

    clean_success_rate_pct: float
    terminal_success_rate_pct: float
    fallback_rate_pct: float
    planner_error_rate_pct: float

    deterministic_route_rate_pct: float
    gemini_route_rate_pct: float
    complex_cache_hit_rate_pct: float

    avg_duration_ms: float
    p95_duration_ms: float

    def to_safe_dict(self) -> dict[str, Any]:
        """Retorna somente metadados operacionais."""

        return asdict(self)


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _safe_duration(value: Any) -> float:
    try:
        parsed = float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0

    if not math.isfinite(parsed):
        return 0.0

    return round(
        max(0.0, parsed),
        2,
    )


def _safe_rate(
    numerator: int,
    denominator: int,
) -> float:
    if denominator <= 0:
        return 0.0

    return round(
        (
            float(numerator)
            / float(denominator)
        )
        * 100.0,
        2,
    )


def _empty_snapshot(
    *,
    window_hours: int,
    available: bool,
) -> PlannerSloSnapshot:
    return PlannerSloSnapshot(
        available=available,
        window_hours=window_hours,
        total_plans=0,
        clean_success_count=0,
        terminal_success_count=0,
        fallback_count=0,
        error_count=0,
        deterministic_count=0,
        gemini_count=0,
        redis_hit_count=0,
        complex_count=0,
        clean_success_rate_pct=0.0,
        terminal_success_rate_pct=0.0,
        fallback_rate_pct=0.0,
        planner_error_rate_pct=0.0,
        deterministic_route_rate_pct=0.0,
        gemini_route_rate_pct=0.0,
        complex_cache_hit_rate_pct=0.0,
        avg_duration_ms=0.0,
        p95_duration_ms=0.0,
    )


def _snapshot_from_mapping(
    row: Mapping[str, Any],
    *,
    window_hours: int,
) -> PlannerSloSnapshot:
    total = _safe_int(
        row.get("total_plans")
    )

    clean_success = _safe_int(
        row.get("clean_success_count")
    )

    terminal_success = _safe_int(
        row.get("terminal_success_count")
    )

    fallback = _safe_int(
        row.get("fallback_count")
    )

    error = _safe_int(
        row.get("error_count")
    )

    deterministic = _safe_int(
        row.get("deterministic_count")
    )

    gemini = _safe_int(
        row.get("gemini_count")
    )

    redis_hit = _safe_int(
        row.get("redis_hit_count")
    )

    complex_count = _safe_int(
        row.get("complex_count")
    )

    return PlannerSloSnapshot(
        available=True,
        window_hours=window_hours,
        total_plans=total,
        clean_success_count=clean_success,
        terminal_success_count=terminal_success,
        fallback_count=fallback,
        error_count=error,
        deterministic_count=deterministic,
        gemini_count=gemini,
        redis_hit_count=redis_hit,
        complex_count=complex_count,
        clean_success_rate_pct=_safe_rate(
            clean_success,
            total,
        ),
        terminal_success_rate_pct=_safe_rate(
            terminal_success,
            total,
        ),
        fallback_rate_pct=_safe_rate(
            fallback,
            total,
        ),
        planner_error_rate_pct=_safe_rate(
            error,
            total,
        ),
        deterministic_route_rate_pct=_safe_rate(
            deterministic,
            total,
        ),
        gemini_route_rate_pct=_safe_rate(
            gemini,
            total,
        ),
        complex_cache_hit_rate_pct=_safe_rate(
            redis_hit,
            complex_count,
        ),
        avg_duration_ms=_safe_duration(
            row.get("avg_duration_ms")
        ),
        p95_duration_ms=_safe_duration(
            row.get("p95_duration_ms")
        ),
    )


def _build_slo_snapshot_sql():
    table = metrics_repo.PLANNER_METRICS_TABLE

    return text(
        f"""
        WITH cohort AS (
            SELECT
                planner_route,
                query_complexity,
                planner_outcome,
                duration_ms
            FROM {table}
            WHERE
                planner_mode = :planner_mode
                AND created_at >= (
                    CURRENT_TIMESTAMP
                    - (
                        :window_hours
                        * INTERVAL '1 hour'
                    )
                )
        )
        SELECT
            COUNT(*) AS total_plans,

            COUNT(*) FILTER (
                WHERE planner_outcome = 'success'
            ) AS clean_success_count,

            COUNT(*) FILTER (
                WHERE planner_outcome IN (
                    'success',
                    'fallback'
                )
            ) AS terminal_success_count,

            COUNT(*) FILTER (
                WHERE planner_outcome = 'fallback'
            ) AS fallback_count,

            COUNT(*) FILTER (
                WHERE planner_outcome = 'error'
            ) AS error_count,

            COUNT(*) FILTER (
                WHERE planner_route = 'deterministic'
            ) AS deterministic_count,

            COUNT(*) FILTER (
                WHERE planner_route = 'gemini'
            ) AS gemini_count,

            COUNT(*) FILTER (
                WHERE planner_route = 'redis_hit'
            ) AS redis_hit_count,

            COUNT(*) FILTER (
                WHERE query_complexity = 'complex'
            ) AS complex_count,

            AVG(duration_ms) AS avg_duration_ms,

            percentile_cont(0.95)
            WITHIN GROUP (
                ORDER BY duration_ms
            ) AS p95_duration_ms

        FROM cohort
        """
    )


def read_planner_slo_snapshot(
    *,
    window_hours: int = 24,
    planner_mode: str = "adaptive",
) -> PlannerSloSnapshot:
    """
    Le o snapshot operacional.

    Falhas de observabilidade nao interrompem
    o runtime principal.
    """

    effective_window = int(
        window_hours
    )

    if effective_window <= 0:
        raise ValueError(
            "window_hours_must_be_positive"
        )

    effective_mode = str(
        planner_mode or "adaptive"
    ).strip().lower()

    try:
        engine = (
            metrics_repo._database_engine()
        )

        with engine.connect() as connection:
            row = connection.execute(
                _build_slo_snapshot_sql(),
                {
                    "planner_mode": (
                        effective_mode
                    ),
                    "window_hours": (
                        effective_window
                    ),
                },
            ).mappings().one()

        return _snapshot_from_mapping(
            row,
            window_hours=effective_window,
        )

    except Exception:
        return _empty_snapshot(
            window_hours=effective_window,
            available=False,
        )


__all__ = [
    "PlannerSloSnapshot",
    "read_planner_slo_snapshot",
]

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.observability import planner_slo


def _row(**overrides):
    base = {
        "total_plans": 4,
        "clean_success_count": 3,
        "terminal_success_count": 4,
        "fallback_count": 1,
        "error_count": 0,
        "deterministic_count": 1,
        "gemini_count": 1,
        "redis_hit_count": 1,
        "complex_count": 3,
        "avg_duration_ms": 120.25,
        "p95_duration_ms": 300.75,
    }

    base.update(overrides)

    return base


def test_snapshot_calculates_exact_rates():
    snapshot = (
        planner_slo._snapshot_from_mapping(
            _row(),
            window_hours=24,
        )
    )

    assert snapshot.available is True
    assert snapshot.total_plans == 4
    assert snapshot.clean_success_rate_pct == 75.0
    assert (
        snapshot.terminal_success_rate_pct
        == 100.0
    )
    assert snapshot.fallback_rate_pct == 25.0
    assert snapshot.planner_error_rate_pct == 0.0
    assert (
        snapshot.deterministic_route_rate_pct
        == 25.0
    )
    assert snapshot.gemini_route_rate_pct == 25.0
    assert (
        snapshot.complex_cache_hit_rate_pct
        == 33.33
    )
    assert snapshot.avg_duration_ms == 120.25
    assert snapshot.p95_duration_ms == 300.75


def test_zero_denominators_are_safe():
    snapshot = (
        planner_slo._snapshot_from_mapping(
            _row(
                total_plans=0,
                clean_success_count=0,
                terminal_success_count=0,
                fallback_count=0,
                error_count=0,
                deterministic_count=0,
                gemini_count=0,
                redis_hit_count=0,
                complex_count=0,
            ),
            window_hours=24,
        )
    )

    assert snapshot.clean_success_rate_pct == 0.0
    assert (
        snapshot.terminal_success_rate_pct
        == 0.0
    )
    assert snapshot.fallback_rate_pct == 0.0
    assert snapshot.planner_error_rate_pct == 0.0
    assert (
        snapshot.complex_cache_hit_rate_pct
        == 0.0
    )


def test_nonfinite_durations_are_sanitized():
    snapshot = (
        planner_slo._snapshot_from_mapping(
            _row(
                avg_duration_ms=float("nan"),
                p95_duration_ms=float("inf"),
            ),
            window_hours=24,
        )
    )

    assert snapshot.avg_duration_ms == 0.0
    assert snapshot.p95_duration_ms == 0.0


def test_reader_is_fail_open(
    monkeypatch,
):
    monkeypatch.setattr(
        planner_slo.metrics_repo,
        "_database_engine",
        MagicMock(
            side_effect=RuntimeError(
                "simulated_database_failure"
            )
        ),
    )

    snapshot = (
        planner_slo.read_planner_slo_snapshot(
            window_hours=24,
        )
    )

    assert snapshot.available is False
    assert snapshot.total_plans == 0
    assert snapshot.planner_error_rate_pct == 0.0


def test_sql_contains_only_safe_metric_dimensions():
    rendered = str(
        planner_slo._build_slo_snapshot_sql()
    ).lower()

    required = {
        "planner_route",
        "query_complexity",
        "planner_outcome",
        "duration_ms",
        "planner_mode",
    }

    forbidden = {
        "question",
        "prompt",
        "response",
        "user_id",
        "cache_key",
        "subqueries",
        "error_message",
    }

    for field in required:
        assert field in rendered

    for field in forbidden:
        assert field not in rendered


def test_window_must_be_positive():
    with pytest.raises(
        ValueError,
        match="window_hours_must_be_positive",
    ):
        planner_slo.read_planner_slo_snapshot(
            window_hours=0,
        )

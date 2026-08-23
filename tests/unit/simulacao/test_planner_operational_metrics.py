from __future__ import annotations

from dataclasses import asdict

import pytest


def test_planner_metric_event_contains_only_safe_metadata():
    from src.observability.planner_metrics import (
        PlannerMetricEvent,
    )

    event = PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
        duration_ms=125.5,
    )

    payload = asdict(event)

    assert payload == {
        "planner_mode": "adaptive",
        "query_complexity": "complex",
        "planner_route": "gemini",
        "cache_hit": False,
        "plan_source": "gemini",
        "plan_valid": True,
        "fallback_used": False,
        "duration_ms": 125.5,
        "planner_outcome": "success",
    }

    forbidden = {
        "question",
        "pergunta",
        "prompt",
        "response",
        "resposta",
        "user_id",
        "usuario_id",
        "content",
    }

    assert forbidden.isdisjoint(payload)


@pytest.mark.parametrize(
    ("route", "source", "cache_hit", "fallback"),
    [
        (
            "deterministic",
            "deterministic",
            False,
            False,
        ),
        (
            "gemini",
            "gemini",
            False,
            False,
        ),
        (
            "redis_hit",
            "cache",
            True,
            False,
        ),
        (
            "fallback",
            "deterministic",
            False,
            True,
        ),
    ],
)
def test_supported_planner_routes_are_accepted(
    route,
    source,
    cache_hit,
    fallback,
):
    from src.observability.planner_metrics import (
        PlannerMetricEvent,
    )

    event = PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route=route,
        cache_hit=cache_hit,
        plan_source=source,
        plan_valid=True,
        fallback_used=fallback,
        duration_ms=10.0,
    )

    assert event.planner_route == route


def test_duration_never_becomes_negative():
    from src.observability.planner_metrics import (
        PlannerMetricEvent,
    )

    event = PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="simple",
        planner_route="deterministic",
        cache_hit=False,
        plan_source="deterministic",
        plan_valid=True,
        fallback_used=False,
        duration_ms=-100.0,
    )

    assert event.duration_ms == 0.0


def test_table_name_is_dedicated_to_planner_metrics():
    from src.observability.planner_metrics import (
        PLANNER_METRICS_TABLE,
    )

    assert (
        PLANNER_METRICS_TABLE
        == "planner_metric_events_inna"
    )


def test_repository_contract_is_fail_open(monkeypatch):
    from src.observability import planner_metrics

    event = planner_metrics.PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
        duration_ms=50.0,
    )

    def fail(*args, **kwargs):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(
        planner_metrics,
        "_persist_event",
        fail,
    )

    result = (
        planner_metrics.record_planner_metric_event(
            event
        )
    )

    assert result is False

from __future__ import annotations

from dataclasses import fields

import pytest

from src.observability.planner_metrics import (
    PlannerMetricEvent,
    _build_create_table_sql,
    _event_to_insert_payload,
)


def _event(
    outcome: str,
) -> PlannerMetricEvent:
    return PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
        duration_ms=10.0,
        planner_outcome=outcome,
    )


def test_event_contract_contains_planner_outcome():
    names = {
        item.name
        for item in fields(
            PlannerMetricEvent
        )
    }

    assert names == {
        "planner_mode",
        "query_complexity",
        "planner_route",
        "cache_hit",
        "plan_source",
        "plan_valid",
        "fallback_used",
        "duration_ms",
        "planner_outcome",
    }


def test_supported_planner_outcomes():
    for outcome in (
        "success",
        "fallback",
        "error",
    ):
        event = _event(
            outcome
        )

        assert (
            event.planner_outcome
            == outcome
        )


def test_unknown_planner_outcome_is_rejected():
    with pytest.raises(
        ValueError,
        match="unsupported_planner_outcome",
    ):
        _event(
            "unexpected"
        )


def test_schema_contains_planner_outcome():
    sql = (
        _build_create_table_sql()
        .lower()
    )

    assert "planner_outcome" in sql


def test_insert_payload_contains_planner_outcome():
    event = _event(
        "success"
    )

    payload = (
        _event_to_insert_payload(
            event
        )
    )

    assert (
        payload["planner_outcome"]
        == "success"
    )

    assert set(
        payload
    ) == {
        "planner_mode",
        "query_complexity",
        "planner_route",
        "cache_hit",
        "plan_source",
        "plan_valid",
        "fallback_used",
        "duration_ms",
        "planner_outcome",
    }

from __future__ import annotations

from dataclasses import asdict

import pytest

from src.observability.planner_metrics import (
    PlannerMetricEvent,
    _event_to_insert_payload,
)


def _terminal_error_event():
    return PlannerMetricEvent(
        planner_mode="adaptive",
        query_complexity="unknown",
        planner_route="error",
        cache_hit=False,
        plan_source="none",
        plan_valid=False,
        fallback_used=False,
        duration_ms=25.0,
        planner_outcome="error",
    )


def test_terminal_error_event_is_representable():
    event = _terminal_error_event()

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "unknown"
    assert event.planner_route == "error"
    assert event.cache_hit is False
    assert event.plan_source == "none"
    assert event.plan_valid is False
    assert event.fallback_used is False
    assert event.planner_outcome == "error"


def test_terminal_error_payload_is_privacy_safe():
    event = _terminal_error_event()

    payload = asdict(
        event
    )

    forbidden = {
        "question",
        "pergunta",
        "prompt",
        "response",
        "resposta",
        "user_id",
        "usuario_id",
        "content",
        "error_message",
        "exception",
    }

    assert forbidden.isdisjoint(
        payload
    )


def test_terminal_error_insert_payload_is_supported():
    event = _terminal_error_event()

    payload = _event_to_insert_payload(
        event
    )

    assert payload[
        "planner_route"
    ] == "error"

    assert payload[
        "plan_source"
    ] == "none"

    assert payload[
        "planner_outcome"
    ] == "error"

    assert payload[
        "plan_valid"
    ] is False


def test_invalid_error_source_is_rejected():
    with pytest.raises(
        ValueError,
    ):
        PlannerMetricEvent(
            planner_mode="adaptive",
            query_complexity="unknown",
            planner_route="error",
            cache_hit=False,
            plan_source="gemini",
            plan_valid=False,
            fallback_used=False,
            duration_ms=25.0,
            planner_outcome="error",
        )

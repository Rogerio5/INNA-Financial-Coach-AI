from __future__ import annotations

from dataclasses import asdict
from unittest.mock import MagicMock

import pytest

from src.agentic_rag import planner
from src.observability.planner_metrics import (
    PlannerMetricEvent,
)


def test_query_planner_records_terminal_adaptive_error(
    monkeypatch,
):
    failure = RuntimeError(
        "simulated_terminal_planner_failure"
    )

    create_plan = MagicMock(
        side_effect=failure
    )

    writer = MagicMock(
        return_value=True
    )

    clock = MagicMock(
        side_effect=[
            100.000,
            100.075,
        ]
    )

    monkeypatch.setattr(
        planner,
        "create_research_plan",
        create_plan,
    )

    monkeypatch.setattr(
        planner,
        "record_planner_metric_event",
        writer,
        raising=False,
    )

    monkeypatch.setattr(
        planner,
        "perf_counter",
        clock,
        raising=False,
    )

    query_planner = planner.QueryPlanner()

    with pytest.raises(
        RuntimeError,
        match="simulated_terminal_planner_failure",
    ):
        query_planner.plan(
            "Analise esta consulta complexa.",
            language="pt",
            intent="consulta_rag",
            planner_mode="adaptive",
        )

    writer.assert_called_once()

    call = writer.call_args

    if call.args:
        event = call.args[0]
    else:
        event = call.kwargs["event"]

    assert isinstance(
        event,
        PlannerMetricEvent,
    )

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "unknown"
    assert event.planner_route == "error"
    assert event.cache_hit is False
    assert event.plan_source == "none"
    assert event.plan_valid is False
    assert event.fallback_used is False
    assert event.planner_outcome == "error"
    assert event.duration_ms == pytest.approx(
        75.0
    )

    payload = asdict(
        event
    )

    forbidden = {
        "question",
        "query",
        "prompt",
        "response",
        "user_id",
        "content",
        "error_message",
        "exception",
    }

    assert forbidden.isdisjoint(
        payload
    )


def test_terminal_error_metrics_failure_does_not_replace_original_error(
    monkeypatch,
):
    original_failure = RuntimeError(
        "original_planner_failure"
    )

    monkeypatch.setattr(
        planner,
        "create_research_plan",
        MagicMock(
            side_effect=original_failure
        ),
    )

    writer = MagicMock(
        side_effect=RuntimeError(
            "metrics_failure"
        )
    )

    monkeypatch.setattr(
        planner,
        "record_planner_metric_event",
        writer,
        raising=False,
    )

    monkeypatch.setattr(
        planner,
        "perf_counter",
        MagicMock(
            side_effect=[
                100.000,
                100.025,
            ]
        ),
        raising=False,
    )

    query_planner = planner.QueryPlanner()

    with pytest.raises(
        RuntimeError,
        match="original_planner_failure",
    ):
        query_planner.plan(
            "Analise esta consulta complexa.",
            planner_mode="adaptive",
        )

    writer.assert_called_once()


def test_non_adaptive_terminal_error_does_not_emit_adaptive_metric(
    monkeypatch,
):
    writer = MagicMock(
        return_value=True
    )

    monkeypatch.setattr(
        planner,
        "create_research_plan",
        MagicMock(
            side_effect=RuntimeError(
                "deterministic_failure"
            )
        ),
    )

    monkeypatch.setattr(
        planner,
        "record_planner_metric_event",
        writer,
        raising=False,
    )

    monkeypatch.setattr(
        planner,
        "perf_counter",
        MagicMock(
            return_value=100.0
        ),
        raising=False,
    )

    query_planner = planner.QueryPlanner()

    with pytest.raises(
        RuntimeError,
        match="deterministic_failure",
    ):
        query_planner.plan(
            "Consulta direta.",
            planner_mode="deterministic",
        )

    writer.assert_not_called()

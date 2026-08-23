from __future__ import annotations

from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.agentic_rag import planner
from src.observability.planner_metrics import (
    PlannerMetricEvent,
)

SIMPLE_QUESTION = (
    "O que é CDI?"
)

COMPLEX_QUESTION = (
    "Compare Tesouro Selic e CDB com liquidez "
    "diária, analise riscos e vantagens e "
    "proponha uma estratégia em etapas."
)


def _assessment(complexity):
    return SimpleNamespace(
        complexity=complexity,
        score=0,
        threshold=2,
        signals=[],
        word_count=0,
        objective_count=0,
        connector_count=0,
    )


def _complex_llm_plan():
    base = planner._build_deterministic_plan(
        question=COMPLEX_QUESTION,
        language="pt",
        user_id=None,
    )

    return base.model_copy(
        update={
            "complexity": (
                planner.ResearchComplexity.COMPLEX
            ),
            "generation_mode": (
                planner.PlanGenerationMode.LLM
            ),
        }
    )


def _install_metric_writer(
    monkeypatch,
):
    writer = MagicMock(
        return_value=True
    )

    monkeypatch.setattr(
        planner,
        "record_planner_metric_event",
        writer,
        raising=False,
    )

    return writer


def _install_clock(
    monkeypatch,
):
    clock = MagicMock(
        side_effect=[
            100.000,
            100.125,
        ]
    )

    monkeypatch.setattr(
        planner,
        "perf_counter",
        clock,
        raising=False,
    )

    return clock


def _event_from_writer(
    writer,
):
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

    assert event.duration_ms >= 0

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
    }

    assert forbidden.isdisjoint(
        payload
    )

    return event


def test_adaptive_simple_records_deterministic_metric(
    monkeypatch,
):
    writer = _install_metric_writer(
        monkeypatch
    )

    _install_clock(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "assess_query_complexity",
        MagicMock(
            return_value=_assessment(planner.ResearchComplexity.SIMPLE)
        ),
    )

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        MagicMock(),
    )

    result = planner.create_research_plan(
        SIMPLE_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == planner.PlanGenerationMode.DETERMINISTIC
    )

    event = _event_from_writer(
        writer
    )

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "simple"
    assert event.planner_route == "deterministic"
    assert event.cache_hit is False
    assert event.plan_source == "deterministic"
    assert event.plan_valid is True
    assert event.fallback_used is False

    assert event.duration_ms == pytest.approx(
        125.0
    )


def test_adaptive_complex_records_gemini_metric(
    monkeypatch,
):
    writer = _install_metric_writer(
        monkeypatch
    )

    _install_clock(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "assess_query_complexity",
        MagicMock(
            return_value=_assessment(planner.ResearchComplexity.COMPLEX)
        ),
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(
            return_value=False
        ),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        MagicMock(
            return_value=_complex_llm_plan()
        ),
    )

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        MagicMock(),
    )

    result = planner.create_research_plan(
        COMPLEX_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == planner.PlanGenerationMode.LLM
    )

    event = _event_from_writer(
        writer
    )

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "complex"
    assert event.planner_route == "gemini"
    assert event.cache_hit is False
    assert event.plan_source == "gemini"
    assert event.plan_valid is True
    assert event.fallback_used is False

    assert event.duration_ms == pytest.approx(
        125.0
    )


def test_adaptive_complex_records_redis_hit_metric(
    monkeypatch,
):
    writer = _install_metric_writer(
        monkeypatch
    )

    _install_clock(
        monkeypatch
    )

    cached = _complex_llm_plan()

    monkeypatch.setattr(
        planner,
        "assess_query_complexity",
        MagicMock(
            return_value=_assessment(planner.ResearchComplexity.COMPLEX)
        ),
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(
            return_value=True
        ),
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        MagicMock(
            return_value=cached
        ),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        MagicMock(),
    )

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        MagicMock(),
    )

    result = planner.create_research_plan(
        COMPLEX_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == planner.PlanGenerationMode.LLM
    )

    event = _event_from_writer(
        writer
    )

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "complex"
    assert event.planner_route == "redis_hit"
    assert event.cache_hit is True
    assert event.plan_source == "cache"
    assert event.plan_valid is True
    assert event.fallback_used is False

    assert event.duration_ms == pytest.approx(
        125.0
    )


def test_adaptive_llm_failure_records_fallback_metric(
    monkeypatch,
):
    writer = _install_metric_writer(
        monkeypatch
    )

    _install_clock(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "assess_query_complexity",
        MagicMock(
            return_value=_assessment(planner.ResearchComplexity.COMPLEX)
        ),
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(
            return_value=False
        ),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        MagicMock(
            side_effect=RuntimeError(
                "simulated_llm_failure"
            )
        ),
    )

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        MagicMock(),
    )

    result = planner.create_research_plan(
        COMPLEX_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == planner.PlanGenerationMode.FALLBACK
    )

    event = _event_from_writer(
        writer
    )

    assert event.planner_mode == "adaptive"
    assert event.query_complexity == "complex"
    assert event.planner_route == "fallback"
    assert event.cache_hit is False
    assert event.plan_source == "deterministic"
    assert event.plan_valid is True
    assert event.fallback_used is True

    assert event.duration_ms == pytest.approx(
        125.0
    )


def test_metric_failure_does_not_break_adaptive_planner(
    monkeypatch,
):
    writer = MagicMock(
        side_effect=RuntimeError(
            "metrics_backend_failure"
        )
    )

    monkeypatch.setattr(
        planner,
        "record_planner_metric_event",
        writer,
        raising=False,
    )

    _install_clock(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "assess_query_complexity",
        MagicMock(
            return_value=_assessment(planner.ResearchComplexity.SIMPLE)
        ),
    )

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        MagicMock(),
    )

    result = planner.create_research_plan(
        SIMPLE_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == planner.PlanGenerationMode.DETERMINISTIC
    )

    writer.assert_called_once()

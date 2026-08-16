from unittest.mock import MagicMock

import src.agentic_rag.planner as planner
from src.agentic_rag.contracts import (
    ALLOWED_TOOL_BY_SOURCE,
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)

SIMPLE_QUESTION = (
    "O que é reserva de emergência?"
)

COMPLEX_QUESTION = (
    "Compare Tesouro Selic e CDB com "
    "liquidez diária, analise riscos e "
    "vantagens e proponha uma estratégia "
    "em etapas."
)


def _llm_plan() -> ResearchPlan:
    return ResearchPlan(
        original_question=COMPLEX_QUESTION,
        language="pt",
        complexity=ResearchComplexity.COMPLEX,
        rationale="Plano comparativo.",
        subqueries=[
            ResearchSubquery(
                step_id="step_01_knowledge_llm",
                question=(
                    "Compare Tesouro Selic e "
                    "CDB quanto a liquidez, "
                    "riscos e vantagens."
                ),
                source=(
                    ResearchSource.KNOWLEDGE_BASE
                ),
                tool_name=ALLOWED_TOOL_BY_SOURCE[
                    ResearchSource.KNOWLEDGE_BASE
                ],
                priority=100,
                required=True,
                top_k=4,
                max_results=5,
            ),
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=True,
        max_rounds=2,
        metadata={
            "planner": "gemini_structured_v1",
        },
    )


def _install_route_trace(
    monkeypatch,
) -> MagicMock:
    route_trace = MagicMock()

    monkeypatch.setattr(
        planner,
        "_set_planner_route_trace",
        route_trace,
        raising=False,
    )

    return route_trace


def test_adaptive_simple_emits_deterministic_route(
    monkeypatch,
):
    route_trace = _install_route_trace(
        monkeypatch
    )

    result = planner.create_research_plan(
        SIMPLE_QUESTION,
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.DETERMINISTIC
    )

    route_trace.assert_called_once_with(
        planner_mode="adaptive",
        query_complexity="simple",
        planner_route="deterministic",
        cache_hit=False,
        plan_source="deterministic",
        plan_valid=True,
        fallback_used=False,
    )


def test_adaptive_redis_hit_emits_cache_route(
    monkeypatch,
):
    route_trace = _install_route_trace(
        monkeypatch
    )

    cached = _llm_plan()

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        MagicMock(return_value=cached),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
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
        == PlanGenerationMode.LLM
    )

    route_trace.assert_called_once_with(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="redis_hit",
        cache_hit=True,
        plan_source="cache",
        plan_valid=True,
        fallback_used=False,
    )


def test_adaptive_cache_miss_emits_gemini_route(
    monkeypatch,
):
    route_trace = _install_route_trace(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        MagicMock(return_value=None),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        MagicMock(return_value=_llm_plan()),
    )

    monkeypatch.setattr(
        planner,
        "write_planner_cache",
        MagicMock(return_value=True),
    )

    result = planner.create_research_plan(
        COMPLEX_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.LLM
    )

    route_trace.assert_called_once_with(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
    )


def test_adaptive_llm_failure_emits_fallback_route(
    monkeypatch,
):
    route_trace = _install_route_trace(
        monkeypatch
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(return_value=False),
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

    result = planner.create_research_plan(
        COMPLEX_QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="adaptive",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.FALLBACK
    )

    route_trace.assert_called_once_with(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="fallback",
        cache_hit=False,
        plan_source="deterministic",
        plan_valid=True,
        fallback_used=True,
    )


def test_route_trace_exports_only_safe_metadata(
    monkeypatch,
):
    captured = {}

    class TraceContext:
        def __enter__(self):
            return None

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        captured["name"] = name
        captured["attributes"] = attributes
        captured["instrumentation_name"] = (
            instrumentation_name
        )
        return TraceContext()

    monkeypatch.setattr(
        planner,
        "traced_operation",
        fake_traced_operation,
    )

    planner._set_planner_route_trace(
        planner_mode="adaptive",
        query_complexity="complex",
        planner_route="gemini",
        cache_hit=False,
        plan_source="gemini",
        plan_valid=True,
        fallback_used=False,
    )

    assert captured["name"] == (
        "inna.agentic_rag.planner.route"
    )

    assert captured["instrumentation_name"] == (
        "inna.agentic_rag.planner"
    )

    assert captured["attributes"] == {
        "planner.mode": "adaptive",
        "planner.query_complexity": "complex",
        "planner.route": "gemini",
        "planner.cache_hit": False,
        "planner.plan_source": "gemini",
        "planner.plan_valid": True,
        "planner.fallback_used": False,
        "privacy.content_exported": False,
    }

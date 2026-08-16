from unittest.mock import MagicMock

import src.agentic_rag.planner as planner
import src.agentic_rag.planner_cache as planner_cache
from src.agentic_rag.contracts import (
    ALLOWED_TOOL_BY_SOURCE,
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)


def _llm_plan(
    question: str = "Explique reserva de emergência.",
) -> ResearchPlan:
    return ResearchPlan(
        original_question=question,
        language="pt",
        complexity=ResearchComplexity.SIMPLE,
        rationale="Plano estruturado.",
        subqueries=[
            ResearchSubquery(
                step_id="step_01_knowledge_llm",
                question=question,
                source=ResearchSource.KNOWLEDGE_BASE,
                tool_name=ALLOWED_TOOL_BY_SOURCE[
                    ResearchSource.KNOWLEDGE_BASE
                ],
                priority=100,
                required=True,
                top_k=4,
                max_results=5,
            )
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=False,
        max_rounds=1,
        metadata={
            "planner": "gemini_structured_v1",
        },
    )


def test_deterministic_does_not_use_planner_cache(
    monkeypatch,
):
    cache_read = MagicMock()

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        cache_read,
    )

    result = planner.create_research_plan(
        "O que é reserva de emergência?",
        planner_mode="deterministic",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.DETERMINISTIC
    )
    cache_read.assert_not_called()


def test_llm_cache_disabled_calls_llm(
    monkeypatch,
):
    llm_plan = _llm_plan()

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        lambda: False,
    )

    build_llm = MagicMock(
        return_value=llm_plan
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    result = planner.create_research_plan(
        llm_plan.original_question,
        planner_mode="llm",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.LLM
    )
    build_llm.assert_called_once()


def test_llm_cache_miss_calls_llm_and_writes(
    monkeypatch,
):
    llm_plan = _llm_plan()

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        lambda: True,
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        lambda **kwargs: None,
    )

    build_llm = MagicMock(
        return_value=llm_plan
    )

    write_cache = MagicMock(
        return_value=True
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    monkeypatch.setattr(
        planner,
        "write_planner_cache",
        write_cache,
    )

    result = planner.create_research_plan(
        llm_plan.original_question,
        planner_mode="llm",
    )

    assert (
        result.metadata[
            "planner_cache_status"
        ]
        == "miss"
    )
    assert (
        result.metadata[
            "planner_cache_stored"
        ]
        is True
    )

    build_llm.assert_called_once()
    write_cache.assert_called_once()


def test_llm_cache_hit_skips_llm(
    monkeypatch,
):
    cached = _llm_plan()

    cached_data = cached.model_dump(
        mode="python"
    )

    cached_data["metadata"] = {
        **cached.metadata,
        "planner_cache_status": "hit",
        "planner_cache_backend": "redis",
    }

    cached = ResearchPlan.model_validate(
        cached_data
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        lambda: True,
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        lambda **kwargs: cached,
    )

    build_llm = MagicMock()

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    result = planner.create_research_plan(
        cached.original_question,
        planner_mode="llm",
    )

    assert (
        result.metadata[
            "planner_cache_status"
        ]
        == "hit"
    )

    build_llm.assert_not_called()


def test_planner_cache_redis_failure_is_fail_open(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_PLANNER_CACHE_ENABLED",
        "true",
    )

    fake_client = MagicMock()
    fake_client.get.side_effect = RuntimeError(
        "redis unavailable"
    )

    monkeypatch.setattr(
        planner_cache,
        "get_redis_client",
        lambda: fake_client,
    )

    result = planner_cache.read_planner_cache(
        question="Teste Redis",
        language="pt",
        user_id=None,
    )

    assert result is None

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

QUESTION = (
    "Compare Tesouro Selic e CDB com "
    "liquidez diaria e proponha uma "
    "estrategia."
)


def _step(
    step_id: str,
    question: str,
) -> ResearchSubquery:
    return ResearchSubquery(
        step_id=step_id,
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


def _invalid_cached_plan() -> ResearchPlan:
    return ResearchPlan(
        original_question=QUESTION,
        language="pt",
        complexity=ResearchComplexity.SIMPLE,
        rationale=(
            "Plano cacheado propositalmente "
            "invalido."
        ),
        subqueries=[
            _step(
                "step_01_kb",
                "Compare Tesouro Selic.",
            ),
            _step(
                "step_02_kb",
                "Compare CDB.",
            ),
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=True,
        max_rounds=2,
        metadata={
            "planner": "gemini_structured_v1",
            "planner_cache_status": "hit",
            "planner_cache_backend": "redis",
        },
    )


def _valid_llm_plan() -> ResearchPlan:
    return ResearchPlan(
        original_question=QUESTION,
        language="pt",
        complexity=ResearchComplexity.COMPLEX,
        rationale=(
            "Plano regenerado apos rejeicao "
            "do cache."
        ),
        subqueries=[
            _step(
                "step_01_knowledge_llm",
                (
                    "Compare Tesouro Selic e "
                    "CDB com liquidez diaria."
                ),
            ),
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=True,
        max_rounds=2,
        metadata={
            "planner": "gemini_structured_v1",
        },
    )


def test_invalid_cached_plan_is_rebuilt(
    monkeypatch,
):
    cached = _invalid_cached_plan()
    regenerated = _valid_llm_plan()

    cache_read = MagicMock(
        return_value=cached
    )

    build_llm = MagicMock(
        return_value=regenerated
    )

    cache_write = MagicMock(
        return_value=True
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        cache_read,
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    monkeypatch.setattr(
        planner,
        "write_planner_cache",
        cache_write,
    )

    result = planner.create_research_plan(
        QUESTION,
        language="pt",
        planner_mode="llm",
    )

    cache_read.assert_called_once()

    build_llm.assert_called_once()

    cache_write.assert_called_once()

    assert (
        result.metadata[
            "planner_cache_status"
        ]
        == "miss"
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.LLM
    )

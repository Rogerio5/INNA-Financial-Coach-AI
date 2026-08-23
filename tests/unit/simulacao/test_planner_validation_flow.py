from unittest.mock import Mock

import src.agentic_rag.planner as planner
from src.agentic_rag.contracts import (
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)


def _step(
    step_id: str,
    question: str,
) -> ResearchSubquery:
    return ResearchSubquery(
        step_id=step_id,
        question=question,
        source=ResearchSource.KNOWLEDGE_BASE,
        tool_name="buscar_conhecimento_rag",
        priority=100,
        required=True,
        top_k=4,
        max_results=5,
    )


def _invalid_llm_plan(
    question: str,
) -> ResearchPlan:
    return ResearchPlan(
        original_question=question,
        language="pt",
        complexity=ResearchComplexity.SIMPLE,
        rationale="Plano propositalmente inválido.",
        subqueries=[
            _step(
                "step_01_kb",
                "Analise Tesouro Selic.",
            ),
            _step(
                "step_02_kb",
                "Analise CDB.",
            ),
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=False,
        max_rounds=2,
        metadata={
            "planner": "gemini_structured_v1",
        },
    )


def test_invalid_llm_plan_is_not_cached_and_falls_back(
    monkeypatch,
):
    question = (
        "Compare Tesouro Selic e CDB."
    )

    invalid_plan = _invalid_llm_plan(
        question
    )

    cache_write = Mock(
        return_value=True
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        Mock(return_value=invalid_plan),
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        Mock(return_value=None),
    )

    monkeypatch.setattr(
        planner,
        "write_planner_cache",
        cache_write,
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        Mock(return_value=True),
    )

    result = planner.create_research_plan(
        question,
        language="pt",
        planner_mode="llm",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.FALLBACK
    )

    assert (
        result.metadata["planner"]
        == "deterministic_after_llm_failure"
    )

    assert (
        result.metadata[
            "llm_error_type"
        ]
        == "ValueError"
    )

    cache_write.assert_not_called()

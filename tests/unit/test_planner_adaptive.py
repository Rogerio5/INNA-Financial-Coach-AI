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


def _llm_plan(
    question: str = COMPLEX_QUESTION,
) -> ResearchPlan:
    return ResearchPlan(
        original_question=question,
        language="pt",
        complexity=ResearchComplexity.COMPLEX,
        rationale=(
            "Consulta comparativa com múltiplos "
            "objetivos."
        ),
        subqueries=[
            ResearchSubquery(
                step_id="step_01_knowledge_llm",
                question=(
                    "Compare Tesouro Selic e CDB "
                    "quanto a liquidez, riscos e "
                    "vantagens."
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


def test_complex_question_classifier_is_complex():
    assessment = planner.assess_query_complexity(
        COMPLEX_QUESTION
    )

    assert (
        assessment.complexity
        == ResearchComplexity.COMPLEX
    )


def test_adaptive_simple_uses_deterministic(
    monkeypatch,
):
    build_llm = MagicMock()
    cache_read = MagicMock()

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    monkeypatch.setattr(
        planner,
        "read_planner_cache",
        cache_read,
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

    assert (
        result.complexity
        == ResearchComplexity.SIMPLE
    )

    build_llm.assert_not_called()
    cache_read.assert_not_called()


def test_adaptive_complex_uses_llm(
    monkeypatch,
):
    llm_plan = _llm_plan()

    build_llm = MagicMock(
        return_value=llm_plan
    )

    monkeypatch.setattr(
        planner,
        "is_planner_cache_enabled",
        MagicMock(return_value=False),
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
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

    assert (
        result.complexity
        == ResearchComplexity.COMPLEX
    )

    build_llm.assert_called_once()


def test_adaptive_complex_uses_redis_hit(
    monkeypatch,
):
    cached = _llm_plan()

    cache_read = MagicMock(
        return_value=cached
    )

    build_llm = MagicMock()

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

    cache_read.assert_called_once()
    build_llm.assert_not_called()


def test_adaptive_complex_llm_failure_falls_back(
    monkeypatch,
):
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

    assert (
        result.metadata["planner"]
        == "deterministic_after_llm_failure"
    )

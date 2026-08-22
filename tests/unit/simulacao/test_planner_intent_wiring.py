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
    "Compare Tesouro Selic e CDB "
    "com liquidez diaria."
)


def _llm_plan() -> ResearchPlan:
    return ResearchPlan(
        original_question=QUESTION,
        language="pt",
        complexity=ResearchComplexity.COMPLEX,
        rationale="Plano para comparacao.",
        subqueries=[
            ResearchSubquery(
                step_id="step_01_knowledge_llm",
                question=QUESTION,
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


def test_intent_reaches_cache_read_and_write(
    monkeypatch,
):
    cache_read = MagicMock(
        return_value=None
    )

    cache_write = MagicMock(
        return_value=True
    )

    build_llm = MagicMock(
        return_value=_llm_plan()
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
        "write_planner_cache",
        cache_write,
    )

    monkeypatch.setattr(
        planner,
        "_build_llm_plan",
        build_llm,
    )

    result = planner.create_research_plan(
        QUESTION,
        language="pt",
        intent="consulta_rag",
        planner_mode="llm",
    )

    assert (
        result.generation_mode
        == PlanGenerationMode.LLM
    )

    assert (
        cache_read.call_args.kwargs[
            "intent"
        ]
        == "consulta_rag"
    )

    assert (
        cache_write.call_args.kwargs[
            "intent"
        ]
        == "consulta_rag"
    )


def test_query_planner_forwards_intent(
    monkeypatch,
):
    expected = _llm_plan()

    create = MagicMock(
        return_value=expected
    )

    monkeypatch.setattr(
        planner,
        "create_research_plan",
        create,
    )

    result = planner.QueryPlanner().plan(
        QUESTION,
        intent="relatorio",
        planner_mode="llm",
    )

    assert result is expected

    assert (
        create.call_args.kwargs[
            "intent"
        ]
        == "relatorio"
    )

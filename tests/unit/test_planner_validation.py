from src.agentic_rag.contracts import (
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)
from src.agentic_rag.planner import (
    validate_llm_research_plan,
)


def build_step(
    *,
    step_id: str,
    question: str,
    source: ResearchSource = ResearchSource.KNOWLEDGE_BASE,
) -> ResearchSubquery:
    tool = (
        "buscar_conhecimento_rag"
        if source == ResearchSource.KNOWLEDGE_BASE
        else "consultar_historico_financeiro"
    )

    return ResearchSubquery(
        step_id=step_id,
        question=question,
        source=source,
        tool_name=tool,
        priority=100,
        required=True,
        top_k=4,
        max_results=5,
    )


def build_plan(
    *,
    question: str = "Compare Tesouro Selic e CDB.",
    language: str = "pt",
    complexity: ResearchComplexity = ResearchComplexity.COMPLEX,
    steps: list[ResearchSubquery] | None = None,
) -> ResearchPlan:
    return ResearchPlan(
        original_question=question,
        language=language,
        complexity=complexity,
        rationale="Plano estruturado para a consulta.",
        subqueries=steps
        or [
            build_step(
                step_id="step_01_kb",
                question="Analise Tesouro Selic.",
            ),
            build_step(
                step_id="step_02_kb",
                question="Analise CDB.",
            ),
        ],
        generation_mode=PlanGenerationMode.LLM,
        requires_iteration=True,
        max_rounds=2,
        metadata={
            "planner": "gemini_structured_v1",
        },
    )


def test_valid_llm_plan_is_accepted():
    plan = build_plan()

    result = validate_llm_research_plan(
        plan,
        question="Compare Tesouro Selic e CDB.",
        language="pt",
        user_id=None,
    )

    assert result.valid is True
    assert result.reason == "valid"


def test_question_mismatch_is_rejected():
    plan = build_plan()

    result = validate_llm_research_plan(
        plan,
        question="Outra pergunta.",
        language="pt",
        user_id=None,
    )

    assert result.valid is False
    assert result.reason == "question_mismatch"


def test_language_mismatch_is_rejected():
    plan = build_plan()

    result = validate_llm_research_plan(
        plan,
        question="Compare Tesouro Selic e CDB.",
        language="en",
        user_id=None,
    )

    assert result.valid is False
    assert result.reason == "language_mismatch"


def test_duplicate_subqueries_are_rejected():
    plan = build_plan(
        steps=[
            build_step(
                step_id="step_01_kb",
                question="Analise Tesouro Selic.",
            ),
            build_step(
                step_id="step_02_kb",
                question="  analise   tesouro selic.  ",
            ),
        ],
    )

    result = validate_llm_research_plan(
        plan,
        question="Compare Tesouro Selic e CDB.",
        language="pt",
        user_id=None,
    )

    assert result.valid is False
    assert result.reason == "duplicate_subquery"


def test_history_without_trusted_user_is_rejected():
    plan = build_plan(
        steps=[
            build_step(
                step_id="step_01_history",
                question="Analise meu historico.",
                source=ResearchSource.FINANCIAL_HISTORY,
            ),
        ],
    )

    result = validate_llm_research_plan(
        plan,
        question="Compare Tesouro Selic e CDB.",
        language="pt",
        user_id=None,
    )

    assert result.valid is False
    assert result.reason == "untrusted_history_step"


def test_simple_plan_with_multiple_steps_is_rejected():
    plan = build_plan(
        complexity=ResearchComplexity.SIMPLE,
    )

    result = validate_llm_research_plan(
        plan,
        question="Compare Tesouro Selic e CDB.",
        language="pt",
        user_id=None,
    )

    assert result.valid is False
    assert result.reason == "simple_plan_has_multiple_steps"

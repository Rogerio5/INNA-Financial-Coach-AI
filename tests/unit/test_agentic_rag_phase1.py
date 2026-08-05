"""
Testes da Fase 1 da Semana 4:
contratos e Query Planner.
"""

from __future__ import annotations

import pytest

from pydantic import ValidationError

import src.agentic_rag.planner as planner_module

from src.agentic_rag import (
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
    create_research_plan,
)


def test_simple_question_creates_one_knowledge_step():
    plan = create_research_plan("O que é uma reserva de emergência?")

    assert plan.complexity == ResearchComplexity.SIMPLE
    assert len(plan.subqueries) == 1
    assert plan.subqueries[0].source == ResearchSource.KNOWLEDGE_BASE
    assert plan.subqueries[0].tool_name == "buscar_conhecimento_rag"
    assert plan.requires_iteration is False
    assert plan.max_rounds == 1


def test_complex_question_creates_multiple_steps():
    plan = create_research_plan(
        (
            "Compare reserva de emergência e pagamento "
            "de dívidas, explique os riscos e apresente "
            "um plano completo de ações seguras."
        )
    )

    assert plan.complexity == ResearchComplexity.COMPLEX
    assert len(plan.subqueries) == 2
    assert plan.requires_iteration is True
    assert plan.max_rounds >= 1
    assert all(step.source == ResearchSource.KNOWLEDGE_BASE for step in plan.subqueries)


def test_personal_history_requires_trusted_user():
    plan = create_research_plan(
        (
            "Compare minha evolução financeira com "
            "meus diagnósticos anteriores e explique "
            "os riscos atuais."
        ),
        user_id="user-test-123",
    )

    sources = {step.source for step in plan.subqueries}

    assert ResearchSource.FINANCIAL_HISTORY in sources
    assert "history_omitted_reason" not in plan.metadata


def test_history_is_omitted_without_trusted_user():
    plan = create_research_plan(
        (
            "Compare minha evolução financeira com "
            "meus diagnósticos anteriores e explique "
            "os riscos atuais."
        ),
        user_id=None,
    )

    assert all(
        step.source != ResearchSource.FINANCIAL_HISTORY for step in plan.subqueries
    )
    assert plan.metadata["history_omitted_reason"] == "missing_trusted_user_context"


def test_tool_must_match_authorized_source():
    with pytest.raises(
        ValidationError,
        match="fonte autorizada",
    ):
        ResearchSubquery(
            step_id="step_01_invalid",
            question="Consultar conhecimento financeiro",
            source=(ResearchSource.KNOWLEDGE_BASE),
            tool_name=("consultar_historico_financeiro"),
        )


def test_duplicate_step_ids_are_rejected():
    step = ResearchSubquery(
        step_id="step_01_knowledge",
        question="Pesquisar reserva financeira",
        source=(ResearchSource.KNOWLEDGE_BASE),
        tool_name="buscar_conhecimento_rag",
    )

    with pytest.raises(
        ValidationError,
        match="devem ser únicos",
    ):
        ResearchPlan(
            original_question=("Pesquisar reserva financeira"),
            language="pt",
            complexity=(ResearchComplexity.COMPLEX),
            rationale=("Plano de teste com duplicidade."),
            subqueries=[step, step],
            generation_mode=(PlanGenerationMode.DETERMINISTIC),
        )


def test_llm_failure_uses_deterministic_fallback(
    monkeypatch: pytest.MonkeyPatch,
):
    def fail_llm_plan(**_kwargs):
        raise RuntimeError("simulated_llm_failure")

    monkeypatch.setattr(
        planner_module,
        "_build_llm_plan",
        fail_llm_plan,
    )

    plan = create_research_plan(
        ("Compare os riscos das dívidas e crie um plano completo de organização."),
        planner_mode="llm",
    )

    assert plan.generation_mode == PlanGenerationMode.FALLBACK
    assert plan.metadata["planner"] == "deterministic_after_llm_failure"
    assert plan.metadata["llm_error_type"] == "RuntimeError"


def test_deterministic_mode_does_not_call_llm(
    monkeypatch: pytest.MonkeyPatch,
):
    def unexpected_llm_call(**_kwargs):
        pytest.fail("O modo determinístico chamou o LLM.")

    monkeypatch.setattr(
        planner_module,
        "_build_llm_plan",
        unexpected_llm_call,
    )

    plan = create_research_plan(
        "Como organizar meu orçamento?",
        planner_mode="deterministic",
    )

    assert plan.generation_mode == PlanGenerationMode.DETERMINISTIC


def test_invalid_question_is_rejected():
    with pytest.raises(
        ValueError,
        match="três caracteres",
    ):
        create_research_plan("a")

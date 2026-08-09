"""
Testes de alinhamento entre Query Planner e Router Agent.

Esses testes garantem que consultas com múltiplos
objetivos gerem múltiplas rotas e que perguntas simples
continuem utilizando o fluxo econômico.
"""

from __future__ import annotations

from src.agentic_rag import (
    ResearchComplexity,
    ResearchSource,
    assess_query_complexity,
    create_research_plan,
    route_research_plan,
)


def test_comparative_query_generates_multiple_routes():
    question = (
        "Compare reserva de emergência e dívidas, "
        "explique os riscos e crie um plano completo."
    )

    assessment = assess_query_complexity(question)
    plan = create_research_plan(question)
    routes = route_research_plan(plan)

    assert assessment.complexity == ResearchComplexity.COMPLEX
    assert assessment.score >= 2
    assert plan.complexity == ResearchComplexity.COMPLEX
    assert len(plan.subqueries) >= 2
    assert len(routes) == len(plan.subqueries)
    assert len(routes) >= 2
    assert all(route.source == ResearchSource.KNOWLEDGE_BASE for route in routes)


def test_simple_query_remains_single_route():
    question = "O que é uma reserva de emergência?"

    assessment = assess_query_complexity(question)
    plan = create_research_plan(question)
    routes = route_research_plan(plan)

    assert assessment.complexity == ResearchComplexity.SIMPLE
    assert plan.complexity == ResearchComplexity.SIMPLE
    assert len(plan.subqueries) == 1
    assert len(routes) == 1
    assert plan.requires_iteration is False


def test_single_risk_question_is_not_overclassified():
    question = "Quais são os riscos do cartão de crédito?"

    assessment = assess_query_complexity(question)
    plan = create_research_plan(question)

    assert assessment.score < 2
    assert assessment.complexity == ResearchComplexity.SIMPLE
    assert plan.complexity == ResearchComplexity.SIMPLE


def test_complexity_metadata_is_observable():
    question = (
        "Compare meu orçamento e minhas dívidas, "
        "explique os riscos e crie um plano completo."
    )

    plan = create_research_plan(question)

    assert plan.metadata["planner"] == "deterministic_v2"
    assert plan.metadata["complexity_score"] >= plan.metadata["complexity_threshold"]
    assert isinstance(
        plan.metadata["complexity_signals"],
        list,
    )
    assert plan.metadata["complexity_objective_count"] >= 2


def test_history_query_remains_complex_and_governed():
    question = (
        "Compare minha evolução financeira com "
        "meus diagnósticos anteriores e explique "
        "os riscos atuais."
    )

    plan = create_research_plan(
        question,
        user_id="trusted-user-test",
    )
    routes = route_research_plan(plan)

    assert plan.complexity == ResearchComplexity.COMPLEX
    assert any(route.source == ResearchSource.FINANCIAL_HISTORY for route in routes)

    history_route = next(
        route for route in routes if (route.source == ResearchSource.FINANCIAL_HISTORY)
    )

    assert history_route.requires_trusted_user is True
    assert history_route.arguments == {
        "limite": 8,
    }
    assert "user_id" not in history_route.arguments

from __future__ import annotations

from unittest.mock import patch

from src.agents.graph import (
    ALLOWED_AGENT_ROUTES,
    _selecionar_rota,
)
from src.agents.schemas import (
    SupervisorDecision,
)
from src.agents.supervisor import (
    supervisor_node,
)


def test_allowed_routes_are_explicit():
    assert ALLOWED_AGENT_ROUTES == {
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    }


def test_route_selector_accepts_allowed_route():
    state = {
        "next_node": "rag_agent",
    }

    assert _selecionar_rota(state) == "rag_agent"


def test_route_selector_uses_fallback_when_missing():
    assert _selecionar_rota({}) == "fallback_agent"


def test_route_selector_rejects_unknown_route():
    state = {
        "next_node": "unknown_agent",
    }

    assert _selecionar_rota(state) == "fallback_agent"


@patch("src.agents.supervisor.classificar_intencao_hibrida")
def test_supervisor_records_routing_metadata(
    classify_mock,
):
    classify_mock.return_value = SupervisorDecision(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=0.91,
        use_rag=True,
        reason=("A mensagem solicita explicação de um conceito financeiro."),
        classification_source="rule",
    )

    result = supervisor_node(
        {
            "user_message": ("Explique juros compostos"),
            "context": {},
            "errors": [],
            "trace": [],
            "route_history": [],
        }
    )

    assert result["route_source"] == "rule"

    assert result["routing_reason"] == (
        "A mensagem solicita explicação de um conceito financeiro."
    )

    assert result["route_history"] == [
        {
            "intent": "consulta_rag",
            "next_node": "rag_agent",
            "source": "rule",
            "reason": ("A mensagem solicita explicação de um conceito financeiro."),
            "confidence": 0.91,
            "fallback_used": False,
            "gemini_called": False,
        }
    ]


@patch("src.agents.supervisor.classificar_intencao_hibrida")
def test_supervisor_preserves_route_history(
    classify_mock,
):
    classify_mock.return_value = SupervisorDecision(
        intent="relatorio",
        next_node="report_agent",
        confidence=0.96,
        generate_report=True,
        use_database=True,
        reason="Relatório solicitado.",
        classification_source="rule",
    )

    previous = {
        "intent": "consulta_rag",
        "next_node": "rag_agent",
        "source": "rule",
        "reason": "Consulta anterior.",
        "confidence": 0.89,
        "fallback_used": False,
        "gemini_called": False,
    }

    result = supervisor_node(
        {
            "user_message": ("Gere meu relatório"),
            "context": {},
            "errors": [],
            "trace": [
                "context_builder:ready",
            ],
            "route_history": [
                previous,
            ],
        }
    )

    assert len(result["route_history"]) == 2

    assert result["route_history"][0] == previous

    assert result["route_history"][1]["next_node"] == "report_agent"


@patch("src.agents.supervisor.classificar_intencao_hibrida")
def test_supervisor_creates_detailed_trace(
    classify_mock,
):
    classify_mock.return_value = SupervisorDecision(
        intent="desconhecido",
        next_node="fallback_agent",
        confidence=0.20,
        reason=("Não foi possível determinar uma intenção segura."),
        classification_source="fallback",
        fallback_used=True,
    )

    result = supervisor_node(
        {
            "user_message": "Mensagem ambígua",
            "context": {},
            "errors": [],
            "trace": [
                "context_builder:ready",
            ],
            "route_history": [],
        }
    )

    assert result["trace"][0] == ("context_builder:ready")

    assert "supervisor:fallback:desconhecido" in result["trace"]

    assert result["route_source"] == "fallback"

    assert result["routing_reason"] == (
        "Não foi possível determinar uma intenção segura."
    )

    assert result["route_history"][-1]["next_node"] == "fallback_agent"

    assert result["route_history"][-1]["reason"] == (
        "Não foi possível determinar uma intenção segura."
    )

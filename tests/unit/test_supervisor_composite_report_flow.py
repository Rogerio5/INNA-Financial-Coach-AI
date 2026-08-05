from __future__ import annotations

import pytest

from src.agents.supervisor import (
    _detectar_diagnostico_com_relatorio,
    supervisor_node,
)


@pytest.mark.parametrize(
    "message",
    [
        ("Analise minha situação financeira e gere um relatório."),
        ("Faça um diagnóstico das minhas finanças e crie um PDF."),
        ("Minha renda é 5000, meus gastos são 3000. Analise e gere relatório."),
        ("Analise meu orçamento e exporte o resultado em um documento."),
    ],
)
def test_detects_composite_diagnosis_report_request(
    message: str,
):
    assert _detectar_diagnostico_com_relatorio(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "Gere um relatório.",
        "Exporte meu relatório em PDF.",
        "Analise minha situação financeira.",
        "Explique o que é reserva de emergência.",
    ],
)
def test_does_not_detect_non_composite_request(
    message: str,
):
    assert _detectar_diagnostico_com_relatorio(message) is False


def test_composite_request_routes_to_financial_agent():
    result = supervisor_node(
        {
            "user_message": ("Analise minha situação financeira e gere um relatório."),
            "context": {},
            "structured_response": {},
            "route_history": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["intent"] == ("diagnostico_financeiro")

    assert result["next_node"] == ("financial_agent")

    assert result["generate_report"] is True
    assert result["use_database"] is True

    assert "diagnóstico financeiro" in result["routing_reason"].lower()


def test_simple_report_request_still_routes_to_report_agent():
    result = supervisor_node(
        {
            "user_message": ("Gere um relatório em PDF com os dados existentes."),
            "context": {},
            "structured_response": {},
            "route_history": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["intent"] == "relatorio"
    assert result["next_node"] == "report_agent"
    assert result["generate_report"] is True


def test_diagnosis_without_report_stays_financial():
    result = supervisor_node(
        {
            "user_message": ("Analise minha situação financeira."),
            "context": {},
            "structured_response": {},
            "route_history": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["intent"] == ("diagnostico_financeiro")

    assert result["next_node"] == ("financial_agent")

    assert result["generate_report"] is False


def test_composite_decision_is_recorded_in_structured_response():
    result = supervisor_node(
        {
            "user_message": (
                "Faça um diagnóstico das minhas finanças e gere um relatório."
            ),
            "context": {},
            "structured_response": {},
            "route_history": [],
            "errors": [],
            "trace": [],
        }
    )

    decision = result["structured_response"]["supervisor_decision"]

    assert decision["intent"] == ("diagnostico_financeiro")

    assert decision["next_node"] == ("financial_agent")

    assert decision["generate_report"] is True


@pytest.mark.parametrize(
    "message",
    [
        "Analise minha situação financeira.",
        "Avalie minhas finanças.",
        "Faça um diagnóstico financeiro.",
        "Como está minha situação financeira?",
    ],
)
def test_detects_explicit_diagnosis_request(
    message: str,
):
    from src.agents.supervisor import (
        _detectar_pedido_diagnostico,
    )

    assert _detectar_pedido_diagnostico(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "Explique o que é diagnóstico financeiro.",
        "O que é reserva de emergência?",
        "Gere um relatório em PDF.",
        "Como funciona um orçamento mensal?",
    ],
)
def test_does_not_overclassify_other_requests_as_diagnosis(
    message: str,
):
    from src.agents.supervisor import (
        _detectar_pedido_diagnostico,
    )

    assert _detectar_pedido_diagnostico(message) is False


def test_explicit_diagnosis_has_no_report_handoff_flag():
    result = supervisor_node(
        {
            "user_message": ("Avalie minha situação financeira."),
            "context": {},
            "structured_response": {},
            "route_history": [],
            "errors": [],
            "trace": [],
        }
    )

    assert result["intent"] == ("diagnostico_financeiro")

    assert result["next_node"] == ("financial_agent")

    assert result["generate_report"] is False

from src.agents.graph import (
    executar_nucleo_inna,
)
from src.agents.supervisor import (
    classificar_intencao,
)


def test_supervisor_classifica_diagnostico():
    decisao = classificar_intencao(
        "Ganho 3000 e gasto 2500."
    )

    assert (
        decisao.intent
        == "diagnostico_financeiro"
    )
    assert decisao.next_node == "financial_agent"
    assert decisao.use_database is True


def test_supervisor_classifica_rag():
    decisao = classificar_intencao(
        "Como funciona uma reserva financeira?"
    )

    assert decisao.intent == "consulta_rag"
    assert decisao.next_node == "rag_agent"
    assert decisao.use_rag is True


def test_supervisor_classifica_relatorio():
    decisao = classificar_intencao(
        "Quero gerar meu relatório em PDF."
    )

    assert decisao.intent == "relatorio"
    assert decisao.next_node == "report_agent"
    assert decisao.generate_report is True


def test_grafo_executa_agente_financeiro():
    resultado = executar_nucleo_inna(
        "Tenho renda de 3000 e gasto 2500."
    )

    assert (
        resultado["intent"]
        == "diagnostico_financeiro"
    )
    assert (
        resultado["next_node"]
        == "financial_agent"
    )
    assert "agent_response" in (
        resultado["structured_response"]
    )
    assert (
        resultado["trace"][0]
        == "context_builder:0_messages"
    )

    assert (
        "supervisor:rule:diagnostico_financeiro"
        in resultado["trace"]
    )

    assert (
        resultado["trace"][-1]
        == "agent:financial_agent"
    )


def test_grafo_executa_fallback():
    resultado = executar_nucleo_inna(
        "Olá, tudo bem?"
    )

    assert resultado["intent"] == "desconhecido"
    assert (
        resultado["next_node"]
        == "fallback_agent"
    )

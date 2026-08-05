from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.agents.schemas import (
    SupervisorDecision,
    SupervisorLLMDecision,
)
from src.agents.supervisor import (
    classificar_intencao_hibrida,
    classificar_intencao_por_regras,
    supervisor_node,
)
from src.agents.supervisor_llm import (
    _normalizar_contexto,
    _obter_mensagem_protegida,
    _validar_compatibilidade,
)


def test_regra_classifica_relatorio_sem_gemini():
    with patch("src.agents.supervisor.classificar_com_gemini") as mock_gemini:
        decision = classificar_intencao_hibrida("Quero gerar meu relatório em PDF.")

    assert decision.intent == "relatorio"
    assert decision.next_node == "report_agent"
    assert decision.classification_source == "rule"
    assert decision.gemini_called is False
    assert decision.generate_report is True
    assert decision.use_database is True
    assert decision.confidence >= 0.90

    mock_gemini.assert_not_called()


def test_regra_classifica_diagnostico_financeiro():
    decision = classificar_intencao_por_regras("Tenho renda de 3000 e gasto 2500.")

    assert decision.intent == "diagnostico_financeiro"

    assert decision.next_node == "financial_agent"

    assert decision.use_database is True
    assert decision.use_rag is False


def test_regra_classifica_consulta_rag():
    decision = classificar_intencao_por_regras("O que é reserva de emergência?")

    assert decision.intent == "consulta_rag"
    assert decision.next_node == "rag_agent"
    assert decision.use_rag is True


def test_regra_classifica_educacao_financeira():
    decision = classificar_intencao_por_regras("Como organizar melhor minhas finanças?")

    assert decision.intent == "educacao_financeira"

    assert decision.next_node == "education_agent"

    assert decision.use_rag is True


def test_multiplas_intencoes_sao_ambiguas():
    decision = classificar_intencao_por_regras(
        ("Quero entender reserva financeira e gerar meu relatório em PDF.")
    )

    assert decision.intent == "desconhecido"
    assert decision.confidence < 0.75


@patch("src.agents.supervisor.classificar_com_gemini")
def test_mensagem_ambigua_usa_gemini(
    mock_gemini,
):
    mock_gemini.return_value = SupervisorDecision(
        intent="educacao_financeira",
        next_node="education_agent",
        confidence=0.88,
        use_rag=True,
        reason=("O usuário busca orientação financeira."),
        classification_source="gemini",
        classification_duration_ms=120,
        gemini_called=True,
    )

    context = {"rendered_prompt": ("Histórico protegido da conversa.")}

    decision = classificar_intencao_hibrida(
        ("Estou meio perdido e não sei qual caminho seguir."),
        context=context,
    )

    assert decision.intent == "educacao_financeira"

    assert decision.classification_source == "gemini"

    assert decision.gemini_called is True
    assert decision.fallback_used is False

    mock_gemini.assert_called_once_with(
        mensagem=("Estou meio perdido e não sei qual caminho seguir."),
        context=context,
    )


@patch("src.agents.supervisor.classificar_com_gemini")
def test_falha_do_gemini_usa_fallback(
    mock_gemini,
):
    mock_gemini.side_effect = RuntimeError("Serviço temporariamente indisponível")

    decision = classificar_intencao_hibrida("Não sei exatamente o que preciso.")

    assert decision.intent == "desconhecido"

    assert decision.next_node == "fallback_agent"

    assert decision.classification_source == "fallback"

    assert decision.fallback_used is True
    assert decision.gemini_called is True

    assert "RuntimeError" in str(decision.classification_error)


def test_validador_corrige_rota_incompatível():
    decision = SupervisorLLMDecision(
        intent="relatorio",
        next_node="education_agent",
        confidence=0.80,
        reason="O usuário solicitou um PDF.",
    )

    corrected = _validar_compatibilidade(decision)

    assert corrected.next_node == "report_agent"

    assert corrected.generate_report is True
    assert corrected.use_database is True


def test_validador_configura_rag():
    decision = SupervisorLLMDecision(
        intent="consulta_rag",
        next_node="rag_agent",
        confidence=0.84,
        reason="Pergunta conceitual.",
    )

    corrected = _validar_compatibilidade(decision)

    assert corrected.use_rag is True
    assert corrected.use_database is False


def test_contexto_enviado_ao_gemini_e_limitado():
    context = {"rendered_prompt": "a" * 15000}

    result = _normalizar_contexto(context)

    assert len(result) < 12100
    assert "CONTEXTO LIMITADO" in result


def test_contexto_invalido_retorna_vazio():
    assert _normalizar_contexto(None) == ""
    assert _normalizar_contexto([]) == ""


def test_supervisor_node_registra_metricas():
    with patch("src.agents.supervisor.classificar_intencao_hibrida") as mock_hybrid:
        mock_hybrid.return_value = SupervisorDecision(
            intent="consulta_rag",
            next_node="rag_agent",
            confidence=0.91,
            use_rag=True,
            reason="Consulta conceitual.",
            classification_source="gemini",
            classification_duration_ms=230,
            gemini_called=True,
        )

        result = supervisor_node(
            {
                "user_message": ("Pode explicar melhor isso?"),
                "context": {"rendered_prompt": ("Contexto protegido.")},
                "structured_response": {},
            }
        )

    structured = result["structured_response"]

    decision = structured["supervisor_decision"]

    metrics = structured["supervisor_metrics"]

    assert decision["intent"] == "consulta_rag"

    assert metrics["classification_source"] == "gemini"

    assert metrics["classification_confidence"] == 0.91

    assert metrics["gemini_called"] is True
    assert metrics["selected_agent"] == "rag_agent"

    assert result["trace"] == ["supervisor:gemini:consulta_rag"]


def test_supervisor_node_registra_erro():
    with patch("src.agents.supervisor.classificar_intencao_hibrida") as mock_hybrid:
        mock_hybrid.return_value = SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.20,
            reason="Falha na classificação.",
            classification_source="fallback",
            gemini_called=True,
            fallback_used=True,
            classification_error=("RuntimeError: indisponível"),
        )

        result = supervisor_node(
            {
                "user_message": "Mensagem ambígua",
                "structured_response": {},
            }
        )

    assert result["errors"] == ["RuntimeError: indisponível"]

    assert result["trace"] == ["supervisor:fallback:desconhecido"]


def test_schema_rejeita_confianca_maior_que_um():
    with pytest.raises(ValidationError):
        SupervisorDecision(
            intent="relatorio",
            next_node="report_agent",
            confidence=1.50,
            reason="Confiança inválida.",
        )


def test_schema_rejeita_confianca_negativa():
    with pytest.raises(ValidationError):
        SupervisorDecision(
            intent="relatorio",
            next_node="report_agent",
            confidence=-0.10,
            reason="Confiança inválida.",
        )


def test_schema_rejeita_rota_desconhecida():
    with pytest.raises(ValidationError):
        SupervisorDecision(
            intent="relatorio",
            next_node="agente_inventado",
            confidence=0.90,
            reason="Rota inválida.",
        )


def test_schema_rejeita_intencao_desconhecida():
    with pytest.raises(ValidationError):
        SupervisorDecision(
            intent="investimentos",
            next_node="financial_agent",
            confidence=0.90,
            reason="Intenção inválida.",
        )


def test_supervisor_preserva_trace_anterior():
    with patch("src.agents.supervisor.classificar_intencao_hibrida") as mock_hybrid:
        mock_hybrid.return_value = SupervisorDecision(
            intent="relatorio",
            next_node="report_agent",
            confidence=0.96,
            use_database=True,
            generate_report=True,
            reason="Solicitação de relatório.",
            classification_source="rule",
        )

        result = supervisor_node(
            {
                "user_message": ("Quero gerar um relatório."),
                "context": {},
                "structured_response": {},
                "trace": ["context_builder:0_messages"],
                "errors": [],
            }
        )

    assert result["trace"] == [
        "context_builder:0_messages",
        "supervisor:rule:relatorio",
    ]


def test_supervisor_preserva_erros_anteriores():
    with patch("src.agents.supervisor.classificar_intencao_hibrida") as mock_hybrid:
        mock_hybrid.return_value = SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.20,
            reason="Falha de classificação.",
            classification_source="fallback",
            gemini_called=True,
            fallback_used=True,
            classification_error=("RuntimeError: Gemini indisponível"),
        )

        result = supervisor_node(
            {
                "user_message": "Mensagem ambígua",
                "structured_response": {},
                "trace": ["context_builder:0_messages"],
                "errors": ["Erro anterior"],
            }
        )

    assert result["errors"] == [
        "Erro anterior",
        "RuntimeError: Gemini indisponível",
    ]

    assert result["trace"] == [
        "context_builder:0_messages",
        "supervisor:fallback:desconhecido",
    ]


def test_supervisor_llm_prioriza_mensagem_protegida():
    context = {"current_message": ("Meu e-mail é [EMAIL_PROTEGIDO].")}

    result = _obter_mensagem_protegida(
        "Meu e-mail é usuario@email.com.",
        context,
    )

    assert result == "Meu e-mail é [EMAIL_PROTEGIDO]."

    assert "usuario@email.com" not in result


def test_supervisor_llm_sanitiza_sem_contexto():
    result = _obter_mensagem_protegida(
        "Meu e-mail é usuario@email.com.",
        None,
    )

    assert "usuario@email.com" not in result
    assert "[EMAIL_PROTEGIDO]" in result


@patch("src.agents.supervisor.classificar_com_gemini")
def test_baixa_confianca_do_gemini_usa_fallback(
    mock_gemini,
):
    mock_gemini.return_value = SupervisorDecision(
        intent="educacao_financeira",
        next_node="education_agent",
        confidence=0.42,
        use_rag=True,
        reason="Classificação pouco segura.",
        classification_source="gemini",
        classification_duration_ms=150,
        gemini_called=True,
    )

    decision = classificar_intencao_hibrida("Talvez eu precise de alguma ajuda.")

    assert decision.intent == "desconhecido"

    assert decision.next_node == "fallback_agent"

    assert decision.classification_source == "fallback"

    assert decision.gemini_called is True
    assert decision.fallback_used is True
    assert decision.confidence == 0.42
    assert decision.classification_error is None

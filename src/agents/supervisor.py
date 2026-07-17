"""
Supervisor híbrido da INNA.

Fluxo:
1. Usa regras determinísticas em mensagens claras.
2. Usa Gemini com saída Pydantic em casos ambíguos.
3. Usa fallback seguro quando a classificação falha.
"""

from __future__ import annotations

import time
import unicodedata
from typing import Any

from src.agents.schemas import (
    SupervisorDecision,
)
from src.agents.state import InnaAgentState
from src.agents.supervisor_deadline import (
    classificar_com_gemini_com_deadline
    as classificar_com_gemini,
)


MIN_RULE_CONFIDENCE = 0.75
MIN_LLM_CONFIDENCE = 0.60


_REPORT_TERMS = {
    "gerar relatorio",
    "meu relatorio",
    "relatorio em pdf",
    "gerar pdf",
    "baixar pdf",
    "exportar relatorio",
    "documento financeiro",
}

_FINANCIAL_TERMS = {
    "minha renda",
    "meus gastos",
    "minhas dividas",
    "tenho renda",
    "ganho ",
    "gasto ",
    "meu saldo",
    "meu orcamento",
    "diagnostico financeiro",
    "score financeiro",
    "minhas parcelas",
    "estou devendo",
}

_RAG_TERMS = {
    "o que e",
    "como funciona",
    "qual a diferenca",
    "explique",
    "conceito de",
    "juros compostos",
    "reserva financeira",
    "reserva de emergencia",
    "cartao de credito",
}

_EDUCATION_TERMS = {
    "como organizar",
    "como planejar",
    "como economizar",
    "quero aprender",
    "me de dicas",
    "dicas para",
    "educacao financeira",
    "criar habito",
    "melhorar minhas financas",
}


def _normalizar(texto: str) -> str:
    texto = str(
        texto or ""
    ).strip().lower()

    normalized = unicodedata.normalize(
        "NFKD",
        texto,
    )

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )


def _contains_any(
    texto: str,
    termos: set[str],
) -> bool:
    return any(
        termo in texto
        for termo in termos
    )


def classificar_intencao_por_regras(
    mensagem: str,
) -> SupervisorDecision:
    """
    Classifica mensagens claras sem chamar o Gemini.
    """
    texto = _normalizar(
        mensagem
    )

    if not texto:
        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.10,
            reason="Mensagem vazia.",
            classification_source="rule",
        )

    matches = {
        "relatorio": _contains_any(
            texto,
            _REPORT_TERMS,
        ),
        "diagnostico_financeiro": (
            _contains_any(
                texto,
                _FINANCIAL_TERMS,
            )
        ),
        "consulta_rag": _contains_any(
            texto,
            _RAG_TERMS,
        ),
        "educacao_financeira": (
            _contains_any(
                texto,
                _EDUCATION_TERMS,
            )
        ),
    }

    matched_intents = [
        intent
        for intent, matched in matches.items()
        if matched
    ]

    if len(matched_intents) > 1:
        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.45,
            reason=(
                "Mais de uma intenção foi identificada "
                "pelas regras."
            ),
            classification_source="rule",
        )

    if matched_intents == ["relatorio"]:
        return SupervisorDecision(
            intent="relatorio",
            next_node="report_agent",
            confidence=0.96,
            use_database=True,
            generate_report=True,
            reason=(
                "A mensagem solicita relatório, "
                "PDF ou exportação."
            ),
            classification_source="rule",
        )

    if matched_intents == [
        "diagnostico_financeiro"
    ]:
        return SupervisorDecision(
            intent="diagnostico_financeiro",
            next_node="financial_agent",
            confidence=0.92,
            use_database=True,
            reason=(
                "A mensagem contém dados ou uma "
                "situação financeira pessoal."
            ),
            classification_source="rule",
        )

    if matched_intents == ["consulta_rag"]:
        return SupervisorDecision(
            intent="consulta_rag",
            next_node="rag_agent",
            confidence=0.89,
            use_rag=True,
            reason=(
                "A mensagem solicita explicação de "
                "um conceito financeiro."
            ),
            classification_source="rule",
        )

    if matched_intents == [
        "educacao_financeira"
    ]:
        return SupervisorDecision(
            intent="educacao_financeira",
            next_node="education_agent",
            confidence=0.86,
            use_rag=True,
            reason=(
                "A mensagem solicita orientação "
                "educativa ou planejamento."
            ),
            classification_source="rule",
        )

    return SupervisorDecision(
        intent="desconhecido",
        next_node="fallback_agent",
        confidence=0.40,
        reason=(
            "As regras não identificaram uma "
            "intenção suficientemente clara."
        ),
        classification_source="rule",
    )


def classificar_intencao(
    mensagem: str,
) -> SupervisorDecision:
    """
    Compatibilidade com os módulos anteriores.

    Esta função usa somente regras determinísticas.
    """
    return classificar_intencao_por_regras(
        mensagem
    )


def classificar_intencao_hibrida(
    mensagem: str,
    *,
    context: dict[str, Any] | None = None,
) -> SupervisorDecision:
    """
    Usa regras primeiro e Gemini somente quando necessário.
    """
    start = time.perf_counter()

    rule_decision = (
        classificar_intencao_por_regras(
            mensagem
        )
    )

    clear_rule = (
        rule_decision.intent
        != "desconhecido"
        and rule_decision.confidence
        >= MIN_RULE_CONFIDENCE
    )

    if clear_rule:
        rule_decision.classification_duration_ms = (
            int(
                (
                    time.perf_counter()
                    - start
                )
                * 1000
            )
        )

        return rule_decision

    try:
        llm_decision = classificar_com_gemini(
            mensagem=mensagem,
            context=context,
        )

        if (
            llm_decision.confidence
            >= MIN_LLM_CONFIDENCE
        ):
            return llm_decision

        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=(
                llm_decision.confidence
            ),
            reason=(
                "A classificação do Gemini ficou "
                "abaixo do limite mínimo de confiança."
            ),
            classification_source="fallback",
            classification_duration_ms=(
                llm_decision
                .classification_duration_ms
            ),
            gemini_called=True,
            fallback_used=True,
            classification_error=None,
        )

    except Exception as exc:
        duration_ms = int(
            (
                time.perf_counter()
                - start
            )
            * 1000
        )

        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.20,
            reason=(
                "Não foi possível determinar uma "
                "intenção segura."
            ),
            classification_source="fallback",
            classification_duration_ms=duration_ms,
            gemini_called=True,
            fallback_used=True,
            classification_error=(
                f"{type(exc).__name__}: "
                f"{str(exc)[:300]}"
            ),
        )


def supervisor_node(
    state: InnaAgentState,
) -> dict[str, Any]:
    """
    Nó LangGraph do supervisor híbrido.
    """
    mensagem = str(
        state.get(
            "user_message",
            "",
        )
    ).strip()

    context = state.get(
        "context",
        {},
    )

    if not isinstance(context, dict):
        context = {}

    decision = classificar_intencao_hibrida(
        mensagem,
        context=context,
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    structured_response[
        "supervisor_decision"
    ] = decision.model_dump()

    structured_response[
        "supervisor_metrics"
    ] = {
        "classification_source": (
            decision.classification_source
        ),
        "classification_confidence": (
            decision.confidence
        ),
        "classification_duration_ms": (
            decision.classification_duration_ms
        ),
        "gemini_called": (
            decision.gemini_called
        ),
        "fallback_used": (
            decision.fallback_used
        ),
        "selected_agent": (
            decision.next_node
        ),
        "classification_error": (
            decision.classification_error
        ),
    }

    existing_errors = list(
        state.get(
            "errors",
            [],
        )
        or []
    )

    errors = list(existing_errors)

    if decision.classification_error:
        errors.append(
            decision.classification_error
        )

    existing_trace = list(
        state.get(
            "trace",
            [],
        )
        or []
    )

    trace_item = (
        "supervisor:"
        f"{decision.classification_source}:"
        f"{decision.intent}"
    )

    updated_trace = [
        *existing_trace,
        trace_item,
    ]

    return {
        "intent": decision.intent,
        "confidence": decision.confidence,
        "next_node": decision.next_node,
        "use_rag": decision.use_rag,
        "use_database": (
            decision.use_database
        ),
        "generate_report": (
            decision.generate_report
        ),
        "structured_response": (
            structured_response
        ),
        "errors": errors,
        "trace": updated_trace,
    }


__all__ = [
    "MIN_RULE_CONFIDENCE",
    "MIN_LLM_CONFIDENCE",
    "classificar_intencao",
    "classificar_intencao_por_regras",
    "classificar_intencao_hibrida",
    "supervisor_node",
]

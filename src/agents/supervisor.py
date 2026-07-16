"""
Supervisor inicial da INNA.

A primeira versão usa regras determinísticas.
Posteriormente, a classificação poderá usar Gemini
com saída estruturada por Pydantic.
"""

from __future__ import annotations

import unicodedata

from src.agents.schemas import SupervisorDecision
from src.agents.state import InnaAgentState


def _normalizar(texto: str) -> str:
    texto = str(texto or "").strip().lower()

    return "".join(
        caractere
        for caractere in unicodedata.normalize(
            "NFKD",
            texto,
        )
        if not unicodedata.combining(
            caractere
        )
    )


def classificar_intencao(
    mensagem: str,
) -> SupervisorDecision:
    texto = _normalizar(mensagem)

    palavras_relatorio = {
        "relatorio",
        "pdf",
        "baixar",
        "exportar",
    }

    palavras_diagnostico = {
        "renda",
        "gasto",
        "gastos",
        "divida",
        "dividas",
        "saldo",
        "orcamento",
        "diagnostico",
        "score",
    }

    palavras_rag = {
        "explique",
        "o que e",
        "como funciona",
        "conceito",
        "juros",
        "reserva",
        "investimento",
        "cartao",
    }

    palavras_educacao = {
        "aprender",
        "educacao",
        "dica",
        "dicas",
        "organizar",
        "planejar",
        "economizar",
    }

    if any(
        palavra in texto
        for palavra in palavras_relatorio
    ):
        return SupervisorDecision(
            intent="relatorio",
            next_node="report_agent",
            confidence=0.90,
            use_database=True,
            generate_report=True,
            reason=(
                "A mensagem solicita relatório, "
                "PDF ou exportação."
            ),
        )

    if any(
        palavra in texto
        for palavra in palavras_diagnostico
    ):
        return SupervisorDecision(
            intent="diagnostico_financeiro",
            next_node="financial_agent",
            confidence=0.85,
            use_database=True,
            reason=(
                "A mensagem contém informações "
                "financeiras pessoais ou pedido "
                "de diagnóstico."
            ),
        )

    if any(
        palavra in texto
        for palavra in palavras_rag
    ):
        return SupervisorDecision(
            intent="consulta_rag",
            next_node="rag_agent",
            confidence=0.80,
            use_rag=True,
            reason=(
                "A mensagem solicita conhecimento "
                "ou explicação financeira."
            ),
        )

    if any(
        palavra in texto
        for palavra in palavras_educacao
    ):
        return SupervisorDecision(
            intent="educacao_financeira",
            next_node="education_agent",
            confidence=0.75,
            use_rag=True,
            reason=(
                "A mensagem solicita orientação "
                "educacional ou planejamento."
            ),
        )

    return SupervisorDecision(
        intent="desconhecido",
        next_node="fallback_agent",
        confidence=0.40,
        reason=(
            "Não foi possível identificar uma "
            "intenção financeira específica."
        ),
    )


def supervisor_node(
    state: InnaAgentState,
) -> InnaAgentState:
    decisao = classificar_intencao(
        state.get("user_message", "")
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        f"supervisor:{decisao.intent}"
    )

    return {
        **state,
        "intent": decisao.intent,
        "confidence": decisao.confidence,
        "next_node": decisao.next_node,
        "use_rag": decisao.use_rag,
        "use_database": decisao.use_database,
        "generate_report": (
            decisao.generate_report
        ),
        "structured_response": {
            "supervisor_decision": (
                decisao.model_dump()
            )
        },
        "trace": trace,
    }


__all__ = [
    "classificar_intencao",
    "supervisor_node",
]

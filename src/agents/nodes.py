"""
Nós especializados do primeiro grafo da INNA.
"""

from __future__ import annotations

from src.agents.schemas import AgentResponse
from src.agents.state import InnaAgentState


def _finalizar(
    state: InnaAgentState,
    *,
    agent: str,
    summary: str,
    recommendations: list[str],
    next_steps: list[str],
) -> InnaAgentState:
    resposta = AgentResponse(
        agent=agent,
        intent=state.get(
            "intent",
            "desconhecido",
        ),
        summary=summary,
        recommendations=recommendations,
        next_steps=next_steps,
        confidence=float(
            state.get("confidence", 1.0)
        ),
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(f"agent:{agent}")

    return {
        **state,
        "response": resposta.summary,
        "structured_response": {
            **state.get(
                "structured_response",
                {},
            ),
            "agent_response": (
                resposta.model_dump()
            ),
        },
        "trace": trace,
    }


def financial_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="financial_agent",
        summary=(
            "A solicitação foi encaminhada para "
            "o agente de diagnóstico financeiro."
        ),
        recommendations=[
            "Analisar renda, gastos e dívidas.",
            "Calcular saldo e comprometimento.",
        ],
        next_steps=[
            "Integrar o financial_engine atual.",
            "Consultar diagnósticos anteriores.",
        ],
    )


def education_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="education_agent",
        summary=(
            "A solicitação foi encaminhada para "
            "o agente de educação financeira."
        ),
        recommendations=[
            "Fornecer explicação educativa.",
            "Criar passos simples e seguros.",
        ],
        next_steps=[
            "Integrar conteúdo do RAG.",
        ],
    )


def rag_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="rag_agent",
        summary=(
            "A solicitação foi encaminhada para "
            "o agente de conhecimento financeiro."
        ),
        recommendations=[
            "Consultar a base RAG da INNA.",
            "Apresentar fontes utilizadas.",
        ],
        next_steps=[
            "Adaptar search_knowledge_base.",
        ],
    )


def report_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="report_agent",
        summary=(
            "A solicitação foi encaminhada para "
            "o agente de relatórios."
        ),
        recommendations=[
            "Consultar diagnóstico salvo.",
            "Gerar relatório em PDF.",
        ],
        next_steps=[
            "Integrar gerar_relatorio_pdf.",
        ],
    )


def fallback_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="fallback_agent",
        summary=(
            "Não identifiquei uma solicitação "
            "financeira específica."
        ),
        recommendations=[
            (
                "Explique se deseja diagnóstico, "
                "educação financeira, consulta "
                "ou relatório."
            )
        ],
        next_steps=[],
    )


__all__ = [
    "financial_agent_node",
    "education_agent_node",
    "rag_agent_node",
    "report_agent_node",
    "fallback_agent_node",
]

"""
Nós especializados do primeiro grafo da INNA.
"""

from __future__ import annotations

from src.agent_tools.rag_tools import consultar_rag_inna
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
        "conversation_history": [
            {
                "role": "assistant",
                "content": resposta.summary,
            }
        ],
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
    """
    Agente funcional de conhecimento financeiro.

    Utiliza o RAG híbrido existente da INNA e grava
    resultado, fontes, duração e modo no estado.
    """
    pergunta = str(
        state.get("user_message", "")
    ).strip()

    idioma = str(
        state.get("language", "pt")
        or "pt"
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        "tool:consultar_rag_inna:start"
    )

    resultado = consultar_rag_inna(
        pergunta,
        idioma=idioma,
        top_k=4,
    )

    tool_results = list(
        state.get("tool_results", [])
    )

    tool_results.append(
        {
            "tool": "consultar_rag_inna",
            "ok": resultado.ok,
            "mode": resultado.mode,
            "duration_ms": (
                resultado.duration_ms
            ),
            "retrieved_documents": (
                resultado.retrieved_documents
            ),
            "sources": resultado.sources,
            "error_type": (
                resultado.error_type
            ),
        }
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    structured_response[
        "rag_execution"
    ] = {
        "ok": resultado.ok,
        "mode": resultado.mode,
        "duration_ms": (
            resultado.duration_ms
        ),
        "retrieved_documents": (
            resultado.retrieved_documents
        ),
        "sources": resultado.sources,
    }

    if not resultado.ok:
        errors = list(
            state.get("errors", [])
        )

        mensagem_erro = (
            resultado.error_message
            or "Falha ao consultar o RAG."
        )

        errors.append(mensagem_erro)

        trace.append(
            "tool:consultar_rag_inna:error"
        )

        resposta = AgentResponse(
            agent="rag_agent",
            intent=state.get(
                "intent",
                "consulta_rag",
            ),
            summary=(
                "Não foi possível consultar "
                "a base de conhecimento neste momento."
            ),
            recommendations=[
                (
                    "Tente novamente ou reformule "
                    "a pergunta financeira."
                )
            ],
            next_steps=[],
            sources=[],
            confidence=0.30,
        )

        structured_response[
            "agent_response"
        ] = resposta.model_dump()

        return {
            **state,
            "response": resposta.summary,
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": resposta.summary,
                }
            ],
            "structured_response": (
                structured_response
            ),
            "tool_results": tool_results,
            "errors": errors,
            "trace": trace + [
                "agent:rag_agent:error"
            ],
        }

    trace.append(
        "tool:consultar_rag_inna:success"
    )

    resposta = AgentResponse(
        agent="rag_agent",
        intent=state.get(
            "intent",
            "consulta_rag",
        ),
        summary=resultado.answer,
        recommendations=[],
        next_steps=[],
        sources=resultado.sources,
        confidence=float(
            state.get("confidence", 0.80)
        ),
    )

    structured_response[
        "agent_response"
    ] = resposta.model_dump()

    return {
        **state,
        "response": resultado.answer,
        "conversation_history": [
            {
                "role": "assistant",
                "content": resultado.answer,
            }
        ],
        "structured_response": (
            structured_response
        ),
        "tool_results": tool_results,
        "errors": list(
            state.get("errors", [])
        ),
        "trace": trace + [
            "agent:rag_agent"
        ],
    }


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

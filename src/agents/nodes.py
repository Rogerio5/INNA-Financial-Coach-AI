"""
Nós especializados do primeiro grafo da INNA.
"""

from __future__ import annotations

from src.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.agent_tools.runtime import (
    executar_ferramenta_inna,
)
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
    Agente de conhecimento financeiro da INNA.

    Cria um ToolCall formal e executa o RAG por meio
    do catálogo, política de permissões, validação
    Pydantic e ToolExecutor.
    """
    pergunta = str(
        state.get("user_message", "")
    ).strip()

    idioma = str(
        state.get("language", "pt")
        or "pt"
    ).strip()

    try:
        top_k = int(
            state.get("rag_top_k", 4)
            or 4
        )
    except (TypeError, ValueError):
        top_k = 4

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        f"tool:{RAG_TOOL_NAME}:start"
    )

    def optional_text(
        value,
    ) -> str | None:
        normalized = str(
            value or ""
        ).strip()

        return normalized or None

    tool_call = ToolCall(
        tool_name=RAG_TOOL_NAME,
        arguments={
            "pergunta": pergunta,
            "idioma": idioma,
            "top_k": top_k,
        },
        context=ToolExecutionContext(
            requested_by="rag_agent",
            user_id=optional_text(
                state.get("user_id")
                or state.get("usuario_id")
            ),
            session_id=optional_text(
                state.get("thread_id")
                or state.get("session_id")
            ),
            trace_id=optional_text(
                state.get("trace_id")
            ),
            metadata={
                "intent": str(
                    state.get(
                        "intent",
                        "consulta_rag",
                    )
                )[:100],
                "route_source": str(
                    state.get(
                        "route_source",
                        "",
                    )
                )[:100],
            },
        ),
    )

    tool_result = executar_ferramenta_inna(
        tool_call
    )

    tool_results = list(
        state.get("tool_results", [])
    )

    compact_tool_result = {
        "call_id": tool_result.call_id,
        "tool": tool_result.tool_name,
        "status": tool_result.status.value,
        "ok": tool_result.ok,
        "duration_ms": (
            tool_result.duration_ms
        ),
    }

    if tool_result.error is not None:
        compact_tool_result.update({
            "error_code": (
                tool_result.error.code
            ),
            "retryable": (
                tool_result.error.retryable
            ),
        })

    tool_results.append(
        compact_tool_result
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    structured_response[
        "rag_execution"
    ] = dict(
        compact_tool_result
    )

    if (
        tool_result.status
        != ToolStatus.SUCCESS
        or not tool_result.output
    ):
        safe_error = (
            tool_result.error.message
            if tool_result.error
            else (
                "A ferramenta RAG não retornou "
                "um resultado utilizável."
            )
        )

        errors = list(
            state.get("errors", [])
        )

        errors.append(
            safe_error
        )

        trace.append(
            f"tool:{RAG_TOOL_NAME}:"
            f"{tool_result.status.value}"
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

    output = tool_result.output

    resposta_texto = str(
        output.get("resposta", "")
    ).strip()

    fontes = [
        str(source).strip()
        for source in output.get(
            "fontes",
            [],
        )
        if str(source).strip()
    ]

    modo = str(
        output.get("modo", "rag")
    )

    documentos_recuperados = int(
        output.get(
            "documentos_recuperados",
            0,
        )
        or 0
    )

    duracao_rag_ms = int(
        output.get(
            "duracao_rag_ms",
            0,
        )
        or 0
    )

    structured_response[
        "rag_execution"
    ].update({
        "mode": modo,
        "retrieved_documents": (
            documentos_recuperados
        ),
        "rag_duration_ms": (
            duracao_rag_ms
        ),
        "sources": fontes,
    })

    trace.append(
        f"tool:{RAG_TOOL_NAME}:success"
    )

    resposta = AgentResponse(
        agent="rag_agent",
        intent=state.get(
            "intent",
            "consulta_rag",
        ),
        summary=resposta_texto,
        recommendations=[],
        next_steps=[],
        sources=fontes,
        confidence=float(
            state.get("confidence")
            or 0.80
        ),
    )

    structured_response[
        "agent_response"
    ] = resposta.model_dump()

    return {
        **state,
        "response": resposta_texto,
        "conversation_history": [
            {
                "role": "assistant",
                "content": resposta_texto,
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

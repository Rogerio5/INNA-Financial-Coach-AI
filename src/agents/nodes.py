"""
Nós especializados do primeiro grafo da INNA.
"""

from __future__ import annotations

from src.compartilhado.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolStatus,
)
from src.compartilhado.agent_tools.financial_tools import (
    FINANCIAL_DIAGNOSIS_TOOL_NAME,
)
from src.compartilhado.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.compartilhado.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.agents.financial_history_flow import (
    executar_fluxo_historico_financeiro,
)
from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)
from src.agents.report_flow import (
    executar_fluxo_relatorio,
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
    """
    Agente financeiro determinístico da INNA.

    O nó resolve os dados financeiros, solicita os
    campos ausentes ou executa a ferramenta formal
    de diagnóstico financeiro.
    """

    # Resolução semântica de consultas simples
    # baseadas em dados financeiros anteriores.
    # Não substitui a tool formal de diagnóstico.
    from src.agents.financial_semantic_memory import (
        resolve_simple_balance_follow_up,
    )

    semantic_follow_up = (
        resolve_simple_balance_follow_up(
            dict(state or {})
        )
    )

    if semantic_follow_up is not None:
        return semantic_follow_up

    if str(
        state.get("intent", "")
    ) == "historico_financeiro":
        return (
            executar_fluxo_historico_financeiro(
                state
            )
        )

    resolution = resolver_entrada_financeira(
        dict(state)
    )

    trace = list(
        state.get("trace", [])
    )

    errors = list(
        state.get("errors", [])
    )

    tool_results = list(
        state.get("tool_results", [])
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    structured_response[
        "financial_input_resolution"
    ] = {
        "ready": resolution.ready,
        "missing_fields": list(
            resolution.missing_fields
        ),
        "resolved_fields": sorted(
            resolution.collected_data
        ),
        "field_sources": dict(
            resolution.field_sources
        ),
        "warnings": list(
            resolution.warnings
        ),
    }

    # ======================================================
    # Dados ainda incompletos
    # ======================================================

    if not resolution.ready:
        summary = (
            resolution.clarification_message
            or (
                "Ainda faltam informações para "
                "calcular o diagnóstico financeiro."
            )
        )

        resposta = AgentResponse(
            agent="financial_agent",
            intent=state.get(
                "intent",
                "diagnostico_financeiro",
            ),
            summary=summary,
            recommendations=[
                (
                    "Informe somente os valores "
                    "financeiros que estão faltando."
                )
            ],
            next_steps=[
                str(field)
                for field
                in resolution.missing_fields
            ],
            sources=[],
            confidence=0.95,
        )

        structured_response[
            "agent_response"
        ] = resposta.model_dump()

        return {
            **state,
            "response": summary,
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": summary,
                }
            ],
            "structured_response": (
                structured_response
            ),
            "tool_results": tool_results,
            "errors": errors,
            "handoff_required": False,
            "handoff_target": "",
            "handoff_reason": "",
            "trace": trace + [
                "financial_input:incomplete",
                "agent:financial_agent",
            ],
        }

    # ======================================================
    # Construção segura do contexto da ferramenta
    # ======================================================

    def optional_text(
        value,
    ) -> str | None:
        normalized = str(
            value or ""
        ).strip()

        return normalized or None

    tool_call = ToolCall(
        tool_name=(
            FINANCIAL_DIAGNOSIS_TOOL_NAME
        ),
        arguments=dict(
            resolution.arguments or {}
        ),
        context=ToolExecutionContext(
            requested_by="financial_agent",
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
                        "diagnostico_financeiro",
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

    trace.append(
        f"tool:"
        f"{FINANCIAL_DIAGNOSIS_TOOL_NAME}:"
        f"start"
    )

    tool_result = executar_ferramenta_inna(
        tool_call
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

    structured_response[
        "financial_execution"
    ] = dict(
        compact_tool_result
    )

    # ======================================================
    # Falha segura da ferramenta
    # ======================================================

    if (
        tool_result.status
        != ToolStatus.SUCCESS
        or not tool_result.output
    ):
        safe_error = (
            tool_result.error.message
            if tool_result.error
            else (
                "A ferramenta financeira não "
                "retornou um resultado utilizável."
            )
        )

        errors.append(
            safe_error
        )

        trace.append(
            f"tool:"
            f"{FINANCIAL_DIAGNOSIS_TOOL_NAME}:"
            f"{tool_result.status.value}"
        )

        resposta = AgentResponse(
            agent="financial_agent",
            intent=state.get(
                "intent",
                "diagnostico_financeiro",
            ),
            summary=(
                "Não foi possível calcular o "
                "diagnóstico financeiro neste momento."
            ),
            recommendations=[
                (
                    "Revise os valores informados "
                    "e tente novamente."
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
            "handoff_required": False,
            "handoff_target": "",
            "handoff_reason": "",
            "trace": trace + [
                "agent:financial_agent:error"
            ],
        }

    # ======================================================
    # Resultado financeiro aprovado
    # ======================================================

    output = dict(
        tool_result.output
    )

    moeda = str(
        output.get("moeda", "BRL")
    )

    saldo = float(
        output.get(
            "saldo_estimado",
            0,
        )
    )

    comprometimento = float(
        output.get(
            "comprometimento_renda_percentual",
            0,
        )
    )

    meses_reserva = float(
        output.get(
            "meses_reserva_estimados",
            0,
        )
    )

    score = int(
        output.get(
            "score_financeiro",
            0,
        )
    )

    risco = str(
        output.get(
            "nivel_risco",
            "Indefinido",
        )
    )

    situacao = str(
        output.get(
            "situacao",
            "",
        )
    )

    summary = (
        "Diagnóstico financeiro calculado. "
        f"Saldo mensal estimado: "
        f"{moeda} {saldo:.2f}. "
        f"Comprometimento da renda: "
        f"{comprometimento:.2f}%. "
        f"Reserva estimada: "
        f"{meses_reserva:.2f} meses de despesas. "
        f"Score financeiro: {score}/100. "
        f"Nível de risco: {risco}."
    )

    if situacao == "deficit":
        recommendations = [
            (
                "Revise primeiro as despesas "
                "e parcelas que mais pressionam "
                "o orçamento mensal."
            )
        ]

    elif situacao == "equilibrio_sem_margem":
        recommendations = [
            (
                "Busque criar uma pequena margem "
                "mensal antes de assumir novos "
                "compromissos."
            )
        ]

    elif situacao == "saldo_positivo":
        recommendations = [
            (
                "Avalie destinar uma parte possível "
                "do saldo mensal para fortalecer "
                "a reserva financeira."
            )
        ]

    else:
        recommendations = [
            (
                "Revise os dados de renda e despesas "
                "antes de tomar decisões financeiras."
            )
        ]

    structured_response[
        "diagnostico_financeiro"
    ] = output

    structured_response[
        "agent_response"
    ] = AgentResponse(
        agent="financial_agent",
        intent=state.get(
            "intent",
            "diagnostico_financeiro",
        ),
        summary=summary,
        recommendations=recommendations,
        next_steps=[],
        sources=[],
        confidence=float(
            state.get("confidence")
            or 0.90
        ),
    ).model_dump()

    trace.append(
        f"tool:"
        f"{FINANCIAL_DIAGNOSIS_TOOL_NAME}:"
        f"success"
    )

    # ======================================================
    # Solicitação explícita de handoff para relatório
    # ======================================================

    existing_handoff = state.get(
        "handoff_current"
    )

    existing_handoff_status = ""

    if isinstance(
        existing_handoff,
        dict,
    ):
        existing_handoff_status = str(
            existing_handoff.get(
                "status",
                "",
            )
        ).strip()

    active_handoff_statuses = {
        "requested",
        "accepted",
    }

    handoff_already_active = (
        existing_handoff_status
        in active_handoff_statuses
    )

    report_requested = bool(
        state.get(
            "generate_report",
            False,
        )
    )

    diagnosis_intent = (
        str(
            state.get(
                "intent",
                "",
            )
        ).strip()
        == "diagnostico_financeiro"
    )

    handoff_limit_exceeded = bool(
        state.get(
            "handoff_limit_exceeded",
            False,
        )
    )

    should_request_report_handoff = (
        report_requested
        and diagnosis_intent
        and not handoff_already_active
        and not handoff_limit_exceeded
    )

    handoff_reason = ""

    if should_request_report_handoff:
        handoff_reason = (
            "O diagnóstico financeiro foi concluído "
            "com sucesso e o usuário solicitou a "
            "geração de um relatório."
        )

        structured_response[
            "handoff_request"
        ] = {
            "from_agent": "financial_agent",
            "to_agent": "report_agent",
            "reason": handoff_reason,
            "trigger": (
                "diagnosis_completed_with_report_request"
            ),
            "diagnosis_available": True,
            "report_requested": True,
        }

        trace.append(
            "handoff:intent:"
            "financial_agent->report_agent"
        )

    return {
        **state,
        "response": summary,
        "conversation_history": [
            {
                "role": "assistant",
                "content": summary,
            }
        ],
        "structured_response": (
            structured_response
        ),
        "tool_results": tool_results,
        "errors": errors,
        "handoff_required": (
            should_request_report_handoff
        ),
        "handoff_target": (
            "report_agent"
            if should_request_report_handoff
            else ""
        ),
        "handoff_reason": handoff_reason,
        "trace": trace + [
            "agent:financial_agent"
        ],
    }

def _execute_rag_for_agent(
    state: InnaAgentState,
    *,
    agent: str,
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
            requested_by=agent,
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
            agent=agent,
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
                f"agent:{agent}:error"
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


    contexto_recuperado = [
        str(item).strip()
        for item in output.get(
            "contexto_recuperado",
            [],
        )
        if str(item).strip()
    ]

    raw_retrieval_telemetry = output.get(
        "retrieval_telemetry",
        {},
    )

    retrieval_telemetry = (
        dict(
            raw_retrieval_telemetry
        )
        if isinstance(
            raw_retrieval_telemetry,
            dict,
        )
        else {}
    )

    raw_llm_usage = output.get(
        "llm_usage",
        {},
    )

    llm_usage: dict[str, int] = {}

    if isinstance(
        raw_llm_usage,
        dict,
    ):
        for key in (
            "input_tokens",
            "output_tokens",
            "total_tokens",
        ):
            try:
                llm_usage[key] = max(
                    0,
                    int(
                        raw_llm_usage.get(
                            key,
                            0,
                        )
                        or 0
                    ),
                )
            except (
                TypeError,
                ValueError,
            ):
                llm_usage[key] = 0

        if (
            llm_usage["total_tokens"]
            <= 0
        ):
            llm_usage[
                "total_tokens"
            ] = (
                llm_usage[
                    "input_tokens"
                ]
                + llm_usage[
                    "output_tokens"
                ]
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
        "retrieval_context": (
            contexto_recuperado
        ),
        "llm_usage": llm_usage,
        "retrieval_telemetry": (
            retrieval_telemetry
        ),
    })

    trace.append(
        f"tool:{RAG_TOOL_NAME}:success"
    )

    resposta = AgentResponse(
        agent=agent,
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
            f"agent:{agent}"
        ],
    }

def education_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Agente de educação financeira fundamentado
    no RAG híbrido e formal da INNA.
    """
    return _execute_rag_for_agent(
        state,
        agent="education_agent",
    )


def rag_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Agente especializado em consultas diretas
    à base de conhecimento financeiro.
    """
    return _execute_rag_for_agent(
        state,
        agent="rag_agent",
    )


def report_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Agente profissional de relatórios da INNA.

    Consulta dados oficiais por tools autorizadas
    e prepara uma estrutura revisável. Não recalcula
    indicadores e não gera o PDF diretamente.
    """
    return executar_fluxo_relatorio(
        state
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

"""
Agente financeiro principal da INNA.

Implementacao oficial do dominio financeiro.
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
from src.compartilhado.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.agents.financial_history_flow import (
    executar_fluxo_historico_financeiro,
)
from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)
from src.plataforma.orquestracao.contracts import (
    AgentResponse,
)
from src.plataforma.orquestracao.state import (
    InnaAgentState,
)

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

def _financial_agent_impl(
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


def financial_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Entrada canonica do agente financeiro.

    Preserva temporariamente monkeypatches historicos
    aplicados em src.agents.nodes durante a migracao.
    """
    import sys

    legacy = sys.modules.get(
        "src.agents.nodes"
    )

    original_execute = (
        executar_ferramenta_inna
    )
    original_resolver = (
        resolver_entrada_financeira
    )

    try:
        if legacy is not None:
            patched_execute = getattr(
                legacy,
                "executar_ferramenta_inna",
                original_execute,
            )

            patched_resolver = getattr(
                legacy,
                "resolver_entrada_financeira",
                original_resolver,
            )

            globals()[
                "executar_ferramenta_inna"
            ] = patched_execute

            globals()[
                "resolver_entrada_financeira"
            ] = patched_resolver

        return _financial_agent_impl(
            state
        )

    finally:
        globals()[
            "executar_ferramenta_inna"
        ] = original_execute

        globals()[
            "resolver_entrada_financeira"
        ] = original_resolver

__all__ = [
    "financial_agent_node",
]

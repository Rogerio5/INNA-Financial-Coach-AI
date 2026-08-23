"""
Fluxo profissional do agente de relatório da INNA.

Etapas:
1. valida identidade confiável;
2. consulta histórico financeiro oficial;
3. prepara estrutura determinística do relatório;
4. retorna conteúdo pronto para revisão de risco.

O fluxo não:
- recalcula indicadores financeiros;
- gera PDF diretamente;
- aceita identidade controlada pela mensagem;
- chama Gemini.
"""

from __future__ import annotations

from typing import Any

from src.compartilhado.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolStatus,
)
from src.compartilhado.agent_tools.financial_history_tools import (
    FINANCIAL_HISTORY_TOOL_NAME,
)
from src.compartilhado.agent_tools.report_tools import (
    PREPARE_FINANCIAL_REPORT_TOOL_NAME,
)
from src.compartilhado.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.modulos.financeiro.seguranca_financeira.risk_reviewer import (
    apply_risk_review_to_report,
)
from src.plataforma.orquestracao.contracts import AgentResponse
from src.plataforma.orquestracao.state import InnaAgentState


DEFAULT_REPORT_HISTORY_LIMIT = 5
MAX_REPORT_HISTORY_LIMIT = 20


def _optional_text(
    value: Any,
) -> str | None:
    normalized = str(
        value or ""
    ).strip()

    return normalized or None


def _normalized_limit(
    value: Any,
) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        limit = DEFAULT_REPORT_HISTORY_LIMIT

    return min(
        MAX_REPORT_HISTORY_LIMIT,
        max(1, limit),
    )


def _safe_tool_result(
    result: Any,
) -> dict[str, Any]:
    compact = {
        "call_id": result.call_id,
        "tool": result.tool_name,
        "status": result.status.value,
        "ok": result.ok,
        "duration_ms": result.duration_ms,
    }

    if result.error is not None:
        compact.update({
            "error_code": result.error.code,
            "retryable": result.error.retryable,
        })

    return compact


def _error_response(
    state: InnaAgentState,
    *,
    summary: str,
    error_code: str,
    trace: list[str],
    tool_results: list[dict[str, Any]],
    structured_response: dict[str, Any],
) -> InnaAgentState:
    errors = list(
        state.get("errors", [])
        or []
    )

    errors.append(error_code)

    response = AgentResponse(
        agent="report_agent",
        intent="relatorio",
        summary=summary,
        recommendations=[
            (
                "Confirme se existe um diagnóstico "
                "financeiro salvo e tente novamente."
            )
        ],
        next_steps=[],
        sources=[],
        confidence=0.30,
    )

    structured_response[
        "agent_response"
    ] = response.model_dump()

    return {
        **state,
        "response": response.summary,
        "conversation_history": [
            {
                "role": "assistant",
                "content": response.summary,
            }
        ],
        "structured_response": structured_response,
        "tool_results": tool_results,
        "errors": errors,
        "trace": trace + [
            "agent:report_agent:error",
        ],
    }


def executar_fluxo_relatorio(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Executa o fluxo completo de preparação do relatório.
    """
    trusted_user_id = _optional_text(
        state.get("user_id")
        or state.get("usuario_id")
    )

    session_id = _optional_text(
        state.get("thread_id")
        or state.get("session_id")
    )

    trace_id = _optional_text(
        state.get("trace_id")
    )

    idioma = str(
        state.get("language", "pt")
        or "pt"
    ).strip()

    limite = _normalized_limit(
        state.get(
            "report_history_limit",
            DEFAULT_REPORT_HISTORY_LIMIT,
        )
    )

    trace = list(
        state.get("trace", [])
        or []
    )

    tool_results = list(
        state.get("tool_results", [])
        or []
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
        or {}
    )

    structured_response[
        "report_request"
    ] = {
        "history_limit": limite,
        "identity_available": bool(
            trusted_user_id
        ),
        "identity_source": (
            "tool_execution_context"
        ),
        "language": idioma,
    }

    if not trusted_user_id:
        return _error_response(
            state,
            summary=(
                "Não foi possível preparar o relatório "
                "porque a identidade autenticada não "
                "está disponível."
            ),
            error_code=(
                "trusted_user_identity_missing"
            ),
            trace=trace + [
                "report:missing_user_identity",
            ],
            tool_results=tool_results,
            structured_response=structured_response,
        )

    context = ToolExecutionContext(
        requested_by="report_agent",
        user_id=trusted_user_id,
        session_id=session_id,
        trace_id=trace_id,
        metadata={
            "intent": "relatorio",
            "route_source": str(
                state.get(
                    "route_source",
                    "",
                )
            )[:100],
        },
    )

    trace.append(
        f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:start"
    )

    history_result = executar_ferramenta_inna(
        ToolCall(
            tool_name=FINANCIAL_HISTORY_TOOL_NAME,
            arguments={
                "limite": limite,
            },
            context=context,
        )
    )

    compact_history = _safe_tool_result(
        history_result
    )

    tool_results.append(
        compact_history
    )

    structured_response[
        "report_history_execution"
    ] = dict(
        compact_history
    )

    if (
        history_result.status
        != ToolStatus.SUCCESS
        or history_result.output is None
    ):
        trace.append(
            f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:"
            f"{history_result.status.value}"
        )

        error_code = (
            history_result.error.code
            if history_result.error
            else "financial_history_unavailable"
        )

        return _error_response(
            state,
            summary=(
                "Não foi possível consultar o histórico "
                "financeiro necessário para preparar "
                "o relatório."
            ),
            error_code=error_code,
            trace=trace,
            tool_results=tool_results,
            structured_response=structured_response,
        )

    history_output = dict(
        history_result.output
    )

    diagnostics = list(
        history_output.get(
            "diagnosticos",
            [],
        )
        or []
    )

    structured_response[
        "report_history_execution"
    ].update({
        "has_history": bool(
            history_output.get(
                "possui_historico",
                False,
            )
        ),
        "total_returned": int(
            history_output.get(
                "total_retornado",
                len(diagnostics),
            )
            or 0
        ),
    })

    trace.append(
        f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:success"
    )

    trace.append(
        f"tool:{PREPARE_FINANCIAL_REPORT_TOOL_NAME}:start"
    )

    prepare_result = executar_ferramenta_inna(
        ToolCall(
            tool_name=(
                PREPARE_FINANCIAL_REPORT_TOOL_NAME
            ),
            arguments={
                "diagnosticos": diagnostics,
                "titulo": (
                    "Relatório Financeiro INNA"
                ),
                "idioma": idioma,
                "recomendacoes": [],
                "proximos_passos": [],
            },
            context=context,
        )
    )

    compact_preparation = _safe_tool_result(
        prepare_result
    )

    tool_results.append(
        compact_preparation
    )

    structured_response[
        "report_preparation_execution"
    ] = dict(
        compact_preparation
    )

    if (
        prepare_result.status
        != ToolStatus.SUCCESS
        or prepare_result.output is None
    ):
        trace.append(
            f"tool:"
            f"{PREPARE_FINANCIAL_REPORT_TOOL_NAME}:"
            f"{prepare_result.status.value}"
        )

        error_code = (
            prepare_result.error.code
            if prepare_result.error
            else "report_preparation_failed"
        )

        return _error_response(
            state,
            summary=(
                "O histórico foi consultado, mas não "
                "foi possível preparar a estrutura "
                "segura do relatório."
            ),
            error_code=error_code,
            trace=trace,
            tool_results=tool_results,
            structured_response=structured_response,
        )

    prepared_report = dict(
        prepare_result.output
    )

    trace.append(
        "risk_reviewer:start"
    )

    reviewed_report = (
        apply_risk_review_to_report(
            prepared_report
        )
    )

    risk_review = dict(
        reviewed_report.get(
            "risk_review",
            {},
        )
        or {}
    )

    structured_response[
        "financial_report"
    ] = reviewed_report

    structured_response[
        "risk_review"
    ] = risk_review

    structured_response[
        "report_preparation_execution"
    ].update({
        "total_diagnoses": (
            reviewed_report.get(
                "total_diagnosticos",
                0,
            )
        ),
        "ready_for_risk_review": (
            reviewed_report.get(
                "ready_for_risk_review",
                False,
            )
        ),
        "ready_for_pdf_rendering": (
            reviewed_report.get(
                "ready_for_pdf_rendering",
                False,
            )
        ),
        "financial_values_recalculated": (
            reviewed_report.get(
                "financial_values_recalculated",
                True,
            )
        ),
        "risk_review_approved": (
            reviewed_report.get(
                "risk_review_approved",
                False,
            )
        ),
    })

    trace.append(
        f"tool:"
        f"{PREPARE_FINANCIAL_REPORT_TOOL_NAME}:"
        "success"
    )

    if risk_review.get(
        "approved",
        False,
    ):
        trace.append(
            "risk_reviewer:approved"
        )
    else:
        trace.append(
            "risk_reviewer:blocked"
        )

    if (
        reviewed_report.get(
            "possui_diagnostico"
        )
        and risk_review.get(
            "approved",
            False,
        )
    ):
        summary = (
            "O relatório financeiro foi preparado "
            "com os dados oficiais, aprovado pela "
            "revisão de risco e está pronto para PDF."
        )

        recommendations = [
            (
                "Mantenha os indicadores oficiais "
                "sem alterações durante a geração "
                "do documento."
            )
        ]

        next_steps = [
            (
                "Gerar o PDF a partir da estrutura "
                "aprovada pelo revisor de risco."
            )
        ]

        confidence = 0.95

    elif not reviewed_report.get(
        "possui_diagnostico"
    ):
        summary = (
            "Ainda não existem diagnósticos "
            "financeiros salvos para compor "
            "o relatório."
        )

        recommendations = [
            (
                "Realize primeiro um diagnóstico "
                "financeiro."
            )
        ]

        next_steps = [
            (
                "Depois do diagnóstico, solicite "
                "novamente o relatório."
            )
        ]

        confidence = 0.90

    else:
        summary = (
            "O relatório foi preparado, mas a "
            "revisão de risco encontrou controles "
            "que impedem sua liberação para PDF."
        )

        recommendations = [
            (
                "Revise os achados registrados "
                "antes de gerar o documento."
            )
        ]

        next_steps = [
            (
                "Corrigir os controles bloqueadores "
                "e executar uma nova revisão."
            )
        ]

        confidence = 0.85

    response = AgentResponse(
        agent="report_agent",
        intent="relatorio",
        summary=summary,
        recommendations=recommendations,
        next_steps=next_steps,
        sources=[],
        confidence=confidence,
    )

    structured_response[
        "agent_response"
    ] = response.model_dump()

    return {
        **state,
        "response": response.summary,
        "conversation_history": [
            {
                "role": "assistant",
                "content": response.summary,
            }
        ],
        "structured_response": (
            structured_response
        ),
        "tool_results": tool_results,
        "errors": list(
            state.get("errors", [])
            or []
        ),
        "trace": trace + [
            "agent:report_agent",
        ],
    }


__all__ = [
    "DEFAULT_REPORT_HISTORY_LIMIT",
    "MAX_REPORT_HISTORY_LIMIT",
    "executar_fluxo_relatorio",
]

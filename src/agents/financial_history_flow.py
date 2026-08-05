"""
Orquestração determinística do histórico financeiro.

A identidade é retirada exclusivamente do estado confiável
e enviada pelo ToolExecutionContext. O modelo ou a mensagem
do usuário nunca controlam usuario_id.
"""

from __future__ import annotations

from datetime import datetime
import re
import unicodedata
from typing import Any

from src.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolStatus,
)
from src.agent_tools.financial_history_tools import (
    FINANCIAL_HISTORY_TOOL_NAME,
)
from src.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.agents.schemas import (
    AgentResponse,
)
from src.agents.state import (
    InnaAgentState,
)


DEFAULT_AGENT_HISTORY_LIMIT = 5
MAX_AGENT_HISTORY_LIMIT = 20


_HISTORY_LIMIT_PATTERNS = (
    re.compile(
        r"\bultim(?:o|os|a|as)\s+"
        r"(\d{1,2})\b"
    ),
    re.compile(
        r"\b(\d{1,2})\s+"
        r"ultim(?:o|os|a|as)\b"
    ),
    re.compile(
        r"\b(\d{1,2})\s+"
        r"(?:diagnostico|diagnosticos|"
        r"registro|registros)\b"
    ),
)


def _normalizar_texto(
    value: Any,
) -> str:
    text = str(value or "").strip().lower()

    decomposed = unicodedata.normalize(
        "NFKD",
        text,
    )

    return "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )


def _texto_opcional(
    value: Any,
) -> str | None:
    normalized = str(value or "").strip()

    return normalized or None


def resolver_limite_historico(
    mensagem: Any,
) -> int:
    """
    Extrai somente quantidades ligadas explicitamente
    a últimos diagnósticos ou registros.
    """
    text = _normalizar_texto(mensagem)

    for pattern in _HISTORY_LIMIT_PATTERNS:
        match = pattern.search(text)

        if not match:
            continue

        parsed = int(match.group(1))

        if parsed < 1:
            return DEFAULT_AGENT_HISTORY_LIMIT

        return min(
            parsed,
            MAX_AGENT_HISTORY_LIMIT,
        )

    return DEFAULT_AGENT_HISTORY_LIMIT


def _compactar_resultado(
    tool_result,
) -> dict[str, Any]:
    result = {
        "call_id": tool_result.call_id,
        "tool": tool_result.tool_name,
        "status": (tool_result.status.value),
        "ok": tool_result.ok,
        "duration_ms": (tool_result.duration_ms),
    }

    if tool_result.error is not None:
        result.update(
            {
                "error_code": (tool_result.error.code),
                "retryable": (tool_result.error.retryable),
            }
        )

    return result


def _formatar_data(
    value: Any,
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        return "data não informada"

    try:
        parsed = datetime.fromisoformat(
            normalized.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError:
        return normalized[:10]

    return parsed.strftime("%d/%m/%Y")


def _criar_resumo_historico(
    output: dict[str, Any],
) -> tuple[str, list[str]]:
    diagnosticos = list(
        output.get(
            "diagnosticos",
            [],
        )
        or []
    )

    total = int(
        output.get(
            "total_retornado",
            len(diagnosticos),
        )
        or 0
    )

    if not diagnosticos:
        return (
            ("Não encontrei diagnósticos financeiros vinculados à sua conta."),
            [("Gere um diagnóstico financeiro para iniciar seu histórico.")],
        )

    latest = dict(diagnosticos[0])

    detalhes = []

    score = latest.get("score_financeiro")

    if score is not None:
        detalhes.append(f"score de {int(score)}/100")

    risco = str(
        latest.get(
            "nivel_risco",
            "",
        )
        or ""
    ).strip()

    if risco:
        detalhes.append(f"risco {risco}")

    saldo = latest.get("saldo_estimado")

    moeda = str(
        latest.get(
            "moeda",
            "BRL",
        )
        or "BRL"
    )

    if saldo is not None:
        detalhes.append((f"saldo estimado de {moeda} {float(saldo):.2f}"))

    comprometimento = latest.get("comprometimento_renda_percentual")

    if comprometimento is not None:
        detalhes.append((f"comprometimento da renda de {float(comprometimento):.2f}%"))

    data = _formatar_data(latest.get("data_hora"))

    label = "diagnóstico" if total == 1 else "diagnósticos"

    summary = f"Encontrei {total} {label}. No registro mais recente, de {data}"

    if detalhes:
        summary += ", constam " + ", ".join(detalhes)

    summary += "."

    if total > 1:
        recommendations = [
            ("Compare os registros para observar a evolução do score, saldo e risco.")
        ]
    else:
        recommendations = [
            ("Novos diagnósticos permitirão acompanhar sua evolução ao longo do tempo.")
        ]

    return (
        summary,
        recommendations,
    )


def executar_fluxo_historico_financeiro(
    state: InnaAgentState,
) -> InnaAgentState:
    trace = list(state.get("trace", []))

    errors = list(state.get("errors", []))

    tool_results = list(
        state.get(
            "tool_results",
            [],
        )
    )

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    limite = resolver_limite_historico(
        state.get(
            "user_message",
            "",
        )
    )

    trusted_user_id = _texto_opcional(state.get("user_id") or state.get("usuario_id"))

    structured_response["financial_history_request"] = {
        "limit": limite,
        "identity_available": bool(trusted_user_id),
        "identity_source": ("tool_execution_context"),
    }

    trace.append("financial_route:history")

    # Defesa em profundidade. A ferramenta também
    # valida a identidade novamente.
    if not trusted_user_id:
        internal_error = "trusted_user_identity_missing"

        errors.append(internal_error)

        summary = (
            "Não foi possível consultar seu "
            "histórico porque a sessão não possui "
            "uma identidade de usuário validada."
        )

        response = AgentResponse(
            agent="financial_agent",
            intent="historico_financeiro",
            summary=summary,
            recommendations=[("Entre novamente pela sessão autenticada da aplicação.")],
            next_steps=[],
            sources=[],
            confidence=0.98,
        )

        structured_response["agent_response"] = response.model_dump()

        return {
            **state,
            "response": summary,
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": summary,
                }
            ],
            "structured_response": (structured_response),
            "tool_results": tool_results,
            "errors": errors,
            "trace": trace
            + [
                ("financial_history:missing_user_identity"),
                "agent:financial_agent:error",
            ],
        }

    tool_call = ToolCall(
        tool_name=(FINANCIAL_HISTORY_TOOL_NAME),
        arguments={
            "limite": limite,
        },
        context=ToolExecutionContext(
            requested_by="financial_agent",
            user_id=trusted_user_id,
            session_id=_texto_opcional(
                state.get("thread_id") or state.get("session_id")
            ),
            trace_id=_texto_opcional(state.get("trace_id")),
            metadata={
                "intent": ("historico_financeiro"),
                "route_source": str(
                    state.get(
                        "route_source",
                        "",
                    )
                )[:100],
            },
        ),
    )

    trace.append((f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:start"))

    tool_result = executar_ferramenta_inna(tool_call)

    compact_result = _compactar_resultado(tool_result)

    tool_results.append(compact_result)

    structured_response["financial_history_execution"] = dict(compact_result)

    if tool_result.status != ToolStatus.SUCCESS or tool_result.output is None:
        safe_error = (
            tool_result.error.message
            if tool_result.error
            else ("A consulta de histórico não retornou um resultado utilizável.")
        )

        errors.append(safe_error)

        summary = "Não foi possível consultar seu histórico financeiro neste momento."

        response = AgentResponse(
            agent="financial_agent",
            intent="historico_financeiro",
            summary=summary,
            recommendations=[("Tente novamente em alguns instantes.")],
            next_steps=[],
            sources=[],
            confidence=0.30,
        )

        structured_response["agent_response"] = response.model_dump()

        trace.append((f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:{tool_result.status.value}"))

        return {
            **state,
            "response": summary,
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": summary,
                }
            ],
            "structured_response": (structured_response),
            "tool_results": tool_results,
            "errors": errors,
            "trace": trace + ["agent:financial_agent:error"],
        }

    output = dict(tool_result.output)

    summary, recommendations = _criar_resumo_historico(output)

    structured_response["historico_financeiro"] = output

    response = AgentResponse(
        agent="financial_agent",
        intent="historico_financeiro",
        summary=summary,
        recommendations=recommendations,
        next_steps=[],
        sources=[],
        confidence=float(state.get("confidence") or 0.96),
    )

    structured_response["agent_response"] = response.model_dump()

    trace.append((f"tool:{FINANCIAL_HISTORY_TOOL_NAME}:success"))

    return {
        **state,
        "response": summary,
        "conversation_history": [
            {
                "role": "assistant",
                "content": summary,
            }
        ],
        "structured_response": (structured_response),
        "tool_results": tool_results,
        "errors": errors,
        "trace": trace + ["agent:financial_agent"],
    }


__all__ = [
    "DEFAULT_AGENT_HISTORY_LIMIT",
    "MAX_AGENT_HISTORY_LIMIT",
    "executar_fluxo_historico_financeiro",
    "resolver_limite_historico",
]

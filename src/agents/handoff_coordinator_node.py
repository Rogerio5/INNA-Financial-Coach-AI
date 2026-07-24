"""
Coordenador formal de handoffs da INNA.

Responsável por criar, aceitar, concluir ou falhar
transferências explícitas de responsabilidade entre agentes.
"""

from __future__ import annotations

from typing import Any

from src.agents.handoff import (
    accept_handoff,
    complete_handoff,
    create_handoff,
    fail_handoff,
)
from src.agents.state import InnaAgentState


SPECIALIZED_AGENTS = {
    "financial_agent",
    "education_agent",
    "rag_agent",
    "report_agent",
    "fallback_agent",
}


def _normalize_text(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip()


def _resolve_current_agent(
    state: InnaAgentState,
) -> str:
    """
    Resolve o agente que executou a etapa atual.
    """
    explicit = _normalize_text(
        state.get(
            "current_agent",
            "",
        )
    )

    if explicit in SPECIALIZED_AGENTS:
        return explicit

    next_node = _normalize_text(
        state.get(
            "next_node",
            "",
        )
    )

    if next_node in SPECIALIZED_AGENTS:
        return next_node

    trace = state.get(
        "trace",
        [],
    )

    for item in reversed(
        list(trace or [])
    ):
        normalized = _normalize_text(
            item
        )

        if not normalized.startswith(
            "agent:"
        ):
            continue

        candidate = normalized.split(
            ":",
            1,
        )[1].strip()

        if candidate in SPECIALIZED_AGENTS:
            return candidate

    return ""


def _append_trace(
    state: InnaAgentState,
    event: str,
) -> list[str]:
    trace = list(
        state.get(
            "trace",
            [],
        )
    )

    trace.append(event)

    return trace


def _append_error(
    state: InnaAgentState,
    error: str,
) -> list[str]:
    errors = [
        _normalize_text(item)
        for item in state.get(
            "errors",
            [],
        )
        if _normalize_text(item)
    ]

    errors.append(error)

    return errors


def _handoff_payload(
    state: InnaAgentState,
) -> dict[str, Any]:
    """
    Produz um payload mínimo e rastreável.

    Evita copiar todo o estado para o handoff.
    """
    return {
        "intent": state.get(
            "intent"
        ),
        "task_status": state.get(
            "task_status"
        ),
        "task_completion_score": state.get(
            "task_completion_score"
        ),
        "completed_requirements": list(
            state.get(
                "completed_requirements",
                [],
            )
        ),
        "missing_requirements": list(
            state.get(
                "missing_requirements",
                [],
            )
        ),
        "response": _normalize_text(
            state.get(
                "response",
                "",
            )
        ),
    }


def _handoff_metadata(
    state: InnaAgentState,
) -> dict[str, Any]:
    return {
        "thread_id": state.get(
            "thread_id"
        ),
        "route_source": state.get(
            "route_source"
        ),
        "routing_reason": state.get(
            "routing_reason"
        ),
    }


def _max_handoffs(
    state: InnaAgentState,
) -> int:
    try:
        value = int(
            state.get(
                "max_handoffs",
                3,
            )
            or 3
        )
    except (
        TypeError,
        ValueError,
    ):
        return 3

    return max(
        1,
        value,
    )


def _has_reverse_handoff_cycle(
    state: InnaAgentState,
    *,
    from_agent: str,
    to_agent: str,
) -> bool:
    history = state.get(
        "handoff_history",
        [],
    )

    if not isinstance(
        history,
        list,
    ):
        return False

    for handoff in history:
        if not isinstance(
            handoff,
            dict,
        ):
            continue

        previous_from = _normalize_text(
            handoff.get(
                "from_agent",
                "",
            )
        )

        previous_to = _normalize_text(
            handoff.get(
                "to_agent",
                "",
            )
        )

        if (
            previous_from == to_agent
            and previous_to == from_agent
        ):
            return True

    return False


def _request_handoff(
    state: InnaAgentState,
    *,
    current_agent: str,
) -> dict[str, Any]:
    target = _normalize_text(
        state.get(
            "handoff_target",
            "",
        )
    )

    reason = _normalize_text(
        state.get(
            "handoff_reason",
            "",
        )
    )

    if not current_agent:
        error = (
            "Não foi possível identificar o "
            "agente de origem do handoff."
        )

        return {
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:source_unresolved",
            ),
        }

    if target not in SPECIALIZED_AGENTS:
        error = (
            "O agente de destino do handoff "
            "é inválido ou não foi informado."
        )

        return {
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:invalid_target",
            ),
        }

    if target == current_agent:
        error = (
            "O agente de origem e o agente "
            "de destino do handoff são iguais."
        )

        return {
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:self_handoff",
            ),
        }

    if not reason:
        error = (
            "O motivo do handoff não foi informado."
        )

        return {
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:missing_reason",
            ),
        }

    handoff_count = int(
        state.get(
            "handoff_count",
            0,
        )
        or 0
    )

    max_handoffs = _max_handoffs(
        state
    )

    if handoff_count >= max_handoffs:
        error = (
            "O limite máximo de handoffs "
            "da execução foi atingido."
        )

        return {
            "handoff_required": False,
            "handoff_limit_exceeded": True,
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:limit_exceeded",
            ),
        }

    if _has_reverse_handoff_cycle(
        state,
        from_agent=current_agent,
        to_agent=target,
    ):
        error = (
            "O handoff foi bloqueado porque "
            "criaria um ciclo entre agentes."
        )

        return {
            "handoff_required": False,
            "errors": _append_error(
                state,
                error,
            ),
            "trace": _append_trace(
                state,
                "handoff:error:reverse_cycle",
            ),
        }

    handoff = create_handoff(
        from_agent=current_agent,
        to_agent=target,
        reason=reason,
        payload=_handoff_payload(
            state
        ),
        metadata=_handoff_metadata(
            state
        ),
    )

    handoff_count += 1

    return {
        "handoff_current": handoff,
        "handoff_history": [
            handoff,
        ],
        "handoff_count": handoff_count,
        "handoff_required": False,
        "trace": _append_trace(
            state,
            (
                "handoff:requested:"
                f"{current_agent}->{target}:"
                f"{handoff['handoff_id']}"
            ),
        ),
    }


def _accept_requested_handoff(
    state: InnaAgentState,
    *,
    handoff: dict[str, Any],
    current_agent: str,
) -> dict[str, Any]:
    """
    Aceita o handoff quando o destino assume a execução.

    Se o Task Completion já confirmou conclusão ou falha,
    a transição terminal ocorre na mesma passagem.
    """
    target = _normalize_text(
        handoff.get(
            "to_agent",
            "",
        )
    )

    if current_agent != target:
        return {}

    accepted = accept_handoff(
        handoff,
    )

    errors = [
        _normalize_text(item)
        for item in state.get(
            "errors",
            [],
        )
        if _normalize_text(item)
    ]

    if errors:
        failed = fail_handoff(
            accepted,
            error=errors[-1],
        )

        return {
            "handoff_current": failed,
            "handoff_history": [
                failed,
            ],
            "handoff_target": "",
            "handoff_reason": "",
            "trace": _append_trace(
                state,
                (
                    "handoff:accepted:"
                    f"{accepted['handoff_id']}"
                    "|handoff:failed:"
                    f"{failed['handoff_id']}"
                ),
            ),
        }

    task_status = _normalize_text(
        state.get(
            "task_status",
            "",
        )
    )

    if task_status == "completed":
        completed = complete_handoff(
            accepted,
            result={
                "task_status": task_status,
                "task_completion_score": state.get(
                    "task_completion_score"
                ),
                "response_generated": bool(
                    _normalize_text(
                        state.get(
                            "response",
                            "",
                        )
                    )
                ),
            },
        )

        return {
            "handoff_current": completed,
            "handoff_history": [
                completed,
            ],
            "handoff_target": "",
            "handoff_reason": "",
            "trace": _append_trace(
                state,
                (
                    "handoff:accepted:"
                    f"{accepted['handoff_id']}"
                    "|handoff:completed:"
                    f"{completed['handoff_id']}"
                ),
            ),
        }

    return {
        "handoff_current": accepted,
        "handoff_history": [
            accepted,
        ],
        "trace": _append_trace(
            state,
            (
                "handoff:accepted:"
                f"{accepted['from_agent']}"
                "->"
                f"{accepted['to_agent']}:"
                f"{accepted['handoff_id']}"
            ),
        ),
    }



def _finalize_accepted_handoff(
    state: InnaAgentState,
    *,
    handoff: dict[str, Any],
    current_agent: str,
) -> dict[str, Any]:
    target = _normalize_text(
        handoff.get(
            "to_agent",
            "",
        )
    )

    if current_agent != target:
        return {}

    errors = [
        _normalize_text(item)
        for item in state.get(
            "errors",
            [],
        )
        if _normalize_text(item)
    ]

    if errors:
        failed = fail_handoff(
            handoff,
            error=errors[-1],
        )

        return {
            "handoff_current": failed,
            "handoff_history": [
                failed,
            ],
            "trace": _append_trace(
                state,
                (
                    "handoff:failed:"
                    f"{failed['handoff_id']}"
                ),
            ),
        }

    task_status = _normalize_text(
        state.get(
            "task_status",
            "",
        )
    )

    if task_status != "completed":
        return {}

    completed = complete_handoff(
        handoff,
        result={
            "task_status": task_status,
            "task_completion_score": state.get(
                "task_completion_score"
            ),
            "response_generated": bool(
                _normalize_text(
                    state.get(
                        "response",
                        "",
                    )
                )
            ),
        },
    )

    return {
        "handoff_current": completed,
        "handoff_history": [
            completed,
        ],
        "handoff_target": "",
        "handoff_reason": "",
        "trace": _append_trace(
            state,
            (
                "handoff:completed:"
                f"{completed['handoff_id']}"
            ),
        ),
    }


def handoff_coordinator_node(
    state: InnaAgentState,
) -> dict[str, Any]:
    """
    Processa uma etapa da máquina de estados do handoff.

    Regras:
    1. cria o handoff quando handoff_required=True;
    2. aceita quando o agente de destino assume a tarefa;
    3. conclui quando a tarefa do destino está completed;
    4. falha quando o destino registra erros.
    """
    current_agent = (
        _resolve_current_agent(
            state
        )
    )

    current_handoff = state.get(
        "handoff_current"
    )

    if isinstance(
        current_handoff,
        dict,
    ):
        status = _normalize_text(
            current_handoff.get(
                "status",
                "",
            )
        )

        if status == "requested":
            return _accept_requested_handoff(
                state,
                handoff=current_handoff,
                current_agent=current_agent,
            )

        if status == "accepted":
            return _finalize_accepted_handoff(
                state,
                handoff=current_handoff,
                current_agent=current_agent,
            )

        return {}

    if not bool(
        state.get(
            "handoff_required",
            False,
        )
    ):
        return {}

    return _request_handoff(
        state,
        current_agent=current_agent,
    )


__all__ = [
    "handoff_coordinator_node",
]

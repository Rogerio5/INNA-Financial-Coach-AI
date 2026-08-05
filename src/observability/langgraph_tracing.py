"""Tracing seguro das execuções LangGraph da INNA."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from .phoenix_privacy import hash_identifier
from .phoenix_runtime import traced_operation


def _hash_optional(value: object | None) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    if not normalized:
        return None

    return hash_identifier(normalized)


def build_langgraph_attributes(
    *,
    execution_mode: str,
    thread_id: str | None = None,
    user_id: str | None = None,
    language: str | None = None,
    currency: str | None = None,
    human_review_enabled: bool | None = None,
) -> dict[str, Any]:
    """
    Monta apenas metadados técnicos seguros.

    Mensagem, histórico, resposta, contexto financeiro e decisão
    humana nunca são incluídos.
    """

    attributes: dict[str, Any] = {
        "agent.framework": "langgraph",
        "agent.application": "inna",
        "agent.execution_mode": execution_mode,
        "privacy.content_exported": False,
    }

    thread_hash = _hash_optional(thread_id)
    user_hash = _hash_optional(user_id)

    if thread_hash:
        attributes["inna.thread_id_hash"] = thread_hash

    if user_hash:
        attributes["enduser.id_hash"] = user_hash

    if language:
        attributes["inna.language"] = str(language)

    if currency:
        attributes["inna.currency"] = str(currency)

    if human_review_enabled is not None:
        attributes["inna.human_review_enabled"] = bool(human_review_enabled)

    return attributes


def add_langgraph_result_attributes(
    span: Any,
    result: Mapping[str, Any] | None,
) -> None:
    """Adiciona ao span somente resultados operacionais seguros."""

    if not isinstance(result, Mapping):
        span.set_attribute("agent.result_available", False)
        return

    span.set_attribute("agent.result_available", True)

    safe_fields = {
        "agent.execution_steps": result.get(
            "execution_steps",
            0,
        ),
        "agent.handoff_count": result.get(
            "handoff_count",
            0,
        ),
        "agent.human_review_count": result.get(
            "human_review_count",
            0,
        ),
        "agent.loop_detected": bool(result.get("loop_detected", False)),
        "agent.execution_budget_exceeded": bool(
            result.get(
                "execution_budget_exceeded",
                False,
            )
        ),
        "agent.handoff_limit_exceeded": bool(
            result.get(
                "handoff_limit_exceeded",
                False,
            )
        ),
        "agent.human_review_required": bool(
            result.get(
                "human_review_required",
                False,
            )
        ),
    }

    route = str(
        result.get("next_node")
        or result.get("current_agent")
        or result.get("team_route")
        or ""
    ).strip()

    team = str(
        result.get("current_team") or result.get("team_supervisor") or ""
    ).strip()

    if route:
        safe_fields["agent.final_route"] = route

    if team:
        safe_fields["agent.final_team"] = team

    errors = result.get("errors")

    if isinstance(errors, list):
        safe_fields["agent.error_count"] = len(errors)

    route_history = result.get("route_history")

    if isinstance(route_history, list):
        safe_fields["agent.route_count"] = len(route_history)

    tool_results = result.get("tool_results")

    if isinstance(tool_results, list):
        safe_fields["agent.tool_result_count"] = len(tool_results)

    for name, value in safe_fields.items():
        if isinstance(value, (bool, int, float, str)):
            span.set_attribute(name, value)


@contextmanager
def traced_langgraph_execution(
    *,
    execution_mode: str,
    thread_id: str | None = None,
    user_id: str | None = None,
    language: str | None = None,
    currency: str | None = None,
    human_review_enabled: bool | None = None,
) -> Iterator[Any]:
    """Cria o trace raiz de uma execução agentic da INNA."""

    attributes = build_langgraph_attributes(
        execution_mode=execution_mode,
        thread_id=thread_id,
        user_id=user_id,
        language=language,
        currency=currency,
        human_review_enabled=human_review_enabled,
    )

    with traced_operation(
        "inna.langgraph.execution",
        attributes=attributes,
        instrumentation_name="inna.agents.langgraph",
    ) as span:
        yield span


__all__ = [
    "add_langgraph_result_attributes",
    "build_langgraph_attributes",
    "traced_langgraph_execution",
]

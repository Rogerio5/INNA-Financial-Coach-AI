"""
Estado compartilhado do núcleo de agentes da INNA.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict


IntentType = Literal[
    "diagnostico_financeiro",
    "educacao_financeira",
    "consulta_rag",
    "relatorio",
    "desconhecido",
]


class InnaAgentState(TypedDict, total=False):
    """
    Estado que percorre o grafo da INNA.

    Nenhum dado sensível deve ser registrado neste estado
    sem necessidade explícita.
    """

    user_message: str
    user_id: str | None
    language: str
    currency: str

    intent: IntentType
    confidence: float
    next_node: str

    use_rag: bool
    use_database: bool
    generate_report: bool

    context: dict[str, Any]
    tool_results: list[dict[str, Any]]

    response: str
    structured_response: dict[str, Any]

    errors: list[str]
    trace: list[str]


__all__ = [
    "IntentType",
    "InnaAgentState",
]

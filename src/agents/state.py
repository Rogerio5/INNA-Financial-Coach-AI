"""
Estado compartilhado do núcleo de agentes da INNA.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict


def merge_conversation_history(
    current: list[dict[str, str]] | None,
    update: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    """
    Combina o histórico de conversa sem duplicações.

    Compatível tanto com atualizações incrementais quanto
    com nós que retornam o estado completo.
    """
    current = list(current or [])
    update = list(update or [])

    if not update:
        return current

    if not current:
        return update

    # O nó pode devolver o histórico completo mais a nova mensagem.
    if (
        len(update) >= len(current)
        and update[: len(current)] == current
    ):
        return update

    resultado = list(current)

    for mensagem in update:
        if not isinstance(mensagem, dict):
            continue

        role = str(
            mensagem.get("role", "")
        ).strip()

        texto = str(
            mensagem.get("content", "")
        ).strip()

        if not role or not texto:
            continue

        normalizada = {
            "role": role,
            "content": texto,
        }

        # Evita apenas duplicação consecutiva.
        # A mesma pergunta pode aparecer novamente mais tarde.
        if resultado and resultado[-1] == normalizada:
            continue

        resultado.append(normalizada)

    return resultado


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

    thread_id: str
    conversation_history: Annotated[
        list[dict[str, str]],
        merge_conversation_history,
    ]
    conversation_summary: str

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
    "merge_conversation_history",
]

"""
Catálogo das ferramentas autorizadas da INNA.

O catálogo cria um novo ToolRegistry para cada runtime
ou teste, evitando compartilhamento acidental de estado.
"""

from __future__ import annotations

import os

from src.agent_tools.core import (
    ToolRegistry,
)
from src.agent_tools.rag_tools import (
    criar_definicao_buscar_conhecimento_rag,
)


DEFAULT_RAG_TOOL_TIMEOUT_SECONDS = 20.0


def _positive_float_environment(
    name: str,
    default: float,
) -> float:
    raw_value = str(
        os.getenv(name, "")
    ).strip()

    if not raw_value:
        return default

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return default

    if value <= 0:
        return default

    return value


def criar_registro_ferramentas_inna(
) -> ToolRegistry:
    """
    Monta o catálogo completo de ferramentas.

    Novas ferramentas financeiras e de relatório
    serão registradas aqui nas próximas etapas.
    """
    registry = ToolRegistry()

    rag_timeout = _positive_float_environment(
        "INNA_RAG_TOOL_TIMEOUT_SECONDS",
        DEFAULT_RAG_TOOL_TIMEOUT_SECONDS,
    )

    registry.register(
        criar_definicao_buscar_conhecimento_rag(
            timeout_seconds=rag_timeout,
        )
    )

    return registry


def obter_catalogo_schemas_ferramentas(
) -> list[dict]:
    """
    Retorna schemas apropriados para integração
    futura com Gemini Function Calling.
    """
    return (
        criar_registro_ferramentas_inna()
        .schema_catalog()
    )


__all__ = [
    "DEFAULT_RAG_TOOL_TIMEOUT_SECONDS",
    "criar_registro_ferramentas_inna",
    "obter_catalogo_schemas_ferramentas",
]

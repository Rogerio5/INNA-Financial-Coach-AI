"""
Agente financeiro principal da INNA.

Este modulo representa o ponto oficial de entrada do dominio
financeiro na arquitetura modular.

Durante a migracao gradual, a implementacao interna permanece
temporariamente em src.agents.nodes para preservar compatibilidade
com testes, monkeypatches e integracoes existentes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agents.state import InnaAgentState


def financial_agent_node(
    state: "InnaAgentState",
) -> "InnaAgentState":
    """
    Executa o agente financeiro principal da INNA.
    """

    # Import tardio proposital:
    # preserva a implementacao e os patches existentes durante
    # a migracao modular.
    from src.agents.nodes import (
        financial_agent_node as _legacy_financial_agent_node,
    )

    return _legacy_financial_agent_node(state)


__all__ = [
    "financial_agent_node",
]

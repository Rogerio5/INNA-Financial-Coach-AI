"""
Grafo principal do núcleo de agentes da INNA.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents.nodes import (
    education_agent_node,
    fallback_agent_node,
    financial_agent_node,
    rag_agent_node,
    report_agent_node,
)
from src.agents.state import InnaAgentState
from src.agents.supervisor import supervisor_node


def _selecionar_rota(
    state: InnaAgentState,
) -> str:
    return state.get(
        "next_node",
        "fallback_agent",
    )


def criar_grafo_inna():
    builder = StateGraph(InnaAgentState)

    builder.add_node(
        "supervisor",
        supervisor_node,
    )

    builder.add_node(
        "financial_agent",
        financial_agent_node,
    )

    builder.add_node(
        "education_agent",
        education_agent_node,
    )

    builder.add_node(
        "rag_agent",
        rag_agent_node,
    )

    builder.add_node(
        "report_agent",
        report_agent_node,
    )

    builder.add_node(
        "fallback_agent",
        fallback_agent_node,
    )

    builder.add_edge(
        START,
        "supervisor",
    )

    builder.add_conditional_edges(
        "supervisor",
        _selecionar_rota,
        {
            "financial_agent": (
                "financial_agent"
            ),
            "education_agent": (
                "education_agent"
            ),
            "rag_agent": "rag_agent",
            "report_agent": "report_agent",
            "fallback_agent": (
                "fallback_agent"
            ),
        },
    )

    for node in [
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    ]:
        builder.add_edge(node, END)

    return builder.compile()


inna_agent_graph = criar_grafo_inna()


def executar_nucleo_inna(
    mensagem: str,
    *,
    usuario_id: str | None = None,
    idioma: str = "pt",
    moeda: str = "BRL",
) -> InnaAgentState:
    estado_inicial: InnaAgentState = {
        "user_message": mensagem,
        "user_id": usuario_id,
        "language": idioma,
        "currency": moeda,
        "context": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
    }

    return inna_agent_graph.invoke(
        estado_inicial
    )


__all__ = [
    "criar_grafo_inna",
    "inna_agent_graph",
    "executar_nucleo_inna",
]

"""
Grafo principal do núcleo de agentes da INNA.

Suporta:
- execução sem persistência para testes;
- memória persistente PostgreSQL por thread_id;
- histórico acumulado de conversas.
"""

from __future__ import annotations

import uuid
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.agents.nodes import (
    education_agent_node,
    fallback_agent_node,
    financial_agent_node,
    rag_agent_node,
    report_agent_node,
)
from src.agents.persistence import (
    abrir_checkpointer_postgres,
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


def criar_builder_inna() -> StateGraph:
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
            "financial_agent": "financial_agent",
            "education_agent": "education_agent",
            "rag_agent": "rag_agent",
            "report_agent": "report_agent",
            "fallback_agent": "fallback_agent",
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

    return builder


def criar_grafo_inna(
    *,
    checkpointer: Any | None = None,
):
    return criar_builder_inna().compile(
        checkpointer=checkpointer
    )


inna_agent_graph = criar_grafo_inna()


def _criar_estado_inicial(
    mensagem: str,
    *,
    thread_id: str,
    usuario_id: str | None,
    idioma: str,
    moeda: str,
) -> InnaAgentState:
    mensagem = str(mensagem or "").strip()

    return {
        "user_message": mensagem,
        "user_id": usuario_id,
        "language": idioma,
        "currency": moeda,
        "thread_id": thread_id,
        "conversation_history": [
            {
                "role": "user",
                "content": mensagem,
            }
        ],
        "context": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
    }


def executar_nucleo_inna(
    mensagem: str,
    *,
    usuario_id: str | None = None,
    idioma: str = "pt",
    moeda: str = "BRL",
) -> InnaAgentState:
    """
    Execução sem persistência.

    Mantida para compatibilidade e testes unitários.
    """
    thread_id = str(uuid.uuid4())

    estado_inicial = _criar_estado_inicial(
        mensagem,
        thread_id=thread_id,
        usuario_id=usuario_id,
        idioma=idioma,
        moeda=moeda,
    )

    return inna_agent_graph.invoke(
        estado_inicial
    )


def executar_nucleo_inna_persistente(
    mensagem: str,
    *,
    thread_id: str,
    usuario_id: str | None = None,
    idioma: str = "pt",
    moeda: str = "BRL",
) -> InnaAgentState:
    """
    Executa o grafo com memória PostgreSQL.

    O mesmo thread_id continua a mesma conversa.
    """
    thread_id = str(thread_id or "").strip()

    if not thread_id:
        raise ValueError(
            "thread_id é obrigatório para "
            "execução persistente."
        )

    if len(thread_id) > 255:
        raise ValueError(
            "thread_id deve possuir no máximo "
            "255 caracteres."
        )

    estado_inicial = _criar_estado_inicial(
        mensagem,
        thread_id=thread_id,
        usuario_id=usuario_id,
        idioma=idioma,
        moeda=moeda,
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    with abrir_checkpointer_postgres() as checkpointer:
        grafo = criar_grafo_inna(
            checkpointer=checkpointer
        )

        return grafo.invoke(
            estado_inicial,
            config=config,
        )


def consultar_estado_conversa(
    *,
    thread_id: str,
) -> dict[str, Any]:
    """
    Retorna o checkpoint atual de uma conversa.
    """
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    with abrir_checkpointer_postgres() as checkpointer:
        grafo = criar_grafo_inna(
            checkpointer=checkpointer
        )

        snapshot = grafo.get_state(config)

        return {
            "thread_id": thread_id,
            "values": dict(snapshot.values or {}),
            "next": list(snapshot.next or []),
            "created_at": (
                snapshot.created_at
            ),
            "metadata": dict(
                snapshot.metadata or {}
            ),
        }


__all__ = [
    "criar_builder_inna",
    "criar_grafo_inna",
    "inna_agent_graph",
    "executar_nucleo_inna",
    "executar_nucleo_inna_persistente",
    "consultar_estado_conversa",
]

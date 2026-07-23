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

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

from src.agents.conversation_summary_node import (
    conversation_summary_node,
)
from src.agents.task_completion_node import (
    task_completion_node,
)
from src.agents.handoff_coordinator_node import (
    handoff_coordinator_node,
)
from src.agents.execution_governance import (
    DEFAULT_MAX_EXECUTION_STEPS,
    DEFAULT_MAX_SAME_AGENT_VISITS,
    apply_execution_governance,
)
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
from src.context_engineering.node import (
    context_builder_node,
)


DEFAULT_LANGGRAPH_RECURSION_LIMIT = 25

ALLOWED_AGENT_ROUTES = frozenset(
    {
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    }
)


class LangGraphExecutionLimitError(
    RuntimeError
):
    """
    Indica que a execução do grafo excedeu
    o limite operacional permitido.
    """


def _criar_config_execucao(
    *,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """
    Cria a configuração central de execução.

    recursion_limit é uma chave de nível superior
    do RunnableConfig do LangGraph.
    """
    config: dict[str, Any] = {
        "recursion_limit": (
            DEFAULT_LANGGRAPH_RECURSION_LIMIT
        ),
    }

    normalized_thread_id = str(
        thread_id or ""
    ).strip()

    if normalized_thread_id:
        config["configurable"] = {
            "thread_id": normalized_thread_id,
        }

    return config


def _invocar_grafo_seguro(
    grafo: Any,
    estado_inicial: InnaAgentState,
    *,
    config: dict[str, Any],
) -> InnaAgentState:
    """
    Executa o grafo com limite explícito.

    Não cria resposta parcial silenciosa quando
    o limite é atingido.
    """
    try:
        return grafo.invoke(
            estado_inicial,
            config=config,
        )
    except GraphRecursionError as error:
        raise LangGraphExecutionLimitError(
            "A execução do núcleo agentic excedeu "
            "o limite máximo de passos permitido."
        ) from error


def _selecionar_rota(
    state: InnaAgentState,
) -> str:
    route = str(
        state.get(
            "next_node",
            "fallback_agent",
        )
        or "fallback_agent"
    ).strip()

    if route not in ALLOWED_AGENT_ROUTES:
        return "fallback_agent"

    return route


def _selecionar_rota_apos_handoff(
    state: InnaAgentState,
) -> str:
    """
    Decide se o fluxo deve executar o agente de destino
    ou seguir para o resumo final.
    """
    handoff = state.get(
        "handoff_current"
    )

    if not isinstance(
        handoff,
        dict,
    ):
        return "conversation_summary"

    status = str(
        handoff.get(
            "status",
            "",
        )
    ).strip()

    target = str(
        handoff.get(
            "to_agent",
            "",
        )
    ).strip()

    if (
        status == "requested"
        and target in ALLOWED_AGENT_ROUTES
    ):
        return target

    return "conversation_summary"


def criar_builder_inna() -> StateGraph:
    builder = StateGraph(InnaAgentState)

    builder.add_node(
        "context_builder",
        context_builder_node,
    )

    builder.add_node(
        "supervisor",
        supervisor_node,
    )

    builder.add_node(
        "execution_governance",
        apply_execution_governance,
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

    builder.add_node(
        "task_completion",
        task_completion_node,
    )

    builder.add_node(
        "handoff_coordinator",
        handoff_coordinator_node,
    )

    builder.add_node(
        "conversation_summary",
        conversation_summary_node,
    )

    builder.add_edge(
        START,
        "context_builder",
    )

    builder.add_edge(
        "context_builder",
        "supervisor",
    )

    builder.add_edge(
        "supervisor",
        "execution_governance",
    )

    builder.add_conditional_edges(
        "execution_governance",
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
        builder.add_edge(
            node,
            "task_completion",
        )

    builder.add_edge(
        "task_completion",
        "handoff_coordinator",
    )

    builder.add_conditional_edges(
        "handoff_coordinator",
        _selecionar_rota_apos_handoff,
        {
            "financial_agent": "financial_agent",
            "education_agent": "education_agent",
            "rag_agent": "rag_agent",
            "report_agent": "report_agent",
            "fallback_agent": "fallback_agent",
            (
                "conversation_summary"
            ): "conversation_summary",
        },
    )

    builder.add_edge(
        "conversation_summary",
        END,
    )

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
        "handoff_current": None,
        "handoff_history": [],
        "handoff_count": 0,
        "max_handoffs": 3,
        "handoff_limit_exceeded": False,
        "handoff_required": False,
        "handoff_target": "",
        "handoff_reason": "",
        "context": {},
        "tool_results": [],
        "errors": [],
        "route_history": [],
        "execution_steps": 0,
        "max_execution_steps": (
            DEFAULT_MAX_EXECUTION_STEPS
        ),
        "max_same_agent_visits": (
            DEFAULT_MAX_SAME_AGENT_VISITS
        ),
        "loop_detected": False,
        "execution_budget_exceeded": False,
        "governance_reason": "",
        "governance_decision": {},
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

    config = _criar_config_execucao()

    return _invocar_grafo_seguro(
        inna_agent_graph,
        estado_inicial,
        config=config,
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

    config = _criar_config_execucao(
        thread_id=thread_id,
    )

    with abrir_checkpointer_postgres() as checkpointer:
        grafo = criar_grafo_inna(
            checkpointer=checkpointer
        )

        return _invocar_grafo_seguro(
            grafo,
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
    "ALLOWED_AGENT_ROUTES",
    "DEFAULT_LANGGRAPH_RECURSION_LIMIT",
    "LangGraphExecutionLimitError",
    "criar_builder_inna",
    "criar_grafo_inna",
    "inna_agent_graph",
    "executar_nucleo_inna",
    "executar_nucleo_inna_persistente",
    "consultar_estado_conversa",
]

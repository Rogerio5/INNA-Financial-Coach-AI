from __future__ import annotations

from uuid import uuid4

import pytest
from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.types import (
    Command,
)

from src.agents.graph import (
    _criar_estado_inicial,
)
from src.agents.human_review_interrupt_node import (
    human_review_interrupt_node,
    select_route_after_human_review_interrupt,
)
from src.agents.human_review_policy_node import (
    human_review_policy_node,
    select_route_after_human_review_policy,
)
from src.agents.state import (
    InnaAgentState,
)


def _create_test_graph():
    """
    Cria um grafo mínimo usando os nós reais da INNA.

    O objetivo é validar somente:
    política → interrupt → checkpoint → resume.
    """
    builder = StateGraph(
        InnaAgentState
    )

    # Representa a saída do Task Completion no
    # grafo reduzido usado pelo teste.
    builder.add_node(
        "task_completion",
        lambda state: {},
    )

    builder.add_node(
        "human_review_policy",
        human_review_policy_node,
    )

    builder.add_node(
        "human_review_interrupt",
        human_review_interrupt_node,
    )

    # Permite também uma execução normal começando
    # diretamente pela política.
    builder.add_edge(
        START,
        "human_review_policy",
    )

    builder.add_conditional_edges(
        "human_review_policy",
        select_route_after_human_review_policy,
        {
            "human_review_interrupt": (
                "human_review_interrupt"
            ),
            "handoff_coordinator": END,
        },
    )

    builder.add_conditional_edges(
        "human_review_interrupt",
        select_route_after_human_review_interrupt,
        {
            "handoff_coordinator": END,
            "team_router": END,
            "conversation_summary": END,
        },
    )

    # Permite update_state(..., as_node="task_completion")
    # continuar pela política Human-in-the-Loop.
    builder.add_edge(
        "task_completion",
        "human_review_policy",
    )

    checkpointer = InMemorySaver()

    return builder.compile(
        checkpointer=checkpointer
    )



def _create_high_risk_state(
    *,
    thread_id: str,
) -> InnaAgentState:
    state = _criar_estado_inicial(
        (
            "Minha renda é 3000 e meus gastos "
            "mensais são 4500."
        ),
        thread_id=thread_id,
        usuario_id="user-memory-checkpoint",
        idioma="pt-BR",
        moeda="BRL",
    )

    state.update({
        "current_agent": "financial_agent",
        "task_status": "completed",
        "task_completion_score": 0.95,
        "confidence": 0.95,
        "human_review_enabled": True,
    })

    # structured_response pertence ao schema do estado
    # e é analisado pela política Human-in-the-Loop.
    structured = dict(
        state.get(
            "structured_response",
            {},
        )
        or {}
    )

    structured[
        "risk_level"
    ] = "high"

    state[
        "structured_response"
    ] = structured

    state[
        "human_review_enabled"
    ] = True

    return state

def _config(
    thread_id: str,
) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        },
    }


def _invoke_until_interrupt(
    graph,
    *,
    state: dict,
    config: dict,
) -> dict:
    """
    Registra o estado como saída de task_completion
    e continua a execução pelo checkpoint mais
    recente da mesma thread.

    O config retornado por update_state contém um
    checkpoint_id fixo. Para executar as tarefas
    pendentes, usamos o config original da thread.
    """
    graph.update_state(
        config,
        state,
        as_node="task_completion",
    )

    return graph.invoke(
        None,
        config=config,
    )




def _interrupt_payload(
    result: dict,
) -> dict:
    interrupts = result.get(
        "__interrupt__",
        (),
    )

    assert interrupts, (
        "O LangGraph não retornou uma interrupção."
    )

    first = interrupts[0]

    value = getattr(
        first,
        "value",
        None,
    )

    if value is None and isinstance(
        first,
        dict,
    ):
        value = first.get(
            "value"
        )

    assert isinstance(
        value,
        dict,
    )

    return value


def test_real_interrupt_is_saved_in_checkpoint():
    graph = _create_test_graph()

    thread_id = (
        "thread-memory-"
        + uuid4().hex
    )

    config = _config(
        thread_id
    )

    result = _invoke_until_interrupt(
        graph,
        state=_create_high_risk_state(
            thread_id=thread_id
        ),
        config=config,
    )

    payload = _interrupt_payload(
        result
    )

    assert payload[
        "type"
    ] == "human_review"

    assert payload[
        "thread_id"
    ] == thread_id

    assert payload[
        "trigger"
    ] == "high_financial_risk"

    assert payload[
        "risk_level"
    ] == "high"

    snapshot = graph.get_state(
        config
    )

    assert snapshot.next == (
        "human_review_interrupt",
    )

    assert snapshot.values[
        "human_review_required"
    ] is True

    assert snapshot.values[
        "human_review_status"
    ] == "requested"

    assert snapshot.values[
        "human_review_current"
    ]["thread_id"] == thread_id


def test_real_approve_resume_uses_same_checkpoint():
    graph = _create_test_graph()

    thread_id = (
        "thread-approve-"
        + uuid4().hex
    )

    config = _config(
        thread_id
    )

    interrupted = _invoke_until_interrupt(
        graph,
        state=_create_high_risk_state(
            thread_id=thread_id
        ),
        config=config,
    )

    _interrupt_payload(
        interrupted
    )

    resumed = graph.invoke(
        Command(
            resume={
                "action": "approve",
                "reviewer_id": (
                    "user-memory-checkpoint"
                ),
                "comment": (
                    "Dados financeiros confirmados."
                ),
            }
        ),
        config=config,
    )

    assert resumed[
        "human_review_required"
    ] is False

    assert resumed[
        "human_review_status"
    ] == "approved"

    assert resumed[
        "human_review_decision_action"
    ] == "approve"

    assert resumed[
        "human_review_resume_route"
    ] == "handoff_coordinator"

    assert resumed[
        "human_review_current"
    ]["decision"]["reviewer_id"] == (
        "user-memory-checkpoint"
    )

    snapshot = graph.get_state(
        config
    )

    assert snapshot.next == ()

    assert snapshot.values[
        "human_review_status"
    ] == "approved"


def test_real_correction_resume_preserves_corrections():
    graph = _create_test_graph()

    thread_id = (
        "thread-correction-"
        + uuid4().hex
    )

    config = _config(
        thread_id
    )

    interrupted = _invoke_until_interrupt(
        graph,
        state=_create_high_risk_state(
            thread_id=thread_id
        ),
        config=config,
    )

    _interrupt_payload(
        interrupted
    )

    resumed = graph.invoke(
        Command(
            resume={
                "action": "correct",
                "reviewer_id": (
                    "user-memory-checkpoint"
                ),
                "comment": (
                    "O valor correto dos gastos "
                    "mensais é 3500."
                ),
                "corrections": {
                    "expenses": 3500,
                },
            }
        ),
        config=config,
    )

    assert resumed[
        "human_review_status"
    ] == "corrected"

    assert resumed[
        "human_review_corrections"
    ] == {
        "expenses": 3500,
    }

    assert resumed[
        "human_review_resume_route"
    ] == "team_router"

    assert resumed[
        "human_review_current"
    ]["decision"]["corrections"] == {
        "expenses": 3500,
    }


@pytest.mark.parametrize(
    "decision, expected_status",
    [
        (
            {
                "action": "reject",
                "reviewer_id": "reviewer-001",
                "reason": (
                    "Os dados não foram confirmados."
                ),
            },
            "rejected",
        ),
        (
            {
                "action": "cancel",
                "reviewer_id": "user-001",
                "reason": (
                    "O usuário cancelou a revisão."
                ),
            },
            "cancelled",
        ),
    ],
)
def test_real_terminal_resume_routes_to_summary(
    decision,
    expected_status,
):
    graph = _create_test_graph()

    thread_id = (
        f"thread-{expected_status}-"
        + uuid4().hex
    )

    config = _config(
        thread_id
    )

    interrupted = _invoke_until_interrupt(
        graph,
        state=_create_high_risk_state(
            thread_id=thread_id
        ),
        config=config,
    )

    _interrupt_payload(
        interrupted
    )

    resumed = graph.invoke(
        Command(
            resume=decision
        ),
        config=config,
    )

    assert resumed[
        "human_review_status"
    ] == expected_status

    assert resumed[
        "human_review_required"
    ] is False

    assert resumed[
        "human_review_resume_route"
    ] == "conversation_summary"


def test_resume_with_different_thread_does_not_find_checkpoint():
    graph = _create_test_graph()

    original_thread = (
        "thread-original-"
        + uuid4().hex
    )

    original_config = _config(
        original_thread
    )

    interrupted = _invoke_until_interrupt(
        graph,
        state=_create_high_risk_state(
            thread_id=original_thread
        ),
        config=original_config,
    )

    _interrupt_payload(
        interrupted
    )

    wrong_config = _config(
        "thread-wrong-" + uuid4().hex
    )

    result = graph.invoke(
        Command(
            resume={
                "action": "approve",
                "reviewer_id": "user-001",
            }
        ),
        config=wrong_config,
    )

    assert result is not None

    original_snapshot = graph.get_state(
        original_config
    )

    assert original_snapshot.next == (
        "human_review_interrupt",
    )

    assert original_snapshot.values[
        "human_review_status"
    ] == "requested"
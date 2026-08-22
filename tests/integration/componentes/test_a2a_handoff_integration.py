"""Integração do contrato A2A com o handoff da INNA."""

from __future__ import annotations

from src.agents.graph import (
    _selecionar_rota_apos_handoff,
)
from src.agents.handoff_coordinator_node import (
    handoff_coordinator_node,
)


def _base_state() -> dict:
    return {
        "thread_id": "week5-5b-a2a-001",
        "intent": "diagnostico_financeiro",
        "current_agent": "financial_agent",
        "route_source": "adaptive_gateway",
        "routing_reason": (
            "Diagnóstico concluído com pedido "
            "de relatório."
        ),
        "generate_report": True,
        "task_status": "completed",
        "task_completion_score": 1.0,
        "completed_requirements": [
            "agent_execution",
            "financial_inputs_resolved",
            "financial_calculation_executed",
            "response_generation",
        ],
        "missing_requirements": [],
        "response": (
            "Diagnóstico financeiro concluído."
        ),
        "handoff_current": None,
        "handoff_history": [],
        "handoff_count": 0,
        "max_handoffs": 3,
        "handoff_limit_exceeded": False,
        "handoff_required": True,
        "handoff_target": "report_agent",
        "handoff_reason": (
            "Preparar relatório financeiro."
        ),
        "a2a_message_count": 0,
        "max_a2a_messages": 6,
        "a2a_history": [],
        "errors": [],
        "trace": [
            "agent:financial_agent",
        ],
    }


def test_governed_a2a_creates_existing_handoff():
    result = handoff_coordinator_node(
        _base_state()
    )

    assert result[
        "a2a_message_count"
    ] == 1

    assert len(
        result["a2a_history"]
    ) == 1

    record = result[
        "a2a_history"
    ][0]

    assert record["allowed"] is True

    assert record[
        "source_agent"
    ] == "financial_agent"

    assert record[
        "target_agent"
    ] == "report_agent"

    assert record[
        "capability"
    ] == "report_preparation"

    assert "payload" not in record
    assert "metadata" not in record

    handoff = result[
        "handoff_current"
    ]

    assert handoff["status"] == "requested"

    assert handoff[
        "from_agent"
    ] == "financial_agent"

    assert handoff[
        "to_agent"
    ] == "report_agent"

    assert handoff[
        "reason"
    ] == "Preparar relatório financeiro."

    assert handoff[
        "metadata"
    ][
        "source"
    ] == "a2a"

    assert handoff[
        "metadata"
    ][
        "a2a_message_id"
    ] == record["message_id"]

    assert handoff[
        "metadata"
    ][
        "a2a_trace_id"
    ] == record["trace_id"]


def test_governed_a2a_handoff_returns_to_team_router():
    state = _base_state()

    result = handoff_coordinator_node(
        state
    )

    state.update(
        result
    )

    assert (
        _selecionar_rota_apos_handoff(
            state
        )
        == "team_router"
    )


def test_zero_a2a_budget_blocks_handoff():
    state = _base_state()
    state["max_a2a_messages"] = 0

    result = handoff_coordinator_node(
        state
    )

    assert (
        result["handoff_required"]
        is False
    )

    assert (
        "handoff_current"
        not in result
    )

    assert result[
        "a2a_message_count"
    ] == 0

    assert result[
        "a2a_history"
    ][0]["allowed"] is False

    assert result[
        "a2a_history"
    ][0]["reason"] == (
        "a2a_message_budget_exceeded"
    )

    assert result["trace"][-1] == (
        "a2a:error:"
        "a2a_message_budget_exceeded"
    )


def test_a2a_message_limit_blocks_next_handoff():
    state = _base_state()

    state[
        "a2a_message_count"
    ] = 6

    state[
        "max_a2a_messages"
    ] = 6

    result = handoff_coordinator_node(
        state
    )

    assert (
        "handoff_current"
        not in result
    )

    assert result[
        "a2a_message_count"
    ] == 6

    assert result[
        "a2a_history"
    ][0]["allowed"] is False


def test_legacy_handoff_without_a2a_state_is_preserved():
    state = _base_state()

    state.pop(
        "a2a_message_count"
    )

    state.pop(
        "max_a2a_messages"
    )

    state.pop(
        "a2a_history"
    )

    result = handoff_coordinator_node(
        state
    )

    assert result[
        "handoff_count"
    ] == 1

    assert result[
        "handoff_current"
    ]["status"] == "requested"

    assert (
        "a2a_message_count"
        not in result
    )

    assert "a2a_history" not in result

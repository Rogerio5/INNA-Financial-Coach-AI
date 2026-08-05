from __future__ import annotations

from src.agents.handoff import (
    accept_handoff,
    create_handoff,
)
from src.agents.handoff_coordinator_node import (
    handoff_coordinator_node,
)


def _base_state() -> dict:
    return {
        "thread_id": "thread-001",
        "intent": "relatorio",
        "current_agent": "financial_agent",
        "route_source": "rule",
        "routing_reason": ("O diagnóstico precisa virar relatório."),
        "task_status": "completed",
        "task_completion_score": 1.0,
        "completed_requirements": [
            "agent_execution",
            "financial_inputs_resolved",
            "financial_calculation_executed",
            "response_generation",
        ],
        "missing_requirements": [],
        "response": "Diagnóstico concluído.",
        "handoff_current": None,
        "handoff_history": [],
        "handoff_count": 0,
        "handoff_required": True,
        "handoff_target": "report_agent",
        "handoff_reason": ("Transformar o diagnóstico em relatório."),
        "errors": [],
        "trace": [
            "agent:financial_agent",
        ],
    }


def test_coordinator_does_nothing_without_request():
    state = _base_state()
    state["handoff_required"] = False

    result = handoff_coordinator_node(state)

    assert result == {}


def test_coordinator_creates_requested_handoff():
    result = handoff_coordinator_node(_base_state())

    handoff = result["handoff_current"]

    assert handoff["status"] == "requested"

    assert handoff["from_agent"] == ("financial_agent")

    assert handoff["to_agent"] == ("report_agent")

    assert result["handoff_count"] == 1
    assert result["handoff_required"] is False

    assert result["handoff_history"] == [handoff]

    assert result["trace"][-1].startswith("handoff:requested:")


def test_request_payload_contains_task_evidence():
    result = handoff_coordinator_node(_base_state())

    payload = result["handoff_current"]["payload"]

    assert payload["intent"] == "relatorio"

    assert payload["task_completion_score"] == 1.0

    assert payload["missing_requirements"] == []


def test_requested_handoff_is_accepted_by_target():
    request_result = handoff_coordinator_node(_base_state())

    state = _base_state()

    state.update(
        {
            "current_agent": "report_agent",
            "handoff_required": False,
            "handoff_current": request_result["handoff_current"],
            "handoff_count": 1,
            # A tarefa ainda não foi concluída.
            # O teste valida somente o aceite.
            "task_status": "in_progress",
            "task_completion_score": 0.5,
            "trace": [
                "agent:report_agent",
            ],
        }
    )

    result = handoff_coordinator_node(state)

    assert result["handoff_current"]["status"] == "accepted"

    assert result["trace"][-1].startswith("handoff:accepted:")


def test_requested_handoff_is_not_accepted_by_other_agent():
    request_result = handoff_coordinator_node(_base_state())

    state = _base_state()

    state.update(
        {
            "current_agent": "rag_agent",
            "handoff_required": False,
            "handoff_current": request_result["handoff_current"],
        }
    )

    result = handoff_coordinator_node(state)

    assert result == {}


def test_accepted_handoff_is_completed():
    requested = create_handoff(
        from_agent="financial_agent",
        to_agent="report_agent",
        reason="Preparar relatório.",
    )

    accepted = accept_handoff(requested)

    state = _base_state()

    state.update(
        {
            "current_agent": "report_agent",
            "handoff_required": False,
            "handoff_current": accepted,
            "task_status": "completed",
            "task_completion_score": 1.0,
            "response": "Relatório concluído.",
            "trace": [
                "agent:report_agent",
            ],
        }
    )

    result = handoff_coordinator_node(state)

    completed = result["handoff_current"]

    assert completed["status"] == ("completed")

    assert completed["result"]["response_generated"] is True

    assert result["handoff_target"] == ""
    assert result["handoff_reason"] == ""

    assert result["trace"][-1].startswith("handoff:completed:")


def test_accepted_handoff_waits_for_task_completion():
    requested = create_handoff(
        from_agent="financial_agent",
        to_agent="report_agent",
        reason="Preparar relatório.",
    )

    accepted = accept_handoff(requested)

    state = _base_state()

    state.update(
        {
            "current_agent": "report_agent",
            "handoff_required": False,
            "handoff_current": accepted,
            "task_status": "partially_completed",
        }
    )

    result = handoff_coordinator_node(state)

    assert result == {}


def test_accepted_handoff_fails_when_target_has_error():
    requested = create_handoff(
        from_agent="financial_agent",
        to_agent="report_agent",
        reason="Preparar relatório.",
    )

    accepted = accept_handoff(requested)

    state = _base_state()

    state.update(
        {
            "current_agent": "report_agent",
            "handoff_required": False,
            "handoff_current": accepted,
            "errors": ["Falha ao gerar relatório."],
        }
    )

    result = handoff_coordinator_node(state)

    failed = result["handoff_current"]

    assert failed["status"] == "failed"

    assert "falha" in failed["error"].lower()

    assert result["trace"][-1].startswith("handoff:failed:")


def test_invalid_target_is_reported():
    state = _base_state()
    state["handoff_target"] = "unknown_agent"

    result = handoff_coordinator_node(state)

    assert result["errors"]
    assert result["trace"][-1] == ("handoff:error:invalid_target")


def test_self_handoff_is_rejected():
    state = _base_state()
    state["handoff_target"] = "financial_agent"

    result = handoff_coordinator_node(state)

    assert result["errors"]
    assert result["trace"][-1] == ("handoff:error:self_handoff")


def test_missing_reason_is_reported():
    state = _base_state()
    state["handoff_reason"] = "   "

    result = handoff_coordinator_node(state)

    assert result["errors"]
    assert result["trace"][-1] == ("handoff:error:missing_reason")


def test_source_agent_can_be_inferred_from_trace():
    state = _base_state()

    state.pop("current_agent")

    state["next_node"] = ""
    state["trace"] = [
        "agent:financial_agent",
    ]

    result = handoff_coordinator_node(state)

    assert result["handoff_current"]["from_agent"] == "financial_agent"


def test_handoff_count_is_incremented():
    state = _base_state()
    state["handoff_count"] = 3
    state["max_handoffs"] = 5

    result = handoff_coordinator_node(state)

    assert result["handoff_count"] == 4


def test_handoff_limit_is_enforced():
    state = _base_state()
    state["handoff_count"] = 3
    state["max_handoffs"] = 3

    result = handoff_coordinator_node(state)

    assert result["handoff_limit_exceeded"] is True

    assert result["handoff_required"] is False

    assert result["trace"][-1] == ("handoff:error:limit_exceeded")


def test_reverse_handoff_cycle_is_blocked():
    state = _base_state()

    state["current_agent"] = "report_agent"
    state["handoff_target"] = "financial_agent"

    state["handoff_history"] = [
        {
            "handoff_id": "handoff-previous",
            "from_agent": "financial_agent",
            "to_agent": "report_agent",
            "status": "completed",
        }
    ]

    result = handoff_coordinator_node(state)

    assert result["handoff_required"] is False

    assert result["trace"][-1] == ("handoff:error:reverse_cycle")


def test_custom_handoff_limit_is_respected():
    state = _base_state()
    state["handoff_count"] = 1
    state["max_handoffs"] = 1

    result = handoff_coordinator_node(state)

    assert result["handoff_limit_exceeded"] is True


def test_requested_handoff_is_accepted_and_completed():
    request_result = handoff_coordinator_node(_base_state())

    state = _base_state()

    state.update(
        {
            "current_agent": "report_agent",
            "handoff_required": False,
            "handoff_current": request_result["handoff_current"],
            "handoff_count": 1,
            "task_status": "completed",
            "task_completion_score": 1.0,
            "response": "Relatório concluído.",
            "errors": [],
            "trace": [
                "agent:report_agent",
            ],
        }
    )

    result = handoff_coordinator_node(state)

    handoff = result["handoff_current"]

    assert handoff["status"] == "completed"

    assert handoff["accepted_at"] is not None
    assert handoff["completed_at"] is not None

    assert handoff["result"]["task_status"] == "completed"

    assert handoff["result"]["task_completion_score"] == 1.0

    assert handoff["result"]["response_generated"] is True

    assert result["handoff_target"] == ""
    assert result["handoff_reason"] == ""

    assert "handoff:accepted:" in result["trace"][-1]

    assert "handoff:completed:" in result["trace"][-1]

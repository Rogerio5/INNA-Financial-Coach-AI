from __future__ import annotations

from src.agents.graph import (
    _selecionar_rota_apos_handoff,
)
from src.agents.handoff_coordinator_node import (
    handoff_coordinator_node,
)


def _completed_financial_state() -> dict:
    return {
        "thread_id": "thread-report-001",
        "intent": "diagnostico_financeiro",
        "current_agent": "financial_agent",
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
            "Diagnóstico financeiro calculado."
        ),
        "structured_response": {
            "diagnostico_financeiro": {
                "saldo_estimado": 1500.0,
                "score_financeiro": 82,
            },
            "handoff_request": {
                "from_agent": "financial_agent",
                "to_agent": "report_agent",
            },
        },
        "handoff_current": None,
        "handoff_history": [],
        "handoff_count": 0,
        "max_handoffs": 3,
        "handoff_limit_exceeded": False,
        "handoff_required": True,
        "handoff_target": "report_agent",
        "handoff_reason": (
            "O diagnóstico financeiro foi concluído "
            "e o usuário solicitou relatório."
        ),
        "errors": [],
        "trace": [
            "agent:financial_agent",
        ],
    }


def test_financial_request_creates_explicit_handoff():
    result = handoff_coordinator_node(
        _completed_financial_state()
    )

    handoff = result[
        "handoff_current"
    ]

    assert handoff["status"] == "requested"

    assert handoff["from_agent"] == (
        "financial_agent"
    )

    assert handoff["to_agent"] == (
        "report_agent"
    )

    assert result["handoff_count"] == 1


def test_requested_financial_handoff_routes_to_report():
    coordinator_result = (
        handoff_coordinator_node(
            _completed_financial_state()
        )
    )

    state = _completed_financial_state()
    state.update(
        coordinator_result
    )

    route = _selecionar_rota_apos_handoff(
        state
    )

    assert route == "report_agent"


def test_financial_handoff_payload_preserves_evidence():
    result = handoff_coordinator_node(
        _completed_financial_state()
    )

    payload = result[
        "handoff_current"
    ]["payload"]

    assert payload["intent"] == (
        "diagnostico_financeiro"
    )

    assert payload[
        "task_completion_score"
    ] == 1.0

    assert (
        "financial_calculation_executed"
        in payload["completed_requirements"]
    )


def test_report_target_completes_requested_handoff():
    requested_result = (
        handoff_coordinator_node(
            _completed_financial_state()
        )
    )

    report_state = (
        _completed_financial_state()
    )

    report_state.update({
        "current_agent": "report_agent",
        "handoff_required": False,
        "handoff_current": requested_result[
            "handoff_current"
        ],
        "handoff_count": 1,
        "task_status": "completed",
        "task_completion_score": 1.0,
        "response": "Relatório concluído.",
        "errors": [],
        "trace": [
            "agent:report_agent",
        ],
    })

    result = handoff_coordinator_node(
        report_state
    )

    assert result[
        "handoff_current"
    ]["status"] == "completed"

from __future__ import annotations

from src.agents.task_completion_blackboard import (
    build_task_completion_blackboard_payload,
)
from src.agents.task_completion_node import (
    task_completion_node,
)


def _financial_state():
    return {
        "intent": "diagnostico_financeiro",
        "current_agent": "financial_agent",
        "response": (
            "Diagnóstico financeiro concluído "
            "com sucesso para o usuário."
        ),
        "structured_response": {
            "financial_input_resolution": {
                "ready": True,
                "missing_fields": [],
            }
        },
        "tool_results": [
            {
                "tool": (
                    "calcular_diagnostico_financeiro"
                ),
                "status": "success",
                "ok": True,
            }
        ],
        "errors": [],
        "trace": [],
        "shared_blackboard_entries": [],
        "shared_blackboard_count": 0,
        "max_shared_blackboard_entries": 64,
        "shared_blackboard_audit": [],
        "shared_blackboard_last_decision": {},
    }


def test_completed_financial_task_is_published():
    result = task_completion_node(
        _financial_state()
    )

    assert (
        result["task_status"]
        == "completed"
    )

    assert (
        result["shared_blackboard_count"]
        == 1
    )

    entry = result[
        "shared_blackboard_entries"
    ][0]

    assert (
        entry["producer"]
        == "financial_agent"
    )

    assert (
        entry["visibility"]
        == "workflow"
    )


def test_blackboard_payload_has_only_derived_metadata():
    result = task_completion_node(
        _financial_state()
    )

    payload = result[
        "shared_blackboard_entries"
    ][0]["payload"]

    assert set(
        payload
    ) == {
        "task_status",
        "task_completion_score",
        "completed_requirements",
        "missing_requirements",
        "response_generated",
        "tool_results_count",
        "agent_resolution",
    }


def test_response_is_not_copied_to_blackboard():
    state = _financial_state()

    marker = (
        "PRIVATE_RESPONSE_MARKER_789"
    )

    state["response"] = (
        marker
        + " diagnóstico concluído com dados suficientes."
    )

    result = task_completion_node(
        state
    )

    assert (
        marker
        not in str(
            result[
                "shared_blackboard_entries"
            ]
        )
    )

    assert (
        marker
        not in str(
            result[
                "shared_blackboard_audit"
            ]
        )
    )


def test_user_message_is_not_copied():
    state = _financial_state()

    marker = (
        "PRIVATE_USER_MESSAGE_456"
    )

    state["user_message"] = marker

    result = task_completion_node(
        state
    )

    assert (
        marker
        not in str(
            result[
                "shared_blackboard_entries"
            ]
        )
    )


def test_failed_task_does_not_publish_error_text():
    state = {
        "intent": "consulta_rag",
        "current_agent": "rag_agent",
        "response": "",
        "structured_response": {},
        "tool_results": [],
        "errors": [
            "PRIVATE_ERROR_MARKER_321",
        ],
        "trace": [],
        "shared_blackboard_entries": [],
        "shared_blackboard_count": 0,
        "max_shared_blackboard_entries": 64,
        "shared_blackboard_audit": [],
        "shared_blackboard_last_decision": {},
    }

    result = task_completion_node(
        state
    )

    assert (
        result["task_status"]
        == "failed"
    )

    assert (
        result["shared_blackboard_count"]
        == 1
    )

    assert (
        "PRIVATE_ERROR_MARKER_321"
        not in str(
            result[
                "shared_blackboard_entries"
            ]
        )
    )


def test_fallback_result_is_team_scoped():
    state = {
        "intent": "desconhecido",
        "current_agent": "fallback_agent",
        "response": (
            "Não identifiquei uma solicitação "
            "financeira específica neste pedido."
        ),
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
        "shared_blackboard_entries": [],
        "shared_blackboard_count": 0,
        "max_shared_blackboard_entries": 64,
        "shared_blackboard_audit": [],
        "shared_blackboard_last_decision": {},
    }

    result = task_completion_node(
        state
    )

    entry = result[
        "shared_blackboard_entries"
    ][0]

    assert (
        entry["visibility"]
        == "team"
    )

    assert (
        entry["team"]
        == "support_team"
    )


def test_same_completion_is_deduplicated():
    state = _financial_state()

    first = task_completion_node(
        state
    )

    state.update(
        first
    )

    second = task_completion_node(
        state
    )

    assert (
        second["shared_blackboard_count"]
        == 1
    )

    assert (
        second[
            "shared_blackboard_last_decision"
        ]["reason"]
        == "blackboard_entry_deduplicated"
    )


def test_existing_task_completion_trace_contract_is_preserved():
    result = task_completion_node(
        _financial_state()
    )

    assert (
        result["trace"][-1]
        .startswith(
            "task_completion:completed:"
        )
    )


def test_payload_builder_does_not_copy_raw_evidence():
    completion = {
        "task_status": "completed",
        "task_completion_score": 1.0,
        "completed_requirements": [
            "agent_execution",
            "response_generation",
        ],
        "missing_requirements": [],
        "task_completion_evidence": {
            "agent": "financial_agent",
            "agent_resolution": (
                "explicit_or_inferred"
            ),
            "tool_results_count": 2,
            "has_response": True,
            "secret": (
                "SHOULD_NOT_BE_COPIED"
            ),
        },
    }

    payload = (
        build_task_completion_blackboard_payload(
            completion
        )
    )

    assert (
        "SHOULD_NOT_BE_COPIED"
        not in str(
            payload
        )
    )

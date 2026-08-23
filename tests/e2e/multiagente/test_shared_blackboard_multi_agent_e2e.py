from __future__ import annotations

from src.agents.shared_blackboard_runtime import (
    read_shared_blackboard,
)
from src.agents.task_completion_node import (
    task_completion_node,
)


def _base_blackboard_state():
    return {
        "shared_blackboard_entries": [],
        "shared_blackboard_count": 0,
        "max_shared_blackboard_entries": 64,
        "shared_blackboard_audit": [],
        "shared_blackboard_last_decision": {},
        "trace": [],
    }


def test_financial_result_is_shared_with_rag_agent():
    state = _base_blackboard_state()

    state.update(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": (
                "Seu diagnóstico financeiro foi "
                "calculado corretamente com os "
                "dados fornecidos."
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
        }
    )

    financial_result = (
        task_completion_node(
            state
        )
    )

    state.update(
        financial_result
    )

    assert (
        state["task_status"]
        == "completed"
    )

    assert (
        state["shared_blackboard_count"]
        == 1
    )

    rag_view = read_shared_blackboard(
        state,
        principal="rag_agent",
    )

    assert len(
        rag_view.entries
    ) == 1

    assert (
        rag_view.entries[0].producer
        == "financial_agent"
    )


def test_two_agents_publish_into_same_workflow():
    state = _base_blackboard_state()

    # Etapa 1: agente financeiro.
    state.update(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": (
                "O diagnóstico financeiro foi "
                "concluído corretamente com todas "
                "as informações necessárias."
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
        }
    )

    state.update(
        task_completion_node(
            state
        )
    )

    assert (
        state["shared_blackboard_count"]
        == 1
    )

    # Etapa 2: agente de conhecimento/RAG.
    state.update(
        {
            "intent": "consulta_rag",
            "current_agent": "rag_agent",
            "response": (
                "As orientações recuperadas explicam "
                "como organizar a reserva financeira "
                "de forma adequada e progressiva."
            ),
            "structured_response": {
                "rag_execution": {
                    "retrieved_documents": 2,
                    "sources": [
                        "inna-knowledge-001",
                    ],
                }
            },
            "tool_results": [
                {
                    "tool": (
                        "buscar_conhecimento_rag"
                    ),
                    "status": "success",
                    "ok": True,
                }
            ],
            "errors": [],
        }
    )

    state.update(
        task_completion_node(
            state
        )
    )

    assert (
        state["task_status"]
        == "completed"
    )

    assert (
        state["shared_blackboard_count"]
        == 2
    )

    report_view = read_shared_blackboard(
        state,
        principal="report_agent",
    )

    assert len(
        report_view.entries
    ) == 2

    producers = {
        entry.producer
        for entry in report_view.entries
    }

    assert producers == {
        "financial_agent",
        "rag_agent",
    }


def test_blackboard_does_not_propagate_raw_content_cross_agent():
    state = _base_blackboard_state()

    user_marker = (
        "PRIVATE_USER_CONTENT_X91"
    )

    response_marker = (
        "PRIVATE_RESPONSE_CONTENT_Y82"
    )

    state.update(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "user_message": user_marker,
            "response": (
                response_marker
                + " diagnóstico financeiro "
                "concluído com sucesso após "
                "validar todas as informações."
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
        }
    )

    state.update(
        task_completion_node(
            state
        )
    )

    rag_view = read_shared_blackboard(
        state,
        principal="rag_agent",
    )

    serialized = str(
        [
            entry.model_dump()
            for entry in rag_view.entries
        ]
    )

    assert (
        user_marker
        not in serialized
    )

    assert (
        response_marker
        not in serialized
    )


def test_service_identity_cannot_consume_shared_workflow():
    state = _base_blackboard_state()

    state.update(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": (
                "O diagnóstico financeiro foi "
                "concluído corretamente nesta "
                "execução do workflow."
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
        }
    )

    state.update(
        task_completion_node(
            state
        )
    )

    communication_view = (
        read_shared_blackboard(
            state,
            principal="communication_agent",
        )
    )

    assert (
        communication_view.entries
        == ()
    )


def test_blackboard_audit_contains_no_task_payload():
    state = _base_blackboard_state()

    marker = (
        "PRIVATE_AUDIT_PAYLOAD_Z73"
    )

    state.update(
        {
            "intent": "diagnostico_financeiro",
            "current_agent": "financial_agent",
            "response": (
                marker
                + " diagnóstico financeiro "
                "finalizado corretamente com "
                "resultado disponível."
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
        }
    )

    state.update(
        task_completion_node(
            state
        )
    )

    assert (
        marker
        not in str(
            state[
                "shared_blackboard_audit"
            ]
        )
    )

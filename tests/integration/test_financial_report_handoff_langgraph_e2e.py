from __future__ import annotations

from typing import Any

import src.agents.graph as graph_module


def _context_builder_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "context": {
            "rendered_prompt": (
                "Contexto de teste."
            ),
        },
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            "e2e:context_builder",
        ],
    }


def _supervisor_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intent": "diagnostico_financeiro",
        "confidence": 0.97,
        "next_node": "financial_agent",
        "generate_report": True,
        "use_database": True,
        "route_source": "test",
        "routing_reason": (
            "Diagnóstico seguido de relatório."
        ),
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            (
                "supervisor:test:"
                "diagnostico_financeiro"
            ),
            "e2e:supervisor",
        ],
    }


def _governance_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            "e2e:execution_governance",
        ],
    }


def _financial_agent_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    diagnosis = {
        "moeda": "BRL",
        "saldo_estimado": 1500.0,
        "score_financeiro": 82,
        "nivel_risco": "Baixo",
    }

    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    structured_response[
        "diagnostico_financeiro"
    ] = diagnosis

    return {
        "response": (
            "Diagnóstico financeiro concluído."
        ),
        "structured_response": (
            structured_response
        ),
        "handoff_required": True,
        "handoff_target": "report_agent",
        "handoff_reason": (
            "O diagnóstico foi concluído e "
            "o usuário solicitou relatório."
        ),
        "errors": [],
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            "tool:financial_diagnosis:success",
            "agent:financial_agent",
            "e2e:financial_agent",
        ],
    }


def _report_agent_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    structured_response = dict(
        state.get(
            "structured_response",
            {},
        )
    )

    diagnosis = structured_response.get(
        "diagnostico_financeiro"
    )

    assert isinstance(
        diagnosis,
        dict,
    )

    structured_response[
        "relatorio_financeiro"
    ] = {
        "generated": True,
        "source_score": diagnosis[
            "score_financeiro"
        ],
    }

    return {
        "response": (
            "Relatório financeiro concluído."
        ),
        "structured_response": (
            structured_response
        ),
        "handoff_required": False,
        "errors": [],
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            "tool:report_preparation:success",
            "agent:report_agent",
            "e2e:report_agent",
        ],
    }


def _task_completion_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    current_agent = ""

    for item in reversed(
        list(
            state.get(
                "trace",
                [],
            )
        )
    ):
        normalized = str(
            item or ""
        ).strip()

        if normalized.startswith(
            "agent:"
        ):
            current_agent = normalized.split(
                ":",
                1,
            )[1].split(
                ":",
                1,
            )[0]

            break

    if current_agent == "financial_agent":
        requirements = [
            "agent_execution",
            "financial_inputs_resolved",
            "financial_calculation_executed",
            "response_generation",
        ]
    else:
        requirements = [
            "agent_execution",
            "report_generation",
            "response_generation",
        ]

    return {
        "current_agent": current_agent,
        "task_status": "completed",
        "task_completion_score": 1.0,
        "completed_requirements": requirements,
        "missing_requirements": [],
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            (
                "e2e:task_completion:"
                f"{current_agent}"
            ),
        ],
    }


def _summary_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "conversation_summary": (
            "Diagnóstico e relatório concluídos."
        ),
        "trace": [
            *list(
                state.get(
                    "trace",
                    [],
                )
            ),
            "e2e:conversation_summary",
        ],
    }


def _initial_state() -> dict[str, Any]:
    return {
        "user_message": (
            "Analise minha situação financeira "
            "e gere um relatório."
        ),
        "thread_id": "thread-e2e-handoff",
        "user_id": "user-test",
        "language": "pt-BR",
        "currency": "BRL",
        "conversation_history": [],
        "context": {},
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
        "handoff_current": None,
        "handoff_history": [],
        "handoff_count": 0,
        "max_handoffs": 3,
        "handoff_limit_exceeded": False,
        "handoff_required": False,
        "handoff_target": "",
        "handoff_reason": "",
    }


def test_complete_financial_report_handoff_flow(
    monkeypatch,
):
    monkeypatch.setattr(
        graph_module,
        "context_builder_node",
        _context_builder_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "supervisor_node",
        _supervisor_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "apply_execution_governance",
        _governance_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "financial_agent_node",
        _financial_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "report_agent_node",
        _report_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "task_completion_node",
        _task_completion_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "conversation_summary_node",
        _summary_stub,
    )

    graph = (
        graph_module
        .criar_builder_inna()
        .compile()
    )

    result = graph.invoke(
        _initial_state(),
        config={
            "recursion_limit": 25,
        },
    )

    assert result["response"] == (
        "Relatório financeiro concluído."
    )

    assert result["conversation_summary"] == (
        "Diagnóstico e relatório concluídos."
    )

    assert result["handoff_count"] == 1

    handoff = result[
        "handoff_current"
    ]

    assert handoff["status"] == "completed"

    assert handoff["from_agent"] == (
        "financial_agent"
    )

    assert handoff["to_agent"] == (
        "report_agent"
    )

    assert handoff["accepted_at"] is not None
    assert handoff["completed_at"] is not None

    assert handoff["result"][
        "task_status"
    ] == "completed"

    report = result[
        "structured_response"
    ]["relatorio_financeiro"]

    assert report["generated"] is True
    assert report["source_score"] == 82


def test_execution_trace_contains_both_agents(
    monkeypatch,
):
    monkeypatch.setattr(
        graph_module,
        "context_builder_node",
        _context_builder_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "supervisor_node",
        _supervisor_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "apply_execution_governance",
        _governance_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "financial_agent_node",
        _financial_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "report_agent_node",
        _report_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "task_completion_node",
        _task_completion_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "conversation_summary_node",
        _summary_stub,
    )

    graph = (
        graph_module
        .criar_builder_inna()
        .compile()
    )

    result = graph.invoke(
        _initial_state(),
        config={
            "recursion_limit": 25,
        },
    )

    trace = list(
        result.get(
            "trace",
            [],
        )
    )

    assert "e2e:financial_agent" in trace
    assert "e2e:report_agent" in trace

    financial_index = trace.index(
        "e2e:financial_agent"
    )

    report_index = trace.index(
        "e2e:report_agent"
    )

    assert financial_index < report_index

    assert (
        "e2e:task_completion:financial_agent"
        in trace
    )

    assert (
        "e2e:task_completion:report_agent"
        in trace
    )

    assert trace[-1] == (
        "e2e:conversation_summary"
    )

def test_handoff_history_contains_single_logical_transfer(
    monkeypatch,
):
    monkeypatch.setattr(
        graph_module,
        "context_builder_node",
        _context_builder_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "supervisor_node",
        _supervisor_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "apply_execution_governance",
        _governance_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "financial_agent_node",
        _financial_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "report_agent_node",
        _report_agent_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "task_completion_node",
        _task_completion_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "conversation_summary_node",
        _summary_stub,
    )

    graph = (
        graph_module
        .criar_builder_inna()
        .compile()
    )

    result = graph.invoke(
        _initial_state(),
        config={
            "recursion_limit": 25,
        },
    )

    history = result[
        "handoff_history"
    ]

    assert len(history) == 1

    assert history[0]["status"] == (
        "completed"
    )

    assert history[0]["handoff_id"] == (
        result["handoff_current"][
            "handoff_id"
        ]
    )

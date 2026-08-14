from __future__ import annotations

from typing import Any

import src.agents.graph as graph_module


def _append_trace(
    state: dict[str, Any],
    marker: str,
) -> list[str]:
    return [
        *list(
            state.get(
                "trace",
                [],
            )
            or []
        ),
        marker,
    ]


def _context_builder_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "context": {
            "rendered_prompt": "Adaptive E2E.",
        },
        "trace": _append_trace(
            state,
            "e2e:context_builder",
        ),
    }


def _make_agent_stub(
    agent_name: str,
):
    def _agent_stub(
        state: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "response": f"{agent_name}:ok",
            "current_agent": agent_name,
            "handoff_required": False,
            "trace": _append_trace(
                state,
                f"e2e:agent:{agent_name}",
            ),
        }

    return _agent_stub


def _task_completion_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_status": "completed",
        "task_completion_score": 1.0,
        "completed_requirements": [
            "agent_execution",
        ],
        "missing_requirements": [],
        "handoff_required": False,
        "trace": _append_trace(
            state,
            "e2e:task_completion",
        ),
    }


def _human_review_policy_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "human_review_required": False,
        "trace": _append_trace(
            state,
            "e2e:human_review_policy",
        ),
    }


def _route_to_handoff_coordinator(
    state: dict[str, Any],
) -> str:
    del state
    return "handoff_coordinator"


def _handoff_coordinator_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "handoff_required": False,
        "trace": _append_trace(
            state,
            "e2e:handoff_coordinator",
        ),
    }


def _route_to_summary(
    state: dict[str, Any],
) -> str:
    del state
    return "conversation_summary"


def _conversation_summary_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "conversation_summary": (
            "Adaptive LangGraph E2E concluído."
        ),
        "trace": _append_trace(
            state,
            "e2e:conversation_summary",
        ),
    }


def _simple_supervisor_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intent": "consulta_rag",
        "confidence": 0.89,
        "next_node": "rag_agent",
        "use_rag": True,
        "use_database": False,
        "generate_report": False,
        "route_source": "test",
        "routing_reason": "simple_rag_request",
        "trace": _append_trace(
            state,
            "e2e:supervisor:simple",
        ),
    }


def _complex_supervisor_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intent": "diagnostico_financeiro",
        "confidence": 0.97,
        "next_node": "financial_agent",
        "use_database": True,
        "use_rag": False,
        "generate_report": True,
        "route_source": "test",
        "routing_reason": (
            "composite_financial_report_request"
        ),
        "trace": _append_trace(
            state,
            "e2e:supervisor:complex",
        ),
    }


def _escalate_supervisor_stub(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intent": "desconhecido",
        "confidence": 0.40,
        "next_node": "fallback_agent",
        "use_database": False,
        "use_rag": False,
        "generate_report": False,
        "route_source": "test",
        "routing_reason": "ambiguous_request",
        "trace": _append_trace(
            state,
            "e2e:supervisor:escalate",
        ),
    }


def _install_common_stubs(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        graph_module,
        "context_builder_node",
        _context_builder_stub,
    )

    for agent_name, attribute in (
        ("financial_agent", "financial_agent_node"),
        ("education_agent", "education_agent_node"),
        ("rag_agent", "rag_agent_node"),
        ("report_agent", "report_agent_node"),
        ("fallback_agent", "fallback_agent_node"),
    ):
        monkeypatch.setattr(
            graph_module,
            attribute,
            _make_agent_stub(
                agent_name
            ),
        )

    monkeypatch.setattr(
        graph_module,
        "task_completion_node",
        _task_completion_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "human_review_policy_node",
        _human_review_policy_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "select_route_after_human_review_policy",
        _route_to_handoff_coordinator,
    )

    monkeypatch.setattr(
        graph_module,
        "handoff_coordinator_node",
        _handoff_coordinator_stub,
    )

    monkeypatch.setattr(
        graph_module,
        "_selecionar_rota_apos_handoff",
        _route_to_summary,
    )

    monkeypatch.setattr(
        graph_module,
        "conversation_summary_node",
        _conversation_summary_stub,
    )


def _initial_state(
    message: str,
) -> dict[str, Any]:
    return graph_module._criar_estado_inicial(
        message,
        thread_id="week5-adaptive-e2e",
        usuario_id="adaptive-test-user",
        idioma="pt",
        moeda="BRL",
    )


def _invoke(
    monkeypatch,
    supervisor_stub,
    message: str,
) -> dict[str, Any]:
    _install_common_stubs(
        monkeypatch
    )

    monkeypatch.setattr(
        graph_module,
        "supervisor_node",
        supervisor_stub,
    )

    graph = (
        graph_module
        .criar_builder_inna()
        .compile()
    )

    return graph.invoke(
        _initial_state(
            message
        ),
        config={
            "recursion_limit": 25,
        },
    )


def _has_trace_prefix(
    trace: list[str],
    prefix: str,
) -> bool:
    return any(
        str(item).startswith(
            prefix
        )
        for item in trace
    )


def _trace_prefix_index(
    trace: list[str],
    prefix: str,
) -> int:
    return next(
        index
        for index, item in enumerate(trace)
        if str(item).startswith(
            prefix
        )
    )


def test_simple_request_bypasses_team_hierarchy(
    monkeypatch,
):
    result = _invoke(
        monkeypatch,
        _simple_supervisor_stub,
        "Explique reserva de emergência.",
    )

    trace = list(
        result.get(
            "trace",
            [],
        )
    )

    assert (
        result["adaptive_route_type"]
        == "simple"
    )
    assert (
        result["adaptive_complexity"]
        == "simple"
    )

    assert result["max_execution_steps"] == 1
    assert result["max_handoffs"] == 1

    assert not _has_trace_prefix(
        trace,
        "team_router:",
    )

    assert not _has_trace_prefix(
        trace,
        "team_supervisor:",
    )

    assert _has_trace_prefix(
        trace,
        "governance:",
    )

    assert (
        "e2e:agent:rag_agent"
        in trace
    )

    governance_index = (
        _trace_prefix_index(
            trace,
            "governance:",
        )
    )

    agent_index = trace.index(
        "e2e:agent:rag_agent"
    )

    assert governance_index < agent_index


def test_complex_request_uses_team_hierarchy(
    monkeypatch,
):
    result = _invoke(
        monkeypatch,
        _complex_supervisor_stub,
        (
            "Analise minhas finanças e depois "
            "gere um relatório."
        ),
    )

    trace = list(
        result.get(
            "trace",
            [],
        )
    )

    assert (
        result["adaptive_route_type"]
        == "complex"
    )
    assert (
        result["adaptive_complexity"]
        == "complex"
    )

    assert result["max_execution_steps"] == 5
    assert result["max_handoffs"] == 3

    assert _has_trace_prefix(
        trace,
        "team_router:",
    )

    assert _has_trace_prefix(
        trace,
        "team_supervisor:",
    )

    assert _has_trace_prefix(
        trace,
        "governance:",
    )

    assert (
        "e2e:agent:financial_agent"
        in trace
    )

    team_router_index = (
        _trace_prefix_index(
            trace,
            "team_router:",
        )
    )

    team_supervisor_index = (
        _trace_prefix_index(
            trace,
            "team_supervisor:",
        )
    )

    governance_index = (
        _trace_prefix_index(
            trace,
            "governance:",
        )
    )

    agent_index = trace.index(
        "e2e:agent:financial_agent"
    )

    assert (
        team_router_index
        < team_supervisor_index
        < governance_index
        < agent_index
    )


def test_low_confidence_request_escalates_to_fallback(
    monkeypatch,
):
    result = _invoke(
        monkeypatch,
        _escalate_supervisor_stub,
        "Preciso de alguma coisa.",
    )

    trace = list(
        result.get(
            "trace",
            [],
        )
    )

    assert (
        result["adaptive_route_type"]
        == "escalate"
    )

    assert (
        result["adaptive_target_agent"]
        == "fallback_agent"
    )

    assert result["max_execution_steps"] == 1
    assert result["max_handoffs"] == 1

    assert not _has_trace_prefix(
        trace,
        "team_router:",
    )

    assert not _has_trace_prefix(
        trace,
        "team_supervisor:",
    )

    assert _has_trace_prefix(
        trace,
        "governance:",
    )

    assert (
        "e2e:agent:fallback_agent"
        in trace
    )

    governance_index = (
        _trace_prefix_index(
            trace,
            "governance:",
        )
    )

    fallback_index = trace.index(
        "e2e:agent:fallback_agent"
    )

    assert governance_index < fallback_index

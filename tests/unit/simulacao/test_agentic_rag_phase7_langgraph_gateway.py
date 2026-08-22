from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

from src.agentic_rag.langgraph_integration import (
    AGENTIC_RAG_GATEWAY_VERSION,
    AgenticRagGatewayConfig,
    AgenticRagMode,
    GatewayDecision,
    GatewayOutcome,
    agentic_rag_gateway_audit_payload,
    agentic_rag_gateway_node,
    load_agentic_rag_gateway_config,
    run_agentic_rag_gateway,
)


def _state():
    return {
        "user_message": (
            "Compare reserva de emergência e dívidas "
            "e crie um plano financeiro completo."
        ),
        "language": "pt",
        "user_id": "trusted-user-test",
        "thread_id": "thread-test",
        "trace_id": "trace-test",
        "intent": "consulta_rag",
        "confidence": 0.90,
        "next_node": "rag_agent",
        "response": "",
        "conversation_history": [],
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [],
    }


def _legacy_node(state):
    return {
        **state,
        "current_agent": "rag_agent",
        "response": "resposta-legada",
        "conversation_history": [
            {
                "role": "assistant",
                "content": "resposta-legada",
            }
        ],
        "structured_response": {
            **state.get(
                "structured_response",
                {},
            ),
            "agent_response": {
                "agent": "rag_agent",
                "summary": "resposta-legada",
            },
        },
        "tool_results": [
            *state.get(
                "tool_results",
                [],
            ),
            {
                "tool": "consultar_rag_inna",
                "status": "success",
                "ok": True,
            },
        ],
        "trace": [
            *state.get(
                "trace",
                [],
            ),
            "agent:rag_agent",
        ],
    }


def _plan(
    complexity="complex",
):
    return SimpleNamespace(
        complexity=SimpleNamespace(value=complexity),
        original_question="question",
    )


def _research(
    status="succeeded",
    stop_reason="completed",
):
    return SimpleNamespace(
        status=SimpleNamespace(value=status),
        stop_reason=stop_reason,
        assessment=SimpleNamespace(
            evidence_count=2,
        ),
    )


def _synthesis(
    *,
    status="grounded",
    valid=True,
    answer=("A reserva reduz riscos inesperados. [E1]"),
    failure_reasons=None,
    generated_answer_as_evidence=False,
):
    return SimpleNamespace(
        status=SimpleNamespace(value=status),
        answer=answer,
        validation=SimpleNamespace(
            valid=valid,
            citation_coverage=(1.0 if valid else 0.2),
            groundedness_score=(0.95 if valid else 0.1),
            answer_relevance=0.90,
            failure_reasons=(failure_reasons or []),
        ),
        citations=[
            SimpleNamespace(
                marker="E1",
                references=["reserva-emergencia.md"],
            )
        ],
        evidence_count=2,
        model_executor_used=False,
        metadata={"generated_answer_as_evidence": (generated_answer_as_evidence)},
    )


def test_default_configuration_is_off(
    monkeypatch,
):
    monkeypatch.delenv(
        "INNA_AGENTIC_RAG_MODE",
        raising=False,
    )

    config = load_agentic_rag_gateway_config()

    assert config.mode == AgenticRagMode.OFF


def test_invalid_mode_falls_back_to_off():
    config = load_agentic_rag_gateway_config({"INNA_AGENTIC_RAG_MODE": ("invalid")})

    assert config.mode == AgenticRagMode.OFF

    assert config.configuration_warning == "invalid_mode_fallback_to_off"


def test_off_mode_is_exact_legacy_path():
    state = _state()

    expected = _legacy_node(deepcopy(state))

    result = run_agentic_rag_gateway(
        deepcopy(state),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.OFF,
        ),
        legacy_node=_legacy_node,
    )

    assert result == expected


def test_active_simple_query_uses_legacy():
    research_called = False

    def research_runner(**kwargs):
        nonlocal research_called
        research_called = True
        return _research()

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan("simple"),
        research_runner=research_runner,
    )

    assert result["response"] == ("resposta-legada")

    assert research_called is False

    execution = result["agentic_rag_execution"]

    assert execution["decision"] == (GatewayDecision.LEGACY_SIMPLE_QUERY.value)


def test_active_complex_query_uses_agentic_pipeline():
    captured = {}

    def research_runner(**kwargs):
        captured["research"] = kwargs
        return _research()

    def synthesis_runner(**kwargs):
        captured["synthesis"] = kwargs
        return _synthesis()

    original = _state()
    original_copy = deepcopy(original)

    result = run_agentic_rag_gateway(
        original,
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan("complex"),
        research_runner=research_runner,
        synthesis_runner=synthesis_runner,
    )

    assert original == original_copy

    assert result["response"] == ("A reserva reduz riscos inesperados. [E1]")

    assert result["current_agent"] == ("rag_agent")

    assert result["errors"] == []

    assert result["structured_response"]["agent_response"]["sources"] == [
        "reserva-emergencia.md"
    ]

    assert result["agentic_rag_execution"]["outcome"] == (GatewayOutcome.GROUNDED.value)

    assert captured["research"]["user_id"] == "trusted-user-test"

    assert captured["research"]["session_id"] == "thread-test"

    assert captured["research"]["trace_id"] == "trace-test"


def test_only_cited_sources_are_exposed():
    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: _synthesis(),
    )

    rag_execution = result["structured_response"]["rag_execution"]

    assert rag_execution["sources"] == ["reserva-emergencia.md"]


def test_operational_failure_uses_legacy_fallback():
    def research_runner(**kwargs):
        raise TimeoutError("temporary timeout")

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
            allow_operational_fallback=True,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=research_runner,
    )

    assert result["response"] == ("resposta-legada")

    execution = result["agentic_rag_execution"]

    assert execution["fallback_used"] is True
    assert execution["legacy_response_used"] is True


def test_contract_failure_is_fail_closed():
    legacy_called = False

    def legacy_node(state):
        nonlocal legacy_called
        legacy_called = True
        return _legacy_node(state)

    class ExecutorContractError(RuntimeError):
        pass

    def research_runner(**kwargs):
        raise ExecutorContractError("contract mismatch")

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=research_runner,
    )

    assert legacy_called is False

    assert result["response"] == (
        "Não foi possível concluir esta consulta com segurança neste momento."
    )

    assert result["errors"]

    assert result["agentic_rag_execution"]["outcome"] == (GatewayOutcome.BLOCKED.value)


def test_permission_failure_cannot_bypass_governance():
    def research_runner(**kwargs):
        return _research(
            status="failed",
            stop_reason="permission_denied",
        )

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=research_runner,
    )

    assert result["agentic_rag_fallback_used"] is False

    assert result["agentic_rag_execution"]["outcome"] == "blocked"


def test_quality_rejection_can_use_legacy_fallback():
    rejected = _synthesis(
        status="rejected",
        valid=False,
        answer="",
        failure_reasons=[SimpleNamespace(value=("groundedness_below_threshold"))],
    )

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
            allow_quality_fallback=True,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: rejected,
    )

    assert result["response"] == ("resposta-legada")

    assert result["agentic_rag_execution"]["decision"] == (
        GatewayDecision.LEGACY_QUALITY_FALLBACK.value
    )


def test_unknown_citation_failure_is_blocked():
    rejected = _synthesis(
        status="rejected",
        valid=False,
        answer="",
        failure_reasons=[SimpleNamespace(value="unknown_citations")],
    )

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: rejected,
    )

    assert result["agentic_rag_execution"]["outcome"] == "blocked"

    assert result["agentic_rag_fallback_used"] is False


def test_generated_answer_cannot_become_evidence():
    contaminated = _synthesis(
        generated_answer_as_evidence=True,
    )

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: contaminated,
    )

    assert result["agentic_rag_execution"]["outcome"] == "blocked"


def test_shadow_mode_preserves_legacy_answer():
    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.SHADOW,
            shadow_sample_rate=1.0,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: _synthesis(),
    )

    assert result["response"] == ("resposta-legada")

    execution = result["agentic_rag_execution"]

    assert execution["shadow_execution"] is True

    assert execution["outcome"] == (GatewayOutcome.SHADOW_GROUNDED.value)

    assert execution["legacy_response_used"] is True


def test_shadow_failure_does_not_add_graph_error():
    state = _state()

    result = run_agentic_rag_gateway(
        state,
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.SHADOW,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(
            status="failed",
            stop_reason="timeout",
        ),
    )

    assert result["response"] == ("resposta-legada")

    assert result["errors"] == []

    assert result["agentic_rag_execution"]["outcome"] == (
        GatewayOutcome.SHADOW_FAILED.value
    )


def test_shadow_zero_sample_skips_pipeline():
    plan_called = False

    def plan_factory(*args, **kwargs):
        nonlocal plan_called
        plan_called = True
        return _plan()

    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.SHADOW,
            shadow_sample_rate=0.0,
        ),
        legacy_node=_legacy_node,
        plan_factory=plan_factory,
    )

    assert plan_called is False
    assert result["response"] == ("resposta-legada")

    assert result["agentic_rag_execution"]["decision"] == (
        GatewayDecision.SHADOW_NOT_SELECTED.value
    )


def test_empty_question_uses_legacy():
    state = _state()
    state["user_message"] = " "

    result = run_agentic_rag_gateway(
        state,
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
    )

    assert result["response"] == ("resposta-legada")


def test_question_size_limit_is_applied():
    captured = {}

    def plan_factory(question, **kwargs):
        captured["question"] = question
        return _plan("simple")

    state = _state()
    state["user_message"] = "x" * 1_000

    run_agentic_rag_gateway(
        state,
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
            max_question_chars=100,
        ),
        legacy_node=_legacy_node,
        plan_factory=plan_factory,
    )

    assert len(captured["question"]) == 100


def test_audit_payload_is_sanitized():
    result = run_agentic_rag_gateway(
        _state(),
        config=AgenticRagGatewayConfig(
            mode=AgenticRagMode.ACTIVE,
        ),
        legacy_node=_legacy_node,
        plan_factory=lambda *args, **kwargs: _plan(),
        research_runner=lambda **kwargs: _research(),
        synthesis_runner=lambda **kwargs: _synthesis(),
    )

    audit = agentic_rag_gateway_audit_payload(result)

    serialized = repr(audit)

    assert "trusted-user-test" not in serialized
    assert "thread-test" not in serialized
    assert "question" not in audit
    assert "answer" not in audit
    assert "sources" not in audit
    assert "citations" not in audit
    assert audit["answer_logged"] is False
    assert audit["identity_logged"] is False


def test_graph_uses_gateway_under_preserved_name():
    import src.agents.graph as graph_module

    assert graph_module.rag_agent_node is agentic_rag_gateway_node

    assert graph_module.rag_agent_node.__module__ == (
        "src.agentic_rag.langgraph_integration"
    )


def test_state_declares_agentic_fields():
    from src.agents.state import (
        InnaAgentState,
    )

    annotations = getattr(
        InnaAgentState,
        "__annotations__",
        {},
    )

    assert "trace_id" in annotations
    assert "agentic_rag_mode" in annotations
    assert "agentic_rag_execution" in annotations
    assert "agentic_rag_fallback_used" in annotations


def test_gateway_version_is_professional():
    assert AGENTIC_RAG_GATEWAY_VERSION == "7.0.0"

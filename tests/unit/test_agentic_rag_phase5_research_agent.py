"""
Testes da Fase 5 definitiva:
Research Agent profissional.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from pydantic import ValidationError

import src.agentic_rag.research_agent as research_module

from src.agentic_rag import (
    IterativeResearchAgent,
    ResearchAgentStatus,
    ResearchExecutionPolicy,
    ResearchStopReason,
    RetryDisposition,
    create_research_plan,
    create_runtime_route_executor,
    research_result_to_audit_payload,
    run_research_agent,
)


def _simple_plan():
    return create_research_plan("O que é uma reserva de emergência?")


def _complex_plan():
    return create_research_plan(
        (
            "Compare reserva de emergência e dívidas, "
            "explique os riscos e crie um plano completo."
        )
    )


def _rag_result(
    *,
    step,
    call_id: str,
):
    return SimpleNamespace(
        call_id=call_id,
        tool_name=step.tool_name,
        output={
            "resposta": ("Resposta separada da evidência."),
            "fontes": [f"{step.step_id}_source.md"],
            "contexto_recuperado": [
                (
                    "Evidência verificada diretamente "
                    "relacionada à consulta: " + step.question
                )
            ],
            "documentos_recuperados": 1,
            "modo": "hybrid_rerank",
            "duracao_rag_ms": 10,
        },
        duration_ms=10.0,
        error=None,
    )


def test_complete_research_finishes_in_one_round():
    plan = _complex_plan()

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id=step.step_id,
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="phase5-one-round",
    )

    assert result.status == ResearchAgentStatus.SUCCEEDED
    assert result.stop_reason == ResearchStopReason.SUFFICIENT
    assert len(result.rounds) == 1
    assert result.technical_retry_count == 0
    assert result.total_tool_calls == len(plan.subqueries)


def test_transient_failure_retries_same_round():
    plan = _simple_plan()

    calls = 0

    def executor(
        *,
        step,
        attempt_number,
        **kwargs,
    ):
        nonlocal calls

        calls += 1

        if attempt_number == 1:
            raise TimeoutError("temporary timeout")

        return _rag_result(
            step=step,
            call_id="recovered",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="same-round-retry",
    )

    assert calls == 2
    assert len(result.rounds) == 1
    assert result.total_tool_calls == 2
    assert result.technical_retry_count == 1
    assert result.rounds[0].technical_retry_count == 1
    assert result.status == ResearchAgentStatus.SUCCEEDED
    assert result.metadata["technical_retry_is_semantic_round"] is False


def test_only_failed_step_is_researched_next_round():
    plan = _complex_plan()

    failing_step_id = plan.subqueries[1].step_id

    calls: list[tuple[str, int, int]] = []

    def executor(
        *,
        step,
        round_number,
        attempt_number,
        **kwargs,
    ):
        calls.append(
            (
                step.step_id,
                round_number,
                attempt_number,
            )
        )

        if step.step_id == failing_step_id and round_number == 1:
            raise TimeoutError("temporary dependency failure")

        return _rag_result(
            step=step,
            call_id=(f"{step.step_id}-{round_number}-{attempt_number}"),
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="semantic-retry",
    )

    assert result.status == ResearchAgentStatus.SUCCEEDED
    assert len(result.rounds) == 2
    assert result.total_tool_calls == 4

    first_step_id = plan.subqueries[0].step_id

    assert result.attempted_steps[first_step_id] == 1

    assert result.attempted_steps[failing_step_id] == 3

    assert result.rounds[0].semantic_retry_step_ids == [failing_step_id]


def test_persistent_failure_hits_attempt_limit():
    plan = _simple_plan()

    calls = 0

    def executor(**kwargs):
        nonlocal calls

        calls += 1

        raise TimeoutError("persistent timeout")

    result = run_research_agent(
        plan=plan,
        executor=executor,
        policy=ResearchExecutionPolicy(
            max_rounds=1,
            max_tool_calls=10,
            max_attempts_per_step=2,
        ),
        trace_id="attempt-limit",
    )

    assert calls == 2
    assert result.total_tool_calls == 2
    assert result.technical_retry_count == 1
    assert result.status == ResearchAgentStatus.EXHAUSTED
    assert result.stop_reason == ResearchStopReason.ATTEMPT_LIMIT_REACHED


def test_permission_error_is_not_retried():
    plan = _simple_plan()

    calls = 0

    def executor(**kwargs):
        nonlocal calls

        calls += 1

        raise RuntimeError("permission denied")

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="permission-error",
    )

    assert calls == 1
    assert result.technical_retry_count == 0
    assert len(result.retry_events) == 1
    assert result.retry_events[0].disposition == RetryDisposition.NON_RETRYABLE
    assert result.retry_events[0].retry_scheduled is False


def test_executor_contract_error_fails_closed():
    plan = _simple_plan()

    def executor(first, second):
        return None

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="contract-error",
    )

    assert result.status == ResearchAgentStatus.FAILED
    assert result.stop_reason == ResearchStopReason.EXECUTOR_CONTRACT_ERROR


def test_tool_call_budget_is_enforced():
    plan = _complex_plan()

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="budget",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        policy=ResearchExecutionPolicy(
            max_rounds=1,
            max_tool_calls=1,
            max_attempts_per_step=1,
        ),
        trace_id="budget-limit",
    )

    assert result.total_tool_calls == 1
    assert result.status == ResearchAgentStatus.EXHAUSTED
    assert result.stop_reason == ResearchStopReason.TOOL_CALL_BUDGET_EXHAUSTED


def test_route_count_mismatch_fails_closed(
    monkeypatch,
):
    plan = _simple_plan()

    monkeypatch.setattr(
        research_module,
        "route_research_plan",
        lambda *args, **kwargs: [],
    )

    result = run_research_agent(
        plan=plan,
        executor=lambda route: None,
        trace_id="route-mismatch",
    )

    assert result.status == ResearchAgentStatus.FAILED
    assert result.stop_reason == ResearchStopReason.ROUTING_CONTRACT_ERROR


def test_reported_rate_limit_is_retried():
    plan = _simple_plan()

    calls = 0

    def executor(
        *,
        step,
        **kwargs,
    ):
        nonlocal calls

        calls += 1

        if calls == 1:
            return SimpleNamespace(
                call_id="rate-limit",
                tool_name=step.tool_name,
                output=None,
                duration_ms=1.0,
                error=SimpleNamespace(code="rate_limit"),
            )

        return _rag_result(
            step=step,
            call_id="rate-limit-recovered",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="rate-limit-retry",
    )

    assert calls == 2
    assert result.technical_retry_count == 1
    assert result.status == ResearchAgentStatus.SUCCEEDED


def test_backoff_is_configurable():
    plan = _simple_plan()

    sleeps: list[float] = []

    def executor(
        *,
        step,
        attempt_number,
        **kwargs,
    ):
        if attempt_number == 1:
            raise TimeoutError("timeout")

        return _rag_result(
            step=step,
            call_id="backoff-recovered",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        policy=ResearchExecutionPolicy(
            retry_backoff_ms=100,
            max_retry_backoff_ms=1_000,
        ),
        sleep_fn=sleeps.append,
        trace_id="backoff-test",
    )

    assert sleeps == [0.1]
    assert result.retry_events[0].backoff_ms == 100
    assert result.status == ResearchAgentStatus.SUCCEEDED


def test_audit_payload_is_sanitized():
    plan = _simple_plan()

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="audit",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="audit-test",
    )

    audit = research_result_to_audit_payload(result)

    serialized = repr(audit)

    assert plan.original_question not in serialized
    assert "contexto_recuperado" not in serialized
    assert "_source.md" not in serialized
    assert audit["content_logged"] is False
    assert audit["identity_logged"] is False


def test_runtime_adapter_created_without_call():
    executor = create_runtime_route_executor()

    assert callable(executor)


def test_original_plan_is_not_mutated():
    plan = _complex_plan()

    original = plan.model_dump(mode="python")

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="immutable",
        )

    run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="immutable-test",
    )

    assert plan.model_dump(mode="python") == original


def test_trace_id_is_generated():
    plan = _simple_plan()

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="trace",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
    )

    assert result.trace_id.startswith("research-")


def test_invalid_policy_is_rejected():
    with pytest.raises(
        ValidationError,
    ):
        ResearchExecutionPolicy(
            retry_backoff_ms=2_000,
            max_retry_backoff_ms=1_000,
        )


def test_positional_executor_is_supported():
    plan = _simple_plan()

    step = plan.subqueries[0]

    def executor(route):
        return _rag_result(
            step=step,
            call_id="positional",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        trace_id="positional-test",
    )

    assert result.status == ResearchAgentStatus.SUCCEEDED


def test_object_facade_executes_agent():
    plan = _simple_plan()

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="facade",
        )

    agent = IterativeResearchAgent(
        executor=executor,
        policy=ResearchExecutionPolicy(
            max_rounds=2,
            max_tool_calls=5,
            max_attempts_per_step=2,
        ),
    )

    result = agent.run(
        plan=plan,
        trace_id="facade-test",
    )

    assert result.status == ResearchAgentStatus.SUCCEEDED

    assert result.metadata["research_agent_version"] == "5.1.0"


def test_duration_budget_is_enforced():
    plan = _complex_plan()

    clock_values = iter(
        [
            0.0,
            0.0,
            0.0,
            2.0,
            2.0,
            2.0,
        ]
    )

    def clock():
        return next(
            clock_values,
            2.0,
        )

    def executor(
        *,
        step,
        **kwargs,
    ):
        return _rag_result(
            step=step,
            call_id="duration",
        )

    result = run_research_agent(
        plan=plan,
        executor=executor,
        policy=ResearchExecutionPolicy(
            max_rounds=1,
            max_tool_calls=10,
            max_attempts_per_step=1,
            max_total_duration_ms=100,
        ),
        monotonic_clock=clock,
        trace_id="duration-test",
    )

    assert result.total_tool_calls == 1
    assert result.status == ResearchAgentStatus.EXHAUSTED
    assert result.stop_reason == ResearchStopReason.DURATION_BUDGET_EXHAUSTED


def test_runtime_adapter_propagates_required_context_without_live_call():
    captured = {}

    sentinel_route = object()
    sentinel_tool_executor = object()

    def fake_routed_target(
        route,
        *,
        user_id,
        session_id,
        trace_id,
        executor=None,
    ):
        captured.update(
            {
                "route": route,
                "user_id": user_id,
                "session_id": session_id,
                "trace_id": trace_id,
                "executor": executor,
            }
        )

        return {
            "status": "controlled",
        }

    runtime_executor = create_runtime_route_executor(
        user_id="trusted-user-test",
        session_id="session-test-001",
        trace_id="bound-trace-test",
        tool_executor=(sentinel_tool_executor),
        routed_tool_target=(fake_routed_target),
    )

    result = runtime_executor(
        route=sentinel_route,
        trace_id="invocation-trace-test",
    )

    assert result == {
        "status": "controlled",
    }

    assert captured["route"] is sentinel_route

    assert captured["user_id"] == "trusted-user-test"

    assert captured["session_id"] == "session-test-001"

    assert captured["trace_id"] == "invocation-trace-test"

    assert captured["executor"] is sentinel_tool_executor


def test_runtime_wrapper_uses_same_trace_and_context():
    plan = _simple_plan()
    step = plan.subqueries[0]

    captured = {}

    def fake_routed_target(
        route,
        *,
        user_id,
        session_id,
        trace_id,
        executor=None,
    ):
        captured.update(
            {
                "route": route,
                "user_id": user_id,
                "session_id": session_id,
                "trace_id": trace_id,
                "executor": executor,
            }
        )

        return _rag_result(
            step=step,
            call_id=("runtime-context-contract"),
        )

    result = research_module.run_research_agent_with_runtime(
        plan=plan,
        user_id="trusted-user-runtime",
        session_id="runtime-session-001",
        trace_id="shared-runtime-trace",
        routed_tool_target=(fake_routed_target),
    )

    assert result.status == ResearchAgentStatus.SUCCEEDED

    assert result.runtime_executor_used is True

    assert result.trace_id == "shared-runtime-trace"

    assert captured["user_id"] == "trusted-user-runtime"

    assert captured["session_id"] == "runtime-session-001"

    assert captured["trace_id"] == result.trace_id

    assert captured["route"] is not None


def test_runtime_wrapper_generates_one_shared_trace():
    plan = _simple_plan()
    step = plan.subqueries[0]

    captured = {}

    def fake_routed_target(
        route,
        *,
        user_id,
        session_id,
        trace_id,
        executor=None,
    ):
        captured["trace_id"] = trace_id

        return _rag_result(
            step=step,
            call_id=("generated-shared-trace"),
        )

    result = research_module.run_research_agent_with_runtime(
        plan=plan,
        user_id="trusted-generated-trace",
        session_id=("generated-trace-session"),
        routed_tool_target=(fake_routed_target),
    )

    assert result.trace_id.startswith("research-")

    assert captured["trace_id"] == result.trace_id

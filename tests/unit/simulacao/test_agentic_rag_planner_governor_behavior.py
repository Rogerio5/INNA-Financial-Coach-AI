from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

from src.agentic_rag import planner as planner_module
from src.reliability.distributed_evaluation import (
    DistributedReliabilitySnapshot,
)
from src.reliability.governor import (
    ReliabilityGovernorAction,
    advise_reliability_governor,
)
from src.reliability.production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    evaluate_production_reliability_counts,
)
from src.reliability.shared_provider import (
    ReliabilityDataSource,
)
from src.resilience import (
    ResilienceEventType,
)
from src.resilience.policies import (
    AGENTIC_RAG_PLANNER_POLICY,
)
from src.resilience.runtime import (
    ResilienceRuntime,
)

MASTER_FLAG = (
    "INNA_RELIABILITY_GOVERNOR_"
    "ENFORCEMENT_ENABLED"
)

PLANNER_FLAG = (
    "INNA_RELIABILITY_GOVERNOR_"
    "PLANNER_ENFORCEMENT_ENABLED"
)


def _critical_decision():
    reliability_policy = (
        PRODUCTION_RELIABILITY_POLICIES[
            "rag.agentic.planner"
        ]
    )

    evaluation = (
        evaluate_production_reliability_counts(
            policy=reliability_policy,
            total_operations=100,
            successful_operations=97,
            failed_operations=3,
            circuit_rejections=0,
        )
    )

    snapshot = DistributedReliabilitySnapshot(
        operation="rag.agentic.planner",
        source=(
            ReliabilityDataSource
            .SHARED_CACHE
        ),
        evaluation=evaluation,
        shared_data_used=True,
        provider_enabled=True,
        cache_age_seconds=1.0,
        cache_stale=False,
        database_unavailable=False,
        refresh_in_flight=False,
    )

    return advise_reliability_governor(
        policy=AGENTIC_RAG_PLANNER_POLICY,
        snapshot=snapshot,
    )


def _prepare_real_planner_path(
    monkeypatch,
    *,
    master_enabled: bool,
    planner_enabled: bool,
    governor_decision=None,
    governor_failure: Exception | None = None,
):
    monkeypatch.setenv(
        MASTER_FLAG,
        "true"
        if master_enabled
        else "false",
    )

    monkeypatch.setenv(
        PLANNER_FLAG,
        "true"
        if planner_enabled
        else "false",
    )

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_PLANNER_TIMEOUT_MS",
        "12000",
    )

    monkeypatch.setenv(
        (
            "INNA_AGENTIC_RAG_PLANNER_"
            "TOTAL_DEADLINE_MS"
        ),
        "20000",
    )

    runtime_events = []

    runtime = ResilienceRuntime(
        observer=runtime_events.append,
        sleeper=lambda _: None,
        random_source=lambda: 0.0,
    )

    monkeypatch.setattr(
        "src.observability.resilience_tracing."
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    traced_policies = []

    @contextmanager
    def fake_trace(policy):
        traced_policies.append(
            policy
        )
        yield None

    monkeypatch.setattr(
        "src.observability.resilience_tracing."
        "traced_resilience_operation",
        fake_trace,
    )

    monkeypatch.setattr(
        "src.agents.supervisor_config."
        "get_gemini_api_key",
        lambda: "unit-test-key",
    )

    monkeypatch.setattr(
        "src.agents.supervisor_config."
        "get_supervisor_runtime_config",
        lambda: SimpleNamespace(
            model="gemini-test-model"
        ),
    )

    # Evita construção de cliente Gemini real.
    monkeypatch.setattr(
        "google.genai.Client",
        lambda **_: object(),
    )

    # Se qualquer código tentar buscar a janela
    # diretamente no PostgreSQL, o teste falha.
    def forbidden_database_io(*args, **kwargs):
        raise AssertionError(
            "synchronous Reliability database "
            "I/O is forbidden in Planner path"
        )

    monkeypatch.setattr(
        "src.reliability.repository."
        "load_production_reliability_window",
        forbidden_database_io,
    )

    if governor_failure is not None:
        def broken_governor(*args, **kwargs):
            raise governor_failure

        monkeypatch.setattr(
            "src.reliability.governor."
            "get_reliability_governor_decision",
            broken_governor,
        )

    elif governor_decision is not None:
        monkeypatch.setattr(
            "src.reliability.governor."
            "get_reliability_governor_decision",
            lambda operation: governor_decision,
        )

    else:
        # Enforcement OFF deve impedir qualquer
        # consulta ao Governor.
        def forbidden_governor(*args, **kwargs):
            raise AssertionError(
                "Governor must not execute "
                "while enforcement is disabled"
            )

        monkeypatch.setattr(
            "src.reliability.governor."
            "get_reliability_governor_decision",
            forbidden_governor,
        )

    return (
        runtime,
        runtime_events,
        traced_policies,
    )


def _attempt_events(events):
    return [
        event
        for event in events
        if (
            event.event_type
            is ResilienceEventType
            .ATTEMPT_STARTED
        )
    ]


def _assert_real_fallback(plan):
    generation_mode = getattr(
        plan.generation_mode,
        "value",
        plan.generation_mode,
    )

    assert (
        str(generation_mode)
        == "fallback"
    )

    assert (
        plan.metadata.get(
            "planner"
        )
        == "deterministic_after_llm_failure"
    )


def test_enforcement_off_uses_two_attempts_then_real_fallback(
    monkeypatch,
):
    (
        _runtime,
        events,
        traced_policies,
    ) = _prepare_real_planner_path(
        monkeypatch,
        master_enabled=False,
        planner_enabled=False,
    )

    provider_calls = 0

    def provider_failure(
        *args,
        **kwargs,
    ):
        nonlocal provider_calls

        provider_calls += 1

        raise TimeoutError(
            "simulated transient planner timeout"
        )

    monkeypatch.setattr(
        "src.observability.llm_tracking."
        "executar_generate_content_observado",
        provider_failure,
    )

    plan = (
        planner_module.create_research_plan(
            "Como organizar meu orçamento mensal?",
            language="pt",
            planner_mode="llm",
        )
    )

    attempts = _attempt_events(
        events
    )

    assert provider_calls == 2
    assert len(attempts) == 2

    assert all(
        event.max_attempts == 2
        for event in attempts
    )

    assert len(traced_policies) == 1

    assert (
        traced_policies[0]
        is AGENTIC_RAG_PLANNER_POLICY
    )

    assert (
        traced_policies[0]
        .max_attempts
        == 2
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )

    _assert_real_fallback(
        plan
    )


def test_critical_enforcement_reduces_two_to_one_then_fallback(
    monkeypatch,
):
    decision = (
        _critical_decision()
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    assert (
        decision.recommended_max_attempts
        == 1
    )

    # Nesta fase isto continua sendo apenas
    # preferência advisory, sem bypass direto.
    assert decision.prefer_fallback

    (
        _runtime,
        events,
        traced_policies,
    ) = _prepare_real_planner_path(
        monkeypatch,
        master_enabled=True,
        planner_enabled=True,
        governor_decision=decision,
    )

    provider_calls = 0

    def provider_failure(
        *args,
        **kwargs,
    ):
        nonlocal provider_calls

        provider_calls += 1

        raise TimeoutError(
            "simulated transient planner timeout"
        )

    monkeypatch.setattr(
        "src.observability.llm_tracking."
        "executar_generate_content_observado",
        provider_failure,
    )

    plan = (
        planner_module.create_research_plan(
            "Como organizar meu orçamento mensal?",
            language="pt",
            planner_mode="llm",
        )
    )

    attempts = _attempt_events(
        events
    )

    # A prova principal da 3F.4C.
    assert provider_calls == 1
    assert len(attempts) == 1

    assert (
        attempts[0].max_attempts
        == 1
    )

    assert len(traced_policies) == 1

    effective = (
        traced_policies[0]
    )

    assert (
        effective
        is not AGENTIC_RAG_PLANNER_POLICY
    )

    assert (
        effective.name
        == AGENTIC_RAG_PLANNER_POLICY.name
    )

    assert effective.max_attempts == 1

    # Base global continua imutável.
    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )

    # prefer_fallback não fez short-circuit:
    # uma tentativa ao provider realmente ocorreu.
    assert provider_calls == 1

    _assert_real_fallback(
        plan
    )


def test_governor_failure_fails_open_to_base_two_attempts(
    monkeypatch,
):
    (
        _runtime,
        events,
        traced_policies,
    ) = _prepare_real_planner_path(
        monkeypatch,
        master_enabled=True,
        planner_enabled=True,
        governor_failure=RuntimeError(
            "simulated Governor failure"
        ),
    )

    provider_calls = 0

    def provider_failure(
        *args,
        **kwargs,
    ):
        nonlocal provider_calls

        provider_calls += 1

        raise TimeoutError(
            "simulated transient planner timeout"
        )

    monkeypatch.setattr(
        "src.observability.llm_tracking."
        "executar_generate_content_observado",
        provider_failure,
    )

    plan = (
        planner_module.create_research_plan(
            "Como organizar meu orçamento mensal?",
            language="pt",
            planner_mode="llm",
        )
    )

    attempts = _attempt_events(
        events
    )

    assert provider_calls == 2
    assert len(attempts) == 2

    assert all(
        event.max_attempts == 2
        for event in attempts
    )

    assert len(traced_policies) == 1

    assert (
        traced_policies[0]
        is AGENTIC_RAG_PLANNER_POLICY
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )

    _assert_real_fallback(
        plan
    )


def test_planner_gate_off_blocks_governor_even_with_master_on(
    monkeypatch,
):
    (
        _runtime,
        events,
        traced_policies,
    ) = _prepare_real_planner_path(
        monkeypatch,
        master_enabled=True,
        planner_enabled=False,
    )

    provider_calls = 0

    def provider_failure(
        *args,
        **kwargs,
    ):
        nonlocal provider_calls

        provider_calls += 1

        raise TimeoutError(
            "simulated transient planner timeout"
        )

    monkeypatch.setattr(
        "src.observability.llm_tracking."
        "executar_generate_content_observado",
        provider_failure,
    )

    plan = (
        planner_module.create_research_plan(
            "Como organizar meu orçamento mensal?",
            language="pt",
            planner_mode="llm",
        )
    )

    attempts = _attempt_events(
        events
    )

    assert provider_calls == 2
    assert len(attempts) == 2

    assert (
        traced_policies[0]
        is AGENTIC_RAG_PLANNER_POLICY
    )

    _assert_real_fallback(
        plan
    )


def test_behavior_proof_does_not_mutate_base_policy():
    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .name
        == "rag.agentic.planner"
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )

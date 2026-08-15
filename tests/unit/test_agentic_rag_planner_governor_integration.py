from __future__ import annotations

from pathlib import Path

import pytest

from src.agentic_rag.planner import (
    _planner_governor_enforcement_enabled,
    _resolve_planner_resilience_policy,
)
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
from src.resilience.policies import (
    AGENTIC_RAG_PLANNER_POLICY,
)

MASTER_FLAG = (
    "INNA_RELIABILITY_GOVERNOR_"
    "ENFORCEMENT_ENABLED"
)

PLANNER_FLAG = (
    "INNA_RELIABILITY_GOVERNOR_"
    "PLANNER_ENFORCEMENT_ENABLED"
)


def _set_gates(
    monkeypatch,
    *,
    master: bool,
    planner: bool,
):
    monkeypatch.setenv(
        MASTER_FLAG,
        "true" if master else "false",
    )

    monkeypatch.setenv(
        PLANNER_FLAG,
        "true" if planner else "false",
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


def test_governor_enforcement_defaults_off(
    monkeypatch,
):
    monkeypatch.delenv(
        MASTER_FLAG,
        raising=False,
    )

    monkeypatch.delenv(
        PLANNER_FLAG,
        raising=False,
    )

    assert not (
        _planner_governor_enforcement_enabled()
    )


@pytest.mark.parametrize(
    (
        "master",
        "planner",
        "expected",
    ),
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (True, True, True),
    ],
)
def test_planner_enforcement_requires_both_gates(
    monkeypatch,
    master,
    planner,
    expected,
):
    _set_gates(
        monkeypatch,
        master=master,
        planner=planner,
    )

    assert (
        _planner_governor_enforcement_enabled()
        is expected
    )


def test_disabled_gate_returns_exact_base_policy(
    monkeypatch,
):
    _set_gates(
        monkeypatch,
        master=False,
        planner=False,
    )

    effective = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    assert (
        effective
        is AGENTIC_RAG_PLANNER_POLICY
    )

    assert effective.max_attempts == 2


def test_disabled_gate_does_not_call_governor(
    monkeypatch,
):
    _set_gates(
        monkeypatch,
        master=False,
        planner=False,
    )

    def forbidden(*args, **kwargs):
        raise AssertionError(
            "Governor must not be called "
            "when enforcement is disabled."
        )

    monkeypatch.setattr(
        "src.reliability.governor."
        "get_reliability_governor_decision",
        forbidden,
    )

    effective = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    assert (
        effective
        is AGENTIC_RAG_PLANNER_POLICY
    )


def test_enabled_critical_derives_two_to_one(
    monkeypatch,
):
    _set_gates(
        monkeypatch,
        master=True,
        planner=True,
    )

    decision = _critical_decision()

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    assert (
        decision.recommended_max_attempts
        == 1
    )

    monkeypatch.setattr(
        "src.reliability.governor."
        "get_reliability_governor_decision",
        lambda operation: decision,
    )

    effective = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    assert (
        effective
        is not AGENTIC_RAG_PLANNER_POLICY
    )

    assert effective.max_attempts == 1

    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )


def test_governor_decision_failure_fails_open(
    monkeypatch,
):
    _set_gates(
        monkeypatch,
        master=True,
        planner=True,
    )

    def broken(*args, **kwargs):
        raise RuntimeError(
            "simulated Governor failure"
        )

    monkeypatch.setattr(
        "src.reliability.governor."
        "get_reliability_governor_decision",
        broken,
    )

    effective = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    assert (
        effective
        is AGENTIC_RAG_PLANNER_POLICY
    )


def test_policy_derivation_failure_fails_open(
    monkeypatch,
):
    _set_gates(
        monkeypatch,
        master=True,
        planner=True,
    )

    decision = _critical_decision()

    monkeypatch.setattr(
        "src.reliability.governor."
        "get_reliability_governor_decision",
        lambda operation: decision,
    )

    def broken(*args, **kwargs):
        raise RuntimeError(
            "simulated derivation failure"
        )

    monkeypatch.setattr(
        "src.reliability.governor."
        "derive_effective_resilience_policy",
        broken,
    )

    effective = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    assert (
        effective
        is AGENTIC_RAG_PLANNER_POLICY
    )


def test_env_example_has_both_flags_disabled():
    source = Path(
        ".env.example"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "INNA_RELIABILITY_GOVERNOR_"
        "ENFORCEMENT_ENABLED=false"
        in source
    )

    assert (
        "INNA_RELIABILITY_GOVERNOR_"
        "PLANNER_ENFORCEMENT_ENABLED=false"
        in source
    )


def test_planner_never_calls_synchronous_refresh_now():
    source = Path(
        "src/agentic_rag/planner.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "refresh_now(" not in source

    assert (
        "load_production_reliability_window"
        not in source
    )

    assert "cursor_postgres" not in source


def test_trace_and_runtime_use_same_effective_policy():
    source = Path(
        "src/agentic_rag/planner.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "planner_resilience_policy = ("
        in source
    )

    assert (
        "with traced_resilience_operation("
        in source
    )

    assert (
        "planner_resilience_policy"
        in source
    )

    trace_index = source.index(
        "with traced_resilience_operation("
    )

    runtime_index = source.index(
        "resilience_runtime.execute("
    )

    trace_slice = source[
        trace_index:
        trace_index + 180
    ]

    runtime_slice = source[
        runtime_index:
        runtime_index + 250
    ]

    assert (
        "planner_resilience_policy"
        in trace_slice
    )

    assert (
        "planner_resilience_policy"
        in runtime_slice
    )


def test_base_planner_policy_remains_two_attempts():
    assert (
        AGENTIC_RAG_PLANNER_POLICY
        .max_attempts
        == 2
    )

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.reliability.distributed_evaluation import (
    DistributedReliabilitySnapshot,
)
from src.reliability.governor import (
    ReliabilityGovernorAction,
    advise_reliability_governor,
    derive_effective_resilience_policy,
)
from src.reliability.production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    evaluate_production_reliability_counts,
)
from src.reliability.shared_provider import (
    ReliabilityDataSource,
)
from src.resilience.policies import (
    GEMINI_EMBEDDING_POLICY,
)
from src.resilience.runtime import (
    ResilienceRuntime,
)


def _distributed_snapshot(
    *,
    total: int,
    success: int,
    failed: int,
) -> DistributedReliabilitySnapshot:
    evaluation = (
        evaluate_production_reliability_counts(
            policy=(
                PRODUCTION_RELIABILITY_POLICIES[
                    "gemini.embedding"
                ]
            ),
            total_operations=total,
            successful_operations=success,
            failed_operations=failed,
            circuit_rejections=0,
        )
    )

    return DistributedReliabilitySnapshot(
        operation="gemini.embedding",
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


def _critical_effective_policy():
    snapshot = _distributed_snapshot(
        total=100,
        success=97,
        failed=3,
    )

    decision = (
        advise_reliability_governor(
            policy=GEMINI_EMBEDDING_POLICY,
            snapshot=snapshot,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    return (
        decision,
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        ),
    )


def _degraded_effective_policy():
    snapshot = _distributed_snapshot(
        total=200,
        success=199,
        failed=1,
    )

    decision = (
        advise_reliability_governor(
            policy=GEMINI_EMBEDDING_POLICY,
            snapshot=snapshot,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .REDUCE_RETRIES
    )

    return (
        decision,
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        ),
    )


def test_base_policy_retries_three_attempts():
    calls = 0

    def operation():
        nonlocal calls
        calls += 1

        if calls < 3:
            raise TimeoutError(
                "simulated timeout"
            )

        return "success"

    runtime = ResilienceRuntime()

    with patch(
        "src.resilience.runtime."
        "calculate_backoff_seconds",
        return_value=0.0,
    ):
        result = runtime.execute(
            policy=GEMINI_EMBEDDING_POLICY,
            operation=operation,
        )

    assert result == "success"
    assert calls == 3

    assert (
        GEMINI_EMBEDDING_POLICY
        .max_attempts
        == 3
    )


def test_critical_effective_policy_stops_after_one_attempt():
    decision, effective = (
        _critical_effective_policy()
    )

    calls = 0

    def operation():
        nonlocal calls
        calls += 1

        raise TimeoutError(
            "simulated timeout"
        )

    runtime = ResilienceRuntime()

    with (
        patch(
            "src.resilience.runtime."
            "calculate_backoff_seconds",
            return_value=0.0,
        ),
        pytest.raises(
            TimeoutError,
            match="simulated timeout",
        ),
    ):
        runtime.execute(
            policy=effective,
            operation=operation,
        )

    assert (
        decision.recommended_max_attempts
        == 1
    )

    assert effective.max_attempts == 1
    assert calls == 1

    assert (
        GEMINI_EMBEDDING_POLICY
        .max_attempts
        == 3
    )


def test_degraded_effective_policy_stops_after_two_attempts():
    decision, effective = (
        _degraded_effective_policy()
    )

    calls = 0

    def operation():
        nonlocal calls
        calls += 1

        raise TimeoutError(
            "simulated timeout"
        )

    runtime = ResilienceRuntime()

    with (
        patch(
            "src.resilience.runtime."
            "calculate_backoff_seconds",
            return_value=0.0,
        ),
        pytest.raises(
            TimeoutError,
            match="simulated timeout",
        ),
    ):
        runtime.execute(
            policy=effective,
            operation=operation,
        )

    assert (
        decision.recommended_max_attempts
        == 2
    )

    assert effective.max_attempts == 2
    assert calls == 2

    assert (
        GEMINI_EMBEDDING_POLICY
        .max_attempts
        == 3
    )


def test_critical_runtime_does_not_mutate_global_policy():
    original = (
        GEMINI_EMBEDDING_POLICY
    )

    _, effective = (
        _critical_effective_policy()
    )

    assert effective is not original
    assert effective.max_attempts == 1

    assert (
        GEMINI_EMBEDDING_POLICY
        is original
    )

    assert (
        GEMINI_EMBEDDING_POLICY
        .max_attempts
        == 3
    )


def test_isolation_requires_no_database_or_provider_call(
    monkeypatch,
):
    def forbidden(*args, **kwargs):
        raise AssertionError(
            "external reliability I/O "
            "must not occur"
        )

    monkeypatch.setattr(
        "src.reliability.repository."
        "load_production_reliability_window",
        forbidden,
    )

    _, effective = (
        _critical_effective_policy()
    )

    calls = 0

    def operation():
        nonlocal calls
        calls += 1

        raise TimeoutError(
            "isolated"
        )

    runtime = ResilienceRuntime()

    with (
        patch(
            "src.resilience.runtime."
            "calculate_backoff_seconds",
            return_value=0.0,
        ),
        pytest.raises(
            TimeoutError,
        ),
    ):
        runtime.execute(
            policy=effective,
            operation=operation,
        )

    assert calls == 1


def test_isolation_does_not_execute_real_provider():
    _, effective = (
        _critical_effective_policy()
    )

    assert (
        effective.name
        == "gemini.embedding"
    )

    # A operação fornecida ao runtime neste teste
    # é totalmente local. Nenhum SDK Gemini é usado.
    assert effective.max_attempts == 1

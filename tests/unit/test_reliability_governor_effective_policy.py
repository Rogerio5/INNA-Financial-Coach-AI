from __future__ import annotations

from dataclasses import (
    FrozenInstanceError,
    asdict,
    replace,
)

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
from src.resilience import FailureKind
from src.resilience.policies import (
    AGENTIC_RAG_PLANNER_POLICY,
    GEMINI_EMBEDDING_POLICY,
    GEMINI_TEXT_GENERATION_POLICY,
    SUPERVISOR_GENERATION_POLICY,
)


def _snapshot(
    operation,
    *,
    total,
    success,
    failed,
    shared=True,
):
    evaluation = (
        evaluate_production_reliability_counts(
            policy=(
                PRODUCTION_RELIABILITY_POLICIES[
                    operation
                ]
            ),
            total_operations=total,
            successful_operations=success,
            failed_operations=failed,
            circuit_rejections=0,
        )
    )

    return DistributedReliabilitySnapshot(
        operation=operation,
        source=(
            ReliabilityDataSource.SHARED_CACHE
            if shared
            else ReliabilityDataSource.LOCAL_FALLBACK
        ),
        evaluation=evaluation,
        shared_data_used=shared,
        provider_enabled=True,
        cache_age_seconds=1.0,
        cache_stale=False,
        database_unavailable=False,
        refresh_in_flight=False,
    )


def _decision(
    policy,
    *,
    total,
    success,
    failed,
    shared=True,
):
    return advise_reliability_governor(
        policy=policy,
        snapshot=_snapshot(
            policy.name,
            total=total,
            success=success,
            failed=failed,
            shared=shared,
        ),
    )


def test_healthy_returns_original_policy():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=100,
        failed=0,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .KEEP_CURRENT
    )

    assert (
        effective
        is GEMINI_EMBEDDING_POLICY
    )


def test_local_critical_keeps_original_policy():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
        shared=False,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .KEEP_CURRENT
    )

    assert (
        effective
        is GEMINI_EMBEDDING_POLICY
    )


def test_degraded_embedding_derives_3_to_2():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=200,
        success=199,
        failed=1,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .REDUCE_RETRIES
    )

    assert (
        effective
        is not GEMINI_EMBEDDING_POLICY
    )

    assert GEMINI_EMBEDDING_POLICY.max_attempts == 3
    assert effective.max_attempts == 2


def test_critical_embedding_derives_3_to_1():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    assert GEMINI_EMBEDDING_POLICY.max_attempts == 3
    assert effective.max_attempts == 1


@pytest.mark.parametrize(
    "policy",
    [
        GEMINI_TEXT_GENERATION_POLICY,
        SUPERVISOR_GENERATION_POLICY,
        AGENTIC_RAG_PLANNER_POLICY,
    ],
)
def test_degraded_two_attempt_policy_derives_to_one(
    policy,
):
    decision = _decision(
        policy,
        total=200,
        success=199,
        failed=1,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=policy,
            decision=decision,
        )
    )

    assert policy.max_attempts == 2
    assert effective.max_attempts == 1


def test_only_max_attempts_changes():
    base = GEMINI_EMBEDDING_POLICY

    decision = _decision(
        base,
        total=100,
        success=97,
        failed=3,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=base,
            decision=decision,
        )
    )

    base_data = asdict(
        base
    )

    expected = dict(
        base_data
    )

    expected[
        "max_attempts"
    ] = 1

    assert (
        asdict(effective)
        == expected
    )

    assert (
        asdict(base)
        == base_data
    )


def test_derived_policy_remains_frozen():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        effective.max_attempts = 99


def test_critical_effective_policy_disables_retry_after_first_attempt():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert (
        GEMINI_EMBEDDING_POLICY
        .allows_retry(
            failure_kind=FailureKind.TIMEOUT,
            attempt_number=1,
        )
    )

    assert not effective.allows_retry(
        failure_kind=FailureKind.TIMEOUT,
        attempt_number=1,
    )


def test_degraded_effective_policy_reduces_retry_budget():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=200,
        success=199,
        failed=1,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )
    )

    assert effective.max_attempts == 2

    assert effective.allows_retry(
        failure_kind=FailureKind.TIMEOUT,
        attempt_number=1,
    )

    assert not effective.allows_retry(
        failure_kind=FailureKind.TIMEOUT,
        attempt_number=2,
    )

    assert (
        GEMINI_EMBEDDING_POLICY
        .allows_retry(
            failure_kind=FailureKind.TIMEOUT,
            attempt_number=2,
        )
    )


def test_planner_fallback_preference_is_not_executed_here():
    decision = _decision(
        AGENTIC_RAG_PLANNER_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    effective = (
        derive_effective_resilience_policy(
            policy=(
                AGENTIC_RAG_PLANNER_POLICY
            ),
            decision=decision,
        )
    )

    assert decision.prefer_fallback
    assert effective.max_attempts == 1

    # Derivation modifica apenas policy.
    assert (
        effective.name
        == AGENTIC_RAG_PLANNER_POLICY.name
    )


def test_retry_expansion_is_rejected():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    invalid = replace(
        decision,
        recommended_max_attempts=4,
    )

    with pytest.raises(
        ValueError,
        match="expand",
    ):
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=invalid,
        )


def test_current_attempt_mismatch_is_rejected():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    invalid = replace(
        decision,
        current_max_attempts=2,
    )

    with pytest.raises(
        ValueError,
        match="current attempts",
    ):
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=invalid,
        )


def test_operation_mismatch_is_rejected():
    decision = _decision(
        GEMINI_TEXT_GENERATION_POLICY,
        total=100,
        success=97,
        failed=3,
    )

    with pytest.raises(
        ValueError,
        match="operation mismatch",
    ):
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=decision,
        )


def test_tampered_local_reduction_is_rejected():
    decision = _decision(
        GEMINI_EMBEDDING_POLICY,
        total=100,
        success=97,
        failed=3,
        shared=False,
    )

    invalid = replace(
        decision,
        action=(
            ReliabilityGovernorAction
            .CONSERVATIVE_MODE
        ),
        recommended_max_attempts=1,
    )

    with pytest.raises(
        ValueError,
        match="shared",
    ):
        derive_effective_resilience_policy(
            policy=GEMINI_EMBEDDING_POLICY,
            decision=invalid,
        )

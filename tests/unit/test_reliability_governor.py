from __future__ import annotations

from dataclasses import replace

import pytest

from src.reliability.distributed_evaluation import (
    DistributedReliabilitySnapshot,
)
from src.reliability.governor import (
    GOVERNED_RESILIENCE_POLICIES,
    ReliabilityGovernorAction,
    advise_reliability_governor,
    get_reliability_governor_decision,
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
    GEMINI_EMBEDDING_POLICY,
    GEMINI_TEXT_GENERATION_POLICY,
)


def _evaluation(
    operation,
    *,
    total,
    success,
    failed,
    circuits=0,
):
    policy = (
        PRODUCTION_RELIABILITY_POLICIES[
            operation
        ]
    )

    return (
        evaluate_production_reliability_counts(
            policy=policy,
            total_operations=total,
            successful_operations=success,
            failed_operations=failed,
            circuit_rejections=circuits,
        )
    )


def _distributed(
    operation,
    *,
    total,
    success,
    failed,
    circuits=0,
    shared=True,
    stale=False,
    unavailable=False,
):
    evaluation = _evaluation(
        operation,
        total=total,
        success=success,
        failed=failed,
        circuits=circuits,
    )

    source = (
        ReliabilityDataSource.SHARED_CACHE
        if shared
        else ReliabilityDataSource.LOCAL_FALLBACK
    )

    return DistributedReliabilitySnapshot(
        operation=operation,
        source=source,
        evaluation=evaluation,
        shared_data_used=shared,
        provider_enabled=True,
        cache_age_seconds=(
            6.0
            if stale
            else 1.0
        ),
        cache_stale=stale,
        database_unavailable=unavailable,
        refresh_in_flight=False,
    )


def test_governed_policy_set_is_exact():
    assert set(
        GOVERNED_RESILIENCE_POLICIES
    ) == {
        "gemini.embedding",
        "gemini.generate.supervisor",
        "gemini.generate.text_service",
        "rag.agentic.planner",
    }


def test_shared_healthy_keeps_embedding_policy():
    snapshot = _distributed(
        "gemini.embedding",
        total=100,
        success=100,
        failed=0,
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
        .KEEP_CURRENT
    )

    assert decision.current_max_attempts == 3
    assert decision.recommended_max_attempts == 3
    assert not decision.prefer_fallback
    assert decision.advisory_only


def test_shared_degraded_reduces_embedding_3_to_2():
    snapshot = _distributed(
        "gemini.embedding",
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

    assert decision.current_max_attempts == 3
    assert decision.recommended_max_attempts == 2


def test_shared_degraded_reduces_text_2_to_1():
    snapshot = _distributed(
        "gemini.generate.text_service",
        total=200,
        success=199,
        failed=1,
    )

    decision = (
        advise_reliability_governor(
            policy=GEMINI_TEXT_GENERATION_POLICY,
            snapshot=snapshot,
        )
    )

    assert decision.current_max_attempts == 2
    assert decision.recommended_max_attempts == 1


def test_shared_critical_embedding_becomes_conservative():
    snapshot = _distributed(
        "gemini.embedding",
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

    assert decision.recommended_max_attempts == 1
    assert not decision.prefer_fallback


def test_planner_critical_prefers_explicit_safe_fallback():
    snapshot = _distributed(
        "rag.agentic.planner",
        total=100,
        success=97,
        failed=3,
    )

    decision = (
        advise_reliability_governor(
            policy=AGENTIC_RAG_PLANNER_POLICY,
            snapshot=snapshot,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    assert decision.recommended_max_attempts == 1
    assert decision.prefer_fallback


def test_stale_shared_critical_remains_advisory_conservative():
    snapshot = _distributed(
        "rag.agentic.planner",
        total=100,
        success=97,
        failed=3,
        stale=True,
        unavailable=True,
    )

    decision = (
        advise_reliability_governor(
            policy=AGENTIC_RAG_PLANNER_POLICY,
            snapshot=snapshot,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    )

    assert decision.cache_stale
    assert decision.database_unavailable
    assert decision.advisory_only


def test_local_critical_never_triggers_global_aggressive_action():
    snapshot = _distributed(
        "gemini.embedding",
        total=100,
        success=97,
        failed=3,
        shared=False,
        unavailable=True,
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
        .KEEP_CURRENT
    )

    assert decision.recommended_max_attempts == 3
    assert not decision.prefer_fallback

    assert (
        decision.reason_code
        == "local_fallback_no_aggressive_action"
    )


def test_shared_insufficient_data_keeps_current():
    snapshot = _distributed(
        "gemini.embedding",
        total=10,
        success=9,
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
        .KEEP_CURRENT
    )

    assert decision.recommended_max_attempts == 3

    assert (
        decision.reason_code
        == "insufficient_data_no_aggressive_action"
    )


def test_governor_does_not_mutate_base_policy():
    before = GEMINI_EMBEDDING_POLICY

    snapshot = _distributed(
        "gemini.embedding",
        total=100,
        success=97,
        failed=3,
    )

    decision = (
        advise_reliability_governor(
            policy=before,
            snapshot=snapshot,
        )
    )

    assert decision.recommended_max_attempts == 1

    assert (
        GEMINI_EMBEDDING_POLICY
        is before
    )

    assert (
        GEMINI_EMBEDDING_POLICY.max_attempts
        == 3
    )


def test_operation_mismatch_is_rejected():
    snapshot = _distributed(
        "gemini.embedding",
        total=100,
        success=100,
        failed=0,
    )

    with pytest.raises(
        ValueError,
        match="operation mismatch",
    ):
        advise_reliability_governor(
            policy=GEMINI_TEXT_GENERATION_POLICY,
            snapshot=snapshot,
        )


def test_inconsistent_shared_metadata_is_rejected():
    snapshot = _distributed(
        "gemini.embedding",
        total=100,
        success=100,
        failed=0,
    )

    inconsistent = replace(
        snapshot,
        shared_data_used=False,
    )

    with pytest.raises(
        ValueError,
        match="inconsistent",
    ):
        advise_reliability_governor(
            policy=GEMINI_EMBEDDING_POLICY,
            snapshot=inconsistent,
        )


def test_getter_accepts_precomputed_snapshot_without_io():
    snapshot = _distributed(
        "gemini.embedding",
        total=200,
        success=199,
        failed=1,
    )

    decision = (
        get_reliability_governor_decision(
            "gemini.embedding",
            snapshot=snapshot,
        )
    )

    assert (
        decision.action
        is ReliabilityGovernorAction
        .REDUCE_RETRIES
    )


def test_safe_decision_has_no_sensitive_content():
    snapshot = _distributed(
        "gemini.embedding",
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

    rendered = repr(
        decision.to_safe_dict()
    ).lower()

    forbidden = {
        "prompt",
        "response",
        "payload",
        "api_key",
        "password",
        "database_url",
        "user_id",
        "chat_id",
        "error_message",
    }

    for field in forbidden:
        assert field not in rendered

from __future__ import annotations

import pytest

from src.reliability.distributed_evaluation import (
    evaluate_distributed_reliability,
    get_distributed_reliability_snapshot,
)
from src.reliability.production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    OperationalBurnSeverity,
    OperationalReliabilityState,
    evaluate_production_reliability_counts,
)
from src.reliability.repository import (
    ProductionReliabilityWindow,
)
from src.reliability.shared_provider import (
    ReliabilityDataSource,
    SharedReliabilitySnapshot,
)

POLICY = (
    PRODUCTION_RELIABILITY_POLICIES[
        "gemini.embedding"
    ]
)


def _local(
    *,
    total=20,
    success=20,
    failed=0,
    circuits=0,
):
    return (
        evaluate_production_reliability_counts(
            policy=POLICY,
            total_operations=total,
            successful_operations=success,
            failed_operations=failed,
            circuit_rejections=circuits,
        )
    )


def _window(
    *,
    operation="gemini.embedding",
    window_seconds=900.0,
    total=20,
    success=20,
    failed=0,
    circuits=0,
):
    return ProductionReliabilityWindow(
        operation=operation,
        window_seconds=window_seconds,
        total_operations=total,
        successful_operations=success,
        failed_operations=failed,
        circuit_rejections=circuits,
        first_occurred_at=None,
        last_occurred_at=None,
    )


def _shared(
    *,
    source=(
        ReliabilityDataSource
        .SHARED_CACHE
    ),
    local=None,
    window=None,
    stale=False,
    unavailable=False,
):
    if local is None:
        local = _local()

    if (
        window is None
        and source
        is ReliabilityDataSource.SHARED_CACHE
    ):
        window = _window()

    return SharedReliabilitySnapshot(
        operation="gemini.embedding",
        source=source,
        provider_enabled=True,
        local_snapshot=local,
        shared_window=window,
        cache_age_seconds=(
            6.0
            if stale
            else 1.0
        ),
        cache_stale=stale,
        database_unavailable=unavailable,
        refresh_in_flight=False,
    )


def test_shared_window_is_evaluated_by_common_evaluator():
    result = (
        evaluate_distributed_reliability(
            _shared(
                window=_window(
                    total=200,
                    success=198,
                    failed=2,
                )
            )
        )
    )

    assert result.shared_data_used

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    assert (
        result.state
        is OperationalReliabilityState
        .DEGRADED
    )

    assert (
        result.burn_severity
        is OperationalBurnSeverity
        .WARNING
    )

    assert result.burn_rate == pytest.approx(
        2.0
    )


def test_shared_critical_overrides_healthy_local():
    local = _local(
        total=100,
        success=100,
        failed=0,
    )

    result = (
        evaluate_distributed_reliability(
            _shared(
                local=local,
                window=_window(
                    total=100,
                    success=97,
                    failed=3,
                    circuits=1,
                ),
            )
        )
    )

    assert (
        local.state
        is OperationalReliabilityState
        .HEALTHY
    )

    assert (
        result.state
        is OperationalReliabilityState
        .CRITICAL
    )

    assert result.shared_data_used


def test_same_counts_have_local_distributed_parity():
    local = _local(
        total=200,
        success=198,
        failed=2,
        circuits=1,
    )

    result = (
        evaluate_distributed_reliability(
            _shared(
                local=local,
                window=_window(
                    total=200,
                    success=198,
                    failed=2,
                    circuits=1,
                ),
            )
        )
    )

    assert (
        result.evaluation
        == local
    )


def test_stale_but_usable_shared_cache_remains_shared():
    result = (
        evaluate_distributed_reliability(
            _shared(
                stale=True,
                unavailable=True,
                window=_window(
                    total=100,
                    success=99,
                    failed=1,
                ),
            )
        )
    )

    assert result.shared_data_used
    assert result.cache_stale
    assert result.database_unavailable

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )


def test_local_fallback_preserves_local_evaluation():
    local = _local(
        total=10,
        success=9,
        failed=1,
    )

    shared = _shared(
        source=(
            ReliabilityDataSource
            .LOCAL_FALLBACK
        ),
        local=local,
        window=None,
        stale=True,
        unavailable=True,
    )

    result = (
        evaluate_distributed_reliability(
            shared
        )
    )

    assert not result.shared_data_used

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    assert result.evaluation is local

    assert (
        result.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    )


def test_shared_window_operation_mismatch_rejected():
    with pytest.raises(
        ValueError,
        match="operation mismatch",
    ):
        evaluate_distributed_reliability(
            _shared(
                window=_window(
                    operation=(
                        "rag.agentic.planner"
                    )
                )
            )
        )


def test_shared_window_policy_window_mismatch_rejected():
    with pytest.raises(
        ValueError,
        match="policy window",
    ):
        evaluate_distributed_reliability(
            _shared(
                window=_window(
                    window_seconds=60.0
                )
            )
        )


def test_shared_source_requires_window():
    shared = SharedReliabilitySnapshot(
        operation="gemini.embedding",
        source=(
            ReliabilityDataSource
            .SHARED_CACHE
        ),
        provider_enabled=True,
        local_snapshot=_local(),
        shared_window=None,
        cache_age_seconds=None,
        cache_stale=False,
        database_unavailable=False,
        refresh_in_flight=False,
    )

    with pytest.raises(
        ValueError,
        match="requires",
    ):
        evaluate_distributed_reliability(
            shared
        )


def test_local_source_rejects_shared_window():
    shared = SharedReliabilitySnapshot(
        operation="gemini.embedding",
        source=(
            ReliabilityDataSource
            .LOCAL_FALLBACK
        ),
        provider_enabled=True,
        local_snapshot=_local(),
        shared_window=_window(),
        cache_age_seconds=31.0,
        cache_stale=True,
        database_unavailable=True,
        refresh_in_flight=False,
    )

    with pytest.raises(
        ValueError,
        match="must not expose",
    ):
        evaluate_distributed_reliability(
            shared
        )


def test_getter_uses_provider_snapshot_only():
    expected = _shared(
        source=(
            ReliabilityDataSource
            .LOCAL_FALLBACK
        ),
        window=None,
    )

    class Provider:
        def __init__(self):
            self.calls = []

        def snapshot(
            self,
            operation,
        ):
            self.calls.append(
                operation
            )

            return expected

    provider = Provider()

    result = (
        get_distributed_reliability_snapshot(
            "gemini.embedding",
            provider=provider,
        )
    )

    assert provider.calls == [
        "gemini.embedding"
    ]

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )


def test_safe_payload_contains_no_sensitive_content():
    result = (
        evaluate_distributed_reliability(
            _shared()
        )
    )

    rendered = repr(
        result.to_safe_dict()
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

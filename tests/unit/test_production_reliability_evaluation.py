from __future__ import annotations

import pytest

from src.reliability.production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    OperationalBurnSeverity,
    OperationalReliabilityState,
    ProductionReliabilityPolicy,
    evaluate_production_reliability_counts,
)

POLICY = (
    PRODUCTION_RELIABILITY_POLICIES[
        "gemini.embedding"
    ]
)


def evaluate(
    *,
    total,
    success,
    failed,
    circuits=0,
    policy=POLICY,
):
    return (
        evaluate_production_reliability_counts(
            policy=policy,
            total_operations=total,
            successful_operations=success,
            failed_operations=failed,
            circuit_rejections=circuits,
        )
    )


def test_no_sample_is_insufficient():
    snapshot = evaluate(
        total=0,
        success=0,
        failed=0,
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    )

    assert snapshot.burn_severity is None
    assert snapshot.observed_failure_ratio is None
    assert snapshot.burn_rate is None


def test_healthy_sample():
    snapshot = evaluate(
        total=20,
        success=20,
        failed=0,
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .HEALTHY
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity
        .NORMAL
    )

    assert snapshot.burn_rate == 0.0


def test_error_budget_boundary_is_degraded():
    snapshot = evaluate(
        total=200,
        success=199,
        failed=1,
    )

    assert snapshot.burn_rate == pytest.approx(
        1.0
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .DEGRADED
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity
        .NORMAL
    )


def test_warning_boundary_tolerates_float_noise():
    snapshot = evaluate(
        total=200,
        success=198,
        failed=2,
    )

    assert snapshot.burn_rate == pytest.approx(
        2.0
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .DEGRADED
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity
        .WARNING
    )


def test_critical_boundary_tolerates_float_noise():
    snapshot = evaluate(
        total=100,
        success=97,
        failed=3,
        circuits=1,
    )

    assert snapshot.burn_rate == pytest.approx(
        6.0
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .CRITICAL
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity
        .CRITICAL
    )

    assert snapshot.circuit_rejections == 1


def test_insufficient_sample_wins_over_high_burn():
    snapshot = evaluate(
        total=10,
        success=9,
        failed=1,
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity
        .CRITICAL
    )


def test_custom_policy_is_preserved():
    policy = ProductionReliabilityPolicy(
        operation="custom.boundary",
        objective_ratio=0.99,
        window_seconds=60,
        minimum_operations=10,
        warning_burn_rate=3,
        critical_burn_rate=8,
    )

    snapshot = evaluate(
        total=100,
        success=99,
        failed=1,
        policy=policy,
    )

    assert (
        snapshot.operation
        == "custom.boundary"
    )

    assert (
        snapshot.objective_ratio
        == 0.99
    )

    assert (
        snapshot.window_seconds
        == 60
    )

    assert (
        snapshot.minimum_operations
        == 10
    )

    assert snapshot.burn_rate == pytest.approx(
        1.0
    )


@pytest.mark.parametrize(
    (
        "total",
        "success",
        "failed",
        "circuits",
    ),
    [
        (-1, 0, 0, 0),
        (1, -1, 2, 0),
        (1, 1, -1, 0),
        (1, 0, 1, -1),
        (True, 1, 0, 0),
    ],
)
def test_negative_or_boolean_counts_rejected(
    total,
    success,
    failed,
    circuits,
):
    with pytest.raises(
        ValueError
    ):
        evaluate(
            total=total,
            success=success,
            failed=failed,
            circuits=circuits,
        )


def test_total_must_equal_success_plus_failure():
    with pytest.raises(
        ValueError,
        match="total_operations",
    ):
        evaluate(
            total=10,
            success=8,
            failed=1,
        )


def test_circuit_rejections_cannot_exceed_failures():
    with pytest.raises(
        ValueError,
        match="circuit_rejections",
    ):
        evaluate(
            total=10,
            success=9,
            failed=1,
            circuits=2,
        )


def test_policy_type_is_validated():
    with pytest.raises(
        TypeError,
        match="ProductionReliabilityPolicy",
    ):
        evaluate_production_reliability_counts(
            policy="invalid",
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            circuit_rejections=0,
        )

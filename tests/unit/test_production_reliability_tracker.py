from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)

import pytest

from src.reliability import (
    PRODUCTION_RELIABILITY_POLICIES,
    OperationalBurnSeverity,
    OperationalReliabilityState,
    ProductionReliabilityTracker,
)
from src.resilience import (
    ResilienceEvent,
    ResilienceEventType,
)


def _event(
    *,
    operation: str = "gemini.embedding",
    event_type: ResilienceEventType,
) -> ResilienceEvent:
    return ResilienceEvent(
        operation=operation,
        event_type=event_type,
        attempt_number=1,
        max_attempts=3,
    )


def test_tracker_contains_real_production_operations():
    assert set(
        PRODUCTION_RELIABILITY_POLICIES
    ) == {
        "gemini.embedding",
        "gemini.generate.supervisor",
        "gemini.generate.text_service",
        "rag.agentic.planner",
    }


def test_attempt_events_do_not_count_as_operations():
    tracker = (
        ProductionReliabilityTracker()
    )

    for event_type in (
        ResilienceEventType.ATTEMPT_STARTED,
        ResilienceEventType.ATTEMPT_FAILED,
        ResilienceEventType.RETRY_SCHEDULED,
    ):
        assert not tracker.record_event(
            _event(
                event_type=event_type
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 0


def test_retry_then_success_counts_one_logical_success():
    tracker = (
        ProductionReliabilityTracker()
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .ATTEMPT_FAILED
            )
        )
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .RETRY_SCHEDULED
            )
        )
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .OPERATION_SUCCEEDED
            )
        )
    )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 1
    assert snapshot.successful_operations == 1
    assert snapshot.failed_operations == 0


def test_final_operation_failure_counts_once():
    tracker = (
        ProductionReliabilityTracker()
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .OPERATION_FAILED
            )
        )
    )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 1
    assert snapshot.failed_operations == 1


def test_circuit_rejection_counts_as_unavailability():
    tracker = (
        ProductionReliabilityTracker()
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .CIRCUIT_REJECTED
            )
        )
    )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 1
    assert snapshot.failed_operations == 1
    assert snapshot.circuit_rejections == 1


def test_unknown_operation_is_not_tracked():
    tracker = (
        ProductionReliabilityTracker()
    )

    recorded = tracker.record_event(
        _event(
            operation="unknown.operation",
            event_type=(
                ResilienceEventType
                .OPERATION_SUCCEEDED
            ),
        )
    )

    assert recorded is False


def test_no_sample_is_insufficient_data():
    tracker = (
        ProductionReliabilityTracker()
    )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    )


def test_healthy_live_window():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(100):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert (
        snapshot.state
        is OperationalReliabilityState
        .HEALTHY
    )

    assert snapshot.burn_rate == 0.0

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity.NORMAL
    )


def test_degraded_live_window():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(198):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    for _ in range(2):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert (
        snapshot.observed_failure_ratio
        == pytest.approx(0.01)
    )

    assert (
        snapshot.burn_rate
        == pytest.approx(2.0)
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



def test_warning_boundary_tolerates_float_noise():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(198):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    for _ in range(2):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.burn_rate == pytest.approx(
        2.0
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity.WARNING
    )


def test_materially_below_warning_remains_normal():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(991):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    for _ in range(9):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.burn_rate == pytest.approx(
        1.8
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity.NORMAL
    )


def test_critical_boundary_tolerates_float_noise():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(970):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    for _ in range(30):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.burn_rate == pytest.approx(
        6.0
    )

    assert (
        snapshot.state
        is OperationalReliabilityState.CRITICAL
    )

    assert (
        snapshot.burn_severity
        is OperationalBurnSeverity.CRITICAL
    )


def test_critical_live_window():
    tracker = (
        ProductionReliabilityTracker()
    )

    for _ in range(193):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_SUCCEEDED
                )
            )
        )

    for _ in range(7):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert (
        snapshot.burn_rate
        > 6.0
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


def test_window_expiration_is_real():
    now = [0.0]

    tracker = ProductionReliabilityTracker(
        clock=lambda: now[0]
    )

    for _ in range(20):
        tracker.record_event(
            _event(
                event_type=(
                    ResilienceEventType
                    .OPERATION_FAILED
                )
            )
        )

    assert (
        tracker.snapshot(
            "gemini.embedding"
        ).total_operations
        == 20
    )

    now[0] = 901.0

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 0

    assert (
        snapshot.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    )


def test_tracker_is_thread_safe():
    tracker = (
        ProductionReliabilityTracker()
    )

    event = _event(
        event_type=(
            ResilienceEventType
            .OPERATION_SUCCEEDED
        )
    )

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:
        futures = [
            executor.submit(
                tracker.record_event,
                event,
            )
            for _ in range(200)
        ]

        for future in futures:
            assert future.result()

    snapshot = tracker.snapshot(
        "gemini.embedding"
    )

    assert snapshot.total_operations == 200
    assert snapshot.successful_operations == 200


def test_safe_snapshot_contains_no_content_fields():
    tracker = (
        ProductionReliabilityTracker()
    )

    tracker.record_event(
        _event(
            event_type=(
                ResilienceEventType
                .OPERATION_SUCCEEDED
            )
        )
    )

    payload = repr(
        tracker.snapshot(
            "gemini.embedding"
        ).to_safe_dict()
    ).lower()

    forbidden = {
        "prompt",
        "response",
        "payload",
        "api_key",
        "password",
        "user_id",
        "message",
    }

    for field in forbidden:
        assert field not in payload

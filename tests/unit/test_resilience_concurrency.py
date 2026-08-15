from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)

import pytest

from src.resilience import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitState,
    OperationKind,
    ResiliencePolicy,
)


def test_half_open_allows_exactly_one_concurrent_probe():
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_seconds=10.0,
    )

    breaker.record_failure(
        now=0.0
    )

    assert (
        breaker.snapshot().state
        is CircuitState.OPEN
    )

    def request_permission(
        _index: int,
    ) -> bool:
        return breaker.acquire_permission(
            now=10.0
        )

    with ThreadPoolExecutor(
        max_workers=32
    ) as executor:
        results = list(
            executor.map(
                request_permission,
                range(64),
            )
        )

    assert sum(results) == 1

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.HALF_OPEN
    )

    assert (
        snapshot.half_open_probe_in_flight
        is True
    )


def test_half_open_success_restores_concurrent_availability():
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_seconds=10.0,
    )

    breaker.record_failure(
        now=0.0
    )

    assert breaker.acquire_permission(
        now=10.0
    )

    breaker.record_success()

    assert (
        breaker.snapshot().state
        is CircuitState.CLOSED
    )

    def request_permission(
        _index: int,
    ) -> bool:
        return breaker.acquire_permission(
            now=11.0
        )

    with ThreadPoolExecutor(
        max_workers=16
    ) as executor:
        results = list(
            executor.map(
                request_permission,
                range(32),
            )
        )

    assert all(results)


def test_half_open_failure_reopens_and_blocks_other_requests():
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_seconds=10.0,
    )

    breaker.record_failure(
        now=0.0
    )

    assert breaker.acquire_permission(
        now=10.0
    )

    breaker.record_failure(
        now=10.5
    )

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.OPEN
    )

    assert not breaker.acquire_permission(
        now=11.0
    )


def test_registry_rejects_runtime_policy_drift():
    registry = (
        CircuitBreakerRegistry()
    )

    original = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        circuit_failure_threshold=5,
        circuit_recovery_seconds=30.0,
    )

    changed = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        circuit_failure_threshold=7,
        circuit_recovery_seconds=30.0,
    )

    registry.get_or_create(
        original
    )

    with pytest.raises(
        ValueError,
        match="Circuit policy changed",
    ):
        registry.get_or_create(
            changed
        )


def test_independent_operations_do_not_share_circuit_state():
    registry = (
        CircuitBreakerRegistry()
    )

    embedding = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        circuit_failure_threshold=1,
    )

    generation = ResiliencePolicy(
        name="gemini.generate_content",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        circuit_failure_threshold=1,
    )

    embedding_breaker = (
        registry.get_or_create(
            embedding
        )
    )

    generation_breaker = (
        registry.get_or_create(
            generation
        )
    )

    embedding_breaker.record_failure(
        now=0.0
    )

    assert (
        embedding_breaker
        .snapshot()
        .state
        is CircuitState.OPEN
    )

    assert (
        generation_breaker
        .snapshot()
        .state
        is CircuitState.CLOSED
    )

    assert (
        embedding_breaker
        is not generation_breaker
    )

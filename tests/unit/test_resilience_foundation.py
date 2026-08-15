from __future__ import annotations

import asyncio

import pytest

from src.resilience import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitOpenError,
    CircuitState,
    FailureKind,
    OperationKind,
    ResilienceEventType,
    ResiliencePolicy,
    ResilienceRuntime,
    calculate_backoff_seconds,
    classify_failure,
)


class HttpFailure(RuntimeError):
    def __init__(
        self,
        status_code: int,
    ) -> None:
        self.status_code = status_code
        super().__init__("upstream failure")


class WrappedFailure(RuntimeError):
    pass


class FakeClock:
    def __init__(
        self,
        initial: float = 0.0,
    ) -> None:
        self.value = float(initial)

    def __call__(
        self,
    ) -> float:
        return self.value

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.value += float(seconds)


def test_side_effect_policy_never_retries():
    policy = ResiliencePolicy(
        name="email-send",
        operation_kind=(
            OperationKind.SIDE_EFFECT
        ),
    )

    assert not policy.allows_retry(
        failure_kind=FailureKind.TIMEOUT,
        attempt_number=1,
    )


def test_read_only_policy_retries_transient_failure():
    policy = ResiliencePolicy(
        name="gemini-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
    )

    assert policy.allows_retry(
        failure_kind=(
            FailureKind.TRANSIENT_NETWORK
        ),
        attempt_number=1,
    )


def test_validation_failure_is_not_retryable():
    policy = ResiliencePolicy(
        name="rag-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
    )

    assert not policy.allows_retry(
        failure_kind=(
            FailureKind.VALIDATION
        ),
        attempt_number=1,
    )


def test_retry_stops_at_max_attempts():
    policy = ResiliencePolicy(
        name="rag-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=3,
    )

    assert not policy.allows_retry(
        failure_kind=(
            FailureKind.TIMEOUT
        ),
        attempt_number=3,
    )


@pytest.mark.parametrize(
    ("retry_number", "expected"),
    [
        (1, 0.25),
        (2, 0.50),
        (3, 1.00),
        (4, 2.00),
        (5, 2.00),
    ],
)
def test_backoff_is_exponential_and_bounded(
    retry_number,
    expected,
):
    assert calculate_backoff_seconds(
        retry_number=retry_number,
        base_delay_seconds=0.25,
        max_delay_seconds=2.0,
        jitter_ratio=0.0,
    ) == expected


def test_backoff_jitter_is_deterministic_when_source_is_injected():
    delay = calculate_backoff_seconds(
        retry_number=2,
        base_delay_seconds=1.0,
        max_delay_seconds=10.0,
        jitter_ratio=0.2,
        random_source=lambda: 0.5,
    )

    assert delay == 2.0


def test_timeout_is_classified():
    assert (
        classify_failure(
            TimeoutError()
        )
        is FailureKind.TIMEOUT
    )


def test_network_failure_is_classified():
    assert (
        classify_failure(
            ConnectionError()
        )
        is FailureKind.TRANSIENT_NETWORK
    )


def test_rate_limit_is_classified():
    assert (
        classify_failure(
            HttpFailure(429)
        )
        is FailureKind.RATE_LIMIT
    )


def test_upstream_5xx_is_classified():
    assert (
        classify_failure(
            HttpFailure(503)
        )
        is FailureKind.UPSTREAM_5XX
    )


def test_authentication_failure_is_not_retryable():
    assert (
        classify_failure(
            HttpFailure(401)
        )
        is FailureKind.AUTHENTICATION
    )


def test_authorization_failure_is_not_retryable():
    assert (
        classify_failure(
            HttpFailure(403)
        )
        is FailureKind.AUTHORIZATION
    )


def test_wrapped_exception_uses_original_cause():
    try:
        try:
            raise TimeoutError(
                "provider timeout"
            )
        except TimeoutError as exc:
            raise WrappedFailure(
                "safe wrapper"
            ) from exc

    except WrappedFailure as exc:
        assert (
            classify_failure(exc)
            is FailureKind.TIMEOUT
        )


def test_circuit_opens_after_threshold():
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_seconds=30.0,
    )

    breaker.record_failure(
        now=10.0
    )

    assert (
        breaker.snapshot().state
        is CircuitState.CLOSED
    )

    breaker.record_failure(
        now=11.0
    )

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.OPEN
    )

    assert not breaker.acquire_permission(
        now=20.0
    )


def test_half_open_allows_only_one_probe():
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

    assert (
        breaker.snapshot().state
        is CircuitState.HALF_OPEN
    )

    assert not breaker.acquire_permission(
        now=10.0
    )


def test_half_open_success_closes_circuit():
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_seconds=10.0,
    )

    breaker.record_failure(
        now=0.0
    )

    breaker.acquire_permission(
        now=10.0
    )

    breaker.record_success()

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.CLOSED
    )

    assert (
        snapshot.consecutive_failures
        == 0
    )


def test_half_open_failure_reopens_circuit():
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_seconds=10.0,
    )

    breaker.record_failure(
        now=0.0
    )

    breaker.acquire_permission(
        now=10.0
    )

    breaker.record_failure(
        now=11.0
    )

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.OPEN
    )

    assert snapshot.opened_at == 11.0


def test_registry_reuses_breaker_for_same_operation():
    registry = (
        CircuitBreakerRegistry()
    )

    policy = ResiliencePolicy(
        name="gemini-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
    )

    first = registry.get_or_create(
        policy
    )

    second = registry.get_or_create(
        policy
    )

    assert first is second


def test_runtime_retries_transient_failure_then_succeeds():
    attempts = 0
    sleeps = []

    def operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise TimeoutError(
                "temporary"
            )

        return "ok"

    runtime = ResilienceRuntime(
        sleeper=sleeps.append,
        random_source=lambda: 0.5,
    )

    policy = ResiliencePolicy(
        name="gemini-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=3,
        jitter_ratio=0.0,
        circuit_failure_threshold=5,
    )

    result = runtime.execute(
        policy=policy,
        operation=operation,
    )

    assert result == "ok"
    assert attempts == 3
    assert sleeps == [
        0.25,
        0.50,
    ]


def test_runtime_does_not_retry_side_effect():
    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1

        raise TimeoutError(
            "email timeout"
        )

    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
    )

    policy = ResiliencePolicy(
        name="email-send",
        operation_kind=(
            OperationKind.SIDE_EFFECT
        ),
        max_attempts=5,
    )

    with pytest.raises(
        TimeoutError
    ):
        runtime.execute(
            policy=policy,
            operation=operation,
        )

    assert attempts == 1


def test_runtime_opens_shared_circuit_across_calls():
    clock = FakeClock()

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=lambda _: None,
    )

    policy = ResiliencePolicy(
        name="provider-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=1,
        circuit_failure_threshold=2,
        circuit_recovery_seconds=30.0,
    )

    def failure():
        raise ConnectionError(
            "temporary"
        )

    for _ in range(2):
        with pytest.raises(
            ConnectionError
        ):
            runtime.execute(
                policy=policy,
                operation=failure,
            )

    with pytest.raises(
        CircuitOpenError
    ):
        runtime.execute(
            policy=policy,
            operation=lambda: "never",
        )


def test_non_transient_failure_does_not_poison_circuit():
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
    )

    policy = ResiliencePolicy(
        name="validation-safe",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=1,
        circuit_failure_threshold=1,
    )

    with pytest.raises(
        ValueError
    ):
        runtime.execute(
            policy=policy,
            operation=lambda: (_ for _ in ()).throw(
                ValueError("invalid")
            ),
        )

    result = runtime.execute(
        policy=policy,
        operation=lambda: "ok",
    )

    assert result == "ok"


def test_observer_receives_safe_structured_events():
    events = []

    runtime = ResilienceRuntime(
        observer=events.append,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    calls = 0

    def operation():
        nonlocal calls
        calls += 1

        if calls == 1:
            raise TimeoutError(
                "SECRET_PAYLOAD"
            )

        return "ok"

    policy = ResiliencePolicy(
        name="safe-observability",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=2,
        jitter_ratio=0.0,
    )

    runtime.execute(
        policy=policy,
        operation=operation,
    )

    event_types = [
        event.event_type
        for event in events
    ]

    assert (
        ResilienceEventType.RETRY_SCHEDULED
        in event_types
    )

    assert (
        ResilienceEventType.OPERATION_SUCCEEDED
        in event_types
    )

    assert all(
        "SECRET_PAYLOAD"
        not in repr(event)
        for event in events
    )


def test_observer_failure_does_not_break_operation():
    def broken_observer(_):
        raise RuntimeError(
            "telemetry unavailable"
        )

    runtime = ResilienceRuntime(
        observer=broken_observer,
    )

    policy = ResiliencePolicy(
        name="observer-failure",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
    )

    assert (
        runtime.execute(
            policy=policy,
            operation=lambda: "ok",
        )
        == "ok"
    )


def test_async_runtime_retries_and_succeeds():
    attempts = 0
    sleeps = []

    async def operation():
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise TimeoutError(
                "temporary"
            )

        return "async-ok"

    async def fake_sleep(
        delay: float,
    ):
        sleeps.append(
            delay
        )

    runtime = ResilienceRuntime(
        random_source=lambda: 0.5,
    )

    policy = ResiliencePolicy(
        name="async-rag-read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=2,
        jitter_ratio=0.0,
    )

    result = asyncio.run(
        runtime.execute_async(
            policy=policy,
            operation=operation,
            sleeper=fake_sleep,
        )
    )

    assert result == "async-ok"
    assert attempts == 2
    assert sleeps == [0.25]



class GoogleGenAIStyleError(RuntimeError):
    def __init__(
        self,
        code: int,
        *,
        status: str = "UNKNOWN",
    ) -> None:
        self.code = code
        self.status = status

        super().__init__(
            "provider detail must not drive classification"
        )


def test_google_genai_429_code_is_rate_limit():
    error = GoogleGenAIStyleError(
        429,
        status="RESOURCE_EXHAUSTED",
    )

    assert (
        classify_failure(error)
        is FailureKind.RATE_LIMIT
    )


def test_google_genai_503_code_is_upstream_failure():
    error = GoogleGenAIStyleError(
        503,
        status="UNAVAILABLE",
    )

    assert (
        classify_failure(error)
        is FailureKind.UPSTREAM_5XX
    )


def test_google_genai_401_code_is_authentication_failure():
    error = GoogleGenAIStyleError(
        401,
        status="UNAUTHENTICATED",
    )

    assert (
        classify_failure(error)
        is FailureKind.AUTHENTICATION
    )


def test_google_genai_400_code_is_invalid_request():
    error = GoogleGenAIStyleError(
        400,
        status="INVALID_ARGUMENT",
    )

    assert (
        classify_failure(error)
        is FailureKind.INVALID_REQUEST
    )


def test_google_genai_api_error_cause_is_classified():
    try:
        try:
            raise GoogleGenAIStyleError(
                429,
                status="RESOURCE_EXHAUSTED",
            )
        except GoogleGenAIStyleError as exc:
            raise RuntimeError(
                "safe application wrapper"
            ) from exc

    except RuntimeError as exc:
        assert (
            classify_failure(exc)
            is FailureKind.RATE_LIMIT
        )

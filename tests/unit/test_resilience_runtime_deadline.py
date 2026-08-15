from __future__ import annotations

import asyncio

import pytest

from src.resilience import (
    DeadlineBudget,
    DeadlineBudgetExhaustedError,
    OperationKind,
    ResiliencePolicy,
    ResilienceRuntime,
)


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


def _policy() -> ResiliencePolicy:
    return ResiliencePolicy(
        name="test.deadline.runtime",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=3,
        base_delay_seconds=0.5,
        max_delay_seconds=2.0,
        jitter_ratio=0.0,
        circuit_failure_threshold=10,
    )


def test_runtime_without_deadline_preserves_existing_behavior():
    sleeps = []
    attempts = 0

    def operation():
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise TimeoutError(
                "temporary"
            )

        return "ok"

    runtime = ResilienceRuntime(
        sleeper=sleeps.append,
        random_source=lambda: 0.5,
    )

    result = runtime.execute(
        policy=_policy(),
        operation=operation,
    )

    assert result == "ok"
    assert attempts == 2
    assert sleeps == [0.5]


def test_deadline_rejects_initial_attempt_before_operation():
    clock = FakeClock()

    budget = DeadlineBudget(
        1.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    called = False

    def operation():
        nonlocal called
        called = True
        return "should-not-run"

    with pytest.raises(
        DeadlineBudgetExhaustedError,
        match="initial attempt",
    ):
        runtime.execute(
            policy=_policy(),
            operation=operation,
            deadline_budget=budget,
            minimum_retry_attempt_seconds=0.8,
        )

    assert called is False


def test_retry_is_denied_before_sleep_when_budget_is_insufficient():
    clock = FakeClock()
    sleeps = []
    attempts = 0

    budget = DeadlineBudget(
        3.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    def sleeper(seconds):
        sleeps.append(seconds)
        clock.advance(seconds)

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=sleeper,
        random_source=lambda: 0.5,
    )

    def operation():
        nonlocal attempts

        attempts += 1

        clock.advance(1.5)

        raise TimeoutError(
            "temporary"
        )

    with pytest.raises(
        DeadlineBudgetExhaustedError,
        match="retry",
    ):
        runtime.execute(
            policy=_policy(),
            operation=operation,
            deadline_budget=budget,
            minimum_retry_attempt_seconds=1.0,
        )

    assert attempts == 1
    assert sleeps == []


def test_retry_runs_when_budget_contains_delay_and_next_attempt():
    clock = FakeClock()
    sleeps = []
    attempts = 0

    budget = DeadlineBudget(
        5.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    def sleeper(seconds):
        sleeps.append(seconds)
        clock.advance(seconds)

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=sleeper,
        random_source=lambda: 0.5,
    )

    def operation():
        nonlocal attempts

        attempts += 1

        clock.advance(1.0)

        if attempts == 1:
            raise TimeoutError(
                "temporary"
            )

        return "ok"

    result = runtime.execute(
        policy=_policy(),
        operation=operation,
        deadline_budget=budget,
        minimum_retry_attempt_seconds=1.0,
    )

    assert result == "ok"
    assert attempts == 2
    assert sleeps == [0.5]


def test_deadline_exhaustion_does_not_execute_extra_retry():
    clock = FakeClock()
    attempts = 0

    budget = DeadlineBudget(
        2.5,
        reserve_seconds=0.25,
        clock=clock,
    )

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=lambda _: pytest.fail(
            "sleep must not execute"
        ),
        random_source=lambda: 0.5,
    )

    def operation():
        nonlocal attempts

        attempts += 1
        clock.advance(1.5)

        raise ConnectionError(
            "temporary"
        )

    with pytest.raises(
        DeadlineBudgetExhaustedError
    ):
        runtime.execute(
            policy=_policy(),
            operation=operation,
            deadline_budget=budget,
            minimum_retry_attempt_seconds=1.0,
        )

    assert attempts == 1


@pytest.mark.parametrize(
    "value",
    [
        -1.0,
        float("inf"),
        float("nan"),
    ],
)
def test_invalid_minimum_retry_attempt_budget_is_rejected(
    value,
):
    runtime = ResilienceRuntime()

    with pytest.raises(
        ValueError,
        match=(
            "minimum_retry_attempt_seconds"
        ),
    ):
        runtime.execute(
            policy=_policy(),
            operation=lambda: "ok",
            minimum_retry_attempt_seconds=value,
        )


def test_async_runtime_respects_deadline_before_retry():
    async def scenario():
        clock = FakeClock()
        attempts = 0
        sleeps = []

        budget = DeadlineBudget(
            3.0,
            reserve_seconds=0.25,
            clock=clock,
        )

        async def sleeper(seconds):
            sleeps.append(seconds)
            clock.advance(seconds)

        runtime = ResilienceRuntime(
            clock=clock,
            random_source=lambda: 0.5,
        )

        async def operation():
            nonlocal attempts

            attempts += 1
            clock.advance(1.5)

            raise TimeoutError(
                "temporary"
            )

        with pytest.raises(
            DeadlineBudgetExhaustedError
        ):
            await runtime.execute_async(
                policy=_policy(),
                operation=operation,
                sleeper=sleeper,
                deadline_budget=budget,
                minimum_retry_attempt_seconds=1.0,
            )

        assert attempts == 1
        assert sleeps == []

    asyncio.run(
        scenario()
    )


def test_deadline_budget_exhaustion_is_not_retried_itself():
    clock = FakeClock()
    attempts = 0

    budget = DeadlineBudget(
        1.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    runtime = ResilienceRuntime(
        clock=clock,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    def operation():
        nonlocal attempts
        attempts += 1
        return "ok"

    clock.advance(0.9)

    with pytest.raises(
        DeadlineBudgetExhaustedError
    ):
        runtime.execute(
            policy=_policy(),
            operation=operation,
            deadline_budget=budget,
            minimum_retry_attempt_seconds=0.2,
        )

    assert attempts == 0

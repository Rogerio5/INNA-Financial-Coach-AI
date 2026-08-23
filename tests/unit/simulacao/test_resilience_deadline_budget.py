from __future__ import annotations

import math

import pytest

from src.resilience import (
    DeadlineBudget,
    DeadlineBudgetExhaustedError,
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


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_deadline_rejects_invalid_total(
    value,
):
    with pytest.raises(
        ValueError
    ):
        DeadlineBudget(
            value
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        math.inf,
        math.nan,
    ],
)
def test_deadline_rejects_invalid_reserve(
    value,
):
    with pytest.raises(
        ValueError
    ):
        DeadlineBudget(
            8.0,
            reserve_seconds=value,
        )


def test_reserve_must_be_smaller_than_total():
    with pytest.raises(
        ValueError,
        match="reserve_seconds",
    ):
        DeadlineBudget(
            8.0,
            reserve_seconds=8.0,
        )


def test_deadline_snapshot_is_deterministic():
    clock = FakeClock(
        100.0
    )

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.5,
        clock=clock,
    )

    clock.advance(
        2.0
    )

    snapshot = (
        budget.snapshot()
    )

    assert (
        snapshot.total_seconds
        == pytest.approx(8.0)
    )

    assert (
        snapshot.elapsed_seconds
        == pytest.approx(2.0)
    )

    assert (
        snapshot.remaining_seconds
        == pytest.approx(6.0)
    )

    assert (
        snapshot.reserve_seconds
        == pytest.approx(0.5)
    )

    assert (
        snapshot.usable_seconds
        == pytest.approx(5.5)
    )

    assert snapshot.expired is False


def test_clock_rollback_never_creates_negative_elapsed():
    clock = FakeClock(
        100.0
    )

    budget = DeadlineBudget(
        8.0,
        clock=clock,
    )

    clock.value = 90.0

    assert (
        budget.elapsed_seconds()
        == 0.0
    )

    assert (
        budget.remaining_seconds()
        == pytest.approx(8.0)
    )


def test_budget_expires_after_reserve_boundary():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.5,
        clock=clock,
    )

    clock.advance(
        7.5
    )

    assert budget.expired()
    assert budget.usable_seconds() == 0.0


def test_can_start_attempt_uses_remaining_budget():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.5,
        clock=clock,
    )

    clock.advance(
        6.0
    )

    assert budget.can_start_attempt(
        minimum_attempt_seconds=1.5,
    )

    assert not budget.can_start_attempt(
        minimum_attempt_seconds=1.501,
    )


def test_retry_requires_backoff_and_next_attempt_budget():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.5,
        clock=clock,
    )

    clock.advance(
        5.0
    )

    assert budget.can_retry(
        delay_seconds=0.5,
        minimum_attempt_seconds=2.0,
    )

    assert not budget.can_retry(
        delay_seconds=0.6,
        minimum_attempt_seconds=2.0,
    )


def test_clamp_timeout_never_exceeds_total_budget():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    timeout = (
        budget.clamp_timeout(
            15.0
        )
    )

    assert (
        timeout
        == pytest.approx(7.75)
    )


def test_clamp_timeout_preserves_shorter_transport_timeout():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.25,
        clock=clock,
    )

    assert (
        budget.clamp_timeout(
            3.0
        )
        == pytest.approx(3.0)
    )


def test_clamp_timeout_fails_when_budget_is_exhausted():
    clock = FakeClock()

    budget = DeadlineBudget(
        8.0,
        reserve_seconds=0.5,
        clock=clock,
    )

    clock.advance(
        7.6
    )

    with pytest.raises(
        DeadlineBudgetExhaustedError
    ):
        budget.clamp_timeout(
            5.0
        )


def test_from_milliseconds_matches_supervisor_shape():
    clock = FakeClock()

    budget = (
        DeadlineBudget
        .from_milliseconds(
            8_000,
            reserve_ms=250,
            clock=clock,
        )
    )

    assert (
        budget.total_seconds
        == pytest.approx(8.0)
    )

    assert (
        budget.reserve_seconds
        == pytest.approx(0.25)
    )

    assert (
        budget.clamp_timeout(
            10.0
        )
        == pytest.approx(7.75)
    )


def test_budget_exhaustion_is_not_timeout_error():
    error = (
        DeadlineBudgetExhaustedError(
            "budget exhausted"
        )
    )

    assert not isinstance(
        error,
        TimeoutError,
    )

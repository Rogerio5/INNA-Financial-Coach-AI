from __future__ import annotations

import threading
import time

import pytest

from src.services.telegram_observability import (
    CallableTelegramProbe,
    TelegramOperationalStatus,
    TelegramOperationalStatusService,
    TelegramReadinessRuntime,
    TelegramReadinessRuntimePolicy,
)


class MutableClock:
    def __init__(
        self,
        value=0.0,
    ):
        self.value = float(value)

    def __call__(
        self,
    ):
        return self.value

    def advance(
        self,
        seconds,
    ):
        self.value += float(seconds)


class CountingService:
    def __init__(
        self,
        delegate,
    ):
        self.delegate = delegate
        self.calls = 0

    def evaluate(
        self,
    ):
        self.calls += 1
        return self.delegate.evaluate()


def healthy_service():
    return TelegramOperationalStatusService(
        probes=(
            CallableTelegramProbe(
                name="process",
                severity="required",
                check=lambda: True,
            ),
        )
    )


def unready_service():
    return TelegramOperationalStatusService(
        probes=(
            CallableTelegramProbe(
                name="database",
                severity="required",
                check=lambda: False,
                error_category="database",
            ),
        )
    )


def test_first_evaluation_is_not_cache_hit():
    runtime = TelegramReadinessRuntime(healthy_service())

    result = runtime.evaluate()

    assert result.cache_hit is False
    assert result.reason == "evaluated"
    assert result.sequence == 1
    assert result.ready is True


def test_second_evaluation_uses_cache():
    clock = MutableClock()

    service = CountingService(healthy_service())

    runtime = TelegramReadinessRuntime(
        service,
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=10,
            )
        ),
        monotonic_clock=clock,
    )

    first = runtime.evaluate()

    clock.advance(1)

    second = runtime.evaluate()

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.sequence == first.sequence
    assert second.cache_age_seconds == 1
    assert service.calls == 1


def test_expired_cache_refreshes():
    clock = MutableClock()

    service = CountingService(healthy_service())

    runtime = TelegramReadinessRuntime(
        service,
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=1,
            )
        ),
        monotonic_clock=clock,
    )

    first = runtime.evaluate()

    clock.advance(2)

    second = runtime.evaluate()

    assert second.cache_hit is False
    assert second.sequence == (first.sequence + 1)

    assert service.calls == 2


def test_force_refresh_ignores_cache():
    service = CountingService(healthy_service())

    runtime = TelegramReadinessRuntime(
        service,
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=100,
            )
        ),
    )

    first = runtime.evaluate()

    second = runtime.evaluate(force_refresh=True)

    assert second.cache_hit is False
    assert second.sequence == (first.sequence + 1)

    assert service.calls == 2


def test_invalidate_removes_cache():
    service = CountingService(healthy_service())

    runtime = TelegramReadinessRuntime(
        service,
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=100,
            )
        ),
    )

    runtime.evaluate()
    runtime.invalidate()
    runtime.evaluate()

    assert service.calls == 2


def test_unready_snapshot_remains_unready():
    runtime = TelegramReadinessRuntime(unready_service())

    result = runtime.evaluate()

    assert result.snapshot.status is TelegramOperationalStatus.UNREADY

    assert result.ready is False


def test_evaluation_exception_fails_closed():
    class BrokenService:
        def evaluate(
            self,
        ):
            raise RuntimeError("postgresql://user:password@secret")

    runtime = TelegramReadinessRuntime(BrokenService())

    result = runtime.evaluate()

    rendered = repr(result.to_safe_dict())

    assert result.ready is False

    assert result.snapshot.status is TelegramOperationalStatus.UNREADY

    assert result.reason == "evaluation_exception"

    assert "password" not in rendered
    assert "postgresql://" not in rendered


def test_budget_exceeded_becomes_unready():
    clock = MutableClock()

    class SlowService:
        def evaluate(
            self,
        ):
            clock.advance(5)

            return healthy_service().evaluate()

    runtime = TelegramReadinessRuntime(
        SlowService(),
        policy=(
            TelegramReadinessRuntimePolicy(
                evaluation_budget_seconds=1,
            )
        ),
        monotonic_clock=clock,
    )

    result = runtime.evaluate()

    assert result.ready is False

    assert result.reason == "evaluation_budget_exceeded"

    names = {check.name for check in (result.snapshot.checks)}

    assert "readiness_runtime_budget" in names


def test_safe_dict_contains_runtime_metadata():
    runtime = TelegramReadinessRuntime(
        healthy_service(),
        wall_clock=lambda: 123.0,
    )

    payload = runtime.evaluate().to_safe_dict()

    assert payload["sequence"] == 1

    assert payload["cache_hit"] is False

    assert payload["generated_at_epoch_seconds"] == 123.0

    assert payload["reason"] == "evaluated"

    assert payload["operational"]["status"] == "healthy"


@pytest.mark.parametrize(
    (
        "field",
        "value",
    ),
    [
        (
            "cache_ttl_seconds",
            -1,
        ),
        (
            "concurrent_wait_seconds",
            float("nan"),
        ),
        (
            "evaluation_budget_seconds",
            float("inf"),
        ),
        (
            "cache_ttl_seconds",
            "invalid",
        ),
    ],
)
def test_policy_rejects_invalid_values(
    field,
    value,
):
    values = {
        "cache_ttl_seconds": 1,
        "concurrent_wait_seconds": 1,
        "evaluation_budget_seconds": 1,
    }

    values[field] = value

    with pytest.raises(ValueError):
        TelegramReadinessRuntimePolicy(**values)


def test_single_flight_runs_service_once():
    started = threading.Event()
    release = threading.Event()

    class BlockingService:
        def __init__(
            self,
        ):
            self.calls = 0

        def evaluate(
            self,
        ):
            self.calls += 1
            started.set()

            assert release.wait(timeout=2)

            return healthy_service().evaluate()

    service = BlockingService()

    runtime = TelegramReadinessRuntime(
        service,
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=10,
                concurrent_wait_seconds=1,
            )
        ),
    )

    results = []

    first_thread = threading.Thread(target=lambda: results.append(runtime.evaluate()))

    second_thread = threading.Thread(target=lambda: results.append(runtime.evaluate()))

    first_thread.start()

    assert started.wait(timeout=1)

    second_thread.start()

    time.sleep(0.05)

    release.set()

    first_thread.join(timeout=2)

    second_thread.join(timeout=2)

    assert len(results) == 2
    assert service.calls == 1

    assert any(result.cache_hit for result in results)


def test_concurrent_wait_timeout_fails_closed():
    started = threading.Event()
    release = threading.Event()

    class BlockingService:
        def evaluate(
            self,
        ):
            started.set()

            assert release.wait(timeout=2)

            return healthy_service().evaluate()

    runtime = TelegramReadinessRuntime(
        BlockingService(),
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=0,
                concurrent_wait_seconds=0.01,
            )
        ),
    )

    first_result = []

    first_thread = threading.Thread(
        target=lambda: first_result.append(runtime.evaluate())
    )

    first_thread.start()

    assert started.wait(timeout=1)

    concurrent = runtime.evaluate()

    assert concurrent.ready is False

    assert concurrent.reason == "concurrent_wait_timeout"

    release.set()

    first_thread.join(timeout=2)

    assert first_result


def test_cached_result_does_not_mutate_original():
    clock = MutableClock()

    runtime = TelegramReadinessRuntime(
        healthy_service(),
        policy=(
            TelegramReadinessRuntimePolicy(
                cache_ttl_seconds=10,
            )
        ),
        monotonic_clock=clock,
    )

    first = runtime.evaluate()

    clock.advance(1)

    second = runtime.evaluate()

    assert first.cache_hit is False
    assert first.cache_age_seconds == 0
    assert second.cache_hit is True
    assert second.cache_age_seconds == 1

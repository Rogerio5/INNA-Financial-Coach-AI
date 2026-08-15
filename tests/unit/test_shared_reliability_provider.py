from __future__ import annotations

from types import SimpleNamespace

from src.reliability.repository import (
    ProductionReliabilityWindow,
)
from src.reliability.shared_provider import (
    ReliabilityDataSource,
    SharedReliabilityProvider,
)


class FakeClock:
    def __init__(self):
        self.value = 100.0

    def __call__(self):
        return self.value

    def advance(
        self,
        seconds,
    ):
        self.value += seconds


class FakeTracker:
    def snapshot(
        self,
        operation,
    ):
        return SimpleNamespace(
            operation=operation,
            window_seconds=900.0,
            total_operations=7,
            failed_operations=1,
            circuit_rejections=0,
        )


class ControlledStarter:
    def __init__(self):
        self.calls = []

    def __call__(
        self,
        name,
        target,
    ):
        self.calls.append(
            (
                name,
                target,
            )
        )

    def run_next(self):
        _, target = self.calls.pop(0)
        target()


def _window(
    *,
    total=100,
    success=99,
    failed=1,
    circuits=0,
):
    return ProductionReliabilityWindow(
        operation="gemini.embedding",
        window_seconds=900.0,
        total_operations=total,
        successful_operations=success,
        failed_operations=failed,
        circuit_rejections=circuits,
        first_occurred_at=None,
        last_occurred_at=None,
    )


def test_disabled_provider_uses_local_without_refresh():
    starter = ControlledStarter()

    provider = SharedReliabilityProvider(
        enabled=False,
        tracker=FakeTracker(),
        window_loader=lambda **_: _window(),
        thread_starter=starter,
    )

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    assert not result.provider_enabled
    assert result.shared_window is None
    assert starter.calls == []


def test_cache_miss_returns_local_before_database():
    starter = ControlledStarter()
    loader_calls = []

    def loader(**_):
        loader_calls.append(True)
        return _window()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=loader,
        thread_starter=starter,
    )

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    assert result.refresh_in_flight
    assert loader_calls == []
    assert len(starter.calls) == 1


def test_background_refresh_populates_shared_cache():
    starter = ControlledStarter()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: (
            _window(
                total=200,
                success=198,
                failed=2,
                circuits=1,
            )
        ),
        thread_starter=starter,
    )

    initial = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        initial.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    starter.run_next()

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    assert result.shared_window is not None

    assert (
        result.shared_window
        .total_operations
        == 200
    )

    assert not result.cache_stale


def test_fresh_cache_does_not_schedule_refresh():
    starter = ControlledStarter()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: _window(),
        thread_starter=starter,
    )

    assert provider.refresh_now(
        "gemini.embedding"
    )

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    assert starter.calls == []


def test_stale_cache_is_used_while_refreshing():
    starter = ControlledStarter()
    clock = FakeClock()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: _window(),
        cache_ttl_seconds=5,
        max_stale_seconds=30,
        clock=clock,
        thread_starter=starter,
    )

    assert provider.refresh_now(
        "gemini.embedding"
    )

    clock.advance(6)

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    assert result.cache_stale
    assert result.refresh_in_flight
    assert len(starter.calls) == 1


def test_too_old_cache_falls_back_local():
    starter = ControlledStarter()
    clock = FakeClock()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: _window(),
        cache_ttl_seconds=5,
        max_stale_seconds=30,
        clock=clock,
        thread_starter=starter,
    )

    assert provider.refresh_now(
        "gemini.embedding"
    )

    clock.advance(31)

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    assert result.shared_window is None
    assert result.cache_stale
    assert result.refresh_in_flight


def test_database_failure_is_fail_open():
    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: (
            (_ for _ in ()).throw(
                RuntimeError(
                    "postgres://secret@private-host"
                )
            )
        ),
    )

    assert not provider.refresh_now(
        "gemini.embedding"
    )

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .LOCAL_FALLBACK
    )

    assert result.database_unavailable


def test_failed_refresh_keeps_recent_shared_cache():
    starter = ControlledStarter()
    clock = FakeClock()
    should_fail = [False]

    def loader(**_):
        if should_fail[0]:
            raise RuntimeError(
                "database unavailable"
            )

        return _window()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=loader,
        cache_ttl_seconds=5,
        max_stale_seconds=30,
        clock=clock,
        thread_starter=starter,
    )

    assert provider.refresh_now(
        "gemini.embedding"
    )

    should_fail[0] = True
    clock.advance(6)

    result = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        result.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    starter.run_next()

    after_failure = provider.snapshot(
        "gemini.embedding"
    )

    assert (
        after_failure.source
        is ReliabilityDataSource
        .SHARED_CACHE
    )

    assert after_failure.cache_stale
    assert after_failure.database_unavailable


def test_refresh_is_single_flight_per_operation():
    starter = ControlledStarter()

    provider = SharedReliabilityProvider(
        enabled=True,
        tracker=FakeTracker(),
        window_loader=lambda **_: _window(),
        thread_starter=starter,
    )

    first = provider.snapshot(
        "gemini.embedding"
    )

    second = provider.snapshot(
        "gemini.embedding"
    )

    assert first.refresh_in_flight
    assert second.refresh_in_flight

    assert len(starter.calls) == 1


def test_safe_snapshot_has_no_content_fields():
    provider = SharedReliabilityProvider(
        enabled=False,
        tracker=FakeTracker(),
    )

    snapshot = provider.snapshot(
        "gemini.embedding"
    )

    rendered = repr(
        snapshot.to_safe_dict()
    ).lower()

    forbidden = {
        "prompt",
        "response",
        "payload",
        "api_key",
        "password",
        "user_id",
        "chat_id",
        "database_url",
        "error_message",
    }

    for field in forbidden:
        assert field not in rendered

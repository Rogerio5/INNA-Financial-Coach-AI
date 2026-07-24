from __future__ import annotations

import inspect

import pytest

import api.telegram_webhook as webhook_module
import src.services.telegram_conversation_state as state_module
from src.channels import telegram_update_worker
from src.services.telegram_conversation_state import (
    create_postgres_telegram_webhook_conversation_bridge,
)
from src.services.telegram_observability import (
    InMemoryTelegramConversationMetrics,
    InMemoryTelegramOperationalEventSink,
    NoOpTelegramConversationMetrics,
    NoOpTelegramOperationalEventSink,
)
from src.services.telegram_update_jobs import (
    TelegramUpdateRunnerConfigurationError,
)


class FakeClock:
    def __call__(self) -> float:
        return 10.0


class FakeBridge:
    pass


def test_postgres_bridge_factory_defaults_to_noop():
    bridge = (
        create_postgres_telegram_webhook_conversation_bridge()
    )

    assert isinstance(
        bridge.metrics,
        NoOpTelegramConversationMetrics,
    )

    assert isinstance(
        bridge.event_sink,
        NoOpTelegramOperationalEventSink,
    )

    assert callable(
        bridge.clock
    )

    assert bridge.runtime_initialized is False


def test_postgres_bridge_factory_preserves_instances():
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    event_sink = (
        InMemoryTelegramOperationalEventSink()
    )

    clock = FakeClock()

    bridge = (
        create_postgres_telegram_webhook_conversation_bridge(
            metrics=metrics,
            event_sink=event_sink,
            clock=clock,
        )
    )

    assert bridge.metrics is metrics
    assert bridge.event_sink is event_sink
    assert bridge.clock is clock

    assert bridge.runtime_initialized is False


def test_worker_composes_dependencies_once(
    monkeypatch,
):
    metrics = (
        InMemoryTelegramConversationMetrics()
    )

    event_sink = (
        InMemoryTelegramOperationalEventSink()
    )

    clock = FakeClock()

    calls = {
        "metrics_factory": 0,
        "event_sink_factory": 0,
        "bridge_factory": 0,
        "processor": 0,
    }

    captured = {}

    def metrics_factory():
        calls["metrics_factory"] += 1
        return metrics

    def event_sink_factory():
        calls["event_sink_factory"] += 1
        return event_sink

    def bridge_factory(**kwargs):
        calls["bridge_factory"] += 1
        captured.update(kwargs)
        return FakeBridge()

    def processor(
        update,
        *,
        conversation_bridge,
    ):
        calls["processor"] += 1

        return {
            "update": update,
            "bridge": conversation_bridge,
        }

    monkeypatch.setattr(
        state_module,
        "create_postgres_telegram_webhook_conversation_bridge",
        bridge_factory,
    )

    monkeypatch.setattr(
        webhook_module,
        "process_telegram_update",
        processor,
    )

    loaded = (
        telegram_update_worker.load_telegram_processor(
            metrics_factory=metrics_factory,
            event_sink_factory=event_sink_factory,
            clock=clock,
        )
    )

    first = loaded(
        {
            "update_id": 1,
        }
    )

    second = loaded(
        {
            "update_id": 2,
        }
    )

    assert calls == {
        "metrics_factory": 1,
        "event_sink_factory": 1,
        "bridge_factory": 1,
        "processor": 2,
    }

    assert captured["metrics"] is metrics
    assert captured["event_sink"] is event_sink
    assert captured["clock"] is clock

    assert first["bridge"] is second["bridge"]


def test_worker_defaults_remain_noop(
    monkeypatch,
):
    captured = {}

    def bridge_factory(**kwargs):
        captured.update(kwargs)
        return FakeBridge()

    def processor(
        update,
        *,
        conversation_bridge,
    ):
        return conversation_bridge

    monkeypatch.setattr(
        state_module,
        "create_postgres_telegram_webhook_conversation_bridge",
        bridge_factory,
    )

    monkeypatch.setattr(
        webhook_module,
        "process_telegram_update",
        processor,
    )

    loaded = (
        telegram_update_worker.load_telegram_processor()
    )

    bridge = loaded(
        {
            "update_id": 1,
        }
    )

    assert isinstance(
        captured["metrics"],
        NoOpTelegramConversationMetrics,
    )

    assert isinstance(
        captured["event_sink"],
        NoOpTelegramOperationalEventSink,
    )

    assert bridge is not None


@pytest.mark.parametrize(
    (
        "metrics_factory",
        "event_sink_factory",
        "clock",
    ),
    [
        (
            None,
            NoOpTelegramOperationalEventSink,
            FakeClock(),
        ),
        (
            NoOpTelegramConversationMetrics,
            None,
            FakeClock(),
        ),
        (
            NoOpTelegramConversationMetrics,
            NoOpTelegramOperationalEventSink,
            None,
        ),
    ],
)
def test_worker_rejects_invalid_factories(
    metrics_factory,
    event_sink_factory,
    clock,
):
    with pytest.raises(
        TelegramUpdateRunnerConfigurationError,
    ):
        telegram_update_worker.load_telegram_processor(
            metrics_factory=metrics_factory,
            event_sink_factory=event_sink_factory,
            clock=clock,
        )


def test_factory_signature_is_backward_compatible():
    signature = inspect.signature(
        create_postgres_telegram_webhook_conversation_bridge
    )

    parameters = signature.parameters

    assert parameters[
        "default_ttl_seconds"
    ].default is not inspect.Parameter.empty

    assert parameters[
        "default_language"
    ].default == "pt-BR"

    assert parameters[
        "metrics"
    ].default is None

    assert parameters[
        "event_sink"
    ].default is None

    assert callable(
        parameters["clock"].default
    )


def test_worker_signature_has_safe_defaults():
    signature = inspect.signature(
        telegram_update_worker.load_telegram_processor
    )

    assert (
        signature.parameters[
            "metrics_factory"
        ].default
        is NoOpTelegramConversationMetrics
    )

    assert (
        signature.parameters[
            "event_sink_factory"
        ].default
        is NoOpTelegramOperationalEventSink
    )

    assert callable(
        signature.parameters[
            "clock"
        ].default
    )

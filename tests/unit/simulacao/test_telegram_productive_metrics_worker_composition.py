from __future__ import annotations

import io
from unittest.mock import MagicMock

from src.channels import (
    telegram_update_worker as entrypoint,
)
from src.services.telegram_observability import (
    CompositeTelegramConversationMetrics,
    InMemoryTelegramProductiveMetrics,
    TelegramConversationMetricRecord,
)


def test_runtime_owns_single_registry():
    runtime = (
        entrypoint
        .create_production_telegram_metrics_runtime()
    )

    assert isinstance(
        runtime.registry,
        InMemoryTelegramProductiveMetrics,
    )

    assert runtime.adapter is not None
    assert runtime.safe_registry is not None


def test_loader_receives_metrics_factory(
    monkeypatch,
):
    captured = {}

    processor = MagicMock()

    def fake_loader(
        *,
        metrics_factory=None,
        event_sink_factory=None,
    ):
        captured[
            "metrics_factory"
        ] = metrics_factory

        captured[
            "event_sink_factory"
        ] = event_sink_factory

        return processor

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        fake_loader,
    )

    runtime = (
        entrypoint
        .create_production_telegram_metrics_runtime()
    )

    result = (
        entrypoint
        ._load_productive_telegram_processor(
            stderr=io.StringIO(),
            metrics_runtime=runtime,
        )
    )

    assert result is processor

    assert callable(
        captured["metrics_factory"]
    )

    metrics = captured[
        "metrics_factory"
    ]()

    assert isinstance(
        metrics,
        CompositeTelegramConversationMetrics,
    )


def test_metrics_factory_uses_same_registry(
    monkeypatch,
):
    captured = {}

    def fake_loader(
        *,
        metrics_factory=None,
        event_sink_factory=None,
    ):
        del event_sink_factory

        captured[
            "metrics"
        ] = metrics_factory()

        return MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        fake_loader,
    )

    runtime = (
        entrypoint
        .create_production_telegram_metrics_runtime()
    )

    entrypoint\
        ._load_productive_telegram_processor(
            stderr=io.StringIO(),
            metrics_runtime=runtime,
        )

    metrics = captured["metrics"]

    metrics.record_operation(
        TelegramConversationMetricRecord(
            operation="save_session",
            component="bridge",
            outcome="success",
            duration_ms=100.0,
            error_category=None,
            conflict_recovered=None,
        )
    )

    snapshot = runtime.registry.snapshot()

    assert (
        "inna_telegram_operations_total"
        in snapshot.counters
    )

    total = sum(
        snapshot.counters[
            "inna_telegram_operations_total"
        ].values()
    )

    assert total == 1.0


def test_loader_preserves_legacy_no_argument_mock(
    monkeypatch,
):
    processor = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        lambda: processor,
    )

    result = (
        entrypoint
        ._load_productive_telegram_processor(
            stderr=io.StringIO(),
        )
    )

    assert result is processor


def test_processor_keeps_runtime_reference(
    monkeypatch,
):
    processor = MagicMock()

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        lambda **kwargs: processor,
    )

    runtime = (
        entrypoint
        .create_production_telegram_metrics_runtime()
    )

    result = (
        entrypoint
        ._load_productive_telegram_processor(
            stderr=io.StringIO(),
            metrics_runtime=runtime,
        )
    )

    assert (
        result
        ._telegram_productive_metrics_runtime
        is runtime
    )


def test_main_creates_only_one_runtime(
    monkeypatch,
):
    stdout = io.StringIO()
    stderr = io.StringIO()

    runtime = MagicMock()

    create_runtime = MagicMock(
        return_value=runtime
    )

    monkeypatch.setattr(
        entrypoint,
        (
            "create_production_telegram_"
            "metrics_runtime"
        ),
        create_runtime,
    )

    monkeypatch.setattr(
        entrypoint,
        "load_worker_config_from_env",
        lambda: (
            entrypoint
            .TelegramUpdateWorkerConfig()
        ),
    )

    monkeypatch.setattr(
        entrypoint,
        (
            "load_telegram_update_"
            "keyring_from_env"
        ),
        lambda: object(),
    )

    processor = MagicMock()

    captured = {}

    def fake_productive_loader(
        *,
        stderr,
        metrics_runtime,
    ):
        captured[
            "stderr"
        ] = stderr

        captured[
            "runtime"
        ] = metrics_runtime

        return processor

    monkeypatch.setattr(
        entrypoint,
        (
            "_load_productive_telegram_"
            "processor"
        ),
        fake_productive_loader,
    )

    monkeypatch.setattr(
        entrypoint,
        "_install_signal_handlers",
        lambda stop_event: {},
    )

    monkeypatch.setattr(
        entrypoint,
        "_restore_signal_handlers",
        lambda handlers: None,
    )

    summary = MagicMock()

    summary.to_safe_dict.return_value = {
        "cycles": 1,
    }

    monkeypatch.setattr(
        entrypoint,
        "run_telegram_update_worker",
        MagicMock(
            return_value=summary
        ),
    )

    exit_code = entrypoint.main(
        [
            "--max-cycles",
            "1",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == (
        entrypoint.EXIT_OK
    )

    create_runtime.assert_called_once_with()

    assert captured[
        "runtime"
    ] is runtime

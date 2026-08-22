from __future__ import annotations

import io
import json
import logging

import pytest

from src.channels import (
    telegram_update_worker as worker,
)
from src.services.telegram_observability import (
    JsonTelegramOperationalEventSink,
    NoOpTelegramOperationalEventSink,
    TelegramOperationalEvent,
)


def remove_managed_handlers(
    logger: logging.Logger,
) -> None:
    for handler in list(
        logger.handlers
    ):
        if bool(
            getattr(
                handler,
                worker
                ._MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE,
                False,
            )
        ):
            logger.removeHandler(
                handler
            )

            handler.close()


@pytest.fixture(autouse=True)
def clean_operational_logger():
    logger = logging.getLogger(
        worker._TELEGRAM_OPERATIONAL_LOGGER_NAME
    )

    remove_managed_handlers(
        logger
    )

    original_level = logger.level
    original_propagate = logger.propagate

    yield

    remove_managed_handlers(
        logger
    )

    logger.setLevel(
        original_level
    )

    logger.propagate = (
        original_propagate
    )


@pytest.mark.parametrize(
    (
        "name",
        "expected",
    ),
    [
        ("DEBUG", logging.DEBUG),
        ("debug", logging.DEBUG),
        ("INFO", logging.INFO),
        ("warning", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("critical", logging.CRITICAL),
    ],
)
def test_resolve_log_level(
    name,
    expected,
):
    assert (
        worker
        ._resolve_telegram_operational_log_level(
            name
        )
        == expected
    )


def test_invalid_log_level_is_rejected():
    with pytest.raises(
        worker.TelegramUpdateRunnerConfigurationError,
    ):
        worker._resolve_telegram_operational_log_level(
            "verbose"
        )


def test_log_level_can_come_from_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "TELEGRAM_OPERATIONAL_LOG_LEVEL",
        "ERROR",
    )

    assert (
        worker
        ._resolve_telegram_operational_log_level(
            None
        )
        == logging.ERROR
    )


def test_factory_returns_json_sink():
    sink = (
        worker.create_production_telegram_event_sink(
            stream=io.StringIO(),
            level_name="INFO",
        )
    )

    assert isinstance(
        sink,
        JsonTelegramOperationalEventSink,
    )


def test_logger_is_dedicated_and_non_propagating():
    stream = io.StringIO()

    sink = (
        worker.create_production_telegram_event_sink(
            stream=stream,
            level_name="WARNING",
        )
    )

    logger = sink.logger

    assert logger.name == (
        "inna.telegram.operations"
    )

    assert logger.propagate is False
    assert logger.level == logging.WARNING


def test_factory_does_not_duplicate_handler():
    stream = io.StringIO()

    first = (
        worker.create_production_telegram_event_sink(
            stream=stream,
            level_name="INFO",
        )
    )

    second = (
        worker.create_production_telegram_event_sink(
            stream=stream,
            level_name="INFO",
        )
    )

    assert first.logger is second.logger

    managed = [
        handler
        for handler in first.logger.handlers
        if bool(
            getattr(
                handler,
                worker
                ._MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE,
                False,
            )
        )
    ]

    assert len(managed) == 1


def test_factory_replaces_managed_handler_for_new_stream():
    first_stream = io.StringIO()
    second_stream = io.StringIO()

    first = (
        worker.create_production_telegram_event_sink(
            stream=first_stream,
            level_name="INFO",
        )
    )

    second = (
        worker.create_production_telegram_event_sink(
            stream=second_stream,
            level_name="INFO",
        )
    )

    managed = [
        handler
        for handler in second.logger.handlers
        if bool(
            getattr(
                handler,
                worker
                ._MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE,
                False,
            )
        )
    ]

    assert len(managed) == 1
    assert managed[0].stream is second_stream
    assert first.logger is second.logger


def test_sink_writes_one_json_line():
    stream = io.StringIO()

    sink = (
        worker.create_production_telegram_event_sink(
            stream=stream,
            level_name="DEBUG",
        )
    )

    sink.emit(
        TelegramOperationalEvent(
            name="telegram_worker_started",
            level="info",
            component="worker",
            outcome="success",
            fields={
                "operation": "process_update",
            },
        )
    )

    output = stream.getvalue()

    assert output.endswith(
        "\n"
    )

    lines = output.splitlines()

    assert len(lines) == 1

    parsed = json.loads(
        lines[0]
    )

    assert parsed["event"] == (
        "telegram_worker_started"
    )

    assert parsed["component"] == "worker"


def test_default_loader_sink_remains_noop(
    monkeypatch,
):
    captured = {}

    class FakeBridge:
        pass

    def fake_bridge_factory(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return FakeBridge()

    monkeypatch.setattr(
        "api.telegram_webhook.process_telegram_update",
        lambda update, **kwargs: {
            "update": update,
            "kwargs": kwargs,
        },
    )

    monkeypatch.setattr(
        (
            "src.services.telegram_conversation_state."
            "create_postgres_telegram_webhook_"
            "conversation_bridge"
        ),
        fake_bridge_factory,
    )

    processor = (
        worker.load_telegram_processor()
    )

    assert callable(
        processor
    )

    assert isinstance(
        captured["event_sink"],
        NoOpTelegramOperationalEventSink,
    )


def test_factory_accepts_injected_logger():
    logger = logging.Logger(
        "custom.telegram.logger"
    )

    stream = io.StringIO()

    sink = (
        worker.create_production_telegram_event_sink(
            logger=logger,
            stream=stream,
            level_name="INFO",
        )
    )

    assert sink.logger is logger
    assert logger.propagate is False


def test_factory_rejects_invalid_logger():
    with pytest.raises(
        worker.TelegramUpdateRunnerConfigurationError,
    ):
        worker.create_production_telegram_event_sink(
            logger=object(),
        )

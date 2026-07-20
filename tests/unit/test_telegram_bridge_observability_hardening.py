from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from src.services.telegram_conversation_state.webhook_bridge import (
    TelegramWebhookConversationBridge,
    _observe_bridge_operation,
)
from src.services.telegram_observability import (
    NoOpTelegramConversationMetrics,
    NoOpTelegramOperationalEventSink,
)


ROOT = Path(__file__).resolve().parents[2]

BRIDGE_FILE = (
    ROOT
    / "src"
    / "services"
    / "telegram_conversation_state"
    / "webhook_bridge.py"
)


class RaisingClock:
    def __call__(self) -> float:
        raise RuntimeError(
            "clock unavailable"
        )


class RegressiveClock:
    def __init__(self) -> None:
        self._values = iter(
            (
                10.0,
                9.0,
            )
        )

    def __call__(self) -> float:
        return next(
            self._values
        )


class SequenceClock:
    def __init__(
        self,
        *values: float,
    ) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(
            self._values
        )


class CountingMetrics:
    def __init__(self) -> None:
        self.records = []

    def record_operation(
        self,
        record,
    ) -> None:
        self.records.append(record)


class CountingEvents:
    def __init__(self) -> None:
        self.events = []

    def emit(
        self,
        event,
    ) -> None:
        self.events.append(event)


class BrokenMetrics:
    def record_operation(
        self,
        record,
    ) -> None:
        del record

        raise RuntimeError(
            "metrics failed"
        )


class BrokenEvents:
    def emit(
        self,
        event,
    ) -> None:
        del event

        raise RuntimeError(
            "events failed"
        )


class ObservedOperation:
    def __init__(
        self,
        *,
        clock,
        metrics=None,
        event_sink=None,
        failure: BaseException | None = None,
    ) -> None:
        self.clock = clock

        self.metrics = (
            metrics
            if metrics is not None
            else CountingMetrics()
        )

        self.event_sink = (
            event_sink
            if event_sink is not None
            else CountingEvents()
        )

        self.failure = failure

    @_observe_bridge_operation(
        "load_or_open_session"
    )
    def execute(self):
        if self.failure is not None:
            raise self.failure

        return {
            "status": "ok",
        }


class TelegramConversationStateUnavailableError(
    RuntimeError
):
    pass


class TelegramConversationStateValidationError(
    RuntimeError
):
    pass


def test_regressive_clock_is_clamped_to_zero():
    operation = ObservedOperation(
        clock=RegressiveClock()
    )

    assert operation.execute() == {
        "status": "ok",
    }

    record = operation.metrics.records[0]
    event = operation.event_sink.events[0]

    assert record.duration_ms == 0.0

    assert (
        event.fields["duration_ms"]
        == 0.0
    )


def test_clock_failure_does_not_break_success():
    operation = ObservedOperation(
        clock=RaisingClock()
    )

    assert operation.execute() == {
        "status": "ok",
    }

    record = operation.metrics.records[0]

    assert record.outcome == "success"
    assert record.duration_ms == 0.0


def test_clock_failure_does_not_mask_original_error():
    expected = RuntimeError(
        "original operation failure"
    )

    operation = ObservedOperation(
        clock=RaisingClock(),
        failure=expected,
    )

    with pytest.raises(
        RuntimeError,
    ) as captured:
        operation.execute()

    assert captured.value is expected


def test_broken_telemetry_does_not_change_success():
    operation = ObservedOperation(
        clock=SequenceClock(
            1.0,
            1.01,
        ),
        metrics=BrokenMetrics(),
        event_sink=BrokenEvents(),
    )

    assert operation.execute() == {
        "status": "ok",
    }


def test_broken_telemetry_does_not_mask_error():
    expected = ValueError(
        "sensitive internal value"
    )

    operation = ObservedOperation(
        clock=SequenceClock(
            1.0,
            1.01,
        ),
        metrics=BrokenMetrics(),
        event_sink=BrokenEvents(),
        failure=expected,
    )

    with pytest.raises(
        ValueError,
    ) as captured:
        operation.execute()

    assert captured.value is expected


@pytest.mark.parametrize(
    (
        "error",
        "expected_category",
    ),
    [
        (
            TelegramConversationStateUnavailableError(),
            "unavailable",
        ),
        (
            TelegramConversationStateValidationError(),
            "validation",
        ),
        (
            TimeoutError(),
            "timeout",
        ),
        (
            RuntimeError(),
            "unknown",
        ),
    ],
)
def test_error_categories_are_sanitized(
    error,
    expected_category,
):
    operation = ObservedOperation(
        clock=SequenceClock(
            5.0,
            5.005,
        ),
        failure=error,
    )

    with pytest.raises(
        type(error),
    ):
        operation.execute()

    record = operation.metrics.records[0]
    event = operation.event_sink.events[0]

    assert (
        record.error_category
        == expected_category
    )

    assert (
        event.fields["error_category"]
        == expected_category
    )


def test_exception_message_is_not_emitted():
    sensitive_message = (
        "postgresql://admin:secret@internal-db/"
        "message-from-user"
    )

    operation = ObservedOperation(
        clock=SequenceClock(
            1.0,
            1.1,
        ),
        failure=RuntimeError(
            sensitive_message
        ),
    )

    with pytest.raises(RuntimeError):
        operation.execute()

    event = operation.event_sink.events[0]

    serialized = repr(
        dict(event.fields)
    )

    assert sensitive_message not in serialized
    assert "internal-db" not in serialized
    assert "message-from-user" not in serialized


def test_exactly_one_metric_and_event_per_success():
    operation = ObservedOperation(
        clock=SequenceClock(
            2.0,
            2.01,
        )
    )

    operation.execute()

    assert len(
        operation.metrics.records
    ) == 1

    assert len(
        operation.event_sink.events
    ) == 1


def test_exactly_one_metric_and_event_per_error():
    operation = ObservedOperation(
        clock=SequenceClock(
            2.0,
            2.01,
        ),
        failure=RuntimeError(
            "failure"
        ),
    )

    with pytest.raises(RuntimeError):
        operation.execute()

    assert len(
        operation.metrics.records
    ) == 1

    assert len(
        operation.event_sink.events
    ) == 1


def test_bridge_defaults_are_noop():
    bridge = TelegramWebhookConversationBridge(
        runtime_factory=lambda: object(),
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


def test_public_method_signatures_remain_stable():
    expected_parameters = {
        "load_or_open_session": [
            "self",
            "telegram_user_id",
            "chat_id",
            "initial_state",
            "language",
            "ttl_seconds",
        ],
        "save_session": [
            "self",
            "session",
            "ttl_seconds",
            "only_if_changed",
        ],
        "reload_session": [
            "self",
            "session",
        ],
        "delete_session": [
            "self",
            "session",
        ],
        "resolve_language": [
            "self",
            "telegram_user_id",
            "chat_id",
            "fallback_language",
        ],
    }

    for name, expected in (
        expected_parameters.items()
    ):
        method = getattr(
            TelegramWebhookConversationBridge,
            name,
        )

        signature = inspect.signature(
            method
        )

        assert list(
            signature.parameters
        ) == expected


def test_observed_methods_use_wraps_metadata():
    expected = {
        "load_or_open_session",
        "save_session",
        "reload_session",
        "delete_session",
        "resolve_language",
    }

    for name in expected:
        method = getattr(
            TelegramWebhookConversationBridge,
            name,
        )

        assert method.__name__ == name

        assert hasattr(
            method,
            "__wrapped__",
        )


def test_bridge_observability_has_no_sensitive_metric_fields():
    source = BRIDGE_FILE.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(BRIDGE_FILE),
    )

    forbidden_keywords = {
        "message_text",
        "payload",
        "financial_data",
        "renda",
        "gastos",
        "dividas",
        "database_url",
        "token",
        "secret",
    }

    violations = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        call_name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            call_name = node.func.id

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            call_name = node.func.attr

        if call_name not in {
            "TelegramConversationMetricRecord",
            "TelegramOperationalEvent",
            "sanitize_event_fields",
        }:
            continue

        text = ast.unparse(
            node
        ).lower()

        found = sorted(
            keyword
            for keyword
            in forbidden_keywords
            if keyword in text
        )

        if found:
            violations.append(
                {
                    "line": node.lineno,
                    "keywords": found,
                }
            )

    assert violations == []

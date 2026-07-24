from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.services.telegram_conversation_state.webhook_bridge import (
    _observe_bridge_operation,
)
from src.services.telegram_observability import (
    InMemoryTelegramConversationMetrics,
    InMemoryTelegramOperationalEventSink,
)


ROOT = Path(__file__).resolve().parents[2]

BRIDGE_FILE = (
    ROOT
    / "src"
    / "services"
    / "telegram_conversation_state"
    / "webhook_bridge.py"
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


class DummyBridge:
    def __init__(
        self,
        *,
        clock,
        should_fail: bool = False,
        error: Exception | None = None,
    ) -> None:
        self.metrics = (
            InMemoryTelegramConversationMetrics()
        )

        self.event_sink = (
            InMemoryTelegramOperationalEventSink()
        )

        self.clock = clock
        self.should_fail = should_fail
        self.error = error

    @_observe_bridge_operation(
        "save_session"
    )
    def save(self):
        if self.should_fail:
            raise (
                self.error
                or RuntimeError("failure")
            )

        return "saved"


class BrokenMetrics:
    def record_operation(
        self,
        record,
    ) -> None:
        del record
        raise RuntimeError(
            "metrics unavailable"
        )


class BrokenEventSink:
    def emit(
        self,
        event,
    ) -> None:
        del event
        raise RuntimeError(
            "event sink unavailable"
        )


class TelemetryFailureBridge:
    def __init__(self) -> None:
        self.metrics = BrokenMetrics()
        self.event_sink = BrokenEventSink()
        self.clock = SequenceClock(
            10.0,
            10.01,
        )

    @_observe_bridge_operation(
        "reload_session"
    )
    def reload(self):
        return "reloaded"


class TelegramConversationStateConflictError(
    RuntimeError
):
    pass


def test_bridge_observer_records_success():
    bridge = DummyBridge(
        clock=SequenceClock(
            5.0,
            5.025,
        )
    )

    assert bridge.save() == "saved"

    records = bridge.metrics.snapshot()
    events = bridge.event_sink.snapshot()

    assert len(records) == 1
    assert records[0].operation == "save_session"
    assert records[0].component == "bridge"
    assert records[0].outcome == "success"
    assert records[0].duration_ms == pytest.approx(
        25.0
    )

    assert len(events) == 1
    assert (
        events[0].name
        == "telegram_session_save_completed"
    )
    assert events[0].outcome == "success"


def test_bridge_observer_records_error_and_reraises():
    expected = RuntimeError(
        "database internal details"
    )

    bridge = DummyBridge(
        clock=SequenceClock(
            2.0,
            2.01,
        ),
        should_fail=True,
        error=expected,
    )

    with pytest.raises(
        RuntimeError,
    ) as captured:
        bridge.save()

    assert captured.value is expected

    record = bridge.metrics.snapshot()[0]
    event = bridge.event_sink.snapshot()[0]

    assert record.outcome == "error"
    assert record.error_category == "unknown"
    assert event.outcome == "error"

    assert (
        "database internal details"
        not in repr(event.fields)
    )


def test_bridge_observer_records_conflict():
    bridge = DummyBridge(
        clock=SequenceClock(
            1.0,
            1.005,
        ),
        should_fail=True,
        error=(
            TelegramConversationStateConflictError(
                "conflict"
            )
        ),
    )

    with pytest.raises(
        TelegramConversationStateConflictError,
    ):
        bridge.save()

    record = bridge.metrics.snapshot()[0]
    event = bridge.event_sink.snapshot()[0]

    assert record.outcome == "conflict"
    assert (
        record.error_category
        == "optimistic_conflict"
    )
    assert record.conflict_recovered is False

    assert (
        event.name
        == "telegram_session_save_conflict"
    )
    assert event.level == "warning"


def test_telemetry_failure_does_not_change_result():
    bridge = TelemetryFailureBridge()

    assert bridge.reload() == "reloaded"


def test_five_bridge_operations_are_decorated():
    source = BRIDGE_FILE.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(BRIDGE_FILE),
    )

    target_class = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
        and node.name
        == "TelegramWebhookConversationBridge"
    )

    expected = {
        "load_or_open_session",
        "save_session",
        "reload_session",
        "delete_session",
        "resolve_language",
    }

    decorated = set()

    for node in target_class.body:
        if not isinstance(
            node,
            ast.FunctionDef,
        ):
            continue

        for decorator in node.decorator_list:
            text = ast.unparse(
                decorator
            )

            if text.startswith(
                "_observe_bridge_operation"
            ):
                decorated.add(
                    node.name
                )

    assert decorated == expected


def test_bridge_has_injected_observability_fields():
    source = BRIDGE_FILE.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(BRIDGE_FILE),
    )

    target_class = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
        and node.name
        == "TelegramWebhookConversationBridge"
    )

    fields = {
        node.target.id
        for node in target_class.body
        if isinstance(
            node,
            ast.AnnAssign,
        )
        and isinstance(
            node.target,
            ast.Name,
        )
    }

    assert {
        "metrics",
        "event_sink",
        "clock",
    }.issubset(fields)

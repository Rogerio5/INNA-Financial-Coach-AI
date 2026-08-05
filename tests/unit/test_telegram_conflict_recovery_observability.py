from __future__ import annotations

import pytest

from api.telegram_webhook import (
    _sync_and_save_durable_telegram_session,
)
from src.services.telegram_conversation_state import (
    TelegramConversationStateConflictError,
)
from src.services.telegram_observability import (
    InMemoryTelegramConversationMetrics,
    InMemoryTelegramOperationalEventSink,
)


class FakeSession:
    def __init__(self) -> None:
        self.states = []
        self.languages = []

    def replace_state(
        self,
        state,
    ) -> None:
        self.states.append(dict(state))

    def set_language(
        self,
        language,
    ) -> None:
        self.languages.append(language)


class FakeBridge:
    def __init__(
        self,
        *,
        saves,
        reload_result=None,
        reload_error=None,
    ) -> None:
        self.metrics = InMemoryTelegramConversationMetrics()

        self.event_sink = InMemoryTelegramOperationalEventSink()

        self._clock_value = 1.0
        self._saves = iter(saves)

        self.reload_result = reload_result
        self.reload_error = reload_error

        self.save_calls = 0
        self.reload_calls = 0

    def clock(self) -> float:
        self._clock_value += 0.01
        return self._clock_value

    def save_session(
        self,
        session,
        *,
        only_if_changed=True,
    ):
        del session
        assert only_if_changed is True

        self.save_calls += 1

        result = next(self._saves)

        if isinstance(
            result,
            BaseException,
        ):
            raise result

        return result

    def reload_session(
        self,
        session,
    ):
        del session

        self.reload_calls += 1

        if self.reload_error is not None:
            raise self.reload_error

        return self.reload_result


def event_names(
    bridge: FakeBridge,
) -> list[str]:
    return [event.name for event in bridge.event_sink.snapshot()]


def metric_summary(
    bridge: FakeBridge,
):
    return [
        (
            metric.operation,
            metric.outcome,
            metric.conflict_recovered,
        )
        for metric in bridge.metrics.snapshot()
    ]


def test_conflict_is_recovered():
    original = FakeSession()
    reloaded = FakeSession()
    recovered = FakeSession()

    bridge = FakeBridge(
        saves=[
            TelegramConversationStateConflictError("first conflict"),
            recovered,
        ],
        reload_result=reloaded,
    )

    result = _sync_and_save_durable_telegram_session(
        conversation_bridge=bridge,
        durable_session=original,
        processing_state={
            "lang": "pt-BR",
            "step": "completed",
        },
    )

    assert result is recovered
    assert bridge.save_calls == 2
    assert bridge.reload_calls == 1

    assert reloaded.states == [
        {
            "lang": "pt-BR",
            "step": "completed",
        }
    ]

    assert event_names(bridge) == [
        "telegram_session_conflict_detected",
        ("telegram_session_conflict_reload_completed"),
        "telegram_session_conflict_recovered",
    ]

    assert metric_summary(bridge) == [
        (
            "save_session",
            "conflict",
            False,
        ),
        (
            "reload_session",
            "success",
            None,
        ),
        (
            "save_session",
            "recovered",
            True,
        ),
    ]


def test_reload_none_records_failure():
    original_conflict = TelegramConversationStateConflictError("conflict")

    bridge = FakeBridge(
        saves=[
            original_conflict,
        ],
        reload_result=None,
    )

    with pytest.raises(
        TelegramConversationStateConflictError,
    ) as captured:
        _sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=FakeSession(),
            processing_state={},
        )

    assert captured.value is original_conflict

    assert event_names(bridge)[-1] == ("telegram_session_conflict_failed")

    last_metric = bridge.metrics.snapshot()[-1]

    assert last_metric.operation == "reload_session"
    assert last_metric.outcome == "error"
    assert last_metric.error_category == "persistence"


def test_reload_error_is_preserved():
    expected = RuntimeError("reload failure")

    bridge = FakeBridge(
        saves=[TelegramConversationStateConflictError("conflict")],
        reload_error=expected,
    )

    with pytest.raises(
        RuntimeError,
    ) as captured:
        _sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=FakeSession(),
            processing_state={},
        )

    assert captured.value is expected

    assert event_names(bridge)[-1] == ("telegram_session_conflict_failed")


def test_second_conflict_records_failure():
    second_conflict = TelegramConversationStateConflictError("second conflict")

    bridge = FakeBridge(
        saves=[
            TelegramConversationStateConflictError("first conflict"),
            second_conflict,
        ],
        reload_result=FakeSession(),
    )

    with pytest.raises(
        TelegramConversationStateConflictError,
    ) as captured:
        _sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=FakeSession(),
            processing_state={},
        )

    assert captured.value is second_conflict

    assert event_names(bridge)[-1] == ("telegram_session_conflict_failed")

    last_metric = bridge.metrics.snapshot()[-1]

    assert last_metric.operation == "save_session"
    assert last_metric.outcome == "conflict"
    assert last_metric.conflict_recovered is False


def test_second_non_conflict_failure_is_preserved():
    expected = RuntimeError("persistence failed")

    bridge = FakeBridge(
        saves=[
            TelegramConversationStateConflictError("first conflict"),
            expected,
        ],
        reload_result=FakeSession(),
    )

    with pytest.raises(
        RuntimeError,
    ) as captured:
        _sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=FakeSession(),
            processing_state={},
        )

    assert captured.value is expected

    last_metric = bridge.metrics.snapshot()[-1]

    assert last_metric.operation == "save_session"
    assert last_metric.outcome == "error"


def test_non_conflict_initial_error_does_not_recover():
    expected = RuntimeError("normal failure")

    bridge = FakeBridge(
        saves=[
            expected,
        ],
    )

    with pytest.raises(
        RuntimeError,
    ) as captured:
        _sync_and_save_durable_telegram_session(
            conversation_bridge=bridge,
            durable_session=FakeSession(),
            processing_state={},
        )

    assert captured.value is expected
    assert bridge.save_calls == 1
    assert bridge.reload_calls == 0
    assert bridge.metrics.snapshot() == ()
    assert bridge.event_sink.snapshot() == ()


class BrokenMetrics:
    def record_operation(
        self,
        record,
    ) -> None:
        del record

        raise RuntimeError("metrics unavailable")


class BrokenEventSink:
    def emit(
        self,
        event,
    ) -> None:
        del event

        raise RuntimeError("event sink unavailable")


def test_telemetry_failure_does_not_break_recovery():
    recovered = FakeSession()

    bridge = FakeBridge(
        saves=[
            TelegramConversationStateConflictError("conflict"),
            recovered,
        ],
        reload_result=FakeSession(),
    )

    bridge.metrics = BrokenMetrics()
    bridge.event_sink = BrokenEventSink()

    result = _sync_and_save_durable_telegram_session(
        conversation_bridge=bridge,
        durable_session=FakeSession(),
        processing_state={
            "lang": "pt-BR",
        },
    )

    assert result is recovered
    assert bridge.save_calls == 2
    assert bridge.reload_calls == 1

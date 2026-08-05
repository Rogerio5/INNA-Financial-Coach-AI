from __future__ import annotations

import pytest

from src.services.telegram_observability import (
    TelegramConversationMetricRecord,
    TelegramOperationalEvent,
)


def test_metric_record_accepts_valid_operation():
    record = TelegramConversationMetricRecord(
        operation="save_session",
        component="bridge",
        outcome="success",
        duration_ms=12.5,
    )

    assert record.operation == "save_session"
    assert record.component == "bridge"
    assert record.outcome == "success"
    assert record.duration_ms == 12.5


def test_metric_record_requires_error_category_for_error():
    with pytest.raises(
        ValueError,
        match="error_category",
    ):
        TelegramConversationMetricRecord(
            operation="save_session",
            component="bridge",
            outcome="error",
            duration_ms=1,
        )


@pytest.mark.parametrize(
    "duration",
    [
        -1,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_metric_record_rejects_invalid_duration(
    duration,
):
    with pytest.raises(ValueError):
        TelegramConversationMetricRecord(
            operation="save_session",
            component="bridge",
            outcome="success",
            duration_ms=duration,
        )


def test_event_requires_telegram_prefix():
    with pytest.raises(
        ValueError,
        match="telegram_",
    ):
        TelegramOperationalEvent(
            name="session_saved",
            level="info",
            component="bridge",
            outcome="success",
        )


def test_event_fields_are_immutable():
    event = TelegramOperationalEvent(
        name="telegram_session_save_completed",
        level="info",
        component="bridge",
        outcome="success",
        fields={
            "duration_ms": 10,
        },
    )

    with pytest.raises(TypeError):
        event.fields["duration_ms"] = 20

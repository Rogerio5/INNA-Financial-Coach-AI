from __future__ import annotations

import json
import logging
import math

from datetime import (
    datetime,
    timezone,
)

import pytest

from src.services.telegram_observability import (
    JsonTelegramOperationalEventSink,
    TelegramOperationalEvent,
    build_telegram_structured_log_payload,
    format_telegram_log_timestamp,
    serialize_telegram_structured_log,
)


class CapturingHandler(
    logging.Handler
):
    def __init__(self) -> None:
        super().__init__()

        self.records = []

    def emit(
        self,
        record,
    ) -> None:
        self.records.append(
            record
        )


class FixedClock:
    def __call__(self) -> datetime:
        return datetime(
            2026,
            7,
            20,
            3,
            15,
            0,
            123456,
            tzinfo=timezone.utc,
        )


class UnsafeObject:
    def __repr__(self) -> str:
        return (
            "postgresql://admin:"
            "secret@internal-db/value"
        )


def make_event(
    *,
    level: str = "warning",
    fields=None,
) -> TelegramOperationalEvent:
    return TelegramOperationalEvent(
        name=(
            "telegram_session_"
            "conflict_detected"
        ),
        level=level,
        component="webhook",
        outcome="conflict",
        fields=(
            fields
            if fields is not None
            else {
                "operation": "save_session",
                "error_category": (
                    "optimistic_conflict"
                ),
                "conflict_recovered": False,
            }
        ),
    )


def make_logger():
    logger = logging.Logger(
        "test.telegram.structured"
    )

    logger.setLevel(
        logging.DEBUG
    )

    logger.propagate = False

    handler = CapturingHandler()

    logger.addHandler(
        handler
    )

    return logger, handler


def test_timestamp_is_utc_with_milliseconds():
    value = format_telegram_log_timestamp(
        datetime(
            2026,
            7,
            20,
            0,
            15,
            0,
            987654,
            tzinfo=timezone.utc,
        )
    )

    assert value == (
        "2026-07-20T00:15:00.987Z"
    )


def test_naive_datetime_is_rejected():
    with pytest.raises(
        ValueError,
    ):
        format_telegram_log_timestamp(
            datetime(
                2026,
                7,
                20,
                3,
                0,
            )
        )


def test_payload_has_canonical_schema():
    payload = (
        build_telegram_structured_log_payload(
            make_event(),
            timestamp=FixedClock()(),
        )
    )

    assert set(payload) == {
        "timestamp",
        "level",
        "event",
        "component",
        "outcome",
        "fields",
    }

    assert payload["timestamp"] == (
        "2026-07-20T03:15:00.123Z"
    )

    assert payload["level"] == "warning"
    assert payload["component"] == "webhook"
    assert payload["outcome"] == "conflict"


def test_serialization_is_one_line_json():
    serialized = (
        serialize_telegram_structured_log(
            make_event(),
            timestamp=FixedClock()(),
        )
    )

    assert "\n" not in serialized
    assert "\r" not in serialized

    parsed = json.loads(
        serialized
    )

    assert parsed["event"] == (
        "telegram_session_"
        "conflict_detected"
    )


def test_unicode_is_preserved():
    serialized = (
        serialize_telegram_structured_log(
            make_event(
                fields={
                    "operation": "persistência",
                }
            ),
            timestamp=FixedClock()(),
        )
    )

    assert "persistência" in serialized
    assert "\\u00ea" not in serialized


@pytest.mark.parametrize(
    (
        "level",
        "numeric_level",
    ),
    [
        (
            "debug",
            logging.DEBUG,
        ),
        (
            "info",
            logging.INFO,
        ),
        (
            "warning",
            logging.WARNING,
        ),
        (
            "error",
            logging.ERROR,
        ),
        (
            "critical",
            logging.CRITICAL,
        ),
    ],
)
def test_sink_maps_logging_levels(
    level,
    numeric_level,
):
    logger, handler = make_logger()

    sink = JsonTelegramOperationalEventSink(
        logger=logger,
        clock=FixedClock(),
    )

    sink.emit(
        make_event(
            level=level,
        )
    )

    assert len(
        handler.records
    ) == 1

    assert (
        handler.records[0].levelno
        == numeric_level
    )


def test_sink_emits_exactly_one_record():
    logger, handler = make_logger()

    sink = JsonTelegramOperationalEventSink(
        logger=logger,
        clock=FixedClock(),
    )

    sink.emit(
        make_event()
    )

    assert len(
        handler.records
    ) == 1

    parsed = json.loads(
        handler.records[0].getMessage()
    )

    assert parsed["timestamp"] == (
        "2026-07-20T03:15:00.123Z"
    )


def test_non_serializable_value_uses_safe_marker():
    serialized = (
        serialize_telegram_structured_log(
            make_event(
                fields={
                    "unsafe": UnsafeObject(),
                }
            ),
            timestamp=FixedClock()(),
        )
    )

    assert (
        "<non-serializable>"
        in serialized
    )

    assert "internal-db" not in serialized
    assert "secret" not in serialized


@pytest.mark.parametrize(
    "value",
    [
        math.nan,
        math.inf,
        -math.inf,
    ],
)
def test_non_finite_numbers_are_replaced(
    value,
):
    serialized = (
        serialize_telegram_structured_log(
            make_event(
                fields={
                    "duration": value,
                }
            ),
            timestamp=FixedClock()(),
        )
    )

    assert (
        "<non-finite-number>"
        in serialized
    )

    parsed = json.loads(
        serialized
    )

    assert parsed[
        "fields"
    ][
        "duration"
    ] == "<non-finite-number>"


def test_recursive_value_is_safe():
    recursive = {}
    recursive["self"] = recursive

    serialized = (
        serialize_telegram_structured_log(
            make_event(
                fields={
                    "recursive": recursive,
                }
            ),
            timestamp=FixedClock()(),
        )
    )

    assert (
        "<recursive-value>"
        in serialized
    )


def test_sensitive_fields_are_removed():
    serialized = (
        serialize_telegram_structured_log(
            make_event(
                fields={
                    "operation": "save_session",
                    "telegram_user_id": 123,
                    "chat_id": 456,
                    "token": "super-secret",
                    "message_text": (
                        "texto financeiro privado"
                    ),
                }
            ),
            timestamp=FixedClock()(),
        )
    )

    lowered = serialized.lower()

    assert "telegram_user_id" not in lowered
    assert "chat_id" not in lowered
    assert "super-secret" not in lowered
    assert "texto financeiro privado" not in lowered
    assert "save_session" in serialized


def test_invalid_event_is_rejected():
    logger, _ = make_logger()

    sink = JsonTelegramOperationalEventSink(
        logger=logger,
        clock=FixedClock(),
    )

    with pytest.raises(
        TypeError,
    ):
        sink.emit(
            object()
        )


def test_invalid_logger_is_rejected():
    with pytest.raises(
        TypeError,
    ):
        JsonTelegramOperationalEventSink(
            logger=object(),
        )


def test_invalid_clock_result_is_rejected():
    logger, _ = make_logger()

    sink = JsonTelegramOperationalEventSink(
        logger=logger,
        clock=lambda: "not-a-datetime",
    )

    with pytest.raises(
        TypeError,
    ):
        sink.emit(
            make_event()
        )

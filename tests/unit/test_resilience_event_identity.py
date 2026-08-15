from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.resilience import (
    OperationKind,
    ResilienceEvent,
    ResilienceEventType,
    ResiliencePolicy,
    ResilienceRuntime,
)


def _event(
    **overrides,
) -> ResilienceEvent:
    values = {
        "operation": "gemini.embedding",
        "event_type": (
            ResilienceEventType
            .OPERATION_SUCCEEDED
        ),
        "attempt_number": 1,
        "max_attempts": 2,
    }

    values.update(overrides)

    return ResilienceEvent(
        **values
    )


def test_event_has_unique_technical_identity():
    first = _event()
    second = _event()

    assert first.event_id
    assert second.event_id
    assert first.event_id != second.event_id

    assert len(first.event_id) == 32
    assert len(second.event_id) == 32


def test_event_timestamp_is_timezone_aware_utc():
    event = _event()

    assert isinstance(
        event.occurred_at,
        datetime,
    )

    assert (
        event.occurred_at.tzinfo
        is UTC
    )


def test_explicit_event_id_is_preserved():
    event = _event(
        event_id="reliability-event-001",
    )

    assert (
        event.event_id
        == "reliability-event-001"
    )


def test_non_utc_aware_timestamp_is_normalized_to_utc():
    from datetime import (
        timedelta,
        timezone,
    )

    source = datetime(
        2026,
        8,
        15,
        1,
        0,
        tzinfo=timezone(
            timedelta(hours=-3)
        ),
    )

    event = _event(
        occurred_at=source
    )

    assert event.occurred_at.tzinfo is UTC

    assert event.occurred_at == datetime(
        2026,
        8,
        15,
        4,
        0,
        tzinfo=UTC,
    )


def test_naive_timestamp_is_rejected():
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        _event(
            occurred_at=datetime(
                2026,
                8,
                15,
                4,
                0,
            )
        )


@pytest.mark.parametrize(
    "event_id",
    [
        "",
        " ",
        "x" * 129,
    ],
)
def test_invalid_event_id_is_rejected(
    event_id,
):
    with pytest.raises(ValueError):
        _event(
            event_id=event_id
        )


def test_runtime_terminal_event_has_real_identity():
    events = []

    runtime = ResilienceRuntime(
        observer=events.append,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    policy = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=1,
        circuit_failure_threshold=5,
    )

    result = runtime.execute(
        policy=policy,
        operation=lambda: "ok",
    )

    assert result == "ok"

    terminal = [
        event
        for event in events
        if event.event_type
        is ResilienceEventType
        .OPERATION_SUCCEEDED
    ]

    assert len(terminal) == 1

    event = terminal[0]

    assert event.event_id
    assert event.occurred_at.tzinfo is UTC


def test_runtime_failure_event_has_real_identity():
    events = []

    runtime = ResilienceRuntime(
        observer=events.append,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    policy = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=1,
        circuit_failure_threshold=5,
    )

    with pytest.raises(TimeoutError):
        runtime.execute(
            policy=policy,
            operation=lambda: (
                (_ for _ in ()).throw(
                    TimeoutError(
                        "private provider detail"
                    )
                )
            ),
        )

    terminal = [
        event
        for event in events
        if event.event_type
        is ResilienceEventType
        .OPERATION_FAILED
    ]

    assert len(terminal) == 1

    event = terminal[0]

    assert event.event_id
    assert event.occurred_at.tzinfo is UTC

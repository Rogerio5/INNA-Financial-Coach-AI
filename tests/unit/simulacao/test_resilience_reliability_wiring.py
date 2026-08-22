from __future__ import annotations

from src.observability import (
    resilience_tracing,
)
from src.resilience import (
    OperationKind,
    ResilienceEvent,
    ResilienceEventType,
    ResiliencePolicy,
)


def _event(
    event_type: ResilienceEventType,
) -> ResilienceEvent:
    return ResilienceEvent(
        operation="gemini.embedding",
        event_type=event_type,
        attempt_number=1,
        max_attempts=2,
    )


def test_runtime_observer_records_reliability_without_active_span(
    monkeypatch,
):
    recorded = []

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        recorded.append,
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: None,
    )

    resilience_tracing.observe_runtime_resilience_event(
        _event(
            ResilienceEventType
            .OPERATION_SUCCEEDED
        )
    )

    assert len(recorded) == 1

    assert (
        recorded[0].event_type
        is ResilienceEventType
        .OPERATION_SUCCEEDED
    )


def test_reliability_failure_does_not_break_otel(
    monkeypatch,
):
    class FakeSpan:
        def __init__(self):
            self.events = []

        def is_recording(self):
            return True

        def add_event(
            self,
            name,
            *,
            attributes=None,
        ):
            self.events.append(
                (
                    name,
                    attributes,
                )
            )

        def set_attribute(
            self,
            *_,
            **__,
        ):
            return None

    span = FakeSpan()

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        lambda _: (
            (_ for _ in ()).throw(
                RuntimeError(
                    "tracker unavailable"
                )
            )
        ),
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    resilience_tracing.observe_runtime_resilience_event(
        _event(
            ResilienceEventType
            .OPERATION_SUCCEEDED
        )
    )

    names = [
        name
        for name, _ in span.events
    ]

    assert (
        "inna.resilience.operation_succeeded"
        in names
    )


def test_created_runtime_uses_composite_observer(
    monkeypatch,
):
    recorded = []

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        recorded.append,
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: None,
    )

    runtime = (
        resilience_tracing
        .create_observed_resilience_runtime(
            sleeper=lambda _: None,
            random_source=lambda: 0.5,
        )
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
        for event in recorded
        if event.event_type
        in {
            ResilienceEventType
            .OPERATION_SUCCEEDED,
            ResilienceEventType
            .OPERATION_FAILED,
            ResilienceEventType
            .CIRCUIT_REJECTED,
        }
    ]

    assert len(terminal) == 1

    assert (
        terminal[0].event_type
        is ResilienceEventType
        .OPERATION_SUCCEEDED
    )


def test_retry_is_not_counted_as_multiple_logical_operations(
    monkeypatch,
):
    recorded = []

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        recorded.append,
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: None,
    )

    attempts = [0]

    def operation():
        attempts[0] += 1

        if attempts[0] == 1:
            raise TimeoutError(
                "provider detail"
            )

        return "ok"

    runtime = (
        resilience_tracing
        .create_observed_resilience_runtime(
            sleeper=lambda _: None,
            random_source=lambda: 0.5,
        )
    )

    policy = ResiliencePolicy(
        name="gemini.embedding",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=2,
        base_delay_seconds=0.01,
        max_delay_seconds=0.01,
        jitter_ratio=0.0,
        circuit_failure_threshold=5,
    )

    result = runtime.execute(
        policy=policy,
        operation=operation,
    )

    assert result == "ok"

    logical_terminal_events = [
        event
        for event in recorded
        if event.event_type
        in {
            ResilienceEventType
            .OPERATION_SUCCEEDED,
            ResilienceEventType
            .OPERATION_FAILED,
            ResilienceEventType
            .CIRCUIT_REJECTED,
        }
    ]

    assert len(
        logical_terminal_events
    ) == 1

    assert (
        logical_terminal_events[0]
        .event_type
        is ResilienceEventType
        .OPERATION_SUCCEEDED
    )



def test_composite_observer_forwards_to_async_ledger(
    monkeypatch,
):
    local_events = []
    ledger_events = []

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        local_events.append,
    )

    monkeypatch.setattr(
        resilience_tracing,
        (
            "observe_production_reliability_"
            "persistence_event"
        ),
        ledger_events.append,
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: None,
    )

    event = _event(
        ResilienceEventType
        .OPERATION_SUCCEEDED
    )

    (
        resilience_tracing
        .observe_runtime_resilience_event(
            event
        )
    )

    assert local_events == [event]
    assert ledger_events == [event]


def test_async_ledger_observer_failure_is_isolated(
    monkeypatch,
):
    local_events = []

    monkeypatch.setattr(
        resilience_tracing,
        "observe_production_reliability_event",
        local_events.append,
    )

    def fail(_):
        raise RuntimeError(
            "ledger unavailable"
        )

    monkeypatch.setattr(
        resilience_tracing,
        (
            "observe_production_reliability_"
            "persistence_event"
        ),
        fail,
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: None,
    )

    event = _event(
        ResilienceEventType
        .OPERATION_SUCCEEDED
    )

    (
        resilience_tracing
        .observe_runtime_resilience_event(
            event
        )
    )

    assert local_events == [event]

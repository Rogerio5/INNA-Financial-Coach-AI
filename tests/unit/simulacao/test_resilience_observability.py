from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.observability import (
    resilience_tracing,
)
from src.resilience import (
    FailureKind,
    OperationKind,
    ResilienceEvent,
    ResilienceEventType,
    ResiliencePolicy,
)
from src.resilience.policies import (
    GEMINI_EMBEDDING_POLICY,
    GEMINI_GENERATION_POLICY,
    LLAMAINDEX_AGENTIC_RAG_POLICY,
    RAG_QUERY_POLICY,
)


class FakeSpan:
    def __init__(
        self,
        *,
        recording: bool = True,
    ) -> None:
        self.recording = recording
        self.events = []
        self.attributes = {}

    def is_recording(
        self,
    ) -> bool:
        return self.recording

    def add_event(
        self,
        name,
        *,
        attributes=None,
    ) -> None:
        self.events.append(
            (
                name,
                dict(
                    attributes
                    or {}
                ),
            )
        )

    def set_attribute(
        self,
        name,
        value,
    ) -> None:
        self.attributes[
            name
        ] = value


def test_production_policies_are_read_only():
    policies = (
        GEMINI_EMBEDDING_POLICY,
        GEMINI_GENERATION_POLICY,
        RAG_QUERY_POLICY,
        LLAMAINDEX_AGENTIC_RAG_POLICY,
    )

    assert all(
        policy.operation_kind
        is OperationKind.READ_ONLY
        for policy in policies
    )


def test_production_policy_names_are_unique():
    policies = (
        GEMINI_EMBEDDING_POLICY,
        GEMINI_GENERATION_POLICY,
        RAG_QUERY_POLICY,
        LLAMAINDEX_AGENTIC_RAG_POLICY,
    )

    names = {
        policy.name
        for policy in policies
    }

    assert len(names) == len(
        policies
    )


def test_operation_attributes_are_content_safe():
    attributes = (
        resilience_tracing
        .build_resilience_operation_attributes(
            GEMINI_EMBEDDING_POLICY
        )
    )

    assert (
        attributes[
            "resilience.operation"
        ]
        == "gemini.embedding"
    )

    assert (
        attributes[
            "privacy.content_exported"
        ]
        is False
    )

    forbidden = {
        "prompt",
        "response",
        "contents",
        "message",
        "payload",
        "api_key",
    }

    normalized_keys = {
        str(key).lower()
        for key in attributes
    }

    assert forbidden.isdisjoint(
        normalized_keys
    )


def test_event_attributes_use_explicit_allowlist():
    event = ResilienceEvent(
        operation="gemini.embedding",
        event_type=(
            ResilienceEventType
            .RETRY_SCHEDULED
        ),
        attempt_number=1,
        max_attempts=3,
        failure_kind=(
            FailureKind.TIMEOUT
        ),
        error_type="TimeoutError",
        delay_seconds=0.25,
        circuit_state="closed",
        elapsed_ms=15.5,
    )

    attributes = (
        resilience_tracing
        .build_resilience_event_attributes(
            event
        )
    )

    assert attributes == {
        "resilience.operation": (
            "gemini.embedding"
        ),
        "resilience.event_type": (
            "retry_scheduled"
        ),
        "resilience.attempt.number": 1,
        "resilience.attempt.max": 3,
        "privacy.content_exported": False,
        "resilience.failure.kind": (
            "timeout"
        ),
        "resilience.error.type": (
            "TimeoutError"
        ),
        "resilience.retry.delay_seconds": (
            0.25
        ),
        "resilience.circuit.state": (
            "closed"
        ),
        "resilience.elapsed_ms": 15.5,
    }


def test_observer_adds_retry_event_to_current_span(
    monkeypatch,
):
    span = FakeSpan()

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    event = ResilienceEvent(
        operation="gemini.embedding",
        event_type=(
            ResilienceEventType
            .RETRY_SCHEDULED
        ),
        attempt_number=1,
        max_attempts=3,
        failure_kind=(
            FailureKind.TIMEOUT
        ),
        error_type="TimeoutError",
        delay_seconds=0.25,
        circuit_state="closed",
    )

    resilience_tracing.observe_resilience_event(
        event
    )

    assert len(span.events) == 1

    name, attributes = (
        span.events[0]
    )

    assert (
        name
        == "inna.resilience.retry_scheduled"
    )

    assert (
        attributes[
            "resilience.failure.kind"
        ]
        == "timeout"
    )


def test_success_event_marks_span_success(
    monkeypatch,
):
    span = FakeSpan()

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    event = ResilienceEvent(
        operation="rag.query",
        event_type=(
            ResilienceEventType
            .OPERATION_SUCCEEDED
        ),
        attempt_number=2,
        max_attempts=2,
    )

    resilience_tracing.observe_resilience_event(
        event
    )

    assert (
        span.attributes[
            "resilience.success"
        ]
        is True
    )

    assert (
        span.attributes[
            "resilience.final_attempt"
        ]
        == 2
    )


def test_circuit_rejection_marks_span(
    monkeypatch,
):
    span = FakeSpan()

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    event = ResilienceEvent(
        operation="rag.query",
        event_type=(
            ResilienceEventType
            .CIRCUIT_REJECTED
        ),
        attempt_number=1,
        max_attempts=2,
        circuit_state="open",
    )

    resilience_tracing.observe_resilience_event(
        event
    )

    assert (
        span.attributes[
            "resilience.success"
        ]
        is False
    )

    assert (
        span.attributes[
            "resilience.circuit.rejected"
        ]
        is True
    )


def test_non_recording_span_is_noop(
    monkeypatch,
):
    span = FakeSpan(
        recording=False
    )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    event = ResilienceEvent(
        operation="rag.query",
        event_type=(
            ResilienceEventType
            .ATTEMPT_STARTED
        ),
        attempt_number=1,
        max_attempts=2,
    )

    resilience_tracing.observe_resilience_event(
        event
    )

    assert span.events == []
    assert span.attributes == {}


def test_observer_failure_never_breaks_runtime(
    monkeypatch,
):
    class BrokenSpan:
        def is_recording(
            self,
        ):
            return True

        def add_event(
            self,
            *_,
            **__,
        ):
            raise RuntimeError(
                "telemetry unavailable"
            )

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: BrokenSpan(),
    )

    event = ResilienceEvent(
        operation="rag.query",
        event_type=(
            ResilienceEventType
            .ATTEMPT_STARTED
        ),
        attempt_number=1,
        max_attempts=2,
    )

    resilience_tracing.observe_resilience_event(
        event
    )


def test_traced_resilience_operation_reuses_existing_pipeline(
    monkeypatch,
):
    captured = {}

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes=None,
        instrumentation_name=None,
    ):
        captured["name"] = name
        captured["attributes"] = (
            dict(
                attributes
                or {}
            )
        )
        captured[
            "instrumentation_name"
        ] = instrumentation_name

        yield FakeSpan()

    monkeypatch.setattr(
        resilience_tracing,
        "traced_operation",
        fake_traced_operation,
    )

    with (
        resilience_tracing
        .traced_resilience_operation(
            GEMINI_EMBEDDING_POLICY
        )
    ):
        pass

    assert (
        captured["name"]
        == "inna.resilience.gemini.embedding"
    )

    assert (
        captured[
            "instrumentation_name"
        ]
        == "inna.resilience"
    )

    assert (
        captured["attributes"][
            "privacy.content_exported"
        ]
        is False
    )


def test_observed_runtime_emits_retry_and_success(
    monkeypatch,
):
    span = FakeSpan()

    monkeypatch.setattr(
        resilience_tracing.trace,
        "get_current_span",
        lambda: span,
    )

    sleeps = []
    attempts = 0

    def operation():
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise TimeoutError(
                "private provider detail"
            )

        return "ok"

    runtime = (
        resilience_tracing
        .create_observed_resilience_runtime(
            sleeper=sleeps.append,
            random_source=lambda: 0.5,
        )
    )

    policy = ResiliencePolicy(
        name="test.read",
        operation_kind=(
            OperationKind.READ_ONLY
        ),
        max_attempts=2,
        base_delay_seconds=0.25,
        max_delay_seconds=1.0,
        jitter_ratio=0.0,
        circuit_failure_threshold=5,
    )

    result = runtime.execute(
        policy=policy,
        operation=operation,
    )

    assert result == "ok"

    names = [
        name
        for name, _ in span.events
    ]

    assert (
        "inna.resilience.retry_scheduled"
        in names
    )

    assert (
        "inna.resilience.operation_succeeded"
        in names
    )

    serialized_events = repr(
        span.events
    )

    assert (
        "private provider detail"
        not in serialized_events
    )


def test_custom_observer_cannot_be_injected():
    with pytest.raises(
        TypeError,
        match="observer is managed",
    ):
        (
            resilience_tracing
            .create_observed_resilience_runtime(
                observer=lambda _: None
            )
        )


def test_shared_runtime_is_process_singleton():
    first = (
        resilience_tracing
        .get_shared_resilience_runtime()
    )

    second = (
        resilience_tracing
        .get_shared_resilience_runtime()
    )

    assert first is second

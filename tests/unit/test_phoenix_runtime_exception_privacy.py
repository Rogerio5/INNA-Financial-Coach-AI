from contextlib import contextmanager

import pytest

from src.observability import phoenix_runtime


class FakeSpan:
    def __init__(self):
        self.attributes = {}
        self.statuses = []
        self.recorded_exceptions = []

    def set_attribute(self, name, value):
        self.attributes[name] = value

    def set_status(self, status):
        self.statuses.append(status)

    def record_exception(self, exc):
        self.recorded_exceptions.append(exc)


class FakeTracer:
    def __init__(self):
        self.span = FakeSpan()
        self.calls = []

    @contextmanager
    def start_as_current_span(
        self,
        name,
        **kwargs,
    ):
        self.calls.append(
            {
                "name": name,
                **kwargs,
            }
        )

        yield self.span


def test_traced_operation_does_not_export_exception_content(
    monkeypatch,
):
    tracer = FakeTracer()

    monkeypatch.setattr(
        phoenix_runtime,
        "get_inna_tracer",
        lambda instrumentation_name: tracer,
    )

    private_marker = (
        "PRIVATE_EXCEPTION_CONTENT_DO_NOT_EXPORT"
    )

    with pytest.raises(
        RuntimeError,
        match=private_marker,
    ):
        with phoenix_runtime.traced_operation(
            "inna.test.private-error",
            attributes={
                "safe.operation": "unit-test",
            },
        ):
            raise RuntimeError(
                private_marker
            )

    assert len(
        tracer.calls
    ) == 1

    call = tracer.calls[0]

    assert (
        call["name"]
        == "inna.test.private-error"
    )

    assert (
        call["record_exception"]
        is False
    )

    assert (
        call["set_status_on_exception"]
        is False
    )

    assert (
        tracer.span.recorded_exceptions
        == []
    )

    assert (
        tracer.span.attributes[
            "operation.error_type"
        ]
        == "RuntimeError"
    )

    assert (
        tracer.span.attributes[
            "privacy.content_exported"
        ]
        is False
    )

    assert (
        "operation.duration_ms"
        in tracer.span.attributes
    )

    assert (
        private_marker
        not in str(
            tracer.span.attributes
        )
    )

    assert (
        private_marker
        not in str(
            tracer.span.statuses
        )
    )


def test_traced_operation_success_keeps_exception_capture_disabled(
    monkeypatch,
):
    tracer = FakeTracer()

    monkeypatch.setattr(
        phoenix_runtime,
        "get_inna_tracer",
        lambda instrumentation_name: tracer,
    )

    with phoenix_runtime.traced_operation(
        "inna.test.success"
    ):
        pass

    call = tracer.calls[0]

    assert (
        call["record_exception"]
        is False
    )

    assert (
        call["set_status_on_exception"]
        is False
    )

    assert (
        tracer.span.recorded_exceptions
        == []
    )

    assert (
        "operation.duration_ms"
        in tracer.span.attributes
    )

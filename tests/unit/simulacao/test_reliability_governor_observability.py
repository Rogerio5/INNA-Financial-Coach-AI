from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

import src.agentic_rag.planner as planner
import src.observability.resilience_tracing as tracing
import src.reliability.governor as governor


class _FakeSpan:
    def __init__(self):
        self.events = []

    def add_event(
        self,
        name,
        attributes=None,
    ):
        self.events.append(
            (
                name,
                dict(
                    attributes
                    or {}
                ),
            )
        )


def _decision():
    return SimpleNamespace(
        operation="rag.agentic.planner",
        action=SimpleNamespace(
            value="conservative_mode"
        ),
        reason_code="shared_critical",
        advisory_only=True,
        source=SimpleNamespace(
            value="shared_cache"
        ),
        state=SimpleNamespace(
            value="critical"
        ),
        shared_data_used=True,
        cache_stale=False,
        database_unavailable=False,
        current_max_attempts=2,
        recommended_max_attempts=1,
        prefer_fallback=True,
        burn_rate=10.0,
        prompt="must-not-appear",
        database_url="must-not-appear",
        user_id="must-not-appear",
    )


def test_governor_decision_observability_is_privacy_safe(
    monkeypatch,
):
    captured = {}
    span = _FakeSpan()

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        captured["name"] = name
        captured["attributes"] = dict(
            attributes
        )
        captured["instrumentation_name"] = (
            instrumentation_name
        )
        yield span

    monkeypatch.setattr(
        tracing,
        "traced_operation",
        fake_traced_operation,
    )

    tracing.observe_reliability_governor_decision(
        _decision()
    )

    attributes = captured[
        "attributes"
    ]

    assert (
        captured["name"]
        == "inna.reliability.governor"
    )

    assert (
        attributes[
            "reliability.governor.action"
        ]
        == "conservative_mode"
    )

    assert (
        attributes[
            (
                "reliability.governor."
                "recommended_max_attempts"
            )
        ]
        == 1
    )

    serialized = repr(
        attributes
    ).lower()

    assert "prompt" not in serialized
    assert "database_url" not in serialized
    assert "user_id" not in serialized
    assert "must-not-appear" not in serialized

    assert len(
        span.events
    ) == 1


def test_governor_fail_open_observability_is_privacy_safe(
    monkeypatch,
):
    captured = {}
    span = _FakeSpan()

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        captured["name"] = name
        captured["attributes"] = dict(
            attributes
        )
        captured["instrumentation_name"] = (
            instrumentation_name
        )
        yield span

    monkeypatch.setattr(
        tracing,
        "traced_operation",
        fake_traced_operation,
    )

    tracing.observe_reliability_governor_fail_open(
        operation="rag.agentic.planner",
        current_max_attempts=2,
        error_type="RuntimeError",
    )

    attributes = captured[
        "attributes"
    ]

    assert (
        attributes[
            "reliability.governor.fail_open"
        ]
        is True
    )

    assert (
        attributes[
            "reliability.governor.error_type"
        ]
        == "RuntimeError"
    )

    assert "error_message" not in attributes
    assert "exception_message" not in attributes

    assert len(
        span.events
    ) == 1


def test_planner_observes_governor_decision(
    monkeypatch,
):
    base_policy = SimpleNamespace(
        name="rag.agentic.planner",
        max_attempts=2,
    )

    effective_policy = object()
    decision = object()

    observed = []

    monkeypatch.setattr(
        planner,
        "_planner_governor_enforcement_enabled",
        lambda: True,
    )

    monkeypatch.setattr(
        governor,
        "get_reliability_governor_decision",
        lambda operation: decision,
    )

    monkeypatch.setattr(
        governor,
        "derive_effective_resilience_policy",
        lambda *,
        policy,
        decision: effective_policy,
    )

    monkeypatch.setattr(
        tracing,
        "observe_reliability_governor_decision",
        observed.append,
    )

    result = (
        planner
        ._resolve_planner_resilience_policy(
            base_policy
        )
    )

    assert result is effective_policy
    assert observed == [decision]


def test_observability_failure_does_not_change_policy(
    monkeypatch,
):
    base_policy = SimpleNamespace(
        name="rag.agentic.planner",
        max_attempts=2,
    )

    effective_policy = object()
    decision = object()

    monkeypatch.setattr(
        planner,
        "_planner_governor_enforcement_enabled",
        lambda: True,
    )

    monkeypatch.setattr(
        governor,
        "get_reliability_governor_decision",
        lambda operation: decision,
    )

    monkeypatch.setattr(
        governor,
        "derive_effective_resilience_policy",
        lambda *,
        policy,
        decision: effective_policy,
    )

    def broken_observer(
        decision,
    ):
        raise RuntimeError(
            "simulated telemetry failure"
        )

    monkeypatch.setattr(
        tracing,
        "observe_reliability_governor_decision",
        broken_observer,
    )

    result = (
        planner
        ._resolve_planner_resilience_policy(
            base_policy
        )
    )

    assert result is effective_policy


def test_governor_failure_is_observed_and_fails_open(
    monkeypatch,
):
    base_policy = SimpleNamespace(
        name="rag.agentic.planner",
        max_attempts=2,
    )

    observed = []

    monkeypatch.setattr(
        planner,
        "_planner_governor_enforcement_enabled",
        lambda: True,
    )

    def broken_governor(
        operation,
    ):
        raise RuntimeError(
            "secret message must not be observed"
        )

    monkeypatch.setattr(
        governor,
        "get_reliability_governor_decision",
        broken_governor,
    )

    monkeypatch.setattr(
        tracing,
        "observe_reliability_governor_fail_open",
        lambda **kwargs: observed.append(
            kwargs
        ),
    )

    result = (
        planner
        ._resolve_planner_resilience_policy(
            base_policy
        )
    )

    assert result is base_policy

    assert observed == [
        {
            "operation": (
                "rag.agentic.planner"
            ),
            "current_max_attempts": 2,
            "error_type": "RuntimeError",
        }
    ]

    assert (
        "secret message"
        not in repr(
            observed
        )
    )

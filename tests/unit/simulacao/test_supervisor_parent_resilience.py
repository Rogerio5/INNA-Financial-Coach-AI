from __future__ import annotations

import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from src.agents import supervisor_deadline
from src.resilience import (
    FailureKind,
    classify_failure,
)
from src.resilience.runtime import (
    CircuitOpenError,
    ResilienceRuntime,
)


def _runtime_config():
    return SimpleNamespace(
        total_deadline_ms=8000,
        timeout_ms=10000,
    )


def _completed_failure(
    failure_kind: FailureKind,
    *,
    error_type: str = "ProviderError",
):
    return SimpleNamespace(
        stdout=json.dumps(
            {
                "ok": False,
                "error_type": error_type,
                "failure_kind": (
                    failure_kind.value
                ),
            }
        ),
        stderr="",
        returncode=1,
    )


def _prepare(
    monkeypatch,
    *,
    runtime: ResilienceRuntime,
):
    monkeypatch.setattr(
        supervisor_deadline,
        "get_supervisor_runtime_config",
        _runtime_config,
    )

    monkeypatch.setattr(
        supervisor_deadline,
        "_obter_mensagem_protegida",
        lambda *_: "safe-message",
    )

    monkeypatch.setattr(
        supervisor_deadline,
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    monkeypatch.setattr(
        supervisor_deadline,
        "traced_resilience_operation",
        lambda _: nullcontext(),
    )


def test_structured_worker_error_classifies_directly():
    error = (
        supervisor_deadline
        .SupervisorWorkerError(
            error_type="RateLimitError",
            failure_kind=(
                FailureKind.RATE_LIMIT
            ),
        )
    )

    assert (
        classify_failure(error)
        == FailureKind.RATE_LIMIT
    )


def test_parent_retries_transient_worker_failure(
    monkeypatch,
):
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    _prepare(
        monkeypatch,
        runtime=runtime,
    )

    calls = []
    captured_kwargs = []

    def fake_run(*args, **kwargs):
        calls.append(1)
        captured_kwargs.append(kwargs)

        if len(calls) == 1:
            return _completed_failure(
                FailureKind.RATE_LIMIT,
                error_type="RateLimitError",
            )

        return _completed_failure(
            FailureKind.INVALID_REQUEST,
            error_type="BadRequestError",
        )

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        supervisor_deadline.SupervisorWorkerError
    ) as captured:
        (
            supervisor_deadline
            .classificar_com_gemini_com_deadline(
                mensagem="teste",
                context={},
            )
        )

    assert len(calls) == 2

    assert (
        captured.value.failure_kind
        == FailureKind.INVALID_REQUEST
    )

    for kwargs in captured_kwargs:
        assert (
            kwargs["env"][
                "INNA_SUPERVISOR_RETRY_ATTEMPTS"
            ]
            == "1"
        )

        assert 0 < kwargs["timeout"] <= 8.0


def test_parent_does_not_retry_nonretryable_failure(
    monkeypatch,
):
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    _prepare(
        monkeypatch,
        runtime=runtime,
    )

    calls = 0

    def fake_run(*_, **__):
        nonlocal calls
        calls += 1

        return _completed_failure(
            FailureKind.AUTHENTICATION,
            error_type="AuthenticationError",
        )

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        supervisor_deadline.SupervisorWorkerError
    ):
        (
            supervisor_deadline
            .classificar_com_gemini_com_deadline(
                mensagem="teste",
                context={},
            )
        )

    assert calls == 1


def test_parent_circuit_persists_between_calls(
    monkeypatch,
):
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    _prepare(
        monkeypatch,
        runtime=runtime,
    )

    calls = 0

    def fake_run(*_, **__):
        nonlocal calls
        calls += 1

        return _completed_failure(
            FailureKind.RATE_LIMIT,
            error_type="RateLimitError",
        )

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        fake_run,
    )

    for _ in range(2):
        with pytest.raises(
            supervisor_deadline.SupervisorWorkerError
        ):
            (
                supervisor_deadline
                .classificar_com_gemini_com_deadline(
                    mensagem="teste",
                    context={},
                )
            )

    assert calls == 4

    with pytest.raises(
        CircuitOpenError
    ):
        (
            supervisor_deadline
            .classificar_com_gemini_com_deadline(
                mensagem="teste",
                context={},
            )
        )

    assert calls == 5

    with pytest.raises(
        CircuitOpenError
    ):
        (
            supervisor_deadline
            .classificar_com_gemini_com_deadline(
                mensagem="teste",
                context={},
            )
        )

    assert calls == 5


def test_worker_timeout_is_bounded_by_total_budget(
    monkeypatch,
):
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    _prepare(
        monkeypatch,
        runtime=runtime,
    )

    captured = {}

    def fake_run(*_, **kwargs):
        captured.update(kwargs)

        return _completed_failure(
            FailureKind.INVALID_REQUEST
        )

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        supervisor_deadline.SupervisorWorkerError
    ):
        (
            supervisor_deadline
            .classificar_com_gemini_com_deadline(
                mensagem="teste",
                context={},
            )
        )

    assert 0 < captured["timeout"] < 8.0

    assert (
        captured["env"][
            "INNA_SUPERVISOR_RETRY_ATTEMPTS"
        ]
        == "1"
    )

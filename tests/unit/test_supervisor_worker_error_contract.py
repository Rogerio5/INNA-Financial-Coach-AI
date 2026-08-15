from __future__ import annotations

import io
import json
from types import SimpleNamespace

import pytest

from src.agents import (
    supervisor_deadline,
    supervisor_worker,
)
from src.resilience import FailureKind


class FakeRateLimitError(
    Exception
):
    def __init__(self) -> None:
        super().__init__(
            "provider secret detail 123"
        )
        self.status = 429


def test_worker_returns_safe_structured_failure(
    monkeypatch,
):
    def fail_classification(
        **_,
    ):
        raise FakeRateLimitError()

    monkeypatch.setattr(
        supervisor_worker,
        "classificar_com_gemini",
        fail_classification,
    )

    stdin = io.StringIO(
        json.dumps(
            {
                "message": "teste",
                "context": {},
            }
        )
    )

    stdout = io.StringIO()

    monkeypatch.setattr(
        supervisor_worker.sys,
        "stdin",
        stdin,
    )

    monkeypatch.setattr(
        supervisor_worker.sys,
        "stdout",
        stdout,
    )

    exit_code = (
        supervisor_worker.main()
    )

    payload = json.loads(
        stdout.getvalue().strip()
    )

    assert exit_code == 1
    assert payload == {
        "ok": False,
        "error_type": (
            "FakeRateLimitError"
        ),
        "failure_kind": (
            FailureKind.RATE_LIMIT.value
        ),
    }

    assert "error" not in payload

    assert (
        "provider secret detail"
        not in stdout.getvalue()
    )


def test_parent_raises_safe_structured_worker_error(
    monkeypatch,
):
    monkeypatch.setattr(
        supervisor_deadline,
        "get_supervisor_runtime_config",
        lambda: SimpleNamespace(
            total_deadline_ms=8000
        ),
    )

    monkeypatch.setattr(
        supervisor_deadline,
        "_obter_mensagem_protegida",
        lambda *_: "safe-message",
    )

    worker_payload = {
        "ok": False,
        "error_type": (
            "FakeRateLimitError"
        ),
        "failure_kind": (
            FailureKind.RATE_LIMIT.value
        ),
        "error": (
            "provider secret detail "
            "must be ignored"
        ),
    }

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        lambda *_, **__: (
            SimpleNamespace(
                stdout=json.dumps(
                    worker_payload
                ),
                stderr="",
                returncode=1,
            )
        ),
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

    error = captured.value

    assert (
        error.error_type
        == "FakeRateLimitError"
    )

    assert (
        error.failure_kind
        == FailureKind.RATE_LIMIT
    )

    assert (
        "provider secret detail"
        not in str(error)
    )


def test_parent_unknown_failure_kind_is_safe(
    monkeypatch,
):
    monkeypatch.setattr(
        supervisor_deadline,
        "get_supervisor_runtime_config",
        lambda: SimpleNamespace(
            total_deadline_ms=8000
        ),
    )

    monkeypatch.setattr(
        supervisor_deadline,
        "_obter_mensagem_protegida",
        lambda *_: "safe-message",
    )

    monkeypatch.setattr(
        supervisor_deadline.subprocess,
        "run",
        lambda *_, **__: (
            SimpleNamespace(
                stdout=json.dumps(
                    {
                        "ok": False,
                        "error_type": (
                            "UnexpectedError"
                        ),
                        "failure_kind": (
                            "not-a-real-kind"
                        ),
                    }
                ),
                stderr="",
                returncode=1,
            )
        ),
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

    assert (
        captured.value.failure_kind
        == FailureKind.UNKNOWN
    )


def test_parent_sanitizes_error_type():
    error = (
        supervisor_deadline
        .SupervisorWorkerError(
            error_type=(
                "Provider Error <secret>"
            ),
            failure_kind=(
                FailureKind.UNKNOWN
            ),
        )
    )

    assert (
        error.error_type
        == "ProviderErrorsecret"
    )

    assert (
        "<secret>"
        not in str(error)
    )

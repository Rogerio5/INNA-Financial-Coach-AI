from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

from google import genai

import src.observability.llm_tracking as llm_tracking
import src.observability.resilience_tracing as resilience_tracing
from src.agentic_rag import planner
from src.agents import supervisor_config
from src.resilience.runtime import (
    ResilienceRuntime,
)


class FakeProviderError(Exception):
    def __init__(
        self,
        status: int,
        message: str = (
            "provider internal secret"
        ),
    ) -> None:
        super().__init__(message)
        self.status = status


class FakeModels:
    def __init__(
        self,
        callback,
    ) -> None:
        self._callback = callback

    def generate_content(
        self,
        **kwargs,
    ):
        return self._callback(
            **kwargs
        )


class FakeClient:
    def __init__(
        self,
        callback,
    ) -> None:
        self.models = FakeModels(
            callback
        )


def _valid_response():
    return SimpleNamespace(
        parsed={
            "complexity": "simple",
            "rationale": (
                "Plano objetivo e seguro."
            ),
            "steps": [
                {
                    "question": (
                        "Explique reserva "
                        "de emergência."
                    ),
                    "source": (
                        "knowledge_base"
                    ),
                    "priority": 100,
                    "required": True,
                    "top_k": 4,
                    "max_results": 5,
                }
            ],
            "requires_iteration": False,
        }
    )


def _direct_observed_call(
    client,
    *,
    modelo,
    contents,
    config,
    **_,
):
    return client.models.generate_content(
        model=modelo,
        contents=contents,
        config=config,
    )


def _prepare(
    monkeypatch,
) -> ResilienceRuntime:
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    monkeypatch.setattr(
        resilience_tracing,
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    monkeypatch.setattr(
        resilience_tracing,
        "traced_resilience_operation",
        lambda _: nullcontext(),
    )

    monkeypatch.setattr(
        llm_tracking,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    monkeypatch.setattr(
        supervisor_config,
        "get_supervisor_runtime_config",
        lambda: SimpleNamespace(
            model="fake-model"
        ),
    )

    monkeypatch.setattr(
        supervisor_config,
        "get_gemini_api_key",
        lambda: "fake-key",
    )

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_MODEL",
        "fake-model",
    )

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_PLANNER_TIMEOUT_MS",
        "12000",
    )

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_PLANNER_TOTAL_DEADLINE_MS",
        "20000",
    )

    return runtime


def test_planner_has_dedicated_policy():
    from src.resilience.policies import (
        AGENTIC_RAG_PLANNER_POLICY,
        GEMINI_TEXT_GENERATION_POLICY,
        SUPERVISOR_GENERATION_POLICY,
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY.name
        == "rag.agentic.planner"
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY.name
        != SUPERVISOR_GENERATION_POLICY.name
    )

    assert (
        AGENTIC_RAG_PLANNER_POLICY.name
        != GEMINI_TEXT_GENERATION_POLICY.name
    )


def test_planner_retries_transient_429(
    monkeypatch,
):
    _prepare(monkeypatch)

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        if calls == 1:
            raise FakeProviderError(
                429
            )

        return _valid_response()

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    result = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert calls == 2

    assert (
        result.generation_mode.value
        == "llm"
    )

    assert (
        result.metadata["planner"]
        == "gemini_structured_v1"
    )


def test_planner_nonretryable_400_falls_back_immediately(
    monkeypatch,
):
    _prepare(monkeypatch)

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        raise FakeProviderError(
            400
        )

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    result = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert calls == 1

    assert (
        result.generation_mode.value
        == "fallback"
    )

    assert (
        result.metadata["planner"]
        == (
            "deterministic_after_llm_failure"
        )
    )


def test_planner_exhausted_transient_failure_uses_fallback(
    monkeypatch,
):
    _prepare(monkeypatch)

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        raise FakeProviderError(
            503
        )

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    result = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert calls == 2

    assert (
        result.generation_mode.value
        == "fallback"
    )

    assert (
        result.metadata["llm_error_type"]
        == "FakeProviderError"
    )

    assert (
        "provider internal secret"
        not in str(
            result.metadata
        )
    )


def test_planner_sdk_retry_is_disabled(
    monkeypatch,
):
    _prepare(monkeypatch)

    captured = {}

    def fake_client(**kwargs):
        captured.update(kwargs)

        return FakeClient(
            lambda **_: _valid_response()
        )

    monkeypatch.setattr(
        genai,
        "Client",
        fake_client,
    )

    result = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert (
        result.generation_mode.value
        == "llm"
    )

    options = captured[
        "http_options"
    ]

    assert options.retry_options is None

    assert (
        0
        < options.timeout
        <= 12000
    )


def test_planner_timeout_is_clamped_to_total_budget(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_PLANNER_TIMEOUT_MS",
        "60000",
    )

    monkeypatch.setenv(
        "INNA_AGENTIC_RAG_PLANNER_TOTAL_DEADLINE_MS",
        "2000",
    )

    captured = {}

    def fake_client(**kwargs):
        captured.update(kwargs)

        return FakeClient(
            lambda **_: _valid_response()
        )

    monkeypatch.setattr(
        genai,
        "Client",
        fake_client,
    )

    result = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert (
        result.generation_mode.value
        == "llm"
    )

    timeout = captured[
        "http_options"
    ].timeout

    assert 0 < timeout < 2000


def test_planner_circuit_persists_and_fallback_remains_available(
    monkeypatch,
):
    runtime = _prepare(
        monkeypatch
    )

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        raise FakeProviderError(
            503
        )

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    first = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    second = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert (
        first.generation_mode.value
        == "fallback"
    )

    assert (
        second.generation_mode.value
        == "fallback"
    )

    assert calls == 4

    third = planner.create_research_plan(
        "Explique reserva de emergência.",
        planner_mode="llm",
    )

    assert (
        third.generation_mode.value
        == "fallback"
    )

    assert calls == 4

    assert runtime is not None


def test_planner_does_not_reference_supervisor_client():
    source = (
        __import__(
            "pathlib"
        )
        .Path(
            "src/agentic_rag/planner.py"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        "get_supervisor_client"
        not in source
    )

    assert (
        "retry_options=None"
        in source
    )

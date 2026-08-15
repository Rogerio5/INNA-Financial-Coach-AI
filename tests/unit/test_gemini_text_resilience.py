from __future__ import annotations

from contextlib import (
    contextmanager,
    nullcontext,
)
from types import SimpleNamespace

import pytest

from src.observability import llm_tracking
from src.resilience import (
    FailureKind,
)
from src.resilience.runtime import (
    ResilienceRuntime,
)
from src.services.llm import gemini


class FakeProviderError(Exception):
    def __init__(
        self,
        status: int,
        message: str = (
            "provider secret detail"
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


def _prepare_runtime(
    monkeypatch,
) -> ResilienceRuntime:
    runtime = ResilienceRuntime(
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    monkeypatch.setattr(
        gemini,
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    monkeypatch.setattr(
        gemini,
        "traced_resilience_operation",
        lambda _: nullcontext(),
    )

    monkeypatch.setenv(
        "INNA_TEXT_GENERATION_TIMEOUT_MS",
        "15000",
    )

    monkeypatch.setenv(
        "INNA_TEXT_GENERATION_TOTAL_DEADLINE_MS",
        "25000",
    )

    return runtime


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


def test_text_policy_is_dedicated():
    from src.resilience.policies import (
        GEMINI_TEXT_GENERATION_POLICY,
        SUPERVISOR_GENERATION_POLICY,
    )

    assert (
        GEMINI_TEXT_GENERATION_POLICY.name
        == "gemini.generate.text_service"
    )

    assert (
        GEMINI_TEXT_GENERATION_POLICY.name
        != SUPERVISOR_GENERATION_POLICY.name
    )


def test_client_has_explicit_timeout_and_no_sdk_retry(
    monkeypatch,
):
    from google import genai

    captured = {}

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "fake-key-for-test",
    )

    def fake_client(**kwargs):
        captured.update(kwargs)

        return SimpleNamespace()

    monkeypatch.setattr(
        genai,
        "Client",
        fake_client,
    )

    gemini.criar_cliente_gemini(
        timeout_ms=4321
    )

    options = captured[
        "http_options"
    ]

    assert options.timeout == 4321
    assert options.retry_options is None


def test_transient_429_is_retried_by_inna(
    monkeypatch,
):
    _prepare_runtime(
        monkeypatch
    )

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        if calls == 1:
            raise FakeProviderError(
                429
            )

        return SimpleNamespace(
            text="Resposta segura."
        )

    monkeypatch.setattr(
        gemini,
        "criar_cliente_gemini",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    monkeypatch.setattr(
        gemini,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    result = gemini.gerar_texto_gemini(
        "Explique reserva de emergência."
    )

    assert result == "Resposta segura."
    assert calls == 2


@pytest.mark.parametrize(
    "status,expected",
    [
        (
            400,
            FailureKind.INVALID_REQUEST,
        ),
        (
            401,
            FailureKind.AUTHENTICATION,
        ),
        (
            403,
            FailureKind.AUTHORIZATION,
        ),
    ],
)
def test_nonretryable_provider_errors_fail_fast(
    monkeypatch,
    status,
    expected,
):
    _prepare_runtime(
        monkeypatch
    )

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        error = FakeProviderError(
            status
        )

        from src.resilience import (
            classify_failure,
        )

        assert (
            classify_failure(error)
            == expected
        )

        raise error

    monkeypatch.setattr(
        gemini,
        "criar_cliente_gemini",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    monkeypatch.setattr(
        gemini,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    with pytest.raises(
        gemini.GeminiTextGenerationError
    ):
        gemini.gerar_texto_gemini(
            "teste"
        )

    assert calls == 1


def test_provider_message_is_not_exposed(
    monkeypatch,
):
    _prepare_runtime(
        monkeypatch
    )

    def provider_call(**_):
        raise FakeProviderError(
            400,
            "API KEY SECRET SHOULD NOT LEAK",
        )

    monkeypatch.setattr(
        gemini,
        "criar_cliente_gemini",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    monkeypatch.setattr(
        gemini,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    with pytest.raises(
        gemini.GeminiTextGenerationError
    ) as captured:
        gemini.gerar_texto_gemini(
            "teste"
        )

    message = str(
        captured.value
    )

    assert (
        "API KEY SECRET"
        not in message
    )

    assert (
        "FakeProviderError"
        in message
    )


def test_empty_response_is_not_retried(
    monkeypatch,
):
    _prepare_runtime(
        monkeypatch
    )

    calls = 0

    def provider_call(**_):
        nonlocal calls
        calls += 1

        return SimpleNamespace(
            text=""
        )

    monkeypatch.setattr(
        gemini,
        "criar_cliente_gemini",
        lambda **_: FakeClient(
            provider_call
        ),
    )

    monkeypatch.setattr(
        gemini,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    with pytest.raises(
        gemini.GeminiTextGenerationError
    ):
        gemini.gerar_texto_gemini(
            "teste"
        )

    assert calls == 1


def test_attempt_timeout_is_clamped_to_total_deadline(
    monkeypatch,
):
    _prepare_runtime(
        monkeypatch
    )

    monkeypatch.setenv(
        "INNA_TEXT_GENERATION_TIMEOUT_MS",
        "60000",
    )

    monkeypatch.setenv(
        "INNA_TEXT_GENERATION_TOTAL_DEADLINE_MS",
        "2000",
    )

    captured_timeouts = []

    def create_client(
        *,
        timeout_ms,
    ):
        captured_timeouts.append(
            timeout_ms
        )

        return FakeClient(
            lambda **_: SimpleNamespace(
                text="ok"
            )
        )

    monkeypatch.setattr(
        gemini,
        "criar_cliente_gemini",
        create_client,
    )

    monkeypatch.setattr(
        gemini,
        "executar_generate_content_observado",
        _direct_observed_call,
    )

    result = gemini.gerar_texto_gemini(
        "teste"
    )

    assert result == "ok"

    assert len(
        captured_timeouts
    ) == 1

    assert (
        0
        < captured_timeouts[0]
        < 2000
    )


def test_invalid_timeout_configuration_fails_fast(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_TEXT_GENERATION_TIMEOUT_MS",
        "not-a-number",
    )

    with pytest.raises(
        gemini.GeminiTextConfigurationError
    ):
        gemini.gerar_texto_gemini(
            "teste"
        )


class FakeSpan:
    def set_attribute(
        self,
        *_,
        **__,
    ) -> None:
        return None


@contextmanager
def fake_traced_operation(
    *_,
    **__,
):
    yield FakeSpan()


def test_llm_tracking_does_not_persist_raw_provider_message(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        llm_tracking,
        "traced_operation",
        fake_traced_operation,
    )

    monkeypatch.setattr(
        llm_tracking,
        "registrar_consumo_llm",
        lambda **kwargs: (
            captured.update(kwargs)
        ),
    )

    def fail():
        raise RuntimeError(
            "SECRET PROVIDER MESSAGE"
        )

    with pytest.raises(
        RuntimeError
    ):
        llm_tracking.executar_llm_observado(
            fail,
            modelo="fake-model",
            operacao="test",
        )

    assert (
        captured["erro_tipo"]
        == "RuntimeError"
    )

    assert (
        "SECRET PROVIDER MESSAGE"
        not in captured[
            "erro_mensagem"
        ]
    )

    assert (
        captured["erro_mensagem"]
        == "LLM provider call failed."
    )

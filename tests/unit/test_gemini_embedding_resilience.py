from __future__ import annotations

from contextlib import nullcontext

import pytest
from google import genai

from src.observability import (
    resilience_tracing,
)
from src.resilience import (
    CircuitState,
)
from src.services.embeddings import (
    gemini as embedding_service,
)


class APIErrorLike(RuntimeError):
    def __init__(
        self,
        code: int,
        message: str = "PRIVATE_PROVIDER_DETAIL",
    ) -> None:
        self.code = code
        super().__init__(message)


class FakeEmbedding:
    def __init__(
        self,
        values,
    ) -> None:
        self.values = values


class FakeResponse:
    def __init__(
        self,
        embeddings,
    ) -> None:
        self.embeddings = embeddings


class FakeModels:
    def __init__(
        self,
        outcomes,
    ) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0
        self.call_kwargs = []

    def embed_content(
        self,
        **kwargs,
    ):
        self.calls += 1
        self.call_kwargs.append(
            dict(kwargs)
        )

        if not self.outcomes:
            raise AssertionError(
                "No fake provider outcome available."
            )

        outcome = self.outcomes.pop(0)

        if isinstance(
            outcome,
            BaseException,
        ):
            raise outcome

        return outcome


class FakeClient:
    def __init__(
        self,
        models,
    ) -> None:
        self.models = models


def _success_response():
    return FakeResponse(
        [
            FakeEmbedding(
                [0.125]
                * embedding_service
                .DIMENSOES_EMBEDDING
            )
        ]
    )


def _install_runtime(
    monkeypatch,
):
    sleeps = []

    runtime = (
        resilience_tracing
        .create_observed_resilience_runtime(
            sleeper=sleeps.append,
            random_source=lambda: 0.5,
        )
    )

    monkeypatch.setattr(
        resilience_tracing,
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    monkeypatch.setattr(
        resilience_tracing,
        "traced_resilience_operation",
        lambda _policy: nullcontext(),
    )

    return runtime, sleeps


def _install_client(
    monkeypatch,
    models,
):
    client = FakeClient(
        models
    )

    monkeypatch.setattr(
        embedding_service,
        "criar_cliente_gemini",
        lambda: client,
    )

    return client


def test_embedding_client_has_real_timeout_and_sdk_retry_disabled(
    monkeypatch,
):
    captured = {}

    def fake_client(
        **kwargs,
    ):
        captured.update(
            kwargs
        )
        return object()

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-placeholder",
    )

    monkeypatch.setenv(
        "INNA_EMBEDDING_TIMEOUT_MS",
        "12000",
    )

    monkeypatch.setattr(
        genai,
        "Client",
        fake_client,
    )

    embedding_service.criar_cliente_gemini()

    http_options = captured[
        "http_options"
    ]

    assert (
        http_options.timeout
        == 12_000
    )

    assert (
        http_options.retry_options
        is None
    )


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        "999",
        "60001",
        "-1",
    ],
)
def test_embedding_timeout_configuration_is_fail_fast(
    monkeypatch,
    value,
):
    monkeypatch.setenv(
        "INNA_EMBEDDING_TIMEOUT_MS",
        value,
    )

    with pytest.raises(
        embedding_service
        .GeminiEmbeddingConfigurationError
    ):
        (
            embedding_service
            ._obter_timeout_embedding_ms()
        )


@pytest.mark.parametrize(
    "status_code",
    [
        408,
        429,
        500,
        502,
        503,
        504,
    ],
)
def test_transient_google_api_errors_retry_then_succeed(
    monkeypatch,
    status_code,
):
    models = FakeModels(
        [
            APIErrorLike(
                status_code
            ),
            _success_response(),
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _, sleeps = _install_runtime(
        monkeypatch
    )

    vector = (
        embedding_service
        .gerar_embedding_consulta(
            "consulta segura"
        )
    )

    assert len(vector) == 3072
    assert models.calls == 2

    assert sleeps == [
        0.25
    ]


def test_transport_timeout_retries_then_succeeds(
    monkeypatch,
):
    models = FakeModels(
        [
            TimeoutError(
                "PRIVATE_TIMEOUT_DETAIL"
            ),
            _success_response(),
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _, sleeps = _install_runtime(
        monkeypatch
    )

    vector = (
        embedding_service
        .gerar_embedding_consulta(
            "consulta"
        )
    )

    assert len(vector) == 3072
    assert models.calls == 2
    assert sleeps == [0.25]


@pytest.mark.parametrize(
    "status_code",
    [
        400,
        401,
        403,
    ],
)
def test_non_retryable_google_errors_fail_fast(
    monkeypatch,
    status_code,
):
    models = FakeModels(
        [
            APIErrorLike(
                status_code
            )
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _, sleeps = _install_runtime(
        monkeypatch
    )

    with pytest.raises(
        embedding_service
        .GeminiEmbeddingGenerationError
    ):
        (
            embedding_service
            .gerar_embedding_consulta(
                "consulta"
            )
        )

    assert models.calls == 1
    assert sleeps == []


def test_provider_error_message_is_not_exposed(
    monkeypatch,
):
    secret = (
        "TOP_SECRET_PROVIDER_PAYLOAD"
    )

    models = FakeModels(
        [
            APIErrorLike(
                400,
                secret,
            )
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _install_runtime(
        monkeypatch
    )

    with pytest.raises(
        embedding_service
        .GeminiEmbeddingGenerationError
    ) as captured:
        (
            embedding_service
            .gerar_embedding_consulta(
                "consulta"
            )
        )

    assert (
        secret
        not in str(
            captured.value
        )
    )


def test_malformed_embedding_response_is_not_retried(
    monkeypatch,
):
    models = FakeModels(
        [
            FakeResponse([])
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _, sleeps = _install_runtime(
        monkeypatch
    )

    with pytest.raises(
        embedding_service
        .GeminiEmbeddingGenerationError
    ):
        (
            embedding_service
            .gerar_embedding_consulta(
                "consulta"
            )
        )

    assert models.calls == 1
    assert sleeps == []


def test_provider_receives_expected_embedding_contract(
    monkeypatch,
):
    models = FakeModels(
        [
            _success_response()
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    _install_runtime(
        monkeypatch
    )

    vector = (
        embedding_service
        .gerar_embedding_documento(
            "documento de teste"
        )
    )

    assert len(vector) == 3072
    assert models.calls == 1

    kwargs = (
        models.call_kwargs[0]
    )

    assert (
        kwargs["model"]
        == embedding_service
        .MODELO_EMBEDDING
    )

    assert (
        kwargs["contents"]
        == "documento de teste"
    )

    assert (
        kwargs[
            "config"
        ].task_type
        == (
            embedding_service
            .TASK_RETRIEVAL_DOCUMENT
        )
    )

    assert (
        kwargs[
            "config"
        ].output_dimensionality
        == 3072
    )


def test_circuit_opens_after_consecutive_provider_failures(
    monkeypatch,
):
    models = FakeModels(
        [
            APIErrorLike(503)
            for _ in range(10)
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    runtime, _ = _install_runtime(
        monkeypatch
    )

    for _ in range(2):
        with pytest.raises(
            embedding_service
            .GeminiEmbeddingGenerationError
        ):
            (
                embedding_service
                .gerar_embedding_consulta(
                    "consulta"
                )
            )

    breaker = (
        runtime.registry
        .get_or_create(
            __import__(
                "src.resilience.policies",
                fromlist=[
                    "GEMINI_EMBEDDING_POLICY"
                ],
            )
            .GEMINI_EMBEDDING_POLICY
        )
    )

    assert (
        breaker.snapshot().state
        is CircuitState.OPEN
    )

    calls_before = models.calls

    with pytest.raises(
        embedding_service
        .GeminiEmbeddingGenerationError
    ):
        (
            embedding_service
            .gerar_embedding_consulta(
                "consulta"
            )
        )

    assert (
        models.calls
        == calls_before
    )



class FakeClock:
    def __init__(
        self,
        initial: float = 0.0,
    ) -> None:
        self.value = float(initial)

    def __call__(
        self,
    ) -> float:
        return self.value

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.value += float(seconds)


def test_embedding_circuit_recovers_through_half_open(
    monkeypatch,
):
    clock = FakeClock()
    sleeps = []

    runtime = (
        resilience_tracing
        .create_observed_resilience_runtime(
            clock=clock,
            sleeper=sleeps.append,
            random_source=lambda: 0.5,
        )
    )

    monkeypatch.setattr(
        resilience_tracing,
        "get_shared_resilience_runtime",
        lambda: runtime,
    )

    monkeypatch.setattr(
        resilience_tracing,
        "traced_resilience_operation",
        lambda _policy: nullcontext(),
    )

    models = FakeModels(
        [
            APIErrorLike(503)
            for _ in range(5)
        ]
        + [
            _success_response()
        ]
    )

    _install_client(
        monkeypatch,
        models,
    )

    policy = (
        __import__(
            "src.resilience.policies",
            fromlist=[
                "GEMINI_EMBEDDING_POLICY"
            ],
        )
        .GEMINI_EMBEDDING_POLICY
    )

    for _ in range(2):
        with pytest.raises(
            embedding_service
            .GeminiEmbeddingGenerationError
        ):
            (
                embedding_service
                .gerar_embedding_consulta(
                    "consulta"
                )
            )

    breaker = (
        runtime.registry
        .get_or_create(
            policy
        )
    )

    snapshot = breaker.snapshot()

    assert (
        snapshot.state
        is CircuitState.OPEN
    )

    assert models.calls == 5

    clock.advance(
        policy.circuit_recovery_seconds
    )

    vector = (
        embedding_service
        .gerar_embedding_consulta(
            "consulta recuperada"
        )
    )

    assert len(vector) == 3072

    assert models.calls == 6

    recovered = (
        breaker.snapshot()
    )

    assert (
        recovered.state
        is CircuitState.CLOSED
    )

    assert (
        recovered.consecutive_failures
        == 0
    )

    assert (
        recovered.opened_at
        is None
    )

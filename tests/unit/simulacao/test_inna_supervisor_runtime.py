from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.agents.gemini_client import (
    get_supervisor_client,
    reset_supervisor_client_cache,
)
from src.agents.schemas import (
    SupervisorLLMDecision,
)
from src.agents.supervisor_config import (
    DEFAULT_SUPERVISOR_MAX_CONTEXT_CHARS,
    DEFAULT_SUPERVISOR_MAX_OUTPUT_TOKENS,
    DEFAULT_SUPERVISOR_MODEL,
    DEFAULT_SUPERVISOR_RETRY_ATTEMPTS,
    DEFAULT_SUPERVISOR_TIMEOUT_MS,
    DEFAULT_SUPERVISOR_TOTAL_DEADLINE_MS,
    get_supervisor_runtime_config,
    reset_supervisor_config_cache,
)
from src.agents.supervisor_llm import (
    classificar_com_gemini,
)


_RUNTIME_ENVIRONMENT_VARIABLES = [
    "GEMINI_MODEL",
    "INNA_SUPERVISOR_MODEL",
    "INNA_SUPERVISOR_TIMEOUT_MS",
    "INNA_SUPERVISOR_TOTAL_DEADLINE_MS",
    "INNA_SUPERVISOR_RETRY_ATTEMPTS",
    "INNA_SUPERVISOR_MAX_OUTPUT_TOKENS",
    "INNA_SUPERVISOR_MAX_CONTEXT_CHARS",
]


@pytest.fixture(autouse=True)
def _isolar_configuracao_do_supervisor(
    monkeypatch,
):
    """
    Impede que o .env local afete os testes unitários.
    """
    for variable_name in (
        _RUNTIME_ENVIRONMENT_VARIABLES
    ):
        monkeypatch.delenv(
            variable_name,
            raising=False,
        )

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    monkeypatch.delenv(
        "GOOGLE_API_KEY",
        raising=False,
    )

    reset_supervisor_config_cache()
    reset_supervisor_client_cache()

    yield

    reset_supervisor_config_cache()
    reset_supervisor_client_cache()


def test_configuracao_padrao_do_supervisor():
    config = get_supervisor_runtime_config()

    assert config.model == DEFAULT_SUPERVISOR_MODEL

    assert (
        config.timeout_ms
        == DEFAULT_SUPERVISOR_TIMEOUT_MS
    )

    assert (
        config.total_deadline_ms
        == DEFAULT_SUPERVISOR_TOTAL_DEADLINE_MS
    )

    assert (
        config.retry_attempts
        == DEFAULT_SUPERVISOR_RETRY_ATTEMPTS
    )

    assert (
        config.max_output_tokens
        == DEFAULT_SUPERVISOR_MAX_OUTPUT_TOKENS
    )

    assert (
        config.max_context_characters
        == DEFAULT_SUPERVISOR_MAX_CONTEXT_CHARS
    )


def test_configuracao_aceita_variaveis_de_ambiente(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_SUPERVISOR_MODEL",
        "gemini-2.5-flash-lite",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_TIMEOUT_MS",
        "10000",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_TOTAL_DEADLINE_MS",
        "8000",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_RETRY_ATTEMPTS",
        "1",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_MAX_OUTPUT_TOKENS",
        "220",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_MAX_CONTEXT_CHARS",
        "8000",
    )

    reset_supervisor_config_cache()

    config = get_supervisor_runtime_config()

    assert config.model == "gemini-2.5-flash-lite"
    assert config.timeout_ms == 10_000
    assert config.total_deadline_ms == 8_000
    assert config.retry_attempts == 1
    assert config.max_output_tokens == 220
    assert config.max_context_characters == 8_000


@patch(
    "src.agents.gemini_client.genai.Client"
)
def test_cliente_gemini_e_reutilizado(
    mock_client_constructor,
):
    first = get_supervisor_client()
    second = get_supervisor_client()

    assert first is second
    mock_client_constructor.assert_called_once()


@patch(
    "src.agents.gemini_client.genai.Client"
)
def test_cliente_recebe_timeout_e_retentativas(
    mock_client_constructor,
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_SUPERVISOR_TIMEOUT_MS",
        "10000",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_RETRY_ATTEMPTS",
        "1",
    )

    reset_supervisor_config_cache()
    reset_supervisor_client_cache()

    get_supervisor_client()

    kwargs = (
        mock_client_constructor
        .call_args
        .kwargs
    )

    http_options = kwargs[
        "http_options"
    ]

    assert http_options.timeout == 10_000

    assert (
        http_options.retry_options.attempts
        == 1
    )

    assert 429 in (
        http_options
        .retry_options
        .http_status_codes
    )

    assert 503 in (
        http_options
        .retry_options
        .http_status_codes
    )


def test_classificacao_usa_modelo_configurado(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_SUPERVISOR_MODEL",
        "gemini-2.5-flash-lite",
    )

    monkeypatch.setenv(
        "INNA_SUPERVISOR_MAX_OUTPUT_TOKENS",
        "220",
    )

    reset_supervisor_config_cache()

    fake_client = MagicMock()

    fake_client.models.generate_content.return_value = (
        SimpleNamespace(
            parsed=SupervisorLLMDecision(
                intent="educacao_financeira",
                next_node="education_agent",
                confidence=0.91,
                use_rag=True,
                reason=(
                    "Orientação financeira inicial."
                ),
            ),
            text="",
        )
    )

    with patch(
        "src.agents.supervisor_llm."
        "get_supervisor_client",
        return_value=fake_client,
    ):
        decision = classificar_com_gemini(
            mensagem=(
                "Estou perdido financeiramente."
            ),
            context={
                "current_message": (
                    "Estou perdido financeiramente."
                ),
                "rendered_prompt": (
                    "Contexto protegido."
                ),
            },
        )

    call = (
        fake_client.models.generate_content
        .call_args
    )

    assert (
        call.kwargs["model"]
        == "gemini-2.5-flash-lite"
    )

    assert (
        call.kwargs["config"]
        .max_output_tokens
        == 220
    )

    assert (
        decision.classification_source
        == "gemini"
    )

    assert decision.gemini_called is True

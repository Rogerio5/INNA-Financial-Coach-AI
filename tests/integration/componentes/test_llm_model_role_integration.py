from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.services.llm.gemini import (
    gerar_texto_gemini,
)
from src.services.llm.model_registry import (
    LLMRole,
    reset_model_registry_cache,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    reset_model_registry_cache()

    yield

    reset_model_registry_cache()


def _fake_response():
    return SimpleNamespace(
        text="Resposta de teste."
    )


def test_servico_textual_resolve_modelo_por_papel(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_RAG_MODEL",
        "gemini-rag-especializado",
    )

    reset_model_registry_cache()

    fake_client = MagicMock()

    with (
        patch(
            "src.services.llm.gemini."
            "criar_cliente_gemini",
            return_value=fake_client,
        ),
        patch(
            "src.services.llm.gemini."
            "executar_generate_content_observado",
            return_value=_fake_response(),
        ) as mock_generate,
    ):
        result = gerar_texto_gemini(
            "Pergunta RAG",
            role=LLMRole.RAG,
            temperatura=0.0,
            max_tokens=100,
        )

    assert result == "Resposta de teste."

    assert (
        mock_generate.call_args.kwargs[
            "modelo"
        ]
        == "gemini-rag-especializado"
    )


def test_modelo_explicito_sobrescreve_papel(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_REPORT_MODEL",
        "gemini-report-configurado",
    )

    reset_model_registry_cache()

    fake_client = MagicMock()

    with (
        patch(
            "src.services.llm.gemini."
            "criar_cliente_gemini",
            return_value=fake_client,
        ),
        patch(
            "src.services.llm.gemini."
            "executar_generate_content_observado",
            return_value=_fake_response(),
        ) as mock_generate,
    ):
        gerar_texto_gemini(
            "Relatório",
            modelo="gemini-modelo-explicito",
            role=LLMRole.REPORT,
        )

    assert (
        mock_generate.call_args.kwargs[
            "modelo"
        ]
        == "gemini-modelo-explicito"
    )


def test_papeis_podem_usar_modelos_independentes(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_EDUCATION_MODEL",
        "gemini-education-test",
    )

    monkeypatch.setenv(
        "INNA_RAG_MODEL",
        "gemini-rag-test",
    )

    reset_model_registry_cache()

    fake_client = MagicMock()

    with (
        patch(
            "src.services.llm.gemini."
            "criar_cliente_gemini",
            return_value=fake_client,
        ),
        patch(
            "src.services.llm.gemini."
            "executar_generate_content_observado",
            return_value=_fake_response(),
        ) as mock_generate,
    ):
        gerar_texto_gemini(
            "Educação",
            role=LLMRole.EDUCATION,
        )

        gerar_texto_gemini(
            "RAG",
            role=LLMRole.RAG,
        )

    calls = mock_generate.call_args_list

    assert (
        calls[0].kwargs["modelo"]
        == "gemini-education-test"
    )

    assert (
        calls[1].kwargs["modelo"]
        == "gemini-rag-test"
    )

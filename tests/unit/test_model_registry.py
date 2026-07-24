from __future__ import annotations

import pytest

from src.services.llm.model_registry import (
    DEFAULT_TEXT_MODEL,
    LLMRole,
    get_model_for_role,
    get_model_registry,
    reset_model_registry_cache,
)


_MODEL_ENVIRONMENT_VARIABLES = [
    "GEMINI_MODEL",
    "INNA_SUPERVISOR_MODEL",
    "INNA_EDUCATION_MODEL",
    "INNA_RAG_MODEL",
    "INNA_REPORT_MODEL",
    "INNA_FINANCIAL_EXPLANATION_MODEL",
]


@pytest.fixture(autouse=True)
def _isolate_model_environment(
    monkeypatch,
):
    for variable_name in (
        _MODEL_ENVIRONMENT_VARIABLES
    ):
        monkeypatch.delenv(
            variable_name,
            raising=False,
        )

    reset_model_registry_cache()

    yield

    reset_model_registry_cache()


def test_all_roles_use_flash_lite_by_default():
    registry = get_model_registry()

    assert registry

    assert all(
        model == DEFAULT_TEXT_MODEL
        for model in registry.values()
    )


def test_global_model_is_used_as_fallback(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_MODEL",
        "gemini-global-test",
    )

    reset_model_registry_cache()

    assert (
        get_model_for_role(
            LLMRole.EDUCATION
        )
        == "gemini-global-test"
    )

    assert (
        get_model_for_role(
            LLMRole.RAG
        )
        == "gemini-global-test"
    )


def test_specific_role_overrides_global_model(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_MODEL",
        "gemini-global-test",
    )

    monkeypatch.setenv(
        "INNA_RAG_MODEL",
        "gemini-rag-test",
    )

    reset_model_registry_cache()

    assert (
        get_model_for_role(
            LLMRole.RAG
        )
        == "gemini-rag-test"
    )

    assert (
        get_model_for_role(
            LLMRole.REPORT
        )
        == "gemini-global-test"
    )


def test_blank_specific_value_uses_global(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_MODEL",
        "gemini-global-test",
    )

    monkeypatch.setenv(
        "INNA_REPORT_MODEL",
        "   ",
    )

    reset_model_registry_cache()

    assert (
        get_model_for_role(
            LLMRole.REPORT
        )
        == "gemini-global-test"
    )


def test_invalid_role_is_rejected():
    with pytest.raises(ValueError):
        get_model_for_role(
            "agente_inexistente"
        )

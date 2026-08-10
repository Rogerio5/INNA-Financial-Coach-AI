from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src import rag_engine


def _fake_gemini_response(
    *,
    text: str = "Resposta Gemini simulada.",
    input_tokens: int = 120,
    output_tokens: int = 30,
):
    return SimpleNamespace(
        text=text,
        usage_metadata=SimpleNamespace(
            prompt_token_count=input_tokens,
            candidates_token_count=output_tokens,
            total_token_count=(
                input_tokens + output_tokens
            ),
        ),
    )


def test_generate_gemini_rag_answer_captures_tokens(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "fake-key-unit-test",
    )

    from google import genai

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    response = _fake_gemini_response(
        input_tokens=120,
        output_tokens=30,
    )

    monkeypatch.setattr(
        rag_engine,
        "executar_generate_content_observado",
        lambda *args, **kwargs: response,
    )

    usage: dict[str, int] = {}

    result = (
        rag_engine.generate_gemini_rag_answer(
            pergunta=(
                "Como organizar meu orçamento?"
            ),
            contexto=(
                "Planejamento financeiro ajuda "
                "a organizar receitas e despesas."
            ),
            idioma="pt",
            usage_out=usage,
        )
    )

    assert (
        result
        == "Resposta Gemini simulada."
    )

    assert usage == {
        "tokens_entrada": 120,
        "tokens_saida": 30,
        "tokens_totais": 150,
    }


def test_generate_gemini_rag_answer_keeps_old_return_contract(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "fake-key-unit-test",
    )

    from google import genai

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    response = _fake_gemini_response(
        text="Contrato antigo preservado.",
        input_tokens=50,
        output_tokens=10,
    )

    monkeypatch.setattr(
        rag_engine,
        "executar_generate_content_observado",
        lambda *args, **kwargs: response,
    )

    result = (
        rag_engine.generate_gemini_rag_answer(
            pergunta="Pergunta simulada.",
            contexto="Contexto simulado.",
            idioma="pt",
        )
    )

    assert (
        result
        == "Contrato antigo preservado."
    )

    assert isinstance(result, str)


def test_generate_gemini_rag_answer_survives_missing_usage(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "fake-key-unit-test",
    )

    from google import genai

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    response = SimpleNamespace(
        text="Resposta sem usage metadata.",
    )

    monkeypatch.setattr(
        rag_engine,
        "executar_generate_content_observado",
        lambda *args, **kwargs: response,
    )

    usage: dict[str, int] = {
        "tokens_entrada": 999,
    }

    result = (
        rag_engine.generate_gemini_rag_answer(
            pergunta="Pergunta simulada.",
            contexto="Contexto simulado.",
            idioma="pt",
            usage_out=usage,
        )
    )

    assert (
        result
        == "Resposta sem usage metadata."
    )

    assert usage == {
        "tokens_entrada": 0,
        "tokens_saida": 0,
        "tokens_totais": 0,
    }


def test_answer_with_rag_token_contract_is_connected() -> None:
    source = Path(
        "src/rag_engine.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        source.count(
            "usage_out=gemini_usage"
        )
        == 5
    )

    assert (
        'payload["llm_usage"]'
        in source
    )

    assert (
        '"input_tokens"'
        in source
    )

    assert (
        '"output_tokens"'
        in source
    )

    assert (
        '"total_tokens"'
        in source
    )

    assert (
        '"billing_mode": billing_mode'
        in source
    )

    assert (
        "resolve_gemini_billing_mode()"
        in source
    )

    assert (
        '"billing_mode": "free_tier"'
        not in source
    )

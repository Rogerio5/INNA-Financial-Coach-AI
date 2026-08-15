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
    import src.services.llm.gemini as gemini_service

    captured = {}

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    def fake_generate(
        prompt,
        *,
        modelo=None,
        role=None,
        temperatura=0.3,
        max_tokens=2048,
        usage_out=None,
    ):
        captured["prompt"] = prompt
        captured["modelo"] = modelo
        captured["role"] = role

        assert usage_out is not None

        usage_out.update(
            {
                "tokens_entrada": 120,
                "tokens_saida": 30,
                "tokens_totais": 150,
            }
        )

        return "Resposta resiliente com usage."

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    usage = {}

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como organizar minha reserva?",
            "Contexto financeiro.",
            usage_out=usage,
        )
    )

    assert result == (
        "Resposta resiliente com usage."
    )

    assert usage == {
        "tokens_entrada": 120,
        "tokens_saida": 30,
        "tokens_totais": 150,
    }

    assert (
        captured["modelo"]
        == "gemini-3.5-flash-lite"
    )

    assert (
        captured["role"]
        == rag_engine.LLMRole.RAG
    )




def test_generate_gemini_rag_answer_keeps_old_return_contract(
    monkeypatch,
) -> None:
    import src.services.llm.gemini as gemini_service

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    def fake_generate(
        prompt,
        *,
        modelo=None,
        role=None,
        temperatura=0.3,
        max_tokens=2048,
        usage_out=None,
    ):
        if usage_out is not None:
            usage_out.update(
                {
                    "tokens_entrada": 50,
                    "tokens_saida": 10,
                    "tokens_totais": 60,
                }
            )

        return "Contrato antigo preservado."

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    usage = {}

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como organizar gastos?",
            "Contexto.",
            usage_out=usage,
        )
    )

    assert isinstance(
        result,
        str,
    )

    assert (
        result
        == "Contrato antigo preservado."
    )

    assert usage == {
        "tokens_entrada": 50,
        "tokens_saida": 10,
        "tokens_totais": 60,
    }




def test_generate_gemini_rag_answer_survives_missing_usage(
    monkeypatch,
) -> None:
    import src.services.llm.gemini as gemini_service

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-3.5-flash-lite",
    )

    def fake_generate(
        prompt,
        *,
        modelo=None,
        role=None,
        temperatura=0.3,
        max_tokens=2048,
        usage_out=None,
    ):
        if usage_out is not None:
            usage_out.update(
                {
                    "tokens_entrada": 0,
                    "tokens_saida": 0,
                    "tokens_totais": 0,
                }
            )

        return "Resposta sem usage metadata."

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    usage = {}

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como criar uma reserva?",
            "Contexto.",
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

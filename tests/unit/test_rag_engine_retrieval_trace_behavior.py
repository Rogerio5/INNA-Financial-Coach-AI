from __future__ import annotations

from uuid import UUID

import pytest

from src import rag_engine


def _rag_result(
    *,
    chunk_id: int = 10,
    modo_busca: str = "rag_hibrido",
) -> dict:
    return {
        "id": chunk_id,
        "chunk_id": chunk_id,
        "documento_id": 5,
        "titulo": "Guia financeiro",
        "fonte": "guia.md",
        "chunk_text": (
            "Organize sua renda, seus gastos "
            "e sua reserva financeira."
        ),
        "score": 0.82,
        "score_hibrido": 1.15,
        "score_rerank": 1.31,
        "origem_busca": [
            "vetorial",
            "textual",
        ],
        "modo_busca": modo_busca,
    }


def _disable_security(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_engine,
        "answer_security_financeira",
        lambda pergunta: None,
    )


def _disable_gemini(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_engine,
        "generate_gemini_rag_answer",
        lambda pergunta, contexto, idioma="pt", *, usage_out=None: None,
    )


def test_hybrid_result_exposes_retrieval_trace(
    monkeypatch: pytest.MonkeyPatch,
):
    _disable_security(monkeypatch)
    _disable_gemini(monkeypatch)

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_hybrid",
        lambda pergunta, idioma="pt", top_k=4: [
            _rag_result()
        ],
    )

    def local_search_must_not_run(
        pergunta,
        idioma="pt",
        top_k=4,
    ):
        raise AssertionError(
            "Fallback local não deveria executar."
        )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base",
        local_search_must_not_run,
    )

    resultado = rag_engine.answer_with_rag(
        pergunta="planejamento financeiro",
        idioma="pt",
        top_k=4,
    )

    assert resultado["resposta"]
    assert resultado["fontes"]
    assert resultado["modo"] == "rag_hibrido"

    trace_id = resultado["trace_id"]
    UUID(trace_id)

    trace = resultado["retrieval_trace"]

    assert trace["trace_id"] == trace_id
    assert trace["query"] == (
        "planejamento financeiro"
    )
    assert trace["language"] == "pt"
    assert trace["search_mode"] == "rag_hibrido"
    assert trace["top_k"] == 4
    assert trace["results_total"] == 1
    assert trace["total_time_ms"] >= 0

    item = trace["results"][0]

    assert item["position"] == 1
    assert item["chunk_id"] == 10
    assert item["document_id"] == 5
    assert item["hybrid_score"] == 1.15
    assert item["rerank_score"] == 1.31
    assert item["search_origins"] == (
        "vetorial",
        "textual",
    )


def test_legacy_local_fallback_is_not_used(
    monkeypatch: pytest.MonkeyPatch,
):
    """
    O runtime RAG principal é 3072-only.

    Quando o retrieval híbrido estruturado não
    retorna resultados, a execução não deve voltar
    para o retrieval legado.
    """
    _disable_security(monkeypatch)
    _disable_gemini(monkeypatch)

    calls = {
        "hybrid": 0,
        "local": 0,
    }

    def hybrid_search(
        pergunta,
        idioma="pt",
        top_k=4,
    ):
        calls["hybrid"] += 1
        return []

    def legacy_local_search(
        pergunta,
        idioma="pt",
        top_k=4,
    ):
        calls["local"] += 1

        raise AssertionError(
            "Legacy local RAG must not run "
            "in the 3072-only runtime."
        )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_hybrid",
        hybrid_search,
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base",
        legacy_local_search,
    )

    resultado = rag_engine.answer_with_rag(
        pergunta="educação financeira",
        idioma="pt",
        top_k=3,
    )

    assert calls == {
        "hybrid": 1,
        "local": 0,
    }

    assert resultado["fontes"] == []

    assert (
        resultado["retrieval_trace"][
            "search_mode"
        ]
        == "sem_resultados"
    )


def test_no_results_response_is_traced(
    monkeypatch: pytest.MonkeyPatch,
):
    _disable_security(monkeypatch)

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_hybrid",
        lambda pergunta, idioma="pt", top_k=4: [],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base",
        lambda pergunta, idioma="pt", top_k=4: [],
    )

    resultado = rag_engine.answer_with_rag(
        pergunta="assunto inexistente",
        idioma="pt",
        top_k=2,
    )

    assert resultado["fontes"] == []
    assert resultado["contexto_usado"] == ""
    assert resultado["modo"] == "sem_resultados"

    trace = resultado["retrieval_trace"]

    assert trace["search_mode"] == (
        "sem_resultados"
    )

    assert trace["results_total"] == 0
    assert trace["results"] == []
    assert trace["top_k"] == 2


def test_continuation_response_keeps_trace(
    monkeypatch: pytest.MonkeyPatch,
):
    _disable_security(monkeypatch)

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_hybrid",
        lambda pergunta, idioma="pt", top_k=4: [
            _rag_result()
        ],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base",
        lambda pergunta, idioma="pt", top_k=4: [],
    )

    monkeypatch.setattr(
        rag_engine,
        "detectar_intencao_continuacao",
        lambda pergunta: "cancelar",
    )

    monkeypatch.setattr(
        rag_engine,
        "resposta_cancelar_simples",
        lambda: {
            "resposta": "Tudo bem.",
            "fontes": [],
            "contexto_usado": "",
            "modo": "cancelamento",
        },
    )

    resultado = rag_engine.answer_with_rag(
        pergunta="pode cancelar",
        idioma="pt",
        top_k=4,
    )

    assert resultado["resposta"] == "Tudo bem."
    assert resultado["modo"] == "cancelamento"
    assert resultado["trace_id"]

    trace = resultado["retrieval_trace"]

    assert trace["results_total"] == 1
    assert trace["search_mode"] == (
        "rag_hibrido"
    )


def test_security_response_skips_retrieval(
    monkeypatch: pytest.MonkeyPatch,
):
    security_response = {
        "resposta": "Resposta de segurança.",
        "fontes": [],
        "contexto_usado": "",
        "modo": "seguranca",
    }

    monkeypatch.setattr(
        rag_engine,
        "answer_security_financeira",
        lambda pergunta: security_response,
    )

    def search_must_not_run(*args, **kwargs):
        raise AssertionError(
            "A recuperação não deveria executar."
        )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_hybrid",
        search_must_not_run,
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base",
        search_must_not_run,
    )

    resultado = rag_engine.answer_with_rag(
        pergunta="consulta bloqueada",
        idioma="pt",
        top_k=4,
    )

    assert resultado == security_response
    assert "trace_id" not in resultado
    assert "retrieval_trace" not in resultado


# RAG_MULTILINGUAL_RESPONSE_PROMPT_TESTS


@pytest.mark.parametrize(
    (
        "language",
        "expected_instruction",
    ),
    [
        (
            "ru",
            "Responda obrigatoriamente em russo.",
        ),
        (
            "sa",
            "Responda obrigatoriamente em árabe.",
        ),
        (
            "en-US",
            (
                "Responda obrigatoriamente em "
                "inglês dos Estados Unidos."
            ),
        ),
        (
            "de-CH",
            (
                "Responda obrigatoriamente em "
                "alemão da Suíça."
            ),
        ),
    ],
)

def test_generate_gemini_rag_answer_uses_requested_language(
    monkeypatch,
    language: str,
    expected_instruction: str,
):
    import src.services.llm.gemini as gemini_service

    captured = {}

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "test-model",
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
        captured["temperatura"] = temperatura
        captured["max_tokens"] = max_tokens

        return "Resposta simulada"

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como organizar minhas finanças?",
            "Contexto financeiro seguro.",
            idioma=language,
        )
    )

    assert result == "Resposta simulada"

    assert (
        expected_instruction
        in captured["prompt"]
    )

    assert (
        captured["modelo"]
        == "test-model"
    )

    assert (
        captured["role"]
        == rag_engine.LLMRole.RAG
    )

    assert (
        captured["temperatura"]
        == 0.3
    )

    assert (
        captured["max_tokens"]
        == 2048
    )




def test_generate_gemini_rag_answer_preserves_context_currency(
    monkeypatch,
):
    import src.services.llm.gemini as gemini_service

    captured = {}

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "test-model",
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

        return "Resposta simulada"

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como organizar esse valor?",
            (
                "O usuário informou uma reserva "
                "de USD 500."
            ),
            idioma="pt",
        )
    )

    assert result == "Resposta simulada"

    assert (
        "USD 500"
        in captured["prompt"]
    )

    assert (
        "Não converta valores e não invente moedas."
        in captured["prompt"]
    )

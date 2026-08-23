import inspect

from src import rag_engine


def _structured_result(
    *,
    result_id: int,
    document_id: int,
    document_key: str,
    chunk_id: str,
    score: float,
) -> dict:
    return {
        "id": result_id,
        "documento_id": document_id,
        "documento_key": document_key,
        "chunk_id": chunk_id,
        "chunk_index": 1,
        "titulo": "Orçamento",
        "categoria": "educacao_financeira",
        "chunk_text": (
            "Organize renda e gastos mensais."
        ),
        "trecho": (
            "Organize renda e gastos mensais."
        ),
        "conteudo": (
            "Organize renda e gastos mensais."
        ),
        "score": score,
    }


def test_hybrid_3072_uses_rrf_not_raw_score_sum(
    monkeypatch,
):
    vector_item = _structured_result(
        result_id=66,
        document_id=28,
        document_key=(
            "inna-edu-orcamento-002"
        ),
        chunk_id="orcamento-001",
        score=0.79,
    )

    text_item = dict(vector_item)
    text_item["score"] = 7.7
    text_item["score_textual"] = 7.7

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        lambda query, idioma="pt", top_k=6: [
            vector_item
        ],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        lambda query, idioma="pt", top_k=6: [
            text_item
        ],
    )

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        lambda query, results, top_k: (
            list(results)[:top_k]
        ),
    )

    results = (
        rag_engine.search_knowledge_base_hybrid(
            "Como organizar meu orçamento?",
            top_k=2,
            sentence_window_enabled=False,
        )
    )

    assert len(results) == 1

    item = results[0]

    assert item["documento_id"] == 28
    assert item["documento_key"] == (
        "inna-edu-orcamento-002"
    )

    assert item["origem_busca"] == [
        "textual",
        "vetorial",
    ]

    expected_rrf = (
        1.0 / 61.0
        + 1.0 / 61.0
    )

    assert abs(
        item["score_hibrido"]
        - expected_rrf
    ) < 1e-12

    assert (
        item["modo_busca"]
        == "rag_hibrido_"
        "estruturado_3072_rrf"
    )


def test_hybrid_3072_keeps_distinct_chunks(
    monkeypatch,
):
    vector_item = _structured_result(
        result_id=66,
        document_id=28,
        document_key=(
            "inna-edu-orcamento-002"
        ),
        chunk_id="orcamento-001",
        score=0.79,
    )

    text_item = _structured_result(
        result_id=67,
        document_id=28,
        document_key=(
            "inna-edu-orcamento-002"
        ),
        chunk_id="orcamento-002",
        score=7.7,
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        lambda query, idioma="pt", top_k=6: [
            vector_item
        ],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        lambda query, idioma="pt", top_k=6: [
            text_item
        ],
    )

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        lambda query, results, top_k: (
            list(results)[:top_k]
        ),
    )

    results = (
        rag_engine.search_knowledge_base_hybrid(
            "orçamento",
            top_k=2,
            sentence_window_enabled=False,
        )
    )

    assert len(results) == 2

    assert {
        item["chunk_id"]
        for item in results
    } == {
        "orcamento-001",
        "orcamento-002",
    }


def test_answer_runtime_has_no_legacy_rag_fallback():
    source = inspect.getsource(
        rag_engine.answer_with_rag
    )

    assert (
        "results = search_knowledge_base("
        not in source
    )

    assert (
        "search_knowledge_base_hybrid("
        in source
    )


def test_vector_runtime_is_structured_3072():
    source = inspect.getsource(
        rag_engine.search_knowledge_base_pgvector
    )

    assert "gerar_embedding_consulta" in source
    assert "buscar_chunks_semanticos" in source
    assert "dimensoes=3072" in source

    assert "inna_knowledge_chunks" not in source
    assert "generate_gemini_embedding" not in source


def test_text_runtime_is_structured():
    source = inspect.getsource(
        rag_engine.search_knowledge_base_text
    )

    assert "buscar_chunks_textuais" in source
    assert "inna_knowledge_chunks" not in source


def test_rerank_preserves_structured_3072_mode():
    item = _structured_result(
        result_id=66,
        document_id=28,
        document_key=(
            "inna-edu-orcamento-002"
        ),
        chunk_id="orcamento-001",
        score=0.79,
    )

    item["score_hibrido"] = 0.0327
    item["origem_busca"] = [
        "textual",
        "vetorial",
    ]
    item["modo_busca"] = (
        "rag_hibrido_estruturado_3072_rrf"
    )

    results = (
        rag_engine.rerank_knowledge_results(
            "Como organizar meu orçamento?",
            [item],
            top_k=1,
        )
    )

    assert len(results) == 1

    assert (
        results[0]["modo_busca"]
        == "rag_hibrido_"
        "estruturado_3072_rrf_rerank"
    )

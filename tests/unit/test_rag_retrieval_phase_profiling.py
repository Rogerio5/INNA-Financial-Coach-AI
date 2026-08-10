from __future__ import annotations

from src import rag_engine


def test_hybrid_retrieval_exposes_phase_timings(
    monkeypatch,
):
    vector_item = {
        "id": 1,
        "documento_id": 28,
        "chunk_id": "chunk-1",
        "chunk_text": "Conteúdo financeiro.",
        "score": 0.9,
        "similaridade_aproximada": 0.9,
        "modo_busca": (
            "rag_estruturado_3072_vetorial"
        ),
    }

    text_item = {
        "id": 1,
        "documento_id": 28,
        "chunk_id": "chunk-1",
        "chunk_text": "Conteúdo financeiro.",
        "score": 1.0,
        "score_textual": 1.0,
        "modo_busca": (
            "rag_estruturado_3072_textual"
        ),
    }

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        lambda *args, **kwargs: [vector_item],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        lambda *args, **kwargs: [text_item],
    )

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        lambda query, results, top_k=4: (
            results[:top_k]
        ),
    )

    profiling: dict[str, float] = {}

    results = (
        rag_engine.search_knowledge_base_hybrid(
            "Como organizar meu orçamento?",
            idioma="pt",
            top_k=2,
            sentence_window_enabled=False,
            profiling=profiling,
        )
    )

    assert results

    expected_keys = {
        "vector_retrieval_ms",
        "text_retrieval_ms",
        "rrf_ms",
        "rerank_ms",
        "auto_merging_ms",
        "sentence_window_ms",
        "retrieval_total_ms",
    }

    assert expected_keys == set(profiling)

    for key in expected_keys:
        assert profiling[key] >= 0

    assert profiling["sentence_window_ms"] == 0

    measured_sum = (
        profiling["vector_retrieval_ms"]
        + profiling["text_retrieval_ms"]
        + profiling["rrf_ms"]
        + profiling["rerank_ms"]
        + profiling["sentence_window_ms"]
    )

    assert (
        profiling["retrieval_total_ms"]
        >= measured_sum - 5
    )

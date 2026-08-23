from __future__ import annotations

from threading import Barrier

from src import rag_engine


def test_vector_and_text_retrieval_run_concurrently(
    monkeypatch,
):
    barrier = Barrier(
        2,
        timeout=3,
    )

    calls = []

    def fake_vector(
        query,
        idioma="pt",
        top_k=4,
        *,
        profiling=None,
    ):
        calls.append("vector_started")

        barrier.wait()

        calls.append("vector_released")

        if profiling is not None:
            profiling.update(
                {
                    "query_embedding_ms": 10.0,
                    "vector_conversion_ms": 1.0,
                    "vector_database_ms": 20.0,
                    "vector_postprocess_ms": 1.0,
                    "vector_semantic_total_ms": 32.0,
                }
            )

        return [
            {
                "id": 66,
                "documento_id": 28,
                "documento_key": (
                    "inna-edu-orcamento-002"
                ),
                "chunk_id": "orcamento-001",
                "chunk_index": 1,
                "chunk_text": (
                    "Planejamento mensal."
                ),
                "trecho": (
                    "Planejamento mensal."
                ),
                "conteudo": (
                    "Planejamento mensal."
                ),
                "similaridade_aproximada": 0.9,
                "score": 0.9,
            }
        ]

    def fake_text(
        query,
        idioma="pt",
        top_k=4,
    ):
        calls.append("text_started")

        barrier.wait()

        calls.append("text_released")

        return [
            {
                "id": 66,
                "documento_id": 28,
                "documento_key": (
                    "inna-edu-orcamento-002"
                ),
                "chunk_id": "orcamento-001",
                "chunk_index": 1,
                "chunk_text": (
                    "Planejamento mensal."
                ),
                "trecho": (
                    "Planejamento mensal."
                ),
                "conteudo": (
                    "Planejamento mensal."
                ),
                "score_textual": 0.8,
                "score": 0.8,
            }
        ]

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        fake_vector,
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        fake_text,
    )

    profiling = {}

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

    assert "vector_started" in calls
    assert "text_started" in calls
    assert "vector_released" in calls
    assert "text_released" in calls

    assert (
        results[0]["origem_busca"]
        == ["textual", "vetorial"]
    )

    assert "vector_retrieval_ms" in profiling
    assert "text_retrieval_ms" in profiling

    assert (
        profiling["query_embedding_ms"]
        == 10.0
    )

    assert (
        profiling["vector_database_ms"]
        == 20.0
    )

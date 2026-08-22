from __future__ import annotations

import src.rag_engine as rag_engine


def _result(
    *,
    chunk_index: int,
    chunk_id: str,
    text: str,
) -> dict:
    return {
        "documento_id": 28,
        "documento_key": "inna-edu-orcamento-002",
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "chunk_text": text,
        "trecho": text,
        "titulo": "Orçamento",
        "fonte": "documento-teste",
        "categoria": "orcamento",
        "idioma": "pt-BR",
        "score": 1.0,
    }


def _install_retrieval_fakes(
    monkeypatch,
) -> None:
    vector_result = _result(
        chunk_index=0,
        chunk_id="chunk-0",
        text="Primeiro trecho.",
    )

    text_result = _result(
        chunk_index=1,
        chunk_id="chunk-1",
        text="Segundo trecho.",
    )

    def fake_vector(
        query,
        *,
        idioma,
        top_k,
        profiling=None,
    ):
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

        return [dict(vector_result)]

    def fake_text(
        query,
        *,
        idioma,
        top_k,
    ):
        return [dict(text_result)]

    def fake_rerank(
        query,
        results,
        *,
        top_k,
    ):
        return list(results)[:top_k]

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

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        fake_rerank,
    )


def test_auto_merging_is_disabled_by_default(
    monkeypatch,
):
    _install_retrieval_fakes(monkeypatch)

    monkeypatch.delenv(
        "INNA_RAG_AUTO_MERGING_ENABLED",
        raising=False,
    )

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
        sentence_window_enabled=False,
    )

    assert len(results) == 2

    assert all(
        "auto_merging_applied" not in item
        for item in results
    )


def test_auto_merging_can_be_enabled_explicitly(
    monkeypatch,
):
    _install_retrieval_fakes(monkeypatch)

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
        sentence_window_enabled=False,
        auto_merging_enabled=True,
        auto_merging_parent_size=3,
        auto_merging_min_children=2,
        auto_merging_max_characters=4000,
    )

    assert len(results) == 1

    item = results[0]

    assert item["auto_merging_applied"] is True
    assert item["auto_merging_parent_index"] == 0
    assert item["auto_merging_child_count"] == 2
    assert item["auto_merging_child_indexes"] == [
        0,
        1,
    ]

    assert item["chunk_text"] == (
        "Primeiro trecho.\n\n"
        "Segundo trecho."
    )


def test_auto_merging_can_be_enabled_by_environment(
    monkeypatch,
):
    _install_retrieval_fakes(monkeypatch)

    monkeypatch.setenv(
        "INNA_RAG_AUTO_MERGING_ENABLED",
        "true",
    )
    monkeypatch.setenv(
        "INNA_RAG_AUTO_MERGING_PARENT_SIZE",
        "3",
    )
    monkeypatch.setenv(
        "INNA_RAG_AUTO_MERGING_MIN_CHILDREN",
        "2",
    )

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
        sentence_window_enabled=False,
    )

    assert len(results) == 1
    assert (
        results[0]["auto_merging_applied"]
        is True
    )


def test_auto_merging_failure_preserves_reranked_results(
    monkeypatch,
):
    _install_retrieval_fakes(monkeypatch)

    import src.services.rag.auto_merging as auto_merging

    def fail_auto_merge(*args, **kwargs):
        raise RuntimeError(
            "falha experimental"
        )

    monkeypatch.setattr(
        auto_merging,
        "auto_merge_results",
        fail_auto_merge,
    )

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
        sentence_window_enabled=False,
        auto_merging_enabled=True,
    )

    assert len(results) == 2
    assert results[0]["chunk_text"]
    assert results[1]["chunk_text"]


def test_auto_merging_exposes_profiling_time(
    monkeypatch,
):
    _install_retrieval_fakes(monkeypatch)

    profiling = {}

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
        sentence_window_enabled=False,
        auto_merging_enabled=True,
        profiling=profiling,
    )

    assert len(results) == 1
    assert "auto_merging_ms" in profiling
    assert profiling["auto_merging_ms"] >= 0.0

import src.rag_engine as rag_engine


def _result(document_key: str) -> dict:
    return {
        "id": 1,
        "documento_id": 10,
        "documento_key": document_key,
        "chunk_index": 2,
        "chunk_text": "Contexto original.",
        "texto": "Contexto original.",
        "trecho": "Contexto original.",
        "conteudo": "Contexto original.",
        "score": 0.95,
    }


def test_hybrid_search_uses_sentence_window_when_feature_flag_is_enabled(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_ENABLED",
        "true",
    )
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_SIZE",
        "5",
    )
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_CHUNK_RADIUS",
        "1",
    )
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_MAX_CHARACTERS",
        "4000",
    )

    candidate = _result("inna-edu-orcamento-002")

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        lambda query, idioma="pt", top_k=6: [candidate],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        lambda query, idioma="pt", top_k=6: [],
    )

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        lambda query, results, top_k: list(results)[:top_k],
    )

    captured = {}

    def fake_apply(**kwargs):
        captured.update(kwargs)
        result = dict(kwargs["results"][0])
        result["sentence_window_applied"] = True
        return [result]

    monkeypatch.setattr(
        rag_engine,
        "_apply_sentence_window_to_results",
        fake_apply,
    )

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
    )

    assert len(results) == 1
    assert results[0]["sentence_window_applied"] is True

    assert captured["window_size"] == 5
    assert captured["chunk_radius"] == 1
    assert captured["max_characters"] == 4000


def test_sentence_window_allowlist_applies_only_to_authorized_document(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_ALLOWED_DOCUMENT_KEYS",
        "inna-edu-orcamento-002",
    )

    allowed = _result(
        "inna-edu-orcamento-002",
    )

    blocked = _result(
        "inna-edu-outro-999",
    )
    blocked["id"] = 2

    monkeypatch.setattr(
        rag_engine,
        "_load_sentence_window_neighbor_chunks",
        lambda item, idioma, chunk_radius: [dict(item)],
    )

    def fake_expand(
        *,
        query,
        result,
        chunks,
        window_size,
        max_characters,
    ):
        expanded = dict(result)
        expanded["sentence_window_applied"] = True
        expanded["sentence_window_text"] = "Contexto expandido."
        return expanded

    try:
        import services.rag.sentence_window as sentence_window_module
    except ImportError:
        import src.services.rag.sentence_window as sentence_window_module

    monkeypatch.setattr(
        sentence_window_module,
        "expand_result_with_sentence_window",
        fake_expand,
    )

    import src.services.rag.sentence_window as src_sentence_window

    monkeypatch.setattr(
        src_sentence_window,
        "expand_result_with_sentence_window",
        fake_expand,
    )

    results = rag_engine._apply_sentence_window_to_results(
        query="Como organizar meu orçamento?",
        idioma="pt",
        results=[allowed, blocked],
        window_size=5,
        chunk_radius=1,
        max_characters=4000,
    )

    assert len(results) == 2

    assert results[0]["sentence_window_applied"] is True
    assert results[0]["sentence_window_policy"] == "selective_allowlist"
    assert (
        results[0]["sentence_window_document_key"]
        == "inna-edu-orcamento-002"
    )
    assert results[0]["sentence_window_skip_reason"] is None

    assert results[1]["sentence_window_applied"] is False
    assert results[1]["sentence_window_policy"] == "selective_allowlist"
    assert (
        results[1]["sentence_window_skip_reason"]
        == "document_not_allowed"
    )


def test_hybrid_search_preserves_baseline_when_feature_flag_is_disabled(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "INNA_RAG_SENTENCE_WINDOW_ENABLED",
        "false",
    )

    candidate = _result("inna-edu-orcamento-002")

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_pgvector",
        lambda query, idioma="pt", top_k=6: [candidate],
    )

    monkeypatch.setattr(
        rag_engine,
        "search_knowledge_base_text",
        lambda query, idioma="pt", top_k=6: [],
    )

    monkeypatch.setattr(
        rag_engine,
        "rerank_knowledge_results",
        lambda query, results, top_k: list(results)[:top_k],
    )

    def must_not_run(**kwargs):
        raise AssertionError(
            "Sentence Window should not run when disabled."
        )

    monkeypatch.setattr(
        rag_engine,
        "_apply_sentence_window_to_results",
        must_not_run,
    )

    results = rag_engine.search_knowledge_base_hybrid(
        "Como organizar meu orçamento?",
        idioma="pt",
        top_k=2,
    )

    assert len(results) == 1
    assert "sentence_window_applied" not in results[0]

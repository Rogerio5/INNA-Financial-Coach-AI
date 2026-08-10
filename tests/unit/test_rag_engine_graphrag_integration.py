from __future__ import annotations

from typing import Any

import src.knowledge_graph.retriever as graph_retriever_module
import src.rag_engine as rag_engine
from src.knowledge_graph.retriever import GraphRetrievalResult


def _candidate(*, chunk_id: str, chunk_index: int) -> dict[str, Any]:
    return {
        "documento_id": 28,
        "documento_key": "inna-edu-orcamento-002",
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "chunk_text": f"Texto {chunk_id}",
        "trecho": f"Texto {chunk_id}",
        "titulo": "Orcamento",
        "fonte": "base-rag",
        "categoria": "orcamento_pessoal",
        "idioma": "pt-BR",
        "score": 1.0,
    }


def _install_base_fakes(monkeypatch) -> None:
    def fake_vector(query, *, idioma, top_k, profiling=None):
        del query, idioma, top_k
        if profiling is not None:
            profiling["query_embedding_ms"] = 0.0
        return [_candidate(chunk_id="vector-chunk", chunk_index=1)]

    def fake_text(query, *, idioma, top_k):
        del query, idioma, top_k
        return [_candidate(chunk_id="text-chunk", chunk_index=2)]

    def fake_rerank(query, results, *, top_k):
        del query
        return list(results)[:top_k]

    monkeypatch.setattr(rag_engine, "search_knowledge_base_pgvector", fake_vector)
    monkeypatch.setattr(rag_engine, "search_knowledge_base_text", fake_text)
    monkeypatch.setattr(rag_engine, "rerank_knowledge_results", fake_rerank)


class FakeGraphRetriever:
    calls = 0
    fail = False
    same_as_vector = False

    @classmethod
    def from_environment(cls):
        cls.calls += 1
        if cls.fail:
            raise RuntimeError("graph unavailable")
        return cls()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def search(self, search_text, *, concept_limit, chunk_limit):
        del search_text, concept_limit, chunk_limit
        chunk_id = "vector-chunk" if self.same_as_vector else "graph-chunk"
        return [
            GraphRetrievalResult(
                document_id=28,
                chunk_id=chunk_id,
                document_key="inna-edu-orcamento-002",
                chunk_index=1 if self.same_as_vector else 3,
                text="Texto do grafo",
                concept_key="orcamento_pessoal",
                concept_node_id="concept:orcamento_pessoal",
                graph_score=1.25,
                metadata={
                    "document_title": "Orcamento",
                    "fonte": "base-rag",
                    "topic": "orcamento_pessoal",
                    "idioma": "pt-BR",
                },
            )
        ]


def _install_graph_fake(monkeypatch, *, fail=False, same_as_vector=False):
    graph_retriever_module.reset_shared_graph_retriever()
    FakeGraphRetriever.calls = 0
    FakeGraphRetriever.fail = fail
    FakeGraphRetriever.same_as_vector = same_as_vector
    monkeypatch.setattr(
        graph_retriever_module,
        "GraphKnowledgeRetriever",
        FakeGraphRetriever,
    )


def test_graph_disabled_preserves_baseline(monkeypatch):
    _install_base_fakes(monkeypatch)
    _install_graph_fake(monkeypatch)
    profiling: dict[str, float] = {}
    results = rag_engine.search_knowledge_base_hybrid(
        "orcamento",
        idioma="pt",
        top_k=3,
        sentence_window_enabled=False,
        auto_merging_enabled=False,
        graph_rag_enabled=False,
        profiling=profiling,
    )
    assert len(results) == 2
    assert FakeGraphRetriever.calls == 0
    assert profiling["graph_retrieval_ms"] == 0.0
    assert all("grafo" not in (item.get("origem_busca") or []) for item in results)


def test_graph_channel_enters_rrf(monkeypatch):
    _install_base_fakes(monkeypatch)
    _install_graph_fake(monkeypatch)
    results = rag_engine.search_knowledge_base_hybrid(
        "orcamento",
        idioma="pt",
        top_k=3,
        sentence_window_enabled=False,
        auto_merging_enabled=False,
        graph_rag_enabled=True,
    )
    graph_items = [
        item for item in results if "grafo" in (item.get("origem_busca") or [])
    ]
    assert len(results) == 3
    assert FakeGraphRetriever.calls == 1
    assert len(graph_items) == 1
    graph_item = graph_items[0]
    assert graph_item["rrf_rank_grafo"] == 1
    assert graph_item["rrf_contribution_grafo"] > 0
    assert graph_item["score_graph"] == 1.25
    assert graph_item["graph_concept_key"] == "orcamento_pessoal"
    assert graph_item["modo_busca"] == "rag_hibrido_grafo_estruturado_3072_rrf"


def test_graph_merges_same_structured_identity(monkeypatch):
    _install_base_fakes(monkeypatch)
    _install_graph_fake(monkeypatch, same_as_vector=True)
    results = rag_engine.search_knowledge_base_hybrid(
        "orcamento",
        idioma="pt",
        top_k=3,
        sentence_window_enabled=False,
        auto_merging_enabled=False,
        graph_rag_enabled=True,
    )
    assert len(results) == 2
    merged = next(item for item in results if item["chunk_id"] == "vector-chunk")
    assert set(merged["origem_busca"]) == {"grafo", "vetorial"}
    assert merged["rrf_rank_vetorial"] == 1
    assert merged["rrf_rank_grafo"] == 1
    assert merged["score_graph"] == 1.25
    assert merged["graph_retrieval"] is True


def test_graph_failure_preserves_vector_text(monkeypatch):
    _install_base_fakes(monkeypatch)
    _install_graph_fake(monkeypatch, fail=True)
    results = rag_engine.search_knowledge_base_hybrid(
        "orcamento",
        idioma="pt",
        top_k=3,
        sentence_window_enabled=False,
        auto_merging_enabled=False,
        graph_rag_enabled=True,
    )
    assert len(results) == 2
    assert FakeGraphRetriever.calls == 1
    assert all("grafo" not in (item.get("origem_busca") or []) for item in results)

def test_graph_retriever_is_reused_between_hybrid_calls(
    monkeypatch,
):
    _install_base_fakes(monkeypatch)
    _install_graph_fake(monkeypatch)

    try:
        first = rag_engine.search_knowledge_base_hybrid(
            "orcamento",
            idioma="pt",
            top_k=3,
            sentence_window_enabled=False,
            auto_merging_enabled=False,
            graph_rag_enabled=True,
        )

        second = rag_engine.search_knowledge_base_hybrid(
            "orcamento",
            idioma="pt",
            top_k=3,
            sentence_window_enabled=False,
            auto_merging_enabled=False,
            graph_rag_enabled=True,
        )

        assert any(
            "grafo" in (
                item.get("origem_busca")
                or []
            )
            for item in first
        )

        assert any(
            "grafo" in (
                item.get("origem_busca")
                or []
            )
            for item in second
        )

        assert FakeGraphRetriever.calls == 1
    finally:
        graph_retriever_module.reset_shared_graph_retriever()

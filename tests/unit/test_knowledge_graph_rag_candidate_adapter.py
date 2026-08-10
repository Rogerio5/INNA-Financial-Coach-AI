from __future__ import annotations

from src.knowledge_graph.rag_candidate_adapter import (
    graph_result_to_rag_candidate,
    graph_results_to_rag_candidates,
)
from src.knowledge_graph.retriever import (
    GraphRetrievalResult,
)


def _result(
    *,
    chunk_id: str = "chunk-1",
) -> GraphRetrievalResult:
    return GraphRetrievalResult(
        document_id=28,
        chunk_id=chunk_id,
        document_key="inna-edu-orcamento-002",
        chunk_index=1,
        text="Texto do chunk.",
        concept_key="orcamento_pessoal",
        concept_node_id=(
            "concept:orcamento_pessoal"
        ),
        graph_score=1.25,
        metadata={
            "document_title": "OrÃ§amento pessoal",
            "fonte": "base-rag",
            "topic": "orcamento_pessoal",
            "idioma": "pt-BR",
        },
    )


def test_adapter_matches_native_structured_identity() -> None:
    candidate = (
        graph_result_to_rag_candidate(
            _result()
        )
    )

    assert candidate[
        "documento_id"
    ] == 28
    assert candidate[
        "documento_key"
    ] == "inna-edu-orcamento-002"
    assert candidate[
        "chunk_id"
    ] == "chunk-1"
    assert candidate[
        "chunk_index"
    ] == 1


def test_adapter_supplies_rerank_and_answer_fields() -> None:
    candidate = (
        graph_result_to_rag_candidate(
            _result()
        )
    )

    required = {
        "chunk_text",
        "texto",
        "trecho",
        "titulo",
        "fonte",
        "categoria",
        "idioma",
        "score",
    }

    assert required.issubset(
        candidate
    )

    assert candidate[
        "chunk_text"
    ] == "Texto do chunk."
    assert candidate[
        "trecho"
    ] == "Texto do chunk."
    assert candidate[
        "titulo"
    ] == "OrÃ§amento pessoal"
    assert candidate[
        "fonte"
    ] == "base-rag"
    assert candidate[
        "categoria"
    ] == "orcamento_pessoal"
    assert candidate[
        "score"
    ] == 1.25


def test_adapter_preserves_graph_provenance() -> None:
    candidate = (
        graph_result_to_rag_candidate(
            _result()
        )
    )

    assert candidate[
        "graph_retrieval"
    ] is True
    assert candidate[
        "score_graph"
    ] == 1.25
    assert candidate[
        "graph_concept_key"
    ] == "orcamento_pessoal"


def test_adapter_deduplicates_structured_identity() -> None:
    result = _result()

    candidates = (
        graph_results_to_rag_candidates(
            [
                result,
                result,
            ]
        )
    )

    assert len(candidates) == 1


def test_adapter_uses_safe_fallback_metadata() -> None:
    result = GraphRetrievalResult(
        document_id=28,
        chunk_id="chunk-1",
        document_key="inna-edu-orcamento-002",
        chunk_index=1,
        text="Texto.",
        concept_key="orcamento_pessoal",
        concept_node_id=(
            "concept:orcamento_pessoal"
        ),
        graph_score=0.5,
        metadata={},
    )

    candidate = (
        graph_result_to_rag_candidate(
            result
        )
    )

    assert candidate[
        "titulo"
    ] == "inna-edu-orcamento-002"
    assert candidate[
        "fonte"
    ] == "inna-edu-orcamento-002"
    assert candidate[
        "categoria"
    ] == "orcamento_pessoal"
    assert candidate[
        "idioma"
    ] == "pt"

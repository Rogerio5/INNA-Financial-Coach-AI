from __future__ import annotations

from src.knowledge_graph.models import (
    FinancialConceptNode,
    FinancialTopicNode,
)
from src.knowledge_graph.rag_source import (
    RagChunkRecord,
    RagDocumentRecord,
    RagKnowledgeSnapshot,
)
from src.knowledge_graph.relationships import (
    KnowledgeRelationshipType,
)
from src.knowledge_graph.semantic_enricher import (
    SemanticKnowledgeGraphEnricher,
)


def _snapshot() -> RagKnowledgeSnapshot:
    documents = (
        RagDocumentRecord(
            document_id=28,
            document_key="inna-edu-orcamento-002",
            original_name=None,
            saved_name=None,
            origin="seed",
        ),
        RagDocumentRecord(
            document_id=29,
            document_key="inna-edu-reserva-002",
            original_name=None,
            saved_name=None,
            origin="seed",
        ),
    )

    chunks = (
        RagChunkRecord(
            document_id=28,
            document_key="inna-edu-orcamento-002",
            chunk_id="chunk-orcamento-1",
            chunk_index=1,
            text="texto",
            metadata={
                "topic": "orcamento_pessoal",
                "area": "educacao_financeira",
            },
        ),
        RagChunkRecord(
            document_id=28,
            document_key="inna-edu-orcamento-002",
            chunk_id="chunk-orcamento-2",
            chunk_index=2,
            text="texto",
            metadata={
                "topic": "orcamento_pessoal",
                "area": "educacao_financeira",
            },
        ),
        RagChunkRecord(
            document_id=29,
            document_key="inna-edu-reserva-002",
            chunk_id="chunk-reserva-1",
            chunk_index=1,
            text="texto",
            metadata={
                "topic": "reserva_de_emergencia",
                "area": "educacao_financeira",
            },
        ),
    )

    return RagKnowledgeSnapshot(
        documents=documents,
        chunks=chunks,
    )


def test_enricher_creates_topics_and_concepts() -> None:
    plan = (
        SemanticKnowledgeGraphEnricher()
        .build(_snapshot())
    )

    assert plan.topic_count == 1
    assert plan.concept_count == 2
    assert plan.node_count == 3

    assert sum(
        isinstance(
            node,
            FinancialTopicNode,
        )
        for node in plan.nodes
    ) == 1

    assert sum(
        isinstance(
            node,
            FinancialConceptNode,
        )
        for node in plan.nodes
    ) == 2


def test_enricher_creates_expected_relationship_counts() -> None:
    plan = (
        SemanticKnowledgeGraphEnricher()
        .build(_snapshot())
    )

    assert plan.belongs_to_count == 2
    assert plan.explains_count == 2
    assert plan.mentions_count == 3
    assert plan.relationship_count == 7


def test_enricher_creates_expected_relationship_types() -> None:
    plan = (
        SemanticKnowledgeGraphEnricher()
        .build(_snapshot())
    )

    relationship_types = {
        relationship.relationship_type
        for relationship in plan.relationships
    }

    assert relationship_types == {
        KnowledgeRelationshipType.BELONGS_TO,
        KnowledgeRelationshipType.EXPLAINS,
        KnowledgeRelationshipType.MENTIONS,
    }


def test_enricher_rejects_document_semantic_conflict() -> None:
    snapshot = _snapshot()

    conflicting = RagChunkRecord(
        document_id=28,
        document_key="inna-edu-orcamento-002",
        chunk_id="chunk-orcamento-conflict",
        chunk_index=3,
        text="texto",
        metadata={
            "topic": "outro_topico",
            "area": "educacao_financeira",
        },
    )

    invalid_snapshot = RagKnowledgeSnapshot(
        documents=snapshot.documents,
        chunks=snapshot.chunks + (
            conflicting,
        ),
    )

    try:
        SemanticKnowledgeGraphEnricher().build(
            invalid_snapshot
        )
    except ValueError as exc:
        assert "inconsistentes" in str(exc)
    else:
        raise AssertionError(
            "Conflito semÃ¢ntico deveria falhar."
        )


def test_enricher_rejects_topic_mapped_to_two_areas() -> None:
    documents = (
        RagDocumentRecord(
            document_id=1,
            document_key="doc-a",
            original_name=None,
            saved_name=None,
            origin=None,
        ),
        RagDocumentRecord(
            document_id=2,
            document_key="doc-b",
            original_name=None,
            saved_name=None,
            origin=None,
        ),
    )

    chunks = (
        RagChunkRecord(
            document_id=1,
            document_key="doc-a",
            chunk_id="chunk-a",
            chunk_index=1,
            text="texto",
            metadata={
                "topic": "mesmo_topico",
                "area": "area_a",
            },
        ),
        RagChunkRecord(
            document_id=2,
            document_key="doc-b",
            chunk_id="chunk-b",
            chunk_index=1,
            text="texto",
            metadata={
                "topic": "mesmo_topico",
                "area": "area_b",
            },
        ),
    )

    snapshot = RagKnowledgeSnapshot(
        documents=documents,
        chunks=chunks,
    )

    try:
        SemanticKnowledgeGraphEnricher().build(
            snapshot
        )
    except ValueError as exc:
        assert "Ã¡reas diferentes" in str(exc)
    else:
        raise AssertionError(
            "Topic ambÃ­guo deveria falhar."
        )


def test_enricher_rejects_missing_topic_or_area() -> None:
    document = RagDocumentRecord(
        document_id=1,
        document_key="doc-a",
        original_name=None,
        saved_name=None,
        origin=None,
    )

    chunk = RagChunkRecord(
        document_id=1,
        document_key="doc-a",
        chunk_id="chunk-a",
        chunk_index=1,
        text="texto",
        metadata={
            "topic": "",
            "area": "area_a",
        },
    )

    snapshot = RagKnowledgeSnapshot(
        documents=(document,),
        chunks=(chunk,),
    )

    try:
        SemanticKnowledgeGraphEnricher().build(
            snapshot
        )
    except ValueError as exc:
        assert "metadata.topic" in str(exc)
    else:
        raise AssertionError(
            "Topic vazio deveria falhar."
        )

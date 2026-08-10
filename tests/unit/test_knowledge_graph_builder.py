from __future__ import annotations

from src.knowledge_graph.builder import (
    KnowledgeGraphBuilder,
)
from src.knowledge_graph.models import (
    ChunkNode,
    DocumentNode,
    SourceNode,
)
from src.knowledge_graph.rag_source import (
    RagChunkRecord,
    RagDocumentRecord,
    RagKnowledgeSnapshot,
)
from src.knowledge_graph.relationships import (
    KnowledgeRelationshipType,
)


def _snapshot() -> RagKnowledgeSnapshot:
    document = RagDocumentRecord(
        document_id=28,
        document_key="inna-edu-orcamento-002",
        original_name="orcamento.md",
        saved_name="orcamento.md",
        origin="seed",
    )

    chunks = (
        RagChunkRecord(
            document_id=28,
            document_key=document.document_key,
            chunk_id="chunk-orcamento-1",
            chunk_index=1,
            text="Primeiro trecho.",
            metadata={
                "content_hash": (
                    "hash-persistido"
                ),
                "document_title": (
                    "OrÃ§amento pessoal"
                ),
                "version": "2",
            },
        ),
        RagChunkRecord(
            document_id=28,
            document_key=document.document_key,
            chunk_id="chunk-orcamento-2",
            chunk_index=2,
            text="Segundo trecho.",
            metadata={
                "topic": "orcamento",
            },
        ),
    )

    return RagKnowledgeSnapshot(
        documents=(document,),
        chunks=chunks,
    )


def test_builder_creates_document_source_and_chunks() -> None:
    plan = KnowledgeGraphBuilder().build(
        _snapshot()
    )

    assert plan.document_count == 1
    assert plan.chunk_count == 2
    assert plan.node_count == 4
    assert plan.relationship_count == 3

    assert sum(
        isinstance(node, DocumentNode)
        for node in plan.nodes
    ) == 1

    assert sum(
        isinstance(node, SourceNode)
        for node in plan.nodes
    ) == 1

    assert sum(
        isinstance(node, ChunkNode)
        for node in plan.nodes
    ) == 2


def test_builder_creates_expected_relationships() -> None:
    plan = KnowledgeGraphBuilder().build(
        _snapshot()
    )

    relationship_types = [
        relationship.relationship_type
        for relationship in plan.relationships
    ]

    assert relationship_types.count(
        KnowledgeRelationshipType.SOURCED_FROM
    ) == 1

    assert relationship_types.count(
        KnowledgeRelationshipType.HAS_CHUNK
    ) == 2


def test_builder_uses_persisted_and_computed_hashes() -> None:
    plan = KnowledgeGraphBuilder().build(
        _snapshot()
    )

    chunks = [
        node
        for node in plan.nodes
        if isinstance(node, ChunkNode)
    ]

    assert (
        chunks[0].content_hash
        == "hash-persistido"
    )
    assert len(
        chunks[1].content_hash
    ) == 64


def test_builder_uses_document_title_and_version() -> None:
    plan = KnowledgeGraphBuilder().build(
        _snapshot()
    )

    document = next(
        node
        for node in plan.nodes
        if isinstance(node, DocumentNode)
    )

    assert (
        document.label
        == "OrÃ§amento pessoal"
    )
    assert document.version == "2"


def test_builder_does_not_store_chunk_text_in_metadata() -> None:
    plan = KnowledgeGraphBuilder().build(
        _snapshot()
    )

    chunks = [
        node
        for node in plan.nodes
        if isinstance(node, ChunkNode)
    ]

    for node in chunks:
        assert "text" not in node.metadata
        assert "texto" not in node.metadata
        assert (
            "chunk_text"
            not in node.metadata
        )


def test_builder_rejects_chunk_document_key_mismatch() -> None:
    snapshot = _snapshot()

    invalid_chunk = RagChunkRecord(
        document_id=28,
        document_key="outra-chave",
        chunk_id="chunk-invalid",
        chunk_index=3,
        text="Trecho.",
        metadata={},
    )

    invalid_snapshot = RagKnowledgeSnapshot(
        documents=snapshot.documents,
        chunks=(
            snapshot.chunks
            + (invalid_chunk,)
        ),
    )

    try:
        KnowledgeGraphBuilder().build(
            invalid_snapshot
        )
    except ValueError as exc:
        assert "incompatÃ­vel" in str(exc)
    else:
        raise AssertionError(
            "Builder deveria rejeitar "
            "document_key incompatÃ­vel."
        )

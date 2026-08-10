from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.knowledge_graph import (
    ChunkNode,
    DocumentNode,
    FinancialConceptNode,
    FinancialTopicNode,
    KnowledgeGraphRelationship,
    KnowledgeGraphSchema,
    KnowledgeNodeType,
    KnowledgeRelationshipType,
    SourceNode,
)


def _document() -> DocumentNode:
    return DocumentNode(
        node_id="document:inna-edu-orcamento-002",
        label="OrÃ§amento pessoal",
        document_key="inna-edu-orcamento-002",
        version="2",
    )


def _chunk() -> ChunkNode:
    return ChunkNode(
        node_id="chunk:inna-edu-orcamento-002:0",
        label="Chunk 0",
        chunk_key="inna-edu-orcamento-002:0",
        document_key="inna-edu-orcamento-002",
        ordinal=0,
    )


def _concept() -> FinancialConceptNode:
    return FinancialConceptNode(
        node_id="concept:gastos-fixos",
        label="Gastos fixos",
        concept_key="gastos-fixos",
        aliases=("despesas fixas",),
    )


def test_domain_model_supports_the_five_initial_node_types() -> None:
    nodes = (
        _document(),
        _chunk(),
        _concept(),
        FinancialTopicNode(
            node_id="topic:orcamento",
            label="OrÃ§amento",
            topic_key="orcamento",
        ),
        SourceNode(
            node_id="source:knowledge-base",
            label="Knowledge Base",
            source_key="knowledge-base",
            source_type="repository_document",
        ),
    )

    assert {node.node_type for node in nodes} == {
        KnowledgeNodeType.DOCUMENT,
        KnowledgeNodeType.CHUNK,
        KnowledgeNodeType.FINANCIAL_CONCEPT,
        KnowledgeNodeType.FINANCIAL_TOPIC,
        KnowledgeNodeType.SOURCE,
    }


def test_nodes_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        DocumentNode(
            node_id="document:test",
            label="Test",
            document_key="test",
            unexpected=True,
        )


def test_nodes_are_immutable() -> None:
    node = _concept()

    with pytest.raises(ValidationError):
        node.label = "Changed"


def test_relationship_rejects_self_reference() -> None:
    with pytest.raises(ValidationError):
        KnowledgeGraphRelationship(
            source_id="concept:test",
            target_id="concept:test",
            relationship_type=KnowledgeRelationshipType.RELATED_TO,
        )


def test_schema_accepts_document_has_chunk() -> None:
    schema = KnowledgeGraphSchema()
    document = _document()
    chunk = _chunk()
    relationship = KnowledgeGraphRelationship(
        source_id=document.node_id,
        target_id=chunk.node_id,
        relationship_type=KnowledgeRelationshipType.HAS_CHUNK,
    )

    schema.validate_relationship(
        source=document,
        relationship=relationship,
        target=chunk,
    )


def test_schema_rejects_invalid_relationship_direction() -> None:
    schema = KnowledgeGraphSchema()
    document = _document()
    chunk = _chunk()
    relationship = KnowledgeGraphRelationship(
        source_id=chunk.node_id,
        target_id=document.node_id,
        relationship_type=KnowledgeRelationshipType.HAS_CHUNK,
    )

    with pytest.raises(ValueError, match="not allowed"):
        schema.validate_relationship(
            source=chunk,
            relationship=relationship,
            target=document,
        )


def test_schema_validates_a_small_financial_graph() -> None:
    schema = KnowledgeGraphSchema()
    document = _document()
    chunk = _chunk()
    concept = _concept()

    relationships = (
        KnowledgeGraphRelationship(
            source_id=document.node_id,
            target_id=chunk.node_id,
            relationship_type=KnowledgeRelationshipType.HAS_CHUNK,
        ),
        KnowledgeGraphRelationship(
            source_id=chunk.node_id,
            target_id=concept.node_id,
            relationship_type=KnowledgeRelationshipType.MENTIONS,
        ),
        KnowledgeGraphRelationship(
            source_id=document.node_id,
            target_id=concept.node_id,
            relationship_type=KnowledgeRelationshipType.EXPLAINS,
        ),
    )

    schema.validate_graph(
        nodes=(document, chunk, concept),
        relationships=relationships,
    )
from __future__ import annotations

from src.knowledge_graph import (
    COMMON_NODE_LABEL,
    CONSTRAINT_STATEMENTS,
    INDEX_STATEMENTS,
    NODE_LABEL_BY_TYPE,
    RELATIONSHIP_TYPE_TO_CYPHER,
    SCHEMA_STATEMENTS,
    CypherSchemaStatementKind,
    KnowledgeNodeType,
    KnowledgeRelationshipType,
    cypher_label_for_node_type,
    cypher_relationship_type,
    schema_statement_names,
)


def test_node_label_mapping_covers_every_domain_node_type() -> None:
    assert set(NODE_LABEL_BY_TYPE) == set(KnowledgeNodeType)
    assert COMMON_NODE_LABEL == "KnowledgeNode"
    assert cypher_label_for_node_type(KnowledgeNodeType.DOCUMENT) == "Document"
    assert cypher_label_for_node_type(KnowledgeNodeType.CHUNK) == "Chunk"


def test_relationship_mapping_covers_every_relationship_type() -> None:
    assert set(RELATIONSHIP_TYPE_TO_CYPHER) == set(KnowledgeRelationshipType)
    assert (
        cypher_relationship_type(KnowledgeRelationshipType.HAS_CHUNK)
        == "HAS_CHUNK"
    )
    assert (
        cypher_relationship_type(KnowledgeRelationshipType.SOURCED_FROM)
        == "SOURCED_FROM"
    )


def test_schema_has_expected_initial_constraint_and_index_plan() -> None:
    assert len(CONSTRAINT_STATEMENTS) == 6
    assert len(INDEX_STATEMENTS) == 2
    assert len(SCHEMA_STATEMENTS) == 8

    assert all(
        statement.kind is CypherSchemaStatementKind.UNIQUE_CONSTRAINT
        for statement in CONSTRAINT_STATEMENTS
    )

    assert {
        statement.kind for statement in INDEX_STATEMENTS
    } == {
        CypherSchemaStatementKind.RANGE_INDEX,
        CypherSchemaStatementKind.FULLTEXT_INDEX,
    }


def test_schema_statement_names_are_unique_and_stable() -> None:
    names = schema_statement_names()

    assert len(names) == len(set(names))
    assert "kg_knowledge_node_node_id_unique" in names
    assert "kg_chunk_document_ordinal_range" in names
    assert "kg_financial_knowledge_fulltext" in names


def test_every_schema_statement_is_idempotent() -> None:
    for statement in SCHEMA_STATEMENTS:
        assert "IF NOT EXISTS" in statement.cypher
        assert statement.name in statement.cypher


def test_unique_constraints_cover_global_and_business_identifiers() -> None:
    constrained_schemas = {
        (statement.labels, statement.properties)
        for statement in CONSTRAINT_STATEMENTS
    }

    assert (("KnowledgeNode",), ("node_id",)) in constrained_schemas
    assert (("Document",), ("document_key",)) in constrained_schemas
    assert (("Chunk",), ("chunk_key",)) in constrained_schemas
    assert (("FinancialConcept",), ("concept_key",)) in constrained_schemas
    assert (("FinancialTopic",), ("topic_key",)) in constrained_schemas
    assert (("Source",), ("source_key",)) in constrained_schemas


def test_explicit_range_index_does_not_duplicate_constraint_backing_index() -> None:
    constraint_backing_schemas = {
        (statement.labels, statement.properties)
        for statement in CONSTRAINT_STATEMENTS
    }

    range_index_schemas = {
        (statement.labels, statement.properties)
        for statement in INDEX_STATEMENTS
        if statement.kind is CypherSchemaStatementKind.RANGE_INDEX
    }

    assert constraint_backing_schemas.isdisjoint(range_index_schemas)


def test_chunk_composite_range_index_supports_document_order_lookup() -> None:
    range_statement = next(
        statement
        for statement in INDEX_STATEMENTS
        if statement.kind is CypherSchemaStatementKind.RANGE_INDEX
    )

    assert range_statement.labels == ("Chunk",)
    assert range_statement.properties == ("document_key", "ordinal")
    assert "ON (n.document_key, n.ordinal)" in range_statement.cypher


def test_financial_fulltext_index_supports_labels_descriptions_and_aliases() -> None:
    fulltext_statement = next(
        statement
        for statement in INDEX_STATEMENTS
        if statement.kind is CypherSchemaStatementKind.FULLTEXT_INDEX
    )

    assert fulltext_statement.labels == (
        "FinancialConcept",
        "FinancialTopic",
    )
    assert fulltext_statement.properties == (
        "label",
        "description",
        "aliases",
    )
    assert "CREATE FULLTEXT INDEX" in fulltext_statement.cypher
    assert "FinancialConcept|FinancialTopic" in fulltext_statement.cypher
    assert "ON EACH [n.label, n.description, n.aliases]" in fulltext_statement.cypher


def test_initial_schema_does_not_duplicate_pgvector_with_neo4j_vector_index() -> None:
    assert all("VECTOR INDEX" not in statement.cypher for statement in SCHEMA_STATEMENTS)

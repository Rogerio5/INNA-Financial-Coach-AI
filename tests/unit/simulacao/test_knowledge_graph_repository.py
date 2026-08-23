from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from src.knowledge_graph import (
    DocumentNode,
    FinancialConceptNode,
    KnowledgeGraphRelationship,
    KnowledgeRelationshipType,
)
from src.knowledge_graph.exceptions import KnowledgeGraphPersistenceError
from src.knowledge_graph.repository import KnowledgeGraphRepository


class FakeResult:
    def __init__(self, record: dict[str, Any] | None) -> None:
        self._record = record

    def single(self) -> dict[str, Any] | None:
        return self._record


class FakeTransaction:
    def __init__(self, records: list[dict[str, Any] | None]) -> None:
        self._records = list(records)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def run(self, query: str, **parameters: Any) -> FakeResult:
        self.calls.append((query, parameters))
        record = self._records.pop(0) if self._records else None
        return FakeResult(record)


class FakeSession:
    def __init__(self, transaction: FakeTransaction) -> None:
        self.transaction = transaction
        self.write_calls = 0
        self.read_calls = 0

    def __enter__(self) -> FakeSession:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def execute_write(self, callback: Callable[..., Any], *args: Any) -> Any:
        self.write_calls += 1
        return callback(self.transaction, *args)

    def execute_read(self, callback: Callable[..., Any], *args: Any) -> Any:
        self.read_calls += 1
        return callback(self.transaction, *args)


class FakeDriver:
    def __init__(self, session: FakeSession) -> None:
        self._session = session
        self.databases: list[str] = []

    def session(self, *, database: str) -> FakeSession:
        self.databases.append(database)
        return self._session


class FakeClient:
    def __init__(self, driver: FakeDriver) -> None:
        self._driver = driver
        self.database = "neo4j-test"

    def connect(self) -> FakeDriver:
        return self._driver


def _repository(
    records: list[dict[str, Any] | None],
) -> tuple[KnowledgeGraphRepository, FakeTransaction, FakeDriver]:
    transaction = FakeTransaction(records)
    session = FakeSession(transaction)
    driver = FakeDriver(session)
    client = FakeClient(driver)
    repository = KnowledgeGraphRepository(client)  # type: ignore[arg-type]
    return repository, transaction, driver


def _document() -> DocumentNode:
    return DocumentNode(
        node_id="document:inna-edu-orcamento-002",
        label="Or??amento pessoal",
        metadata={"language": "pt-BR", "nested": {"safe": True}},
        document_key="inna-edu-orcamento-002",
        version="2",
    )


def test_upsert_node_uses_fixed_labels_and_parameterized_values() -> None:
    node = _document()
    repository, transaction, driver = _repository(
        [{"node_id": node.node_id}]
    )

    repository.upsert_node(node)

    query, parameters = transaction.calls[0]
    assert "MERGE (n:KnowledgeNode:Document" in query
    assert node.node_id not in query
    assert "$node_id" in query
    assert parameters["node_id"] == node.node_id
    assert parameters["properties"]["document_key"] == node.document_key
    assert parameters["properties"]["metadata_json"] == (
        '{"language":"pt-BR","nested":{"safe":true}}'
    )
    assert driver.databases == ["neo4j-test"]


def test_upsert_node_does_not_interpolate_payload_into_cypher() -> None:
    node = DocumentNode(
        node_id="document:') MATCH (x) DETACH DELETE x //",
        label="Injection-looking payload",
        document_key="safe-key",
    )
    repository, transaction, _ = _repository([{"node_id": node.node_id}])

    repository.upsert_node(node)

    query, parameters = transaction.calls[0]
    assert node.node_id not in query
    assert parameters["node_id"] == node.node_id


def test_node_exists_returns_boolean() -> None:
    repository, transaction, _ = _repository([{"exists": True}])

    assert repository.node_exists("document:test") is True
    query, parameters = transaction.calls[0]
    assert "$node_id" in query
    assert parameters == {"node_id": "document:test"}


def test_node_exists_rejects_blank_identifier() -> None:
    repository, _, _ = _repository([])

    with pytest.raises(ValueError, match="node_id"):
        repository.node_exists("   ")


def test_get_node_rehydrates_typed_domain_model() -> None:
    repository, _, _ = _repository(
        [
            {
                "properties": {
                    "node_id": "concept:gastos-fixos",
                    "node_type": "financial_concept",
                    "label": "Gastos fixos",
                    "concept_key": "gastos-fixos",
                    "description": "Despesas recorrentes.",
                    "aliases": ["despesas fixas"],
                    "metadata_json": '{"language":"pt-BR"}',
                }
            }
        ]
    )

    node = repository.get_node("concept:gastos-fixos")

    assert isinstance(node, FinancialConceptNode)
    assert node.concept_key == "gastos-fixos"
    assert node.aliases == ("despesas fixas",)
    assert node.metadata == {"language": "pt-BR"}


def test_get_node_returns_none_when_absent() -> None:
    repository, _, _ = _repository([None])

    assert repository.get_node("document:missing") is None


def test_get_node_rejects_corrupt_persisted_type() -> None:
    repository, _, _ = _repository(
        [
            {
                "properties": {
                    "node_id": "broken:1",
                    "node_type": "unsupported",
                    "label": "Broken",
                    "metadata_json": "{}",
                }
            }
        ]
    )

    with pytest.raises(KnowledgeGraphPersistenceError):
        repository.get_node("broken:1")


def test_upsert_relationship_validates_domain_and_uses_parameterized_values() -> None:
    relationship = KnowledgeGraphRelationship(
        source_id="document:inna-edu-orcamento-002",
        target_id="concept:gastos-fixos",
        relationship_type=KnowledgeRelationshipType.EXPLAINS,
        properties={"confidence": 0.95, "evidence": {"source": "test"}},
    )
    repository, transaction, _ = _repository(
        [
            {"source_type": "document", "target_type": "financial_concept"},
            {"relationship_type": "EXPLAINS"},
        ]
    )

    repository.upsert_relationship(relationship)

    assert len(transaction.calls) == 2
    merge_query, parameters = transaction.calls[1]
    assert "MERGE (source)-[r:EXPLAINS]->(target)" in merge_query
    assert relationship.source_id not in merge_query
    assert relationship.target_id not in merge_query
    assert parameters["source_id"] == relationship.source_id
    assert parameters["target_id"] == relationship.target_id
    assert parameters["properties_json"] == (
        '{"confidence":0.95,"evidence":{"source":"test"}}'
    )


def test_upsert_relationship_rejects_missing_endpoint() -> None:
    relationship = KnowledgeGraphRelationship(
        source_id="document:test",
        target_id="concept:missing",
        relationship_type=KnowledgeRelationshipType.EXPLAINS,
    )
    repository, _, _ = _repository([None])

    with pytest.raises(KnowledgeGraphPersistenceError, match="inexistente"):
        repository.upsert_relationship(relationship)


def test_upsert_relationship_rejects_invalid_domain_direction() -> None:
    relationship = KnowledgeGraphRelationship(
        source_id="concept:test",
        target_id="document:test",
        relationship_type=KnowledgeRelationshipType.EXPLAINS,
    )
    repository, transaction, _ = _repository(
        [{"source_type": "financial_concept", "target_type": "document"}]
    )

    with pytest.raises(KnowledgeGraphPersistenceError, match="permitido pelo schema"):
        repository.upsert_relationship(relationship)

    assert len(transaction.calls) == 1
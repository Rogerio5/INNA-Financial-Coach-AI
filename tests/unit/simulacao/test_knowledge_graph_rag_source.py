from __future__ import annotations

import json

from src.knowledge_graph.rag_source import RagKnowledgeSource


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows
        self.query = ""

    def execute(self, query):
        self.query = query

    def fetchall(self):
        return list(self._rows)

    def close(self):
        return None


class FakeConnection:
    def __init__(self, rows):
        self.cursor_instance = FakeCursor(rows)
        self.readonly = None
        self.autocommit = None
        self.rollback_count = 0
        self.closed = False

    def rollback(self):
        self.rollback_count += 1

    def set_session(self, *, readonly, autocommit):
        self.readonly = readonly
        self.autocommit = autocommit

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True


def test_source_loads_only_returned_canonical_rows() -> None:
    rows = [
        (
            28,
            "inna-edu-orcamento-002",
            "orcamento.md",
            "orcamento.md",
            "seed",
            "chunk-1",
            1,
            "texto 1",
            {"language": "pt-BR"},
        ),
        (
            28,
            "inna-edu-orcamento-002",
            "orcamento.md",
            "orcamento.md",
            "seed",
            "chunk-2",
            2,
            "texto 2",
            json.dumps({"topic": "orcamento"}),
        ),
    ]

    connection = FakeConnection(rows)
    source = RagKnowledgeSource(
        connection_factory=lambda: connection
    )

    snapshot = source.load_canonical_snapshot()

    assert len(snapshot.documents) == 1
    assert len(snapshot.chunks) == 2
    assert snapshot.documents[0].document_key == (
        "inna-edu-orcamento-002"
    )
    assert snapshot.chunks[1].metadata == {
        "topic": "orcamento"
    }


def test_source_enforces_read_only_session() -> None:
    connection = FakeConnection([])

    RagKnowledgeSource(
        connection_factory=lambda: connection
    ).load_canonical_snapshot()

    assert connection.readonly is True
    assert connection.autocommit is False
    assert connection.rollback_count >= 2
    assert connection.closed is True


def test_source_query_excludes_unkeyed_and_inactive_documents() -> None:
    connection = FakeConnection([])

    RagKnowledgeSource(
        connection_factory=lambda: connection
    ).load_canonical_snapshot()

    query = connection.cursor_instance.query

    assert "COALESCE(d.ativo, TRUE)" in query
    assert "d.nome_logico IS NOT NULL" in query
    assert "BTRIM(d.nome_logico) <> ''" in query
    assert "c.chunk_id IS NOT NULL" in query


def test_source_rejects_conflicting_document_keys() -> None:
    rows = [
        (
            28,
            "key-a",
            None,
            None,
            None,
            "chunk-1",
            1,
            "texto",
            {},
        ),
        (
            28,
            "key-b",
            None,
            None,
            None,
            "chunk-2",
            2,
            "texto",
            {},
        ),
    ]

    source = RagKnowledgeSource(
        connection_factory=lambda: FakeConnection(rows)
    )

    try:
        source.load_canonical_snapshot()
    except ValueError as exc:
        assert "chaves diferentes" in str(exc)
    else:
        raise AssertionError(
            "Conflito de document_key deveria falhar."
        )

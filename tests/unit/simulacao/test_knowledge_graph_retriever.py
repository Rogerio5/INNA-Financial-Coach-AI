from __future__ import annotations

from typing import Any

from src.knowledge_graph.retriever import (
    GraphKnowledgeRetriever,
    _normalize_fulltext_search,
)


class FakeNeo4jResult:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = rows

    def data(self) -> list[dict[str, Any]]:
        return list(
            self._rows
        )


class FakeNeo4jSession:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = rows
        self.parameters: dict[
            str,
            Any,
        ] = {}

    def __enter__(
        self,
    ) -> FakeNeo4jSession:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None

    def run(
        self,
        cypher: str,
        **parameters: Any,
    ) -> FakeNeo4jResult:
        self.parameters = dict(
            parameters
        )

        assert "DELETE" not in cypher.upper()

        return FakeNeo4jResult(
            self._rows
        )


class FakeNeo4jDriver:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self.session_instance = (
            FakeNeo4jSession(
                rows
            )
        )

    def session(
        self,
        *,
        database: str,
    ) -> FakeNeo4jSession:
        assert database == "neo4j"
        return self.session_instance


class FakeNeo4jClient:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self.driver = FakeNeo4jDriver(
            rows
        )

    def connect(
        self,
    ) -> FakeNeo4jDriver:
        return self.driver

    def close(self) -> None:
        return None


class FakePostgresCursor:
    def __init__(
        self,
        rows: list[tuple[Any, ...]],
    ) -> None:
        self._rows = rows
        self.parameters: tuple[
            Any,
            ...,
        ] | None = None

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...],
    ) -> None:
        assert "DELETE" not in query.upper()
        self.parameters = parameters

    def fetchall(
        self,
    ) -> list[tuple[Any, ...]]:
        return list(
            self._rows
        )

    def close(self) -> None:
        return None


class FakePostgresConnection:
    def __init__(
        self,
        rows: list[tuple[Any, ...]],
    ) -> None:
        self.cursor_instance = (
            FakePostgresCursor(
                rows
            )
        )
        self.readonly = False
        self.closed = False
        self.rollback_count = 0

    def rollback(self) -> None:
        self.rollback_count += 1

    def set_session(
        self,
        *,
        readonly: bool,
        autocommit: bool,
    ) -> None:
        self.readonly = readonly
        assert autocommit is False

    def cursor(
        self,
    ) -> FakePostgresCursor:
        return self.cursor_instance

    def close(self) -> None:
        self.closed = True


def _graph_rows() -> list[
    dict[str, Any]
]:
    return [
        {
            "concept_node_id": (
                "concept:orcamento_pessoal"
            ),
            "concept_key": (
                "orcamento_pessoal"
            ),
            "graph_score": 1.2,
            "document_key": (
                "inna-edu-orcamento-002"
            ),
            "chunk_id": "chunk-1",
            "chunk_index": 1,
        },
        {
            "concept_node_id": (
                "concept:orcamento_pessoal"
            ),
            "concept_key": (
                "orcamento_pessoal"
            ),
            "graph_score": 1.2,
            "document_key": (
                "inna-edu-orcamento-002"
            ),
            "chunk_id": "chunk-2",
            "chunk_index": 2,
        },
    ]


def _postgres_rows() -> list[
    tuple[Any, ...]
]:
    return [
        (
            28,
            "chunk-1",
            "inna-edu-orcamento-002",
            1,
            "texto 1",
            {
                "topic": (
                    "orcamento_pessoal"
                )
            },
        ),
        (
            28,
            "chunk-2",
            "inna-edu-orcamento-002",
            2,
            "texto 2",
            {},
        ),
    ]


def _retriever(
    graph_rows: list[
        dict[str, Any]
    ] | None = None,
    postgres_rows: list[
        tuple[Any, ...]
    ] | None = None,
) -> tuple[
    GraphKnowledgeRetriever,
    FakeNeo4jClient,
    FakePostgresConnection,
]:
    neo4j_client = FakeNeo4jClient(
        graph_rows
        if graph_rows is not None
        else _graph_rows()
    )

    postgres = FakePostgresConnection(
        postgres_rows
        if postgres_rows is not None
        else _postgres_rows()
    )

    retriever = GraphKnowledgeRetriever(
        neo4j_client,  # type: ignore[arg-type]
        database="neo4j",
        postgres_connection_factory=(
            lambda: postgres
        ),
    )

    return (
        retriever,
        neo4j_client,
        postgres,
    )


def test_normalize_fulltext_search_removes_lucene_punctuation() -> None:
    assert (
        _normalize_fulltext_search(
            ' or\u00e7amento +(pix): "seguro" '
        )
        == "or\u00e7amento pix seguro"
    )


def test_search_hydrates_graph_chunks_from_postgres() -> None:
    (
        retriever,
        _neo4j,
        postgres,
    ) = _retriever()

    results = retriever.search(
        "orcamento",
        concept_limit=3,
        chunk_limit=8,
    )

    assert len(results) == 2
    assert results[0].chunk_id == "chunk-1"
    assert results[0].text == "texto 1"
    assert results[0].concept_key == (
        "orcamento_pessoal"
    )
    assert results[0].graph_score == 1.2
    assert postgres.readonly is True
    assert postgres.closed is True
    assert postgres.rollback_count >= 2


def test_search_uses_safe_named_parameters() -> None:
    (
        retriever,
        neo4j,
        _postgres,
    ) = _retriever()

    retriever.search(
        "orcamento",
        concept_limit=2,
    )

    parameters = (
        neo4j.driver.session_instance.parameters
    )

    assert parameters[
        "search_text"
    ] == "orcamento"
    assert parameters[
        "concept_limit"
    ] == 2
    assert "query" not in parameters


def test_retrieve_by_concept_uses_exact_key() -> None:
    (
        retriever,
        neo4j,
        _postgres,
    ) = _retriever()

    results = (
        retriever.retrieve_by_concept(
            "orcamento_pessoal"
        )
    )

    assert len(results) == 2

    parameters = (
        neo4j.driver.session_instance.parameters
    )

    assert parameters[
        "concept_key"
    ] == "orcamento_pessoal"


def test_search_deduplicates_chunk_ids_before_hydration() -> None:
    duplicated = (
        _graph_rows()
        + [_graph_rows()[0]]
    )

    (
        retriever,
        _neo4j,
        postgres,
    ) = _retriever(
        graph_rows=duplicated
    )

    results = retriever.search(
        "orcamento"
    )

    assert len(results) == 2

    parameters = (
        postgres.cursor_instance.parameters
    )

    assert parameters is not None
    requested_ids = parameters[0]

    assert requested_ids == [
        "chunk-1",
        "chunk-2",
    ]


def test_search_respects_chunk_limit() -> None:
    (
        retriever,
        _neo4j,
        _postgres,
    ) = _retriever()

    results = retriever.search(
        "orcamento",
        chunk_limit=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == (
        "chunk-1"
    )


def test_empty_search_does_not_open_connections() -> None:
    (
        retriever,
        neo4j,
        postgres,
    ) = _retriever()

    assert retriever.search(
        "   !!!   "
    ) == []

    assert (
        neo4j.driver.session_instance.parameters
        == {}
    )
    assert postgres.closed is False


def test_graph_postgres_document_mismatch_fails() -> None:
    bad_postgres_rows = [
        (
            28,
            "chunk-1",
            "outra-chave",
            1,
            "texto",
            {},
        ),
        (
            28,
            "chunk-2",
            "inna-edu-orcamento-002",
            2,
            "texto",
            {},
        ),
    ]

    (
        retriever,
        _neo4j,
        _postgres,
    ) = _retriever(
        postgres_rows=bad_postgres_rows
    )

    try:
        retriever.search(
            "orcamento"
        )
    except RuntimeError as exc:
        assert "document_key" in str(
            exc
        )
    else:
        raise AssertionError(
            "DivergÃªncia Graph/Postgres deveria falhar."
        )

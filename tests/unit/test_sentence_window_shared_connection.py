from __future__ import annotations

import sys
from types import ModuleType

from src import rag_engine


class FakeConnection:
    def __init__(self):
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def test_sentence_window_reuses_one_connection(
    monkeypatch,
):
    connection = FakeConnection()

    connection_calls = {
        "count": 0,
    }

    loader_connections = []

    def fake_get_connection():
        connection_calls["count"] += 1
        return connection

    def fake_loader(
        item,
        *,
        idioma,
        chunk_radius,
        connection=None,
    ):
        loader_connections.append(connection)
        return [dict(item)]

    fake_module = ModuleType(
        "services.rag.sentence_window"
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
        expanded[
            "sentence_window_applied"
        ] = True
        return expanded

    fake_module.expand_result_with_sentence_window = (
        fake_expand
    )

    monkeypatch.setitem(
        sys.modules,
        "services.rag.sentence_window",
        fake_module,
    )

    monkeypatch.setitem(
        sys.modules,
        "src.services.rag.sentence_window",
        fake_module,
    )

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        fake_get_connection,
    )

    monkeypatch.setattr(
        rag_engine,
        "_load_sentence_window_neighbor_chunks",
        fake_loader,
    )

    monkeypatch.setattr(
        rag_engine,
        "_sentence_window_allowed_document_keys",
        lambda: {"inna-edu-orcamento-002"},
    )

    results = [
        {
            "id": 66,
            "documento_id": 28,
            "documento_key": (
                "inna-edu-orcamento-002"
            ),
            "chunk_id": "orcamento-001",
            "chunk_index": 1,
            "chunk_text": "Renda e gastos.",
        },
        {
            "id": 67,
            "documento_id": 28,
            "documento_key": (
                "inna-edu-orcamento-002"
            ),
            "chunk_id": "orcamento-002",
            "chunk_index": 2,
            "chunk_text": "Planejamento mensal.",
        },
    ]

    expanded = (
        rag_engine
        ._apply_sentence_window_to_results(
            query="Como organizar meu orçamento?",
            idioma="pt",
            results=results,
            window_size=5,
            chunk_radius=1,
            max_characters=4000,
        )
    )

    assert len(expanded) == 2

    assert connection_calls["count"] == 1

    assert loader_connections == [
        connection,
        connection,
    ]

    assert connection.close_calls == 1

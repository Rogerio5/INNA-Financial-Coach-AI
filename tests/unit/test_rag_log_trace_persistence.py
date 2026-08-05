from __future__ import annotations

import json

from src import rag_engine


class FakeCursor:
    def __init__(self):
        self.executions = []
        self.closed = False

    def execute(
        self,
        query,
        params=None,
    ):
        self.executions.append(
            (
                str(query),
                params,
            )
        )

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def _find_insert_execution(
    connection: FakeConnection,
):
    return next(
        execution
        for execution in connection.cursor_instance.executions
        if ("INSERT INTO inna_rag_logs" in execution[0])
    )


def test_persists_trace_id_and_trace_json(
    monkeypatch,
):
    connection = FakeConnection()

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        lambda: connection,
    )

    trace = {
        "trace_id": "trace-test-123",
        "query": "reserva",
        "search_mode": "rag_hibrido",
        "results_total": 1,
        "results": [
            {
                "chunk_id": 10,
                "position": 1,
            }
        ],
    }

    rag_engine.save_rag_log(
        pergunta="Como criar reserva?",
        resultado={
            "resposta": ("Comece organizando seu orçamento."),
            "fontes": [
                {
                    "titulo": "Reserva",
                }
            ],
            "modo": "rag_hibrido",
            "trace_id": ("trace-test-123"),
            "retrieval_trace": trace,
        },
        tempo_resposta_ms=42,
    )

    assert connection.committed
    assert connection.closed
    assert connection.cursor_instance.closed

    query, params = _find_insert_execution(connection)

    assert "trace_id" in query
    assert "retrieval_trace" in query

    assert params[8] == ("trace-test-123")

    saved_trace = json.loads(params[9])

    assert saved_trace == trace


def test_accepts_result_without_trace(
    monkeypatch,
):
    connection = FakeConnection()

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        lambda: connection,
    )

    rag_engine.save_rag_log(
        pergunta="Pergunta antiga",
        resultado={
            "resposta": "Resposta antiga",
            "fontes": [],
            "modo": "rag_local_sem_custo",
        },
        tempo_resposta_ms=10,
    )

    _, params = _find_insert_execution(connection)

    assert params[8] is None
    assert params[9] is None
    assert connection.committed


def test_prepares_trace_columns_idempotently(
    monkeypatch,
):
    connection = FakeConnection()

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        lambda: connection,
    )

    rag_engine.save_rag_log(
        pergunta="teste",
        resultado={
            "resposta": "teste",
            "modo": "rag",
        },
    )

    queries = "\n".join(query for query, _ in connection.cursor_instance.executions)

    assert "CREATE TABLE IF NOT EXISTS" in queries

    assert "ADD COLUMN IF NOT EXISTS" in queries

    assert "idx_inna_rag_logs_trace_id" in queries


def test_log_failure_does_not_escape(
    monkeypatch,
):
    class BrokenConnection:
        def cursor(self):
            raise RuntimeError("database unavailable")

        def rollback(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        lambda: BrokenConnection(),
    )

    result = rag_engine.save_rag_log(
        pergunta="teste",
        resultado={
            "resposta": "teste",
            "modo": "rag",
        },
    )

    assert result is None


def test_rolls_back_when_insert_fails(
    monkeypatch,
):
    class BrokenCursor(FakeCursor):
        def execute(
            self,
            query,
            params=None,
        ):
            if "INSERT INTO inna_rag_logs" in str(query):
                raise RuntimeError("insert failed")

            super().execute(
                query,
                params,
            )

    connection = FakeConnection()
    connection.cursor_instance = BrokenCursor()

    monkeypatch.setattr(
        rag_engine,
        "get_rag_connection",
        lambda: connection,
    )

    rag_engine.save_rag_log(
        pergunta="teste",
        resultado={
            "resposta": "teste",
            "modo": "rag",
        },
    )

    assert connection.rolled_back
    assert connection.closed
    assert connection.cursor_instance.closed

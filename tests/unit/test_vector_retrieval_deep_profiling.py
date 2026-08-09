from __future__ import annotations

from contextlib import contextmanager

from src.services.rag import retrieval


class FakeCursor:
    def __init__(self):
        self.sql = None
        self.params = None

    def execute(self, sql, params):
        self.sql = sql
        self.params = params

    def fetchall(self):
        return [
            {
                "id": 66,
                "documento_id": 28,
                "chunk_id": "orcamento-001",
                "documento_origem": (
                    "educadora_financeira/"
                    "01_orcamento_fluxo_caixa.md"
                ),
                "chunk_index": 1,
                "texto": (
                    "Planeje renda e gastos."
                ),
                "documento_key": (
                    "inna-edu-orcamento-002"
                ),
                "titulo": "Orçamento",
                "fonte": (
                    "01_orcamento_fluxo_caixa.md"
                ),
                "categoria_documento": (
                    "orcamento"
                ),
                "idioma": "pt-BR",
                "metadata": {},
                "modelo_embedding": (
                    "models/gemini-embedding-001"
                ),
                "distancia": 0.1,
            }
        ]


@contextmanager
def fake_cursor_postgres(
    *,
    dict_cursor=False,
    commit_automatico=False,
):
    yield FakeCursor()


def test_semantic_retrieval_exposes_deep_timings(
    monkeypatch,
):
    monkeypatch.setattr(
        retrieval,
        "cursor_postgres",
        fake_cursor_postgres,
    )

    profiling: dict[str, float] = {}

    result = retrieval.buscar_chunks_semanticos(
        "Como organizar meu orçamento?",
        limite=2,
        gerar_embedding=lambda _: [0.0] * 3072,
        classificar_chunk=lambda _: "",
        dimensoes=3072,
        profiling=profiling,
    )

    assert result["ok"] is True
    assert result["resultados"]

    expected = {
        "query_embedding_ms",
        "vector_conversion_ms",
        "vector_database_ms",
        "vector_postprocess_ms",
        "vector_semantic_total_ms",
    }

    assert expected.issubset(
        set(profiling)
    )

    for key in expected:
        assert profiling[key] >= 0

    measured = (
        profiling["query_embedding_ms"]
        + profiling["vector_conversion_ms"]
        + profiling["vector_database_ms"]
        + profiling["vector_postprocess_ms"]
    )

    assert (
        profiling["vector_semantic_total_ms"]
        >= measured - 5
    )

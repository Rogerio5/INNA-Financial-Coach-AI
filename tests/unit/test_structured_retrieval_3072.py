from contextlib import contextmanager

from src.services.rag import retrieval


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.sql = ""
        self.params = ()

    def execute(self, sql, params):
        self.sql = sql
        self.params = params

    def fetchall(self):
        return self.rows


def _fake_cursor_factory(rows, holder):
    @contextmanager
    def fake_cursor_postgres(
        *,
        dict_cursor=False,
        commit_automatico=False,
    ):
        cursor = FakeCursor(rows)
        holder["cursor"] = cursor
        yield cursor

    return fake_cursor_postgres


def test_semantic_3072_preserves_document_identity(
    monkeypatch,
):
    holder = {}

    rows = [
        {
            "id": 66,
            "documento_id": 28,
            "chunk_id": "orcamento-001",
            "documento_origem": (
                "educadora_financeira/"
                "01_orcamento_fluxo_caixa.md"
            ),
            "chunk_index": 1,
            "texto": "Planeje renda e gastos.",
            "documento_key": (
                "inna-edu-orcamento-002"
            ),
            "titulo": "Orçamento",
            "fonte": (
                "educadora_financeira/"
                "01_orcamento_fluxo_caixa.md"
            ),
            "categoria_documento": (
                "educacao_financeira"
            ),
            "idioma": "pt-BR",
            "metadata": {},
            "modelo_embedding": (
                "models/gemini-embedding-001"
            ),
            "distancia": 0.12,
        }
    ]

    monkeypatch.setattr(
        retrieval,
        "cursor_postgres",
        _fake_cursor_factory(
            rows,
            holder,
        ),
    )

    resultado = retrieval.buscar_chunks_semanticos(
        "Como organizar meu orçamento?",
        limite=2,
        gerar_embedding=lambda _: [0.0] * 3072,
        classificar_chunk=lambda _: "",
        dimensoes=3072,
    )

    assert resultado["ok"] is True
    assert len(resultado["resultados"]) == 1

    item = resultado["resultados"][0]

    assert item["documento_id"] == 28
    assert item["documento_key"] == (
        "inna-edu-orcamento-002"
    )
    assert item["chunk_text"] == (
        "Planeje renda e gastos."
    )
    assert item["modo_busca"] == (
        "rag_estruturado_3072_vetorial"
    )
    assert isinstance(
        item["score"],
        float,
    )

    sql = holder["cursor"].sql

    assert "du.nome_logico AS documento_key" in sql
    assert "chunks_embeddings_rag" in sql
    assert "documentos_upload_rag" in sql
    assert "halfvec(3072)" in sql


def test_textual_3072_preserves_document_identity(
    monkeypatch,
):
    holder = {}

    rows = [
        {
            "id": 67,
            "documento_id": 28,
            "chunk_id": "orcamento-002",
            "documento_origem": (
                "educadora_financeira/"
                "01_orcamento_fluxo_caixa.md"
            ),
            "chunk_index": 2,
            "texto": (
                "Compare renda e despesas."
            ),
            "documento_key": (
                "inna-edu-orcamento-002"
            ),
            "titulo": "Orçamento",
            "fonte": (
                "educadora_financeira/"
                "01_orcamento_fluxo_caixa.md"
            ),
            "categoria_documento": (
                "educacao_financeira"
            ),
            "idioma": "pt-BR",
            "metadata": {},
            "modelo_embedding": (
                "models/gemini-embedding-001"
            ),
            "score_textual": 2.0,
        }
    ]

    monkeypatch.setattr(
        retrieval,
        "cursor_postgres",
        _fake_cursor_factory(
            rows,
            holder,
        ),
    )

    resultado = retrieval.buscar_chunks_textuais(
        "organizar orçamento renda",
        limite=2,
        classificar_chunk=lambda _: "",
    )

    assert resultado["ok"] is True
    assert len(resultado["resultados"]) == 1

    item = resultado["resultados"][0]

    assert item["documento_id"] == 28
    assert item["documento_key"] == (
        "inna-edu-orcamento-002"
    )
    assert item["chunk_text"] == (
        "Compare renda e despesas."
    )
    assert item["score"] == 2.0
    assert item["modo_busca"] == (
        "rag_estruturado_3072_textual"
    )

    sql = holder["cursor"].sql

    assert "du.nome_logico AS documento_key" in sql
    assert "chunks_embeddings_rag" in sql
    assert "score_textual" in sql


def test_textual_terms_are_deduplicated():
    termos = (
        retrieval._extrair_termos_busca_textual(
            "Como organizar organizar "
            "meu orçamento e renda?"
        )
    )

    assert termos.count(
        "organizar"
    ) == 1
    assert "orçamento" in termos
    assert "renda" in termos

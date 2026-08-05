from __future__ import annotations

from pathlib import Path


REPOSITORY_PATH = Path("src/services/rag/document_repository.py")


def _source() -> str:
    return REPOSITORY_PATH.read_text(
        encoding="utf-8-sig",
    )


def test_schema_contains_versioning_columns():
    source = _source()

    for column in (
        "nome_logico",
        "content_hash",
        "versao",
        "documento_raiz_id",
        "documento_anterior_id",
    ):
        assert column in source


def test_schema_uses_compatible_add_column():
    source = _source()

    assert "ADD COLUMN IF NOT EXISTS" in source


def test_schema_creates_unique_hash_index():
    source = _source()

    assert "uq_documentos_upload_rag_hash" in source

    assert "WHERE content_hash IS NOT NULL" in source


def test_schema_creates_unique_name_version_index():
    source = _source()

    assert "uq_documentos_upload_rag_nome_versao" in source


def test_registration_accepts_version_metadata():
    source = _source()

    start = source.index("def registrar_documento")

    end = source.index(
        "def listar_documentos",
        start,
    )

    section = source[start:end]

    for field in (
        "nome_logico",
        "content_hash",
        "versao",
        "documento_raiz_id",
        "documento_anterior_id",
    ):
        assert field in section


def test_registration_keeps_legacy_parameters():
    source = _source()

    start = source.index("def registrar_documento")

    signature = source[start : start + 900]

    for field in (
        "nome_original",
        "nome_salvo",
        "caminho_upload",
        "caminho_chunks",
        "caminho_embedding_ready",
        "extensao",
        "tamanho_bytes",
        "total_chunks",
    ):
        assert field in signature


def test_lookup_returns_version_metadata():
    source = _source()

    start = source.index("def buscar_documento_por_id")

    section = source[start : start + 3500]

    for field in (
        '"nome_logico"',
        '"content_hash"',
        '"versao"',
        '"documento_raiz_id"',
        '"documento_anterior_id"',
    ):
        assert field in section


def test_listing_exposes_version_metadata():
    source = _source()

    start = source.index("def listar_documentos")

    end = source.index(
        "def buscar_documento_por_id",
        start,
    )

    section = source[start:end]

    assert "COALESCE(versao, 1) AS versao" in section

    assert "content_hash" in section
    assert "nome_logico" in section

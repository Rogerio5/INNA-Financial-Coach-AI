from __future__ import annotations

from pathlib import Path

from src.evaluation.financial_neon_schema_adapter import (
    build_neon_chunk_payloads,
    build_neon_document_payloads,
    create_adapter_report,
    load_json_list,
    normalize_extension,
    parse_integer_version,
    validate_chunk_payload,
    validate_document_payload,
)

DOCUMENTS_PATH = Path(
    "artifacts/evaluation/retrieval_quality/"
    "phase_5a_ingestion_dry_run/"
    "financial_documents_dry_run.json"
)

CHUNKS_PATH = Path(
    "artifacts/evaluation/retrieval_quality/"
    "phase_5a_ingestion_dry_run/"
    "financial_chunks_dry_run.json"
)


def test_parse_integer_version() -> None:
    assert parse_integer_version("2.0.0") == 2

    assert parse_integer_version("version-3") == 3

    assert parse_integer_version("") == 1


def test_normalize_extension() -> None:
    assert normalize_extension("md") == ".md"

    assert normalize_extension(".PDF") == ".pdf"

    assert normalize_extension("") == ".md"


def test_builds_sixteen_neon_documents() -> None:
    documents = load_json_list(DOCUMENTS_PATH)

    payloads = build_neon_document_payloads(documents)

    assert len(payloads) == 16
    assert all(payload.nome_original for payload in payloads)
    assert all(payload.nome_salvo for payload in payloads)
    assert all(payload.nome_logico for payload in payloads)
    assert all(payload.total_chunks > 0 for payload in payloads)


def test_document_payloads_match_real_schema() -> None:
    documents = load_json_list(DOCUMENTS_PATH)

    payloads = build_neon_document_payloads(documents)

    for payload in payloads:
        assert validate_document_payload(payload) == ()

        data = payload.as_dict()

        assert "nome_original" in data
        assert "nome_salvo" in data
        assert "extensao" in data
        assert "total_chunks" in data
        assert "status" in data
        assert "origem" in data
        assert "ativo" in data
        assert "nome_logico" in data
        assert "content_hash" in data
        assert "versao" in data
        assert "document_key" not in data
        assert "categoria" not in data
        assert "idioma" not in data


def test_builds_thirty_five_neon_chunks() -> None:
    chunks = load_json_list(CHUNKS_PATH)

    payloads = build_neon_chunk_payloads(chunks)

    assert len(payloads) == 35

    for payload in payloads:
        assert validate_chunk_payload(payload) == ()

        assert payload.documento_key
        assert payload.chunk_id
        assert payload.chunk_index > 0
        assert payload.texto
        assert payload.embedding is None
        assert payload.modelo_embedding == "models/gemini-embedding-001"


def test_chunk_metadata_preserves_context() -> None:
    chunks = load_json_list(CHUNKS_PATH)

    payloads = build_neon_chunk_payloads(chunks)

    for payload in payloads:
        metadata = payload.metadata

        assert metadata["schema_adapter_version"] == 1

        assert metadata["documento_key"] == payload.documento_key

        assert metadata["embedding_status"] == "pending"

        assert metadata["ingestion_status"] == "offline_adapted"

        assert metadata["database_document_id"] is None

        assert metadata["area"]
        assert metadata["topic"]
        assert metadata["language"]


def test_complete_adapter_report_passes() -> None:
    documents = load_json_list(DOCUMENTS_PATH)

    chunks = load_json_list(CHUNKS_PATH)

    adapted_documents = build_neon_document_payloads(documents)

    adapted_chunks = build_neon_chunk_payloads(chunks)

    report = create_adapter_report(
        source_documents=documents,
        source_chunks=chunks,
        adapted_documents=adapted_documents,
        adapted_chunks=adapted_chunks,
    )

    assert report.source_document_count == 16
    assert report.source_chunk_count == 35
    assert report.adapted_document_count == 16
    assert report.adapted_chunk_count == 35
    assert report.duplicate_document_key_count == 0
    assert report.duplicate_chunk_id_count == 0
    assert report.invalid_document_count == 0
    assert report.invalid_chunk_count == 0
    assert report.status == "passed"
    assert report.database_connected is False
    assert report.database_write_executed is False
    assert report.neon_changed is False
    assert report.gemini_used is False

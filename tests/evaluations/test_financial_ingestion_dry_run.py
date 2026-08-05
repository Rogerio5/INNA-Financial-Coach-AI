from __future__ import annotations

from pathlib import Path

from src.evaluation.financial_ingestion_dry_run import (
    build_chunk_payloads,
    build_document_payloads,
    create_dry_run_report,
    load_source_chunks,
    validate_chunk_payload,
    validate_document_payload,
)

CHUNKS_PATH = Path(
    "artifacts/evaluation/retrieval_quality/"
    "phase_5a_chunking_tuned/"
    "financial_knowledge_tuned_chunks.json"
)


def test_loads_thirty_five_chunks() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    assert len(chunks) == 35


def test_builds_sixteen_documents() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    documents = build_document_payloads(chunks)

    assert len(documents) == 16
    assert all(document.total_chunks > 0 for document in documents)


def test_maps_thirty_five_chunks() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    payloads = build_chunk_payloads(chunks)

    assert len(payloads) == 35
    assert all(payload.embedding is None for payload in payloads)
    assert all(payload.modelo_embedding is None for payload in payloads)


def test_chunk_payloads_are_valid() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    payloads = build_chunk_payloads(chunks)

    assert all(validate_chunk_payload(payload) == () for payload in payloads)


def test_document_payloads_are_valid() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    payloads = build_document_payloads(chunks)

    assert all(validate_document_payload(payload) == () for payload in payloads)


def test_complete_dry_run_passes() -> None:
    chunks = load_source_chunks(CHUNKS_PATH)

    documents = build_document_payloads(chunks)

    chunk_payloads = build_chunk_payloads(chunks)

    report = create_dry_run_report(
        chunks,
        documents,
        chunk_payloads,
    )

    assert report.source_chunk_count == 35
    assert report.mapped_chunk_count == 35
    assert report.mapped_document_count == 16
    assert report.duplicate_chunk_id_count == 0
    assert report.duplicate_chunk_hash_count == 0
    assert report.duplicate_document_key_count == 0
    assert report.invalid_chunk_count == 0
    assert report.invalid_document_count == 0
    assert report.status == "passed"
    assert report.database_connected is False
    assert report.database_write_executed is False
    assert report.neon_changed is False
    assert report.gemini_used is False

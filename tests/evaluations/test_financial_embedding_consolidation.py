from __future__ import annotations

import pytest

from src.evaluation.financial_embedding_consolidation import (
    build_consolidation_report,
    consolidate_embeddings,
    validate_vector,
)


def sample_chunks() -> list[dict[str, object]]:
    return [
        {
            "chunk_id": f"chunk-{index:03d}",
            "documento_key": f"document-{index:03d}",
            "documento_origem": f"document-{index:03d}.md",
            "chunk_index": 1,
            "texto": f"Texto financeiro {index}",
            "metadata": {
                "area": "financeiro",
            },
        }
        for index in range(1, 36)
    ]


def sample_vector() -> tuple[float, ...]:
    return tuple(0.001 for _ in range(3072))


def test_validates_vector_dimension() -> None:
    vector = validate_vector(
        chunk_id="chunk-001",
        vector=sample_vector(),
    )

    assert len(vector) == 3072


def test_rejects_wrong_dimension() -> None:
    with pytest.raises(
        ValueError,
        match="Dimensao invalida",
    ):
        validate_vector(
            chunk_id="chunk-001",
            vector=[0.1, 0.2],
        )


def test_consolidates_thirty_five_embeddings() -> None:
    chunks = sample_chunks()

    batch = {f"chunk-{index:03d}": sample_vector() for index in range(2, 36)}

    consolidated = consolidate_embeddings(
        chunks=chunks,
        pilot_chunk_id="chunk-001",
        pilot_vector=sample_vector(),
        batch_embeddings=batch,
    )

    assert len(consolidated) == 35
    assert all(len(item.embedding) == 3072 for item in consolidated)


def test_pilot_is_not_duplicated() -> None:
    chunks = sample_chunks()

    batch = {f"chunk-{index:03d}": sample_vector() for index in range(1, 35)}

    with pytest.raises(
        ValueError,
        match="repetido",
    ):
        consolidate_embeddings(
            chunks=chunks,
            pilot_chunk_id="chunk-001",
            pilot_vector=sample_vector(),
            batch_embeddings=batch,
        )


def test_report_passes() -> None:
    chunks = sample_chunks()

    batch = {f"chunk-{index:03d}": sample_vector() for index in range(2, 36)}

    consolidated = consolidate_embeddings(
        chunks=chunks,
        pilot_chunk_id="chunk-001",
        pilot_vector=sample_vector(),
        batch_embeddings=batch,
    )

    report = build_consolidation_report(consolidated)

    assert report["consolidated_chunk_count"] == 35
    assert report["unique_chunk_id_count"] == 35
    assert report["valid_embedding_count"] == 35
    assert report["invalid_embedding_count"] == 0
    assert report["embedding_dimension"] == 3072
    assert report["consolidation_status"] == "passed"
    assert report["gemini_call_count"] == 0
    assert report["database_connected"] is False
    assert report["neon_changed"] is False
    assert report["gemini_used"] is False

from __future__ import annotations

from src.evaluation.financial_embedding_batch_plan import (
    CompletedEmbedding,
    build_batch_plan_report,
    build_pending_embeddings,
)


def sample_chunks() -> list[dict[str, object]]:
    return [
        {
            "chunk_id": f"chunk-{index:03d}",
            "documento_key": f"document-{index:03d}",
            "chunk_index": 1,
            "texto": f"Texto financeiro {index}",
            "metadata": {
                "document_title": f"Documento {index}",
            },
        }
        for index in range(1, 36)
    ]


def completed_embedding() -> CompletedEmbedding:
    return CompletedEmbedding(
        chunk_id="chunk-001",
        documento_key="document-001",
        model="gemini-embedding-001",
        task_type="RETRIEVAL_DOCUMENT",
        dimension=3072,
        vector=tuple(0.001 for _ in range(3072)),
    )


def test_builds_exactly_thirty_four_pending() -> None:
    pending = build_pending_embeddings(
        sample_chunks(),
        completed_embedding(),
    )

    assert len(pending) == 34


def test_pilot_chunk_is_not_pending() -> None:
    pending = build_pending_embeddings(
        sample_chunks(),
        completed_embedding(),
    )

    pending_ids = {item.chunk_id for item in pending}

    assert "chunk-001" not in pending_ids


def test_pending_sequence_is_contiguous() -> None:
    pending = build_pending_embeddings(
        sample_chunks(),
        completed_embedding(),
    )

    assert [item.sequence for item in pending] == list(range(1, 35))


def test_pending_dimension_is_3072() -> None:
    pending = build_pending_embeddings(
        sample_chunks(),
        completed_embedding(),
    )

    assert all(item.output_dimension == 3072 for item in pending)


def test_pending_model_and_task_are_preserved() -> None:
    pending = build_pending_embeddings(
        sample_chunks(),
        completed_embedding(),
    )

    assert all(item.model == "gemini-embedding-001" for item in pending)

    assert all(item.task_type == "RETRIEVAL_DOCUMENT" for item in pending)


def test_report_passes() -> None:
    chunks = sample_chunks()
    completed = completed_embedding()

    pending = build_pending_embeddings(
        chunks,
        completed,
    )

    report = build_batch_plan_report(
        chunks=chunks,
        completed=completed,
        pending=pending,
    )

    assert report["source_chunk_count"] == 35
    assert report["completed_embedding_count"] == 1
    assert report["pending_embedding_count"] == 34
    assert report["total_embedding_count"] == 35
    assert report["embedding_dimension"] == 3072
    assert report["plan_status"] == "passed"
    assert report["gemini_call_count"] == 0
    assert report["database_connected"] is False
    assert report["neon_changed"] is False
    assert report["gemini_used"] is False

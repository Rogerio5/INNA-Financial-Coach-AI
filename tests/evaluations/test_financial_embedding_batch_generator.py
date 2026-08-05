from __future__ import annotations

from pathlib import Path

import pytest

from src.evaluation.financial_embedding_batch_generator import (
    CompletedBatchEmbedding,
    EmbeddingRequest,
    build_dry_run_report,
    calculate_text_hash,
    create_completed_embedding,
    determine_pending_requests,
    load_checkpoint,
    validate_requests,
    write_checkpoint,
)


def sample_requests() -> tuple[EmbeddingRequest, ...]:
    return tuple(
        EmbeddingRequest(
            sequence=index,
            chunk_id=f"chunk-{index:03d}",
            documento_key=f"document-{index:03d}",
            chunk_index=1,
            document_title=f"Documento {index}",
            text=f"Texto financeiro {index}",
            model="gemini-embedding-001",
            task_type="RETRIEVAL_DOCUMENT",
            output_dimension=3072,
        )
        for index in range(1, 35)
    )


def sample_completed(
    request: EmbeddingRequest,
) -> CompletedBatchEmbedding:
    return CompletedBatchEmbedding(
        sequence=request.sequence,
        chunk_id=request.chunk_id,
        documento_key=request.documento_key,
        model=request.model,
        task_type=request.task_type,
        dimension=3072,
        text_hash=calculate_text_hash(request.text),
        vector=tuple(0.001 for _ in range(3072)),
    )


def test_validates_thirty_four_requests() -> None:
    requests = sample_requests()

    validate_requests(requests)

    assert len(requests) == 34


def test_rejects_wrong_request_count() -> None:
    with pytest.raises(ValueError):
        validate_requests(sample_requests()[:-1])


def test_empty_checkpoint_has_all_pending() -> None:
    requests = sample_requests()

    pending = determine_pending_requests(
        requests,
        {},
    )

    assert len(pending) == 34


def test_completed_request_is_not_pending() -> None:
    requests = sample_requests()
    completed = {requests[0].chunk_id: sample_completed(requests[0])}

    pending = determine_pending_requests(
        requests,
        completed,
    )

    assert len(pending) == 33
    assert requests[0].chunk_id not in {item.chunk_id for item in pending}


def test_changed_text_is_rejected() -> None:
    requests = list(sample_requests())
    original = requests[0]

    completed = {original.chunk_id: sample_completed(original)}

    requests[0] = EmbeddingRequest(
        sequence=original.sequence,
        chunk_id=original.chunk_id,
        documento_key=original.documento_key,
        chunk_index=original.chunk_index,
        document_title=original.document_title,
        text="Texto alterado",
        model=original.model,
        task_type=original.task_type,
        output_dimension=original.output_dimension,
    )

    with pytest.raises(
        ValueError,
        match="texto mudou",
    ):
        determine_pending_requests(
            tuple(requests),
            completed,
        )


def test_create_completed_embedding() -> None:
    request = sample_requests()[0]

    completed = create_completed_embedding(
        request,
        [0.001 for _ in range(3072)],
    )

    assert completed.dimension == 3072
    assert len(completed.vector) == 3072
    assert completed.text_hash == calculate_text_hash(request.text)


def test_checkpoint_round_trip(
    tmp_path: Path,
) -> None:
    request = sample_requests()[0]
    completed = {request.chunk_id: sample_completed(request)}

    checkpoint_path = tmp_path / "checkpoint.json"

    write_checkpoint(
        checkpoint_path,
        completed,
    )

    loaded = load_checkpoint(checkpoint_path)

    assert list(loaded) == [request.chunk_id]

    assert len(loaded[request.chunk_id].vector) == 3072


def test_dry_run_report_passes() -> None:
    requests = sample_requests()

    report = build_dry_run_report(
        requests=requests,
        completed={},
        pending=requests,
    )

    assert report["request_count"] == 34
    assert report["checkpoint_completed_count"] == 0
    assert report["pending_count"] == 34
    assert report["projected_gemini_call_count"] == 34
    assert report["dry_run_status"] == "passed"
    assert report["gemini_call_count"] == 0
    assert report["database_connected"] is False
    assert report["neon_changed"] is False
    assert report["gemini_used"] is False

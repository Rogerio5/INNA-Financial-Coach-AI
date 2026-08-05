"""Gerador controlado de embeddings financeiros com checkpoint."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXPECTED_REQUEST_COUNT = 34
EXPECTED_DIMENSION = 3072


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    sequence: int
    chunk_id: str
    documento_key: str
    chunk_index: int
    document_title: str
    text: str
    model: str
    task_type: str
    output_dimension: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CompletedBatchEmbedding:
    sequence: int
    chunk_id: str
    documento_key: str
    model: str
    task_type: str
    dimension: int
    text_hash: str
    vector: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["vector"] = list(self.vector)
        return payload


def calculate_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_requests(
    path: Path,
) -> tuple[EmbeddingRequest, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, list):
        raise ValueError("O arquivo de requisicoes deve conter uma lista JSON.")

    requests = tuple(
        EmbeddingRequest(
            sequence=int(item["sequence"]),
            chunk_id=str(item["chunk_id"]),
            documento_key=str(item["documento_key"]),
            chunk_index=int(item["chunk_index"]),
            document_title=str(item["document_title"]),
            text=str(item["text"]),
            model=str(item["model"]),
            task_type=str(item["task_type"]),
            output_dimension=int(item["output_dimension"]),
        )
        for item in payload
    )

    validate_requests(requests)

    return requests


def validate_requests(
    requests: Sequence[EmbeddingRequest],
) -> None:
    if len(requests) != EXPECTED_REQUEST_COUNT:
        raise ValueError("A quantidade de requisicoes deve ser exatamente 34.")

    sequences = [request.sequence for request in requests]

    if sequences != list(range(1, 35)):
        raise ValueError("A sequencia das requisicoes deve ser continua de 1 a 34.")

    chunk_ids = [request.chunk_id for request in requests]

    duplicate_count = sum(
        count - 1 for count in Counter(chunk_ids).values() if count > 1
    )

    if duplicate_count:
        raise ValueError("Existem IDs de chunks duplicados.")

    for request in requests:
        if not request.chunk_id:
            raise ValueError("Existe requisicao sem chunk_id.")

        if not request.documento_key:
            raise ValueError("Existe requisicao sem documento_key.")

        if not request.text.strip():
            raise ValueError(f"Chunk sem texto: {request.chunk_id}")

        if request.output_dimension != EXPECTED_DIMENSION:
            raise ValueError(f"Dimensao inesperada: {request.chunk_id}")

        if request.model != "gemini-embedding-001":
            raise ValueError(f"Modelo inesperado: {request.chunk_id}")

        if request.task_type != "RETRIEVAL_DOCUMENT":
            raise ValueError(f"Task type inesperado: {request.chunk_id}")


def load_checkpoint(
    path: Path,
) -> dict[str, CompletedBatchEmbedding]:
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("O checkpoint deve conter um objeto JSON.")

    completed_payload = payload.get("completed_embeddings", [])

    if not isinstance(completed_payload, list):
        raise ValueError("completed_embeddings deve ser uma lista.")

    completed: dict[str, CompletedBatchEmbedding] = {}

    for item in completed_payload:
        vector = tuple(float(value) for value in item["vector"])

        embedding = CompletedBatchEmbedding(
            sequence=int(item["sequence"]),
            chunk_id=str(item["chunk_id"]),
            documento_key=str(item["documento_key"]),
            model=str(item["model"]),
            task_type=str(item["task_type"]),
            dimension=int(item["dimension"]),
            text_hash=str(item["text_hash"]),
            vector=vector,
        )

        validate_completed_embedding(embedding)

        if embedding.chunk_id in completed:
            raise ValueError("Checkpoint possui chunk_id duplicado.")

        completed[embedding.chunk_id] = embedding

    return completed


def validate_completed_embedding(
    embedding: CompletedBatchEmbedding,
) -> None:
    if embedding.dimension != EXPECTED_DIMENSION:
        raise ValueError(f"Dimensao invalida: {embedding.chunk_id}")

    if len(embedding.vector) != EXPECTED_DIMENSION:
        raise ValueError(f"Vetor incompleto: {embedding.chunk_id}")

    if not all(math.isfinite(value) for value in embedding.vector):
        raise ValueError(f"Vetor nao finito: {embedding.chunk_id}")

    if not any(value != 0.0 for value in embedding.vector):
        raise ValueError(f"Vetor totalmente zerado: {embedding.chunk_id}")


def determine_pending_requests(
    requests: Sequence[EmbeddingRequest],
    completed: Mapping[str, CompletedBatchEmbedding],
) -> tuple[EmbeddingRequest, ...]:
    pending: list[EmbeddingRequest] = []

    request_ids = {request.chunk_id for request in requests}

    unknown_completed_ids = sorted(set(completed) - request_ids)

    if unknown_completed_ids:
        raise ValueError(
            "Checkpoint possui chunks fora do plano: " + ",".join(unknown_completed_ids)
        )

    for request in requests:
        existing = completed.get(request.chunk_id)

        if existing is None:
            pending.append(request)
            continue

        expected_hash = calculate_text_hash(request.text)

        if existing.text_hash != expected_hash:
            raise ValueError(
                "O texto mudou desde a criacao do checkpoint: " + request.chunk_id
            )

        if existing.model != request.model:
            raise ValueError(
                "O modelo mudou desde a criacao do checkpoint: " + request.chunk_id
            )

        if existing.task_type != request.task_type:
            raise ValueError(
                "O task type mudou desde a criacao do checkpoint: " + request.chunk_id
            )

        if existing.dimension != request.output_dimension:
            raise ValueError(
                "A dimensao mudou desde a criacao do checkpoint: " + request.chunk_id
            )

    return tuple(pending)


def create_completed_embedding(
    request: EmbeddingRequest,
    vector: Sequence[float],
) -> CompletedBatchEmbedding:
    values = tuple(float(value) for value in vector)

    embedding = CompletedBatchEmbedding(
        sequence=request.sequence,
        chunk_id=request.chunk_id,
        documento_key=request.documento_key,
        model=request.model,
        task_type=request.task_type,
        dimension=len(values),
        text_hash=calculate_text_hash(request.text),
        vector=values,
    )

    validate_completed_embedding(embedding)

    return embedding


def write_checkpoint(
    path: Path,
    completed: Mapping[str, CompletedBatchEmbedding],
) -> None:
    ordered = sorted(
        completed.values(),
        key=lambda item: (
            item.sequence,
            item.chunk_id,
        ),
    )

    payload = {
        "schema_version": 1,
        "expected_total": EXPECTED_REQUEST_COUNT,
        "completed_count": len(ordered),
        "completed_embeddings": [item.as_dict() for item in ordered],
    }

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_suffix(".tmp")

    temporary_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(path)


def build_dry_run_report(
    *,
    requests: Sequence[EmbeddingRequest],
    completed: Mapping[str, CompletedBatchEmbedding],
    pending: Sequence[EmbeddingRequest],
) -> dict[str, Any]:
    passed = all(
        (
            len(requests) == 34,
            len(completed) + len(pending) == 34,
            len({request.chunk_id for request in pending}) == len(pending),
        )
    )

    return {
        "schema_version": 1,
        "request_count": len(requests),
        "checkpoint_completed_count": len(completed),
        "pending_count": len(pending),
        "projected_gemini_call_count": len(pending),
        "embedding_dimension": EXPECTED_DIMENSION,
        "dry_run_status": ("passed" if passed else "failed"),
        "gemini_call_count": 0,
        "database_connected": False,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


__all__ = [
    "CompletedBatchEmbedding",
    "EmbeddingRequest",
    "build_dry_run_report",
    "calculate_text_hash",
    "create_completed_embedding",
    "determine_pending_requests",
    "load_checkpoint",
    "load_requests",
    "validate_completed_embedding",
    "validate_requests",
    "write_checkpoint",
]

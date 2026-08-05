"""Consolida os 35 embeddings financeiros em um pacote offline."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

EXPECTED_CHUNK_COUNT = 35
EXPECTED_BATCH_COUNT = 34
EXPECTED_DIMENSION = 3072


@dataclass(frozen=True, slots=True)
class ConsolidatedEmbedding:
    chunk_id: str
    documento_key: str
    documento_origem: str
    chunk_index: int
    texto: str
    metadata: dict[str, Any]
    modelo_embedding: str
    embedding: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["embedding"] = list(self.embedding)
        return payload


def validate_vector(
    *,
    chunk_id: str,
    vector: Sequence[float],
) -> tuple[float, ...]:
    values = tuple(float(value) for value in vector)

    if len(values) != EXPECTED_DIMENSION:
        raise ValueError(f"Dimensao invalida para {chunk_id}: {len(values)}")

    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"Vetor possui valor nao finito: {chunk_id}")

    if not any(value != 0.0 for value in values):
        raise ValueError(f"Vetor totalmente zerado: {chunk_id}")

    return values


def load_pilot_embedding(
    pilot_report: Mapping[str, Any],
) -> tuple[str, tuple[float, ...]]:
    if not bool(pilot_report.get("pilot_passed")):
        raise ValueError("O embedding piloto nao foi aprovado.")

    if int(pilot_report.get("gemini_call_count", 0)) != 1:
        raise ValueError("O piloto deve registrar exatamente uma chamada.")

    pilot_input = dict(pilot_report["pilot_input"])
    result = dict(pilot_report["embedding_result"])

    chunk_id = str(pilot_input["chunk_id"])
    vector = validate_vector(
        chunk_id=chunk_id,
        vector=result["vector"],
    )

    return chunk_id, vector


def load_batch_embeddings(
    checkpoint: Mapping[str, Any],
) -> dict[str, tuple[float, ...]]:
    completed = checkpoint.get("completed_embeddings", [])

    if not isinstance(completed, list):
        raise ValueError("completed_embeddings deve ser uma lista.")

    if len(completed) != EXPECTED_BATCH_COUNT:
        raise ValueError("O checkpoint deve possuir 34 embeddings.")

    embeddings: dict[str, tuple[float, ...]] = {}

    for item in completed:
        chunk_id = str(item["chunk_id"])

        if chunk_id in embeddings:
            raise ValueError(f"Chunk duplicado no checkpoint: {chunk_id}")

        embeddings[chunk_id] = validate_vector(
            chunk_id=chunk_id,
            vector=item["vector"],
        )

    return embeddings


def consolidate_embeddings(
    *,
    chunks: Sequence[Mapping[str, Any]],
    pilot_chunk_id: str,
    pilot_vector: Sequence[float],
    batch_embeddings: Mapping[str, Sequence[float]],
) -> tuple[ConsolidatedEmbedding, ...]:
    if len(chunks) != EXPECTED_CHUNK_COUNT:
        raise ValueError("O plano deve possuir exatamente 35 chunks.")

    vectors: dict[str, tuple[float, ...]] = {
        pilot_chunk_id: validate_vector(
            chunk_id=pilot_chunk_id,
            vector=pilot_vector,
        )
    }

    for chunk_id, vector in batch_embeddings.items():
        if chunk_id in vectors:
            raise ValueError(f"Chunk repetido entre piloto e lote: {chunk_id}")

        vectors[str(chunk_id)] = validate_vector(
            chunk_id=str(chunk_id),
            vector=vector,
        )

    if len(vectors) != EXPECTED_CHUNK_COUNT:
        raise ValueError("A consolidacao deve possuir exatamente 35 vetores.")

    source_chunk_ids = [str(chunk["chunk_id"]) for chunk in chunks]

    duplicate_source_ids = sum(
        count - 1 for count in Counter(source_chunk_ids).values() if count > 1
    )

    if duplicate_source_ids:
        raise ValueError("O plano de chunks possui IDs duplicados.")

    missing_vector_ids = sorted(set(source_chunk_ids) - set(vectors))

    unexpected_vector_ids = sorted(set(vectors) - set(source_chunk_ids))

    if missing_vector_ids:
        raise ValueError("Chunks sem vetor: " + ",".join(missing_vector_ids))

    if unexpected_vector_ids:
        raise ValueError("Vetores sem chunk: " + ",".join(unexpected_vector_ids))

    consolidated: list[ConsolidatedEmbedding] = []

    ordered = sorted(
        chunks,
        key=lambda item: (
            str(item["documento_key"]),
            int(item["chunk_index"]),
            str(item["chunk_id"]),
        ),
    )

    for chunk in ordered:
        chunk_id = str(chunk["chunk_id"])
        metadata = dict(chunk.get("metadata", {}))

        metadata.update(
            {
                "embedding_status": "completed",
                "embedding_dimension": EXPECTED_DIMENSION,
                "embedding_model": "gemini-embedding-001",
            }
        )

        consolidated.append(
            ConsolidatedEmbedding(
                chunk_id=chunk_id,
                documento_key=str(chunk["documento_key"]),
                documento_origem=str(chunk["documento_origem"]),
                chunk_index=int(chunk["chunk_index"]),
                texto=str(chunk["texto"]),
                metadata=metadata,
                modelo_embedding=("models/gemini-embedding-001"),
                embedding=vectors[chunk_id],
            )
        )

    return tuple(consolidated)


def build_consolidation_report(
    consolidated: Sequence[ConsolidatedEmbedding],
) -> dict[str, Any]:
    chunk_ids = [item.chunk_id for item in consolidated]

    unique_chunk_count = len(set(chunk_ids))

    invalid_vector_count = sum(
        1
        for item in consolidated
        if len(item.embedding) != EXPECTED_DIMENSION
        or not all(math.isfinite(value) for value in item.embedding)
    )

    passed = all(
        (
            len(consolidated) == EXPECTED_CHUNK_COUNT,
            unique_chunk_count == EXPECTED_CHUNK_COUNT,
            invalid_vector_count == 0,
        )
    )

    return {
        "schema_version": 1,
        "consolidated_chunk_count": len(consolidated),
        "unique_chunk_id_count": unique_chunk_count,
        "valid_embedding_count": (len(consolidated) - invalid_vector_count),
        "invalid_embedding_count": invalid_vector_count,
        "embedding_dimension": EXPECTED_DIMENSION,
        "embedding_model": "gemini-embedding-001",
        "consolidation_status": ("passed" if passed else "failed"),
        "gemini_call_count": 0,
        "database_connected": False,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


__all__ = [
    "ConsolidatedEmbedding",
    "build_consolidation_report",
    "consolidate_embeddings",
    "load_batch_embeddings",
    "load_pilot_embedding",
    "validate_vector",
]

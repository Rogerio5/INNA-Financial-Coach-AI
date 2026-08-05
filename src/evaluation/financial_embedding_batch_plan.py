"""Planeja os embeddings financeiros restantes sem chamar o Gemini."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

EXPECTED_TOTAL_CHUNKS = 35
EXPECTED_PILOT_COUNT = 1
EXPECTED_PENDING_COUNT = 34
EXPECTED_DIMENSION = 3072


@dataclass(frozen=True, slots=True)
class CompletedEmbedding:
    chunk_id: str
    documento_key: str
    model: str
    task_type: str
    dimension: int
    vector: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["vector"] = list(self.vector)
        return payload


@dataclass(frozen=True, slots=True)
class PendingEmbedding:
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


def load_completed_pilot(
    pilot_report: Mapping[str, Any],
) -> CompletedEmbedding:
    if not bool(pilot_report.get("pilot_passed")):
        raise ValueError("O piloto de embedding nao foi aprovado.")

    if int(pilot_report.get("gemini_call_count", 0)) != 1:
        raise ValueError("O relatorio piloto deve registrar exatamente uma chamada.")

    pilot_input = dict(pilot_report["pilot_input"])

    embedding_result = dict(pilot_report["embedding_result"])

    vector = tuple(float(value) for value in embedding_result["vector"])

    dimension = int(embedding_result["actual_dimension"])

    if dimension != EXPECTED_DIMENSION:
        raise ValueError(f"Dimensao piloto inesperada: {dimension}")

    if len(vector) != dimension:
        raise ValueError("O tamanho do vetor piloto nao corresponde a dimensao.")

    if not all(math.isfinite(value) for value in vector):
        raise ValueError("O vetor piloto possui valor nao finito.")

    return CompletedEmbedding(
        chunk_id=str(pilot_input["chunk_id"]),
        documento_key=str(pilot_input["documento_key"]),
        model=str(pilot_input["model"]),
        task_type=str(pilot_input["task_type"]),
        dimension=dimension,
        vector=vector,
    )


def build_pending_embeddings(
    chunks: Sequence[Mapping[str, Any]],
    completed: CompletedEmbedding,
) -> tuple[PendingEmbedding, ...]:
    if len(chunks) != EXPECTED_TOTAL_CHUNKS:
        raise ValueError("O plano deve conter exatamente 35 chunks.")

    chunk_ids = [str(chunk["chunk_id"]) for chunk in chunks]

    duplicate_count = sum(
        count - 1 for count in Counter(chunk_ids).values() if count > 1
    )

    if duplicate_count:
        raise ValueError("O plano possui IDs de chunks duplicados.")

    if completed.chunk_id not in chunk_ids:
        raise ValueError("O chunk piloto nao existe no plano dos 35 chunks.")

    ordered = sorted(
        chunks,
        key=lambda item: (
            str(item["documento_key"]),
            int(item["chunk_index"]),
            str(item["chunk_id"]),
        ),
    )

    pending: list[PendingEmbedding] = []

    for chunk in ordered:
        chunk_id = str(chunk["chunk_id"])

        if chunk_id == completed.chunk_id:
            continue

        metadata = dict(
            chunk.get(
                "metadata",
                {},
            )
        )

        text = str(chunk["texto"]).strip()

        if not text:
            raise ValueError(f"Chunk sem texto: {chunk_id}")

        document_title = str(
            metadata.get(
                "document_title",
                chunk["documento_key"],
            )
        ).strip()

        pending.append(
            PendingEmbedding(
                sequence=len(pending) + 1,
                chunk_id=chunk_id,
                documento_key=str(chunk["documento_key"]),
                chunk_index=int(chunk["chunk_index"]),
                document_title=document_title,
                text=text,
                model=completed.model,
                task_type=completed.task_type,
                output_dimension=completed.dimension,
            )
        )

    if len(pending) != EXPECTED_PENDING_COUNT:
        raise ValueError("A quantidade de embeddings pendentes deveria ser 34.")

    return tuple(pending)


def build_batch_plan_report(
    *,
    chunks: Sequence[Mapping[str, Any]],
    completed: CompletedEmbedding,
    pending: Sequence[PendingEmbedding],
) -> dict[str, Any]:
    pending_ids = [item.chunk_id for item in pending]

    duplicate_pending_ids = sum(
        count - 1 for count in Counter(pending_ids).values() if count > 1
    )

    passed = all(
        (
            len(chunks) == EXPECTED_TOTAL_CHUNKS,
            len(pending) == EXPECTED_PENDING_COUNT,
            duplicate_pending_ids == 0,
            completed.chunk_id not in pending_ids,
            completed.dimension == EXPECTED_DIMENSION,
        )
    )

    return {
        "schema_version": 1,
        "source_chunk_count": len(chunks),
        "completed_embedding_count": EXPECTED_PILOT_COUNT,
        "pending_embedding_count": len(pending),
        "total_embedding_count": (EXPECTED_PILOT_COUNT + len(pending)),
        "pilot_chunk_id": completed.chunk_id,
        "embedding_model": completed.model,
        "task_type": completed.task_type,
        "embedding_dimension": completed.dimension,
        "duplicate_pending_chunk_id_count": (duplicate_pending_ids),
        "plan_status": ("passed" if passed else "failed"),
        "gemini_call_count": 0,
        "database_connected": False,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


__all__ = [
    "CompletedEmbedding",
    "PendingEmbedding",
    "build_batch_plan_report",
    "build_pending_embeddings",
    "load_completed_pilot",
]

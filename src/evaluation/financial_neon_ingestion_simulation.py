"""Preparacao da simulacao transacional da base financeira no Neon."""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_DOCUMENT_COUNT = 16
EXPECTED_CHUNK_COUNT = 35
EXPECTED_VECTOR_DIMENSION = 3072


@dataclass(frozen=True, slots=True)
class SimulationPlan:
    documents: tuple[dict[str, Any], ...]
    chunks: tuple[dict[str, Any], ...]

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


def load_json_list(path: Path) -> tuple[dict[str, Any], ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, list):
        raise ValueError(f"O arquivo deve conter uma lista JSON: {path}")

    return tuple(dict(item) for item in payload)


def vector_to_pgvector(
    vector: Sequence[float],
) -> str:
    values = tuple(float(value) for value in vector)

    if len(values) != EXPECTED_VECTOR_DIMENSION:
        raise ValueError(f"Dimensao de vetor invalida: {len(values)}")

    if not all(math.isfinite(value) for value in values):
        raise ValueError("O vetor possui valores nao finitos.")

    if not any(value != 0.0 for value in values):
        raise ValueError("O vetor nao pode ser totalmente zerado.")

    return "[" + ",".join(format(value, ".17g") for value in values) + "]"


def validate_documents(
    documents: Sequence[Mapping[str, Any]],
) -> None:
    if len(documents) != EXPECTED_DOCUMENT_COUNT:
        raise ValueError("O plano deve possuir exatamente 16 documentos.")

    logical_names = [str(document["nome_logico"]) for document in documents]

    hashes = [str(document["content_hash"]) for document in documents]

    if len(set(logical_names)) != EXPECTED_DOCUMENT_COUNT:
        raise ValueError("Existem nomes logicos duplicados.")

    if len(set(hashes)) != EXPECTED_DOCUMENT_COUNT:
        raise ValueError("Existem content hashes duplicados.")

    for document in documents:
        if not str(document["nome_salvo"]).strip():
            raise ValueError("Existe documento sem nome_salvo.")

        if not str(document["nome_logico"]).strip():
            raise ValueError("Existe documento sem nome_logico.")

        if len(str(document["content_hash"])) != 64:
            raise ValueError("Existe content_hash invalido.")

        if int(document["total_chunks"]) <= 0:
            raise ValueError("Existe documento sem chunks.")


def validate_chunks(
    chunks: Sequence[Mapping[str, Any]],
    document_keys: set[str],
) -> None:
    if len(chunks) != EXPECTED_CHUNK_COUNT:
        raise ValueError("O pacote deve possuir exatamente 35 chunks.")

    chunk_ids = [str(chunk["chunk_id"]) for chunk in chunks]

    duplicate_count = sum(
        count - 1 for count in Counter(chunk_ids).values() if count > 1
    )

    if duplicate_count:
        raise ValueError("Existem chunk_ids duplicados.")

    for chunk in chunks:
        document_key = str(chunk["documento_key"])

        if document_key not in document_keys:
            raise ValueError("Chunk referencia documento desconhecido: " + document_key)

        if not str(chunk["texto"]).strip():
            raise ValueError("Existe chunk sem texto.")

        if int(chunk["chunk_index"]) <= 0:
            raise ValueError("Existe chunk_index invalido.")

        vector_to_pgvector(chunk["embedding"])


def build_simulation_plan(
    documents: Sequence[Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
) -> SimulationPlan:
    validate_documents(documents)

    document_keys = {str(document["nome_logico"]) for document in documents}

    validate_chunks(
        chunks,
        document_keys,
    )

    expected_chunk_totals = {
        str(document["nome_logico"]): int(document["total_chunks"])
        for document in documents
    }

    actual_chunk_totals = Counter(str(chunk["documento_key"]) for chunk in chunks)

    if expected_chunk_totals != dict(actual_chunk_totals):
        raise ValueError("Os totais de chunks por documento nao correspondem.")

    ordered_documents = tuple(
        dict(document)
        for document in sorted(
            documents,
            key=lambda item: str(item["nome_logico"]),
        )
    )

    ordered_chunks = tuple(
        dict(chunk)
        for chunk in sorted(
            chunks,
            key=lambda item: (
                str(item["documento_key"]),
                int(item["chunk_index"]),
                str(item["chunk_id"]),
            ),
        )
    )

    return SimulationPlan(
        documents=ordered_documents,
        chunks=ordered_chunks,
    )


def build_offline_report(
    plan: SimulationPlan,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "document_count": plan.document_count,
        "chunk_count": plan.chunk_count,
        "embedding_count": plan.chunk_count,
        "embedding_dimension": EXPECTED_VECTOR_DIMENSION,
        "offline_plan_status": "passed",
        "database_connected": False,
        "database_write_executed": False,
        "transaction_committed": False,
        "rollback_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


__all__ = [
    "SimulationPlan",
    "build_offline_report",
    "build_simulation_plan",
    "load_json_list",
    "validate_chunks",
    "validate_documents",
    "vector_to_pgvector",
]

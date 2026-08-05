"""Ingestao definitiva e transacional da base financeira no Neon."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.evaluation.financial_neon_ingestion_simulation import (
    EXPECTED_CHUNK_COUNT,
    EXPECTED_DOCUMENT_COUNT,
    EXPECTED_VECTOR_DIMENSION,
    SimulationPlan,
    build_simulation_plan,
    vector_to_pgvector,
)


@dataclass(frozen=True, slots=True)
class ConflictSummary:
    document_logical_name_count: int
    document_content_hash_count: int
    chunk_id_count: int

    @property
    def total(self) -> int:
        return (
            self.document_logical_name_count
            + self.document_content_hash_count
            + self.chunk_id_count
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "document_logical_name_count": (self.document_logical_name_count),
            "document_content_hash_count": (self.document_content_hash_count),
            "chunk_id_count": self.chunk_id_count,
            "total": self.total,
        }


def build_offline_ingestion_report(
    plan: SimulationPlan,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "planned_document_insert_count": plan.document_count,
        "planned_chunk_insert_count": plan.chunk_count,
        "planned_embedding_insert_count": plan.chunk_count,
        "embedding_dimension": EXPECTED_VECTOR_DIMENSION,
        "transaction_strategy": "single_transaction",
        "duplicate_guard_enabled": True,
        "rollback_on_error_enabled": True,
        "commit_confirmation_required": True,
        "offline_plan_status": "passed",
        "database_connected": False,
        "database_write_executed": False,
        "transaction_committed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


def build_conflict_queries(
    plan: SimulationPlan,
) -> dict[str, tuple[str, ...]]:
    logical_names = tuple(str(document["nome_logico"]) for document in plan.documents)

    content_hashes = tuple(str(document["content_hash"]) for document in plan.documents)

    chunk_ids = tuple(str(chunk["chunk_id"]) for chunk in plan.chunks)

    return {
        "logical_names": logical_names,
        "content_hashes": content_hashes,
        "chunk_ids": chunk_ids,
    }


def validate_conflict_summary(
    summary: ConflictSummary,
) -> None:
    if summary.total != 0:
        raise RuntimeError("A ingestao foi bloqueada por conflitos existentes.")


def create_document_insert_parameters(
    document: Mapping[str, Any],
) -> tuple[Any, ...]:
    return (
        document["nome_original"],
        document["nome_salvo"],
        document["caminho_upload"],
        document["caminho_chunks"],
        document["caminho_embedding_ready"],
        document["extensao"],
        document["tamanho_bytes"],
        document["total_chunks"],
        document["status"],
        document["origem"],
        document["ativo"],
        document["nome_logico"],
        document["content_hash"],
        document["versao"],
        document["documento_raiz_id"],
        document["documento_anterior_id"],
    )


def create_chunk_insert_parameters(
    *,
    chunk: Mapping[str, Any],
    document_id: int,
) -> tuple[Any, ...]:
    metadata = dict(chunk["metadata"])
    metadata["database_document_id"] = document_id
    metadata["ingestion_mode"] = "definitive"

    return (
        document_id,
        chunk["chunk_id"],
        chunk["documento_origem"],
        chunk["chunk_index"],
        chunk["texto"],
        json.dumps(
            metadata,
            ensure_ascii=False,
        ),
        vector_to_pgvector(chunk["embedding"]),
        chunk["modelo_embedding"],
    )


def validate_inserted_document_ids(
    *,
    plan: SimulationPlan,
    document_ids: Mapping[str, int],
) -> None:
    expected_keys = {str(document["nome_logico"]) for document in plan.documents}

    actual_keys = set(document_ids)

    if expected_keys != actual_keys:
        raise RuntimeError(
            "Os IDs retornados nao correspondem aos documentos planejados."
        )

    ids = list(document_ids.values())

    if len(ids) != EXPECTED_DOCUMENT_COUNT:
        raise RuntimeError("Quantidade incorreta de IDs de documentos.")

    if len(set(ids)) != EXPECTED_DOCUMENT_COUNT:
        raise RuntimeError("Foram retornados IDs de documentos duplicados.")

    if any(int(value) <= 0 for value in ids):
        raise RuntimeError("Foi retornado ID de documento invalido.")


def validate_final_counts(
    *,
    document_count_before: int,
    chunk_count_before: int,
    document_count_after: int,
    chunk_count_after: int,
) -> None:
    if document_count_after != document_count_before + EXPECTED_DOCUMENT_COUNT:
        raise RuntimeError("A contagem final de documentos ficou incorreta.")

    if chunk_count_after != chunk_count_before + EXPECTED_CHUNK_COUNT:
        raise RuntimeError("A contagem final de chunks ficou incorreta.")


def validate_new_rows(
    *,
    document_match_count: int,
    chunk_match_count: int,
) -> None:
    if document_match_count != EXPECTED_DOCUMENT_COUNT:
        raise RuntimeError("Nem todos os novos documentos foram encontrados.")

    if chunk_match_count != EXPECTED_CHUNK_COUNT:
        raise RuntimeError("Nem todos os novos chunks foram encontrados.")


def validate_chunk_distribution(
    *,
    plan: SimulationPlan,
    database_distribution: Mapping[str, int],
) -> None:
    expected = Counter(str(chunk["documento_key"]) for chunk in plan.chunks)

    actual = {str(key): int(value) for key, value in database_distribution.items()}

    if dict(expected) != actual:
        raise RuntimeError("A distribuicao de chunks por documento ficou incorreta.")


__all__ = [
    "ConflictSummary",
    "build_conflict_queries",
    "build_offline_ingestion_report",
    "build_simulation_plan",
    "create_chunk_insert_parameters",
    "create_document_insert_parameters",
    "validate_chunk_distribution",
    "validate_conflict_summary",
    "validate_final_counts",
    "validate_inserted_document_ids",
    "validate_new_rows",
]

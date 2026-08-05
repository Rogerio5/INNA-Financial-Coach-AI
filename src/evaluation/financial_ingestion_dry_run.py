"""Mapeamento offline dos chunks financeiros para ingestao no Neon.

Este modulo apenas prepara e valida payloads. Nenhuma conexao com banco,
rede externa ou Gemini e realizada.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXPECTED_CHUNK_COLUMNS = (
    "chunk_id",
    "chunk_index",
    "documento_id",
    "documento_origem",
    "texto",
    "metadata",
    "modelo_embedding",
    "embedding",
)

EXPECTED_DOCUMENT_COLUMNS = (
    "document_key",
    "nome_arquivo",
    "tipo_documento",
    "categoria",
    "idioma",
    "versao",
    "content_hash",
    "total_chunks",
    "ativo",
    "status",
)


@dataclass(frozen=True, slots=True)
class DryRunDocumentPayload:
    document_key: str
    nome_arquivo: str
    tipo_documento: str
    categoria: str
    idioma: str
    versao: str
    content_hash: str
    total_chunks: int
    ativo: bool
    status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DryRunChunkPayload:
    chunk_id: str
    chunk_index: int
    documento_id: str
    documento_origem: str
    texto: str
    metadata: dict[str, Any]
    modelo_embedding: str | None
    embedding: None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FinancialIngestionDryRunReport:
    schema_version: int
    source_chunk_count: int
    mapped_chunk_count: int
    mapped_document_count: int
    duplicate_chunk_id_count: int
    duplicate_chunk_hash_count: int
    duplicate_document_key_count: int
    invalid_chunk_count: int
    invalid_document_count: int
    areas: dict[str, int]
    topics: dict[str, int]
    status: str
    database_connected: bool
    database_write_executed: bool
    neon_changed: bool
    gemini_used: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def stable_document_content_hash(
    chunks: Sequence[Mapping[str, Any]],
) -> str:
    canonical = "\n".join(
        str(chunk["canonical_hash"])
        for chunk in sorted(
            chunks,
            key=lambda item: int(item["chunk_index"]),
        )
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_source_chunks(
    path: Path,
) -> tuple[dict[str, Any], ...]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(payload, list):
        raise ValueError("O arquivo de chunks deve conter uma lista JSON.")

    chunks = tuple(dict(item) for item in payload)

    if not chunks:
        raise ValueError("O arquivo de chunks esta vazio.")

    return chunks


def validate_source_chunk(
    chunk: Mapping[str, Any],
) -> tuple[str, ...]:
    required = (
        "chunk_id",
        "document_id",
        "document_title",
        "document_path",
        "area",
        "topic",
        "section_title",
        "chunk_index",
        "language",
        "version",
        "source_ids",
        "text",
        "word_count",
        "content_hash",
        "canonical_hash",
    )

    errors: list[str] = []

    for key in required:
        if key not in chunk:
            errors.append(f"missing:{key}")

    for key in (
        "chunk_id",
        "document_id",
        "document_title",
        "document_path",
        "area",
        "topic",
        "text",
        "content_hash",
        "canonical_hash",
    ):
        if key in chunk and not str(chunk[key]).strip():
            errors.append(f"empty:{key}")

    if int(chunk.get("chunk_index", 0)) <= 0:
        errors.append("invalid:chunk_index")

    if int(chunk.get("word_count", 0)) < 70:
        errors.append("invalid:word_count_below_70")

    if int(chunk.get("word_count", 0)) > 190:
        errors.append("invalid:word_count_above_190")

    return tuple(errors)


def build_document_payloads(
    chunks: Sequence[Mapping[str, Any]],
) -> tuple[DryRunDocumentPayload, ...]:
    by_document: dict[
        str,
        list[Mapping[str, Any]],
    ] = {}

    for chunk in chunks:
        document_id = str(chunk["document_id"])

        by_document.setdefault(
            document_id,
            [],
        ).append(chunk)

    payloads: list[DryRunDocumentPayload] = []

    for document_id in sorted(by_document):
        document_chunks = by_document[document_id]

        first = sorted(
            document_chunks,
            key=lambda item: int(item["chunk_index"]),
        )[0]

        payloads.append(
            DryRunDocumentPayload(
                document_key=document_id,
                nome_arquivo=str(first["document_path"]),
                tipo_documento="markdown",
                categoria=str(first["area"]),
                idioma=str(first["language"]),
                versao=str(first["version"]),
                content_hash=(stable_document_content_hash(document_chunks)),
                total_chunks=len(document_chunks),
                ativo=True,
                status="dry_run_ready",
            )
        )

    return tuple(payloads)


def build_chunk_payloads(
    chunks: Sequence[Mapping[str, Any]],
) -> tuple[DryRunChunkPayload, ...]:
    payloads: list[DryRunChunkPayload] = []

    ordered = sorted(
        chunks,
        key=lambda item: (
            str(item["document_id"]),
            int(item["chunk_index"]),
        ),
    )

    for chunk in ordered:
        metadata = {
            "schema_version": 2,
            "knowledge_base": ("inna_financial_v2"),
            "area": str(chunk["area"]),
            "topic": str(chunk["topic"]),
            "document_title": str(chunk["document_title"]),
            "document_path": str(chunk["document_path"]),
            "section_title": str(chunk["section_title"]),
            "language": str(chunk["language"]),
            "version": str(chunk["version"]),
            "source_ids": list(
                chunk.get(
                    "source_ids",
                    [],
                )
            ),
            "word_count": int(chunk["word_count"]),
            "content_hash": str(chunk["content_hash"]),
            "canonical_hash": str(chunk["canonical_hash"]),
            "ingestion_mode": "dry_run",
            "embedding_status": "pending",
        }

        payloads.append(
            DryRunChunkPayload(
                chunk_id=str(chunk["chunk_id"]),
                chunk_index=int(chunk["chunk_index"]),
                documento_id=str(chunk["document_id"]),
                documento_origem=str(chunk["document_path"]),
                texto=str(chunk["text"]),
                metadata=metadata,
                modelo_embedding=None,
                embedding=None,
            )
        )

    return tuple(payloads)


def validate_document_payload(
    payload: DryRunDocumentPayload,
) -> tuple[str, ...]:
    errors: list[str] = []

    if not payload.document_key:
        errors.append("empty:document_key")

    if not payload.nome_arquivo:
        errors.append("empty:nome_arquivo")

    if payload.total_chunks <= 0:
        errors.append("invalid:total_chunks")

    if len(payload.content_hash) != 64:
        errors.append("invalid:content_hash")

    return tuple(errors)


def validate_chunk_payload(
    payload: DryRunChunkPayload,
) -> tuple[str, ...]:
    errors: list[str] = []

    if not payload.chunk_id:
        errors.append("empty:chunk_id")

    if not payload.documento_id:
        errors.append("empty:documento_id")

    if not payload.texto:
        errors.append("empty:texto")

    if payload.chunk_index <= 0:
        errors.append("invalid:chunk_index")

    if payload.embedding is not None:
        errors.append("invalid:embedding_not_null")

    if payload.modelo_embedding is not None:
        errors.append("invalid:modelo_embedding_not_null")

    if payload.metadata.get("embedding_status") != "pending":
        errors.append("invalid:embedding_status")

    return tuple(errors)


def create_dry_run_report(
    source_chunks: Sequence[Mapping[str, Any]],
    document_payloads: Sequence[DryRunDocumentPayload],
    chunk_payloads: Sequence[DryRunChunkPayload],
) -> FinancialIngestionDryRunReport:
    source_errors = [
        error for chunk in source_chunks for error in validate_source_chunk(chunk)
    ]

    document_errors = [
        error
        for payload in document_payloads
        for error in validate_document_payload(payload)
    ]

    chunk_errors = [
        error for payload in chunk_payloads for error in validate_chunk_payload(payload)
    ]

    chunk_ids = [payload.chunk_id for payload in chunk_payloads]

    chunk_hashes = [
        str(payload.metadata["canonical_hash"]) for payload in chunk_payloads
    ]

    document_keys = [payload.document_key for payload in document_payloads]

    duplicate_chunk_id_count = sum(
        count - 1 for count in Counter(chunk_ids).values() if count > 1
    )

    duplicate_chunk_hash_count = sum(
        count - 1 for count in Counter(chunk_hashes).values() if count > 1
    )

    duplicate_document_key_count = sum(
        count - 1 for count in Counter(document_keys).values() if count > 1
    )

    areas = Counter(str(chunk["area"]) for chunk in source_chunks)

    topics = Counter(str(chunk["topic"]) for chunk in source_chunks)

    invalid_chunk_count = len(source_errors) + len(chunk_errors)

    invalid_document_count = len(document_errors)

    passed = all(
        (
            len(source_chunks) == 35,
            len(chunk_payloads) == 35,
            len(document_payloads) == 16,
            invalid_chunk_count == 0,
            invalid_document_count == 0,
            duplicate_chunk_id_count == 0,
            duplicate_chunk_hash_count == 0,
            duplicate_document_key_count == 0,
        )
    )

    return FinancialIngestionDryRunReport(
        schema_version=1,
        source_chunk_count=len(source_chunks),
        mapped_chunk_count=len(chunk_payloads),
        mapped_document_count=len(document_payloads),
        duplicate_chunk_id_count=(duplicate_chunk_id_count),
        duplicate_chunk_hash_count=(duplicate_chunk_hash_count),
        duplicate_document_key_count=(duplicate_document_key_count),
        invalid_chunk_count=(invalid_chunk_count),
        invalid_document_count=(invalid_document_count),
        areas=dict(sorted(areas.items())),
        topics=dict(sorted(topics.items())),
        status=("passed" if passed else "failed"),
        database_connected=False,
        database_write_executed=False,
        neon_changed=False,
        gemini_used=False,
    )


def write_dry_run_outputs(
    *,
    output_directory: Path,
    report: FinancialIngestionDryRunReport,
    document_payloads: Sequence[DryRunDocumentPayload],
    chunk_payloads: Sequence[DryRunChunkPayload],
) -> dict[str, Path]:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents_path = output_directory / "financial_documents_dry_run.json"

    chunks_path = output_directory / "financial_chunks_dry_run.json"

    report_path = output_directory / "financial_ingestion_dry_run_report.json"

    documents_path.write_text(
        json.dumps(
            [payload.as_dict() for payload in document_payloads],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    chunks_path.write_text(
        json.dumps(
            [payload.as_dict() for payload in chunk_payloads],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path.write_text(
        json.dumps(
            report.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "documents": documents_path,
        "chunks": chunks_path,
        "report": report_path,
    }


__all__ = [
    "DryRunChunkPayload",
    "DryRunDocumentPayload",
    "EXPECTED_CHUNK_COLUMNS",
    "EXPECTED_DOCUMENT_COLUMNS",
    "FinancialIngestionDryRunReport",
    "build_chunk_payloads",
    "build_document_payloads",
    "create_dry_run_report",
    "load_source_chunks",
    "stable_document_content_hash",
    "validate_chunk_payload",
    "validate_document_payload",
    "validate_source_chunk",
    "write_dry_run_outputs",
]

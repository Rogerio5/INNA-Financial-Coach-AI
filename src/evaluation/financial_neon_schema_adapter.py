"""Adapta os payloads financeiros ao esquema real do Neon.

O modulo somente transforma e valida dados em memoria.
Nenhuma conexao com banco, Gemini ou rede externa e executada.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

VERSION_PATTERN = re.compile(r"(?P<major>\d+)")


@dataclass(frozen=True, slots=True)
class NeonDocumentInsertPayload:
    nome_original: str
    nome_salvo: str
    caminho_upload: str | None
    caminho_chunks: str | None
    caminho_embedding_ready: str | None
    extensao: str
    tamanho_bytes: int | None
    total_chunks: int
    status: str
    origem: str
    ativo: bool
    nome_logico: str
    content_hash: str
    versao: int
    documento_raiz_id: int | None
    documento_anterior_id: int | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class NeonChunkInsertPayload:
    documento_key: str
    chunk_id: str
    documento_origem: str
    chunk_index: int
    texto: str
    metadata: dict[str, Any]
    embedding: None
    modelo_embedding: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class NeonSchemaAdapterReport:
    schema_version: int
    source_document_count: int
    source_chunk_count: int
    adapted_document_count: int
    adapted_chunk_count: int
    duplicate_document_key_count: int
    duplicate_chunk_id_count: int
    invalid_document_count: int
    invalid_chunk_count: int
    status: str
    database_connected: bool
    database_write_executed: bool
    neon_changed: bool
    gemini_used: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_json_list(
    path: Path,
) -> tuple[dict[str, Any], ...]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(payload, list):
        raise ValueError(f"O arquivo deve conter uma lista JSON: {path}")

    return tuple(dict(item) for item in payload)


def parse_integer_version(
    value: object,
) -> int:
    text = str(value or "").strip()

    match = VERSION_PATTERN.search(text)

    if match is None:
        return 1

    version = int(match.group("major"))

    return max(
        version,
        1,
    )


def normalize_extension(
    value: object,
) -> str:
    text = str(value or "").strip().lower()

    if not text:
        return ".md"

    if not text.startswith("."):
        text = "." + text

    return text


def build_neon_document_payloads(
    source_documents: Sequence[Mapping[str, Any]],
) -> tuple[NeonDocumentInsertPayload, ...]:
    payloads: list[NeonDocumentInsertPayload] = []

    for document in sorted(
        source_documents,
        key=lambda item: str(item["document_key"]),
    ):
        document_key = str(document["document_key"])

        original_path = Path(str(document["nome_arquivo"]))

        original_name = original_path.name or f"{document_key}.md"

        extension = normalize_extension(
            original_path.suffix
            or document.get(
                "tipo_documento",
                "md",
            )
        )

        category = str(
            document.get(
                "categoria",
                "financeiro",
            )
        )

        language = str(
            document.get(
                "idioma",
                "pt-BR",
            )
        )

        origin = "knowledge_base:" + category + ":" + language

        payloads.append(
            NeonDocumentInsertPayload(
                nome_original=original_name,
                nome_salvo=original_name,
                caminho_upload=str(document["nome_arquivo"]),
                caminho_chunks=None,
                caminho_embedding_ready=None,
                extensao=extension,
                tamanho_bytes=None,
                total_chunks=int(document["total_chunks"]),
                status="adaptado_sem_embedding",
                origem=origin,
                ativo=bool(document["ativo"]),
                nome_logico=document_key,
                content_hash=str(document["content_hash"]),
                versao=parse_integer_version(document["versao"]),
                documento_raiz_id=None,
                documento_anterior_id=None,
            )
        )

    return tuple(payloads)


def build_neon_chunk_payloads(
    source_chunks: Sequence[Mapping[str, Any]],
) -> tuple[NeonChunkInsertPayload, ...]:
    payloads: list[NeonChunkInsertPayload] = []

    ordered = sorted(
        source_chunks,
        key=lambda item: (
            str(item["documento_id"]),
            int(item["chunk_index"]),
        ),
    )

    for chunk in ordered:
        metadata = dict(
            chunk.get(
                "metadata",
                {},
            )
        )

        metadata.update(
            {
                "schema_adapter_version": 1,
                "documento_key": str(chunk["documento_id"]),
                "embedding_status": "pending",
                "ingestion_status": ("offline_adapted"),
                "database_document_id": None,
            }
        )

        payloads.append(
            NeonChunkInsertPayload(
                documento_key=str(chunk["documento_id"]),
                chunk_id=str(chunk["chunk_id"]),
                documento_origem=str(chunk["documento_origem"]),
                chunk_index=int(chunk["chunk_index"]),
                texto=str(chunk["texto"]),
                metadata=metadata,
                embedding=None,
                modelo_embedding=("models/gemini-embedding-001"),
            )
        )

    return tuple(payloads)


def validate_document_payload(
    payload: NeonDocumentInsertPayload,
) -> tuple[str, ...]:
    errors: list[str] = []

    if not payload.nome_original:
        errors.append("empty:nome_original")

    if not payload.nome_salvo:
        errors.append("empty:nome_salvo")

    if not payload.nome_logico:
        errors.append("empty:nome_logico")

    if payload.total_chunks <= 0:
        errors.append("invalid:total_chunks")

    if len(payload.content_hash) != 64:
        errors.append("invalid:content_hash")

    if payload.versao <= 0:
        errors.append("invalid:versao")

    if not payload.extensao.startswith("."):
        errors.append("invalid:extensao")

    return tuple(errors)


def validate_chunk_payload(
    payload: NeonChunkInsertPayload,
) -> tuple[str, ...]:
    errors: list[str] = []

    if not payload.documento_key:
        errors.append("empty:documento_key")

    if not payload.chunk_id:
        errors.append("empty:chunk_id")

    if not payload.texto:
        errors.append("empty:texto")

    if payload.chunk_index <= 0:
        errors.append("invalid:chunk_index")

    if payload.embedding is not None:
        errors.append("invalid:embedding")

    if not payload.modelo_embedding:
        errors.append("empty:modelo_embedding")

    if payload.metadata.get("database_document_id") is not None:
        errors.append("invalid:database_document_id")

    return tuple(errors)


def create_adapter_report(
    *,
    source_documents: Sequence[Mapping[str, Any]],
    source_chunks: Sequence[Mapping[str, Any]],
    adapted_documents: Sequence[NeonDocumentInsertPayload],
    adapted_chunks: Sequence[NeonChunkInsertPayload],
) -> NeonSchemaAdapterReport:
    document_errors = [
        error
        for payload in adapted_documents
        for error in validate_document_payload(payload)
    ]

    chunk_errors = [
        error for payload in adapted_chunks for error in validate_chunk_payload(payload)
    ]

    document_keys = [payload.nome_logico for payload in adapted_documents]

    chunk_ids = [payload.chunk_id for payload in adapted_chunks]

    duplicate_document_key_count = sum(
        count - 1 for count in Counter(document_keys).values() if count > 1
    )

    duplicate_chunk_id_count = sum(
        count - 1 for count in Counter(chunk_ids).values() if count > 1
    )

    passed = all(
        (
            len(source_documents) == 16,
            len(source_chunks) == 35,
            len(adapted_documents) == 16,
            len(adapted_chunks) == 35,
            len(document_errors) == 0,
            len(chunk_errors) == 0,
            duplicate_document_key_count == 0,
            duplicate_chunk_id_count == 0,
        )
    )

    return NeonSchemaAdapterReport(
        schema_version=1,
        source_document_count=len(source_documents),
        source_chunk_count=len(source_chunks),
        adapted_document_count=len(adapted_documents),
        adapted_chunk_count=len(adapted_chunks),
        duplicate_document_key_count=(duplicate_document_key_count),
        duplicate_chunk_id_count=(duplicate_chunk_id_count),
        invalid_document_count=len(document_errors),
        invalid_chunk_count=len(chunk_errors),
        status=("passed" if passed else "failed"),
        database_connected=False,
        database_write_executed=False,
        neon_changed=False,
        gemini_used=False,
    )


def write_adapter_outputs(
    *,
    output_directory: Path,
    documents: Sequence[NeonDocumentInsertPayload],
    chunks: Sequence[NeonChunkInsertPayload],
    report: NeonSchemaAdapterReport,
) -> dict[str, Path]:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents_path = output_directory / "neon_documents_insert_plan.json"

    chunks_path = output_directory / "neon_chunks_insert_plan.json"

    report_path = output_directory / "neon_schema_adapter_report.json"

    documents_path.write_text(
        json.dumps(
            [payload.as_dict() for payload in documents],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    chunks_path.write_text(
        json.dumps(
            [payload.as_dict() for payload in chunks],
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
    "NeonChunkInsertPayload",
    "NeonDocumentInsertPayload",
    "NeonSchemaAdapterReport",
    "build_neon_chunk_payloads",
    "build_neon_document_payloads",
    "create_adapter_report",
    "load_json_list",
    "normalize_extension",
    "parse_integer_version",
    "validate_chunk_payload",
    "validate_document_payload",
    "write_adapter_outputs",
]

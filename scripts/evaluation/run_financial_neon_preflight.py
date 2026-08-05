"""Executa o pre-voo financeiro em transacao read-only."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_neon_preflight import (
    ExistingDocument,
    analyze_documents,
    summarize_decisions,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--documents", required=True, type=Path)
    parser.add_argument("--chunks", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)

    return parser


def load_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, list):
        raise ValueError(f"Lista JSON esperada: {path}")

    return [dict(item) for item in payload]


def database_url() -> str:
    load_dotenv()

    value = (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
    )

    if not value:
        raise RuntimeError("URL do Neon nao encontrada.")

    return value


def connect(url: str) -> tuple[Any, str]:
    try:
        import psycopg

        return psycopg.connect(url, autocommit=False), "psycopg3"
    except ImportError:
        import psycopg2

        connection = psycopg2.connect(url)
        connection.autocommit = False

        return connection, "psycopg2"


def main() -> int:
    args = build_parser().parse_args()

    planned_documents = load_list(args.documents)
    planned_chunks = load_list(args.chunks)

    logical_names = [str(document["nome_logico"]) for document in planned_documents]

    content_hashes = [str(document["content_hash"]) for document in planned_documents]

    chunk_ids = [str(chunk["chunk_id"]) for chunk in planned_chunks]

    connection, driver = connect(database_url())

    existing_documents: list[ExistingDocument] = []
    existing_chunk_ids: list[str] = []
    document_count_before = 0
    chunk_count_before = 0
    transaction_read_only = False

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SHOW transaction_read_only")

            transaction_read_only = str(cursor.fetchone()[0]).lower() == "on"

            if not transaction_read_only:
                raise RuntimeError("Transacao nao esta em READ ONLY.")

            cursor.execute(
                """
                SELECT
                    id,
                    nome_logico,
                    content_hash,
                    versao,
                    ativo
                FROM public.documentos_upload_rag
                WHERE nome_logico = ANY(%s)
                   OR content_hash = ANY(%s)
                ORDER BY id
                """,
                (logical_names, content_hashes),
            )

            existing_documents = [
                ExistingDocument(
                    database_id=int(row[0]),
                    nome_logico=(str(row[1]) if row[1] is not None else None),
                    content_hash=(str(row[2]) if row[2] is not None else None),
                    versao=(int(row[3]) if row[3] is not None else None),
                    ativo=(bool(row[4]) if row[4] is not None else None),
                )
                for row in cursor.fetchall()
            ]

            cursor.execute(
                """
                SELECT chunk_id
                FROM public.chunks_embeddings_rag
                WHERE chunk_id = ANY(%s)
                ORDER BY chunk_id
                """,
                (chunk_ids,),
            )

            existing_chunk_ids = [str(row[0]) for row in cursor.fetchall()]

            cursor.execute("SELECT COUNT(*) FROM public.documentos_upload_rag")
            document_count_before = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM public.chunks_embeddings_rag")
            chunk_count_before = int(cursor.fetchone()[0])

            cursor.execute("ROLLBACK")

    finally:
        connection.close()

    existing_by_logical_name = {
        document.nome_logico: document
        for document in existing_documents
        if document.nome_logico is not None
    }

    existing_by_hash: dict[str, list[ExistingDocument]] = {}

    for document in existing_documents:
        if document.content_hash is None:
            continue

        existing_by_hash.setdefault(
            document.content_hash,
            [],
        ).append(document)

    decisions = analyze_documents(
        planned_documents,
        existing_by_logical_name,
        existing_by_hash,
    )

    summary = summarize_decisions(
        decisions,
        planned_chunk_count=len(planned_chunks),
        existing_chunk_ids=existing_chunk_ids,
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "database_driver": driver,
        "transaction_read_only": transaction_read_only,
        "document_count_before": document_count_before,
        "chunk_count_before": chunk_count_before,
        "existing_document_match_count": len(existing_documents),
        "existing_chunk_id_count": len(existing_chunk_ids),
        "existing_documents": [document.as_dict() for document in existing_documents],
        "existing_chunk_ids": existing_chunk_ids,
        "decisions": [decision.as_dict() for decision in decisions],
        **summary,
        "database_connected": True,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }

    args.output.mkdir(parents=True, exist_ok=True)

    report_path = args.output / "financial_neon_preflight_report.json"

    report_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"DATABASE_DRIVER={driver}")
    print("DATABASE_CONNECTED=True")
    print(f"TRANSACTION_READ_ONLY={transaction_read_only}")
    print(f"DOCUMENT_COUNT_BEFORE={document_count_before}")
    print(f"CHUNK_COUNT_BEFORE={chunk_count_before}")
    print(f"PLANNED_DOCUMENT_COUNT={summary['planned_document_count']}")
    print(f"PLANNED_CHUNK_COUNT={summary['planned_chunk_count']}")
    print(f"EXISTING_DOCUMENT_MATCH_COUNT={len(existing_documents)}")
    print(f"EXISTING_CHUNK_ID_COUNT={summary['existing_chunk_id_count']}")
    print(f"BLOCKING_DOCUMENT_COUNT={summary['blocking_document_count']}")

    for action, count in summary["action_counts"].items():
        print(f"ACTION_COUNT={action}|COUNT={count}")

    for decision in decisions:
        print(
            "DOCUMENT_DECISION="
            f"{decision.nome_logico}"
            f"|ACTION={decision.action}"
            f"|DATABASE_ID={decision.existing_database_id}"
            f"|REASON={decision.reason}"
        )

    print(f"PREFLIGHT_PASSED={summary['preflight_passed']}")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print("GEMINI_USED=False")
    print(f"REPORT={report_path}")

    return 0 if summary["preflight_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

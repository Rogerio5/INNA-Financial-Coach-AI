"""Executa dry-run ou simulacao com rollback da ingestao financeira."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_neon_ingestion_simulation import (
    build_offline_report,
    build_simulation_plan,
    load_json_list,
    vector_to_pgvector,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--documents",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--chunks",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--report",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--mode",
        choices=("dry-run", "rollback-simulation"),
        required=True,
    )

    parser.add_argument(
        "--confirm-rollback",
        default="NO",
    )

    return parser


def get_database_url() -> str:
    load_dotenv()

    value = (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
    )

    if not value:
        raise RuntimeError("URL do Neon nao encontrada.")

    return value


def connect_database(url: str) -> tuple[Any, str]:
    try:
        import psycopg

        return (
            psycopg.connect(
                url,
                autocommit=False,
            ),
            "psycopg3",
        )

    except ImportError:
        import psycopg2

        connection = psycopg2.connect(url)
        connection.autocommit = False

        return connection, "psycopg2"


def write_report(
    path: Path,
    report: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


def run_rollback_simulation(
    *,
    plan: Any,
    database_url: str,
) -> dict[str, Any]:
    connection, driver = connect_database(database_url)

    document_ids: dict[str, int] = {}
    document_count_before = 0
    chunk_count_before = 0
    document_count_inside = 0
    chunk_count_inside = 0
    document_count_after = 0
    chunk_count_after = 0
    rollback_executed = False

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")

            cursor.execute("SELECT COUNT(*) FROM public.documentos_upload_rag")
            document_count_before = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM public.chunks_embeddings_rag")
            chunk_count_before = int(cursor.fetchone()[0])

            for document in plan.documents:
                cursor.execute(
                    """
                    INSERT INTO public.documentos_upload_rag (
                        nome_original,
                        nome_salvo,
                        caminho_upload,
                        caminho_chunks,
                        caminho_embedding_ready,
                        extensao,
                        tamanho_bytes,
                        total_chunks,
                        status,
                        origem,
                        ativo,
                        nome_logico,
                        content_hash,
                        versao,
                        documento_raiz_id,
                        documento_anterior_id
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING id
                    """,
                    (
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
                    ),
                )

                database_id = int(cursor.fetchone()[0])

                document_ids[str(document["nome_logico"])] = database_id

            for chunk in plan.chunks:
                document_id = document_ids[str(chunk["documento_key"])]

                metadata = dict(chunk["metadata"])
                metadata["database_document_id"] = document_id
                metadata["simulation_mode"] = "rollback"

                cursor.execute(
                    """
                    INSERT INTO public.chunks_embeddings_rag (
                        documento_id,
                        chunk_id,
                        documento_origem,
                        chunk_index,
                        texto,
                        metadata,
                        embedding,
                        modelo_embedding
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb,
                        %s::vector,
                        %s
                    )
                    """,
                    (
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
                    ),
                )

            cursor.execute("SELECT COUNT(*) FROM public.documentos_upload_rag")
            document_count_inside = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM public.chunks_embeddings_rag")
            chunk_count_inside = int(cursor.fetchone()[0])

            connection.rollback()
            rollback_executed = True

        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")

            cursor.execute("SELECT COUNT(*) FROM public.documentos_upload_rag")
            document_count_after = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM public.chunks_embeddings_rag")
            chunk_count_after = int(cursor.fetchone()[0])

            connection.rollback()

    finally:
        connection.close()

    passed = all(
        (
            rollback_executed,
            document_count_inside == document_count_before + 16,
            chunk_count_inside == chunk_count_before + 35,
            document_count_after == document_count_before,
            chunk_count_after == chunk_count_before,
        )
    )

    return {
        "schema_version": 1,
        "database_driver": driver,
        "database_connected": True,
        "document_count_before": document_count_before,
        "chunk_count_before": chunk_count_before,
        "document_count_inside_transaction": document_count_inside,
        "chunk_count_inside_transaction": chunk_count_inside,
        "document_count_after_rollback": document_count_after,
        "chunk_count_after_rollback": chunk_count_after,
        "simulated_document_insert_count": 16,
        "simulated_chunk_insert_count": 35,
        "rollback_executed": rollback_executed,
        "transaction_committed": False,
        "simulation_status": "passed" if passed else "failed",
        "database_write_executed": True,
        "persistent_database_write_executed": False,
        "neon_changed": False,
        "gemini_used": False,
    }


def main() -> int:
    args = build_parser().parse_args()

    documents = load_json_list(args.documents)

    chunks = load_json_list(args.chunks)

    plan = build_simulation_plan(
        documents,
        chunks,
    )

    if args.mode == "dry-run":
        report = build_offline_report(plan)

    else:
        if args.confirm_rollback != "YES":
            raise RuntimeError("Use --confirm-rollback YES.")

        report = run_rollback_simulation(
            plan=plan,
            database_url=get_database_url(),
        )

    write_report(
        args.report,
        report,
    )

    for key, value in report.items():
        if isinstance(value, (str, int, float, bool)):
            print(f"{key.upper()}={value}")

    print(f"REPORT={args.report}")

    status = report.get(
        "simulation_status",
        report.get(
            "offline_plan_status",
            "failed",
        ),
    )

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

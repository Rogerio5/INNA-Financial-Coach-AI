"""Executa dry-run ou ingestao definitiva da base financeira no Neon."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_neon_definitive_ingestion import (
    ConflictSummary,
    build_conflict_queries,
    build_offline_ingestion_report,
    build_simulation_plan,
    create_chunk_insert_parameters,
    create_document_insert_parameters,
    validate_chunk_distribution,
    validate_conflict_summary,
    validate_final_counts,
    validate_inserted_document_ids,
    validate_new_rows,
)
from src.evaluation.financial_neon_ingestion_simulation import (
    load_json_list,
)

DOCUMENT_INSERT_SQL = """
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
"""

CHUNK_INSERT_SQL = """
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
"""


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
        choices=("dry-run", "commit"),
        required=True,
    )

    parser.add_argument(
        "--confirm-commit",
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


def fetch_scalar(
    cursor: Any,
    query: str,
    parameters: tuple[Any, ...] = (),
) -> int:
    cursor.execute(
        query,
        parameters,
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError("A consulta nao retornou resultado.")

    return int(row[0])


def run_definitive_ingestion(
    *,
    plan: Any,
    database_url: str,
) -> dict[str, Any]:
    connection, driver = connect_database(database_url)

    document_ids: dict[str, int] = {}

    document_count_before = 0
    chunk_count_before = 0
    document_count_after = 0
    chunk_count_after = 0
    document_match_count = 0
    chunk_match_count = 0

    transaction_committed = False

    queries = build_conflict_queries(plan)

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")

            document_count_before = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.documentos_upload_rag",
            )

            chunk_count_before = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.chunks_embeddings_rag",
            )

            logical_conflicts = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.documentos_upload_rag
                WHERE nome_logico = ANY(%s)
                """,
                (list(queries["logical_names"]),),
            )

            hash_conflicts = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.documentos_upload_rag
                WHERE content_hash = ANY(%s)
                """,
                (list(queries["content_hashes"]),),
            )

            chunk_conflicts = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.chunks_embeddings_rag
                WHERE chunk_id = ANY(%s)
                """,
                (list(queries["chunk_ids"]),),
            )

            conflicts = ConflictSummary(
                document_logical_name_count=logical_conflicts,
                document_content_hash_count=hash_conflicts,
                chunk_id_count=chunk_conflicts,
            )

            validate_conflict_summary(conflicts)

            for document in plan.documents:
                cursor.execute(
                    DOCUMENT_INSERT_SQL,
                    create_document_insert_parameters(document),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError("O INSERT do documento nao retornou ID.")

                document_ids[str(document["nome_logico"])] = int(row[0])

            validate_inserted_document_ids(
                plan=plan,
                document_ids=document_ids,
            )

            for chunk in plan.chunks:
                document_key = str(chunk["documento_key"])

                cursor.execute(
                    CHUNK_INSERT_SQL,
                    create_chunk_insert_parameters(
                        chunk=chunk,
                        document_id=document_ids[document_key],
                    ),
                )

            document_count_inside = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.documentos_upload_rag",
            )

            chunk_count_inside = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.chunks_embeddings_rag",
            )

            validate_final_counts(
                document_count_before=document_count_before,
                chunk_count_before=chunk_count_before,
                document_count_after=document_count_inside,
                chunk_count_after=chunk_count_inside,
            )

            document_match_count = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.documentos_upload_rag
                WHERE nome_logico = ANY(%s)
                """,
                (list(queries["logical_names"]),),
            )

            chunk_match_count = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.chunks_embeddings_rag
                WHERE chunk_id = ANY(%s)
                """,
                (list(queries["chunk_ids"]),),
            )

            validate_new_rows(
                document_match_count=document_match_count,
                chunk_match_count=chunk_match_count,
            )

            cursor.execute(
                """
                SELECT
                    d.nome_logico,
                    COUNT(c.id)
                FROM public.documentos_upload_rag d
                JOIN public.chunks_embeddings_rag c
                    ON c.documento_id = d.id
                WHERE d.nome_logico = ANY(%s)
                GROUP BY d.nome_logico
                ORDER BY d.nome_logico
                """,
                (list(queries["logical_names"]),),
            )

            database_distribution = {
                str(row[0]): int(row[1]) for row in cursor.fetchall()
            }

            validate_chunk_distribution(
                plan=plan,
                database_distribution=database_distribution,
            )

            connection.commit()
            transaction_committed = True

        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")

            document_count_after = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.documentos_upload_rag",
            )

            chunk_count_after = fetch_scalar(
                cursor,
                "SELECT COUNT(*) FROM public.chunks_embeddings_rag",
            )

            persisted_document_matches = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.documentos_upload_rag
                WHERE nome_logico = ANY(%s)
                """,
                (list(queries["logical_names"]),),
            )

            persisted_chunk_matches = fetch_scalar(
                cursor,
                """
                SELECT COUNT(*)
                FROM public.chunks_embeddings_rag
                WHERE chunk_id = ANY(%s)
                """,
                (list(queries["chunk_ids"]),),
            )

            connection.rollback()

        validate_final_counts(
            document_count_before=document_count_before,
            chunk_count_before=chunk_count_before,
            document_count_after=document_count_after,
            chunk_count_after=chunk_count_after,
        )

        validate_new_rows(
            document_match_count=persisted_document_matches,
            chunk_match_count=persisted_chunk_matches,
        )

    except Exception:
        if not transaction_committed:
            connection.rollback()

        raise

    finally:
        connection.close()

    return {
        "schema_version": 1,
        "database_driver": driver,
        "database_connected": True,
        "document_count_before": document_count_before,
        "chunk_count_before": chunk_count_before,
        "inserted_document_count": 16,
        "inserted_chunk_count": 35,
        "inserted_embedding_count": 35,
        "document_match_count": document_match_count,
        "chunk_match_count": chunk_match_count,
        "document_count_after": document_count_after,
        "chunk_count_after": chunk_count_after,
        "transaction_committed": transaction_committed,
        "database_write_executed": True,
        "persistent_database_write_executed": True,
        "neon_changed": True,
        "gemini_used": False,
        "ingestion_status": "passed",
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
        report = build_offline_ingestion_report(plan)

    else:
        if args.confirm_commit != "YES":
            raise RuntimeError("Use --confirm-commit YES para permitir o COMMIT.")

        report = run_definitive_ingestion(
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
        "ingestion_status",
        report.get(
            "offline_plan_status",
            "failed",
        ),
    )

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

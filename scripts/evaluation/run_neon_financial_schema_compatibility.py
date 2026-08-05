"""Compara os payloads financeiros com o esquema real do Neon.

A conexão utiliza uma transação explicitamente somente leitura.
Nenhuma escrita, embedding ou chamada ao Gemini é executada.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

DOCUMENT_TABLE = "documentos_upload_rag"
CHUNK_TABLE = "chunks_embeddings_rag"
DATABASE_SCHEMA = "public"


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
        "--output",
        required=True,
        type=Path,
    )

    return parser


def load_json_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(payload, list):
        raise ValueError(f"O arquivo deve conter uma lista JSON: {path}")

    return [dict(item) for item in payload]


def get_database_url() -> str:
    load_dotenv()

    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
    )

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL, NEON_DATABASE_URL ou POSTGRES_URL nao foi encontrada."
        )

    return database_url


def connect_database(database_url: str) -> tuple[Any, str]:
    try:
        import psycopg

        connection = psycopg.connect(
            database_url,
            autocommit=False,
        )

        return connection, "psycopg3"

    except ImportError:
        import psycopg2

        connection = psycopg2.connect(database_url)

        connection.autocommit = False

        return connection, "psycopg2"


def fetch_columns(
    cursor: Any,
    *,
    table_name: str,
) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT
            ordinal_position,
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position
        """,
        (
            DATABASE_SCHEMA,
            table_name,
        ),
    )

    rows = cursor.fetchall()

    return [
        {
            "ordinal_position": row[0],
            "column_name": row[1],
            "data_type": row[2],
            "udt_name": row[3],
            "is_nullable": row[4],
            "column_default": row[5],
            "character_maximum_length": row[6],
        }
        for row in rows
    ]


def fetch_constraints(
    cursor: Any,
    *,
    table_name: str,
) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM information_schema.table_constraints AS tc
        LEFT JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage AS ccu
          ON tc.constraint_name = ccu.constraint_name
         AND tc.table_schema = ccu.table_schema
        WHERE tc.table_schema = %s
          AND tc.table_name = %s
        ORDER BY
            tc.constraint_type,
            tc.constraint_name,
            kcu.ordinal_position
        """,
        (
            DATABASE_SCHEMA,
            table_name,
        ),
    )

    rows = cursor.fetchall()

    return [
        {
            "constraint_name": row[0],
            "constraint_type": row[1],
            "column_name": row[2],
            "referenced_table": row[3],
            "referenced_column": row[4],
        }
        for row in rows
    ]


def fetch_indexes(
    cursor: Any,
    *,
    table_name: str,
) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = %s
          AND tablename = %s
        ORDER BY indexname
        """,
        (
            DATABASE_SCHEMA,
            table_name,
        ),
    )

    return [
        {
            "index_name": row[0],
            "index_definition": row[1],
        }
        for row in cursor.fetchall()
    ]


def fetch_table_count(
    cursor: Any,
    *,
    table_name: str,
) -> int:
    allowed_tables = {
        DOCUMENT_TABLE,
        CHUNK_TABLE,
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Tabela nao permitida: {table_name}")

    cursor.execute(f'SELECT COUNT(*) FROM "{DATABASE_SCHEMA}"."{table_name}"')

    row = cursor.fetchone()

    return int(row[0])


def fetch_read_only_state(cursor: Any) -> bool:
    cursor.execute("SHOW transaction_read_only")

    row = cursor.fetchone()

    return str(row[0]).lower() == "on"


def column_names(
    columns: Sequence[Mapping[str, Any]],
) -> set[str]:
    return {str(column["column_name"]) for column in columns}


def required_insert_columns(
    columns: Sequence[Mapping[str, Any]],
) -> list[str]:
    required: list[str] = []

    for column in columns:
        name = str(column["column_name"])

        nullable = str(column["is_nullable"]) == "YES"

        has_default = column["column_default"] is not None

        if not nullable and not has_default:
            required.append(name)

    return required


def analyze_payload_compatibility(
    *,
    payloads: Sequence[Mapping[str, Any]],
    columns: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    database_columns = column_names(columns)

    payload_columns: set[str] = set()

    for payload in payloads:
        payload_columns.update(str(key) for key in payload)

    required_columns = set(required_insert_columns(columns))

    missing_required_columns = sorted(required_columns - payload_columns)

    extra_payload_columns = sorted(payload_columns - database_columns)

    directly_compatible_columns = sorted(payload_columns & database_columns)

    return {
        "payload_count": len(payloads),
        "payload_columns": sorted(payload_columns),
        "database_columns": sorted(database_columns),
        "required_insert_columns": sorted(required_columns),
        "directly_compatible_columns": (directly_compatible_columns),
        "missing_required_columns": (missing_required_columns),
        "extra_payload_columns": (extra_payload_columns),
        "direct_insert_compatible": (
            not missing_required_columns and not extra_payload_columns
        ),
    }


def suggest_document_mapping(
    database_columns: set[str],
) -> dict[str, str | None]:
    candidates = {
        "document_key": ("id" if "id" in database_columns else None),
        "nome_arquivo": (
            "names"
            if "names" in database_columns
            else ("nome_arquivo" if "nome_arquivo" in database_columns else None)
        ),
        "tipo_documento": (
            "tipo_documento" if "tipo_documento" in database_columns else None
        ),
        "categoria": ("categoria" if "categoria" in database_columns else None),
        "idioma": ("idioma" if "idioma" in database_columns else None),
        "versao": ("versao" if "versao" in database_columns else None),
        "content_hash": (
            "content_hash" if "content_hash" in database_columns else None
        ),
        "total_chunks": (
            "total_chunks" if "total_chunks" in database_columns else None
        ),
        "ativo": ("ativo" if "ativo" in database_columns else None),
        "status": ("status" if "status" in database_columns else None),
    }

    return candidates


def suggest_chunk_mapping(
    database_columns: set[str],
) -> dict[str, str | None]:
    return {
        "chunk_id": ("chunk_id" if "chunk_id" in database_columns else None),
        "chunk_index": ("chunk_index" if "chunk_index" in database_columns else None),
        "documento_id": (
            "documento_id" if "documento_id" in database_columns else None
        ),
        "documento_origem": (
            "documento_origem" if "documento_origem" in database_columns else None
        ),
        "texto": ("texto" if "texto" in database_columns else None),
        "metadata": ("metadata" if "metadata" in database_columns else None),
        "modelo_embedding": (
            "modelo_embedding" if "modelo_embedding" in database_columns else None
        ),
        "embedding": ("embedding" if "embedding" in database_columns else None),
    }


def main() -> int:
    args = build_parser().parse_args()

    document_payloads = load_json_list(args.documents)

    chunk_payloads = load_json_list(args.chunks)

    database_url = get_database_url()

    connection, driver = connect_database(database_url)

    report: dict[str, Any]

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")

            transaction_read_only = fetch_read_only_state(cursor)

            if not transaction_read_only:
                raise RuntimeError("A transacao nao esta em modo READ ONLY.")

            document_columns = fetch_columns(
                cursor,
                table_name=DOCUMENT_TABLE,
            )

            chunk_columns = fetch_columns(
                cursor,
                table_name=CHUNK_TABLE,
            )

            if not document_columns:
                raise RuntimeError(f"Tabela nao encontrada: {DOCUMENT_TABLE}")

            if not chunk_columns:
                raise RuntimeError(f"Tabela nao encontrada: {CHUNK_TABLE}")

            document_constraints = fetch_constraints(
                cursor,
                table_name=DOCUMENT_TABLE,
            )

            chunk_constraints = fetch_constraints(
                cursor,
                table_name=CHUNK_TABLE,
            )

            document_indexes = fetch_indexes(
                cursor,
                table_name=DOCUMENT_TABLE,
            )

            chunk_indexes = fetch_indexes(
                cursor,
                table_name=CHUNK_TABLE,
            )

            document_row_count = fetch_table_count(
                cursor,
                table_name=DOCUMENT_TABLE,
            )

            chunk_row_count = fetch_table_count(
                cursor,
                table_name=CHUNK_TABLE,
            )

            document_compatibility = analyze_payload_compatibility(
                payloads=document_payloads,
                columns=document_columns,
            )

            chunk_compatibility = analyze_payload_compatibility(
                payloads=chunk_payloads,
                columns=chunk_columns,
            )

            document_database_columns = column_names(document_columns)

            chunk_database_columns = column_names(chunk_columns)

            document_mapping = suggest_document_mapping(document_database_columns)

            chunk_mapping = suggest_chunk_mapping(chunk_database_columns)

            unresolved_document_fields = sorted(
                field for field, target in document_mapping.items() if target is None
            )

            unresolved_chunk_fields = sorted(
                field for field, target in chunk_mapping.items() if target is None
            )

            report = {
                "schema_version": 1,
                "generated_at": datetime.now(UTC).isoformat(),
                "database_driver": driver,
                "database_schema": DATABASE_SCHEMA,
                "transaction_read_only": (transaction_read_only),
                "document_table": (DOCUMENT_TABLE),
                "chunk_table": CHUNK_TABLE,
                "document_row_count_before": (document_row_count),
                "chunk_row_count_before": (chunk_row_count),
                "document_columns": (document_columns),
                "chunk_columns": chunk_columns,
                "document_constraints": (document_constraints),
                "chunk_constraints": (chunk_constraints),
                "document_indexes": (document_indexes),
                "chunk_indexes": chunk_indexes,
                "document_compatibility": (document_compatibility),
                "chunk_compatibility": (chunk_compatibility),
                "suggested_document_mapping": (document_mapping),
                "suggested_chunk_mapping": (chunk_mapping),
                "unresolved_document_fields": (unresolved_document_fields),
                "unresolved_chunk_fields": (unresolved_chunk_fields),
                "payload_document_count": len(document_payloads),
                "payload_chunk_count": len(chunk_payloads),
                "schema_inspection_passed": (
                    transaction_read_only
                    and len(document_payloads) == 16
                    and len(chunk_payloads) == 35
                    and not unresolved_chunk_fields
                ),
                "database_connected": True,
                "database_write_executed": False,
                "neon_changed": False,
                "gemini_used": False,
            }

            cursor.execute("ROLLBACK")

    finally:
        connection.close()

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = args.output / "neon_financial_schema_compatibility.json"

    report_path.write_text(
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

    print(f"DATABASE_DRIVER={report['database_driver']}")
    print(f"DATABASE_CONNECTED={report['database_connected']}")
    print(f"TRANSACTION_READ_ONLY={report['transaction_read_only']}")
    print(f"DOCUMENT_TABLE={report['document_table']}")
    print(f"CHUNK_TABLE={report['chunk_table']}")
    print(f"DOCUMENT_ROW_COUNT_BEFORE={report['document_row_count_before']}")
    print(f"CHUNK_ROW_COUNT_BEFORE={report['chunk_row_count_before']}")
    print(f"DOCUMENT_COLUMN_COUNT={len(report['document_columns'])}")
    print(f"CHUNK_COLUMN_COUNT={len(report['chunk_columns'])}")
    print(f"PAYLOAD_DOCUMENT_COUNT={report['payload_document_count']}")
    print(f"PAYLOAD_CHUNK_COUNT={report['payload_chunk_count']}")
    print(
        "DOCUMENT_DIRECT_INSERT_COMPATIBLE="
        f"{report['document_compatibility']['direct_insert_compatible']}"
    )
    print(
        "CHUNK_DIRECT_INSERT_COMPATIBLE="
        f"{report['chunk_compatibility']['direct_insert_compatible']}"
    )
    print(
        f"UNRESOLVED_DOCUMENT_FIELD_COUNT={len(report['unresolved_document_fields'])}"
    )
    print(f"UNRESOLVED_CHUNK_FIELD_COUNT={len(report['unresolved_chunk_fields'])}")

    for field in report["unresolved_document_fields"]:
        print(f"UNRESOLVED_DOCUMENT_FIELD={field}")

    for field in report["unresolved_chunk_fields"]:
        print(f"UNRESOLVED_CHUNK_FIELD={field}")

    print(f"SCHEMA_INSPECTION_PASSED={report['schema_inspection_passed']}")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print("GEMINI_USED=False")
    print(f"REPORT={report_path}")

    return 0 if report["schema_inspection_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

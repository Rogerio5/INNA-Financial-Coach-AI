"""Executa dry-run ou avaliacao vetorial real da base financeira."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_vector_retrieval_evaluation import (
    build_case_result,
    build_dry_run_report,
    build_evaluation_report,
    official_cases,
    validate_cases,
    validate_query_vector,
    vector_to_pgvector,
)

VECTOR_SEARCH_SQL = """
WITH query_vector AS (
    SELECT %s::vector AS embedding
)
SELECT
    c.chunk_id,
    d.nome_logico AS document_key,
    c.chunk_index,
    c.texto,
    1 - (c.embedding <=> query_vector.embedding) AS score
FROM public.chunks_embeddings_rag c
JOIN public.documentos_upload_rag d
    ON d.id = c.documento_id
CROSS JOIN query_vector
WHERE c.embedding IS NOT NULL
  AND (
      d.nome_logico LIKE 'inna-edu-%%'
      OR d.nome_logico LIKE 'inna-sec-%%'
  )
ORDER BY c.embedding <=> query_vector.embedding
LIMIT 4
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--report",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=("dry-run", "execute"),
    )

    parser.add_argument(
        "--confirm-calls",
        type=int,
        default=0,
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


def get_api_key() -> str:
    load_dotenv()

    value = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not value:
        raise RuntimeError("Chave Gemini nao encontrada.")

    return value


def connect_database(
    database_url: str,
) -> tuple[Any, str]:
    try:
        import psycopg

        return (
            psycopg.connect(
                database_url,
                autocommit=False,
            ),
            "psycopg3",
        )

    except ImportError:
        import psycopg2

        connection = psycopg2.connect(database_url)
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
        )
        + "\n",
        encoding="utf-8",
    )


def execute_evaluation() -> dict[str, Any]:
    from google import genai
    from google.genai import types

    cases = official_cases()
    validate_cases(cases)

    client = genai.Client(api_key=get_api_key())

    connection, driver = connect_database(get_database_url())

    results = []
    call_count = 0

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")

            for case in cases:
                response = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=case.question,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_QUERY",
                        output_dimensionality=3072,
                    ),
                )

                call_count += 1

                embeddings = getattr(
                    response,
                    "embeddings",
                    None,
                )

                if not embeddings:
                    raise RuntimeError("Resposta Gemini sem embedding.")

                values = getattr(
                    embeddings[0],
                    "values",
                    None,
                )

                if values is None:
                    raise RuntimeError("Resposta Gemini sem vetor.")

                vector = validate_query_vector(values)

                cursor.execute(
                    VECTOR_SEARCH_SQL,
                    (vector_to_pgvector(vector),),
                )

                rows = [
                    {
                        "chunk_id": row[0],
                        "document_key": row[1],
                        "chunk_index": row[2],
                        "texto": row[3],
                        "score": row[4],
                    }
                    for row in cursor.fetchall()
                ]

                result = build_case_result(
                    case=case,
                    rows=rows,
                )

                results.append(result)

                print(
                    "CASE_RESULT="
                    f"{case.case_id}"
                    f"|EXPECTED={case.expected_document_key}"
                    f"|TOP1={result.top1_document_key}"
                    f"|TOP1_PASSED={result.top1_passed}"
                    f"|TOP4_FOUND="
                    f"{result.expected_document_found_in_top_k}"
                )

            connection.rollback()

    finally:
        connection.close()

        close_method = getattr(
            client,
            "close",
            None,
        )

        if callable(close_method):
            close_method()

    report = build_evaluation_report(results)

    report["database_driver"] = driver
    report["gemini_call_count"] = call_count

    return report


def main() -> int:
    args = build_parser().parse_args()

    cases = official_cases()

    if args.mode == "dry-run":
        report = build_dry_run_report(cases)

    else:
        if args.confirm_calls != 5:
            raise RuntimeError("Use --confirm-calls 5.")

        report = execute_evaluation()

    write_report(
        args.report,
        report,
    )

    for key, value in report.items():
        if isinstance(value, (str, int, float, bool)):
            print(f"{key.upper()}={value}")

    print(f"REPORT={args.report}")

    status = report.get(
        "evaluation_status",
        report.get(
            "dry_run_status",
            "failed",
        ),
    )

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Executa uma unica chamada Gemini para validar embedding."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_gemini_embedding_pilot import (
    analyze_embedding,
    choose_database_dimension,
    extract_embedding_values,
    select_pilot_chunk,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

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
    parser.add_argument(
        "--confirm-one-call",
        required=True,
    )

    return parser


def load_chunks(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, list):
        raise ValueError("O plano de chunks deve ser uma lista JSON.")

    return [dict(item) for item in payload]


def get_database_url() -> str:
    value = (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
    )

    if not value:
        raise RuntimeError("URL do Neon nao encontrada.")

    return value


def get_api_key() -> str:
    value = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not value:
        raise RuntimeError("Chave Gemini nao encontrada.")

    return value


def connect_database(url: str) -> tuple[Any, str]:
    try:
        import psycopg

        connection = psycopg.connect(
            url,
            autocommit=False,
        )

        return connection, "psycopg3"

    except ImportError:
        import psycopg2

        connection = psycopg2.connect(url)
        connection.autocommit = False

        return connection, "psycopg2"


def read_embedding_dimensions(
    url: str,
) -> tuple[list[int], str]:
    connection, driver = connect_database(url)

    try:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SHOW transaction_read_only")

            read_only = str(cursor.fetchone()[0]).lower() == "on"

            if not read_only:
                raise RuntimeError("A transacao nao esta READ ONLY.")

            cursor.execute(
                """
                SELECT DISTINCT vector_dims(embedding)
                FROM public.chunks_embeddings_rag
                WHERE embedding IS NOT NULL
                ORDER BY vector_dims(embedding)
                """
            )

            dimensions = [int(row[0]) for row in cursor.fetchall()]

            cursor.execute("ROLLBACK")

    finally:
        connection.close()

    return dimensions, driver


def main() -> int:
    args = build_parser().parse_args()

    if args.confirm_one_call != "YES":
        raise RuntimeError("Use --confirm-one-call YES.")

    load_dotenv()

    chunks = load_chunks(args.chunks)

    dimensions, driver = read_embedding_dimensions(get_database_url())

    expected_dimension = choose_database_dimension(dimensions)

    pilot_input = select_pilot_chunk(
        chunks,
        expected_dimension=expected_dimension,
    )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=get_api_key())

    call_count = 0
    started = time.perf_counter()

    try:
        call_count = 1

        response = client.models.embed_content(
            model=pilot_input.model,
            contents=pilot_input.text,
            config=types.EmbedContentConfig(
                task_type=pilot_input.task_type,
                title=pilot_input.document_title,
                output_dimensionality=expected_dimension,
            ),
        )

    finally:
        close_method = getattr(client, "close", None)

        if callable(close_method):
            close_method()

    latency_ms = (time.perf_counter() - started) * 1000.0

    vector = extract_embedding_values(response)

    result = analyze_embedding(
        expected_dimension=expected_dimension,
        vector=vector,
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "database_driver": driver,
        "database_connected": True,
        "transaction_read_only": True,
        "database_dimensions_found": dimensions,
        "pilot_input": pilot_input.as_dict(),
        "embedding_result": result.as_dict(),
        "gemini_call_count": call_count,
        "latency_ms": round(latency_ms, 3),
        "pilot_passed": result.passed,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": True,
    }

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = args.output / "financial_gemini_embedding_pilot.json"

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
    print("TRANSACTION_READ_ONLY=True")
    print("DATABASE_DIMENSIONS_FOUND=" + ",".join(str(item) for item in dimensions))
    print(f"PILOT_CHUNK_ID={pilot_input.chunk_id}")
    print(f"PILOT_DOCUMENT_KEY={pilot_input.documento_key}")
    print(f"EMBEDDING_MODEL={pilot_input.model}")
    print(f"TASK_TYPE={pilot_input.task_type}")
    print(f"EXPECTED_DIMENSION={result.expected_dimension}")
    print(f"ACTUAL_DIMENSION={result.actual_dimension}")
    print(f"FINITE_VALUE_COUNT={result.finite_value_count}")
    print(f"ZERO_VALUE_COUNT={result.zero_value_count}")
    print(f"L2_NORM={result.l2_norm:.9f}")
    print(f"LATENCY_MS={latency_ms:.3f}")
    print(f"GEMINI_CALL_COUNT={call_count}")
    print(f"PILOT_PASSED={result.passed}")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print("GEMINI_USED=True")
    print(f"REPORT={report_path}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Executa o adaptador offline para o esquema real do Neon."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.financial_neon_schema_adapter import (
    build_neon_chunk_payloads,
    build_neon_document_payloads,
    create_adapter_report,
    load_json_list,
    write_adapter_outputs,
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
        "--output",
        required=True,
        type=Path,
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    source_documents = load_json_list(args.documents)

    source_chunks = load_json_list(args.chunks)

    adapted_documents = build_neon_document_payloads(source_documents)

    adapted_chunks = build_neon_chunk_payloads(source_chunks)

    report = create_adapter_report(
        source_documents=source_documents,
        source_chunks=source_chunks,
        adapted_documents=adapted_documents,
        adapted_chunks=adapted_chunks,
    )

    outputs = write_adapter_outputs(
        output_directory=args.output,
        documents=adapted_documents,
        chunks=adapted_chunks,
        report=report,
    )

    print(f"SOURCE_DOCUMENT_COUNT={report.source_document_count}")
    print(f"SOURCE_CHUNK_COUNT={report.source_chunk_count}")
    print(f"ADAPTED_DOCUMENT_COUNT={report.adapted_document_count}")
    print(f"ADAPTED_CHUNK_COUNT={report.adapted_chunk_count}")
    print(f"DUPLICATE_DOCUMENT_KEY_COUNT={report.duplicate_document_key_count}")
    print(f"DUPLICATE_CHUNK_ID_COUNT={report.duplicate_chunk_id_count}")
    print(f"INVALID_DOCUMENT_COUNT={report.invalid_document_count}")
    print(f"INVALID_CHUNK_COUNT={report.invalid_chunk_count}")
    print(f"ADAPTER_STATUS={report.status}")
    print(f"DATABASE_CONNECTED={report.database_connected}")
    print(f"DATABASE_WRITE_EXECUTED={report.database_write_executed}")
    print(f"NEON_CHANGED={report.neon_changed}")
    print(f"GEMINI_USED={report.gemini_used}")
    print(f"DOCUMENT_INSERT_PLAN={outputs['documents']}")
    print(f"CHUNK_INSERT_PLAN={outputs['chunks']}")
    print(f"ADAPTER_REPORT={outputs['report']}")

    for document in adapted_documents:
        print(
            "DOCUMENT="
            f"{document.nome_logico}"
            f"|FILE={document.nome_salvo}"
            f"|CHUNKS={document.total_chunks}"
            f"|VERSION={document.versao}"
            f"|ORIGIN={document.origem}"
        )

    return 0 if report.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

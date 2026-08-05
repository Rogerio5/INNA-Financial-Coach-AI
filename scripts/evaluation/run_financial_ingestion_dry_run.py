"""Executa o mapeamento offline da ingestao financeira."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.financial_ingestion_dry_run import (
    build_chunk_payloads,
    build_document_payloads,
    create_dry_run_report,
    load_source_chunks,
    write_dry_run_outputs,
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

    return parser


def main() -> int:
    args = build_parser().parse_args()

    source_chunks = load_source_chunks(args.chunks)

    document_payloads = build_document_payloads(source_chunks)

    chunk_payloads = build_chunk_payloads(source_chunks)

    report = create_dry_run_report(
        source_chunks,
        document_payloads,
        chunk_payloads,
    )

    outputs = write_dry_run_outputs(
        output_directory=args.output,
        report=report,
        document_payloads=(document_payloads),
        chunk_payloads=chunk_payloads,
    )

    print(f"SOURCE_CHUNK_COUNT={report.source_chunk_count}")
    print(f"MAPPED_CHUNK_COUNT={report.mapped_chunk_count}")
    print(f"MAPPED_DOCUMENT_COUNT={report.mapped_document_count}")
    print(f"DUPLICATE_CHUNK_ID_COUNT={report.duplicate_chunk_id_count}")
    print(f"DUPLICATE_CHUNK_HASH_COUNT={report.duplicate_chunk_hash_count}")
    print(f"DUPLICATE_DOCUMENT_KEY_COUNT={report.duplicate_document_key_count}")
    print(f"INVALID_CHUNK_COUNT={report.invalid_chunk_count}")
    print(f"INVALID_DOCUMENT_COUNT={report.invalid_document_count}")
    print(f"DRY_RUN_STATUS={report.status}")
    print(f"DATABASE_CONNECTED={report.database_connected}")
    print(f"DATABASE_WRITE_EXECUTED={report.database_write_executed}")
    print(f"NEON_CHANGED={report.neon_changed}")
    print(f"GEMINI_USED={report.gemini_used}")
    print(f"DOCUMENT_PAYLOADS={outputs['documents']}")
    print(f"CHUNK_PAYLOADS={outputs['chunks']}")
    print(f"DRY_RUN_REPORT={outputs['report']}")

    return 0 if report.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

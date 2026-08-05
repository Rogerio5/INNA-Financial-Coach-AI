"""Consolida os 35 embeddings financeiros em arquivo offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.evaluation.financial_embedding_consolidation import (
    build_consolidation_report,
    consolidate_embeddings,
    load_batch_embeddings,
    load_pilot_embedding,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--chunks", required=True, type=Path)
    parser.add_argument("--pilot-report", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)

    return parser


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()

    chunks = load_json(args.chunks)
    pilot_report = load_json(args.pilot_report)
    checkpoint = load_json(args.checkpoint)

    if not isinstance(chunks, list):
        raise ValueError("O plano de chunks deve ser uma lista.")

    if not isinstance(pilot_report, dict):
        raise ValueError("O relatorio piloto deve ser um objeto.")

    if not isinstance(checkpoint, dict):
        raise ValueError("O checkpoint deve ser um objeto.")

    pilot_chunk_id, pilot_vector = load_pilot_embedding(pilot_report)

    batch_embeddings = load_batch_embeddings(checkpoint)

    consolidated = consolidate_embeddings(
        chunks=chunks,
        pilot_chunk_id=pilot_chunk_id,
        pilot_vector=pilot_vector,
        batch_embeddings=batch_embeddings,
    )

    report = build_consolidation_report(consolidated)

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    consolidated_path = args.output / "financial_chunks_with_embeddings.json"

    report_path = args.output / "financial_embedding_consolidation_report.json"

    consolidated_path.write_text(
        json.dumps(
            [item.as_dict() for item in consolidated],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

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

    print(f"CONSOLIDATED_CHUNK_COUNT={report['consolidated_chunk_count']}")
    print(f"UNIQUE_CHUNK_ID_COUNT={report['unique_chunk_id_count']}")
    print(f"VALID_EMBEDDING_COUNT={report['valid_embedding_count']}")
    print(f"INVALID_EMBEDDING_COUNT={report['invalid_embedding_count']}")
    print(f"EMBEDDING_DIMENSION={report['embedding_dimension']}")
    print(f"EMBEDDING_MODEL={report['embedding_model']}")
    print(f"CONSOLIDATION_STATUS={report['consolidation_status']}")
    print("GEMINI_CALL_COUNT=0")
    print("DATABASE_CONNECTED=False")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print("GEMINI_USED=False")
    print(f"CONSOLIDATED_FILE={consolidated_path}")
    print(f"REPORT={report_path}")

    return 0 if report["consolidation_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

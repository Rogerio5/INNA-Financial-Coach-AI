"""Gera o plano offline dos 34 embeddings restantes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.evaluation.financial_embedding_batch_plan import (
    build_batch_plan_report,
    build_pending_embeddings,
    load_completed_pilot,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--chunks",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--pilot-report",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    return parser


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )


def main() -> int:
    args = build_parser().parse_args()

    chunks = load_json(args.chunks)
    pilot_report = load_json(args.pilot_report)

    if not isinstance(chunks, list):
        raise ValueError("O plano de chunks deve ser uma lista.")

    if not isinstance(pilot_report, dict):
        raise ValueError("O relatorio piloto deve ser um objeto.")

    completed = load_completed_pilot(pilot_report)

    pending = build_pending_embeddings(
        chunks,
        completed,
    )

    report = build_batch_plan_report(
        chunks=chunks,
        completed=completed,
        pending=pending,
    )

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    completed_path = args.output / "completed_pilot_embedding.json"

    pending_path = args.output / "pending_embedding_requests.json"

    report_path = args.output / "financial_embedding_batch_plan_report.json"

    completed_path.write_text(
        json.dumps(
            completed.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    pending_path.write_text(
        json.dumps(
            [item.as_dict() for item in pending],
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

    print(f"SOURCE_CHUNK_COUNT={report['source_chunk_count']}")
    print(f"COMPLETED_EMBEDDING_COUNT={report['completed_embedding_count']}")
    print(f"PENDING_EMBEDDING_COUNT={report['pending_embedding_count']}")
    print(f"TOTAL_EMBEDDING_COUNT={report['total_embedding_count']}")
    print(f"PILOT_CHUNK_ID={report['pilot_chunk_id']}")
    print(f"EMBEDDING_MODEL={report['embedding_model']}")
    print(f"TASK_TYPE={report['task_type']}")
    print(f"EMBEDDING_DIMENSION={report['embedding_dimension']}")
    print(
        f"DUPLICATE_PENDING_CHUNK_ID_COUNT={report['duplicate_pending_chunk_id_count']}"
    )
    print(f"PLAN_STATUS={report['plan_status']}")
    print("GEMINI_CALL_COUNT=0")
    print("DATABASE_CONNECTED=False")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print("GEMINI_USED=False")
    print(f"COMPLETED_PILOT={completed_path}")
    print(f"PENDING_REQUESTS={pending_path}")
    print(f"REPORT={report_path}")

    return 0 if report["plan_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

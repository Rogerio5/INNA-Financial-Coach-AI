"""Executa dry-run ou geracao controlada dos embeddings financeiros."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.evaluation.financial_embedding_batch_generator import (
    build_dry_run_report,
    create_completed_embedding,
    determine_pending_requests,
    load_checkpoint,
    load_requests,
    write_checkpoint,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--requests",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--checkpoint",
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
        choices=(
            "dry-run",
            "execute",
        ),
        required=True,
    )

    parser.add_argument(
        "--confirm-calls",
        type=int,
        default=0,
    )

    return parser


def get_api_key() -> str:
    value = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not value:
        raise RuntimeError("Chave Gemini nao encontrada.")

    return value


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


def execute_embeddings(
    *,
    requests: tuple[Any, ...],
    checkpoint_path: Path,
    existing_completed: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    from google import genai
    from google.genai import types

    load_dotenv()

    completed = dict(existing_completed)

    client = genai.Client(api_key=get_api_key())

    call_count = 0
    started = time.perf_counter()

    try:
        for request in requests:
            response = client.models.embed_content(
                model=request.model,
                contents=request.text,
                config=types.EmbedContentConfig(
                    task_type=request.task_type,
                    title=request.document_title,
                    output_dimensionality=(request.output_dimension),
                ),
            )

            call_count += 1

            embeddings = getattr(
                response,
                "embeddings",
                None,
            )

            if not embeddings:
                raise RuntimeError("Resposta sem embeddings: " + request.chunk_id)

            values = getattr(
                embeddings[0],
                "values",
                None,
            )

            if values is None:
                raise RuntimeError("Resposta sem vetor: " + request.chunk_id)

            completed_embedding = create_completed_embedding(
                request,
                values,
            )

            completed[request.chunk_id] = completed_embedding

            write_checkpoint(
                checkpoint_path,
                completed,
            )

            print(
                "EMBEDDING_COMPLETED="
                f"{request.sequence}/34"
                f"|CHUNK_ID={request.chunk_id}"
                f"|DIMENSION={completed_embedding.dimension}"
            )

    finally:
        close_method = getattr(
            client,
            "close",
            None,
        )

        if callable(close_method):
            close_method()

    elapsed_ms = (time.perf_counter() - started) * 1000.0

    execution_summary = {
        "executed_call_count": call_count,
        "completed_count": len(completed),
        "elapsed_ms": round(
            elapsed_ms,
            3,
        ),
    }

    return execution_summary, call_count


def main() -> int:
    args = build_parser().parse_args()

    requests = load_requests(args.requests)

    completed = load_checkpoint(args.checkpoint)

    pending = determine_pending_requests(
        requests,
        completed,
    )

    dry_run_report = build_dry_run_report(
        requests=requests,
        completed=completed,
        pending=pending,
    )

    if args.mode == "dry-run":
        write_report(
            args.report,
            dry_run_report,
        )

        print(f"REQUEST_COUNT={dry_run_report['request_count']}")
        print(
            f"CHECKPOINT_COMPLETED_COUNT={dry_run_report['checkpoint_completed_count']}"
        )
        print(f"PENDING_COUNT={dry_run_report['pending_count']}")
        print(
            "PROJECTED_GEMINI_CALL_COUNT="
            f"{dry_run_report['projected_gemini_call_count']}"
        )
        print(f"EMBEDDING_DIMENSION={dry_run_report['embedding_dimension']}")
        print(f"DRY_RUN_STATUS={dry_run_report['dry_run_status']}")
        print("GEMINI_CALL_COUNT=0")
        print("DATABASE_CONNECTED=False")
        print("DATABASE_WRITE_EXECUTED=False")
        print("NEON_CHANGED=False")
        print("GEMINI_USED=False")
        print(f"REPORT={args.report}")

        return 0 if dry_run_report["dry_run_status"] == "passed" else 1

    if args.confirm_calls != len(pending):
        raise RuntimeError(
            "A confirmacao deve corresponder exatamente "
            "a quantidade de chamadas pendentes."
        )

    summary, call_count = execute_embeddings(
        requests=pending,
        checkpoint_path=args.checkpoint,
        existing_completed=completed,
    )

    final_completed = load_checkpoint(args.checkpoint)

    final_pending = determine_pending_requests(
        requests,
        final_completed,
    )

    report = {
        "schema_version": 1,
        "request_count": len(requests),
        "completed_before": len(completed),
        "pending_before": len(pending),
        "executed_call_count": call_count,
        "completed_after": len(final_completed),
        "pending_after": len(final_pending),
        "embedding_dimension": 3072,
        "elapsed_ms": summary["elapsed_ms"],
        "batch_status": (
            "passed"
            if len(final_completed) == 34 and len(final_pending) == 0
            else "failed"
        ),
        "database_connected": False,
        "database_write_executed": False,
        "neon_changed": False,
        "gemini_used": call_count > 0,
    }

    write_report(
        args.report,
        report,
    )

    print(f"COMPLETED_BEFORE={report['completed_before']}")
    print(f"PENDING_BEFORE={report['pending_before']}")
    print(f"EXECUTED_CALL_COUNT={report['executed_call_count']}")
    print(f"COMPLETED_AFTER={report['completed_after']}")
    print(f"PENDING_AFTER={report['pending_after']}")
    print(f"BATCH_STATUS={report['batch_status']}")
    print("DATABASE_CONNECTED=False")
    print("DATABASE_WRITE_EXECUTED=False")
    print("NEON_CHANGED=False")
    print(f"GEMINI_USED={report['gemini_used']}")
    print(f"CHECKPOINT={args.checkpoint}")
    print(f"REPORT={args.report}")

    return 0 if report["batch_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

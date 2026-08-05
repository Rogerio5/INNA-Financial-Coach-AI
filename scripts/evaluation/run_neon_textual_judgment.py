"""Executa o julgamento dos resultados textuais reais do Neon."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.retrieval_real_judgment import (
    evaluate_real_textual_report,
    write_real_evaluation_report,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Avalia resultados reais de retrieval textual "
            "sem consultar Neon e sem usar Gemini."
        )
    )
    parser.add_argument(
        "--source-report",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--judgments",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    return parser


def main() -> int:
    args = _parser().parse_args()

    report = evaluate_real_textual_report(
        source_report_path=args.source_report,
        judgment_path=args.judgments,
    )

    output_path = write_real_evaluation_report(
        report,
        args.output,
    )

    aggregate = report.aggregate

    print(f"CASE_COUNT={aggregate.case_count}")
    print(f"ORIGINAL_RESULTS={aggregate.total_original_results}")
    print(f"UNIQUE_RESULTS={aggregate.total_unique_results}")
    print(f"DUPLICATES_REMOVED={aggregate.total_duplicates_removed}")
    print(f"MEAN_HIT_RATE={aggregate.mean_hit_rate:.6f}")
    print(f"MEAN_RECALL={aggregate.mean_recall:.6f}")
    print(f"MEAN_PRECISION={aggregate.mean_precision:.6f}")
    print(f"MEAN_RECIPROCAL_RANK={aggregate.mean_reciprocal_rank:.6f}")
    print(f"MEAN_NDCG={aggregate.mean_ndcg:.6f}")
    print(
        "CASES_WITHOUT_STRONG_RELEVANCE="
        + ",".join(aggregate.cases_without_strong_relevance)
    )

    for case in report.cases:
        print("")
        print(
            "CASE="
            f"{case.case_id}"
            f"|COVERAGE={case.coverage_status}"
            f"|ORIGINAL={case.original_result_count}"
            f"|UNIQUE={case.deduplicated_result_count}"
            f"|DUPLICATES={case.duplicate_count}"
            f"|HIT={case.metrics.hit_rate:.6f}"
            f"|RECALL={case.metrics.recall:.6f}"
            f"|PRECISION={case.metrics.precision:.6f}"
            f"|MRR={case.metrics.reciprocal_rank:.6f}"
            f"|NDCG={case.metrics.ndcg:.6f}"
        )

    print("")
    print(f"REAL_TEXTUAL_QUALITY_GATE_PASSED={report.quality_gate.passed}")
    print("FAILED_CHECKS=" + ",".join(report.quality_gate.failed_checks))
    print(f"REPORT={output_path}")
    print("NEON_QUERIED_DURING_EVALUATION=False")
    print("GEMINI_USED=False")
    print("GEMINI_QUOTA_CONSUMED=False")
    print("DATABASE_WRITE_EXECUTED=False")

    # O gate pode falhar e ainda assim a avaliação estar correta.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

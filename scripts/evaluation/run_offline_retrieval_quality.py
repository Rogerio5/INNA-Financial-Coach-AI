"""Executa a avaliação offline de qualidade do retrieval."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.retrieval_evaluation import (
    RetrievalQualityThresholds,
    evaluate_retrieval_dataset,
    load_retrieval_dataset,
    write_retrieval_reports,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Executa métricas offline de retrieval sem Gemini e sem Neon.")
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Arquivo JSON com os casos offline.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Diretório dos relatórios JSON e Markdown.",
    )
    parser.add_argument(
        "--minimum-hit-rate",
        type=float,
        default=0.80,
    )
    parser.add_argument(
        "--minimum-recall",
        type=float,
        default=0.75,
    )
    parser.add_argument(
        "--minimum-precision",
        type=float,
        default=0.50,
    )
    parser.add_argument(
        "--minimum-mrr",
        type=float,
        default=0.70,
    )
    parser.add_argument(
        "--minimum-ndcg",
        type=float,
        default=0.75,
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    dataset_name, cases = load_retrieval_dataset(args.dataset)

    thresholds = RetrievalQualityThresholds(
        minimum_hit_rate=args.minimum_hit_rate,
        minimum_recall=args.minimum_recall,
        minimum_precision=args.minimum_precision,
        minimum_mrr=args.minimum_mrr,
        minimum_ndcg=args.minimum_ndcg,
    )

    report = evaluate_retrieval_dataset(
        dataset_name=dataset_name,
        cases=cases,
        thresholds=thresholds,
    )

    json_path, markdown_path = write_retrieval_reports(
        report,
        args.output_dir,
    )

    aggregate = report.aggregate_metrics

    print(f"RUN_ID={report.run_id}")
    print(f"DATASET={report.dataset_name}")
    print(f"CASE_COUNT={aggregate.case_count}")
    print(f"MEAN_HIT_RATE={aggregate.mean_hit_rate:.6f}")
    print(f"MEAN_RECALL={aggregate.mean_recall:.6f}")
    print(f"MEAN_PRECISION={aggregate.mean_precision:.6f}")
    print(f"MEAN_RECIPROCAL_RANK={aggregate.mean_reciprocal_rank:.6f}")
    print(f"MEAN_NDCG={aggregate.mean_ndcg:.6f}")
    print(f"QUALITY_GATE_PASSED={report.quality_gate.passed}")
    print("FAILED_CHECKS=" + ",".join(report.quality_gate.failed_checks))
    print(f"JSON_REPORT={json_path}")
    print(f"MARKDOWN_REPORT={markdown_path}")
    print("EXTERNAL_API_CALL_EXECUTED=False")
    print("DATABASE_CONNECTION_EXECUTED=False")
    print("GEMINI_QUOTA_CONSUMED=False")

    return 0 if report.quality_gate.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

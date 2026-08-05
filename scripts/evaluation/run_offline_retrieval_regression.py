"""Executa comparação offline de regressão de retrieval."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.retrieval_evaluation import (
    evaluate_retrieval_dataset,
    load_retrieval_dataset,
)
from src.evaluation.retrieval_regression import (
    RetrievalRegressionThresholds,
    compare_retrieval_reports,
    load_latency_fixture,
    write_regression_reports,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Compara qualidade e latencia de retrieval offline.")
    )

    parser.add_argument(
        "--baseline-dataset",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--candidate-dataset",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--baseline-latency",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--candidate-latency",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--maximum-quality-drop",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--maximum-mean-latency-increase-ms",
        type=float,
        default=15.0,
    )
    parser.add_argument(
        "--maximum-median-latency-increase-ms",
        type=float,
        default=15.0,
    )
    parser.add_argument(
        "--maximum-p95-latency-increase-ms",
        type=float,
        default=20.0,
    )

    return parser


def main() -> int:
    args = _parser().parse_args()

    baseline_name, baseline_cases = load_retrieval_dataset(args.baseline_dataset)
    candidate_name, candidate_cases = load_retrieval_dataset(args.candidate_dataset)

    baseline_report = evaluate_retrieval_dataset(
        dataset_name=baseline_name,
        cases=baseline_cases,
    )
    candidate_report = evaluate_retrieval_dataset(
        dataset_name=candidate_name,
        cases=candidate_cases,
    )

    _, baseline_latencies = load_latency_fixture(args.baseline_latency)
    _, candidate_latencies = load_latency_fixture(args.candidate_latency)

    quality_drop = args.maximum_quality_drop

    thresholds = RetrievalRegressionThresholds(
        maximum_hit_rate_drop=quality_drop,
        maximum_recall_drop=quality_drop,
        maximum_precision_drop=quality_drop,
        maximum_mrr_drop=quality_drop,
        maximum_ndcg_drop=quality_drop,
        maximum_mean_latency_increase_ms=(args.maximum_mean_latency_increase_ms),
        maximum_median_latency_increase_ms=(args.maximum_median_latency_increase_ms),
        maximum_p95_latency_increase_ms=(args.maximum_p95_latency_increase_ms),
    )

    report = compare_retrieval_reports(
        baseline_report=baseline_report,
        candidate_report=candidate_report,
        baseline_latencies_ms=baseline_latencies,
        candidate_latencies_ms=candidate_latencies,
        thresholds=thresholds,
    )

    json_path, markdown_path = write_regression_reports(
        report,
        args.output_dir,
    )

    print(f"RUN_ID={report.run_id}")
    print(f"BASELINE_DATASET={report.baseline_dataset}")
    print(f"CANDIDATE_DATASET={report.candidate_dataset}")
    print(f"DELTA_HIT_RATE={report.deltas.hit_rate:.6f}")
    print(f"DELTA_RECALL={report.deltas.recall:.6f}")
    print(f"DELTA_PRECISION={report.deltas.precision:.6f}")
    print(f"DELTA_RECIPROCAL_RANK={report.deltas.reciprocal_rank:.6f}")
    print(f"DELTA_NDCG={report.deltas.ndcg:.6f}")
    print(f"DELTA_MEAN_LATENCY_MS={report.deltas.mean_latency_ms:.6f}")
    print(f"DELTA_MEDIAN_LATENCY_MS={report.deltas.median_latency_ms:.6f}")
    print(f"DELTA_P95_LATENCY_MS={report.deltas.p95_latency_ms:.6f}")
    print(f"REGRESSION_GATE_PASSED={report.regression_gate.passed}")
    print("FAILED_CHECKS=" + ",".join(report.regression_gate.failed_checks))
    print(f"JSON_REPORT={json_path}")
    print(f"MARKDOWN_REPORT={markdown_path}")
    print("EXTERNAL_API_CALL_EXECUTED=False")
    print("DATABASE_CONNECTION_EXECUTED=False")
    print("GEMINI_QUOTA_CONSUMED=False")

    return 0 if report.regression_gate.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

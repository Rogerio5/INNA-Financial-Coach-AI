"""Executa toda a validação offline de retrieval em um comando."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from src.evaluation.retrieval_evaluation import (
    RetrievalQualityThresholds,
    evaluate_retrieval_dataset,
    load_retrieval_dataset,
    write_retrieval_reports,
)
from src.evaluation.retrieval_offline_e2e import (
    build_offline_validation_report,
    write_offline_validation_reports,
)
from src.evaluation.retrieval_regression import (
    RetrievalRegressionThresholds,
    compare_retrieval_reports,
    load_latency_fixture,
    write_regression_reports,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Executa a validacao ponta a ponta offline de retrieval.")
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
        "--skip-ruff",
        action="store_true",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
    )

    return parser


def _run_command(
    command: list[str],
    *,
    label: str,
) -> bool:
    print("")
    print("==========================================")
    print(label)
    print("==========================================")
    print("COMMAND=" + " ".join(command))

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    passed = completed.returncode == 0

    print(f"{label.replace(' ', '_')}_PASSED={passed}")
    print(f"{label.replace(' ', '_')}_EXIT_CODE={completed.returncode}")

    return passed


def _run_ruff() -> bool:
    paths = [
        "src/evaluation/retrieval_metrics.py",
        "src/evaluation/retrieval_evaluation.py",
        "src/evaluation/retrieval_regression.py",
        "src/evaluation/retrieval_offline_e2e.py",
        "scripts/evaluation/run_offline_retrieval_quality.py",
        "scripts/evaluation/run_offline_retrieval_regression.py",
        "scripts/evaluation/run_offline_retrieval_e2e.py",
        "tests/evaluations/test_retrieval_metrics.py",
        "tests/evaluations/test_retrieval_evaluation.py",
        "tests/evaluations/test_retrieval_regression.py",
        "tests/evaluations/test_retrieval_offline_e2e.py",
    ]

    return _run_command(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *paths,
        ],
        label="RUFF VALIDATION",
    )


def _run_tests() -> bool:
    test_paths = [
        "tests/evaluations/test_retrieval_metrics.py",
        "tests/evaluations/test_retrieval_evaluation.py",
        "tests/evaluations/test_retrieval_regression.py",
        "tests/evaluations/test_retrieval_offline_e2e.py",
    ]

    return _run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            *test_paths,
            "-q",
        ],
        label="OFFLINE TESTS",
    )


def main() -> int:
    args = _parser().parse_args()

    print("==========================================")
    print("INNA RETRIEVAL OFFLINE E2E")
    print("SEM GEMINI E SEM NEON")
    print("==========================================")

    ruff_passed = True if args.skip_ruff else _run_ruff()

    tests_passed = True if args.skip_tests else _run_tests()

    baseline_name, baseline_cases = load_retrieval_dataset(args.baseline_dataset)
    candidate_name, candidate_cases = load_retrieval_dataset(args.candidate_dataset)

    quality_thresholds = RetrievalQualityThresholds(
        minimum_hit_rate=0.80,
        minimum_recall=0.75,
        minimum_precision=0.50,
        minimum_mrr=0.70,
        minimum_ndcg=0.75,
    )

    baseline_report = evaluate_retrieval_dataset(
        dataset_name=baseline_name,
        cases=baseline_cases,
        thresholds=quality_thresholds,
    )

    candidate_report = evaluate_retrieval_dataset(
        dataset_name=candidate_name,
        cases=candidate_cases,
        thresholds=quality_thresholds,
    )

    _, baseline_latencies = load_latency_fixture(args.baseline_latency)
    _, candidate_latencies = load_latency_fixture(args.candidate_latency)

    regression_thresholds = RetrievalRegressionThresholds(
        maximum_hit_rate_drop=0.05,
        maximum_recall_drop=0.05,
        maximum_precision_drop=0.05,
        maximum_mrr_drop=0.05,
        maximum_ndcg_drop=0.05,
        maximum_mean_latency_increase_ms=15.0,
        maximum_median_latency_increase_ms=15.0,
        maximum_p95_latency_increase_ms=20.0,
    )

    regression_report = compare_retrieval_reports(
        baseline_report=baseline_report,
        candidate_report=candidate_report,
        baseline_latencies_ms=baseline_latencies,
        candidate_latencies_ms=candidate_latencies,
        thresholds=regression_thresholds,
    )

    quality_output = args.output_dir / "quality"
    regression_output = args.output_dir / "regression"
    final_output = args.output_dir / "final"

    quality_json, quality_markdown = write_retrieval_reports(
        baseline_report,
        quality_output,
    )

    regression_json, regression_markdown = write_regression_reports(
        regression_report,
        regression_output,
    )

    final_report = build_offline_validation_report(
        ruff_passed=ruff_passed,
        tests_passed=tests_passed,
        quality_report=baseline_report,
        regression_report=regression_report,
    )

    final_json, final_markdown = write_offline_validation_reports(
        final_report,
        final_output,
    )

    print("")
    print("==========================================")
    print("RESULTADO FINAL")
    print("==========================================")
    print(f"RUFF_PASSED={ruff_passed}")
    print(f"TESTS_PASSED={tests_passed}")
    print(f"QUALITY_GATE_PASSED={baseline_report.quality_gate.passed}")
    print(f"REGRESSION_GATE_PASSED={regression_report.regression_gate.passed}")
    print(f"OFFLINE_RETRIEVAL_VALIDATION={'PASS' if final_report.passed else 'FAIL'}")
    print("FAILED_CHECKS=" + ",".join(final_report.failed_checks))
    print(f"QUALITY_JSON_REPORT={quality_json}")
    print(f"QUALITY_MARKDOWN_REPORT={quality_markdown}")
    print(f"REGRESSION_JSON_REPORT={regression_json}")
    print(f"REGRESSION_MARKDOWN_REPORT={regression_markdown}")
    print(f"FINAL_JSON_REPORT={final_json}")
    print(f"FINAL_MARKDOWN_REPORT={final_markdown}")
    print("EXTERNAL_API_CALL_EXECUTED=False")
    print("DATABASE_CONNECTION_EXECUTED=False")
    print("GEMINI_QUOTA_CONSUMED=False")
    print("NEON_USED=False")

    return 0 if final_report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

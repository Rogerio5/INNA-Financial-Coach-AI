"""Executa benchmark e Quality Gate Agentic RAG sem serviços externos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.evaluation.agentic_benchmark import (
    BenchmarkProfile,
    evaluate_benchmark_quality_gate,
    load_benchmark_dataset,
    load_quality_gate_policy,
    quality_gate_to_dict,
    run_offline_benchmark,
    write_benchmark_csv,
    write_benchmark_json,
    write_quality_gate_report,
)


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser da CLI."""

    parser = argparse.ArgumentParser(
        description=("Executa o benchmark e o Quality Gate offline do Agentic RAG.")
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--policy",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--expected-case-count",
        type=int,
        default=24,
    )

    parser.add_argument(
        "--expected-category-count",
        type=int,
        default=12,
    )

    return parser


def main() -> int:
    """Executa o pipeline completo e retorna código de processo."""

    args = build_parser().parse_args()

    dataset = load_benchmark_dataset(args.dataset)

    policy = load_quality_gate_policy(args.policy)

    benchmark = run_offline_benchmark(dataset)

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=policy,
        expected_case_count=(args.expected_case_count),
        expected_category_count=(args.expected_category_count),
    )

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    benchmark_json = write_benchmark_json(
        benchmark,
        args.output_dir / "offline_benchmark_latest.json",
    )

    benchmark_csv = write_benchmark_csv(
        benchmark,
        args.output_dir / "offline_benchmark_latest.csv",
    )

    gate_json = write_quality_gate_report(
        gate,
        args.output_dir / "offline_quality_gate_latest.json",
    )

    summary_json = args.output_dir / "offline_quality_summary_latest.json"

    agentic = benchmark.summary(BenchmarkProfile.AGENTIC)

    summary_payload = {
        "offline": True,
        "live_services_used": False,
        "dataset_version": dataset.version,
        "dataset_case_count": len(dataset.cases),
        "agentic_pass_rate": (agentic.pass_rate),
        "agentic_average_score": (agentic.average_score),
        "agentic_average_latency_ms": (agentic.average_latency_ms),
        "regression_count": len(benchmark.comparison.regressions),
        "quality_gate": (quality_gate_to_dict(gate)),
        "artifacts": {
            "benchmark_json": str(benchmark_json),
            "benchmark_csv": str(benchmark_csv),
            "quality_gate_json": str(gate_json),
        },
    }

    summary_json.write_text(
        json.dumps(
            summary_payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"DATASET_VERSION={dataset.version}")

    print(f"DATASET_CASE_COUNT={len(dataset.cases)}")

    print(f"AGENTIC_PASS_RATE={agentic.pass_rate}")

    print(f"AGENTIC_AVERAGE_SCORE={agentic.average_score}")

    print(f"REGRESSION_COUNT={len(benchmark.comparison.regressions)}")

    for check in gate.checks:
        print(
            f"QUALITY_CHECK={check.code} "
            f"ACTUAL={check.actual} "
            f"EXPECTED={check.expected} "
            f"PASSED={check.passed}"
        )

    print(f"QUALITY_GATE_PASSED={gate.passed}")

    print(f"QUALITY_GATE_REPORT={gate_json}")

    print(f"QUALITY_SUMMARY_REPORT={summary_json}")

    print("LIVE_SERVICES_USED=False")
    print("SECRETS_USED=False")
    print("LLM_JUDGE_USED=False")

    return 0 if gate.passed else 1


if __name__ == "__main__":
    sys.exit(main())

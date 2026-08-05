from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from src.evaluation.comparison import (
    EvaluationRegressionError,
    compare_report_files,
    enforce_comparison,
    write_comparison_reports,
)
from src.evaluation.history import (
    append_report_to_history,
    load_history,
)

DEFAULT_CRITICAL_METRICS = frozenset(
    {
        "financial-safety",
        "safety-policy",
        "tool-selection",
        "routing-correctness",
    }
)


class CIPipelineError(RuntimeError):
    """Erro de execução do pipeline LLMOps."""


def _find_single_report(
    directory: Path,
) -> Path:
    reports = tuple(sorted(directory.glob("inna-evaluation-*.json")))

    if len(reports) != 1:
        raise CIPipelineError(
            "Era esperado exatamente um relatório "
            "oficial em "
            f"{directory}; encontrados: "
            f"{len(reports)}."
        )

    return reports[0]


def run_ci_pipeline(
    *,
    report_directory: Path,
    baseline_path: Path,
    comparison_output_directory: Path,
    history_seed_path: Path | None,
    history_output_path: Path,
    branch: str,
    commit_sha: str,
    environment: str,
    evaluation_mode: str,
    maximum_metric_regression: float,
    maximum_pass_rate_regression: float,
    critical_metric_ids: frozenset[str],
) -> dict[str, Any]:
    report_path = _find_single_report(report_directory)

    comparison = compare_report_files(
        baseline_path,
        report_path,
        maximum_metric_regression=(maximum_metric_regression),
        maximum_pass_rate_regression=(maximum_pass_rate_regression),
        critical_metric_ids=(critical_metric_ids),
    )

    json_report, markdown_report = write_comparison_reports(
        comparison,
        comparison_output_directory,
    )

    history_output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (
        history_seed_path is not None
        and history_seed_path.exists()
        and not history_output_path.exists()
    ):
        shutil.copy2(
            history_seed_path,
            history_output_path,
        )

    entry = append_report_to_history(
        report_path=report_path,
        history_path=history_output_path,
        comparison=comparison,
        branch=branch,
        commit_sha=commit_sha,
        environment=environment,
        evaluation_mode=evaluation_mode,
        replace_existing=True,
    )

    history = load_history(history_output_path)

    result = {
        "passed": comparison.passed,
        "report_path": str(report_path),
        "baseline_path": str(baseline_path),
        "comparison_json": str(json_report),
        "comparison_markdown": str(markdown_report),
        "history_path": str(history_output_path),
        "history_entries": len(history.entries),
        "run_reference": (entry.run_reference),
        "pass_rate": entry.pass_rate,
        "regression_count": (entry.regression_count),
        "violation_count": (entry.violation_count),
        "missing_case_count": len(comparison.missing_case_ids),
        "missing_dataset_count": len(comparison.missing_dataset_ids),
    }

    summary_path = comparison_output_directory / "ci-pipeline-summary.json"

    summary_path.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    enforce_comparison(comparison)

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Executa comparação, gate de regressão e histórico sanitizado da INNA."
        )
    )

    parser.add_argument(
        "--report-directory",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--comparison-output-directory",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--history-seed",
        type=Path,
    )
    parser.add_argument(
        "--history-output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--branch",
        required=True,
    )
    parser.add_argument(
        "--commit-sha",
        required=True,
    )
    parser.add_argument(
        "--environment",
        default="github-actions",
    )
    parser.add_argument(
        "--evaluation-mode",
        default="deterministic-synthetic",
    )
    parser.add_argument(
        "--maximum-metric-regression",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--maximum-pass-rate-regression",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--critical-metric",
        action="append",
        default=[],
    )

    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    critical_metrics = frozenset(args.critical_metric) or DEFAULT_CRITICAL_METRICS

    try:
        result = run_ci_pipeline(
            report_directory=(args.report_directory),
            baseline_path=args.baseline,
            comparison_output_directory=(args.comparison_output_directory),
            history_seed_path=(args.history_seed),
            history_output_path=(args.history_output),
            branch=args.branch,
            commit_sha=args.commit_sha,
            environment=args.environment,
            evaluation_mode=(args.evaluation_mode),
            maximum_metric_regression=(args.maximum_metric_regression),
            maximum_pass_rate_regression=(args.maximum_pass_rate_regression),
            critical_metric_ids=(critical_metrics),
        )
    except (
        CIPipelineError,
        EvaluationRegressionError,
    ) as exc:
        print(f"LLMOPS_CI_PIPELINE_REJECTED: {exc}")
        return 1

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    print("LLMOPS_CI_PIPELINE_APPROVED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CIPipelineError",
    "DEFAULT_CRITICAL_METRICS",
    "build_parser",
    "main",
    "run_ci_pipeline",
]

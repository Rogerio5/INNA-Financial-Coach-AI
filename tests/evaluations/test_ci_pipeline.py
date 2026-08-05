from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.baseline import (
    EvaluationBaseline,
    write_baseline,
)
from src.evaluation.ci_pipeline import (
    CIPipelineError,
    main,
    run_ci_pipeline,
)


def _report(
    *,
    score: float = 1.0,
) -> dict:
    return {
        "report_type": ("inna-evaluation-batch"),
        "schema_version": "1.0.0",
        "generated_at": None,
        "generated_date": "2026-07-27",
        "run_reference": "run-ci-001",
        "batch": {
            "batch_id": None,
            "run_reference": "run-ci-001",
            "status": "passed",
        },
        "summary": {
            "pass_rate": 1.0,
            "total_cases": 1,
            "passed_cases": 1,
            "failed_cases": 0,
            "blocked_cases": 0,
            "error_cases": 0,
        },
        "quality_gate": {
            "batch_id": None,
            "run_reference": "run-ci-001",
            "passed": True,
        },
        "cases": [
            {
                "case_id": "safety-001",
                "status": "passed",
            }
        ],
        "datasets": [
            {
                "dataset_id": "safety-v1",
            }
        ],
        "metrics": [
            {
                "metric_id": ("financial-safety"),
                "average_score": score,
                "total_executions": 1,
                "passed": 1,
                "failed": 0,
                "blocked": 0,
                "errors": 0,
                "skipped": 0,
            }
        ],
    }


def _prepare_files(
    tmp_path: Path,
    *,
    current_score: float = 1.0,
) -> tuple[Path, Path]:
    report_directory = tmp_path / "reports"
    report_directory.mkdir()

    baseline_report = _report(score=1.0)
    baseline_report["run_reference"] = "run-baseline"
    baseline_report["batch"]["run_reference"] = "run-baseline"
    baseline_report["quality_gate"]["run_reference"] = "run-baseline"

    baseline = EvaluationBaseline.from_report(
        baseline_report,
        baseline_id="production-v1",
        promoted_at="2026-07-27T03:00:00Z",
    )

    baseline_path = tmp_path / "baseline.json"

    write_baseline(
        baseline,
        baseline_path,
    )

    report_path = report_directory / "inna-evaluation-current.json"

    report_path.write_text(
        json.dumps(_report(score=current_score)),
        encoding="utf-8",
    )

    return report_directory, baseline_path


def test_runs_complete_ci_pipeline(
    tmp_path: Path,
) -> None:
    report_directory, baseline_path = _prepare_files(tmp_path)

    result = run_ci_pipeline(
        report_directory=report_directory,
        baseline_path=baseline_path,
        comparison_output_directory=(tmp_path / "comparison"),
        history_seed_path=None,
        history_output_path=(tmp_path / "history/history.json"),
        branch="feat/llmops",
        commit_sha="abc123",
        environment="github-actions",
        evaluation_mode=("deterministic-synthetic"),
        maximum_metric_regression=0.05,
        maximum_pass_rate_regression=0.05,
        critical_metric_ids=frozenset({"financial-safety"}),
    )

    assert result["passed"] is True
    assert result["regression_count"] == 0
    assert result["history_entries"] == 1

    assert (tmp_path / "comparison" / "comparison-report.json").exists()

    assert (tmp_path / "comparison" / "comparison-report.md").exists()

    assert (tmp_path / "comparison" / "ci-pipeline-summary.json").exists()


def test_rejects_regression(
    tmp_path: Path,
) -> None:
    report_directory, baseline_path = _prepare_files(
        tmp_path,
        current_score=0.70,
    )

    exit_code = main(
        [
            "--report-directory",
            str(report_directory),
            "--baseline",
            str(baseline_path),
            "--comparison-output-directory",
            str(tmp_path / "comparison"),
            "--history-output",
            str(tmp_path / "history/history.json"),
            "--branch",
            "feat/llmops",
            "--commit-sha",
            "abc123",
            "--critical-metric",
            "financial-safety",
        ]
    )

    assert exit_code == 1

    assert (tmp_path / "comparison" / "comparison-report.json").exists()


def test_requires_exactly_one_report(
    tmp_path: Path,
) -> None:
    baseline_report = _report()
    baseline = EvaluationBaseline.from_report(baseline_report)

    baseline_path = tmp_path / "baseline.json"

    write_baseline(
        baseline,
        baseline_path,
    )

    empty_directory = tmp_path / "reports"
    empty_directory.mkdir()

    with pytest.raises(
        CIPipelineError,
        match="exatamente um relatório",
    ):
        run_ci_pipeline(
            report_directory=empty_directory,
            baseline_path=baseline_path,
            comparison_output_directory=(tmp_path / "comparison"),
            history_seed_path=None,
            history_output_path=(tmp_path / "history.json"),
            branch="main",
            commit_sha="abc123",
            environment="ci",
            evaluation_mode="synthetic",
            maximum_metric_regression=0.05,
            maximum_pass_rate_regression=0.05,
            critical_metric_ids=frozenset(),
        )

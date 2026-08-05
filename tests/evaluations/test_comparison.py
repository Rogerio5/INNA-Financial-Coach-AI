from __future__ import annotations

import copy
from pathlib import Path

import pytest

from src.evaluation.baseline import (
    EvaluationBaseline,
)
from src.evaluation.comparison import (
    EvaluationRegressionError,
    compare_report_to_baseline,
    enforce_comparison,
    write_comparison_reports,
)


def _report() -> dict:
    return {
        "report_type": ("inna-evaluation-batch"),
        "schema_version": "1.0.0",
        "generated_date": "2026-07-27",
        "run_reference": "run-current-001",
        "batch": {
            "batch_id": "batch-current-001",
            "status": "passed",
        },
        "summary": {
            "pass_rate": 1.0,
            "total_cases": 2,
            "passed_cases": 2,
            "failed_cases": 0,
            "blocked_cases": 0,
            "error_cases": 0,
        },
        "quality_gate": {
            "passed": True,
        },
        "cases": [
            {"case_id": "rag-001"},
            {"case_id": "safety-001"},
        ],
        "datasets": [
            {"dataset_id": "rag-v1"},
            {"dataset_id": "safety-v1"},
        ],
        "metrics": [
            {
                "metric_id": "faithfulness",
                "average_score": 0.95,
                "total_executions": 2,
                "passed": 2,
                "failed": 0,
                "blocked": 0,
                "errors": 0,
                "skipped": 0,
            },
            {
                "metric_id": "financial-safety",
                "average_score": 1.0,
                "total_executions": 2,
                "passed": 2,
                "failed": 0,
                "blocked": 0,
                "errors": 0,
                "skipped": 0,
            },
        ],
    }


def _baseline() -> EvaluationBaseline:
    report = _report()
    report["run_reference"] = "run-baseline"
    report["batch"]["batch_id"] = "batch-baseline"

    return EvaluationBaseline.from_report(
        report,
        baseline_id="production-v1",
        promoted_at="2026-07-27T03:00:00Z",
    )


def test_identical_report_passes() -> None:
    comparison = compare_report_to_baseline(
        _baseline(),
        _report(),
        critical_metric_ids=frozenset({"financial-safety"}),
    )

    assert comparison.passed
    assert comparison.violations == ()
    assert all(metric.status == "stable" for metric in comparison.metrics)


def test_blocks_metric_regression() -> None:
    report = _report()
    report["metrics"][0]["average_score"] = 0.70

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
        maximum_metric_regression=0.05,
    )

    assert not comparison.passed
    assert comparison.regressed_metrics
    assert "Regressão da métrica" in (comparison.violations[0])


def test_blocks_missing_metric() -> None:
    report = _report()
    report["metrics"] = [report["metrics"][0]]

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    assert not comparison.passed
    assert any(metric.status == "missing" for metric in comparison.metrics)


def test_blocks_removed_case() -> None:
    report = _report()
    report["cases"] = [{"case_id": "rag-001"}]

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    assert not comparison.passed
    assert comparison.missing_case_ids == ("safety-001",)


def test_blocks_removed_dataset() -> None:
    report = _report()
    report["datasets"] = [{"dataset_id": "rag-v1"}]

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    assert not comparison.passed
    assert comparison.missing_dataset_ids == ("safety-v1",)


def test_accepts_new_case_and_dataset() -> None:
    report = _report()
    report["cases"].append({"case_id": "routing-001"})
    report["datasets"].append({"dataset_id": "routing-v1"})

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    assert comparison.passed
    assert comparison.new_case_ids == ("routing-001",)
    assert comparison.new_dataset_ids == ("routing-v1",)


def test_blocks_failed_quality_gate() -> None:
    report = copy.deepcopy(_report())
    report["quality_gate"]["passed"] = False

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    assert not comparison.passed
    assert any(
        "quality gate" in violation.lower() for violation in comparison.violations
    )


def test_critical_metric_failure_blocks() -> None:
    report = _report()
    report["metrics"][1]["failed"] = 1
    report["metrics"][1]["passed"] = 1

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
        critical_metric_ids=frozenset({"financial-safety"}),
    )

    assert not comparison.passed
    assert any("Métrica crítica" in violation for violation in comparison.violations)


def test_enforce_raises_on_regression() -> None:
    report = _report()
    report["summary"]["pass_rate"] = 0.70

    comparison = compare_report_to_baseline(
        _baseline(),
        report,
    )

    with pytest.raises(
        EvaluationRegressionError,
        match="taxa de aprovação",
    ):
        enforce_comparison(comparison)


def test_writes_json_and_markdown(
    tmp_path: Path,
) -> None:
    comparison = compare_report_to_baseline(
        _baseline(),
        _report(),
    )

    json_path, markdown_path = write_comparison_reports(
        comparison,
        tmp_path,
    )

    assert json_path.exists()
    assert markdown_path.exists()

    markdown = markdown_path.read_text(encoding="utf-8")

    assert "Relatório de Regressão" in markdown
    assert "APROVADO" in markdown
    assert "faithfulness" in markdown

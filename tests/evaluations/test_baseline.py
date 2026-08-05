from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.baseline import (
    BaselineError,
    BaselinePromotionError,
    EvaluationBaseline,
    load_baseline,
    promote_report_file,
    write_baseline,
)


def _official_report() -> dict:
    return {
        "report_type": ("inna-evaluation-batch"),
        "schema_version": "1.0.0",
        "generated_date": "2026-07-27",
        "run_reference": "run-test-001",
        "batch": {
            "batch_id": "batch-test-001",
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
            {
                "case_id": "rag-001",
                "status": "passed",
            },
            {
                "case_id": "safety-001",
                "status": "passed",
            },
        ],
        "datasets": [
            {
                "dataset_id": ("financial-rag-v1"),
            },
            {
                "dataset_id": ("financial-safety-v1"),
            },
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
                "metric_id": ("financial-safety"),
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


def test_builds_baseline_from_approved_report() -> None:
    baseline = EvaluationBaseline.from_report(
        _official_report(),
        baseline_id="production-v1",
        promoted_at="2026-07-27T03:00:00Z",
        metadata={
            "commit_sha": "abc123",
            "environment": "production",
        },
    )

    assert baseline.baseline_id == ("production-v1")
    assert baseline.pass_rate == 1.0
    assert baseline.quality_gate_passed
    assert baseline.case_ids == (
        "rag-001",
        "safety-001",
    )
    assert baseline.dataset_ids == (
        "financial-rag-v1",
        "financial-safety-v1",
    )
    assert [metric.metric_id for metric in baseline.metrics] == [
        "faithfulness",
        "financial-safety",
    ]


def test_rejects_failed_quality_gate() -> None:
    report = _official_report()
    report["quality_gate"]["passed"] = False

    with pytest.raises(
        BaselinePromotionError,
        match="quality gate",
    ):
        EvaluationBaseline.from_report(report)


def test_rejects_failed_batch() -> None:
    report = _official_report()
    report["batch"]["status"] = "failed"

    with pytest.raises(
        BaselinePromotionError,
        match="lotes aprovados",
    ):
        EvaluationBaseline.from_report(report)


def test_writes_and_loads_baseline(
    tmp_path: Path,
) -> None:
    baseline = EvaluationBaseline.from_report(
        _official_report(),
        baseline_id="production-v1",
        promoted_at="2026-07-27T03:00:00Z",
    )

    destination = tmp_path / "production-baseline.json"

    write_baseline(
        baseline,
        destination,
    )

    loaded = load_baseline(destination)

    assert loaded == baseline

    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert payload["baseline_schema_version"] == "1.0.0"


def test_does_not_overwrite_without_permission(
    tmp_path: Path,
) -> None:
    baseline = EvaluationBaseline.from_report(
        _official_report(),
    )

    destination = tmp_path / "production-baseline.json"

    write_baseline(
        baseline,
        destination,
    )

    with pytest.raises(
        BaselineError,
        match="já existe",
    ):
        write_baseline(
            baseline,
            destination,
        )


def test_promotes_report_file(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "report.json"
    baseline_path = tmp_path / "baseline.json"

    report_path.write_text(
        json.dumps(
            _official_report(),
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    baseline = promote_report_file(
        report_path,
        baseline_path,
        baseline_id="production-v1",
        metadata={
            "commit_sha": "abc123",
        },
    )

    assert baseline_path.exists()
    assert baseline.baseline_id == ("production-v1")
    assert baseline.metadata["commit_sha"] == "abc123"


def test_uses_quality_gate_batch_id_as_fallback() -> None:
    report = _official_report()
    report["batch"]["batch_id"] = None
    report["quality_gate"]["batch_id"] = "quality-gate-batch-001"

    baseline = EvaluationBaseline.from_report(report)

    assert baseline.source_batch_id == ("quality-gate-batch-001")


def test_uses_run_reference_when_batch_ids_are_missing() -> None:
    report = _official_report()
    report["batch"]["batch_id"] = None
    report["quality_gate"]["batch_id"] = None
    report["batch"]["run_reference"] = "run-fallback-001"

    baseline = EvaluationBaseline.from_report(report)

    assert baseline.source_batch_id == ("run-fallback-001")

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.baseline import (
    EvaluationBaseline,
)
from src.evaluation.comparison import (
    compare_report_to_baseline,
)
from src.evaluation.history import (
    DuplicateHistoryEntryError,
    EvaluationHistory,
    EvaluationHistoryEntry,
    append_report_to_history,
    load_history,
    write_history,
)


def _report(
    *,
    run_reference: str = "run-current-001",
    score: float = 0.95,
) -> dict:
    return {
        "report_type": (
            "inna-evaluation-batch"
        ),
        "schema_version": "1.0.0",
        "generated_date": "2026-07-27",
        "run_reference": run_reference,
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
        ],
        "metrics": [
            {
                "metric_id": "faithfulness",
                "average_score": score,
                "total_executions": 2,
                "passed": 2,
                "failed": 0,
                "blocked": 0,
                "errors": 0,
                "skipped": 0,
            },
        ],
    }


def _comparison(
    report: dict,
):
    baseline_report = _report(
        run_reference="run-baseline",
    )

    baseline = EvaluationBaseline.from_report(
        baseline_report,
        baseline_id="production-v1",
        promoted_at="2026-07-27T03:00:00Z",
    )

    return compare_report_to_baseline(
        baseline,
        report,
    )


def test_builds_history_entry() -> None:
    report = _report()
    comparison = _comparison(report)

    entry = EvaluationHistoryEntry.from_report(
        report,
        comparison=comparison,
        branch="feat/llmops",
        commit_sha="abc123",
        environment="ci",
        recorded_at="2026-07-27T03:30:00Z",
    )

    assert entry.run_reference == (
        "run-current-001"
    )
    assert entry.branch == "feat/llmops"
    assert entry.commit_sha == "abc123"
    assert entry.passed
    assert entry.pass_rate == 1.0
    assert entry.case_count == 2
    assert entry.dataset_count == 1
    assert entry.metric_count == 1
    assert entry.regression_count == 0
    assert entry.baseline_id == (
        "production-v1"
    )


def test_adds_and_loads_history(
    tmp_path: Path,
) -> None:
    report = _report()
    entry = EvaluationHistoryEntry.from_report(
        report,
        comparison=_comparison(report),
        branch="main",
        commit_sha="abc123",
        recorded_at="2026-07-27T03:30:00Z",
    )

    history = EvaluationHistory.empty().add(
        entry
    )

    destination = tmp_path / "history.json"

    write_history(
        history,
        destination,
    )

    loaded = load_history(destination)

    assert loaded == history
    assert loaded.latest() == entry


def test_rejects_duplicate_run_reference(
) -> None:
    report = _report()
    entry = EvaluationHistoryEntry.from_report(
        report,
        comparison=_comparison(report),
        recorded_at="2026-07-27T03:30:00Z",
    )

    history = EvaluationHistory.empty().add(
        entry
    )

    with pytest.raises(
        DuplicateHistoryEntryError,
        match="Já existe",
    ):
        history.add(entry)


def test_replaces_existing_entry() -> None:
    first_report = _report(score=0.90)
    second_report = _report(score=0.95)

    first = EvaluationHistoryEntry.from_report(
        first_report,
        comparison=_comparison(first_report),
        recorded_at="2026-07-27T03:30:00Z",
    )

    second = EvaluationHistoryEntry.from_report(
        second_report,
        comparison=_comparison(second_report),
        recorded_at="2026-07-27T03:31:00Z",
    )

    history = (
        EvaluationHistory.empty()
        .add(first)
        .add(
            second,
            replace_existing=True,
        )
    )

    assert len(history.entries) == 1
    assert (
        history.entries[0]
        .metrics[0]
        .average_score
        == 0.95
    )


def test_metric_series() -> None:
    first_report = _report(
        run_reference="run-001",
        score=0.90,
    )
    second_report = _report(
        run_reference="run-002",
        score=0.95,
    )

    first = EvaluationHistoryEntry.from_report(
        first_report,
        comparison=_comparison(first_report),
        recorded_at="2026-07-27T03:30:00Z",
    )

    second = EvaluationHistoryEntry.from_report(
        second_report,
        comparison=_comparison(second_report),
        recorded_at="2026-07-27T03:31:00Z",
    )

    history = (
        EvaluationHistory.empty()
        .add(first)
        .add(second)
    )

    assert history.metric_series(
        "faithfulness"
    ) == (
        (
            "2026-07-27T03:30:00Z",
            0.90,
        ),
        (
            "2026-07-27T03:31:00Z",
            0.95,
        ),
    )


def test_missing_history_returns_empty(
    tmp_path: Path,
) -> None:
    history = load_history(
        tmp_path / "missing.json"
    )

    assert history.entries == ()
    assert history.latest() is None


def test_append_report_to_history(
    tmp_path: Path,
) -> None:
    report = _report()

    report_path = tmp_path / "report.json"
    history_path = tmp_path / "history.json"

    report_path.write_text(
        json.dumps(report),
        encoding="utf-8",
    )

    entry = append_report_to_history(
        report_path=report_path,
        history_path=history_path,
        comparison=_comparison(report),
        branch="main",
        commit_sha="abc123",
        environment="ci",
    )

    assert history_path.exists()
    assert entry.run_reference == (
        "run-current-001"
    )

    loaded = load_history(history_path)

    assert len(loaded.entries) == 1
    assert loaded.entries[0] == entry

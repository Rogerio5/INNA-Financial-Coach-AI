from __future__ import annotations

from src.evaluation.dashboard_data import (
    build_dashboard_summary,
    build_metric_series,
    build_metric_snapshot,
    build_pass_rate_series,
    build_runs_table,
    filter_history,
    get_metric_ids,
)
from src.evaluation.history import (
    EvaluationHistory,
    EvaluationHistoryEntry,
    HistoryMetric,
)


def _entry(
    *,
    run_reference: str,
    recorded_at: str,
    branch: str,
    environment: str,
    passed: bool,
    pass_rate: float,
    metric_score: float,
) -> EvaluationHistoryEntry:
    return EvaluationHistoryEntry(
        recorded_at=recorded_at,
        run_reference=run_reference,
        report_generated_date="2026-07-27",
        branch=branch,
        commit_sha="abc123",
        environment=environment,
        evaluation_mode=("deterministic-synthetic"),
        passed=passed,
        quality_gate_passed=passed,
        pass_rate=pass_rate,
        case_count=11,
        dataset_count=3,
        metric_count=1,
        regression_count=0 if passed else 1,
        violation_count=0 if passed else 1,
        baseline_id="production-v1",
        metrics=(
            HistoryMetric(
                metric_id="faithfulness",
                average_score=metric_score,
                status=("stable" if passed else "regressed"),
                delta_from_baseline=(0.0 if passed else -0.20),
            ),
        ),
    )


def _history() -> EvaluationHistory:
    return EvaluationHistory(
        entries=(
            _entry(
                run_reference="run-001",
                recorded_at=("2026-07-27T03:00:00Z"),
                branch="main",
                environment="ci",
                passed=True,
                pass_rate=1.0,
                metric_score=0.95,
            ),
            _entry(
                run_reference="run-002",
                recorded_at=("2026-07-27T04:00:00Z"),
                branch="feat/llmops",
                environment="local",
                passed=False,
                pass_rate=0.80,
                metric_score=0.75,
            ),
        )
    )


def test_builds_dashboard_summary() -> None:
    summary = build_dashboard_summary(_history())

    assert summary.total_runs == 2
    assert summary.approved_runs == 1
    assert summary.failed_runs == 1
    assert summary.approval_rate == 0.5
    assert summary.latest_pass_rate == 0.80
    assert summary.latest_regressions == 1
    assert summary.latest_violations == 1
    assert summary.tracked_metrics == 1


def test_builds_runs_table_newest_first() -> None:
    rows = build_runs_table(_history())

    assert rows[0]["run_reference"] == ("run-002")
    assert rows[1]["run_reference"] == ("run-001")


def test_builds_pass_rate_series_oldest_first() -> None:
    rows = build_pass_rate_series(_history())

    assert [row["run_reference"] for row in rows] == [
        "run-001",
        "run-002",
    ]


def test_builds_metric_series() -> None:
    rows = build_metric_series(_history())

    assert len(rows) == 2
    assert rows[0]["metric_id"] == ("faithfulness")
    assert rows[1]["average_score"] == 0.75


def test_filters_metric_series() -> None:
    rows = build_metric_series(
        _history(),
        metric_ids={"unknown"},
    )

    assert rows == []


def test_builds_latest_metric_snapshot() -> None:
    snapshot = build_metric_snapshot(_history().latest())

    assert len(snapshot) == 1
    assert snapshot[0]["status"] == ("regressed")


def test_returns_metric_ids() -> None:
    assert get_metric_ids(_history()) == ("faithfulness",)


def test_filters_history() -> None:
    filtered = filter_history(
        _history(),
        branches={"main"},
        environments={"ci"},
        passed=True,
    )

    assert len(filtered.entries) == 1
    assert filtered.entries[0].run_reference == "run-001"


def test_empty_history_summary() -> None:
    summary = build_dashboard_summary(EvaluationHistory.empty())

    assert summary.total_runs == 0
    assert summary.approval_rate == 0.0
    assert summary.latest_pass_rate is None

from __future__ import annotations

import pytest

from src.evaluation.dashboard_data import (
    build_dashboard_summary,
    build_rag_triad_series,
    build_rag_triad_snapshot,
    build_runs_table,
)
from src.evaluation.history import (
    EvaluationHistory,
    EvaluationHistoryEntry,
    HistoryRagTriad,
)


def _entry(
    *,
    run_reference: str,
    recorded_at: str,
    triad: HistoryRagTriad | None,
    passed: bool = True,
) -> EvaluationHistoryEntry:
    return EvaluationHistoryEntry(
        recorded_at=recorded_at,
        run_reference=run_reference,
        report_generated_date="2026-07-30",
        branch="main",
        commit_sha="abc123",
        environment="ci",
        evaluation_mode="live",
        passed=passed,
        quality_gate_passed=passed,
        pass_rate=1.0 if passed else 0.5,
        case_count=2,
        dataset_count=1,
        metric_count=3,
        regression_count=0,
        violation_count=0,
        baseline_id="production-v1",
        metrics=(),
        rag_triad=triad,
    )


def _passing_triad(
    score: float = 0.90,
) -> HistoryRagTriad:
    return HistoryRagTriad(
        status="passed",
        average_score=score,
        passed=True,
        total_cases=2,
        complete_cases=2,
        failing_metric_ids=(),
    )


def _failed_triad() -> HistoryRagTriad:
    return HistoryRagTriad(
        status="failed",
        average_score=0.60,
        passed=False,
        total_cases=2,
        complete_cases=2,
        failing_metric_ids=(
            "faithfulness",
        ),
    )


def _history() -> EvaluationHistory:
    return EvaluationHistory(
        entries=(
            _entry(
                run_reference="run-001",
                recorded_at=(
                    "2026-07-30T01:00:00Z"
                ),
                triad=_passing_triad(),
            ),
            _entry(
                run_reference="run-002",
                recorded_at=(
                    "2026-07-30T02:00:00Z"
                ),
                triad=None,
            ),
            _entry(
                run_reference="run-003",
                recorded_at=(
                    "2026-07-30T03:00:00Z"
                ),
                triad=_failed_triad(),
                passed=False,
            ),
        )
    )


def test_summary_contains_rag_triad_indicators(
) -> None:
    summary = build_dashboard_summary(
        _history()
    )

    assert summary.rag_triad_runs == 2
    assert summary.rag_triad_approved_runs == 1
    assert summary.rag_triad_pass_rate == (
        pytest.approx(0.50)
    )
    assert summary.latest_rag_triad_status == (
        "failed"
    )
    assert summary.latest_rag_triad_score == (
        pytest.approx(0.60)
    )
    assert (
        summary.latest_rag_triad_passed
        is False
    )


def test_summary_serializes_rag_triad_fields(
) -> None:
    payload = build_dashboard_summary(
        _history()
    ).to_dict()

    assert payload["rag_triad_runs"] == 2
    assert payload[
        "rag_triad_approved_runs"
    ] == 1
    assert payload[
        "rag_triad_pass_rate"
    ] == pytest.approx(0.50)
    assert payload[
        "latest_rag_triad_status"
    ] == "failed"


def test_rag_triad_series_ignores_old_runs(
) -> None:
    rows = build_rag_triad_series(
        _history()
    )

    assert len(rows) == 2
    assert rows[0]["run_reference"] == (
        "run-001"
    )
    assert rows[1]["run_reference"] == (
        "run-003"
    )


def test_rag_triad_series_is_oldest_first(
) -> None:
    rows = build_rag_triad_series(
        _history()
    )

    assert [
        row["recorded_at"]
        for row in rows
    ] == [
        "2026-07-30T01:00:00Z",
        "2026-07-30T03:00:00Z",
    ]


def test_rag_triad_series_exposes_failure(
) -> None:
    rows = build_rag_triad_series(
        _history()
    )

    latest = rows[-1]

    assert latest["status"] == "failed"
    assert latest["passed"] is False
    assert latest["average_score"] == (
        pytest.approx(0.60)
    )
    assert latest[
        "failing_metric_ids"
    ] == [
        "faithfulness",
    ]


def test_rag_triad_series_calculates_completeness(
) -> None:
    rows = build_rag_triad_series(
        _history()
    )

    assert rows[0][
        "completeness_rate"
    ] == pytest.approx(1.0)


def test_rag_triad_snapshot_returns_latest_data(
) -> None:
    snapshot = build_rag_triad_snapshot(
        _history().latest()
    )

    assert snapshot is not None
    assert snapshot["status"] == "failed"
    assert snapshot["passed"] is False
    assert snapshot["average_score"] == (
        pytest.approx(0.60)
    )
    assert snapshot[
        "failing_metric_ids"
    ] == [
        "faithfulness",
    ]


def test_snapshot_without_triad_returns_none(
) -> None:
    entry = _entry(
        run_reference="run-no-triad",
        recorded_at="2026-07-30T04:00:00Z",
        triad=None,
    )

    assert (
        build_rag_triad_snapshot(entry)
        is None
    )


def test_runs_table_contains_rag_triad_columns(
) -> None:
    rows = build_runs_table(
        _history()
    )

    latest = rows[0]

    assert latest["run_reference"] == (
        "run-003"
    )
    assert latest["rag_triad_status"] == (
        "failed"
    )
    assert latest["rag_triad_score"] == (
        pytest.approx(0.60)
    )
    assert latest[
        "rag_triad_failing_metrics"
    ] == [
        "faithfulness",
    ]


def test_runs_table_handles_old_history(
) -> None:
    rows = build_runs_table(
        EvaluationHistory(
            entries=(
                _entry(
                    run_reference="run-old",
                    recorded_at=(
                        "2026-07-30T01:00:00Z"
                    ),
                    triad=None,
                ),
            )
        )
    )

    assert rows[0][
        "rag_triad_status"
    ] is None
    assert rows[0][
        "rag_triad_score"
    ] is None
    assert rows[0][
        "rag_triad_total_cases"
    ] == 0


def test_empty_history_has_no_triad_metrics(
) -> None:
    summary = build_dashboard_summary(
        EvaluationHistory.empty()
    )

    assert summary.rag_triad_runs == 0
    assert summary.rag_triad_approved_runs == 0
    assert summary.rag_triad_pass_rate is None
    assert summary.latest_rag_triad_status is None
    assert summary.latest_rag_triad_score is None
    assert summary.latest_rag_triad_passed is None

    assert build_rag_triad_series(
        EvaluationHistory.empty()
    ) == []

    assert build_rag_triad_snapshot(
        None
    ) is None

from types import SimpleNamespace

import pytest

from src.evaluation.rag_lab_dashboard_data import (
    build_rag_lab_comparison_rows,
    build_rag_lab_run_options,
    build_rag_lab_summary,
    build_rag_lab_timeline,
    build_selected_comparison,
    find_rag_lab_entry,
    get_rag_lab_entries,
    select_default_comparison,
)


def _metric(
    metric_id: str,
    score: float,
):
    return SimpleNamespace(
        metric_id=metric_id,
        average_score=score,
    )


def _entry(
    reference: str,
    *,
    recorded_at: str,
    aggregate: float | None,
    passed: bool | None = True,
    complete: bool = True,
    branch: str = "main",
    environment: str = "test",
):
    total_cases = 10

    complete_cases = total_cases if complete else 7

    triad = SimpleNamespace(
        status=(
            "passed" if passed is True else "failed" if passed is False else "partial"
        ),
        average_score=aggregate,
        passed=passed,
        total_cases=total_cases,
        complete_cases=complete_cases,
        failing_metric_ids=(),
    )

    base_score = aggregate if aggregate is not None else 0.0

    return SimpleNamespace(
        run_reference=reference,
        recorded_at=recorded_at,
        branch=branch,
        environment=environment,
        evaluation_mode="offline",
        metrics=(
            _metric(
                "answer-relevancy",
                min(base_score + 0.01, 1.0),
            ),
            _metric(
                "faithfulness",
                base_score,
            ),
            _metric(
                "contextual-relevancy",
                max(base_score - 0.01, 0.0),
            ),
        ),
        rag_triad=triad,
    )


def _history(*entries):
    return SimpleNamespace(
        entries=entries,
    )


def test_selects_only_rag_triad_entries():
    old_entry = SimpleNamespace(
        run_reference="old",
        recorded_at="2026-07-01T00:00:00Z",
        rag_triad=None,
    )

    current = _entry(
        "current",
        recorded_at="2026-07-02T00:00:00Z",
        aggregate=0.90,
    )

    entries = get_rag_lab_entries(
        _history(
            old_entry,
            current,
        )
    )

    assert tuple(item.run_reference for item in entries) == ("current",)


def test_orders_entries_from_newest_to_oldest():
    older = _entry(
        "older",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.80,
    )

    newer = _entry(
        "newer",
        recorded_at="2026-07-03T00:00:00Z",
        aggregate=0.90,
    )

    entries = get_rag_lab_entries(
        _history(
            older,
            newer,
        )
    )

    assert tuple(item.run_reference for item in entries) == (
        "newer",
        "older",
    )


def test_complete_only_removes_partial_runs():
    complete = _entry(
        "complete",
        recorded_at="2026-07-03T00:00:00Z",
        aggregate=0.90,
    )

    partial = _entry(
        "partial",
        recorded_at="2026-07-04T00:00:00Z",
        aggregate=0.85,
        passed=None,
        complete=False,
    )

    entries = get_rag_lab_entries(
        _history(
            complete,
            partial,
        ),
        complete_only=True,
    )

    assert tuple(item.run_reference for item in entries) == ("complete",)


def test_builds_professional_summary():
    first = _entry(
        "run-001",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.80,
        passed=True,
    )

    second = _entry(
        "run-002",
        recorded_at="2026-07-02T00:00:00Z",
        aggregate=0.92,
        passed=True,
    )

    third = _entry(
        "run-003",
        recorded_at="2026-07-03T00:00:00Z",
        aggregate=0.70,
        passed=False,
    )

    summary = build_rag_lab_summary(
        _history(
            first,
            second,
            third,
        )
    )

    assert summary.total_history_runs == 3
    assert summary.comparable_runs == 3
    assert summary.approved_runs == 2
    assert summary.failed_runs == 1
    assert summary.approval_rate == pytest.approx(2 / 3)
    assert summary.latest_reference == "run-003"
    assert summary.best_reference == "run-002"
    assert summary.best_score == pytest.approx(0.92)
    assert summary.worst_reference == "run-003"


def test_builds_run_options_with_labels():
    entry = _entry(
        "run-001",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.91,
        branch="feature/rag",
        environment="ci",
    )

    options = build_rag_lab_run_options(_history(entry))

    assert len(options) == 1
    assert options[0].score == pytest.approx(0.91)
    assert "run-001" in options[0].label
    assert "91.00%" in options[0].label
    assert "feature/rag" in options[0].label


def test_selects_default_baseline_and_candidate():
    older = _entry(
        "baseline",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.80,
    )

    newer = _entry(
        "candidate",
        recorded_at="2026-07-02T00:00:00Z",
        aggregate=0.90,
    )

    selected = select_default_comparison(
        _history(
            older,
            newer,
        )
    )

    assert selected is not None

    baseline, candidate = selected

    assert baseline.run_reference == "baseline"
    assert candidate.run_reference == "candidate"


def test_returns_none_with_less_than_two_runs():
    selected = select_default_comparison(
        _history(
            _entry(
                "only",
                recorded_at=("2026-07-01T00:00:00Z"),
                aggregate=0.80,
            )
        )
    )

    assert selected is None


def test_builds_selected_comparison_and_rows():
    baseline = _entry(
        "baseline",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.80,
    )

    candidate = _entry(
        "candidate",
        recorded_at="2026-07-02T00:00:00Z",
        aggregate=0.90,
    )

    history = _history(
        baseline,
        candidate,
    )

    comparison = build_selected_comparison(
        history,
        baseline_reference="baseline",
        candidate_reference="candidate",
    )

    assert comparison is not None
    assert comparison.status.value == "improved"

    rows = build_rag_lab_comparison_rows(comparison)

    assert len(rows) == 4
    assert rows[-1]["metric_id"] == ("rag-triad-average")


def test_rejects_same_baseline_and_candidate():
    entry = _entry(
        "same",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.90,
    )

    comparison = build_selected_comparison(
        _history(entry),
        baseline_reference="same",
        candidate_reference="same",
    )

    assert comparison is None


def test_finds_entry_by_reference():
    entry = _entry(
        "run-lookup",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.90,
    )

    found = find_rag_lab_entry(
        _history(entry),
        "run-lookup",
    )

    assert found is entry

    missing = find_rag_lab_entry(
        _history(entry),
        "missing",
    )

    assert missing is None


def test_builds_chronological_timeline():
    newer = _entry(
        "newer",
        recorded_at="2026-07-02T00:00:00Z",
        aggregate=0.90,
    )

    older = _entry(
        "older",
        recorded_at="2026-07-01T00:00:00Z",
        aggregate=0.80,
    )

    rows = build_rag_lab_timeline(
        _history(
            newer,
            older,
        )
    )

    assert [row["run_reference"] for row in rows] == [
        "older",
        "newer",
    ]

    assert rows[0]["rag_triad_score"] == pytest.approx(0.80)

    assert rows[1]["answer-relevancy"] == pytest.approx(0.91)


def test_empty_history_is_supported():
    history = _history()

    summary = build_rag_lab_summary(history)

    assert summary.total_history_runs == 0
    assert summary.comparable_runs == 0
    assert summary.approval_rate is None
    assert summary.latest_reference is None

    assert build_rag_lab_run_options(history) == ()

    assert build_rag_lab_timeline(history) == []

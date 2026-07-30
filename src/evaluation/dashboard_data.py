from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.evaluation.history import (
    EvaluationHistory,
    EvaluationHistoryEntry,
    load_history,
)


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    total_runs: int
    approved_runs: int
    failed_runs: int
    approval_rate: float
    latest_pass_rate: float | None
    latest_regressions: int
    latest_violations: int
    latest_quality_gate_passed: bool | None
    tracked_metrics: int
    rag_triad_runs: int = 0
    rag_triad_approved_runs: int = 0
    rag_triad_pass_rate: float | None = None
    latest_rag_triad_status: str | None = None
    latest_rag_triad_score: float | None = None
    latest_rag_triad_passed: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "approved_runs": self.approved_runs,
            "failed_runs": self.failed_runs,
            "approval_rate": self.approval_rate,
            "latest_pass_rate": self.latest_pass_rate,
            "latest_regressions": (
                self.latest_regressions
            ),
            "latest_violations": (
                self.latest_violations
            ),
            "latest_quality_gate_passed": (
                self.latest_quality_gate_passed
            ),
            "tracked_metrics": self.tracked_metrics,
            "rag_triad_runs": self.rag_triad_runs,
            "rag_triad_approved_runs": (
                self.rag_triad_approved_runs
            ),
            "rag_triad_pass_rate": (
                self.rag_triad_pass_rate
            ),
            "latest_rag_triad_status": (
                self.latest_rag_triad_status
            ),
            "latest_rag_triad_score": (
                self.latest_rag_triad_score
            ),
            "latest_rag_triad_passed": (
                self.latest_rag_triad_passed
            ),
        }


def _parse_recorded_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            "recorded_at inválido no histórico: "
            f"{value!r}."
        ) from exc


def build_dashboard_summary(
    history: EvaluationHistory,
) -> DashboardSummary:
    total_runs = len(history.entries)

    approved_runs = sum(
        1
        for entry in history.entries
        if entry.passed
    )

    failed_runs = total_runs - approved_runs

    approval_rate = (
        approved_runs / total_runs
        if total_runs
        else 0.0
    )

    latest = history.latest()

    metric_ids = {
        metric.metric_id
        for entry in history.entries
        for metric in entry.metrics
    }

    rag_triad_entries = tuple(
        entry
        for entry in history.entries
        if entry.rag_triad is not None
    )

    rag_triad_runs = len(
        rag_triad_entries
    )

    rag_triad_approved_runs = sum(
        1
        for entry in rag_triad_entries
        if (
            entry.rag_triad is not None
            and entry.rag_triad.passed is True
        )
    )

    rag_triad_pass_rate = (
        rag_triad_approved_runs
        / rag_triad_runs
        if rag_triad_runs
        else None
    )

    latest_triad = (
        latest.rag_triad
        if latest is not None
        else None
    )

    return DashboardSummary(
        total_runs=total_runs,
        approved_runs=approved_runs,
        failed_runs=failed_runs,
        approval_rate=approval_rate,
        latest_pass_rate=(
            latest.pass_rate
            if latest is not None
            else None
        ),
        latest_regressions=(
            latest.regression_count
            if latest is not None
            else 0
        ),
        latest_violations=(
            latest.violation_count
            if latest is not None
            else 0
        ),
        latest_quality_gate_passed=(
            latest.quality_gate_passed
            if latest is not None
            else None
        ),
        tracked_metrics=len(metric_ids),
        rag_triad_runs=rag_triad_runs,
        rag_triad_approved_runs=(
            rag_triad_approved_runs
        ),
        rag_triad_pass_rate=(
            rag_triad_pass_rate
        ),
        latest_rag_triad_status=(
            latest_triad.status
            if latest_triad is not None
            else None
        ),
        latest_rag_triad_score=(
            latest_triad.average_score
            if latest_triad is not None
            else None
        ),
        latest_rag_triad_passed=(
            latest_triad.passed
            if latest_triad is not None
            else None
        ),
    )


def build_runs_table(
    history: EvaluationHistory,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for entry in sorted(
        history.entries,
        key=lambda item: _parse_recorded_at(
            item.recorded_at
        ),
        reverse=True,
    ):
        rows.append(
            {
                "recorded_at": entry.recorded_at,
                "run_reference": (
                    entry.run_reference
                ),
                "branch": entry.branch,
                "commit_sha": entry.commit_sha,
                "environment": entry.environment,
                "evaluation_mode": (
                    entry.evaluation_mode
                ),
                "passed": entry.passed,
                "quality_gate_passed": (
                    entry.quality_gate_passed
                ),
                "pass_rate": entry.pass_rate,
                "case_count": entry.case_count,
                "dataset_count": (
                    entry.dataset_count
                ),
                "metric_count": entry.metric_count,
                "regression_count": (
                    entry.regression_count
                ),
                "violation_count": (
                    entry.violation_count
                ),
                "baseline_id": entry.baseline_id,
                "rag_triad_status": (
                    entry.rag_triad.status
                    if entry.rag_triad is not None
                    else None
                ),
                "rag_triad_score": (
                    entry.rag_triad.average_score
                    if entry.rag_triad is not None
                    else None
                ),
                "rag_triad_passed": (
                    entry.rag_triad.passed
                    if entry.rag_triad is not None
                    else None
                ),
                "rag_triad_total_cases": (
                    entry.rag_triad.total_cases
                    if entry.rag_triad is not None
                    else 0
                ),
                "rag_triad_complete_cases": (
                    entry.rag_triad.complete_cases
                    if entry.rag_triad is not None
                    else 0
                ),
                "rag_triad_failing_metrics": (
                    list(
                        entry.rag_triad
                        .failing_metric_ids
                    )
                    if entry.rag_triad is not None
                    else []
                ),
            }
        )

    return rows


def build_pass_rate_series(
    history: EvaluationHistory,
) -> list[dict[str, Any]]:
    return [
        {
            "recorded_at": entry.recorded_at,
            "run_reference": entry.run_reference,
            "pass_rate": entry.pass_rate,
            "passed": entry.passed,
        }
        for entry in sorted(
            history.entries,
            key=lambda item: _parse_recorded_at(
                item.recorded_at
            ),
        )
    ]


def build_metric_series(
    history: EvaluationHistory,
    metric_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for entry in sorted(
        history.entries,
        key=lambda item: _parse_recorded_at(
            item.recorded_at
        ),
    ):
        for metric in entry.metrics:
            if (
                metric_ids is not None
                and metric.metric_id not in metric_ids
            ):
                continue

            rows.append(
                {
                    "recorded_at": entry.recorded_at,
                    "run_reference": (
                        entry.run_reference
                    ),
                    "metric_id": metric.metric_id,
                    "average_score": (
                        metric.average_score
                    ),
                    "status": metric.status,
                    "delta_from_baseline": (
                        metric.delta_from_baseline
                    ),
                }
            )

    return rows


def build_rag_triad_series(
    history: EvaluationHistory,
) -> list[dict[str, Any]]:
    """
    Constrói a série temporal da RAG Triad.

    Históricos antigos e execuções sem RAG Triad são
    ignorados sem gerar dados artificiais.
    """

    rows: list[dict[str, Any]] = []

    for entry in sorted(
        history.entries,
        key=lambda item: _parse_recorded_at(
            item.recorded_at
        ),
    ):
        triad = entry.rag_triad

        if triad is None:
            continue

        rows.append(
            {
                "recorded_at": entry.recorded_at,
                "run_reference": (
                    entry.run_reference
                ),
                "status": triad.status,
                "average_score": (
                    triad.average_score
                ),
                "passed": triad.passed,
                "total_cases": triad.total_cases,
                "complete_cases": (
                    triad.complete_cases
                ),
                "completeness_rate": (
                    triad.complete_cases
                    / triad.total_cases
                    if triad.total_cases
                    else 0.0
                ),
                "failing_metric_ids": list(
                    triad.failing_metric_ids
                ),
            }
        )

    return rows


def build_rag_triad_snapshot(
    entry: EvaluationHistoryEntry | None,
) -> dict[str, Any] | None:
    """
    Retorna o snapshot consolidado da RAG Triad mais recente.
    """

    if (
        entry is None
        or entry.rag_triad is None
    ):
        return None

    triad = entry.rag_triad

    return {
        "status": triad.status,
        "average_score": triad.average_score,
        "passed": triad.passed,
        "total_cases": triad.total_cases,
        "complete_cases": triad.complete_cases,
        "completeness_rate": (
            triad.complete_cases
            / triad.total_cases
            if triad.total_cases
            else 0.0
        ),
        "failing_metric_ids": list(
            triad.failing_metric_ids
        ),
    }


def build_metric_snapshot(
    entry: EvaluationHistoryEntry | None,
) -> list[dict[str, Any]]:
    if entry is None:
        return []

    return [
        {
            "metric_id": metric.metric_id,
            "average_score": metric.average_score,
            "status": metric.status,
            "delta_from_baseline": (
                metric.delta_from_baseline
            ),
        }
        for metric in sorted(
            entry.metrics,
            key=lambda item: item.metric_id,
        )
    ]


def get_metric_ids(
    history: EvaluationHistory,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                metric.metric_id
                for entry in history.entries
                for metric in entry.metrics
            }
        )
    )


def filter_history(
    history: EvaluationHistory,
    *,
    branches: set[str] | None = None,
    environments: set[str] | None = None,
    passed: bool | None = None,
) -> EvaluationHistory:
    entries = tuple(
        entry
        for entry in history.entries
        if (
            branches is None
            or entry.branch in branches
        )
        and (
            environments is None
            or entry.environment in environments
        )
        and (
            passed is None
            or entry.passed is passed
        )
    )

    return EvaluationHistory(entries=entries)


def load_dashboard_history(
    path: str,
) -> EvaluationHistory:
    return load_history(path)


__all__ = [
    "DashboardSummary",
    "build_dashboard_summary",
    "build_metric_series",
    "build_metric_snapshot",
    "build_pass_rate_series",
    "build_rag_triad_series",
    "build_rag_triad_snapshot",
    "build_runs_table",
    "filter_history",
    "get_metric_ids",
    "load_dashboard_history",
]

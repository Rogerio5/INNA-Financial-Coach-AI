from __future__ import annotations

import pytest

from src.evaluation.history import (
    EvaluationHistoryEntry,
    HistoryRagTriad,
)


def _base_report(
    cases: list[dict],
) -> dict:
    return {
        "report_type": ("inna-evaluation-batch"),
        "schema_version": "1.0.0",
        "generated_date": "2026-07-30",
        "run_reference": "run-triad-001",
        "batch": {
            "batch_id": None,
            "status": "passed",
        },
        "summary": {
            "pass_rate": 1.0,
            "total_cases": len(cases),
            "passed_cases": len(cases),
            "failed_cases": 0,
            "blocked_cases": 0,
            "error_cases": 0,
        },
        "quality_gate": {
            "passed": True,
        },
        "cases": cases,
        "datasets": [
            {
                "dataset_id": "rag@1.0.0",
            }
        ],
        "metrics": [
            {
                "metric_id": "faithfulness",
                "average_score": 0.90,
            }
        ],
    }


def _triad(
    *,
    status: str = "passed",
    score: float | None = 0.90,
    passed: bool | None = True,
    complete: bool = True,
    failing: list[str] | None = None,
) -> dict:
    return {
        "status": status,
        "aggregate_score": score,
        "passed": passed,
        "is_complete": complete,
        "missing_metric_ids": [],
        "failing_metric_ids": (failing or []),
        "axes": [],
    }


def test_history_reads_external_case_triad() -> None:
    report = _base_report(
        [
            {
                "case_id": "rag-001",
                "rag_triad": _triad(),
            }
        ]
    )

    entry = EvaluationHistoryEntry.from_report(report)

    assert entry.rag_triad is not None
    assert entry.rag_triad.status == "passed"
    assert entry.rag_triad.average_score == 0.90
    assert entry.rag_triad.passed is True
    assert entry.rag_triad.total_cases == 1
    assert entry.rag_triad.complete_cases == 1


def test_history_reads_internal_nested_triad() -> None:
    report = _base_report(
        [
            {
                "case_id": "rag-001",
                "evaluation": {
                    "rag_triad": _triad(score=0.85),
                },
            }
        ]
    )

    entry = EvaluationHistoryEntry.from_report(report)

    assert entry.rag_triad is not None
    assert entry.rag_triad.average_score == (pytest.approx(0.85))


def test_history_aggregates_multiple_triads() -> None:
    report = _base_report(
        [
            {
                "case_id": "rag-001",
                "rag_triad": _triad(score=0.90),
            },
            {
                "case_id": "rag-002",
                "rag_triad": _triad(score=0.80),
            },
        ]
    )

    entry = EvaluationHistoryEntry.from_report(report)

    assert entry.rag_triad is not None
    assert entry.rag_triad.average_score == (pytest.approx(0.85))
    assert entry.rag_triad.total_cases == 2
    assert entry.rag_triad.complete_cases == 2
    assert entry.rag_triad.passed is True


def test_failed_triad_has_priority() -> None:
    report = _base_report(
        [
            {
                "case_id": "rag-001",
                "rag_triad": _triad(),
            },
            {
                "case_id": "rag-002",
                "rag_triad": _triad(
                    status="failed",
                    score=0.50,
                    passed=False,
                    failing=[
                        "faithfulness",
                    ],
                ),
            },
        ]
    )

    entry = EvaluationHistoryEntry.from_report(report)

    assert entry.rag_triad is not None
    assert entry.rag_triad.status == "failed"
    assert entry.rag_triad.passed is False
    assert entry.rag_triad.failing_metric_ids == ("faithfulness",)


def test_report_without_triad_remains_supported() -> None:
    report = _base_report(
        [
            {
                "case_id": "budget-001",
            }
        ]
    )

    entry = EvaluationHistoryEntry.from_report(report)

    assert entry.rag_triad is None


def test_old_history_payload_without_triad_loads() -> None:
    entry = EvaluationHistoryEntry.from_report(
        _base_report(
            [
                {
                    "case_id": "budget-001",
                }
            ]
        )
    )

    payload = entry.to_dict()
    payload.pop("rag_triad")

    restored = EvaluationHistoryEntry.from_dict(payload)

    assert restored.rag_triad is None


def test_history_triad_round_trip() -> None:
    original = HistoryRagTriad(
        status="failed",
        average_score=0.70,
        passed=False,
        total_cases=2,
        complete_cases=2,
        failing_metric_ids=("faithfulness",),
    )

    restored = HistoryRagTriad.from_dict(original.to_dict())

    assert restored == original


def test_entry_serializes_optional_triad() -> None:
    entry = EvaluationHistoryEntry.from_report(
        _base_report(
            [
                {
                    "case_id": "rag-001",
                    "rag_triad": _triad(),
                }
            ]
        )
    )

    payload = entry.to_dict()

    assert payload["rag_triad"] == {
        "status": "passed",
        "average_score": 0.90,
        "passed": True,
        "total_cases": 1,
        "complete_cases": 1,
        "failing_metric_ids": [],
    }

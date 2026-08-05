from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.evaluation.deepeval_metrics import (
    MetricExecutionMode,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunResult,
    EvaluationRunStatus,
    MetricRunResult,
    MetricRunStatus,
)
from src.evaluation.rag_triad import (
    RAG_TRIAD_METRIC_IDS,
    RagTriadStatus,
)


def build_metric_result(
    metric_id: str,
    *,
    status: MetricRunStatus = MetricRunStatus.PASSED,
    score: float | None = 0.90,
    threshold: float | None = 0.80,
    passed: bool | None = True,
    estimated_cost: float = 0.01,
) -> MetricRunResult:
    return MetricRunResult(
        metric_id=metric_id,
        status=status,
        execution_mode=(MetricExecutionMode.LIVE_OPT_IN),
        score=score,
        threshold=threshold,
        passed=passed,
        reason=None,
        duration_ms=10.0,
        estimated_cost=estimated_cost,
    )


def build_complete_triad() -> tuple[MetricRunResult, ...]:
    return tuple(build_metric_result(metric_id) for metric_id in RAG_TRIAD_METRIC_IDS)


def build_run_result(
    metric_results: tuple[
        MetricRunResult,
        ...,
    ],
    *,
    category: str = "rag",
    profile_id: str = "rag-profile",
    mode: EvaluationRunMode = (EvaluationRunMode.LIVE),
    status: EvaluationRunStatus = (EvaluationRunStatus.PASSED),
) -> EvaluationRunResult:
    now = datetime.now(UTC)

    return EvaluationRunResult(
        run_id="run-rag-triad-001",
        case_id="rag-case-001",
        dataset_id="rag-dataset@1.0.0",
        category=category,
        profile_id=profile_id,
        mode=mode,
        status=status,
        metric_results=metric_results,
        started_at=now,
        finished_at=now,
        duration_ms=30.0,
        total_estimated_cost=sum(metric.estimated_cost for metric in metric_results),
        external_run=False,
        deepeval_live_enabled=True,
        metadata={
            "environment": "test",
        },
    )


def test_run_result_exposes_complete_rag_triad() -> None:
    result = build_run_result(build_complete_triad())

    triad = result.rag_triad

    assert triad is not None
    assert triad.status == RagTriadStatus.PASSED
    assert triad.passed is True
    assert triad.is_complete is True
    assert triad.aggregate_score == pytest.approx(0.90)


def test_triad_contains_run_audit_metadata() -> None:
    triad = build_run_result(build_complete_triad()).rag_triad

    assert triad is not None
    assert triad.metadata["run_id"] == ("run-rag-triad-001")
    assert triad.metadata["case_id"] == ("rag-case-001")
    assert triad.metadata["dataset_id"] == ("rag-dataset@1.0.0")
    assert triad.metadata["profile_id"] == ("rag-profile")
    assert triad.metadata["mode"] == "live"
    assert triad.metadata["run_status"] == ("passed")


def test_non_rag_run_has_no_triad() -> None:
    result = build_run_result(
        (build_metric_result("financial-quality"),),
        category="budget",
        profile_id="budget-profile",
    )

    assert result.rag_triad is None
    assert result.rag_triad_payload is None


def test_partial_triad_remains_partial() -> None:
    result = build_run_result(
        build_complete_triad()[:2],
        status=EvaluationRunStatus.PARTIAL,
    )

    triad = result.rag_triad

    assert triad is not None
    assert triad.status == RagTriadStatus.PARTIAL
    assert triad.passed is None
    assert triad.missing_metric_ids == ("contextual-relevancy",)


def test_failed_faithfulness_fails_triad() -> None:
    metrics = list(build_complete_triad())

    metrics[1] = build_metric_result(
        "faithfulness",
        status=MetricRunStatus.FAILED,
        score=0.50,
        passed=False,
    )

    triad = build_run_result(
        tuple(metrics),
        status=EvaluationRunStatus.FAILED,
    ).rag_triad

    assert triad is not None
    assert triad.status == RagTriadStatus.FAILED
    assert triad.passed is False
    assert triad.failing_metric_ids == ("faithfulness",)


def test_dry_run_exposes_planned_triad() -> None:
    metrics = tuple(
        build_metric_result(
            metric_id,
            status=MetricRunStatus.PLANNED,
            score=None,
            passed=None,
            estimated_cost=0.0,
        )
        for metric_id in RAG_TRIAD_METRIC_IDS
    )

    triad = build_run_result(
        metrics,
        mode=EvaluationRunMode.DRY_RUN,
        status=EvaluationRunStatus.PLANNED,
    ).rag_triad

    assert triad is not None
    assert triad.status == RagTriadStatus.PLANNED
    assert triad.passed is None
    assert triad.aggregate_score is None


def test_payload_is_serializable_and_auditable() -> None:
    payload = build_run_result(build_complete_triad()).rag_triad_payload

    assert payload is not None
    assert payload["status"] == "passed"
    assert payload["aggregate_score"] == (pytest.approx(0.90))
    assert payload["passed"] is True
    assert payload["is_complete"] is True
    assert len(payload["axes"]) == 3
    assert payload["metadata"]["run_id"] == ("run-rag-triad-001")


def test_unrelated_metrics_are_ignored() -> None:
    result = build_run_result(
        build_complete_triad() + (build_metric_result("financial-safety"),)
    )

    triad = result.rag_triad

    assert triad is not None
    assert tuple(axis.metric_id for axis in triad.axes) == RAG_TRIAD_METRIC_IDS

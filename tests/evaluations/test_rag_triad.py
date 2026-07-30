from __future__ import annotations

import pytest

from src.evaluation.deepeval_metrics import (
    MetricExecutionMode,
)
from src.evaluation.deepeval_runner import (
    MetricRunResult,
    MetricRunStatus,
)
from src.evaluation.rag_triad import (
    RAG_TRIAD_METRIC_IDS,
    RagTriadAggregationError,
    RagTriadStatus,
    aggregate_rag_triad,
)


def build_result(
    metric_id: str,
    *,
    status: MetricRunStatus = MetricRunStatus.PASSED,
    score: float | None = 0.90,
    threshold: float | None = 0.80,
    passed: bool | None = True,
    duration_ms: float = 10.0,
    estimated_cost: float = 0.01,
) -> MetricRunResult:
    return MetricRunResult(
        metric_id=metric_id,
        status=status,
        execution_mode=(
            MetricExecutionMode.LIVE_OPT_IN
        ),
        score=score,
        threshold=threshold,
        passed=passed,
        reason=None,
        duration_ms=duration_ms,
        estimated_cost=estimated_cost,
    )


def build_complete_results(
) -> tuple[MetricRunResult, ...]:
    return tuple(
        build_result(metric_id)
        for metric_id in RAG_TRIAD_METRIC_IDS
    )


def test_rag_triad_metric_ids_are_stable() -> None:
    assert RAG_TRIAD_METRIC_IDS == (
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    )


def test_complete_passing_triad_is_approved() -> None:
    result = aggregate_rag_triad(
        build_complete_results(),
        require_complete=True,
    )

    assert result.status == RagTriadStatus.PASSED
    assert result.passed is True
    assert result.is_complete is True
    assert result.missing_metric_ids == ()
    assert result.failing_metric_ids == ()
    assert result.aggregate_score == pytest.approx(
        0.90
    )
    assert result.total_duration_ms == 30.0
    assert result.total_estimated_cost == (
        pytest.approx(0.03)
    )


def test_failed_axis_fails_triad() -> None:
    results = list(build_complete_results())
    results[1] = build_result(
        "faithfulness",
        status=MetricRunStatus.FAILED,
        score=0.60,
        passed=False,
    )

    result = aggregate_rag_triad(results)

    assert result.status == RagTriadStatus.FAILED
    assert result.passed is False
    assert result.failing_metric_ids == (
        "faithfulness",
    )


def test_blocked_axis_blocks_triad() -> None:
    results = list(build_complete_results())
    results[2] = build_result(
        "contextual-relevancy",
        status=MetricRunStatus.BLOCKED,
        score=None,
        passed=None,
    )

    result = aggregate_rag_triad(results)

    assert result.status == RagTriadStatus.BLOCKED
    assert result.passed is False
    assert result.aggregate_score == pytest.approx(
        0.90
    )


def test_error_axis_marks_triad_error() -> None:
    results = list(build_complete_results())
    results[0] = build_result(
        "answer-relevancy",
        status=MetricRunStatus.ERROR,
        score=None,
        passed=None,
    )

    result = aggregate_rag_triad(results)

    assert result.status == RagTriadStatus.ERROR
    assert result.passed is False


def test_dry_run_triad_is_planned() -> None:
    results = tuple(
        build_result(
            metric_id,
            status=MetricRunStatus.PLANNED,
            score=None,
            passed=None,
            estimated_cost=0.0,
        )
        for metric_id in RAG_TRIAD_METRIC_IDS
    )

    result = aggregate_rag_triad(results)

    assert result.status == RagTriadStatus.PLANNED
    assert result.passed is None
    assert result.aggregate_score is None


def test_incomplete_triad_is_partial() -> None:
    result = aggregate_rag_triad(
        build_complete_results()[:2]
    )

    assert result.status == RagTriadStatus.PARTIAL
    assert result.passed is None
    assert result.is_complete is False
    assert result.missing_metric_ids == (
        "contextual-relevancy",
    )


def test_empty_results_are_unavailable() -> None:
    result = aggregate_rag_triad(())

    assert result.status == (
        RagTriadStatus.UNAVAILABLE
    )
    assert result.axes == ()
    assert result.aggregate_score is None
    assert result.passed is None
    assert result.missing_metric_ids == (
        RAG_TRIAD_METRIC_IDS
    )


def test_unrelated_metrics_are_ignored() -> None:
    result = aggregate_rag_triad(
        (
            build_result(
                "answer-relevancy"
            ),
            build_result(
                "financial-quality"
            ),
        )
    )

    assert tuple(
        axis.metric_id
        for axis in result.axes
    ) == (
        "answer-relevancy",
    )


def test_duplicate_triad_metric_is_rejected() -> None:
    with pytest.raises(
        RagTriadAggregationError,
        match="duplicado",
    ):
        aggregate_rag_triad(
            (
                build_result(
                    "faithfulness"
                ),
                build_result(
                    "faithfulness"
                ),
            )
        )


def test_require_complete_rejects_missing_axis() -> None:
    with pytest.raises(
        RagTriadAggregationError,
        match="incompleta",
    ):
        aggregate_rag_triad(
            build_complete_results()[:2],
            require_complete=True,
        )


def test_result_serialization_is_auditable() -> None:
    result = aggregate_rag_triad(
        build_complete_results(),
        metadata={
            "dataset_version": "1.0.0",
            "model": "gemini",
        },
    )

    payload = result.to_dict()

    assert payload["status"] == "passed"
    assert payload["passed"] is True
    assert payload["is_complete"] is True
    assert len(payload["axes"]) == 3
    assert payload["metadata"] == {
        "dataset_version": "1.0.0",
        "model": "gemini",
    }


def test_scores_by_metric_is_read_only() -> None:
    result = aggregate_rag_triad(
        build_complete_results()
    )

    with pytest.raises(TypeError):
        result.scores_by_metric[
            "faithfulness"
        ] = 0.0

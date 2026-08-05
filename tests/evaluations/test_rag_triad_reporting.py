from __future__ import annotations

from dataclasses import replace

from src.evaluation.batch_runner import (
    EvaluationBatchRunner,
)
from src.evaluation.case_catalog import (
    build_core_dataset,
)
from src.evaluation.deepeval_metrics import (
    MetricExecutionMode,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunnerSettings,
    EvaluationRunStatus,
    MetricRunResult,
    MetricRunStatus,
)
from src.evaluation.deterministic_executors import (
    build_deterministic_runner,
)
from src.evaluation.payload_providers import (
    SyntheticPassingPayloadProvider,
)
from src.evaluation.rag_triad import (
    RAG_TRIAD_METRIC_IDS,
)
from src.evaluation.reporting import (
    batch_report_to_json,
    build_batch_report,
)


def _metric_result(
    metric_id: str,
) -> MetricRunResult:
    return MetricRunResult(
        metric_id=metric_id,
        status=MetricRunStatus.PASSED,
        execution_mode=(MetricExecutionMode.LIVE_OPT_IN),
        score=0.90,
        threshold=0.80,
        passed=True,
        reason="Métrica aprovada.",
        duration_ms=10.0,
        estimated_cost=0.01,
        metadata={
            "private_detail": ("não exportar externamente"),
        },
    )


def _batch_with_rag_triad():
    batch = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(SyntheticPassingPayloadProvider()),
    ).run(
        (build_core_dataset(),),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
    )

    first_case = batch.case_results[0]

    assert first_case.evaluation is not None

    rag_evaluation = replace(
        first_case.evaluation,
        category="rag",
        profile_id="rag-profile",
        mode=EvaluationRunMode.LIVE,
        status=EvaluationRunStatus.PASSED,
        metric_results=tuple(
            _metric_result(metric_id) for metric_id in RAG_TRIAD_METRIC_IDS
        ),
        total_estimated_cost=0.03,
        deepeval_live_enabled=True,
    )

    rag_case = replace(
        first_case,
        category="rag",
        evaluation=rag_evaluation,
    )

    return replace(
        batch,
        case_results=(
            rag_case,
            *batch.case_results[1:],
        ),
    )


def test_internal_report_contains_complete_triad() -> None:
    report = build_batch_report(
        _batch_with_rag_triad(),
        sanitize=False,
    )

    evaluation = report["cases"][0]["evaluation"]

    triad = evaluation["rag_triad"]

    assert triad["status"] == "passed"
    assert triad["aggregate_score"] == 0.90
    assert triad["passed"] is True
    assert triad["is_complete"] is True
    assert triad["missing_metric_ids"] == []
    assert triad["failing_metric_ids"] == []
    assert len(triad["axes"]) == 3

    assert triad["metadata"]["profile_id"] == ("rag-profile")


def test_external_report_contains_safe_triad() -> None:
    report = build_batch_report(
        _batch_with_rag_triad(),
        sanitize=True,
    )

    triad = report["cases"][0]["rag_triad"]

    assert set(triad) == {
        "status",
        "aggregate_score",
        "passed",
        "is_complete",
        "missing_metric_ids",
        "failing_metric_ids",
        "axes",
    }

    assert triad["status"] == "passed"
    assert triad["aggregate_score"] == 0.90
    assert triad["passed"] is True
    assert len(triad["axes"]) == 3

    assert all(
        set(axis)
        == {
            "metric_id",
            "status",
            "score",
            "threshold",
            "passed",
        }
        for axis in triad["axes"]
    )

    assert "metadata" not in triad
    assert "reason" not in triad

    serialized = str(triad)

    assert "private_detail" not in serialized
    assert "não exportar externamente" not in serialized


def test_non_rag_cases_keep_previous_shape() -> None:
    report = build_batch_report(
        _batch_with_rag_triad(),
        sanitize=True,
    )

    non_rag_case = report["cases"][1]

    assert "rag_triad" not in non_rag_case

    assert set(non_rag_case) == {
        "dataset_id",
        "case_id",
        "category",
        "status",
        "has_evaluation",
        "error_type",
    }


def test_internal_json_serializes_rag_triad() -> None:
    content = batch_report_to_json(
        _batch_with_rag_triad(),
        sanitize=False,
    )

    assert '"rag_triad"' in content
    assert '"aggregate_score": 0.9' in content


def test_external_json_does_not_export_reasons() -> None:
    content = batch_report_to_json(
        _batch_with_rag_triad(),
        sanitize=True,
    )

    assert '"rag_triad"' in content
    assert '"private_detail"' not in content
    assert "não exportar externamente" not in content

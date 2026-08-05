from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from time import perf_counter
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from src.evaluation.datasets import (
    EvaluationDataset,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunner,
    EvaluationRunnerSettings,
    EvaluationRunResult,
    EvaluationRunStatus,
)
from src.evaluation.payload_providers import (
    EvaluationPayloadProvider,
)


class BatchRunStatus(StrEnum):
    """Status agregado de uma execução em lote."""

    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    ERROR = "error"


class BatchCaseStatus(StrEnum):
    """Status normalizado de um caso no lote."""

    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PARTIAL = "partial"
    PLANNED = "planned"
    ERROR = "error"


class BatchRunnerError(RuntimeError):
    """Erro base da execução em lote."""


@dataclass(frozen=True, slots=True)
class BatchCaseResult:
    dataset_id: str
    case_id: str
    category: str
    status: BatchCaseStatus
    evaluation: EvaluationRunResult | None
    error_type: str | None = None
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == BatchCaseStatus.PASSED


@dataclass(frozen=True, slots=True)
class DatasetBatchSummary:
    dataset_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    blocked_cases: int
    partial_cases: int
    planned_cases: int
    error_cases: int

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0

        return self.passed_cases / self.total_cases


@dataclass(frozen=True, slots=True)
class CategoryBatchSummary:
    category: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0

        return self.passed_cases / self.total_cases


@dataclass(frozen=True, slots=True)
class MetricBatchSummary:
    metric_id: str
    total_executions: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    errors: int
    average_score: float | None

    @property
    def pass_rate(self) -> float:
        evaluated = self.passed + self.failed

        if evaluated == 0:
            return 0.0

        return self.passed / evaluated


@dataclass(frozen=True, slots=True)
class BatchRunResult:
    batch_id: str
    schema_version: str
    status: BatchRunStatus
    started_at: datetime
    finished_at: datetime
    duration_ms: float
    case_results: tuple[BatchCaseResult, ...]
    dataset_summaries: tuple[
        DatasetBatchSummary,
        ...,
    ]
    category_summaries: tuple[
        CategoryBatchSummary,
        ...,
    ]
    metric_summaries: tuple[
        MetricBatchSummary,
        ...,
    ]
    total_estimated_cost: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise ValueError("batch_id não pode ser vazio.")

        if self.started_at.tzinfo is None:
            raise ValueError("started_at precisa de timezone.")

        if self.finished_at.tzinfo is None:
            raise ValueError("finished_at precisa de timezone.")

        if self.finished_at < self.started_at:
            raise ValueError("finished_at não pode ser anterior a started_at.")

        if self.duration_ms < 0:
            raise ValueError("duration_ms não pode ser negativo.")

        if self.total_estimated_cost < 0:
            raise ValueError("total_estimated_cost não pode ser negativo.")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def total_cases(self) -> int:
        return len(self.case_results)

    @property
    def passed_cases(self) -> int:
        return sum(
            result.status == BatchCaseStatus.PASSED for result in self.case_results
        )

    @property
    def failed_cases(self) -> int:
        return sum(
            result.status == BatchCaseStatus.FAILED for result in self.case_results
        )

    @property
    def blocked_cases(self) -> int:
        return sum(
            result.status == BatchCaseStatus.BLOCKED for result in self.case_results
        )

    @property
    def error_cases(self) -> int:
        return sum(
            result.status == BatchCaseStatus.ERROR for result in self.case_results
        )

    @property
    def pass_rate(self) -> float:
        if not self.case_results:
            return 0.0

        return self.passed_cases / len(self.case_results)


class EvaluationBatchRunner:
    """
    Executa múltiplos datasets com isolamento por caso.

    Uma falha do payload provider ou de um caso não interrompe os
    demais casos, salvo quando continue_on_case_error=False.
    """

    def __init__(
        self,
        *,
        runner: EvaluationRunner,
        payload_provider: EvaluationPayloadProvider,
    ) -> None:
        self._runner = runner
        self._payload_provider = payload_provider

    def run(
        self,
        datasets: Iterable[EvaluationDataset],
        *,
        runner_settings: EvaluationRunnerSettings,
        continue_on_case_error: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> BatchRunResult:
        resolved_datasets = tuple(datasets)

        started_at = datetime.now(UTC)
        started_counter = perf_counter()

        case_results: list[BatchCaseResult] = []

        for dataset in resolved_datasets:
            for case in dataset.cases:
                try:
                    payload = self._payload_provider(case)

                    evaluation = self._runner.run(
                        case,
                        payload,
                        settings=runner_settings,
                        metadata={
                            "batch_dataset_id": (dataset.dataset_id),
                        },
                    )

                    case_results.append(
                        BatchCaseResult(
                            dataset_id=(dataset.dataset_id),
                            case_id=case.case_id,
                            category=case.category,
                            status=(_map_evaluation_status(evaluation.status)),
                            evaluation=evaluation,
                        )
                    )
                except Exception as error:
                    case_results.append(
                        BatchCaseResult(
                            dataset_id=(dataset.dataset_id),
                            case_id=case.case_id,
                            category=case.category,
                            status=(BatchCaseStatus.ERROR),
                            evaluation=None,
                            error_type=(type(error).__name__),
                            error_message=str(error),
                        )
                    )

                    if not continue_on_case_error:
                        break

            if (
                not continue_on_case_error
                and case_results
                and case_results[-1].status == BatchCaseStatus.ERROR
            ):
                break

        finished_at = datetime.now(UTC)

        duration_ms = (perf_counter() - started_counter) * 1000

        dataset_summaries = _build_dataset_summaries(case_results)

        category_summaries = _build_category_summaries(case_results)

        metric_summaries = _build_metric_summaries(case_results)

        total_cost = sum(
            result.evaluation.total_estimated_cost
            for result in case_results
            if result.evaluation is not None
        )

        status = _aggregate_batch_status(case_results)

        return BatchRunResult(
            batch_id=uuid4().hex,
            schema_version="1.0.0",
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            case_results=tuple(case_results),
            dataset_summaries=(dataset_summaries),
            category_summaries=(category_summaries),
            metric_summaries=metric_summaries,
            total_estimated_cost=total_cost,
            metadata=dict(metadata or {}),
        )


def _map_evaluation_status(
    status: EvaluationRunStatus,
) -> BatchCaseStatus:
    mapping = {
        EvaluationRunStatus.PASSED: (BatchCaseStatus.PASSED),
        EvaluationRunStatus.FAILED: (BatchCaseStatus.FAILED),
        EvaluationRunStatus.BLOCKED: (BatchCaseStatus.BLOCKED),
        EvaluationRunStatus.PARTIAL: (BatchCaseStatus.PARTIAL),
        EvaluationRunStatus.PLANNED: (BatchCaseStatus.PLANNED),
        EvaluationRunStatus.ERROR: (BatchCaseStatus.ERROR),
    }

    return mapping[status]


def _aggregate_batch_status(
    case_results: list[BatchCaseResult],
) -> BatchRunStatus:
    if not case_results:
        return BatchRunStatus.ERROR

    statuses = {result.status for result in case_results}

    if statuses == {BatchCaseStatus.PASSED}:
        return BatchRunStatus.PASSED

    if BatchCaseStatus.ERROR in statuses and len(statuses) == 1:
        return BatchRunStatus.ERROR

    if BatchCaseStatus.FAILED in statuses or BatchCaseStatus.BLOCKED in statuses:
        return BatchRunStatus.FAILED

    return BatchRunStatus.PARTIAL


def _build_dataset_summaries(
    results: list[BatchCaseResult],
) -> tuple[DatasetBatchSummary, ...]:
    grouped: dict[
        str,
        list[BatchCaseResult],
    ] = defaultdict(list)

    for result in results:
        grouped[result.dataset_id].append(result)

    summaries: list[DatasetBatchSummary] = []

    for dataset_id in sorted(grouped):
        items = grouped[dataset_id]

        counter = Counter(item.status for item in items)

        summaries.append(
            DatasetBatchSummary(
                dataset_id=dataset_id,
                total_cases=len(items),
                passed_cases=counter[BatchCaseStatus.PASSED],
                failed_cases=counter[BatchCaseStatus.FAILED],
                blocked_cases=counter[BatchCaseStatus.BLOCKED],
                partial_cases=counter[BatchCaseStatus.PARTIAL],
                planned_cases=counter[BatchCaseStatus.PLANNED],
                error_cases=counter[BatchCaseStatus.ERROR],
            )
        )

    return tuple(summaries)


def _build_category_summaries(
    results: list[BatchCaseResult],
) -> tuple[CategoryBatchSummary, ...]:
    grouped: dict[
        str,
        list[BatchCaseResult],
    ] = defaultdict(list)

    for result in results:
        grouped[result.category].append(result)

    summaries: list[CategoryBatchSummary] = []

    for category in sorted(grouped):
        items = grouped[category]

        summaries.append(
            CategoryBatchSummary(
                category=category,
                total_cases=len(items),
                passed_cases=sum(
                    item.status == BatchCaseStatus.PASSED for item in items
                ),
                failed_cases=sum(
                    item.status
                    in {
                        BatchCaseStatus.FAILED,
                        BatchCaseStatus.BLOCKED,
                    }
                    for item in items
                ),
                error_cases=sum(item.status == BatchCaseStatus.ERROR for item in items),
            )
        )

    return tuple(summaries)


def _build_metric_summaries(
    results: list[BatchCaseResult],
) -> tuple[MetricBatchSummary, ...]:
    grouped: dict[
        str,
        list[Any],
    ] = defaultdict(list)

    for result in results:
        if result.evaluation is None:
            continue

        for metric in result.evaluation.metric_results:
            grouped[metric.metric_id].append(metric)

    summaries: list[MetricBatchSummary] = []

    for metric_id in sorted(grouped):
        metrics = grouped[metric_id]

        scores = tuple(metric.score for metric in metrics if metric.score is not None)

        average_score = sum(scores) / len(scores) if scores else None

        counter = Counter(metric.status.value for metric in metrics)

        summaries.append(
            MetricBatchSummary(
                metric_id=metric_id,
                total_executions=len(metrics),
                passed=counter["passed"],
                failed=counter["failed"],
                blocked=counter["blocked"],
                skipped=counter["skipped"],
                errors=counter["error"],
                average_score=average_score,
            )
        )

    return tuple(summaries)


__all__ = [
    "BatchCaseResult",
    "BatchCaseStatus",
    "BatchRunResult",
    "BatchRunnerError",
    "BatchRunStatus",
    "CategoryBatchSummary",
    "DatasetBatchSummary",
    "EvaluationBatchRunner",
    "MetricBatchSummary",
]

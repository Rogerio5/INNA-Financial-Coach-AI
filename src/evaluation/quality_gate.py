from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from src.evaluation.batch_runner import (
    BatchRunResult,
    BatchRunStatus,
)


class QualityGateSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QualityGateRule(StrEnum):
    BATCH_STATUS = "batch-status"
    MINIMUM_PASS_RATE = "minimum-pass-rate"
    MAXIMUM_FAILED_CASES = "maximum-failed-cases"
    MAXIMUM_BLOCKED_CASES = "maximum-blocked-cases"
    MAXIMUM_ERROR_CASES = "maximum-error-cases"
    MAXIMUM_TOTAL_COST = "maximum-total-cost"
    CRITICAL_METRIC = "critical-metric"
    REQUIRED_DATASET = "required-dataset"
    SYNTHETIC_PRODUCTION_MISMATCH = "synthetic-production-mismatch"


@dataclass(frozen=True, slots=True)
class QualityGateViolation:
    rule: QualityGateRule
    severity: QualityGateSeverity
    message: str
    actual: Any = None
    expected: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        message = self.message.strip()

        if not message:
            raise ValueError("message não pode ser vazia.")

        object.__setattr__(
            self,
            "message",
            message,
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class QualityGateSettings:
    minimum_pass_rate: float = 1.0
    maximum_failed_cases: int = 0
    maximum_blocked_cases: int = 0
    maximum_error_cases: int = 0
    maximum_total_cost: float | None = None
    critical_metric_ids: tuple[str, ...] = (
        "contract-validation",
        "forbidden-terms",
        "human-review-policy",
        "retrieval-contract",
    )
    required_dataset_ids: tuple[str, ...] = (
        "inna-core@1.0.0",
        "inna-safety@1.0.0",
        "inna-conversation@1.0.0",
    )
    require_production_execution: bool = False
    fail_on_warning: bool = False

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.minimum_pass_rate) <= 1.0):
            raise ValueError("minimum_pass_rate deve estar entre 0 e 1.")

        for field_name in (
            "maximum_failed_cases",
            "maximum_blocked_cases",
            "maximum_error_cases",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} não pode ser negativo.")

        if self.maximum_total_cost is not None and self.maximum_total_cost < 0:
            raise ValueError("maximum_total_cost não pode ser negativo.")

        critical_metric_ids = tuple(
            dict.fromkeys(
                metric_id.strip().casefold()
                for metric_id in self.critical_metric_ids
                if metric_id.strip()
            )
        )

        required_dataset_ids = tuple(
            dict.fromkeys(
                dataset_id.strip()
                for dataset_id in self.required_dataset_ids
                if dataset_id.strip()
            )
        )

        object.__setattr__(
            self,
            "minimum_pass_rate",
            float(self.minimum_pass_rate),
        )
        object.__setattr__(
            self,
            "critical_metric_ids",
            critical_metric_ids,
        )
        object.__setattr__(
            self,
            "required_dataset_ids",
            required_dataset_ids,
        )


@dataclass(frozen=True, slots=True)
class QualityGateResult:
    passed: bool
    violations: tuple[
        QualityGateViolation,
        ...,
    ]
    evaluated_rules: int
    batch_id: str

    @property
    def critical_violations(
        self,
    ) -> tuple[QualityGateViolation, ...]:
        return tuple(
            violation
            for violation in self.violations
            if violation.severity == QualityGateSeverity.CRITICAL
        )

    @property
    def error_violations(
        self,
    ) -> tuple[QualityGateViolation, ...]:
        return tuple(
            violation
            for violation in self.violations
            if violation.severity == QualityGateSeverity.ERROR
        )

    @property
    def warning_violations(
        self,
    ) -> tuple[QualityGateViolation, ...]:
        return tuple(
            violation
            for violation in self.violations
            if violation.severity == QualityGateSeverity.WARNING
        )


def evaluate_quality_gate(
    batch: BatchRunResult,
    settings: QualityGateSettings | None = None,
) -> QualityGateResult:
    resolved = settings or QualityGateSettings()

    violations: list[QualityGateViolation] = []

    evaluated_rules = 0

    evaluated_rules += 1

    if batch.status != BatchRunStatus.PASSED:
        violations.append(
            QualityGateViolation(
                rule=QualityGateRule.BATCH_STATUS,
                severity=QualityGateSeverity.ERROR,
                message=("O lote não terminou com status aprovado."),
                actual=batch.status.value,
                expected=BatchRunStatus.PASSED.value,
            )
        )

    evaluated_rules += 1

    if batch.pass_rate < resolved.minimum_pass_rate:
        violations.append(
            QualityGateViolation(
                rule=(QualityGateRule.MINIMUM_PASS_RATE),
                severity=QualityGateSeverity.ERROR,
                message=("A taxa de aprovação ficou abaixo do limite definido."),
                actual=batch.pass_rate,
                expected=resolved.minimum_pass_rate,
            )
        )

    evaluated_rules += 1

    if batch.failed_cases > resolved.maximum_failed_cases:
        violations.append(
            QualityGateViolation(
                rule=(QualityGateRule.MAXIMUM_FAILED_CASES),
                severity=QualityGateSeverity.ERROR,
                message=("O lote excedeu o máximo de casos reprovados."),
                actual=batch.failed_cases,
                expected=(resolved.maximum_failed_cases),
            )
        )

    evaluated_rules += 1

    if batch.blocked_cases > resolved.maximum_blocked_cases:
        violations.append(
            QualityGateViolation(
                rule=(QualityGateRule.MAXIMUM_BLOCKED_CASES),
                severity=QualityGateSeverity.ERROR,
                message=("O lote excedeu o máximo de casos bloqueados."),
                actual=batch.blocked_cases,
                expected=(resolved.maximum_blocked_cases),
            )
        )

    evaluated_rules += 1

    if batch.error_cases > resolved.maximum_error_cases:
        violations.append(
            QualityGateViolation(
                rule=(QualityGateRule.MAXIMUM_ERROR_CASES),
                severity=(QualityGateSeverity.CRITICAL),
                message=("O lote excedeu o máximo de casos com erro técnico."),
                actual=batch.error_cases,
                expected=resolved.maximum_error_cases,
            )
        )

    if resolved.maximum_total_cost is not None:
        evaluated_rules += 1

        if batch.total_estimated_cost > resolved.maximum_total_cost:
            violations.append(
                QualityGateViolation(
                    rule=(QualityGateRule.MAXIMUM_TOTAL_COST),
                    severity=(QualityGateSeverity.ERROR),
                    message=("O custo estimado do lote excedeu o limite permitido."),
                    actual=batch.total_estimated_cost,
                    expected=(resolved.maximum_total_cost),
                )
            )

    metric_summaries = {
        summary.metric_id: summary for summary in batch.metric_summaries
    }

    for metric_id in resolved.critical_metric_ids:
        evaluated_rules += 1

        summary = metric_summaries.get(metric_id)

        if summary is None:
            violations.append(
                QualityGateViolation(
                    rule=(QualityGateRule.CRITICAL_METRIC),
                    severity=(QualityGateSeverity.WARNING),
                    message=("A métrica crítica não foi executada no lote."),
                    actual=None,
                    expected=metric_id,
                    metadata={
                        "metric_id": metric_id,
                    },
                )
            )
            continue

        if summary.failed > 0 or summary.blocked > 0 or summary.errors > 0:
            violations.append(
                QualityGateViolation(
                    rule=(QualityGateRule.CRITICAL_METRIC),
                    severity=(QualityGateSeverity.CRITICAL),
                    message=("Uma métrica crítica apresentou falha, bloqueio ou erro."),
                    actual={
                        "failed": summary.failed,
                        "blocked": summary.blocked,
                        "errors": summary.errors,
                    },
                    expected={
                        "failed": 0,
                        "blocked": 0,
                        "errors": 0,
                    },
                    metadata={
                        "metric_id": metric_id,
                    },
                )
            )

    dataset_ids = {summary.dataset_id for summary in batch.dataset_summaries}

    for dataset_id in resolved.required_dataset_ids:
        evaluated_rules += 1

        if dataset_id not in dataset_ids:
            violations.append(
                QualityGateViolation(
                    rule=(QualityGateRule.REQUIRED_DATASET),
                    severity=(QualityGateSeverity.ERROR),
                    message=("Um dataset obrigatório não foi executado."),
                    actual=tuple(sorted(dataset_ids)),
                    expected=dataset_id,
                )
            )

    if resolved.require_production_execution:
        evaluated_rules += 1

        production_execution = bool(
            batch.metadata.get(
                "production_evaluation",
                batch.metadata.get(
                    "production_execution",
                    False,
                ),
            )
        )

        if not production_execution:
            violations.append(
                QualityGateViolation(
                    rule=(QualityGateRule.SYNTHETIC_PRODUCTION_MISMATCH),
                    severity=(QualityGateSeverity.CRITICAL),
                    message=(
                        "O quality gate exige execução "
                        "real da aplicação, mas o lote foi "
                        "marcado como sintético."
                    ),
                    actual=False,
                    expected=True,
                )
            )

    blocking_severities = {
        QualityGateSeverity.ERROR,
        QualityGateSeverity.CRITICAL,
    }

    if resolved.fail_on_warning:
        blocking_severities.add(QualityGateSeverity.WARNING)

    passed = not any(
        violation.severity in blocking_severities for violation in violations
    )

    return QualityGateResult(
        passed=passed,
        violations=tuple(violations),
        evaluated_rules=evaluated_rules,
        batch_id=batch.batch_id,
    )


__all__ = [
    "QualityGateResult",
    "QualityGateRule",
    "QualityGateSettings",
    "QualityGateSeverity",
    "QualityGateViolation",
    "evaluate_quality_gate",
]

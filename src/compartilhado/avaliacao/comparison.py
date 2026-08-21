from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from src.compartilhado.avaliacao.baseline import (
    BaselineSchemaError,
    EvaluationBaseline,
    load_baseline,
    load_json_object,
)

ComparisonStatus = Literal[
    "improved",
    "stable",
    "regressed",
    "missing",
    "new",
]


class ComparisonError(RuntimeError):
    """Erro base da comparação de avaliações."""


class EvaluationRegressionError(ComparisonError):
    """A avaliação atual contém regressão bloqueante."""


def _number(
    value: object,
    *,
    field_name: str,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise BaselineSchemaError(
            f"{field_name} deve ser numérico."
        )

    return float(value)


def _text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BaselineSchemaError(
            f"{field_name} deve ser texto não vazio."
        )

    return value.strip()


def _mapping(
    value: object,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BaselineSchemaError(
            f"{field_name} deve ser um objeto."
        )

    return value


def _sequence(
    value: object,
    *,
    field_name: str,
) -> Sequence[Any]:
    if not isinstance(value, list):
        raise BaselineSchemaError(
            f"{field_name} deve ser uma lista."
        )

    return value


def _extract_identifiers(
    items: Sequence[Any],
    *,
    collection_name: str,
    candidate_fields: tuple[str, ...],
) -> tuple[str, ...]:
    identifiers: list[str] = []

    for index, raw_item in enumerate(items):
        item = _mapping(
            raw_item,
            field_name=(
                f"{collection_name}[{index}]"
            ),
        )

        identifier: object = None

        for candidate in candidate_fields:
            value = item.get(candidate)

            if isinstance(value, str) and value.strip():
                identifier = value
                break

        identifiers.append(
            _text(
                identifier,
                field_name=(
                    f"{collection_name}[{index}]"
                    f".{candidate_fields[0]}"
                ),
            )
        )

    if len(identifiers) != len(set(identifiers)):
        raise BaselineSchemaError(
            f"{collection_name} possui identificadores "
            "duplicados."
        )

    return tuple(sorted(identifiers))


@dataclass(frozen=True, slots=True)
class CurrentMetric:
    metric_id: str
    average_score: float
    total_executions: int
    passed: int
    failed: int
    blocked: int
    errors: int
    skipped: int

    @classmethod
    def from_report_entry(
        cls,
        payload: Mapping[str, Any],
    ) -> CurrentMetric:
        metric_id = _text(
            payload.get("metric_id"),
            field_name="metrics[].metric_id",
        )

        integer_values: dict[str, int] = {}

        for field_name in (
            "total_executions",
            "passed",
            "failed",
            "blocked",
            "errors",
            "skipped",
        ):
            value = payload.get(field_name)

            if isinstance(value, bool) or not isinstance(
                value,
                int,
            ):
                raise BaselineSchemaError(
                    f"metrics[{metric_id}]."
                    f"{field_name} deve ser inteiro."
                )

            if value < 0:
                raise BaselineSchemaError(
                    f"metrics[{metric_id}]."
                    f"{field_name} não pode ser negativo."
                )

            integer_values[field_name] = value

        average_score = _number(
            payload.get("average_score"),
            field_name=(
                f"metrics[{metric_id}].average_score"
            ),
        )

        if not 0.0 <= average_score <= 1.0:
            raise BaselineSchemaError(
                f"metrics[{metric_id}].average_score "
                "deve estar entre 0 e 1."
            )

        return cls(
            metric_id=metric_id,
            average_score=average_score,
            **integer_values,
        )


@dataclass(frozen=True, slots=True)
class MetricComparison:
    metric_id: str
    baseline_score: float | None
    current_score: float | None
    delta: float | None
    allowed_regression: float
    status: ComparisonStatus
    blocking: bool
    critical: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "baseline_score": self.baseline_score,
            "current_score": self.current_score,
            "delta": self.delta,
            "allowed_regression": (
                self.allowed_regression
            ),
            "status": self.status,
            "blocking": self.blocking,
            "critical": self.critical,
        }


@dataclass(frozen=True, slots=True)
class EvaluationComparison:
    baseline_id: str
    current_run_reference: str
    baseline_pass_rate: float
    current_pass_rate: float
    pass_rate_delta: float
    quality_gate_passed: bool
    metrics: tuple[MetricComparison, ...]
    missing_case_ids: tuple[str, ...]
    new_case_ids: tuple[str, ...]
    missing_dataset_ids: tuple[str, ...]
    new_dataset_ids: tuple[str, ...]
    violations: tuple[str, ...]
    passed: bool

    @property
    def regressed_metrics(
        self,
    ) -> tuple[MetricComparison, ...]:
        return tuple(
            metric
            for metric in self.metrics
            if metric.status == "regressed"
        )

    @property
    def blocking_metrics(
        self,
    ) -> tuple[MetricComparison, ...]:
        return tuple(
            metric
            for metric in self.metrics
            if metric.blocking
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparison_schema_version": "1.0.0",
            "baseline_id": self.baseline_id,
            "current_run_reference": (
                self.current_run_reference
            ),
            "baseline_pass_rate": (
                self.baseline_pass_rate
            ),
            "current_pass_rate": (
                self.current_pass_rate
            ),
            "pass_rate_delta": (
                self.pass_rate_delta
            ),
            "quality_gate_passed": (
                self.quality_gate_passed
            ),
            "passed": self.passed,
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
            "missing_case_ids": list(
                self.missing_case_ids
            ),
            "new_case_ids": list(
                self.new_case_ids
            ),
            "missing_dataset_ids": list(
                self.missing_dataset_ids
            ),
            "new_dataset_ids": list(
                self.new_dataset_ids
            ),
            "violations": list(self.violations),
        }


def compare_report_to_baseline(
    baseline: EvaluationBaseline,
    report: Mapping[str, Any],
    *,
    maximum_metric_regression: float = 0.05,
    maximum_pass_rate_regression: float = 0.05,
    critical_metric_ids: frozenset[str] | None = None,
    block_missing_cases: bool = True,
    block_missing_datasets: bool = True,
    block_missing_metrics: bool = True,
) -> EvaluationComparison:
    if not 0.0 <= maximum_metric_regression <= 1.0:
        raise ValueError(
            "maximum_metric_regression deve estar "
            "entre 0 e 1."
        )

    if not 0.0 <= maximum_pass_rate_regression <= 1.0:
        raise ValueError(
            "maximum_pass_rate_regression deve estar "
            "entre 0 e 1."
        )

    critical_ids = critical_metric_ids or frozenset()

    summary = _mapping(
        report.get("summary"),
        field_name="summary",
    )

    quality_gate = _mapping(
        report.get("quality_gate"),
        field_name="quality_gate",
    )

    current_pass_rate = _number(
        summary.get("pass_rate"),
        field_name="summary.pass_rate",
    )

    if not 0.0 <= current_pass_rate <= 1.0:
        raise BaselineSchemaError(
            "summary.pass_rate deve estar entre 0 e 1."
        )

    quality_gate_passed = quality_gate.get("passed")

    if not isinstance(quality_gate_passed, bool):
        raise BaselineSchemaError(
            "quality_gate.passed deve ser booleano."
        )

    current_run_reference = _text(
        report.get("run_reference"),
        field_name="run_reference",
    )

    current_cases = _extract_identifiers(
        _sequence(
            report.get("cases"),
            field_name="cases",
        ),
        collection_name="cases",
        candidate_fields=("case_id",),
    )

    current_datasets = _extract_identifiers(
        _sequence(
            report.get("datasets"),
            field_name="datasets",
        ),
        collection_name="datasets",
        candidate_fields=(
            "dataset_id",
            "id",
            "name",
        ),
    )

    metrics_payload = _sequence(
        report.get("metrics"),
        field_name="metrics",
    )

    current_metrics: dict[str, CurrentMetric] = {}

    for index, raw_metric in enumerate(metrics_payload):
        metric = CurrentMetric.from_report_entry(
            _mapping(
                raw_metric,
                field_name=f"metrics[{index}]",
            )
        )

        if metric.metric_id in current_metrics:
            raise BaselineSchemaError(
                "O relatório atual possui metric_id "
                f"duplicado: {metric.metric_id}."
            )

        current_metrics[metric.metric_id] = metric

    baseline_metrics = {
        metric.metric_id: metric
        for metric in baseline.metrics
    }

    comparisons: list[MetricComparison] = []
    violations: list[str] = []

    metric_ids = sorted(
        set(baseline_metrics)
        | set(current_metrics)
    )

    for metric_id in metric_ids:
        baseline_metric = baseline_metrics.get(
            metric_id
        )
        current_metric = current_metrics.get(
            metric_id
        )
        critical = metric_id in critical_ids

        if baseline_metric is None:
            comparisons.append(
                MetricComparison(
                    metric_id=metric_id,
                    baseline_score=None,
                    current_score=(
                        current_metric.average_score
                        if current_metric
                        else None
                    ),
                    delta=None,
                    allowed_regression=(
                        maximum_metric_regression
                    ),
                    status="new",
                    blocking=False,
                    critical=critical,
                )
            )
            continue

        if current_metric is None:
            blocking = (
                block_missing_metrics or critical
            )

            comparisons.append(
                MetricComparison(
                    metric_id=metric_id,
                    baseline_score=(
                        baseline_metric.average_score
                    ),
                    current_score=None,
                    delta=None,
                    allowed_regression=(
                        maximum_metric_regression
                    ),
                    status="missing",
                    blocking=blocking,
                    critical=critical,
                )
            )

            if blocking:
                violations.append(
                    "Métrica obrigatória ausente: "
                    f"{metric_id}."
                )

            continue

        delta = (
            current_metric.average_score
            - baseline_metric.average_score
        )

        if delta < -maximum_metric_regression:
            status: ComparisonStatus = "regressed"
            blocking = True
            violations.append(
                "Regressão da métrica "
                f"{metric_id}: "
                f"{baseline_metric.average_score:.4f} "
                "→ "
                f"{current_metric.average_score:.4f} "
                f"(delta {delta:.4f})."
            )
        elif delta > maximum_metric_regression:
            status = "improved"
            blocking = False
        else:
            status = "stable"
            blocking = False

        if critical and current_metric.failed > 0:
            blocking = True
            violations.append(
                "Métrica crítica possui falhas: "
                f"{metric_id}="
                f"{current_metric.failed}."
            )

        if critical and (
            current_metric.blocked > 0
            or current_metric.errors > 0
        ):
            blocking = True
            violations.append(
                "Métrica crítica possui bloqueios "
                "ou erros: "
                f"{metric_id}."
            )

        comparisons.append(
            MetricComparison(
                metric_id=metric_id,
                baseline_score=(
                    baseline_metric.average_score
                ),
                current_score=(
                    current_metric.average_score
                ),
                delta=delta,
                allowed_regression=(
                    maximum_metric_regression
                ),
                status=status,
                blocking=blocking,
                critical=critical,
            )
        )

    baseline_case_ids = set(baseline.case_ids)
    current_case_ids = set(current_cases)

    missing_case_ids = tuple(
        sorted(
            baseline_case_ids
            - current_case_ids
        )
    )

    new_case_ids = tuple(
        sorted(
            current_case_ids
            - baseline_case_ids
        )
    )

    baseline_dataset_ids = set(
        baseline.dataset_ids
    )
    current_dataset_ids = set(current_datasets)

    missing_dataset_ids = tuple(
        sorted(
            baseline_dataset_ids
            - current_dataset_ids
        )
    )

    new_dataset_ids = tuple(
        sorted(
            current_dataset_ids
            - baseline_dataset_ids
        )
    )

    if block_missing_cases and missing_case_ids:
        violations.append(
            "Casos da baseline ausentes: "
            + ", ".join(missing_case_ids)
            + "."
        )

    if (
        block_missing_datasets
        and missing_dataset_ids
    ):
        violations.append(
            "Datasets da baseline ausentes: "
            + ", ".join(missing_dataset_ids)
            + "."
        )

    pass_rate_delta = (
        current_pass_rate
        - baseline.pass_rate
    )

    if (
        pass_rate_delta
        < -maximum_pass_rate_regression
    ):
        violations.append(
            "Regressão da taxa de aprovação: "
            f"{baseline.pass_rate:.4f} → "
            f"{current_pass_rate:.4f} "
            f"(delta {pass_rate_delta:.4f})."
        )

    if not quality_gate_passed:
        violations.append(
            "O quality gate da avaliação atual "
            "foi reprovado."
        )

    passed = not violations and not any(
        metric.blocking
        for metric in comparisons
    )

    return EvaluationComparison(
        baseline_id=baseline.baseline_id,
        current_run_reference=(
            current_run_reference
        ),
        baseline_pass_rate=baseline.pass_rate,
        current_pass_rate=current_pass_rate,
        pass_rate_delta=pass_rate_delta,
        quality_gate_passed=quality_gate_passed,
        metrics=tuple(comparisons),
        missing_case_ids=missing_case_ids,
        new_case_ids=new_case_ids,
        missing_dataset_ids=(
            missing_dataset_ids
        ),
        new_dataset_ids=new_dataset_ids,
        violations=tuple(violations),
        passed=passed,
    )


def compare_report_files(
    baseline_path: str | Path,
    report_path: str | Path,
    **options: Any,
) -> EvaluationComparison:
    return compare_report_to_baseline(
        load_baseline(baseline_path),
        load_json_object(report_path),
        **options,
    )


def render_comparison_markdown(
    comparison: EvaluationComparison,
) -> str:
    status = (
        "APROVADO"
        if comparison.passed
        else "REPROVADO"
    )

    lines = [
        "# Relatório de Regressão LLMOps — INNA",
        "",
        f"**Status:** {status}",
        "",
        f"- Baseline: `{comparison.baseline_id}`",
        (
            "- Execução atual: "
            f"`{comparison.current_run_reference}`"
        ),
        (
            "- Taxa de aprovação da baseline: "
            f"{comparison.baseline_pass_rate:.2%}"
        ),
        (
            "- Taxa de aprovação atual: "
            f"{comparison.current_pass_rate:.2%}"
        ),
        (
            "- Variação da taxa de aprovação: "
            f"{comparison.pass_rate_delta:+.2%}"
        ),
        (
            "- Quality Gate atual: "
            + (
                "aprovado"
                if comparison.quality_gate_passed
                else "reprovado"
            )
        ),
        "",
        "## Métricas",
        "",
        (
            "| Métrica | Baseline | Atual | Delta | "
            "Status | Bloqueante |"
        ),
        (
            "|---|---:|---:|---:|---|---|"
        ),
    ]

    for metric in comparison.metrics:
        baseline_score = (
            f"{metric.baseline_score:.4f}"
            if metric.baseline_score is not None
            else "-"
        )
        current_score = (
            f"{metric.current_score:.4f}"
            if metric.current_score is not None
            else "-"
        )
        delta = (
            f"{metric.delta:+.4f}"
            if metric.delta is not None
            else "-"
        )

        lines.append(
            "| "
            f"{metric.metric_id} | "
            f"{baseline_score} | "
            f"{current_score} | "
            f"{delta} | "
            f"{metric.status} | "
            f"{'sim' if metric.blocking else 'não'} |"
        )

    lines.extend(
        [
            "",
            "## Compatibilidade de casos e datasets",
            "",
            (
                "- Casos removidos: "
                + (
                    ", ".join(
                        comparison.missing_case_ids
                    )
                    if comparison.missing_case_ids
                    else "nenhum"
                )
            ),
            (
                "- Casos novos: "
                + (
                    ", ".join(
                        comparison.new_case_ids
                    )
                    if comparison.new_case_ids
                    else "nenhum"
                )
            ),
            (
                "- Datasets removidos: "
                + (
                    ", ".join(
                        comparison.missing_dataset_ids
                    )
                    if comparison.missing_dataset_ids
                    else "nenhum"
                )
            ),
            (
                "- Datasets novos: "
                + (
                    ", ".join(
                        comparison.new_dataset_ids
                    )
                    if comparison.new_dataset_ids
                    else "nenhum"
                )
            ),
            "",
            "## Violações",
            "",
        ]
    )

    if comparison.violations:
        lines.extend(
            f"- {violation}"
            for violation in comparison.violations
        )
    else:
        lines.append(
            "- Nenhuma regressão bloqueante."
        )

    return "\n".join(lines) + "\n"


def write_comparison_reports(
    comparison: EvaluationComparison,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    directory = Path(output_directory)
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = (
        directory / "comparison-report.json"
    )
    markdown_path = (
        directory / "comparison-report.md"
    )

    json_path.write_text(
        json.dumps(
            comparison.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path.write_text(
        render_comparison_markdown(
            comparison
        ),
        encoding="utf-8",
    )

    return json_path, markdown_path


def enforce_comparison(
    comparison: EvaluationComparison,
) -> None:
    if comparison.passed:
        return

    details = "; ".join(
        comparison.violations
    ) or "Regressão bloqueante identificada."

    raise EvaluationRegressionError(details)


__all__ = [
    "ComparisonError",
    "CurrentMetric",
    "EvaluationComparison",
    "EvaluationRegressionError",
    "MetricComparison",
    "compare_report_files",
    "compare_report_to_baseline",
    "enforce_comparison",
    "render_comparison_markdown",
    "write_comparison_reports",
]

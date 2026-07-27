from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.evaluation.baseline import (
    load_json_object,
)
from src.evaluation.comparison import (
    EvaluationComparison,
)

HISTORY_SCHEMA_VERSION = "1.0.0"


class EvaluationHistoryError(RuntimeError):
    """Erro base do histórico de avaliações."""


class EvaluationHistorySchemaError(
    EvaluationHistoryError
):
    """O histórico possui estrutura inválida."""


class DuplicateHistoryEntryError(
    EvaluationHistoryError
):
    """Já existe uma entrada para a execução."""


def _utc_now() -> str:
    return (
        datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _required_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser texto não vazio."
        )

    return value.strip()


def _required_number(
    value: object,
    *,
    field_name: str,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser numérico."
        )

    return float(value)


def _required_integer(
    value: object,
    *,
    field_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(
        value,
        int,
    ):
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser inteiro."
        )

    if value < 0:
        raise EvaluationHistorySchemaError(
            f"{field_name} não pode ser negativo."
        )

    return value


def _required_bool(
    value: object,
    *,
    field_name: str,
) -> bool:
    if not isinstance(value, bool):
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser booleano."
        )

    return value


def _required_mapping(
    value: object,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser um objeto."
        )

    return value


def _required_sequence(
    value: object,
    *,
    field_name: str,
) -> Sequence[Any]:
    if not isinstance(value, list):
        raise EvaluationHistorySchemaError(
            f"{field_name} deve ser uma lista."
        )

    return value


@dataclass(frozen=True, slots=True)
class HistoryMetric:
    metric_id: str
    average_score: float
    status: str
    delta_from_baseline: float | None

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> HistoryMetric:
        delta = payload.get(
            "delta_from_baseline"
        )

        if delta is not None:
            delta = _required_number(
                delta,
                field_name=(
                    "metrics[].delta_from_baseline"
                ),
            )

        score = _required_number(
            payload.get("average_score"),
            field_name="metrics[].average_score",
        )

        if not 0.0 <= score <= 1.0:
            raise EvaluationHistorySchemaError(
                "metrics[].average_score deve estar "
                "entre 0 e 1."
            )

        return cls(
            metric_id=_required_text(
                payload.get("metric_id"),
                field_name="metrics[].metric_id",
            ),
            average_score=score,
            status=_required_text(
                payload.get("status"),
                field_name="metrics[].status",
            ),
            delta_from_baseline=delta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "average_score": self.average_score,
            "status": self.status,
            "delta_from_baseline": (
                self.delta_from_baseline
            ),
        }


@dataclass(frozen=True, slots=True)
class EvaluationHistoryEntry:
    recorded_at: str
    run_reference: str
    report_generated_date: str
    branch: str
    commit_sha: str
    environment: str
    evaluation_mode: str
    passed: bool
    quality_gate_passed: bool
    pass_rate: float
    case_count: int
    dataset_count: int
    metric_count: int
    regression_count: int
    violation_count: int
    baseline_id: str | None
    metrics: tuple[HistoryMetric, ...]

    @classmethod
    def from_report(
        cls,
        report: Mapping[str, Any],
        *,
        comparison: EvaluationComparison | None = None,
        branch: str = "unknown",
        commit_sha: str = "unknown",
        environment: str = "local",
        evaluation_mode: str = (
            "deterministic-synthetic"
        ),
        recorded_at: str | None = None,
    ) -> EvaluationHistoryEntry:
        summary = _required_mapping(
            report.get("summary"),
            field_name="summary",
        )

        quality_gate = _required_mapping(
            report.get("quality_gate"),
            field_name="quality_gate",
        )

        cases = _required_sequence(
            report.get("cases"),
            field_name="cases",
        )

        datasets = _required_sequence(
            report.get("datasets"),
            field_name="datasets",
        )

        metrics_payload = _required_sequence(
            report.get("metrics"),
            field_name="metrics",
        )

        comparison_metrics = {}

        if comparison is not None:
            comparison_metrics = {
                metric.metric_id: metric
                for metric in comparison.metrics
            }

        metrics: list[HistoryMetric] = []

        for index, raw_metric in enumerate(
            metrics_payload
        ):
            metric = _required_mapping(
                raw_metric,
                field_name=f"metrics[{index}]",
            )

            metric_id = _required_text(
                metric.get("metric_id"),
                field_name=(
                    f"metrics[{index}].metric_id"
                ),
            )

            score = _required_number(
                metric.get("average_score"),
                field_name=(
                    f"metrics[{index}].average_score"
                ),
            )

            comparison_metric = (
                comparison_metrics.get(metric_id)
            )

            metrics.append(
                HistoryMetric(
                    metric_id=metric_id,
                    average_score=score,
                    status=(
                        comparison_metric.status
                        if comparison_metric
                        else "not-compared"
                    ),
                    delta_from_baseline=(
                        comparison_metric.delta
                        if comparison_metric
                        else None
                    ),
                )
            )

        pass_rate = _required_number(
            summary.get("pass_rate"),
            field_name="summary.pass_rate",
        )

        quality_gate_passed = _required_bool(
            quality_gate.get("passed"),
            field_name="quality_gate.passed",
        )

        return cls(
            recorded_at=recorded_at or _utc_now(),
            run_reference=_required_text(
                report.get("run_reference"),
                field_name="run_reference",
            ),
            report_generated_date=_required_text(
                report.get("generated_date"),
                field_name="generated_date",
            ),
            branch=_required_text(
                branch,
                field_name="branch",
            ),
            commit_sha=_required_text(
                commit_sha,
                field_name="commit_sha",
            ),
            environment=_required_text(
                environment,
                field_name="environment",
            ),
            evaluation_mode=_required_text(
                evaluation_mode,
                field_name="evaluation_mode",
            ),
            passed=(
                comparison.passed
                if comparison is not None
                else quality_gate_passed
            ),
            quality_gate_passed=(
                quality_gate_passed
            ),
            pass_rate=pass_rate,
            case_count=len(cases),
            dataset_count=len(datasets),
            metric_count=len(metrics),
            regression_count=(
                len(comparison.regressed_metrics)
                if comparison is not None
                else 0
            ),
            violation_count=(
                len(comparison.violations)
                if comparison is not None
                else 0
            ),
            baseline_id=(
                comparison.baseline_id
                if comparison is not None
                else None
            ),
            metrics=tuple(
                sorted(
                    metrics,
                    key=lambda item: item.metric_id,
                )
            ),
        )

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> EvaluationHistoryEntry:
        metrics = tuple(
            HistoryMetric.from_dict(
                _required_mapping(
                    raw_metric,
                    field_name=f"metrics[{index}]",
                )
            )
            for index, raw_metric in enumerate(
                _required_sequence(
                    payload.get("metrics"),
                    field_name="metrics",
                )
            )
        )

        baseline_id = payload.get("baseline_id")

        if baseline_id is not None:
            baseline_id = _required_text(
                baseline_id,
                field_name="baseline_id",
            )

        return cls(
            recorded_at=_required_text(
                payload.get("recorded_at"),
                field_name="recorded_at",
            ),
            run_reference=_required_text(
                payload.get("run_reference"),
                field_name="run_reference",
            ),
            report_generated_date=_required_text(
                payload.get(
                    "report_generated_date"
                ),
                field_name=(
                    "report_generated_date"
                ),
            ),
            branch=_required_text(
                payload.get("branch"),
                field_name="branch",
            ),
            commit_sha=_required_text(
                payload.get("commit_sha"),
                field_name="commit_sha",
            ),
            environment=_required_text(
                payload.get("environment"),
                field_name="environment",
            ),
            evaluation_mode=_required_text(
                payload.get("evaluation_mode"),
                field_name="evaluation_mode",
            ),
            passed=_required_bool(
                payload.get("passed"),
                field_name="passed",
            ),
            quality_gate_passed=_required_bool(
                payload.get(
                    "quality_gate_passed"
                ),
                field_name="quality_gate_passed",
            ),
            pass_rate=_required_number(
                payload.get("pass_rate"),
                field_name="pass_rate",
            ),
            case_count=_required_integer(
                payload.get("case_count"),
                field_name="case_count",
            ),
            dataset_count=_required_integer(
                payload.get("dataset_count"),
                field_name="dataset_count",
            ),
            metric_count=_required_integer(
                payload.get("metric_count"),
                field_name="metric_count",
            ),
            regression_count=_required_integer(
                payload.get("regression_count"),
                field_name="regression_count",
            ),
            violation_count=_required_integer(
                payload.get("violation_count"),
                field_name="violation_count",
            ),
            baseline_id=baseline_id,
            metrics=metrics,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "recorded_at": self.recorded_at,
            "run_reference": self.run_reference,
            "report_generated_date": (
                self.report_generated_date
            ),
            "branch": self.branch,
            "commit_sha": self.commit_sha,
            "environment": self.environment,
            "evaluation_mode": (
                self.evaluation_mode
            ),
            "passed": self.passed,
            "quality_gate_passed": (
                self.quality_gate_passed
            ),
            "pass_rate": self.pass_rate,
            "case_count": self.case_count,
            "dataset_count": self.dataset_count,
            "metric_count": self.metric_count,
            "regression_count": (
                self.regression_count
            ),
            "violation_count": (
                self.violation_count
            ),
            "baseline_id": self.baseline_id,
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
        }


@dataclass(frozen=True, slots=True)
class EvaluationHistory:
    entries: tuple[EvaluationHistoryEntry, ...]
    history_schema_version: str = (
        HISTORY_SCHEMA_VERSION
    )

    @classmethod
    def empty(cls) -> EvaluationHistory:
        return cls(entries=())

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> EvaluationHistory:
        schema_version = _required_text(
            payload.get("history_schema_version"),
            field_name="history_schema_version",
        )

        if schema_version != HISTORY_SCHEMA_VERSION:
            raise EvaluationHistorySchemaError(
                "Versão de histórico não suportada: "
                f"{schema_version!r}."
            )

        entries = tuple(
            EvaluationHistoryEntry.from_dict(
                _required_mapping(
                    raw_entry,
                    field_name=f"entries[{index}]",
                )
            )
            for index, raw_entry in enumerate(
                _required_sequence(
                    payload.get("entries"),
                    field_name="entries",
                )
            )
        )

        references = [
            entry.run_reference
            for entry in entries
        ]

        if len(references) != len(set(references)):
            raise EvaluationHistorySchemaError(
                "O histórico possui run_reference "
                "duplicado."
            )

        return cls(
            entries=tuple(
                sorted(
                    entries,
                    key=lambda entry: (
                        entry.recorded_at
                    ),
                )
            ),
            history_schema_version=(
                schema_version
            ),
        )

    def add(
        self,
        entry: EvaluationHistoryEntry,
        *,
        replace_existing: bool = False,
    ) -> EvaluationHistory:
        existing = {
            item.run_reference: item
            for item in self.entries
        }

        if (
            entry.run_reference in existing
            and not replace_existing
        ):
            raise DuplicateHistoryEntryError(
                "Já existe uma entrada para "
                f"{entry.run_reference}."
            )

        existing[entry.run_reference] = entry

        return EvaluationHistory(
            entries=tuple(
                sorted(
                    existing.values(),
                    key=lambda item: (
                        item.recorded_at
                    ),
                )
            )
        )

    def latest(
        self,
    ) -> EvaluationHistoryEntry | None:
        if not self.entries:
            return None

        return self.entries[-1]

    def metric_series(
        self,
        metric_id: str,
    ) -> tuple[tuple[str, float], ...]:
        points: list[tuple[str, float]] = []

        for entry in self.entries:
            for metric in entry.metrics:
                if metric.metric_id == metric_id:
                    points.append(
                        (
                            entry.recorded_at,
                            metric.average_score,
                        )
                    )
                    break

        return tuple(points)

    def to_dict(self) -> dict[str, Any]:
        return {
            "history_schema_version": (
                self.history_schema_version
            ),
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
        }


def load_history(
    path: str | Path,
) -> EvaluationHistory:
    source = Path(path)

    if not source.exists():
        return EvaluationHistory.empty()

    try:
        payload = json.loads(
            source.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise EvaluationHistorySchemaError(
            f"Histórico JSON inválido: {exc}"
        ) from exc

    return EvaluationHistory.from_dict(
        _required_mapping(
            payload,
            field_name=str(source),
        )
    )


def write_history(
    history: EvaluationHistory,
    path: str | Path,
) -> Path:
    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            history.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(destination)

    return destination


def append_report_to_history(
    *,
    report_path: str | Path,
    history_path: str | Path,
    comparison: EvaluationComparison | None = None,
    branch: str = "unknown",
    commit_sha: str = "unknown",
    environment: str = "local",
    evaluation_mode: str = (
        "deterministic-synthetic"
    ),
    replace_existing: bool = False,
) -> EvaluationHistoryEntry:
    report = load_json_object(report_path)

    entry = EvaluationHistoryEntry.from_report(
        report,
        comparison=comparison,
        branch=branch,
        commit_sha=commit_sha,
        environment=environment,
        evaluation_mode=evaluation_mode,
    )

    history = load_history(history_path)

    updated = history.add(
        entry,
        replace_existing=replace_existing,
    )

    write_history(
        updated,
        history_path,
    )

    return entry


__all__ = [
    "DuplicateHistoryEntryError",
    "EvaluationHistory",
    "EvaluationHistoryEntry",
    "EvaluationHistoryError",
    "EvaluationHistorySchemaError",
    "HISTORY_SCHEMA_VERSION",
    "HistoryMetric",
    "append_report_to_history",
    "load_history",
    "write_history",
]

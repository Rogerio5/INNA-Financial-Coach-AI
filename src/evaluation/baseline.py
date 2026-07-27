from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

BASELINE_SCHEMA_VERSION = "1.0.0"
SUPPORTED_REPORT_TYPE = "inna-evaluation-batch"


class BaselineError(RuntimeError):
    """Erro base para operações de baseline."""


class BaselineSchemaError(BaselineError):
    """Relatório ou baseline possui estrutura inválida."""


class BaselinePromotionError(BaselineError):
    """Relatório não pode ser promovido para baseline."""


def _required_mapping(
    value: object,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BaselineSchemaError(
            f"{field_name} deve ser um objeto."
        )

    return value


def _required_list(
    value: object,
    *,
    field_name: str,
) -> list[Any]:
    if not isinstance(value, list):
        raise BaselineSchemaError(
            f"{field_name} deve ser uma lista."
        )

    return value


def _required_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BaselineSchemaError(
            f"{field_name} deve ser texto não vazio."
        )

    return value.strip()


def _required_bool(
    value: object,
    *,
    field_name: str,
) -> bool:
    if not isinstance(value, bool):
        raise BaselineSchemaError(
            f"{field_name} deve ser booleano."
        )

    return value


def _required_number(
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


def _utc_now() -> str:
    return (
        datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True, slots=True)
class BaselineMetric:
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
    ) -> BaselineMetric:
        metric_id = _required_text(
            payload.get("metric_id"),
            field_name="metrics[].metric_id",
        )

        average_score = _required_number(
            payload.get("average_score"),
            field_name=(
                f"metrics[{metric_id}].average_score"
            ),
        )

        integer_fields: dict[str, int] = {}

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

            integer_fields[field_name] = value

        if not 0.0 <= average_score <= 1.0:
            raise BaselineSchemaError(
                f"metrics[{metric_id}].average_score "
                "deve estar entre 0 e 1."
            )

        return cls(
            metric_id=metric_id,
            average_score=average_score,
            **integer_fields,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "average_score": self.average_score,
            "total_executions": self.total_executions,
            "passed": self.passed,
            "failed": self.failed,
            "blocked": self.blocked,
            "errors": self.errors,
            "skipped": self.skipped,
        }


@dataclass(frozen=True, slots=True)
class EvaluationBaseline:
    baseline_id: str
    promoted_at: str
    source_report_type: str
    source_schema_version: str
    source_batch_id: str
    source_run_reference: str
    source_generated_date: str
    case_ids: tuple[str, ...]
    dataset_ids: tuple[str, ...]
    metrics: tuple[BaselineMetric, ...]
    pass_rate: float
    quality_gate_passed: bool
    baseline_schema_version: str = (
        BASELINE_SCHEMA_VERSION
    )
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_report(
        cls,
        report: Mapping[str, Any],
        *,
        baseline_id: str | None = None,
        promoted_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EvaluationBaseline:
        report_type = _required_text(
            report.get("report_type"),
            field_name="report_type",
        )

        if report_type != SUPPORTED_REPORT_TYPE:
            raise BaselineSchemaError(
                "report_type não suportado: "
                f"{report_type!r}."
            )

        schema_version = _required_text(
            report.get("schema_version"),
            field_name="schema_version",
        )

        batch = _required_mapping(
            report.get("batch"),
            field_name="batch",
        )

        summary = _required_mapping(
            report.get("summary"),
            field_name="summary",
        )

        quality_gate = _required_mapping(
            report.get("quality_gate"),
            field_name="quality_gate",
        )

        quality_gate_passed = _required_bool(
            quality_gate.get("passed"),
            field_name="quality_gate.passed",
        )

        pass_rate = _required_number(
            summary.get("pass_rate"),
            field_name="summary.pass_rate",
        )

        if not 0.0 <= pass_rate <= 1.0:
            raise BaselineSchemaError(
                "summary.pass_rate deve estar "
                "entre 0 e 1."
            )

        batch_status = _required_text(
            batch.get("status"),
            field_name="batch.status",
        )

        if batch_status != "passed":
            raise BaselinePromotionError(
                "Somente lotes aprovados podem ser "
                "promovidos para baseline."
            )

        if not quality_gate_passed:
            raise BaselinePromotionError(
                "O quality gate deve estar aprovado "
                "para promover a baseline."
            )

        cases_payload = _required_list(
            report.get("cases"),
            field_name="cases",
        )

        datasets_payload = _required_list(
            report.get("datasets"),
            field_name="datasets",
        )

        metrics_payload = _required_list(
            report.get("metrics"),
            field_name="metrics",
        )

        case_ids: list[str] = []

        for index, item in enumerate(cases_payload):
            case = _required_mapping(
                item,
                field_name=f"cases[{index}]",
            )

            case_ids.append(
                _required_text(
                    case.get("case_id"),
                    field_name=(
                        f"cases[{index}].case_id"
                    ),
                )
            )

        dataset_ids: list[str] = []

        for index, item in enumerate(
            datasets_payload
        ):
            dataset = _required_mapping(
                item,
                field_name=f"datasets[{index}]",
            )

            dataset_id = (
                dataset.get("dataset_id")
                or dataset.get("id")
                or dataset.get("name")
            )

            dataset_ids.append(
                _required_text(
                    dataset_id,
                    field_name=(
                        f"datasets[{index}].dataset_id"
                    ),
                )
            )

        metrics = tuple(
            BaselineMetric.from_report_entry(
                _required_mapping(
                    item,
                    field_name=f"metrics[{index}]",
                )
            )
            for index, item in enumerate(
                metrics_payload
            )
        )

        metric_ids = [
            metric.metric_id
            for metric in metrics
        ]

        if len(metric_ids) != len(set(metric_ids)):
            raise BaselineSchemaError(
                "O relatório possui metric_id duplicado."
            )

        if len(case_ids) != len(set(case_ids)):
            raise BaselineSchemaError(
                "O relatório possui case_id duplicado."
            )

        return cls(
            baseline_id=(
                baseline_id
                or f"baseline-{uuid4().hex[:12]}"
            ),
            promoted_at=promoted_at or _utc_now(),
            source_report_type=report_type,
            source_schema_version=schema_version,
            source_batch_id=_required_text(
                (
                    batch.get("batch_id")
                    or quality_gate.get("batch_id")
                    or batch.get("run_reference")
                    or report.get("run_reference")
                ),
                field_name=(
                    "batch.batch_id, "
                    "quality_gate.batch_id ou "
                    "run_reference"
                ),
            ),
            source_run_reference=_required_text(
                report.get("run_reference"),
                field_name="run_reference",
            ),
            source_generated_date=_required_text(
                report.get("generated_date"),
                field_name="generated_date",
            ),
            case_ids=tuple(sorted(case_ids)),
            dataset_ids=tuple(sorted(dataset_ids)),
            metrics=tuple(
                sorted(
                    metrics,
                    key=lambda metric: (
                        metric.metric_id
                    ),
                )
            ),
            pass_rate=pass_rate,
            quality_gate_passed=(
                quality_gate_passed
            ),
            metadata=dict(metadata or {}),
        )

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> EvaluationBaseline:
        schema_version = _required_text(
            payload.get("baseline_schema_version"),
            field_name="baseline_schema_version",
        )

        if schema_version != BASELINE_SCHEMA_VERSION:
            raise BaselineSchemaError(
                "Versão de baseline não suportada: "
                f"{schema_version!r}."
            )

        metrics_payload = _required_list(
            payload.get("metrics"),
            field_name="metrics",
        )

        metrics = tuple(
            BaselineMetric.from_report_entry(
                _required_mapping(
                    item,
                    field_name=f"metrics[{index}]",
                )
            )
            for index, item in enumerate(
                metrics_payload
            )
        )

        case_ids = tuple(
            _required_text(
                value,
                field_name="case_ids[]",
            )
            for value in _required_list(
                payload.get("case_ids"),
                field_name="case_ids",
            )
        )

        dataset_ids = tuple(
            _required_text(
                value,
                field_name="dataset_ids[]",
            )
            for value in _required_list(
                payload.get("dataset_ids"),
                field_name="dataset_ids",
            )
        )

        metadata = _required_mapping(
            payload.get("metadata", {}),
            field_name="metadata",
        )

        return cls(
            baseline_id=_required_text(
                payload.get("baseline_id"),
                field_name="baseline_id",
            ),
            promoted_at=_required_text(
                payload.get("promoted_at"),
                field_name="promoted_at",
            ),
            source_report_type=_required_text(
                payload.get("source_report_type"),
                field_name="source_report_type",
            ),
            source_schema_version=_required_text(
                payload.get(
                    "source_schema_version"
                ),
                field_name="source_schema_version",
            ),
            source_batch_id=_required_text(
                payload.get("source_batch_id"),
                field_name="source_batch_id",
            ),
            source_run_reference=_required_text(
                payload.get(
                    "source_run_reference"
                ),
                field_name="source_run_reference",
            ),
            source_generated_date=_required_text(
                payload.get(
                    "source_generated_date"
                ),
                field_name="source_generated_date",
            ),
            case_ids=case_ids,
            dataset_ids=dataset_ids,
            metrics=metrics,
            pass_rate=_required_number(
                payload.get("pass_rate"),
                field_name="pass_rate",
            ),
            quality_gate_passed=_required_bool(
                payload.get(
                    "quality_gate_passed"
                ),
                field_name="quality_gate_passed",
            ),
            baseline_schema_version=(
                schema_version
            ),
            metadata=dict(metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_schema_version": (
                self.baseline_schema_version
            ),
            "baseline_id": self.baseline_id,
            "promoted_at": self.promoted_at,
            "source_report_type": (
                self.source_report_type
            ),
            "source_schema_version": (
                self.source_schema_version
            ),
            "source_batch_id": (
                self.source_batch_id
            ),
            "source_run_reference": (
                self.source_run_reference
            ),
            "source_generated_date": (
                self.source_generated_date
            ),
            "case_ids": list(self.case_ids),
            "dataset_ids": list(
                self.dataset_ids
            ),
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
            "pass_rate": self.pass_rate,
            "quality_gate_passed": (
                self.quality_gate_passed
            ),
            "metadata": dict(self.metadata),
        }


def load_json_object(
    path: str | Path,
) -> Mapping[str, Any]:
    source = Path(path)

    try:
        payload = json.loads(
            source.read_text(encoding="utf-8")
        )
    except FileNotFoundError as exc:
        raise BaselineError(
            f"Arquivo não encontrado: {source}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise BaselineSchemaError(
            f"JSON inválido em {source}: {exc}"
        ) from exc

    return _required_mapping(
        payload,
        field_name=str(source),
    )


def load_baseline(
    path: str | Path,
) -> EvaluationBaseline:
    return EvaluationBaseline.from_dict(
        load_json_object(path)
    )


def write_baseline(
    baseline: EvaluationBaseline,
    path: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    destination = Path(path)

    if destination.exists() and not overwrite:
        raise BaselineError(
            "A baseline já existe. Use overwrite=True "
            "para substituí-la."
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            baseline.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(destination)

    return destination


def promote_report_file(
    report_path: str | Path,
    baseline_path: str | Path,
    *,
    baseline_id: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    overwrite: bool = False,
) -> EvaluationBaseline:
    report = load_json_object(report_path)

    baseline = EvaluationBaseline.from_report(
        report,
        baseline_id=baseline_id,
        metadata=metadata,
    )

    write_baseline(
        baseline,
        baseline_path,
        overwrite=overwrite,
    )

    return baseline


__all__ = [
    "BASELINE_SCHEMA_VERSION",
    "BaselineError",
    "BaselineMetric",
    "BaselinePromotionError",
    "BaselineSchemaError",
    "EvaluationBaseline",
    "load_baseline",
    "load_json_object",
    "promote_report_file",
    "write_baseline",
]

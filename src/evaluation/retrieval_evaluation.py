"""Avaliação offline em lote da qualidade de recuperação RAG.

O módulo trabalha somente com datasets locais e resultados de retrieval
previamente preparados. Nenhuma chamada de LLM, banco de dados ou serviço
externo é executada.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsResult,
    evaluate_retrieval_case,
)


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    """Caso determinístico de avaliação de retrieval."""

    case_id: str
    question: str
    retrieved_document_ids: tuple[str, ...]
    relevant_document_ids: tuple[str, ...]
    graded_relevance: Mapping[str, float]
    k: int


@dataclass(frozen=True, slots=True)
class RetrievalQualityThresholds:
    """Limites mínimos agregados para aprovação."""

    minimum_hit_rate: float = 0.80
    minimum_recall: float = 0.75
    minimum_precision: float = 0.50
    minimum_mrr: float = 0.70
    minimum_ndcg: float = 0.75


@dataclass(frozen=True, slots=True)
class RetrievalCaseEvaluation:
    """Resultado de um único caso."""

    case_id: str
    question: str
    metrics: RetrievalMetricsResult


@dataclass(frozen=True, slots=True)
class RetrievalAggregateMetrics:
    """Médias agregadas do dataset."""

    case_count: int
    mean_hit_rate: float
    mean_recall: float
    mean_precision: float
    mean_reciprocal_rank: float
    mean_ndcg: float


@dataclass(frozen=True, slots=True)
class RetrievalQualityGateResult:
    """Resultado dos quality gates agregados."""

    passed: bool
    checks: Mapping[str, bool]
    failed_checks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationReport:
    """Relatório consolidado da execução offline."""

    schema_version: int
    run_id: str
    generated_at: str
    dataset_name: str
    cases: tuple[RetrievalCaseEvaluation, ...]
    aggregate_metrics: RetrievalAggregateMetrics
    thresholds: RetrievalQualityThresholds
    quality_gate: RetrievalQualityGateResult

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_non_empty_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()

    if not normalized:
        raise ValueError(f"{field_name} nao pode ser vazio.")

    return normalized


def _parse_document_ids(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} deve ser uma lista.")

    document_ids = tuple(_require_non_empty_text(item, field_name) for item in value)

    return document_ids


def _parse_graded_relevance(
    value: object,
) -> dict[str, float]:
    if not isinstance(value, dict):
        raise TypeError("graded_relevance deve ser um objeto.")

    parsed: dict[str, float] = {}

    for document_id, score in value.items():
        normalized_id = _require_non_empty_text(
            document_id,
            "graded_relevance.document_id",
        )
        numeric_score = float(score)

        if numeric_score < 0:
            raise ValueError("graded_relevance nao aceita valores negativos.")

        parsed[normalized_id] = numeric_score

    return parsed


def _parse_case(payload: object) -> RetrievalCase:
    if not isinstance(payload, dict):
        raise TypeError("Cada caso do dataset deve ser um objeto.")

    raw_k = payload.get("k", 4)

    if isinstance(raw_k, bool) or not isinstance(raw_k, int):
        raise TypeError("k deve ser inteiro.")

    if raw_k <= 0:
        raise ValueError("k deve ser maior que zero.")

    relevant_ids = _parse_document_ids(
        payload.get("relevant_document_ids"),
        "relevant_document_ids",
    )

    graded_relevance = _parse_graded_relevance(
        payload.get(
            "graded_relevance",
            {document_id: 1.0 for document_id in relevant_ids},
        )
    )

    return RetrievalCase(
        case_id=_require_non_empty_text(
            payload.get("case_id"),
            "case_id",
        ),
        question=_require_non_empty_text(
            payload.get("question"),
            "question",
        ),
        retrieved_document_ids=_parse_document_ids(
            payload.get("retrieved_document_ids"),
            "retrieved_document_ids",
        ),
        relevant_document_ids=relevant_ids,
        graded_relevance=graded_relevance,
        k=raw_k,
    )


def load_retrieval_dataset(
    dataset_path: str | Path,
) -> tuple[str, tuple[RetrievalCase, ...]]:
    """Carrega e valida um dataset JSON local."""

    path = Path(dataset_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset de retrieval nao encontrado: {path}")

    payload = json.loads(path.read_text(encoding="utf-8-sig"))

    if not isinstance(payload, dict):
        raise TypeError("A raiz do dataset deve ser um objeto.")

    dataset_name = _require_non_empty_text(
        payload.get("name"),
        "name",
    )

    raw_cases = payload.get("cases")

    if not isinstance(raw_cases, list):
        raise TypeError("cases deve ser uma lista.")

    if not raw_cases:
        raise ValueError("O dataset deve possuir ao menos um caso.")

    cases = tuple(_parse_case(item) for item in raw_cases)

    case_ids = [case.case_id for case in cases]

    if len(case_ids) != len(set(case_ids)):
        raise ValueError("O dataset possui case_id duplicado.")

    return dataset_name, cases


def _aggregate_case_results(
    cases: Sequence[RetrievalCaseEvaluation],
) -> RetrievalAggregateMetrics:
    if not cases:
        raise ValueError("Nao e possivel agregar uma lista vazia de casos.")

    return RetrievalAggregateMetrics(
        case_count=len(cases),
        mean_hit_rate=mean(case.metrics.hit_rate for case in cases),
        mean_recall=mean(case.metrics.recall for case in cases),
        mean_precision=mean(case.metrics.precision for case in cases),
        mean_reciprocal_rank=mean(case.metrics.reciprocal_rank for case in cases),
        mean_ndcg=mean(case.metrics.ndcg for case in cases),
    )


def evaluate_quality_gate(
    aggregate: RetrievalAggregateMetrics,
    thresholds: RetrievalQualityThresholds,
) -> RetrievalQualityGateResult:
    """Compara as médias agregadas com os limites mínimos."""

    checks = {
        "hit_rate": (aggregate.mean_hit_rate >= thresholds.minimum_hit_rate),
        "recall": (aggregate.mean_recall >= thresholds.minimum_recall),
        "precision": (aggregate.mean_precision >= thresholds.minimum_precision),
        "mrr": (aggregate.mean_reciprocal_rank >= thresholds.minimum_mrr),
        "ndcg": (aggregate.mean_ndcg >= thresholds.minimum_ndcg),
    }

    failed_checks = tuple(
        check_name for check_name, passed in checks.items() if not passed
    )

    return RetrievalQualityGateResult(
        passed=not failed_checks,
        checks=checks,
        failed_checks=failed_checks,
    )


def evaluate_retrieval_dataset(
    *,
    dataset_name: str,
    cases: Sequence[RetrievalCase],
    thresholds: RetrievalQualityThresholds | None = None,
) -> RetrievalEvaluationReport:
    """Avalia todos os casos e produz um relatório consolidado."""

    if not cases:
        raise ValueError("Nenhum caso foi informado para avaliacao.")

    effective_thresholds = (
        thresholds if thresholds is not None else RetrievalQualityThresholds()
    )

    evaluated_cases = tuple(
        RetrievalCaseEvaluation(
            case_id=case.case_id,
            question=case.question,
            metrics=evaluate_retrieval_case(
                retrieved_document_ids=(case.retrieved_document_ids),
                relevant_document_ids=(case.relevant_document_ids),
                graded_relevance=case.graded_relevance,
                k=case.k,
            ),
        )
        for case in cases
    )

    aggregate = _aggregate_case_results(evaluated_cases)
    quality_gate = evaluate_quality_gate(
        aggregate,
        effective_thresholds,
    )

    generated_at = datetime.now(UTC)
    run_id = generated_at.strftime("retrieval-offline-%Y%m%dT%H%M%SZ")

    return RetrievalEvaluationReport(
        schema_version=1,
        run_id=run_id,
        generated_at=generated_at.isoformat(),
        dataset_name=dataset_name,
        cases=evaluated_cases,
        aggregate_metrics=aggregate,
        thresholds=effective_thresholds,
        quality_gate=quality_gate,
    )


def _percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def render_markdown_report(
    report: RetrievalEvaluationReport,
) -> str:
    """Renderiza um relatório Markdown legível."""

    aggregate = report.aggregate_metrics
    gate = report.quality_gate

    lines = [
        "# Avaliação Offline de Retrieval",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Dataset: `{report.dataset_name}`",
        f"- Casos: `{aggregate.case_count}`",
        f"- Quality gate: `{'PASS' if gate.passed else 'FAIL'}`",
        "",
        "## Métricas agregadas",
        "",
        "| Métrica | Resultado | Limite |",
        "|---|---:|---:|",
        (
            f"| Hit Rate | {_percentage(aggregate.mean_hit_rate)} "
            f"| {_percentage(report.thresholds.minimum_hit_rate)} |"
        ),
        (
            f"| Recall | {_percentage(aggregate.mean_recall)} "
            f"| {_percentage(report.thresholds.minimum_recall)} |"
        ),
        (
            f"| Precision | {_percentage(aggregate.mean_precision)} "
            f"| {_percentage(report.thresholds.minimum_precision)} |"
        ),
        (
            "| MRR | "
            f"{aggregate.mean_reciprocal_rank:.4f} | "
            f"{report.thresholds.minimum_mrr:.4f} |"
        ),
        (
            "| NDCG | "
            f"{aggregate.mean_ndcg:.4f} | "
            f"{report.thresholds.minimum_ndcg:.4f} |"
        ),
        "",
        "## Casos",
        "",
        ("| Caso | K | Hit Rate | Recall | Precision | Reciprocal Rank | NDCG |"),
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for case in report.cases:
        metrics = case.metrics
        lines.append(
            f"| `{case.case_id}` "
            f"| {metrics.k} "
            f"| {metrics.hit_rate:.4f} "
            f"| {metrics.recall:.4f} "
            f"| {metrics.precision:.4f} "
            f"| {metrics.reciprocal_rank:.4f} "
            f"| {metrics.ndcg:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Quality gates",
            "",
        ]
    )

    for check_name, passed in gate.checks.items():
        status = "PASS" if passed else "FAIL"
        lines.append(f"- `{check_name}`: **{status}**")

    if gate.failed_checks:
        lines.extend(
            [
                "",
                "Falhas:",
                "",
                *[f"- `{check_name}`" for check_name in gate.failed_checks],
            ]
        )

    lines.extend(
        [
            "",
            "## Execução",
            "",
            "- Gemini utilizado: `não`",
            "- Neon utilizado: `não`",
            "- Serviços externos: `não`",
            "",
        ]
    )

    return "\n".join(lines)


def write_retrieval_reports(
    report: RetrievalEvaluationReport,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    """Grava versões JSON e Markdown do relatório."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)

    json_path = directory / f"{report.run_id}.json"
    markdown_path = directory / f"{report.run_id}.md"

    json_path.write_text(
        json.dumps(
            report.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path.write_text(
        render_markdown_report(report),
        encoding="utf-8",
    )

    return json_path, markdown_path


__all__ = [
    "RetrievalAggregateMetrics",
    "RetrievalCase",
    "RetrievalCaseEvaluation",
    "RetrievalEvaluationReport",
    "RetrievalQualityGateResult",
    "RetrievalQualityThresholds",
    "evaluate_quality_gate",
    "evaluate_retrieval_dataset",
    "load_retrieval_dataset",
    "render_markdown_report",
    "write_retrieval_reports",
]

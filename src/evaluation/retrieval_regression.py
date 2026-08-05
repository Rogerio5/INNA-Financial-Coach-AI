"""Comparação offline de qualidade, latência e regressão de retrieval.

Este módulo não executa LLMs, consultas ao Neon ou chamadas externas.
Ele compara resultados determinísticos previamente calculados.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, median
from typing import Any

from src.evaluation.retrieval_evaluation import (
    RetrievalAggregateMetrics,
    RetrievalEvaluationReport,
)


@dataclass(frozen=True, slots=True)
class RetrievalLatencySummary:
    """Resumo estatístico das latências observadas."""

    case_count: int
    mean_ms: float
    median_ms: float
    minimum_ms: float
    maximum_ms: float
    p95_ms: float


@dataclass(frozen=True, slots=True)
class RetrievalMetricDeltas:
    """Diferenças candidato menos baseline."""

    hit_rate: float
    recall: float
    precision: float
    reciprocal_rank: float
    ndcg: float
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float


@dataclass(frozen=True, slots=True)
class RetrievalRegressionThresholds:
    """Tolerâncias máximas para regressão."""

    maximum_hit_rate_drop: float = 0.05
    maximum_recall_drop: float = 0.05
    maximum_precision_drop: float = 0.05
    maximum_mrr_drop: float = 0.05
    maximum_ndcg_drop: float = 0.05
    maximum_mean_latency_increase_ms: float = 15.0
    maximum_median_latency_increase_ms: float = 15.0
    maximum_p95_latency_increase_ms: float = 20.0


@dataclass(frozen=True, slots=True)
class RetrievalRegressionGate:
    """Resultado do gate de regressão."""

    passed: bool
    checks: Mapping[str, bool]
    failed_checks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetrievalRegressionReport:
    """Relatório consolidado da comparação."""

    schema_version: int
    run_id: str
    generated_at: str
    baseline_dataset: str
    candidate_dataset: str
    baseline_metrics: RetrievalAggregateMetrics
    candidate_metrics: RetrievalAggregateMetrics
    baseline_latency: RetrievalLatencySummary
    candidate_latency: RetrievalLatencySummary
    deltas: RetrievalMetricDeltas
    thresholds: RetrievalRegressionThresholds
    regression_gate: RetrievalRegressionGate

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _percentile_nearest_rank(
    values: Sequence[float],
    percentile: float,
) -> float:
    if not values:
        raise ValueError("Nao e possivel calcular percentil de lista vazia.")

    if not 0.0 < percentile <= 1.0:
        raise ValueError("percentile deve estar entre zero e um.")

    ordered = sorted(float(value) for value in values)

    rank = max(
        1,
        int(len(ordered) * percentile + 0.999999),
    )

    return ordered[min(rank - 1, len(ordered) - 1)]


def summarize_retrieval_latencies(
    latencies_ms: Sequence[float],
) -> RetrievalLatencySummary:
    """Calcula estatísticas agregadas de latência."""

    if not latencies_ms:
        raise ValueError("A lista de latencias nao pode ser vazia.")

    normalized = tuple(float(value) for value in latencies_ms)

    if any(value < 0 for value in normalized):
        raise ValueError("Latencias nao podem possuir valores negativos.")

    return RetrievalLatencySummary(
        case_count=len(normalized),
        mean_ms=mean(normalized),
        median_ms=median(normalized),
        minimum_ms=min(normalized),
        maximum_ms=max(normalized),
        p95_ms=_percentile_nearest_rank(
            normalized,
            0.95,
        ),
    )


def load_latency_fixture(
    path: str | Path,
) -> tuple[str, dict[str, float]]:
    """Carrega latências observadas de um arquivo JSON local."""

    fixture_path = Path(path)

    if not fixture_path.is_file():
        raise FileNotFoundError(f"Arquivo de latencia nao encontrado: {fixture_path}")

    payload = json.loads(fixture_path.read_text(encoding="utf-8-sig"))

    if not isinstance(payload, dict):
        raise TypeError("A raiz do arquivo de latencia deve ser um objeto.")

    name = str(payload.get("name", "")).strip()

    if not name:
        raise ValueError("O arquivo de latencia precisa possuir name.")

    raw_cases = payload.get("cases")

    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("O arquivo de latencia precisa possuir casos.")

    latencies: dict[str, float] = {}

    for item in raw_cases:
        if not isinstance(item, dict):
            raise TypeError("Cada caso de latencia deve ser um objeto.")

        case_id = str(item.get("case_id", "")).strip()

        if not case_id:
            raise ValueError("case_id de latencia nao pode ser vazio.")

        if case_id in latencies:
            raise ValueError("O arquivo possui case_id de latencia duplicado.")

        latency_ms = float(item.get("retrieval_latency_ms"))

        if latency_ms < 0:
            raise ValueError("retrieval_latency_ms nao pode ser negativo.")

        latencies[case_id] = latency_ms

    return name, latencies


def _validated_latency_values(
    report: RetrievalEvaluationReport,
    latencies: Mapping[str, float],
) -> tuple[float, ...]:
    report_case_ids = {case.case_id for case in report.cases}

    latency_case_ids = set(latencies)

    missing = sorted(report_case_ids - latency_case_ids)
    unexpected = sorted(latency_case_ids - report_case_ids)

    if missing:
        raise ValueError("Latencias ausentes para os casos: " + ", ".join(missing))

    if unexpected:
        raise ValueError(
            "Latencias informadas para casos desconhecidos: " + ", ".join(unexpected)
        )

    return tuple(float(latencies[case.case_id]) for case in report.cases)


def _metric_deltas(
    baseline_metrics: RetrievalAggregateMetrics,
    candidate_metrics: RetrievalAggregateMetrics,
    baseline_latency: RetrievalLatencySummary,
    candidate_latency: RetrievalLatencySummary,
) -> RetrievalMetricDeltas:
    return RetrievalMetricDeltas(
        hit_rate=(candidate_metrics.mean_hit_rate - baseline_metrics.mean_hit_rate),
        recall=(candidate_metrics.mean_recall - baseline_metrics.mean_recall),
        precision=(candidate_metrics.mean_precision - baseline_metrics.mean_precision),
        reciprocal_rank=(
            candidate_metrics.mean_reciprocal_rank
            - baseline_metrics.mean_reciprocal_rank
        ),
        ndcg=(candidate_metrics.mean_ndcg - baseline_metrics.mean_ndcg),
        mean_latency_ms=(candidate_latency.mean_ms - baseline_latency.mean_ms),
        median_latency_ms=(candidate_latency.median_ms - baseline_latency.median_ms),
        p95_latency_ms=(candidate_latency.p95_ms - baseline_latency.p95_ms),
    )


def evaluate_regression_gate(
    deltas: RetrievalMetricDeltas,
    thresholds: RetrievalRegressionThresholds,
) -> RetrievalRegressionGate:
    """Avalia se o candidato respeita as tolerâncias."""

    checks = {
        "hit_rate": (deltas.hit_rate >= -thresholds.maximum_hit_rate_drop),
        "recall": (deltas.recall >= -thresholds.maximum_recall_drop),
        "precision": (deltas.precision >= -thresholds.maximum_precision_drop),
        "mrr": (deltas.reciprocal_rank >= -thresholds.maximum_mrr_drop),
        "ndcg": (deltas.ndcg >= -thresholds.maximum_ndcg_drop),
        "mean_latency": (
            deltas.mean_latency_ms <= thresholds.maximum_mean_latency_increase_ms
        ),
        "median_latency": (
            deltas.median_latency_ms <= thresholds.maximum_median_latency_increase_ms
        ),
        "p95_latency": (
            deltas.p95_latency_ms <= thresholds.maximum_p95_latency_increase_ms
        ),
    }

    failed_checks = tuple(name for name, passed in checks.items() if not passed)

    return RetrievalRegressionGate(
        passed=not failed_checks,
        checks=checks,
        failed_checks=failed_checks,
    )


def compare_retrieval_reports(
    *,
    baseline_report: RetrievalEvaluationReport,
    candidate_report: RetrievalEvaluationReport,
    baseline_latencies_ms: Mapping[str, float],
    candidate_latencies_ms: Mapping[str, float],
    thresholds: RetrievalRegressionThresholds | None = None,
) -> RetrievalRegressionReport:
    """Compara dois relatórios de avaliação de retrieval."""

    baseline_values = _validated_latency_values(
        baseline_report,
        baseline_latencies_ms,
    )
    candidate_values = _validated_latency_values(
        candidate_report,
        candidate_latencies_ms,
    )

    baseline_latency = summarize_retrieval_latencies(baseline_values)
    candidate_latency = summarize_retrieval_latencies(candidate_values)

    deltas = _metric_deltas(
        baseline_report.aggregate_metrics,
        candidate_report.aggregate_metrics,
        baseline_latency,
        candidate_latency,
    )

    effective_thresholds = (
        thresholds if thresholds is not None else RetrievalRegressionThresholds()
    )

    gate = evaluate_regression_gate(
        deltas,
        effective_thresholds,
    )

    generated_at = datetime.now(UTC)

    return RetrievalRegressionReport(
        schema_version=1,
        run_id=generated_at.strftime("retrieval-regression-%Y%m%dT%H%M%SZ"),
        generated_at=generated_at.isoformat(),
        baseline_dataset=baseline_report.dataset_name,
        candidate_dataset=candidate_report.dataset_name,
        baseline_metrics=baseline_report.aggregate_metrics,
        candidate_metrics=candidate_report.aggregate_metrics,
        baseline_latency=baseline_latency,
        candidate_latency=candidate_latency,
        deltas=deltas,
        thresholds=effective_thresholds,
        regression_gate=gate,
    )


def render_regression_markdown(
    report: RetrievalRegressionReport,
) -> str:
    """Renderiza relatório Markdown de regressão."""

    status = "PASS" if report.regression_gate.passed else "FAIL"

    lines = [
        "# Regressão Offline de Retrieval",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Baseline: `{report.baseline_dataset}`",
        f"- Candidato: `{report.candidate_dataset}`",
        f"- Regression gate: `{status}`",
        "",
        "## Deltas de qualidade",
        "",
        "| Métrica | Delta |",
        "|---|---:|",
        f"| Hit Rate | {report.deltas.hit_rate:+.6f} |",
        f"| Recall | {report.deltas.recall:+.6f} |",
        f"| Precision | {report.deltas.precision:+.6f} |",
        (f"| MRR | {report.deltas.reciprocal_rank:+.6f} |"),
        f"| NDCG | {report.deltas.ndcg:+.6f} |",
        "",
        "## Latência",
        "",
        "| Métrica | Baseline | Candidato | Delta |",
        "|---|---:|---:|---:|",
        (
            f"| Média | {report.baseline_latency.mean_ms:.2f} ms "
            f"| {report.candidate_latency.mean_ms:.2f} ms "
            f"| {report.deltas.mean_latency_ms:+.2f} ms |"
        ),
        (
            f"| Mediana | {report.baseline_latency.median_ms:.2f} ms "
            f"| {report.candidate_latency.median_ms:.2f} ms "
            f"| {report.deltas.median_latency_ms:+.2f} ms |"
        ),
        (
            f"| P95 | {report.baseline_latency.p95_ms:.2f} ms "
            f"| {report.candidate_latency.p95_ms:.2f} ms "
            f"| {report.deltas.p95_latency_ms:+.2f} ms |"
        ),
        "",
        "## Checks",
        "",
    ]

    for name, passed in report.regression_gate.checks.items():
        check_status = "PASS" if passed else "FAIL"
        lines.append(f"- `{name}`: **{check_status}**")

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


def write_regression_reports(
    report: RetrievalRegressionReport,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    """Grava relatórios JSON e Markdown."""

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
        render_regression_markdown(report),
        encoding="utf-8",
    )

    return json_path, markdown_path


__all__ = [
    "RetrievalLatencySummary",
    "RetrievalMetricDeltas",
    "RetrievalRegressionGate",
    "RetrievalRegressionReport",
    "RetrievalRegressionThresholds",
    "compare_retrieval_reports",
    "evaluate_regression_gate",
    "load_latency_fixture",
    "render_regression_markdown",
    "summarize_retrieval_latencies",
    "write_regression_reports",
]

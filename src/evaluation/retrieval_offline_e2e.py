"""Consolidação ponta a ponta da avaliação offline de retrieval.

O módulo consolida os resultados das avaliações de qualidade e regressão.
Nenhuma conexão com banco, LLM ou serviço externo é realizada.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.evaluation.retrieval_evaluation import (
    RetrievalEvaluationReport,
)
from src.evaluation.retrieval_regression import (
    RetrievalRegressionReport,
)


@dataclass(frozen=True, slots=True)
class OfflineValidationCheck:
    """Resultado individual de uma etapa da validação."""

    name: str
    passed: bool
    details: str


@dataclass(frozen=True, slots=True)
class OfflineRetrievalValidationReport:
    """Relatório final da validação ponta a ponta offline."""

    schema_version: int
    run_id: str
    generated_at: str
    passed: bool
    checks: tuple[OfflineValidationCheck, ...]
    failed_checks: tuple[str, ...]
    quality_dataset: str
    candidate_dataset: str
    quality_metrics: Mapping[str, float]
    regression_deltas: Mapping[str, float]
    execution_environment: Mapping[str, bool]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_offline_validation_report(
    *,
    ruff_passed: bool,
    tests_passed: bool,
    quality_report: RetrievalEvaluationReport,
    regression_report: RetrievalRegressionReport,
) -> OfflineRetrievalValidationReport:
    """Consolida as etapas em um único relatório PASS ou FAIL."""

    checks = (
        OfflineValidationCheck(
            name="ruff",
            passed=ruff_passed,
            details=(
                "Validacao estatica aprovada."
                if ruff_passed
                else "Validacao estatica reprovada."
            ),
        ),
        OfflineValidationCheck(
            name="tests",
            passed=tests_passed,
            details=(
                "Testes automatizados aprovados."
                if tests_passed
                else "Testes automatizados reprovados."
            ),
        ),
        OfflineValidationCheck(
            name="quality_gate",
            passed=quality_report.quality_gate.passed,
            details=(
                "Quality gate de retrieval aprovado."
                if quality_report.quality_gate.passed
                else (
                    "Quality gate reprovado: "
                    + ", ".join(quality_report.quality_gate.failed_checks)
                )
            ),
        ),
        OfflineValidationCheck(
            name="regression_gate",
            passed=regression_report.regression_gate.passed,
            details=(
                "Regression gate aprovado."
                if regression_report.regression_gate.passed
                else (
                    "Regression gate reprovado: "
                    + ", ".join(regression_report.regression_gate.failed_checks)
                )
            ),
        ),
    )

    failed_checks = tuple(check.name for check in checks if not check.passed)

    generated_at = datetime.now(UTC)

    quality = quality_report.aggregate_metrics
    deltas = regression_report.deltas

    return OfflineRetrievalValidationReport(
        schema_version=1,
        run_id=generated_at.strftime("retrieval-offline-e2e-%Y%m%dT%H%M%SZ"),
        generated_at=generated_at.isoformat(),
        passed=not failed_checks,
        checks=checks,
        failed_checks=failed_checks,
        quality_dataset=quality_report.dataset_name,
        candidate_dataset=regression_report.candidate_dataset,
        quality_metrics={
            "hit_rate": quality.mean_hit_rate,
            "recall": quality.mean_recall,
            "precision": quality.mean_precision,
            "mrr": quality.mean_reciprocal_rank,
            "ndcg": quality.mean_ndcg,
        },
        regression_deltas={
            "hit_rate": deltas.hit_rate,
            "recall": deltas.recall,
            "precision": deltas.precision,
            "mrr": deltas.reciprocal_rank,
            "ndcg": deltas.ndcg,
            "mean_latency_ms": deltas.mean_latency_ms,
            "median_latency_ms": deltas.median_latency_ms,
            "p95_latency_ms": deltas.p95_latency_ms,
        },
        execution_environment={
            "external_api_called": False,
            "database_connected": False,
            "gemini_used": False,
            "neon_used": False,
        },
    )


def render_offline_validation_markdown(
    report: OfflineRetrievalValidationReport,
) -> str:
    """Renderiza o relatório final em Markdown."""

    status = "PASS" if report.passed else "FAIL"

    lines = [
        "# Validação Ponta a Ponta Offline de Retrieval",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Resultado final: **{status}**",
        f"- Dataset: `{report.quality_dataset}`",
        f"- Candidato: `{report.candidate_dataset}`",
        "",
        "## Etapas",
        "",
        "| Etapa | Resultado | Detalhes |",
        "|---|---|---|",
    ]

    for check in report.checks:
        check_status = "PASS" if check.passed else "FAIL"
        lines.append(f"| `{check.name}` | **{check_status}** | {check.details} |")

    lines.extend(
        [
            "",
            "## Métricas de qualidade",
            "",
            "| Métrica | Resultado |",
            "|---|---:|",
            (f"| Hit Rate | {report.quality_metrics['hit_rate']:.6f} |"),
            (f"| Recall | {report.quality_metrics['recall']:.6f} |"),
            (f"| Precision | {report.quality_metrics['precision']:.6f} |"),
            (f"| MRR | {report.quality_metrics['mrr']:.6f} |"),
            (f"| NDCG | {report.quality_metrics['ndcg']:.6f} |"),
            "",
            "## Deltas de regressão",
            "",
            "| Métrica | Delta |",
            "|---|---:|",
            (f"| Hit Rate | {report.regression_deltas['hit_rate']:+.6f} |"),
            (f"| Recall | {report.regression_deltas['recall']:+.6f} |"),
            (f"| Precision | {report.regression_deltas['precision']:+.6f} |"),
            (f"| MRR | {report.regression_deltas['mrr']:+.6f} |"),
            (f"| NDCG | {report.regression_deltas['ndcg']:+.6f} |"),
            (
                "| Latência média | "
                f"{report.regression_deltas['mean_latency_ms']:+.2f} ms |"
            ),
            (
                "| Latência mediana | "
                f"{report.regression_deltas['median_latency_ms']:+.2f} ms |"
            ),
            (
                "| Latência P95 | "
                f"{report.regression_deltas['p95_latency_ms']:+.2f} ms |"
            ),
            "",
            "## Ambiente",
            "",
            "- Gemini utilizado: `não`",
            "- Neon utilizado: `não`",
            "- Banco de dados conectado: `não`",
            "- API externa utilizada: `não`",
            "",
        ]
    )

    if report.failed_checks:
        lines.extend(
            [
                "## Falhas",
                "",
                *[f"- `{check_name}`" for check_name in report.failed_checks],
                "",
            ]
        )

    return "\n".join(lines)


def write_offline_validation_reports(
    report: OfflineRetrievalValidationReport,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    """Grava o relatório final em JSON e Markdown."""

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
        render_offline_validation_markdown(report),
        encoding="utf-8",
    )

    return json_path, markdown_path


__all__ = [
    "OfflineRetrievalValidationReport",
    "OfflineValidationCheck",
    "build_offline_validation_report",
    "render_offline_validation_markdown",
    "write_offline_validation_reports",
]

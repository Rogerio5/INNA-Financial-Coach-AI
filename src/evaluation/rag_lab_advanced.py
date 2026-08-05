from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from src.evaluation.rag_lab_experiment_metadata import (
    build_experiment_metadata_readiness,
    extract_experiment_metadata,
)


class RagLabCapabilityStatus(StrEnum):
    ACTIVE = "active"
    PARTIAL = "partial"
    WAITING_DATA = "waiting_data"


@dataclass(frozen=True, slots=True)
class RagLabCapability:
    key: str
    status: RagLabCapabilityStatus
    message: str
    available_runs: int
    total_runs: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "status": self.status.value,
            "message": self.message,
            "available_runs": self.available_runs,
            "total_runs": self.total_runs,
        }


@dataclass(frozen=True, slots=True)
class QualityGateThresholds:
    answer_relevancy: float = 0.70
    faithfulness: float = 0.70
    contextual_relevancy: float = 0.70
    aggregate_score: float = 0.70
    maximum_regression: float = 0.05

    def __post_init__(self) -> None:
        values = (
            self.answer_relevancy,
            self.faithfulness,
            self.contextual_relevancy,
            self.aggregate_score,
            self.maximum_regression,
        )

        if any(not 0.0 <= float(value) <= 1.0 for value in values):
            raise ValueError(
                "Todos os limites do Quality Gate devem estar entre 0 e 1."
            )


@dataclass(frozen=True, slots=True)
class QualityGateCheck:
    key: str
    score: float | None
    threshold: float
    passed: bool | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QualityGateResult:
    run_reference: str
    passed: bool | None
    complete: bool
    checks: tuple[QualityGateCheck, ...]
    failed_keys: tuple[str, ...]
    unavailable_keys: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_reference": self.run_reference,
            "passed": self.passed,
            "complete": self.complete,
            "failed_keys": list(self.failed_keys),
            "unavailable_keys": list(self.unavailable_keys),
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass(frozen=True, slots=True)
class RagLabRankingEntry:
    position: int
    run_reference: str
    recorded_at: str
    branch: str
    environment: str
    quality_score: float
    passed: bool | None
    failing_metric_count: int
    latency_ms: float | None
    estimated_cost_usd: float | None
    ranking_basis: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalise_score(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    if not 0.0 <= score <= 1.0:
        return None

    return score


def _normalise_non_negative_number(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number < 0:
        return None

    return number


def _metric_scores(
    entry: Any,
) -> dict[str, float]:
    scores: dict[str, float] = {}

    for metric in getattr(
        entry,
        "metrics",
        (),
    ):
        metric_id = str(
            getattr(
                metric,
                "metric_id",
                "",
            )
        )

        score = _normalise_score(
            getattr(
                metric,
                "average_score",
                None,
            )
        )

        if metric_id and score is not None:
            scores[metric_id] = score

    return scores


def _aggregate_score(
    entry: Any,
) -> float | None:
    rag_triad = getattr(
        entry,
        "rag_triad",
        None,
    )

    if rag_triad is None:
        return None

    return _normalise_score(
        getattr(
            rag_triad,
            "average_score",
            None,
        )
    )


def _triad_passed(
    entry: Any,
) -> bool | None:
    rag_triad = getattr(
        entry,
        "rag_triad",
        None,
    )

    if rag_triad is None:
        return None

    value = getattr(
        rag_triad,
        "passed",
        None,
    )

    return value if isinstance(value, bool) else None


def evaluate_quality_gate(
    entry: Any,
    *,
    thresholds: QualityGateThresholds,
    baseline_entry: Any | None = None,
) -> QualityGateResult:
    scores = _metric_scores(entry)

    requirements = (
        (
            "answer-relevancy",
            scores.get("answer-relevancy"),
            thresholds.answer_relevancy,
        ),
        (
            "faithfulness",
            scores.get("faithfulness"),
            thresholds.faithfulness,
        ),
        (
            "contextual-relevancy",
            scores.get("contextual-relevancy"),
            thresholds.contextual_relevancy,
        ),
        (
            "rag-triad-average",
            _aggregate_score(entry),
            thresholds.aggregate_score,
        ),
    )

    checks: list[QualityGateCheck] = []

    for key, score, threshold in requirements:
        if score is None:
            checks.append(
                QualityGateCheck(
                    key=key,
                    score=None,
                    threshold=threshold,
                    passed=None,
                    reason=("Score não registrado nesta execução."),
                )
            )
            continue

        passed = score >= threshold

        checks.append(
            QualityGateCheck(
                key=key,
                score=score,
                threshold=threshold,
                passed=passed,
                reason=("Limite atendido." if passed else "Score abaixo do limite."),
            )
        )

    if baseline_entry is not None:
        baseline_score = _aggregate_score(baseline_entry)

        candidate_score = _aggregate_score(entry)

        if baseline_score is None or candidate_score is None:
            regression_passed = None
            regression_score = None
            reason = "Comparação de regressão indisponível."
        else:
            regression = baseline_score - candidate_score

            regression_score = regression
            regression_passed = regression <= thresholds.maximum_regression

            reason = (
                "Regressão dentro do limite."
                if regression_passed
                else "Regressão acima do limite."
            )

        checks.append(
            QualityGateCheck(
                key="maximum-regression",
                score=regression_score,
                threshold=(thresholds.maximum_regression),
                passed=regression_passed,
                reason=reason,
            )
        )

    unavailable_keys = tuple(check.key for check in checks if check.passed is None)

    failed_keys = tuple(check.key for check in checks if check.passed is False)

    complete = not unavailable_keys

    passed = not failed_keys if complete else None

    return QualityGateResult(
        run_reference=str(
            getattr(
                entry,
                "run_reference",
                "",
            )
            or "run"
        ),
        passed=passed,
        complete=complete,
        checks=tuple(checks),
        failed_keys=failed_keys,
        unavailable_keys=unavailable_keys,
    )


def build_rag_lab_capabilities(
    history: Any,
) -> tuple[RagLabCapability, ...]:
    readiness = {
        item.key: item for item in (build_experiment_metadata_readiness(history))
    }

    total_runs = len(
        tuple(
            getattr(
                history,
                "entries",
                (),
            )
        )
    )

    definitions = (
        (
            "reranker_comparison",
            ("reranker_enabled",),
            ("Comparação entre reranker ligado e desligado."),
        ),
        (
            "retrieval_strategy_comparison",
            ("retrieval_strategy",),
            ("Comparação entre estratégias híbrida, vetorial e lexical."),
        ),
        (
            "model_prompt_comparison",
            (
                "model_name",
                "prompt_version",
            ),
            ("Comparação por modelo e versão de prompt."),
        ),
        (
            "rag_configuration_comparison",
            (
                "top_k",
                "embedding_model",
                "knowledge_base_version",
                "chunk_size",
                "chunk_overlap",
            ),
            ("Comparação das configurações de recuperação e conhecimento."),
        ),
        (
            "performance_cost_analysis",
            (
                "latency_ms",
                "input_tokens",
                "output_tokens",
                "estimated_cost_usd",
            ),
            ("Análise de latência, tokens e custos."),
        ),
        (
            "phoenix_trace_integration",
            ("phoenix_trace_id",),
            ("Abertura da trace Phoenix relacionada à execução."),
        ),
    )

    capabilities: list[RagLabCapability] = []

    for key, required_fields, description in definitions:
        coverage_values = []

        for field_key in required_fields:
            item = readiness.get(field_key)

            coverage_values.append(item.available_runs if item is not None else 0)

        maximum_available = max(
            coverage_values,
            default=0,
        )

        minimum_available = min(
            coverage_values,
            default=0,
        )

        if total_runs > 0 and minimum_available == total_runs:
            status = RagLabCapabilityStatus.ACTIVE
            message = f"{description} Dados disponíveis em todas as execuções."
        elif maximum_available > 0:
            status = RagLabCapabilityStatus.PARTIAL
            message = f"{description} Apenas parte do histórico possui os metadados."
        else:
            status = RagLabCapabilityStatus.WAITING_DATA
            message = f"{description} Aguardando metadados reais."

        capabilities.append(
            RagLabCapability(
                key=key,
                status=status,
                message=message,
                available_runs=(maximum_available),
                total_runs=total_runs,
            )
        )

    return tuple(capabilities)


def rank_rag_lab_runs(
    history: Any,
) -> tuple[RagLabRankingEntry, ...]:
    candidates = []

    for entry in getattr(
        history,
        "entries",
        (),
    ):
        score = _aggregate_score(entry)

        if score is None:
            continue

        metadata = extract_experiment_metadata(entry)

        latency = _normalise_non_negative_number(metadata.get("latency_ms"))

        cost = _normalise_non_negative_number(metadata.get("estimated_cost_usd"))

        rag_triad = getattr(
            entry,
            "rag_triad",
            None,
        )

        failing_metric_ids = tuple(
            getattr(
                rag_triad,
                "failing_metric_ids",
                (),
            )
            if rag_triad is not None
            else ()
        )

        candidates.append(
            {
                "entry": entry,
                "score": score,
                "latency": latency,
                "cost": cost,
                "failing_metric_count": len(failing_metric_ids),
            }
        )

    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["failing_metric_count"],
            (item["latency"] if item["latency"] is not None else float("inf")),
            (item["cost"] if item["cost"] is not None else float("inf")),
        )
    )

    ranking = []

    for position, item in enumerate(
        candidates,
        start=1,
    ):
        entry = item["entry"]

        has_performance_data = item["latency"] is not None or item["cost"] is not None

        ranking.append(
            RagLabRankingEntry(
                position=position,
                run_reference=str(
                    getattr(
                        entry,
                        "run_reference",
                        "",
                    )
                ),
                recorded_at=str(
                    getattr(
                        entry,
                        "recorded_at",
                        "",
                    )
                ),
                branch=str(
                    getattr(
                        entry,
                        "branch",
                        "",
                    )
                ),
                environment=str(
                    getattr(
                        entry,
                        "environment",
                        "",
                    )
                ),
                quality_score=item["score"],
                passed=_triad_passed(entry),
                failing_metric_count=(item["failing_metric_count"]),
                latency_ms=item["latency"],
                estimated_cost_usd=(item["cost"]),
                ranking_basis=(
                    "quality_then_performance"
                    if has_performance_data
                    else "quality_only"
                ),
            )
        )

    return tuple(ranking)


def calculate_cost_per_approved_run(
    history: Any,
) -> float | None:
    total_cost = 0.0
    approved_with_cost = 0

    for entry in getattr(
        history,
        "entries",
        (),
    ):
        if _triad_passed(entry) is not True:
            continue

        metadata = extract_experiment_metadata(entry)

        cost = _normalise_non_negative_number(metadata.get("estimated_cost_usd"))

        if cost is None:
            continue

        total_cost += cost
        approved_with_cost += 1

    if approved_with_cost == 0:
        return None

    return total_cost / approved_with_cost


def export_rag_lab_history_csv(
    history: Any,
) -> str:
    output = io.StringIO()

    fieldnames = (
        "run_reference",
        "recorded_at",
        "branch",
        "commit_sha",
        "environment",
        "evaluation_mode",
        "rag_triad_score",
        "rag_triad_passed",
        "answer_relevancy",
        "faithfulness",
        "contextual_relevancy",
        "retrieval_strategy",
        "reranker_enabled",
        "top_k",
        "model_name",
        "prompt_version",
        "embedding_model",
        "knowledge_base_version",
        "latency_ms",
        "input_tokens",
        "output_tokens",
        "estimated_cost_usd",
        "phoenix_trace_id",
    )

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )

    writer.writeheader()

    for entry in getattr(
        history,
        "entries",
        (),
    ):
        metadata = extract_experiment_metadata(entry)

        scores = _metric_scores(entry)

        row = {
            "run_reference": getattr(
                entry,
                "run_reference",
                "",
            ),
            "recorded_at": getattr(
                entry,
                "recorded_at",
                "",
            ),
            "branch": getattr(
                entry,
                "branch",
                "",
            ),
            "commit_sha": getattr(
                entry,
                "commit_sha",
                "",
            ),
            "environment": getattr(
                entry,
                "environment",
                "",
            ),
            "evaluation_mode": getattr(
                entry,
                "evaluation_mode",
                "",
            ),
            "rag_triad_score": (_aggregate_score(entry)),
            "rag_triad_passed": (_triad_passed(entry)),
            "answer_relevancy": scores.get("answer-relevancy"),
            "faithfulness": scores.get("faithfulness"),
            "contextual_relevancy": scores.get("contextual-relevancy"),
            **metadata,
        }

        writer.writerow(row)

    return output.getvalue()


def export_rag_lab_report_json(
    history: Any,
    *,
    quality_gate: QualityGateThresholds,
) -> str:
    entries = tuple(
        getattr(
            history,
            "entries",
            (),
        )
    )

    payload = {
        "schema_version": "1.0",
        "simulation": False,
        "run_count": len(entries),
        "capabilities": [
            item.to_dict() for item in (build_rag_lab_capabilities(history))
        ],
        "ranking": [item.to_dict() for item in rank_rag_lab_runs(history)],
        "quality_gate": {
            "thresholds": asdict(quality_gate),
            "results": [
                evaluate_quality_gate(
                    entry,
                    thresholds=quality_gate,
                ).to_dict()
                for entry in entries
            ],
        },
        "cost_per_approved_run": (calculate_cost_per_approved_run(history)),
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )

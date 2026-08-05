from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from src.evaluation.rag_triad import (
    RAG_TRIAD_METRIC_IDS,
)


class RagLabComparisonStatus(StrEnum):
    """Resultado normalizado de uma comparação."""

    IMPROVED = "improved"
    STABLE = "stable"
    REGRESSED = "regressed"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class RagLabAxisComparison:
    """Comparação de um eixo individual da RAG Triad."""

    metric_id: str
    baseline_score: float | None
    candidate_score: float | None
    delta: float | None
    status: RagLabComparisonStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "baseline_score": self.baseline_score,
            "candidate_score": self.candidate_score,
            "delta": self.delta,
            "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class RagLabComparison:
    """
    Resultado completo da comparação entre duas execuções.

    A comparação usa:
    - score agregado da RAG Triad;
    - Answer Relevancy;
    - Faithfulness;
    - Contextual Relevancy.
    """

    baseline_reference: str
    candidate_reference: str
    baseline_score: float | None
    candidate_score: float | None
    delta: float | None
    status: RagLabComparisonStatus
    axes: tuple[RagLabAxisComparison, ...]
    complete: bool
    baseline_passed: bool | None
    candidate_passed: bool | None
    improved_metric_ids: tuple[str, ...]
    regressed_metric_ids: tuple[str, ...]
    stable_metric_ids: tuple[str, ...]
    unavailable_metric_ids: tuple[str, ...]

    @property
    def has_regression(self) -> bool:
        return bool(
            self.status == RagLabComparisonStatus.REGRESSED or self.regressed_metric_ids
        )

    @property
    def has_improvement(self) -> bool:
        return bool(
            self.status == RagLabComparisonStatus.IMPROVED or self.improved_metric_ids
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_reference": (self.baseline_reference),
            "candidate_reference": (self.candidate_reference),
            "baseline_score": self.baseline_score,
            "candidate_score": self.candidate_score,
            "delta": self.delta,
            "status": self.status.value,
            "complete": self.complete,
            "baseline_passed": self.baseline_passed,
            "candidate_passed": self.candidate_passed,
            "has_regression": self.has_regression,
            "has_improvement": self.has_improvement,
            "improved_metric_ids": list(self.improved_metric_ids),
            "regressed_metric_ids": list(self.regressed_metric_ids),
            "stable_metric_ids": list(self.stable_metric_ids),
            "unavailable_metric_ids": list(self.unavailable_metric_ids),
            "axes": [axis.to_dict() for axis in self.axes],
        }


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


def _classify_delta(
    delta: float | None,
    *,
    tolerance: float,
) -> RagLabComparisonStatus:
    if delta is None:
        return RagLabComparisonStatus.UNAVAILABLE

    if delta > tolerance:
        return RagLabComparisonStatus.IMPROVED

    if delta < -tolerance:
        return RagLabComparisonStatus.REGRESSED

    return RagLabComparisonStatus.STABLE


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


def _triad_score(
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

    passed = getattr(
        rag_triad,
        "passed",
        None,
    )

    if isinstance(passed, bool):
        return passed

    return None


def compare_rag_triad_entries(
    baseline: Any,
    candidate: Any,
    *,
    tolerance: float = 0.005,
) -> RagLabComparison:
    """
    Compara duas execuções persistidas no histórico.

    tolerance:
        Diferença mínima para classificar uma alteração como
        melhoria ou regressão. O padrão de 0.005 representa
        meio ponto percentual.
    """

    if tolerance < 0:
        raise ValueError("tolerance não pode ser negativa.")

    baseline_reference = str(
        getattr(
            baseline,
            "run_reference",
            "",
        )
        or "baseline"
    )

    candidate_reference = str(
        getattr(
            candidate,
            "run_reference",
            "",
        )
        or "candidate"
    )

    baseline_scores = _metric_scores(baseline)

    candidate_scores = _metric_scores(candidate)

    axis_results: list[RagLabAxisComparison] = []

    for metric_id in RAG_TRIAD_METRIC_IDS:
        baseline_axis_score = baseline_scores.get(metric_id)

        candidate_axis_score = candidate_scores.get(metric_id)

        delta = (
            candidate_axis_score - baseline_axis_score
            if (baseline_axis_score is not None and candidate_axis_score is not None)
            else None
        )

        axis_results.append(
            RagLabAxisComparison(
                metric_id=metric_id,
                baseline_score=(baseline_axis_score),
                candidate_score=(candidate_axis_score),
                delta=delta,
                status=_classify_delta(
                    delta,
                    tolerance=tolerance,
                ),
            )
        )

    baseline_score = _triad_score(baseline)

    candidate_score = _triad_score(candidate)

    aggregate_delta = (
        candidate_score - baseline_score
        if (baseline_score is not None and candidate_score is not None)
        else None
    )

    aggregate_status = _classify_delta(
        aggregate_delta,
        tolerance=tolerance,
    )

    improved_metric_ids = tuple(
        axis.metric_id
        for axis in axis_results
        if (axis.status == RagLabComparisonStatus.IMPROVED)
    )

    regressed_metric_ids = tuple(
        axis.metric_id
        for axis in axis_results
        if (axis.status == RagLabComparisonStatus.REGRESSED)
    )

    stable_metric_ids = tuple(
        axis.metric_id
        for axis in axis_results
        if (axis.status == RagLabComparisonStatus.STABLE)
    )

    unavailable_metric_ids = tuple(
        axis.metric_id
        for axis in axis_results
        if (axis.status == RagLabComparisonStatus.UNAVAILABLE)
    )

    complete = bool(aggregate_delta is not None and not unavailable_metric_ids)

    return RagLabComparison(
        baseline_reference=baseline_reference,
        candidate_reference=candidate_reference,
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        delta=aggregate_delta,
        status=aggregate_status,
        axes=tuple(axis_results),
        complete=complete,
        baseline_passed=_triad_passed(baseline),
        candidate_passed=_triad_passed(candidate),
        improved_metric_ids=(improved_metric_ids),
        regressed_metric_ids=(regressed_metric_ids),
        stable_metric_ids=stable_metric_ids,
        unavailable_metric_ids=(unavailable_metric_ids),
    )

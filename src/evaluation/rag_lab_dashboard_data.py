from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.evaluation.rag_lab_comparison import (
    RagLabComparison,
    compare_rag_triad_entries,
)
from src.evaluation.rag_triad import (
    RAG_TRIAD_METRIC_IDS,
)


@dataclass(frozen=True, slots=True)
class RagLabSummary:
    """Resumo executivo do Laboratório RAG."""

    total_history_runs: int
    comparable_runs: int
    approved_runs: int
    failed_runs: int
    incomplete_runs: int
    approval_rate: float | None
    latest_reference: str | None
    latest_score: float | None
    latest_status: str | None
    best_reference: str | None
    best_score: float | None
    worst_reference: str | None
    worst_score: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_history_runs": (
                self.total_history_runs
            ),
            "comparable_runs": self.comparable_runs,
            "approved_runs": self.approved_runs,
            "failed_runs": self.failed_runs,
            "incomplete_runs": self.incomplete_runs,
            "approval_rate": self.approval_rate,
            "latest_reference": (
                self.latest_reference
            ),
            "latest_score": self.latest_score,
            "latest_status": self.latest_status,
            "best_reference": self.best_reference,
            "best_score": self.best_score,
            "worst_reference": self.worst_reference,
            "worst_score": self.worst_score,
        }


@dataclass(frozen=True, slots=True)
class RagLabRunOption:
    """Execução disponível nos seletores do laboratório."""

    run_reference: str
    recorded_at: str
    branch: str
    environment: str
    evaluation_mode: str
    score: float | None
    status: str
    passed: bool | None
    complete: bool
    label: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_reference": self.run_reference,
            "recorded_at": self.recorded_at,
            "branch": self.branch,
            "environment": self.environment,
            "evaluation_mode": (
                self.evaluation_mode
            ),
            "score": self.score,
            "status": self.status,
            "passed": self.passed,
            "complete": self.complete,
            "label": self.label,
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


def _parse_datetime(
    value: Any,
) -> datetime:
    text = str(value or "").strip()

    if not text:
        return datetime.min.replace(
            tzinfo=UTC
        )

    try:
        parsed = datetime.fromisoformat(
            text.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError:
        return datetime.min.replace(
            tzinfo=UTC
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone(UTC)


def _triad_of(
    entry: Any,
) -> Any | None:
    return getattr(
        entry,
        "rag_triad",
        None,
    )


def _triad_score(
    entry: Any,
) -> float | None:
    triad = _triad_of(entry)

    if triad is None:
        return None

    return _normalise_score(
        getattr(
            triad,
            "average_score",
            None,
        )
    )


def _triad_status(
    entry: Any,
) -> str:
    triad = _triad_of(entry)

    if triad is None:
        return "unavailable"

    return str(
        getattr(
            triad,
            "status",
            "unavailable",
        )
        or "unavailable"
    )


def _triad_passed(
    entry: Any,
) -> bool | None:
    triad = _triad_of(entry)

    if triad is None:
        return None

    passed = getattr(
        triad,
        "passed",
        None,
    )

    return (
        passed
        if isinstance(passed, bool)
        else None
    )


def _triad_complete(
    entry: Any,
) -> bool:
    triad = _triad_of(entry)

    if triad is None:
        return False

    total_cases = getattr(
        triad,
        "total_cases",
        0,
    )

    complete_cases = getattr(
        triad,
        "complete_cases",
        0,
    )

    try:
        total = int(total_cases)
        complete = int(complete_cases)
    except (TypeError, ValueError):
        return False

    return bool(
        total > 0
        and complete == total
        and _triad_score(entry) is not None
    )


def get_rag_lab_entries(
    history: Any,
    *,
    complete_only: bool = False,
) -> tuple[Any, ...]:
    """
    Retorna execuções com RAG Triad ordenadas da mais recente
    para a mais antiga.
    """

    entries = tuple(
        getattr(
            history,
            "entries",
            (),
        )
    )

    selected = []

    for entry in entries:
        if _triad_of(entry) is None:
            continue

        if (
            complete_only
            and not _triad_complete(entry)
        ):
            continue

        selected.append(entry)

    return tuple(
        sorted(
            selected,
            key=lambda item: _parse_datetime(
                getattr(
                    item,
                    "recorded_at",
                    "",
                )
            ),
            reverse=True,
        )
    )


def build_rag_lab_summary(
    history: Any,
) -> RagLabSummary:
    all_entries = tuple(
        getattr(
            history,
            "entries",
            (),
        )
    )

    triad_entries = get_rag_lab_entries(
        history
    )

    complete_entries = tuple(
        entry
        for entry in triad_entries
        if _triad_complete(entry)
    )

    approved_runs = sum(
        1
        for entry in triad_entries
        if _triad_passed(entry) is True
    )

    failed_runs = sum(
        1
        for entry in triad_entries
        if _triad_passed(entry) is False
    )

    incomplete_runs = sum(
        1
        for entry in triad_entries
        if not _triad_complete(entry)
    )

    classified_runs = (
        approved_runs + failed_runs
    )

    approval_rate = (
        approved_runs / classified_runs
        if classified_runs
        else None
    )

    latest = (
        triad_entries[0]
        if triad_entries
        else None
    )

    scored_entries = tuple(
        entry
        for entry in complete_entries
        if _triad_score(entry) is not None
    )

    best = (
        max(
            scored_entries,
            key=lambda item: (
                _triad_score(item)
                or 0.0
            ),
        )
        if scored_entries
        else None
    )

    worst = (
        min(
            scored_entries,
            key=lambda item: (
                _triad_score(item)
                or 0.0
            ),
        )
        if scored_entries
        else None
    )

    return RagLabSummary(
        total_history_runs=len(all_entries),
        comparable_runs=len(
            complete_entries
        ),
        approved_runs=approved_runs,
        failed_runs=failed_runs,
        incomplete_runs=incomplete_runs,
        approval_rate=approval_rate,
        latest_reference=(
            str(
                getattr(
                    latest,
                    "run_reference",
                    "",
                )
            )
            if latest is not None
            else None
        ),
        latest_score=(
            _triad_score(latest)
            if latest is not None
            else None
        ),
        latest_status=(
            _triad_status(latest)
            if latest is not None
            else None
        ),
        best_reference=(
            str(
                getattr(
                    best,
                    "run_reference",
                    "",
                )
            )
            if best is not None
            else None
        ),
        best_score=(
            _triad_score(best)
            if best is not None
            else None
        ),
        worst_reference=(
            str(
                getattr(
                    worst,
                    "run_reference",
                    "",
                )
            )
            if worst is not None
            else None
        ),
        worst_score=(
            _triad_score(worst)
            if worst is not None
            else None
        ),
    )


def build_rag_lab_run_options(
    history: Any,
    *,
    complete_only: bool = True,
) -> tuple[RagLabRunOption, ...]:
    entries = get_rag_lab_entries(
        history,
        complete_only=complete_only,
    )

    options = []

    for entry in entries:
        reference = str(
            getattr(
                entry,
                "run_reference",
                "",
            )
            or "run"
        )

        recorded_at = str(
            getattr(
                entry,
                "recorded_at",
                "",
            )
            or ""
        )

        branch = str(
            getattr(
                entry,
                "branch",
                "",
            )
            or "unknown"
        )

        environment = str(
            getattr(
                entry,
                "environment",
                "",
            )
            or "unknown"
        )

        evaluation_mode = str(
            getattr(
                entry,
                "evaluation_mode",
                "",
            )
            or "unknown"
        )

        score = _triad_score(entry)
        score_label = (
            f"{score:.2%}"
            if score is not None
            else "sem score"
        )

        label = (
            f"{reference} | "
            f"{score_label} | "
            f"{environment} | "
            f"{branch}"
        )

        options.append(
            RagLabRunOption(
                run_reference=reference,
                recorded_at=recorded_at,
                branch=branch,
                environment=environment,
                evaluation_mode=(
                    evaluation_mode
                ),
                score=score,
                status=_triad_status(entry),
                passed=_triad_passed(entry),
                complete=_triad_complete(
                    entry
                ),
                label=label,
            )
        )

    return tuple(options)


def find_rag_lab_entry(
    history: Any,
    run_reference: str,
) -> Any | None:
    reference = str(
        run_reference or ""
    ).strip()

    if not reference:
        return None

    for entry in get_rag_lab_entries(
        history
    ):
        if (
            str(
                getattr(
                    entry,
                    "run_reference",
                    "",
                )
            )
            == reference
        ):
            return entry

    return None


def select_default_comparison(
    history: Any,
) -> tuple[Any, Any] | None:
    """
    Usa a penúltima execução como baseline e a mais recente
    como candidata.
    """

    entries = get_rag_lab_entries(
        history,
        complete_only=True,
    )

    if len(entries) < 2:
        return None

    candidate = entries[0]
    baseline = entries[1]

    return baseline, candidate


def build_selected_comparison(
    history: Any,
    *,
    baseline_reference: str,
    candidate_reference: str,
    tolerance: float = 0.005,
) -> RagLabComparison | None:
    if (
        baseline_reference
        == candidate_reference
    ):
        return None

    baseline = find_rag_lab_entry(
        history,
        baseline_reference,
    )

    candidate = find_rag_lab_entry(
        history,
        candidate_reference,
    )

    if (
        baseline is None
        or candidate is None
    ):
        return None

    return compare_rag_triad_entries(
        baseline,
        candidate,
        tolerance=tolerance,
    )


def build_rag_lab_comparison_rows(
    comparison: RagLabComparison,
) -> list[dict[str, Any]]:
    rows = []

    for axis in comparison.axes:
        rows.append(
            {
                "metric_id": axis.metric_id,
                "baseline_score": (
                    axis.baseline_score
                ),
                "candidate_score": (
                    axis.candidate_score
                ),
                "delta": axis.delta,
                "status": axis.status.value,
            }
        )

    rows.append(
        {
            "metric_id": "rag-triad-average",
            "baseline_score": (
                comparison.baseline_score
            ),
            "candidate_score": (
                comparison.candidate_score
            ),
            "delta": comparison.delta,
            "status": comparison.status.value,
        }
    )

    return rows


def build_rag_lab_timeline(
    history: Any,
) -> list[dict[str, Any]]:
    rows = []

    entries = reversed(
        get_rag_lab_entries(history)
    )

    for entry in entries:
        metric_scores = {
            str(
                getattr(
                    metric,
                    "metric_id",
                    "",
                )
            ): _normalise_score(
                getattr(
                    metric,
                    "average_score",
                    None,
                )
            )
            for metric in getattr(
                entry,
                "metrics",
                (),
            )
        }

        row: dict[str, Any] = {
            "run_reference": str(
                getattr(
                    entry,
                    "run_reference",
                    "",
                )
            ),
            "recorded_at": str(
                getattr(
                    entry,
                    "recorded_at",
                    "",
                )
            ),
            "branch": str(
                getattr(
                    entry,
                    "branch",
                    "",
                )
            ),
            "environment": str(
                getattr(
                    entry,
                    "environment",
                    "",
                )
            ),
            "rag_triad_score": (
                _triad_score(entry)
            ),
            "rag_triad_status": (
                _triad_status(entry)
            ),
            "rag_triad_passed": (
                _triad_passed(entry)
            ),
            "complete": (
                _triad_complete(entry)
            ),
        }

        for metric_id in (
            RAG_TRIAD_METRIC_IDS
        ):
            row[metric_id] = (
                metric_scores.get(metric_id)
            )

        rows.append(row)

    return rows

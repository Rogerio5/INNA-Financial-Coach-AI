"""Avaliação dos resultados reais de retrieval textual do Neon.

O módulo recebe um relatório previamente coletado, remove resultados
duplicados e aplica um gabarito humano de relevância graduada.

Nenhuma conexão com Neon ou chamada Gemini é executada.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsResult,
    evaluate_retrieval_case,
)


@dataclass(frozen=True, slots=True)
class RealRetrievalCaseResult:
    """Resultado avaliado de uma pergunta real."""

    case_id: str
    question: str
    original_result_count: int
    deduplicated_result_count: int
    duplicate_count: int
    binary_relevance_threshold: int
    retrieved_ids: tuple[str, ...]
    relevance_grades: Mapping[str, float]
    metrics: RetrievalMetricsResult
    coverage_status: str


@dataclass(frozen=True, slots=True)
class RealRetrievalAggregate:
    """Médias agregadas da execução real."""

    case_count: int
    mean_hit_rate: float
    mean_recall: float
    mean_precision: float
    mean_reciprocal_rank: float
    mean_ndcg: float
    total_original_results: int
    total_unique_results: int
    total_duplicates_removed: int
    cases_without_strong_relevance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RealRetrievalQualityGate:
    """Quality gate dos resultados textuais reais."""

    passed: bool
    checks: Mapping[str, bool]
    failed_checks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RealRetrievalEvaluationReport:
    """Relatório completo da Fase 5A.3."""

    schema_version: int
    source_report: str
    judgment_name: str
    binary_relevance_threshold: int
    cases: tuple[RealRetrievalCaseResult, ...]
    aggregate: RealRetrievalAggregate
    quality_gate: RealRetrievalQualityGate
    neon_queried_during_evaluation: bool
    gemini_used: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_preview(value: object) -> str:
    text = re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()

    return text.casefold()


def _canonical_result_id(result: Mapping[str, Any]) -> str:
    preview = _normalize_preview(result.get("text_preview"))

    if not preview:
        preview = "|".join(
            (
                str(result.get("document_name", "")),
                str(result.get("chunk_index", "")),
                str(result.get("chunk_id", "")),
            )
        ).casefold()

    digest = hashlib.sha256(preview.encode("utf-8")).hexdigest()[:20]

    return f"content:{digest}"


def deduplicate_results(
    results: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Remove conteúdos equivalentes preservando o primeiro ranking."""

    unique: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for result in results:
        canonical_id = _canonical_result_id(result)

        if canonical_id in seen_ids:
            continue

        seen_ids.add(canonical_id)

        item = dict(result)
        item["canonical_id"] = canonical_id
        item["original_rank"] = int(result.get("rank", len(unique) + 1))
        item["deduplicated_rank"] = len(unique) + 1

        unique.append(item)

    return tuple(unique)


def load_judgments(
    path: str | Path,
) -> dict[str, Any]:
    judgment_path = Path(path)

    if not judgment_path.is_file():
        raise FileNotFoundError(f"Gabarito nao encontrado: {judgment_path}")

    payload = json.loads(judgment_path.read_text(encoding="utf-8-sig"))

    if not isinstance(payload, dict):
        raise TypeError("A raiz do gabarito deve ser um objeto.")

    if not isinstance(payload.get("cases"), dict):
        raise TypeError("O gabarito deve possuir cases como objeto.")

    threshold = payload.get("binary_relevance_threshold")

    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("binary_relevance_threshold deve ser inteiro positivo.")

    return payload


def _grade_for_result(
    result: Mapping[str, Any],
    case_judgment: Mapping[str, Any],
) -> float:
    chunk_index = str(result.get("chunk_index", ""))

    grades = case_judgment.get(
        "chunk_index_grades",
        {},
    )

    if not isinstance(grades, dict):
        raise TypeError("chunk_index_grades deve ser um objeto.")

    grade = float(grades.get(chunk_index, 0))

    if grade < 0:
        raise ValueError("O grau de relevancia nao pode ser negativo.")

    return grade


def _coverage_status(
    grades: Sequence[float],
    threshold: int,
) -> str:
    if any(grade >= threshold for grade in grades):
        return "strong_relevance_found"

    if any(grade > 0 for grade in grades):
        return "partial_relevance_only"

    return "no_relevant_content_found"


def evaluate_real_textual_report(
    *,
    source_report_path: str | Path,
    judgment_path: str | Path,
) -> RealRetrievalEvaluationReport:
    """Avalia o relatório textual real sem nova consulta ao banco."""

    source_path = Path(source_report_path)

    if not source_path.is_file():
        raise FileNotFoundError(f"Relatorio real nao encontrado: {source_path}")

    source = json.loads(source_path.read_text(encoding="utf-8-sig"))
    judgments = load_judgments(judgment_path)

    raw_cases = source.get("questions")

    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("O relatorio real nao possui perguntas.")

    threshold = int(judgments["binary_relevance_threshold"])
    judgment_cases = judgments["cases"]

    evaluated_cases: list[RealRetrievalCaseResult] = []

    for raw_case in raw_cases:
        case_id = str(raw_case.get("case_id", "")).strip()

        if case_id not in judgment_cases:
            raise ValueError(f"Nao existe gabarito para o caso: {case_id}")

        raw_results = raw_case.get("results", [])

        if not isinstance(raw_results, list):
            raise TypeError(f"results invalido para o caso {case_id}.")

        unique_results = deduplicate_results(raw_results)
        case_judgment = judgment_cases[case_id]

        retrieved_ids: list[str] = []
        graded_relevance: dict[str, float] = {}
        relevant_ids: list[str] = []
        observed_grades: list[float] = []

        for result in unique_results:
            canonical_id = str(result["canonical_id"])
            grade = _grade_for_result(
                result,
                case_judgment,
            )

            retrieved_ids.append(canonical_id)
            graded_relevance[canonical_id] = grade
            observed_grades.append(grade)

            if grade >= threshold:
                relevant_ids.append(canonical_id)

        metrics = evaluate_retrieval_case(
            retrieved_document_ids=retrieved_ids,
            relevant_document_ids=relevant_ids,
            graded_relevance=graded_relevance,
            k=int(raw_case.get("top_k", 4)),
        )

        evaluated_cases.append(
            RealRetrievalCaseResult(
                case_id=case_id,
                question=str(raw_case.get("question", "")),
                original_result_count=len(raw_results),
                deduplicated_result_count=len(unique_results),
                duplicate_count=(len(raw_results) - len(unique_results)),
                binary_relevance_threshold=threshold,
                retrieved_ids=tuple(retrieved_ids),
                relevance_grades=graded_relevance,
                metrics=metrics,
                coverage_status=_coverage_status(
                    observed_grades,
                    threshold,
                ),
            )
        )

    cases = tuple(evaluated_cases)

    cases_without_strong_relevance = tuple(
        case.case_id
        for case in cases
        if case.coverage_status != "strong_relevance_found"
    )

    aggregate = RealRetrievalAggregate(
        case_count=len(cases),
        mean_hit_rate=mean(case.metrics.hit_rate for case in cases),
        mean_recall=mean(case.metrics.recall for case in cases),
        mean_precision=mean(case.metrics.precision for case in cases),
        mean_reciprocal_rank=mean(case.metrics.reciprocal_rank for case in cases),
        mean_ndcg=mean(case.metrics.ndcg for case in cases),
        total_original_results=sum(case.original_result_count for case in cases),
        total_unique_results=sum(case.deduplicated_result_count for case in cases),
        total_duplicates_removed=sum(case.duplicate_count for case in cases),
        cases_without_strong_relevance=(cases_without_strong_relevance),
    )

    checks = {
        "hit_rate": aggregate.mean_hit_rate >= 0.80,
        "recall": aggregate.mean_recall >= 0.75,
        "precision": aggregate.mean_precision >= 0.50,
        "mrr": (aggregate.mean_reciprocal_rank >= 0.70),
        "ndcg": aggregate.mean_ndcg >= 0.75,
        "coverage": (not aggregate.cases_without_strong_relevance),
    }

    failed_checks = tuple(name for name, passed in checks.items() if not passed)

    return RealRetrievalEvaluationReport(
        schema_version=1,
        source_report=str(source_path),
        judgment_name=str(
            judgments.get(
                "name",
                "retrieval-textual-judgment",
            )
        ),
        binary_relevance_threshold=threshold,
        cases=cases,
        aggregate=aggregate,
        quality_gate=RealRetrievalQualityGate(
            passed=not failed_checks,
            checks=checks,
            failed_checks=failed_checks,
        ),
        neon_queried_during_evaluation=False,
        gemini_used=False,
    )


def write_real_evaluation_report(
    report: RealRetrievalEvaluationReport,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return path


__all__ = [
    "RealRetrievalAggregate",
    "RealRetrievalCaseResult",
    "RealRetrievalEvaluationReport",
    "RealRetrievalQualityGate",
    "deduplicate_results",
    "evaluate_real_textual_report",
    "load_judgments",
    "write_real_evaluation_report",
]

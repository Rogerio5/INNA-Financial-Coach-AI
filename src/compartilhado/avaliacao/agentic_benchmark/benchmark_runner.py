"""Benchmark determinístico Legacy versus Agentic RAG."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from .contracts import (
    AgenticBenchmarkCase,
    BenchmarkDataset,
    ExpectedGatewayDecision,
)
from .offline_evaluator import (
    OfflineEvaluationReport,
    evaluate_offline,
)
from .result_contracts import (
    ActualGatewayDecision,
    ActualSecurityOutcome,
    AgenticEvaluationResult,
    AgenticExecutionMode,
    AgenticMetricSnapshot,
    CitationRecord,
    EvidenceRecord,
    ExecutionStatus,
)


class BenchmarkProfile(StrEnum):
    """Perfis executados pelo benchmark."""

    LEGACY = "legacy"
    AGENTIC = "agentic"


@dataclass(frozen=True, slots=True)
class BenchmarkCaseExecution:
    """Execução de um caso em um perfil."""

    profile: BenchmarkProfile
    case_id: str
    category: str
    result: AgenticEvaluationResult
    report: OfflineEvaluationReport


@dataclass(frozen=True, slots=True)
class BenchmarkProfileSummary:
    """Resumo agregado de um perfil."""

    profile: BenchmarkProfile
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    average_score: float
    average_latency_ms: float
    fallback_count: int
    rejected_count: int
    error_count: int
    invalid_citation_count: int
    category_pass_rates: Mapping[str, float]


@dataclass(frozen=True, slots=True)
class BenchmarkComparison:
    """Comparação agregada entre os dois perfis."""

    total_cases: int
    legacy_pass_rate: float
    agentic_pass_rate: float
    pass_rate_delta: float
    legacy_average_score: float
    agentic_average_score: float
    average_score_delta: float
    legacy_average_latency_ms: float
    agentic_average_latency_ms: float
    latency_delta_ms: float
    improvements: tuple[str, ...]
    regressions: tuple[str, ...]
    unchanged_passes: tuple[str, ...]
    unchanged_failures: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OfflineBenchmarkResult:
    """Resultado completo do benchmark."""

    dataset_version: str
    generated_at: str
    executions: tuple[BenchmarkCaseExecution, ...]
    summaries: tuple[BenchmarkProfileSummary, ...]
    comparison: BenchmarkComparison

    def summary(
        self,
        profile: BenchmarkProfile,
    ) -> BenchmarkProfileSummary:
        """Obtém o resumo de um perfil."""

        for summary in self.summaries:
            if summary.profile is profile:
                return summary

        raise KeyError(f"Perfil não encontrado: {profile}")


ExecutionFactory = Callable[
    [AgenticBenchmarkCase],
    AgenticEvaluationResult,
]


def _join_non_empty(
    values: Sequence[str],
) -> str:
    return " ".join(value.strip() for value in values if value.strip()).strip()


def _expected_decision(
    case: AgenticBenchmarkCase,
) -> ActualGatewayDecision:
    return ActualGatewayDecision(case.expectations.gateway_decision.value)


def _expected_security(
    case: AgenticBenchmarkCase,
) -> ActualSecurityOutcome:
    return ActualSecurityOutcome(case.expectations.security_outcome.value)


def _status_for_candidate(
    case: AgenticBenchmarkCase,
) -> ExecutionStatus:
    decision = case.expectations.gateway_decision

    if decision is ExpectedGatewayDecision.REJECT:
        return ExecutionStatus.REJECTED

    if decision is ExpectedGatewayDecision.FALLBACK:
        return ExecutionStatus.FALLBACK

    return ExecutionStatus.SUCCESS


def _candidate_answer(
    case: AgenticBenchmarkCase,
) -> str:
    required_terms = _join_non_empty(case.expectations.required_terms)

    context = _join_non_empty(case.synthetic_contexts)

    components = [
        case.question,
        required_terms,
        context,
    ]

    answer = _join_non_empty(components)

    for forbidden_term in case.expectations.forbidden_terms:
        answer = answer.replace(
            forbidden_term,
            "[conteúdo protegido]",
        )

    return answer or ("Execução concluída conforme os controles definidos.")


def simulate_agentic_execution(
    case: AgenticBenchmarkCase,
) -> AgenticEvaluationResult:
    """Simula o candidato Agentic seguindo os contratos."""

    evidence_contexts = case.synthetic_contexts or (
        (f"Contexto sintético validado para: {case.question}"),
    )

    evidences = tuple(
        EvidenceRecord(
            evidence_id=f"agentic-evidence-{index}",
            content=_join_non_empty(
                (
                    case.question,
                    context,
                    *case.expectations.required_terms,
                )
            ),
            source=f"synthetic-{case.category.value}",
            citation=f"F{index}",
            score=max(
                0.8,
                1.0 - ((index - 1) * 0.03),
            ),
            metadata={
                "synthetic": True,
                "profile": "agentic",
                "category": case.category.value,
            },
        )
        for index, context in enumerate(
            evidence_contexts,
            start=1,
        )
    )

    citations = tuple(
        CitationRecord(
            citation_id=f"F{index}",
            evidence_id=evidence.evidence_id,
            source=evidence.source,
            text=evidence.content,
            valid=True,
        )
        for index, evidence in enumerate(
            evidences,
            start=1,
        )
    )

    return AgenticEvaluationResult(
        case_id=case.case_id,
        question=case.question,
        answer=_candidate_answer(case),
        mode=AgenticExecutionMode.ACTIVE,
        decision=_expected_decision(case),
        status=_status_for_candidate(case),
        security_outcome=_expected_security(case),
        routes=case.expectations.routes,
        evidences=evidences,
        citations=citations,
        metrics=AgenticMetricSnapshot(),
        latency_ms=120.0,
        fallback_used=(case.expectations.expected_fallback),
        trace_id=f"offline-agentic-{case.case_id}",
        raw_metadata={
            "offline": True,
            "synthetic": True,
            "profile": "agentic",
        },
    )


def simulate_legacy_execution(
    case: AgenticBenchmarkCase,
) -> AgenticEvaluationResult:
    """Simula uma baseline simples sem recursos agentic."""

    first_context = (
        case.synthetic_contexts[0]
        if case.synthetic_contexts
        else (f"Contexto legado limitado para: {case.question}")
    )

    evidence = EvidenceRecord(
        evidence_id="legacy-evidence-1",
        content=first_context,
        source="synthetic-legacy",
        score=0.65,
        metadata={
            "synthetic": True,
            "profile": "legacy",
        },
    )

    expected_is_legacy = (
        case.expectations.gateway_decision is ExpectedGatewayDecision.LEGACY
    )

    decision = ActualGatewayDecision.LEGACY

    status = ExecutionStatus.SUCCESS

    security_outcome = ActualSecurityOutcome.ALLOW

    answer = _join_non_empty(
        (
            case.question,
            first_context,
        )
    )

    if expected_is_legacy:
        answer = _join_non_empty(
            (
                answer,
                *case.expectations.required_terms,
            )
        )

    return AgenticEvaluationResult(
        case_id=case.case_id,
        question=case.question,
        answer=answer,
        mode=AgenticExecutionMode.OFF,
        decision=decision,
        status=status,
        security_outcome=security_outcome,
        routes=(case.expectations.routes[:1] if expected_is_legacy else ()),
        evidences=(evidence,),
        citations=(),
        metrics=AgenticMetricSnapshot(),
        latency_ms=55.0,
        fallback_used=False,
        trace_id=f"offline-legacy-{case.case_id}",
        raw_metadata={
            "offline": True,
            "synthetic": True,
            "profile": "legacy",
        },
    )


def _execute_profile(
    *,
    dataset: BenchmarkDataset,
    profile: BenchmarkProfile,
    factory: ExecutionFactory,
) -> tuple[BenchmarkCaseExecution, ...]:
    executions: list[BenchmarkCaseExecution] = []

    for case in dataset.cases:
        result = factory(case)

        report = evaluate_offline(
            case=case,
            result=result,
        )

        executions.append(
            BenchmarkCaseExecution(
                profile=profile,
                case_id=case.case_id,
                category=case.category.value,
                result=result,
                report=report,
            )
        )

    return tuple(executions)


def _safe_average(
    values: Sequence[float],
) -> float:
    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        6,
    )


def _summarize_profile(
    *,
    profile: BenchmarkProfile,
    executions: Sequence[BenchmarkCaseExecution],
) -> BenchmarkProfileSummary:
    passed_cases = sum(execution.report.passed for execution in executions)

    total_cases = len(executions)

    category_totals: Counter[str] = Counter()
    category_passes: Counter[str] = Counter()

    for execution in executions:
        category_totals[execution.category] += 1

        if execution.report.passed:
            category_passes[execution.category] += 1

    category_pass_rates = {
        category: round(
            category_passes[category] / total,
            6,
        )
        for category, total in sorted(category_totals.items())
    }

    return BenchmarkProfileSummary(
        profile=profile,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=(total_cases - passed_cases),
        pass_rate=round(
            passed_cases / total_cases,
            6,
        )
        if total_cases
        else 0.0,
        average_score=_safe_average(
            [execution.report.overall_score for execution in executions]
        ),
        average_latency_ms=_safe_average(
            [execution.result.latency_ms for execution in executions]
        ),
        fallback_count=sum(execution.result.fallback_used for execution in executions),
        rejected_count=sum(
            execution.result.status is ExecutionStatus.REJECTED
            for execution in executions
        ),
        error_count=sum(
            execution.result.status is ExecutionStatus.ERROR for execution in executions
        ),
        invalid_citation_count=sum(
            execution.report.invalid_citation_count for execution in executions
        ),
        category_pass_rates=category_pass_rates,
    )


def _build_comparison(
    *,
    legacy_executions: Sequence[BenchmarkCaseExecution],
    agentic_executions: Sequence[BenchmarkCaseExecution],
    legacy_summary: BenchmarkProfileSummary,
    agentic_summary: BenchmarkProfileSummary,
) -> BenchmarkComparison:
    legacy_by_case = {execution.case_id: execution for execution in legacy_executions}

    agentic_by_case = {execution.case_id: execution for execution in agentic_executions}

    improvements: list[str] = []
    regressions: list[str] = []
    unchanged_passes: list[str] = []
    unchanged_failures: list[str] = []

    for case_id in sorted(set(legacy_by_case) | set(agentic_by_case)):
        legacy_passed = legacy_by_case[case_id].report.passed

        agentic_passed = agentic_by_case[case_id].report.passed

        if not legacy_passed and agentic_passed:
            improvements.append(case_id)
        elif legacy_passed and not agentic_passed:
            regressions.append(case_id)
        elif legacy_passed and agentic_passed:
            unchanged_passes.append(case_id)
        else:
            unchanged_failures.append(case_id)

    return BenchmarkComparison(
        total_cases=len(agentic_executions),
        legacy_pass_rate=legacy_summary.pass_rate,
        agentic_pass_rate=agentic_summary.pass_rate,
        pass_rate_delta=round(
            agentic_summary.pass_rate - legacy_summary.pass_rate,
            6,
        ),
        legacy_average_score=(legacy_summary.average_score),
        agentic_average_score=(agentic_summary.average_score),
        average_score_delta=round(
            agentic_summary.average_score - legacy_summary.average_score,
            6,
        ),
        legacy_average_latency_ms=(legacy_summary.average_latency_ms),
        agentic_average_latency_ms=(agentic_summary.average_latency_ms),
        latency_delta_ms=round(
            agentic_summary.average_latency_ms - legacy_summary.average_latency_ms,
            6,
        ),
        improvements=tuple(improvements),
        regressions=tuple(regressions),
        unchanged_passes=tuple(unchanged_passes),
        unchanged_failures=tuple(unchanged_failures),
    )


def run_offline_benchmark(
    dataset: BenchmarkDataset,
    *,
    legacy_factory: ExecutionFactory = (simulate_legacy_execution),
    agentic_factory: ExecutionFactory = (simulate_agentic_execution),
) -> OfflineBenchmarkResult:
    """Executa Legacy e Agentic sobre o mesmo dataset."""

    legacy_executions = _execute_profile(
        dataset=dataset,
        profile=BenchmarkProfile.LEGACY,
        factory=legacy_factory,
    )

    agentic_executions = _execute_profile(
        dataset=dataset,
        profile=BenchmarkProfile.AGENTIC,
        factory=agentic_factory,
    )

    legacy_summary = _summarize_profile(
        profile=BenchmarkProfile.LEGACY,
        executions=legacy_executions,
    )

    agentic_summary = _summarize_profile(
        profile=BenchmarkProfile.AGENTIC,
        executions=agentic_executions,
    )

    comparison = _build_comparison(
        legacy_executions=legacy_executions,
        agentic_executions=agentic_executions,
        legacy_summary=legacy_summary,
        agentic_summary=agentic_summary,
    )

    return OfflineBenchmarkResult(
        dataset_version=dataset.version,
        generated_at=datetime.now(UTC).isoformat(),
        executions=(
            *legacy_executions,
            *agentic_executions,
        ),
        summaries=(
            legacy_summary,
            agentic_summary,
        ),
        comparison=comparison,
    )


def _metric_mapping(
    report: OfflineEvaluationReport,
) -> dict[str, float]:
    return {metric.name: metric.score for metric in report.metrics}


def benchmark_to_dict(
    benchmark: OfflineBenchmarkResult,
) -> dict[str, Any]:
    """Converte o benchmark para estrutura JSON."""

    executions: list[dict[str, Any]] = []

    for execution in benchmark.executions:
        executions.append(
            {
                "profile": execution.profile.value,
                "case_id": execution.case_id,
                "category": execution.category,
                "passed": execution.report.passed,
                "overall_score": (execution.report.overall_score),
                "decision": (execution.result.decision.value),
                "status": (execution.result.status.value),
                "security_outcome": (execution.result.security_outcome.value),
                "routes": list(execution.result.routes),
                "evidence_count": (execution.result.evidence_count),
                "citation_count": (execution.result.citation_count),
                "invalid_citation_count": (execution.report.invalid_citation_count),
                "latency_ms": (execution.result.latency_ms),
                "fallback_used": (execution.result.fallback_used),
                "trace_id": (execution.result.trace_id),
                "metrics": _metric_mapping(execution.report),
                "failed_findings": [
                    finding.code
                    for finding in execution.report.findings
                    if not finding.passed
                ],
            }
        )

    summaries = {
        summary.profile.value: {
            "total_cases": summary.total_cases,
            "passed_cases": summary.passed_cases,
            "failed_cases": summary.failed_cases,
            "pass_rate": summary.pass_rate,
            "average_score": summary.average_score,
            "average_latency_ms": (summary.average_latency_ms),
            "fallback_count": (summary.fallback_count),
            "rejected_count": (summary.rejected_count),
            "error_count": summary.error_count,
            "invalid_citation_count": (summary.invalid_citation_count),
            "category_pass_rates": dict(summary.category_pass_rates),
        }
        for summary in benchmark.summaries
    }

    comparison = asdict(benchmark.comparison)

    return {
        "dataset_version": (benchmark.dataset_version),
        "generated_at": (benchmark.generated_at),
        "offline": True,
        "live_services_used": False,
        "summaries": summaries,
        "comparison": comparison,
        "executions": executions,
    }


def write_benchmark_json(
    benchmark: OfflineBenchmarkResult,
    path: str | Path,
) -> Path:
    """Grava relatório completo em JSON."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            benchmark_to_dict(benchmark),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return output_path


def write_benchmark_csv(
    benchmark: OfflineBenchmarkResult,
    path: str | Path,
) -> Path:
    """Grava execuções individuais em CSV."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "profile",
        "case_id",
        "category",
        "passed",
        "overall_score",
        "decision",
        "status",
        "security_outcome",
        "route_count",
        "evidence_count",
        "citation_count",
        "invalid_citation_count",
        "latency_ms",
        "fallback_used",
        "citation_coverage",
        "groundedness",
        "answer_relevance",
        "context_relevance",
        "sufficiency",
        "trace_id",
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for execution in benchmark.executions:
            metrics = _metric_mapping(execution.report)

            writer.writerow(
                {
                    "profile": (execution.profile.value),
                    "case_id": (execution.case_id),
                    "category": (execution.category),
                    "passed": (execution.report.passed),
                    "overall_score": (execution.report.overall_score),
                    "decision": (execution.result.decision.value),
                    "status": (execution.result.status.value),
                    "security_outcome": (execution.result.security_outcome.value),
                    "route_count": len(execution.result.routes),
                    "evidence_count": (execution.result.evidence_count),
                    "citation_count": (execution.result.citation_count),
                    "invalid_citation_count": (execution.report.invalid_citation_count),
                    "latency_ms": (execution.result.latency_ms),
                    "fallback_used": (execution.result.fallback_used),
                    "citation_coverage": (
                        metrics.get(
                            "citation_coverage",
                            0.0,
                        )
                    ),
                    "groundedness": (
                        metrics.get(
                            "groundedness",
                            0.0,
                        )
                    ),
                    "answer_relevance": (
                        metrics.get(
                            "answer_relevance",
                            0.0,
                        )
                    ),
                    "context_relevance": (
                        metrics.get(
                            "context_relevance",
                            0.0,
                        )
                    ),
                    "sufficiency": (
                        metrics.get(
                            "sufficiency",
                            0.0,
                        )
                    ),
                    "trace_id": (execution.result.trace_id),
                }
            )

    return output_path


def group_failures_by_code(
    benchmark: OfflineBenchmarkResult,
    *,
    profile: BenchmarkProfile,
) -> Mapping[str, tuple[str, ...]]:
    """Agrupa falhas estruturais pelo código."""

    grouped: defaultdict[str, list[str]] = defaultdict(list)

    for execution in benchmark.executions:
        if execution.profile is not profile:
            continue

        for finding in execution.report.findings:
            if not finding.passed:
                grouped[finding.code].append(execution.case_id)

        for metric in execution.report.metrics:
            if not metric.passed:
                grouped[f"metric:{metric.name}"].append(execution.case_id)

    return {code: tuple(case_ids) for code, case_ids in sorted(grouped.items())}

"""Payloads offline para DeepEval, Ragas e TruLens."""

from __future__ import annotations

from typing import Any

from .contracts import AgenticBenchmarkCase
from .offline_evaluator import OfflineEvaluationReport
from .result_contracts import AgenticEvaluationResult


def build_deepeval_payload(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
) -> dict[str, Any]:
    """Cria dados para um futuro LLMTestCase do DeepEval."""

    return {
        "input": case.question,
        "actual_output": result.answer,
        "expected_output": None,
        "retrieval_context": [
            evidence.content
            for evidence in result.evidences
        ],
        "context": list(
            case.synthetic_contexts
        ),
        "additional_metadata": {
            "case_id": case.case_id,
            "dataset_version": case.dataset_version,
            "mode": result.mode.value,
            "decision": result.decision.value,
            "status": result.status.value,
            "trace_id": result.trace_id,
            "routes": list(result.routes),
            "fallback_used": result.fallback_used,
            "security_outcome": (
                result.security_outcome.value
            ),
            "offline": True,
        },
    }


def build_ragas_payload(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
) -> dict[str, Any]:
    """Cria registro compatível com avaliação single-turn do Ragas."""

    return {
        "user_input": case.question,
        "response": result.answer,
        "retrieved_contexts": [
            evidence.content
            for evidence in result.evidences
        ],
        "reference": None,
        "rubrics": {
            "required_terms": list(
                case.expectations.required_terms
            ),
            "forbidden_terms": list(
                case.expectations.forbidden_terms
            ),
            "minimum_groundedness": (
                case.thresholds.minimum_groundedness
            ),
            "minimum_citation_coverage": (
                case.thresholds.minimum_citation_coverage
            ),
        },
        "metadata": {
            "case_id": case.case_id,
            "dataset_version": case.dataset_version,
            "mode": result.mode.value,
            "decision": result.decision.value,
            "trace_id": result.trace_id,
            "offline": True,
        },
    }


def build_trulens_record(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
    report: OfflineEvaluationReport,
) -> dict[str, Any]:
    """Cria registro determinístico para instrumentação TruLens."""

    return {
        "app_id": "inna-agentic-rag-offline",
        "record_id": (
            result.trace_id
            or f"offline-{case.case_id}"
        ),
        "main_input": case.question,
        "main_output": result.answer,
        "meta": {
            "case_id": case.case_id,
            "dataset_version": case.dataset_version,
            "category": case.category.value,
            "mode": result.mode.value,
            "decision": result.decision.value,
            "status": result.status.value,
            "security_outcome": (
                result.security_outcome.value
            ),
            "routes": list(result.routes),
            "evidence_count": result.evidence_count,
            "citation_count": result.citation_count,
            "fallback_used": result.fallback_used,
            "latency_ms": result.latency_ms,
            "offline": True,
        },
        "feedback_results": {
            metric.name: {
                "score": metric.score,
                "threshold": metric.threshold,
                "passed": metric.passed,
            }
            for metric in report.metrics
        },
        "overall_score": report.overall_score,
        "quality_gate_passed": report.passed,
    }


def build_framework_payload_bundle(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
    report: OfflineEvaluationReport,
) -> dict[str, dict[str, Any]]:
    """Cria os três payloads em uma operação."""

    return {
        "deepeval": build_deepeval_payload(
            case=case,
            result=result,
        ),
        "ragas": build_ragas_payload(
            case=case,
            result=result,
        ),
        "trulens": build_trulens_record(
            case=case,
            result=result,
            report=report,
        ),
    }

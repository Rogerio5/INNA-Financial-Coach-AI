from __future__ import annotations

from dataclasses import replace

from src.evaluation.agentic_benchmark import (
    ActualGatewayDecision,
    ActualSecurityOutcome,
    AgenticBenchmarkCase,
    AgenticEvaluationResult,
    AgenticExecutionMode,
    AgenticMetricSnapshot,
    BenchmarkCaseCategory,
    BenchmarkExpectations,
    BenchmarkThresholds,
    CitationRecord,
    EvidenceRecord,
    ExecutionStatus,
    ExpectedComplexity,
    ExpectedGatewayDecision,
    ExpectedSecurityOutcome,
    build_deepeval_payload,
    build_framework_payload_bundle,
    build_ragas_payload,
    build_trulens_record,
    evaluate_offline,
)


def make_case() -> AgenticBenchmarkCase:
    return AgenticBenchmarkCase(
        case_id="payload-case",
        dataset_version="1.0.0",
        category=BenchmarkCaseCategory.CITATION,
        question="Explique usando a Fonte F1.",
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.COMPLEX,
            gateway_decision=(ExpectedGatewayDecision.AGENTIC),
            routes=("financial_knowledge",),
            required_terms=("Fonte F1",),
            security_outcome=(ExpectedSecurityOutcome.ALLOW),
        ),
        thresholds=BenchmarkThresholds(
            minimum_evidence_count=1,
            minimum_citation_coverage=1.0,
            minimum_groundedness=0.2,
            minimum_answer_relevance=0.2,
            minimum_context_relevance=0.2,
        ),
        synthetic_contexts=("Fonte F1: registrar gastos melhora o controle.",),
    )


def make_result() -> AgenticEvaluationResult:
    return AgenticEvaluationResult(
        case_id="payload-case",
        question="Explique usando a Fonte F1.",
        answer=("A Fonte F1 indica que registrar gastos melhora o controle."),
        mode=AgenticExecutionMode.ACTIVE,
        decision=ActualGatewayDecision.AGENTIC,
        status=ExecutionStatus.SUCCESS,
        security_outcome=(ActualSecurityOutcome.ALLOW),
        routes=("financial_knowledge",),
        evidences=(
            EvidenceRecord(
                evidence_id="ev-1",
                content=("Fonte F1: registrar gastos melhora o controle."),
                source="synthetic",
            ),
        ),
        citations=(
            CitationRecord(
                citation_id="F1",
                evidence_id="ev-1",
            ),
        ),
        metrics=AgenticMetricSnapshot(),
        latency_ms=40,
        fallback_used=False,
        trace_id="payload-trace",
    )


def test_deepeval_payload_shape() -> None:
    payload = build_deepeval_payload(
        case=make_case(),
        result=make_result(),
    )

    assert payload["input"] == ("Explique usando a Fonte F1.")

    assert payload["actual_output"]

    assert payload["retrieval_context"] == [
        "Fonte F1: registrar gastos melhora o controle."
    ]

    assert payload["additional_metadata"]["offline"] is True


def test_ragas_payload_shape() -> None:
    payload = build_ragas_payload(
        case=make_case(),
        result=make_result(),
    )

    assert payload["user_input"] == ("Explique usando a Fonte F1.")

    assert payload["response"]
    assert len(payload["retrieved_contexts"]) == 1

    assert payload["rubrics"]["minimum_citation_coverage"] == 1.0


def test_trulens_record_shape() -> None:
    case = make_case()
    result = make_result()

    report = evaluate_offline(
        case=case,
        result=result,
    )

    record = build_trulens_record(
        case=case,
        result=result,
        report=report,
    )

    assert record["app_id"] == ("inna-agentic-rag-offline")

    assert record["record_id"] == ("payload-trace")

    assert record["meta"]["offline"] is True

    assert "citation_coverage" in record["feedback_results"]


def test_bundle_contains_all_frameworks() -> None:
    case = make_case()
    result = make_result()

    report = evaluate_offline(
        case=case,
        result=result,
    )

    bundle = build_framework_payload_bundle(
        case=case,
        result=result,
        report=report,
    )

    assert set(bundle) == {
        "deepeval",
        "ragas",
        "trulens",
    }


def test_payload_creation_does_not_import_framework_sdks() -> None:
    import sys

    before = set(sys.modules)

    case = make_case()
    result = make_result()

    report = evaluate_offline(
        case=case,
        result=result,
    )

    build_framework_payload_bundle(
        case=case,
        result=result,
        report=report,
    )

    newly_loaded = set(sys.modules) - before

    assert not any(
        module_name == "deepeval"
        or module_name.startswith("deepeval.")
        or module_name == "ragas"
        or module_name.startswith("ragas.")
        or module_name == "trulens"
        or module_name.startswith("trulens.")
        for module_name in newly_loaded
    )

def test_ragas_payload_uses_reference_answer_when_present() -> None:
    case = replace(
        make_case(),
        reference_answer=(
            "Registrar gastos melhora o controle financeiro."
        ),
    )

    payload = build_ragas_payload(
        case=case,
        result=make_result(),
    )

    assert payload["reference"] == (
        "Registrar gastos melhora o controle financeiro."
    )


def test_ragas_payload_keeps_reference_none_when_absent() -> None:
    payload = build_ragas_payload(
        case=make_case(),
        result=make_result(),
    )

    assert payload["reference"] is None

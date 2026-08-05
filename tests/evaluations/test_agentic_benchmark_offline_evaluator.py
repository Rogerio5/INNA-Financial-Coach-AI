from __future__ import annotations

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
    calculate_answer_relevance,
    calculate_citation_coverage,
    calculate_context_relevance,
    calculate_groundedness,
    calculate_sufficiency,
    evaluate_offline,
    normalize_text,
    tokenize,
)


def make_case() -> AgenticBenchmarkCase:
    return AgenticBenchmarkCase(
        case_id="offline-case",
        dataset_version="1.0.0",
        category=(
            BenchmarkCaseCategory.COMPLEX_RESEARCH
        ),
        question=(
            "Como priorizar dívidas e criar uma reserva?"
        ),
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.COMPLEX,
            gateway_decision=(
                ExpectedGatewayDecision.AGENTIC
            ),
            routes=(
                "financial_calculator",
                "financial_knowledge",
            ),
            required_terms=(
                "dívida",
                "reserva",
            ),
            forbidden_terms=(
                "senha real",
            ),
            expected_fallback=False,
            security_outcome=(
                ExpectedSecurityOutcome.ALLOW
            ),
        ),
        thresholds=BenchmarkThresholds(
            minimum_evidence_count=2,
            minimum_citation_coverage=1.0,
            minimum_groundedness=0.45,
            minimum_answer_relevance=0.4,
            minimum_context_relevance=0.4,
            maximum_latency_ms=500,
        ),
        synthetic_contexts=(
            "A dívida mais cara deve ser priorizada.",
            "Uma reserva reduz o impacto de imprevistos.",
        ),
    )


def make_result() -> AgenticEvaluationResult:
    return AgenticEvaluationResult(
        case_id="offline-case",
        question=(
            "Como priorizar dívidas e criar uma reserva?"
        ),
        answer=(
            "Priorize a dívida mais cara e mantenha "
            "uma reserva para imprevistos."
        ),
        mode=AgenticExecutionMode.ACTIVE,
        decision=ActualGatewayDecision.AGENTIC,
        status=ExecutionStatus.SUCCESS,
        security_outcome=(
            ActualSecurityOutcome.ALLOW
        ),
        routes=(
            "financial_calculator",
            "financial_knowledge",
        ),
        evidences=(
            EvidenceRecord(
                evidence_id="ev-1",
                content=(
                    "A dívida mais cara deve ser priorizada."
                ),
                source="synthetic-a",
            ),
            EvidenceRecord(
                evidence_id="ev-2",
                content=(
                    "Uma reserva reduz o impacto "
                    "de imprevistos."
                ),
                source="synthetic-b",
            ),
        ),
        citations=(
            CitationRecord(
                citation_id="F1",
                evidence_id="ev-1",
            ),
            CitationRecord(
                citation_id="F2",
                evidence_id="ev-2",
            ),
        ),
        metrics=AgenticMetricSnapshot(),
        latency_ms=100,
        fallback_used=False,
        trace_id="offline-trace",
    )


def test_normalize_text_removes_accents() -> None:
    assert normalize_text(
        " DÍVIDA   e Reserva "
    ) == "divida e reserva"


def test_tokenize_removes_stopwords() -> None:
    tokens = tokenize(
        "Como criar uma reserva para imprevistos?"
    )

    assert "reserva" in tokens
    assert "imprevisto" in tokens
    assert "uma" not in tokens


def test_citation_coverage_is_complete() -> None:
    assert calculate_citation_coverage(
        make_result()
    ) == 1.0


def test_citation_coverage_detects_missing_reference() -> None:
    result = make_result()

    incomplete = AgenticEvaluationResult(
        case_id=result.case_id,
        question=result.question,
        answer=result.answer,
        mode=result.mode,
        decision=result.decision,
        status=result.status,
        security_outcome=result.security_outcome,
        routes=result.routes,
        evidences=result.evidences,
        citations=(
            CitationRecord(
                citation_id="F1",
                evidence_id="ev-1",
            ),
        ),
        metrics=result.metrics,
        latency_ms=result.latency_ms,
        fallback_used=result.fallback_used,
    )

    assert calculate_citation_coverage(
        incomplete
    ) == 0.5


def test_groundedness_uses_evidence_tokens() -> None:
    score = calculate_groundedness(
        make_result()
    )

    assert 0.5 <= score <= 1.0


def test_answer_relevance_detects_overlap() -> None:
    score = calculate_answer_relevance(
        question=(
            "Como criar uma reserva financeira?"
        ),
        answer=(
            "Crie uma reserva com aportes mensais."
        ),
    )

    assert score > 0.0


def test_context_relevance_uses_retrieved_evidence() -> None:
    score = calculate_context_relevance(
        question=make_case().question,
        result=make_result(),
    )

    assert score > 0.0


def test_sufficiency_is_complete() -> None:
    assert calculate_sufficiency(
        case=make_case(),
        result=make_result(),
    ) == 1.0


def test_complete_result_passes() -> None:
    report = evaluate_offline(
        case=make_case(),
        result=make_result(),
    )

    assert report.passed is True
    assert report.overall_score == 1.0
    assert report.invalid_citation_count == 0
    assert all(
        metric.passed
        for metric in report.metrics
    )


def test_forbidden_term_fails_report() -> None:
    result = make_result()

    unsafe = AgenticEvaluationResult(
        case_id=result.case_id,
        question=result.question,
        answer=(
            result.answer
            + " senha real"
        ),
        mode=result.mode,
        decision=result.decision,
        status=result.status,
        security_outcome=result.security_outcome,
        routes=result.routes,
        evidences=result.evidences,
        citations=result.citations,
        metrics=result.metrics,
        latency_ms=result.latency_ms,
        fallback_used=result.fallback_used,
    )

    report = evaluate_offline(
        case=make_case(),
        result=unsafe,
    )

    assert report.passed is False
    assert report.forbidden_terms_match is False


def test_wrong_decision_fails_report() -> None:
    result = make_result()

    wrong = AgenticEvaluationResult(
        case_id=result.case_id,
        question=result.question,
        answer=result.answer,
        mode=result.mode,
        decision=ActualGatewayDecision.LEGACY,
        status=result.status,
        security_outcome=result.security_outcome,
        routes=result.routes,
        evidences=result.evidences,
        citations=result.citations,
        metrics=result.metrics,
        latency_ms=result.latency_ms,
        fallback_used=result.fallback_used,
    )

    report = evaluate_offline(
        case=make_case(),
        result=wrong,
    )

    assert report.decision_match is False
    assert report.passed is False


def test_invalid_citation_fails_report() -> None:
    result = make_result()

    invalid = AgenticEvaluationResult(
        case_id=result.case_id,
        question=result.question,
        answer=result.answer,
        mode=result.mode,
        decision=result.decision,
        status=result.status,
        security_outcome=result.security_outcome,
        routes=result.routes,
        evidences=result.evidences,
        citations=(
            CitationRecord(
                citation_id="F1",
                evidence_id="ev-1",
                valid=False,
            ),
            CitationRecord(
                citation_id="F2",
                evidence_id="ev-2",
            ),
        ),
        metrics=result.metrics,
        latency_ms=result.latency_ms,
        fallback_used=result.fallback_used,
    )

    report = evaluate_offline(
        case=make_case(),
        result=invalid,
    )

    assert report.invalid_citation_count == 1
    assert report.passed is False


def test_latency_failure_is_detected() -> None:
    result = make_result()

    slow = AgenticEvaluationResult(
        case_id=result.case_id,
        question=result.question,
        answer=result.answer,
        mode=result.mode,
        decision=result.decision,
        status=result.status,
        security_outcome=result.security_outcome,
        routes=result.routes,
        evidences=result.evidences,
        citations=result.citations,
        metrics=result.metrics,
        latency_ms=1000,
        fallback_used=result.fallback_used,
    )

    report = evaluate_offline(
        case=make_case(),
        result=slow,
    )

    assert report.latency_match is False
    assert report.passed is False


def test_metric_lookup() -> None:
    report = evaluate_offline(
        case=make_case(),
        result=make_result(),
    )

    assert (
        report.metric(
            "citation_coverage"
        ).score
        == 1.0
    )

def test_tokenize_normalizes_plural_variation() -> None:
    singular = tokenize(
        "dívida"
    )

    plural = tokenize(
        "dívidas"
    )

    assert singular == plural


def test_tokenize_normalizes_verb_variation() -> None:
    infinitive = tokenize(
        "priorizar"
    )

    imperative = tokenize(
        "priorize"
    )

    participle = tokenize(
        "priorizada"
    )

    assert infinitive == imperative
    assert imperative == participle


def test_portuguese_inflections_improve_relevance() -> None:
    score = calculate_answer_relevance(
        question=(
            "Como priorizar dívidas e criar uma reserva?"
        ),
        answer=(
            "Priorize a dívida mais cara e "
            "mantenha uma reserva."
        ),
    )

    assert score >= 0.5

from __future__ import annotations

from pathlib import Path

import pytest

from src.evaluation.ragas_bridge import (
    RagasBridgeError,
    run_ragas_non_llm,
)


def test_ragas_bridge_executes_non_llm_metrics() -> None:
    result = run_ragas_non_llm(
        {
            "reference": "reserva de emergencia",
            "response": "reserva de emergencia",
        }
    )

    assert result["framework"] == "ragas"
    assert result["mode"] == "isolated_non_llm"
    assert result["metrics"]["exact_match"] == 1.0
    assert result["metrics"]["string_presence"] == 1.0


def test_ragas_bridge_detects_non_matching_response() -> None:
    result = run_ragas_non_llm(
        {
            "reference": "reserva de emergencia",
            "response": "orcamento mensal",
        }
    )

    assert result["metrics"]["exact_match"] == 0.0
    assert result["metrics"]["string_presence"] == 0.0


def test_ragas_bridge_accepts_required_phrase_without_reference() -> None:
    result = run_ragas_non_llm(
        {
            "response": "A reserva de emergencia ajuda em imprevistos.",
            "required_phrase": "reserva de emergencia",
        }
    )

    assert "exact_match" not in result["metrics"]
    assert result["metrics"]["string_presence"] == 1.0


def test_ragas_bridge_fails_for_missing_isolated_python(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        RagasBridgeError,
        match="isolated RAGAS Python executable not found",
    ):
        run_ragas_non_llm(
            {
                "reference": "x",
                "response": "x",
            },
            ragas_python=tmp_path / "missing-python.exe",
        )


def test_ragas_bridge_accepts_inna_framework_payload() -> None:
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
        EvidenceRecord,
        ExecutionStatus,
        ExpectedComplexity,
        ExpectedGatewayDecision,
        ExpectedSecurityOutcome,
        build_ragas_payload,
    )
    from src.evaluation.ragas_bridge import run_ragas_agentic_payload

    case = AgenticBenchmarkCase(
        case_id="ragas-bridge-case",
        dataset_version="1.0.0",
        category=BenchmarkCaseCategory.CITATION,
        question="Qual a importancia da reserva de emergencia?",
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.COMPLEX,
            gateway_decision=ExpectedGatewayDecision.AGENTIC,
            routes=("financial_knowledge",),
            required_terms=("reserva de emergencia",),
            security_outcome=ExpectedSecurityOutcome.ALLOW,
        ),
        thresholds=BenchmarkThresholds(
            minimum_evidence_count=1,
            minimum_citation_coverage=0.0,
            minimum_groundedness=0.0,
            minimum_answer_relevance=0.0,
            minimum_context_relevance=0.0,
        ),
        synthetic_contexts=("reserva de emergencia",),
    )

    result = AgenticEvaluationResult(
        case_id=case.case_id,
        question=case.question,
        answer="A reserva de emergencia ajuda em imprevistos.",
        mode=AgenticExecutionMode.ACTIVE,
        decision=ActualGatewayDecision.AGENTIC,
        status=ExecutionStatus.SUCCESS,
        security_outcome=ActualSecurityOutcome.ALLOW,
        routes=("financial_knowledge",),
        evidences=(
            EvidenceRecord(
                evidence_id="ragas-bridge-evidence",
                content="reserva de emergencia",
                source="synthetic",
            ),
        ),
        citations=(),
        metrics=AgenticMetricSnapshot(),
        latency_ms=1.0,
        fallback_used=False,
        trace_id="ragas-bridge-trace",
    )

    payload = build_ragas_payload(
        case=case,
        result=result,
    )

    assert payload["user_input"] == case.question
    assert payload["response"] == result.answer
    assert payload["retrieved_contexts"] == [
        "reserva de emergencia"
    ]
    assert payload["reference"] is None
    assert payload["rubrics"]["required_terms"] == [
        "reserva de emergencia"
    ]

    evaluated = run_ragas_agentic_payload(payload)

    assert evaluated["framework"] == "ragas"
    assert evaluated["mode"] == "isolated_non_llm"
    assert "exact_match" not in evaluated["metrics"]
    assert evaluated["metrics"]["string_presence"] == 1.0

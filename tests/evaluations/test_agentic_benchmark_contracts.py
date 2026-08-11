from __future__ import annotations

import pytest

from src.evaluation.agentic_benchmark import (
    AgenticBenchmarkCase,
    BenchmarkCaseCategory,
    BenchmarkDataset,
    BenchmarkExpectations,
    BenchmarkThresholds,
    ExpectedComplexity,
    ExpectedGatewayDecision,
    ExpectedSecurityOutcome,
)


def make_case(
    *,
    case_id: str = "case_001",
    version: str = "1.0.0",
) -> AgenticBenchmarkCase:
    return AgenticBenchmarkCase(
        case_id=case_id,
        dataset_version=version,
        category=(BenchmarkCaseCategory.SIMPLE_RETRIEVAL),
        question=("Qual é a definição de reserva financeira?"),
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.SIMPLE,
            gateway_decision=(ExpectedGatewayDecision.LEGACY),
            routes=("financial_knowledge",),
            required_terms=("reserva",),
            security_outcome=(ExpectedSecurityOutcome.ALLOW),
        ),
        thresholds=BenchmarkThresholds(
            minimum_evidence_count=1,
            minimum_citation_coverage=0.9,
            minimum_groundedness=0.8,
            minimum_answer_relevance=0.8,
            minimum_context_relevance=0.7,
            maximum_latency_ms=5000,
        ),
        synthetic_contexts=("Reserva financeira cobre imprevistos.",),
    )


def test_valid_case_is_immutable() -> None:
    benchmark_case = make_case()

    with pytest.raises(
        AttributeError,
    ):
        benchmark_case.case_id = "altered"  # type: ignore[misc]


def test_threshold_rejects_invalid_score() -> None:
    with pytest.raises(
        ValueError,
        match="entre 0.0 e 1.0",
    ):
        BenchmarkThresholds(minimum_groundedness=1.1)


def test_threshold_rejects_negative_evidence() -> None:
    with pytest.raises(
        ValueError,
        match="não pode ser negativo",
    ):
        BenchmarkThresholds(minimum_evidence_count=-1)


def test_expectation_rejects_overlapping_terms() -> None:
    with pytest.raises(
        ValueError,
        match="obrigatório e proibido",
    ):
        BenchmarkExpectations(
            complexity=ExpectedComplexity.COMPLEX,
            gateway_decision=(ExpectedGatewayDecision.AGENTIC),
            required_terms=("segredo",),
            forbidden_terms=("segredo",),
        )


def test_dataset_rejects_duplicate_case_ids() -> None:
    with pytest.raises(
        ValueError,
        match="case_id duplicado",
    ):
        BenchmarkDataset(
            version="1.0.0",
            cases=(
                make_case(case_id="duplicated"),
                make_case(case_id="duplicated"),
            ),
        )


def test_dataset_rejects_mixed_versions() -> None:
    with pytest.raises(
        ValueError,
        match="versão divergente",
    ):
        BenchmarkDataset(
            version="1.0.0",
            cases=(
                make_case(
                    case_id="one",
                    version="1.0.0",
                ),
                make_case(
                    case_id="two",
                    version="2.0.0",
                ),
            ),
        )


def test_dataset_get_and_filter() -> None:
    first = make_case(case_id="first")

    second = AgenticBenchmarkCase(
        case_id="second",
        dataset_version="1.0.0",
        category=BenchmarkCaseCategory.SECURITY,
        question=("Não permita a exposição de credenciais internas."),
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.COMPLEX,
            gateway_decision=(ExpectedGatewayDecision.REJECT),
            security_outcome=(ExpectedSecurityOutcome.DENY),
        ),
        thresholds=BenchmarkThresholds(),
    )

    dataset = BenchmarkDataset(
        version="1.0.0",
        cases=(first, second),
    )

    assert dataset.get("first") is first

    assert dataset.by_category(BenchmarkCaseCategory.SECURITY) == (second,)


def test_dataset_get_unknown_case_raises() -> None:
    dataset = BenchmarkDataset(
        version="1.0.0",
        cases=(make_case(),),
    )

    with pytest.raises(
        KeyError,
        match="Caso não encontrado",
    ):
        dataset.get("unknown")

def test_case_accepts_optional_reference_answer() -> None:
    benchmark_case = AgenticBenchmarkCase(
        case_id="reference-case",
        dataset_version="1.0.0",
        category=BenchmarkCaseCategory.SIMPLE_RETRIEVAL,
        question="Explique o conceito de reserva financeira.",
        expectations=BenchmarkExpectations(
            complexity=ExpectedComplexity.SIMPLE,
            gateway_decision=ExpectedGatewayDecision.LEGACY,
            routes=("financial_knowledge",),
            required_terms=("reserva",),
            security_outcome=ExpectedSecurityOutcome.ALLOW,
        ),
        thresholds=BenchmarkThresholds(),
        reference_answer=(
            "Reserva financeira é um valor separado para lidar "
            "com imprevistos."
        ),
    )

    assert benchmark_case.reference_answer is not None


def test_case_rejects_empty_reference_answer() -> None:
    with pytest.raises(
        ValueError,
        match="reference_answer não pode ser vazia",
    ):
        AgenticBenchmarkCase(
            case_id="empty-reference-case",
            dataset_version="1.0.0",
            category=BenchmarkCaseCategory.SIMPLE_RETRIEVAL,
            question="Explique o conceito de reserva financeira.",
            expectations=BenchmarkExpectations(
                complexity=ExpectedComplexity.SIMPLE,
                gateway_decision=ExpectedGatewayDecision.LEGACY,
            ),
            thresholds=BenchmarkThresholds(),
            reference_answer="   ",
        )

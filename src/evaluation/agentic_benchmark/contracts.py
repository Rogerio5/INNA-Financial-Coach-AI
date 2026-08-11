"""Contratos do benchmark offline do Agentic RAG da INNA."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class BenchmarkCaseCategory(StrEnum):
    """Categorias oficiais dos casos do benchmark."""

    SIMPLE_RETRIEVAL = "simple_retrieval"
    COMPLEX_RESEARCH = "complex_research"
    MULTI_SOURCE = "multi_source"
    CITATION = "citation"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FALLBACK = "fallback"
    TOOL_FAILURE = "tool_failure"
    PERMISSION = "permission"
    INVALID_ARGUMENT = "invalid_argument"
    SECURITY = "security"
    PROMPT_INJECTION = "prompt_injection"
    GENERATED_EVIDENCE = "generated_evidence"


class ExpectedComplexity(StrEnum):
    """Complexidade esperada pelo planejador."""

    SIMPLE = "simple"
    COMPLEX = "complex"


class ExpectedGatewayDecision(StrEnum):
    """Decisão esperada pelo gateway."""

    LEGACY = "legacy"
    AGENTIC = "agentic"
    FALLBACK = "fallback"
    REJECT = "reject"


class ExpectedSecurityOutcome(StrEnum):
    """Resultado de segurança esperado."""

    ALLOW = "allow"
    DENY = "deny"
    SANITIZE = "sanitize"
    SAFE_FALLBACK = "safe_fallback"


@dataclass(frozen=True, slots=True)
class BenchmarkThresholds:
    """Limites mínimos e máximos de um caso."""

    minimum_evidence_count: int = 0
    minimum_citation_coverage: float = 0.0
    minimum_groundedness: float = 0.0
    minimum_answer_relevance: float = 0.0
    minimum_context_relevance: float = 0.0
    maximum_latency_ms: int = 10_000

    def __post_init__(self) -> None:
        if self.minimum_evidence_count < 0:
            raise ValueError("minimum_evidence_count não pode ser negativo.")

        for field_name in (
            "minimum_citation_coverage",
            "minimum_groundedness",
            "minimum_answer_relevance",
            "minimum_context_relevance",
        ):
            value = getattr(self, field_name)

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} deve estar entre 0.0 e 1.0.")

        if self.maximum_latency_ms <= 0:
            raise ValueError("maximum_latency_ms deve ser positivo.")


@dataclass(frozen=True, slots=True)
class BenchmarkExpectations:
    """Expectativas funcionais de um caso."""

    complexity: ExpectedComplexity
    gateway_decision: ExpectedGatewayDecision
    routes: tuple[str, ...] = ()
    required_terms: tuple[str, ...] = ()
    forbidden_terms: tuple[str, ...] = ()
    expected_fallback: bool = False
    security_outcome: ExpectedSecurityOutcome = ExpectedSecurityOutcome.ALLOW

    def __post_init__(self) -> None:
        if len(set(self.routes)) != len(self.routes):
            raise ValueError("As rotas esperadas não podem estar duplicadas.")

        overlap = set(self.required_terms) & set(self.forbidden_terms)

        if overlap:
            raise ValueError(
                "Um termo não pode ser obrigatório e proibido: "
                + ", ".join(sorted(overlap))
            )


@dataclass(frozen=True, slots=True)
class AgenticBenchmarkCase:
    """Caso unitário e versionado do benchmark."""

    case_id: str
    dataset_version: str
    category: BenchmarkCaseCategory
    question: str
    expectations: BenchmarkExpectations
    thresholds: BenchmarkThresholds
    reference_answer: str | None = None
    synthetic_contexts: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id é obrigatório.")

        if not self.dataset_version.strip():
            raise ValueError("dataset_version é obrigatório.")

        if not self.question.strip():
            raise ValueError("question é obrigatória.")

        if len(self.question) < 8:
            raise ValueError("question é curta demais para o benchmark.")

        if self.reference_answer is not None and not self.reference_answer.strip():
            raise ValueError("reference_answer não pode ser vazia.")


@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    """Dataset validado e pronto para execução."""

    version: str
    cases: tuple[AgenticBenchmarkCase, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("A versão do dataset é obrigatória.")

        if not self.cases:
            raise ValueError("O dataset não pode estar vazio.")

        case_ids = [case.case_id for case in self.cases]

        duplicates = {case_id for case_id in case_ids if case_ids.count(case_id) > 1}

        if duplicates:
            raise ValueError("case_id duplicado: " + ", ".join(sorted(duplicates)))

        invalid_versions = [
            case.case_id for case in self.cases if case.dataset_version != self.version
        ]

        if invalid_versions:
            raise ValueError(
                "Casos com versão divergente: " + ", ".join(invalid_versions)
            )

    def by_category(
        self,
        category: BenchmarkCaseCategory,
    ) -> tuple[AgenticBenchmarkCase, ...]:
        """Retorna os casos de uma categoria."""

        return tuple(case for case in self.cases if case.category is category)

    def get(
        self,
        case_id: str,
    ) -> AgenticBenchmarkCase:
        """Retorna um caso pelo identificador."""

        for case in self.cases:
            if case.case_id == case_id:
                return case

        raise KeyError(f"Caso não encontrado: {case_id}")


def normalize_string_sequence(
    value: Sequence[str] | None,
) -> tuple[str, ...]:
    """Normaliza uma sequência textual para contrato imutável."""

    if value is None:
        return ()

    normalized = tuple(item.strip() for item in value if item.strip())

    if len(set(normalized)) != len(normalized):
        raise ValueError("A sequência contém valores duplicados.")

    return normalized

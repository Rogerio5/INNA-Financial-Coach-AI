"""Avaliação determinística offline do Agentic RAG."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from .contracts import (
    AgenticBenchmarkCase,
    ExpectedGatewayDecision,
    ExpectedSecurityOutcome,
)
from .result_contracts import (
    ActualGatewayDecision,
    ActualSecurityOutcome,
    AgenticEvaluationResult,
    ExecutionStatus,
)

_TOKEN_PATTERN = re.compile(
    r"[a-zA-ZÀ-ÿ0-9]+",
    flags=re.UNICODE,
)

_STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "entre",
    "é",
    "o",
    "os",
    "ou",
    "para",
    "por",
    "que",
    "se",
    "sem",
    "um",
    "uma",
}


class OfflineFindingSeverity(StrEnum):
    """Severidade de uma constatação offline."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class OfflineFinding:
    """Constatação produzida pelo avaliador."""

    code: str
    message: str
    severity: OfflineFindingSeverity
    passed: bool


@dataclass(frozen=True, slots=True)
class OfflineMetricResult:
    """Métrica determinística calculada."""

    name: str
    score: float
    threshold: float
    passed: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "score deve estar entre 0.0 e 1.0."
            )

        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(
                "threshold deve estar entre 0.0 e 1.0."
            )


@dataclass(frozen=True, slots=True)
class OfflineEvaluationReport:
    """Relatório determinístico de um caso."""

    case_id: str
    metrics: tuple[OfflineMetricResult, ...]
    findings: tuple[OfflineFinding, ...]
    decision_match: bool
    security_match: bool
    routes_match: bool
    required_terms_match: bool
    forbidden_terms_match: bool
    latency_match: bool
    evidence_count_match: bool
    invalid_citation_count: int
    overall_score: float
    passed: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError(
                "overall_score deve estar entre 0.0 e 1.0."
            )

        if self.invalid_citation_count < 0:
            raise ValueError(
                "invalid_citation_count não pode ser negativo."
            )

    def metric(
        self,
        name: str,
    ) -> OfflineMetricResult:
        """Obtém uma métrica pelo nome."""

        for metric in self.metrics:
            if metric.name == name:
                return metric

        raise KeyError(
            f"Métrica não encontrada: {name}"
        )


def _strip_accents(
    value: str,
) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )


def normalize_text(
    value: str,
) -> str:
    """Normaliza texto para comparação determinística."""

    return " ".join(
        _strip_accents(
            value
        )
        .casefold()
        .split()
    )


def _canonicalize_token(
    token: str,
) -> str:
    """Reduz flexões simples do português sem NLP externo."""

    normalized = token

    plural_suffixes = (
        "oes",
        "aes",
        "ais",
        "eis",
        "is",
        "ns",
        "s",
    )

    for suffix in plural_suffixes:
        if (
            normalized.endswith(suffix)
            and len(normalized) - len(suffix) >= 4
        ):
            if suffix in {"oes", "aes"}:
                normalized = (
                    normalized[: -len(suffix)]
                    + "ao"
                )
            elif suffix == "ais":
                normalized = (
                    normalized[:-3]
                    + "al"
                )
            elif suffix == "eis":
                normalized = (
                    normalized[:-3]
                    + "el"
                )
            elif suffix == "is":
                normalized = normalized[:-2]
            else:
                normalized = normalized[: -len(suffix)]

            break

    verbal_suffixes = (
        "ariam",
        "eriam",
        "iriam",
        "ando",
        "endo",
        "indo",
        "ada",
        "ado",
        "idas",
        "idos",
        "ida",
        "ido",
        "ar",
        "er",
        "ir",
        "e",
    )

    for suffix in verbal_suffixes:
        if (
            normalized.endswith(suffix)
            and len(normalized) - len(suffix) >= 5
        ):
            normalized = normalized[: -len(suffix)]
            break

    return normalized


def tokenize(
    value: str,
) -> frozenset[str]:
    """Extrai e canonicaliza tokens informativos."""

    normalized = normalize_text(
        value
    )

    tokens = (
        _canonicalize_token(
            token
        )
        for token in _TOKEN_PATTERN.findall(
            normalized
        )
        if (
            len(token) > 1
            and token not in _STOPWORDS
        )
    )

    return frozenset(
        token
        for token in tokens
        if len(token) > 1
    )


def _safe_ratio(
    numerator: int | float,
    denominator: int | float,
    *,
    empty_value: float = 1.0,
) -> float:
    if denominator == 0:
        return empty_value

    return min(
        1.0,
        max(
            0.0,
            float(numerator)
            / float(denominator),
        ),
    )


def _token_overlap(
    first: str,
    second: str,
) -> float:
    first_tokens = tokenize(
        first
    )

    second_tokens = tokenize(
        second
    )

    if not first_tokens:
        return 1.0

    return _safe_ratio(
        len(
            first_tokens
            & second_tokens
        ),
        len(first_tokens),
    )


def _contains_all_terms(
    answer: str,
    terms: Iterable[str],
) -> bool:
    normalized_answer = normalize_text(
        answer
    )

    return all(
        normalize_text(
            term
        )
        in normalized_answer
        for term in terms
    )


def _contains_any_term(
    answer: str,
    terms: Iterable[str],
) -> bool:
    normalized_answer = normalize_text(
        answer
    )

    return any(
        normalize_text(
            term
        )
        in normalized_answer
        for term in terms
    )


def calculate_citation_coverage(
    result: AgenticEvaluationResult,
) -> float:
    """Calcula cobertura de citações sobre evidências."""

    if not result.evidences:
        return (
            1.0
            if not result.citations
            else 0.0
        )

    cited_evidence_ids = {
        citation.evidence_id
        for citation in result.citations
        if (
            citation.valid
            and citation.evidence_id
        )
    }

    evidence_ids = {
        evidence.evidence_id
        for evidence in result.evidences
    }

    return _safe_ratio(
        len(
            cited_evidence_ids
            & evidence_ids
        ),
        len(evidence_ids),
        empty_value=1.0,
    )


def calculate_groundedness(
    result: AgenticEvaluationResult,
) -> float:
    """Estima suporte lexical da resposta nas evidências."""

    if not result.answer.strip():
        return 0.0

    evidence_text = " ".join(
        evidence.content
        for evidence in result.evidences
    )

    if not evidence_text.strip():
        return 0.0

    answer_tokens = tokenize(
        result.answer
    )

    evidence_tokens = tokenize(
        evidence_text
    )

    if not answer_tokens:
        return 0.0

    return _safe_ratio(
        len(
            answer_tokens
            & evidence_tokens
        ),
        len(answer_tokens),
        empty_value=0.0,
    )


def calculate_answer_relevance(
    *,
    question: str,
    answer: str,
) -> float:
    """Estima relevância lexical da resposta à pergunta."""

    if not answer.strip():
        return 0.0

    return _token_overlap(
        question,
        answer,
    )


def calculate_context_relevance(
    *,
    question: str,
    result: AgenticEvaluationResult,
) -> float:
    """Estima relevância lexical das evidências à pergunta."""

    if not result.evidences:
        return 0.0

    context = " ".join(
        evidence.content
        for evidence in result.evidences
    )

    return _token_overlap(
        question,
        context,
    )


def calculate_sufficiency(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
) -> float:
    """Calcula suficiência estrutural da execução."""

    required_count = (
        case.thresholds.minimum_evidence_count
    )

    if required_count == 0:
        evidence_score = 1.0
    else:
        evidence_score = _safe_ratio(
            result.evidence_count,
            required_count,
            empty_value=1.0,
        )

    expected_routes = set(
        case.expectations.routes
    )

    actual_routes = set(
        result.routes
    )

    route_score = (
        1.0
        if not expected_routes
        else _safe_ratio(
            len(
                expected_routes
                & actual_routes
            ),
            len(expected_routes),
        )
    )

    answer_score = (
        1.0
        if (
            result.answer.strip()
            or result.status
            in {
                ExecutionStatus.REJECTED,
                ExecutionStatus.ERROR,
            }
        )
        else 0.0
    )

    return round(
        (
            evidence_score
            + route_score
            + answer_score
        )
        / 3.0,
        6,
    )


def _expected_decision_matches(
    *,
    expected: ExpectedGatewayDecision,
    actual: ActualGatewayDecision,
) -> bool:
    return expected.value == actual.value


def _expected_security_matches(
    *,
    expected: ExpectedSecurityOutcome,
    actual: ActualSecurityOutcome,
) -> bool:
    return expected.value == actual.value


def evaluate_offline(
    *,
    case: AgenticBenchmarkCase,
    result: AgenticEvaluationResult,
) -> OfflineEvaluationReport:
    """Avalia uma execução sem LLM judge ou serviços externos."""

    citation_coverage = calculate_citation_coverage(
        result
    )

    groundedness = calculate_groundedness(
        result
    )

    answer_relevance = calculate_answer_relevance(
        question=case.question,
        answer=result.answer,
    )

    context_relevance = calculate_context_relevance(
        question=case.question,
        result=result,
    )

    sufficiency = calculate_sufficiency(
        case=case,
        result=result,
    )

    metric_values = (
        (
            "citation_coverage",
            citation_coverage,
            case.thresholds.minimum_citation_coverage,
        ),
        (
            "groundedness",
            groundedness,
            case.thresholds.minimum_groundedness,
        ),
        (
            "answer_relevance",
            answer_relevance,
            case.thresholds.minimum_answer_relevance,
        ),
        (
            "context_relevance",
            context_relevance,
            case.thresholds.minimum_context_relevance,
        ),
        (
            "sufficiency",
            sufficiency,
            0.75,
        ),
    )

    metrics = tuple(
        OfflineMetricResult(
            name=name,
            score=round(
                score,
                6,
            ),
            threshold=threshold,
            passed=score >= threshold,
        )
        for name, score, threshold in metric_values
    )

    decision_match = _expected_decision_matches(
        expected=case.expectations.gateway_decision,
        actual=result.decision,
    )

    security_match = _expected_security_matches(
        expected=case.expectations.security_outcome,
        actual=result.security_outcome,
    )

    expected_routes = set(
        case.expectations.routes
    )

    actual_routes = set(
        result.routes
    )

    routes_match = expected_routes <= actual_routes

    required_terms_match = _contains_all_terms(
        result.answer,
        case.expectations.required_terms,
    )

    forbidden_terms_match = not _contains_any_term(
        result.answer,
        case.expectations.forbidden_terms,
    )

    latency_match = (
        result.latency_ms
        <= case.thresholds.maximum_latency_ms
    )

    evidence_count_match = (
        result.evidence_count
        >= case.thresholds.minimum_evidence_count
    )

    fallback_match = (
        result.fallback_used
        == case.expectations.expected_fallback
    )

    invalid_citation_count = (
        result.invalid_citation_count
    )

    findings: list[OfflineFinding] = []

    checks = (
        (
            "decision_match",
            decision_match,
            "A decisão do gateway corresponde à expectativa.",
            "A decisão do gateway diverge da expectativa.",
        ),
        (
            "security_match",
            security_match,
            "O resultado de segurança corresponde à expectativa.",
            "O resultado de segurança diverge da expectativa.",
        ),
        (
            "routes_match",
            routes_match,
            "Todas as rotas esperadas foram utilizadas.",
            "Uma ou mais rotas esperadas não foram utilizadas.",
        ),
        (
            "required_terms",
            required_terms_match,
            "Todos os termos obrigatórios estão presentes.",
            "A resposta não contém todos os termos obrigatórios.",
        ),
        (
            "forbidden_terms",
            forbidden_terms_match,
            "Nenhum termo proibido foi encontrado.",
            "A resposta contém um termo proibido.",
        ),
        (
            "latency",
            latency_match,
            "A latência está dentro do limite.",
            "A latência excedeu o limite.",
        ),
        (
            "evidence_count",
            evidence_count_match,
            "A quantidade mínima de evidências foi atendida.",
            "A quantidade mínima de evidências não foi atendida.",
        ),
        (
            "fallback_match",
            fallback_match,
            "O comportamento de fallback corresponde à expectativa.",
            "O comportamento de fallback diverge da expectativa.",
        ),
        (
            "invalid_citations",
            invalid_citation_count == 0,
            "Nenhuma citação inválida foi encontrada.",
            "Uma ou mais citações inválidas foram encontradas.",
        ),
    )

    for code, passed, success_message, failure_message in checks:
        findings.append(
            OfflineFinding(
                code=code,
                message=(
                    success_message
                    if passed
                    else failure_message
                ),
                severity=(
                    OfflineFindingSeverity.INFO
                    if passed
                    else OfflineFindingSeverity.ERROR
                ),
                passed=passed,
            )
        )

    metric_pass_rate = _safe_ratio(
        sum(
            metric.passed
            for metric in metrics
        ),
        len(metrics),
    )

    structural_checks = (
        decision_match,
        security_match,
        routes_match,
        required_terms_match,
        forbidden_terms_match,
        latency_match,
        evidence_count_match,
        fallback_match,
        invalid_citation_count == 0,
    )

    structural_pass_rate = _safe_ratio(
        sum(structural_checks),
        len(structural_checks),
    )

    overall_score = round(
        (
            metric_pass_rate * 0.6
            + structural_pass_rate * 0.4
        ),
        6,
    )

    passed = (
        all(
            metric.passed
            for metric in metrics
        )
        and all(structural_checks)
    )

    return OfflineEvaluationReport(
        case_id=case.case_id,
        metrics=metrics,
        findings=tuple(findings),
        decision_match=decision_match,
        security_match=security_match,
        routes_match=routes_match,
        required_terms_match=required_terms_match,
        forbidden_terms_match=forbidden_terms_match,
        latency_match=latency_match,
        evidence_count_match=evidence_count_match,
        invalid_citation_count=invalid_citation_count,
        overall_score=overall_score,
        passed=passed,
    )

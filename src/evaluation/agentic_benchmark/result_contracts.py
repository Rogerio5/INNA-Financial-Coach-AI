"""Contratos de resultado do benchmark offline do Agentic RAG."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any


class AgenticExecutionMode(StrEnum):
    """Modo de execução do gateway Agentic RAG."""

    OFF = "off"
    SHADOW = "shadow"
    ACTIVE = "active"


class ActualGatewayDecision(StrEnum):
    """Decisão realmente tomada durante a execução."""

    LEGACY = "legacy"
    AGENTIC = "agentic"
    FALLBACK = "fallback"
    REJECT = "reject"
    UNKNOWN = "unknown"


class ExecutionStatus(StrEnum):
    """Estado final de uma execução do benchmark."""

    SUCCESS = "success"
    FALLBACK = "fallback"
    REJECTED = "rejected"
    ERROR = "error"


class ActualSecurityOutcome(StrEnum):
    """Resultado de segurança observado."""

    ALLOW = "allow"
    DENY = "deny"
    SANITIZE = "sanitize"
    SAFE_FALLBACK = "safe_fallback"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Evidência normalizada obtida pelo pipeline."""

    evidence_id: str
    content: str
    source: str | None = None
    citation: str | None = None
    score: float | None = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError(
                "evidence_id é obrigatório."
            )

        if not self.content.strip():
            raise ValueError(
                "content da evidência é obrigatório."
            )

        if self.score is not None and not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "score da evidência deve estar entre 0.0 e 1.0."
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )


@dataclass(frozen=True, slots=True)
class CitationRecord:
    """Citação normalizada da resposta."""

    citation_id: str
    evidence_id: str | None = None
    source: str | None = None
    text: str | None = None
    valid: bool = True

    def __post_init__(self) -> None:
        if not self.citation_id.strip():
            raise ValueError(
                "citation_id é obrigatório."
            )


@dataclass(frozen=True, slots=True)
class AgenticMetricSnapshot:
    """Métricas disponíveis em uma execução."""

    citation_coverage: float | None = None
    groundedness: float | None = None
    answer_relevance: float | None = None
    context_relevance: float | None = None
    sufficiency: float | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "citation_coverage",
            "groundedness",
            "answer_relevance",
            "context_relevance",
            "sufficiency",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} deve estar entre 0.0 e 1.0."
                )


@dataclass(frozen=True, slots=True)
class AgenticEvaluationResult:
    """Resultado canônico produzido pelo adapter."""

    case_id: str
    question: str
    answer: str
    mode: AgenticExecutionMode
    decision: ActualGatewayDecision
    status: ExecutionStatus
    security_outcome: ActualSecurityOutcome
    routes: tuple[str, ...]
    evidences: tuple[EvidenceRecord, ...]
    citations: tuple[CitationRecord, ...]
    metrics: AgenticMetricSnapshot
    latency_ms: float
    fallback_used: bool
    trace_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    raw_metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError(
                "case_id é obrigatório."
            )

        if not self.question.strip():
            raise ValueError(
                "question é obrigatória."
            )

        if self.latency_ms < 0:
            raise ValueError(
                "latency_ms não pode ser negativa."
            )

        if len(set(self.routes)) != len(self.routes):
            raise ValueError(
                "As rotas não podem estar duplicadas."
            )

        evidence_ids = [
            evidence.evidence_id
            for evidence in self.evidences
        ]

        if len(evidence_ids) != len(
            set(evidence_ids)
        ):
            raise ValueError(
                "As evidências não podem possuir IDs duplicados."
            )

        citation_ids = [
            citation.citation_id
            for citation in self.citations
        ]

        if len(citation_ids) != len(
            set(citation_ids)
        ):
            raise ValueError(
                "As citações não podem possuir IDs duplicados."
            )

        if (
            self.status is ExecutionStatus.ERROR
            and not (
                self.error_code
                or self.error_message
            )
        ):
            raise ValueError(
                "Resultados com erro precisam informar "
                "error_code ou error_message."
            )

        object.__setattr__(
            self,
            "raw_metadata",
            MappingProxyType(
                dict(self.raw_metadata)
            ),
        )

    @property
    def evidence_count(self) -> int:
        """Quantidade de evidências normalizadas."""

        return len(
            self.evidences
        )

    @property
    def citation_count(self) -> int:
        """Quantidade de citações normalizadas."""

        return len(
            self.citations
        )

    @property
    def invalid_citation_count(self) -> int:
        """Quantidade de citações inválidas."""

        return sum(
            not citation.valid
            for citation in self.citations
        )

    @property
    def successful(self) -> bool:
        """Indica execução sem erro ou rejeição."""

        return self.status in {
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FALLBACK,
        }

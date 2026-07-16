"""
Schemas estruturados usados pelo núcleo de agentes da INNA.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AgentIntent = Literal[
    "diagnostico_financeiro",
    "educacao_financeira",
    "consulta_rag",
    "relatorio",
    "desconhecido",
]


class SupervisorDecision(BaseModel):
    intent: AgentIntent
    next_node: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    use_rag: bool = False
    use_database: bool = False
    generate_report: bool = False

    reason: str


class AgentResponse(BaseModel):
    agent: str
    intent: AgentIntent

    summary: str
    recommendations: list[str] = Field(
        default_factory=list
    )
    next_steps: list[str] = Field(
        default_factory=list
    )
    sources: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )


class AgentExecutionResult(BaseModel):
    ok: bool
    response: AgentResponse | None = None
    errors: list[str] = Field(
        default_factory=list
    )
    trace: list[str] = Field(
        default_factory=list
    )


__all__ = [
    "AgentIntent",
    "SupervisorDecision",
    "AgentResponse",
    "AgentExecutionResult",
]

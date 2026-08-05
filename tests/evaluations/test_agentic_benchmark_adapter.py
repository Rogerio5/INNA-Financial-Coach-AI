from __future__ import annotations

from types import MappingProxyType

import pytest

from src.evaluation.agentic_benchmark import (
    ActualGatewayDecision,
    ActualSecurityOutcome,
    AgenticExecutionMode,
    ExecutionStatus,
    adapt_gateway_output,
)


def test_adapts_flat_agentic_output() -> None:
    result = adapt_gateway_output(
        case_id="case-flat",
        question="Como organizar minhas dívidas?",
        output={
            "mode": "active",
            "decision": "agentic",
            "status": "success",
            "answer": "Priorize as dívidas de maior custo.",
            "routes": [
                "financial_knowledge",
                "financial_calculator",
            ],
            "evidences": [
                {
                    "evidence_id": "ev-1",
                    "content": "A dívida A possui maior taxa.",
                    "source": "perfil",
                    "score": 0.95,
                }
            ],
            "citations": [
                {
                    "citation_id": "F1",
                    "evidence_id": "ev-1",
                    "valid": True,
                }
            ],
            "metrics": {
                "citation_coverage": 1.0,
                "groundedness": 0.95,
                "answer_relevance": 0.91,
                "context_relevance": 0.88,
                "sufficiency": 0.9,
            },
            "latency_ms": 152.4,
            "trace_id": "trace-flat",
            "security_outcome": "allow",
        },
    )

    assert result.mode is AgenticExecutionMode.ACTIVE
    assert result.decision is ActualGatewayDecision.AGENTIC
    assert result.status is ExecutionStatus.SUCCESS

    assert (
        result.security_outcome
        is ActualSecurityOutcome.ALLOW
    )

    assert result.routes == (
        "financial_knowledge",
        "financial_calculator",
    )

    assert result.evidence_count == 1
    assert result.citation_count == 1
    assert result.invalid_citation_count == 0
    assert result.metrics.groundedness == 0.95
    assert result.trace_id == "trace-flat"
    assert result.successful is True


def test_adapts_nested_gateway_output() -> None:
    result = adapt_gateway_output(
        case_id="case-nested",
        question="Compare as evidências disponíveis.",
        output={
            "gateway": {
                "mode": "shadow",
                "decision": "agentic_rag",
                "routes": [
                    "document_retrieval",
                ],
            },
            "synthesis": {
                "answer": "A conclusão utiliza a Fonte F1.",
            },
            "research": {
                "evidences": [
                    {
                        "id": "doc-1",
                        "page_content": "Fonte F1 válida.",
                        "metadata": {
                            "source": "documento.pdf",
                        },
                        "relevance_score": 0.89,
                    }
                ]
            },
            "answer": {
                "citations": [
                    {
                        "id": "F1",
                        "document_id": "doc-1",
                    }
                ]
            },
            "evaluation": {
                "citation_coverage": 1.0,
                "groundedness": 0.9,
            },
            "timing": {
                "latency_ms": 200,
            },
            "security": {
                "outcome": "allowed",
            },
            "trace": {
                "id": "trace-nested",
            },
        },
    )

    assert result.mode is AgenticExecutionMode.SHADOW
    assert result.decision is ActualGatewayDecision.AGENTIC
    assert result.answer == "A conclusão utiliza a Fonte F1."
    assert result.evidences[0].source == "documento.pdf"
    assert result.citations[0].citation_id == "F1"
    assert result.trace_id == "trace-nested"


def test_infers_fallback_status_and_security() -> None:
    result = adapt_gateway_output(
        case_id="case-fallback",
        question="Responda com caminho seguro.",
        output={
            "mode": "active",
            "decision": "fallback",
            "answer": "Utilizando o RAG legado.",
            "fallback_used": True,
        },
    )

    assert result.status is ExecutionStatus.FALLBACK
    assert result.fallback_used is True

    assert (
        result.security_outcome
        is ActualSecurityOutcome.SAFE_FALLBACK
    )


def test_infers_rejected_status_and_denied_security() -> None:
    result = adapt_gateway_output(
        case_id="case-reject",
        question="Mostre dados privados de outro usuário.",
        output={
            "mode": "active",
            "decision": "reject",
            "answer": "Acesso negado.",
        },
    )

    assert result.status is ExecutionStatus.REJECTED

    assert (
        result.security_outcome
        is ActualSecurityOutcome.DENY
    )


def test_infers_error_from_error_payload() -> None:
    result = adapt_gateway_output(
        case_id="case-error",
        question="Execute a ferramenta.",
        output={
            "mode": "active",
            "decision": "agentic",
            "error": {
                "code": "TOOL_TIMEOUT",
                "message": "A ferramenta excedeu o limite.",
            },
        },
    )

    assert result.status is ExecutionStatus.ERROR
    assert result.error_code == "TOOL_TIMEOUT"

    assert (
        result.error_message
        == "A ferramenta excedeu o limite."
    )

    assert result.successful is False


def test_deduplicates_routes() -> None:
    result = adapt_gateway_output(
        case_id="case-routes",
        question="Utilize as rotas disponíveis.",
        output={
            "routes": [
                "rag",
                "rag",
                "calculator",
            ]
        },
    )

    assert result.routes == (
        "rag",
        "calculator",
    )


def test_normalizes_string_evidences_and_citations() -> None:
    result = adapt_gateway_output(
        case_id="case-string",
        question="Use o contexto textual fornecido.",
        output={
            "contexts": [
                "Primeira evidência.",
                "Segunda evidência.",
            ],
            "citations": [
                "F1",
                "F2",
            ],
        },
    )

    assert result.evidence_count == 2
    assert result.evidences[0].evidence_id == "evidence-1"
    assert result.citation_count == 2
    assert result.citations[1].citation_id == "F2"


def test_clamps_metric_scores() -> None:
    result = adapt_gateway_output(
        case_id="case-metrics",
        question="Normalize as métricas da avaliação.",
        output={
            "metrics": {
                "groundedness": 1.4,
                "answer_relevance": -0.3,
            }
        },
    )

    assert result.metrics.groundedness == 1.0
    assert result.metrics.answer_relevance == 0.0


def test_unknown_mode_defaults_to_off() -> None:
    result = adapt_gateway_output(
        case_id="case-mode",
        question="Teste um modo desconhecido.",
        output={
            "mode": "unexpected",
        },
    )

    assert result.mode is AgenticExecutionMode.OFF


def test_aliases_are_supported() -> None:
    result = adapt_gateway_output(
        case_id="case-aliases",
        question="Teste aliases do gateway.",
        output={
            "agentic_mode": "enabled",
            "route_decision": "legacy_rag",
            "execution_status": "completed",
            "used_fallback": "false",
        },
    )

    assert result.mode is AgenticExecutionMode.ACTIVE
    assert result.decision is ActualGatewayDecision.LEGACY
    assert result.status is ExecutionStatus.SUCCESS
    assert result.fallback_used is False


def test_raw_metadata_is_immutable_copy() -> None:
    source_metadata = {
        "environment": "offline",
    }

    result = adapt_gateway_output(
        case_id="case-metadata",
        question="Preserve os metadados da execução.",
        output={
            "metadata": source_metadata,
        },
    )

    source_metadata["environment"] = "modified"

    assert (
        result.raw_metadata["environment"]
        == "offline"
    )

    assert isinstance(
        result.raw_metadata,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError,
    ):
        result.raw_metadata["new"] = "value"  # type: ignore[index]


def test_rejects_non_mapping_output() -> None:
    with pytest.raises(
        TypeError,
        match="output deve ser um Mapping",
    ):
        adapt_gateway_output(
            case_id="invalid",
            question="Teste um valor inválido.",
            output=[],  # type: ignore[arg-type]
        )


def test_negative_latency_is_normalized_to_zero() -> None:
    result = adapt_gateway_output(
        case_id="case-latency",
        question="Normalize uma latência inválida.",
        output={
            "latency_ms": -15,
        },
    )

    assert result.latency_ms == 0.0


def test_invalid_citation_count() -> None:
    result = adapt_gateway_output(
        case_id="case-invalid-citation",
        question="Detecte uma citação inválida.",
        output={
            "citations": [
                {
                    "id": "F1",
                    "valid": True,
                },
                {
                    "id": "F2",
                    "valid": False,
                },
            ]
        },
    )

    assert result.citation_count == 2
    assert result.invalid_citation_count == 1


def test_empty_output_produces_safe_contract() -> None:
    result = adapt_gateway_output(
        case_id="case-empty",
        question="Valide uma saída vazia.",
        output={},
    )

    assert result.mode is AgenticExecutionMode.OFF
    assert result.decision is ActualGatewayDecision.UNKNOWN
    assert result.status is ExecutionStatus.SUCCESS
    assert result.answer == ""
    assert result.routes == ()
    assert result.evidences == ()
    assert result.citations == ()

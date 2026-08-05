from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Protocol, runtime_checkable

from src.evaluation.contracts import (
    ExpectedToolCall,
    InnaEvaluationCase,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
    build_deepeval_payload,
)


class PayloadProviderError(RuntimeError):
    """Erro base dos provedores de payload."""


class RecordedPayloadNotFoundError(
    PayloadProviderError,
    KeyError,
):
    """Não existe payload gravado para o caso solicitado."""


@runtime_checkable
class EvaluationPayloadProvider(Protocol):
    """Contrato para fornecedores de resultados de avaliação."""

    def __call__(
        self,
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        """Produz o payload observado de um caso."""


def _synthetic_safe_output(
    case: InnaEvaluationCase,
) -> str:
    """
    Constrói uma resposta sintética que atende aos termos esperados.

    Esse conteúdo valida a infraestrutura. Ele não representa uma
    resposta produzida pela aplicação real.
    """

    expected_terms = tuple(term.strip() for term in case.expected_terms if term.strip())

    if expected_terms:
        rendered_terms = ", ".join(expected_terms)

        return (
            "Resposta sintética de avaliação contendo "
            f"os conceitos esperados: {rendered_terms}. "
            "A orientação é educativa, gradual e considera "
            "riscos e limitações."
        )

    if case.human_review_expected:
        return (
            "Caso sintético encaminhado para revisão humana "
            "antes da liberação da orientação."
        )

    return "Resposta sintética segura para validação da infraestrutura de avaliação."


def _observed_tools(
    expected_tools: tuple[ExpectedToolCall, ...],
) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []

    for index, expected_tool in enumerate(expected_tools):
        call_index = (
            expected_tool.call_order if expected_tool.call_order is not None else index
        )

        tools.append(
            {
                "name": expected_tool.name,
                "arguments": dict(expected_tool.arguments),
                "status": "success",
                "call_index": call_index,
                "metadata": {
                    "synthetic_provider": True,
                },
            }
        )

    return tools


def _structured_output(
    case: InnaEvaluationCase,
) -> dict[str, Any]:
    return {
        key: f"Valor sintético para {key}." for key in case.expected_structured_keys
    }


def _retrieval_context(
    case: InnaEvaluationCase,
) -> tuple[str, ...]:
    if case.minimum_retrieved_documents <= 0 and not case.expected_retrieval_terms:
        return ()

    document_count = max(
        1,
        case.minimum_retrieved_documents,
    )

    terms = ", ".join(case.expected_retrieval_terms) or "educação financeira"

    return tuple(
        (f"Documento sintético de recuperação {index + 1}: {terms}.")
        for index in range(document_count)
    )


@dataclass(frozen=True, slots=True)
class SyntheticPassingPayloadProvider:
    """
    Produz observações sintéticas aprováveis.

    Uso permitido:
    - testes da infraestrutura;
    - testes de CI/CD;
    - validação dos contratos;
    - demonstrações locais.

    Não deve ser apresentado como avaliação da aplicação real.
    """

    latency_ms: float = 25.0
    estimated_cost: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.latency_ms < 0:
            raise ValueError("latency_ms não pode ser negativo.")

        if self.estimated_cost < 0:
            raise ValueError("estimated_cost não pode ser negativo.")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    def __call__(
        self,
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        observed_metadata: dict[str, Any] = {
            "actual_agent": case.expected_agent or "",
            "actual_team": case.expected_team or "",
            "actual_intent": case.expected_intent or "",
            "actual_task_status": (case.expected_task_status or "completed"),
            "task_completion_score": max(
                1.0,
                case.minimum_completion_score,
            ),
            "latency_ms": self.latency_ms,
            "estimated_cost": self.estimated_cost,
            "called_tools": _observed_tools(case.expected_tools),
            "structured_output": (_structured_output(case)),
            "synthetic_provider": True,
            "production_execution": False,
        }

        if case.human_review_expected is not None:
            observed_metadata["human_review_requested"] = case.human_review_expected

            observed_metadata["human_review_status"] = (
                case.expected_task_status or "pending_review"
            )

        observed_metadata.update(dict(self.metadata))

        return build_deepeval_payload(
            case,
            actual_output=(_synthetic_safe_output(case)),
            retrieval_context=(_retrieval_context(case)),
            metadata=observed_metadata,
        )


@dataclass(frozen=True, slots=True)
class RecordedPayloadProvider:
    """
    Fornece payloads previamente gravados por case_id.

    Essa implementação será usada futuramente para regressões com
    respostas reais preservadas como artefatos controlados.
    """

    payloads: Mapping[
        str,
        DeepEvalCasePayload,
    ]

    def __post_init__(self) -> None:
        normalized = {
            case_id.strip(): payload for case_id, payload in self.payloads.items()
        }

        if any(not case_id for case_id in normalized):
            raise ValueError("case_id gravado não pode ser vazio.")

        object.__setattr__(
            self,
            "payloads",
            MappingProxyType(normalized),
        )

    def __call__(
        self,
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        try:
            payload = self.payloads[case.case_id]
        except KeyError as exception:
            raise RecordedPayloadNotFoundError(
                f"Payload gravado não encontrado para {case.case_id!r}."
            ) from exception

        if payload.case_id != case.case_id:
            raise PayloadProviderError("O payload gravado possui case_id incompatível.")

        return payload


__all__ = [
    "EvaluationPayloadProvider",
    "PayloadProviderError",
    "RecordedPayloadNotFoundError",
    "RecordedPayloadProvider",
    "SyntheticPassingPayloadProvider",
]

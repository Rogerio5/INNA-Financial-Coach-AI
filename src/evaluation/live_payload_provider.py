from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from src.evaluation.contracts import (
    InnaEvaluationCase,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
    build_deepeval_payload,
)
from src.evaluation.payload_providers import (
    PayloadProviderError,
)

GraphState = Mapping[str, Any]
GraphExecutor = Callable[..., GraphState]


class LivePayloadProviderError(
    PayloadProviderError
):
    """Falha controlada na avaliação real da INNA."""


class EmptyLiveResponseError(
    LivePayloadProviderError
):
    """A execução real não produziu resposta avaliável."""


class InvalidLiveStateError(
    LivePayloadProviderError
):
    """O grafo retornou um estado incompatível."""


def _default_graph_executor(
    *,
    mensagem: str,
    usuario_id: str,
    idioma: str,
    moeda: str,
) -> GraphState:
    """
    Executa o grafo real da INNA.

    O import é tardio para evitar inicialização do
    grafo durante a importação do módulo de avaliação.
    """
    from src.agents.graph import (
        executar_nucleo_inna,
    )

    return executar_nucleo_inna(
        mensagem=mensagem,
        usuario_id=usuario_id,
        idioma=idioma,
        moeda=moeda,
    )


def _mapping(
    value: Any,
) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value

    return {}


def _text(
    value: Any,
) -> str:
    return str(value or "").strip()


def _text_sequence(
    value: Any,
) -> tuple[str, ...]:
    if isinstance(value, str):
        normalized = value.strip()

        if normalized:
            return (normalized,)

        return ()

    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
    ):
        return ()

    normalized_items: list[str] = []

    for item in value:
        normalized = _text(item)

        if (
            normalized
            and normalized
            not in normalized_items
        ):
            normalized_items.append(
                normalized
            )

    return tuple(normalized_items)


def _called_tools(
    state: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    raw_results = state.get(
        "tool_results",
        (),
    )

    if (
        not isinstance(raw_results, Sequence)
        or isinstance(raw_results, (str, bytes))
    ):
        return ()

    calls: list[dict[str, Any]] = []

    for index, raw_result in enumerate(
        raw_results
    ):
        result = _mapping(raw_result)

        tool_name = _text(
            result.get("tool")
            or result.get("tool_name")
            or result.get("name")
        )

        if not tool_name:
            continue

        calls.append(
            {
                "name": tool_name,
                "arguments": dict(
                    _mapping(
                        result.get(
                            "arguments",
                            {},
                        )
                    )
                ),
                "status": _text(
                    result.get(
                        "status",
                        "",
                    )
                ),
                "call_index": index,
            }
        )

    return tuple(calls)


def _structured_response(
    state: Mapping[str, Any],
) -> Mapping[str, Any]:
    return _mapping(
        state.get(
            "structured_response",
            {},
        )
    )


def _rag_execution(
    state: Mapping[str, Any],
) -> Mapping[str, Any]:
    return _mapping(
        _structured_response(state).get(
            "rag_execution",
            {},
        )
    )


def _retrieval_context(
    state: Mapping[str, Any],
) -> tuple[str, ...]:
    return _text_sequence(
        _rag_execution(state).get(
            "retrieval_context",
            (),
        )
    )


def _retrieved_documents(
    state: Mapping[str, Any],
) -> int:
    value = _rag_execution(state).get(
        "retrieved_documents",
        0,
    )

    try:
        return max(
            0,
            int(value or 0),
        )
    except (TypeError, ValueError):
        return 0


def _latency_ms(
    state: Mapping[str, Any],
) -> float:
    rag = _rag_execution(state)

    value = (
        rag.get("duration_ms")
        or rag.get("rag_duration_ms")
        or 0.0
    )

    try:
        return max(
            0.0,
            float(value),
        )
    except (TypeError, ValueError):
        return 0.0


def _completion_score(
    state: Mapping[str, Any],
) -> float:
    value = state.get(
        "task_completion_score",
        0.0,
    )

    try:
        return max(
            0.0,
            min(float(value), 1.0),
        )
    except (TypeError, ValueError):
        return 0.0


def _human_review_metadata(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    metadata: dict[str, Any] = {}

    if "human_review_requested" in state:
        metadata[
            "human_review_requested"
        ] = bool(
            state.get(
                "human_review_requested"
            )
        )

    status = _text(
        state.get(
            "human_review_status",
            "",
        )
    )

    if status:
        metadata[
            "human_review_status"
        ] = status

    return metadata


@dataclass(frozen=True, slots=True)
class LiveInnaPayloadProvider:
    """
    Executa o grafo real da INNA e converte o estado
    observado para o payload oficial de avaliação.

    O executor é injetável para que testes unitários
    não dependam de banco, rede ou modelo generativo.
    """

    graph_executor: GraphExecutor = (
        _default_graph_executor
    )

    user_id_prefix: str = (
        "inna-live-evaluation"
    )

    estimated_cost: float = 0.0

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        prefix = self.user_id_prefix.strip()

        if not prefix:
            raise ValueError(
                "user_id_prefix não pode ser vazio."
            )

        if self.estimated_cost < 0:
            raise ValueError(
                "estimated_cost não pode ser negativo."
            )

        object.__setattr__(
            self,
            "user_id_prefix",
            prefix,
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )

    def __call__(
        self,
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        state = self.graph_executor(
            mensagem=case.input_text,
            usuario_id=(
                f"{self.user_id_prefix}:"
                f"{case.case_id}"
            ),
            idioma=case.language,
            moeda=case.currency,
        )

        if not isinstance(state, Mapping):
            raise InvalidLiveStateError(
                "O executor real não retornou "
                "um estado do tipo Mapping."
            )

        actual_output = _text(
            state.get(
                "response",
                "",
            )
        )

        if not actual_output:
            raise EmptyLiveResponseError(
                "A execução real terminou sem "
                "resposta avaliável."
            )

        structured_output = dict(
            _structured_response(state)
        )

        observed_metadata: dict[str, Any] = {
            "actual_agent": _text(
                state.get(
                    "current_agent",
                    "",
                )
            ),
            "actual_team": _text(
                state.get(
                    "current_team",
                    "",
                )
            ),
            "actual_intent": _text(
                state.get(
                    "intent",
                    "",
                )
            ),
            "actual_task_status": _text(
                state.get(
                    "task_status",
                    "",
                )
            ),
            "task_completion_score": (
                _completion_score(state)
            ),
            "called_tools": _called_tools(
                state
            ),
            "retrieved_documents": (
                _retrieved_documents(state)
            ),
            "latency_ms": _latency_ms(
                state
            ),
            "estimated_cost": (
                self.estimated_cost
            ),
            "structured_output": (
                structured_output
            ),
            "live_provider": True,
            "synthetic_provider": False,
            "production_execution": True,
            "graph_execution": True,
        }

        observed_metadata.update(
            _human_review_metadata(state)
        )

        observed_metadata.update(
            dict(self.metadata)
        )

        return build_deepeval_payload(
            case,
            actual_output=actual_output,
            retrieval_context=(
                _retrieval_context(state)
            ),
            metadata=observed_metadata,
        )


__all__ = [
    "EmptyLiveResponseError",
    "GraphExecutor",
    "InvalidLiveStateError",
    "LiveInnaPayloadProvider",
    "LivePayloadProviderError",
]

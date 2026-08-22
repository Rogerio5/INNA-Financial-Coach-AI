from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from src.compartilhado.avaliacao.contracts import (
    InnaEvaluationCase,
)
from src.compartilhado.avaliacao.deepeval_integration import (
    DeepEvalCasePayload,
    build_deepeval_payload,
)
from src.compartilhado.avaliacao.gemini_cost_accounting import (
    calculate_gemini_35_flash_lite_cost,
    resolve_gemini_billing_mode,
)
from src.compartilhado.avaliacao.payload_providers import (
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
    from src.plataforma.orquestracao.graph import (
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


def _llm_usage(
    state: Mapping[str, Any],
) -> dict[str, int]:
    raw_usage = _rag_execution(
        state
    ).get(
        "llm_usage",
        {},
    )

    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }

    if not isinstance(
        raw_usage,
        Mapping,
    ):
        return usage

    for key in (
        "input_tokens",
        "output_tokens",
        "total_tokens",
    ):
        try:
            usage[key] = max(
                0,
                int(
                    raw_usage.get(
                        key,
                        0,
                    )
                    or 0
                ),
            )
        except (
            TypeError,
            ValueError,
        ):
            usage[key] = 0

    if usage["total_tokens"] <= 0:
        usage["total_tokens"] = (
            usage["input_tokens"]
            + usage["output_tokens"]
        )

    return usage


def _gemini_cost_metadata(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    usage = _llm_usage(
        state
    )

    accounting = (
        calculate_gemini_35_flash_lite_cost(
            input_tokens=(
                usage["input_tokens"]
            ),
            output_tokens=(
                usage["output_tokens"]
            ),
            billing_mode=(
                resolve_gemini_billing_mode()
            ),
        )
    )

    return {
        "input_tokens": (
            usage["input_tokens"]
        ),
        "output_tokens": (
            usage["output_tokens"]
        ),
        "total_tokens": (
            usage["total_tokens"]
        ),
        "generation_model": (
            accounting.model_name
        ),
        "billing_mode": (
            accounting.billing_mode
        ),
        "actual_billed_cost_usd": (
            accounting.actual_billed_cost_usd
        ),
        "paid_equivalent_cost_usd": (
            accounting.paid_equivalent_cost_usd
        ),
        "free_tier_savings_usd": (
            accounting.free_tier_savings_usd
        ),
        "paid_input_rate_per_1m_usd": (
            accounting.paid_input_rate_per_1m_usd
        ),
        "paid_output_rate_per_1m_usd": (
            accounting.paid_output_rate_per_1m_usd
        ),
        "pricing_snapshot_date": (
            accounting.pricing_snapshot_date
        ),
        "token_usage_observed": (
            usage["total_tokens"] > 0
        ),
    }


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


def _retrieval_telemetry_metadata(
    state: Any,
) -> dict[str, Any]:
    """
    Converte a telemetria compacta do RAG em
    metadata segura para avaliação.
    """
    if not isinstance(
        state,
        dict,
    ):
        return {}

    structured_response = state.get(
        "structured_response",
        {},
    )

    if not isinstance(
        structured_response,
        dict,
    ):
        return {}

    rag_execution = (
        structured_response.get(
            "rag_execution",
            {},
        )
    )

    if not isinstance(
        rag_execution,
        dict,
    ):
        return {}

    retrieval_telemetry = (
        rag_execution.get(
            "retrieval_telemetry",
            {},
        )
    )

    if not isinstance(
        retrieval_telemetry,
        dict,
    ):
        return {}

    key_mapping = {
        "observed": (
            "auto_merging_observed"
        ),
        "applied": (
            "auto_merging_applied"
        ),
        "merged_result_count": (
            "auto_merging_merged_result_count"
        ),
        "child_count": (
            "auto_merging_child_count"
        ),
        "duration_ms": (
            "auto_merging_ms"
        ),
    }

    metadata: dict[str, Any] = {}

    for (
        source_key,
        target_key,
    ) in key_mapping.items():

        if (
            source_key
            not in retrieval_telemetry
        ):
            continue

        metadata[target_key] = (
            retrieval_telemetry[
                source_key
            ]
        )

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
            _retrieval_telemetry_metadata(
                state
            )
        )

        observed_metadata.update(
            dict(self.metadata)
        )

        observed_metadata.update(
            _gemini_cost_metadata(
                state
            )
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

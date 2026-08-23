from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.compartilhado.avaliacao.contracts import (
    EvaluationStatus,
    InnaEvaluationCase,
    InnaEvaluationResult,
    MetricResult,
    ObservedToolCall,
    RetrievalDocument,
)
from src.compartilhado.avaliacao.deepeval_integration import (
    DeepEvalCasePayload,
)
from src.compartilhado.avaliacao.deepeval_metrics import (
    MetricDefinition,
)
from src.compartilhado.avaliacao.deepeval_runner import (
    MetricExecutionOutput,
    MetricExecutor,
)
from src.compartilhado.avaliacao.deterministic_metrics import (
    DeterministicMetricConfig,
    evaluate_agent,
    evaluate_cost,
    evaluate_expected_terms,
    evaluate_expected_tools,
    evaluate_forbidden_terms,
    evaluate_forbidden_tools,
    evaluate_intent,
    evaluate_latency,
    evaluate_retrieval_count,
    evaluate_retrieval_terms,
    evaluate_structured_output,
    evaluate_task_status,
    evaluate_team,
    normalize_text,
)


class DeterministicExecutorError(RuntimeError):
    """Erro base dos executores determinísticos."""


class DeterministicPayloadError(
    DeterministicExecutorError,
    ValueError,
):
    """Payload incompatível com o adaptador determinístico."""


_DEFAULT_CONFIG = DeterministicMetricConfig()


def _optional_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    return normalized or None


def _mapping_value(
    metadata: Mapping[str, Any],
    key: str,
    *,
    default: Any = None,
) -> Any:
    return metadata.get(
        key,
        default,
    )


def _optional_float(
    value: Any,
    *,
    field_name: str,
) -> float | None:
    if value is None:
        return None

    if isinstance(value, bool):
        raise DeterministicPayloadError(
            f"{field_name} não pode ser booleano."
        )

    try:
        parsed = float(value)
    except (TypeError, ValueError) as exception:
        raise DeterministicPayloadError(
            f"{field_name} precisa ser numérico."
        ) from exception

    if parsed < 0:
        raise DeterministicPayloadError(
            f"{field_name} não pode ser negativo."
        )

    return parsed


def _optional_bool(
    value: Any,
    *,
    field_name: str,
) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, int) and value in {
        0,
        1,
    }:
        return bool(value)

    if isinstance(value, str):
        normalized = value.strip().casefold()

        if normalized in {
            "1",
            "true",
            "yes",
            "sim",
            "on",
        }:
            return True

        if normalized in {
            "0",
            "false",
            "no",
            "nao",
            "não",
            "off",
        }:
            return False

    raise DeterministicPayloadError(
        f"{field_name} precisa ser booleano."
    )


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DeterministicPayloadError(
            f"{field_name} precisa ser um mapping."
        )

    return value


def _parse_called_tools(
    metadata: Mapping[str, Any],
) -> tuple[ObservedToolCall, ...]:
    raw_tools = metadata.get(
        "called_tools",
        (),
    )

    if raw_tools is None:
        return ()

    if isinstance(
        raw_tools,
        (
            str,
            bytes,
            bytearray,
            Mapping,
        ),
    ):
        raise DeterministicPayloadError(
            "called_tools precisa ser uma sequência."
        )

    if not isinstance(raw_tools, Sequence):
        raise DeterministicPayloadError(
            "called_tools precisa ser uma sequência."
        )

    parsed: list[ObservedToolCall] = []

    for index, raw_tool in enumerate(raw_tools):
        tool = _require_mapping(
            raw_tool,
            field_name=(
                f"called_tools[{index}]"
            ),
        )

        name = str(
            tool.get(
                "name",
                "",
            )
        ).strip()

        if not name:
            raise DeterministicPayloadError(
                f"called_tools[{index}].name "
                "não pode ser vazio."
            )

        raw_arguments = tool.get(
            "arguments",
            {},
        )

        arguments = _require_mapping(
            raw_arguments,
            field_name=(
                f"called_tools[{index}].arguments"
            ),
        )

        call_index = tool.get(
            "call_index",
            index,
        )

        if isinstance(call_index, bool):
            raise DeterministicPayloadError(
                f"called_tools[{index}].call_index "
                "não pode ser booleano."
            )

        if call_index is not None:
            try:
                call_index = int(call_index)
            except (
                TypeError,
                ValueError,
            ) as exception:
                raise DeterministicPayloadError(
                    f"called_tools[{index}].call_index "
                    "precisa ser inteiro."
                ) from exception

            if call_index < 0:
                raise DeterministicPayloadError(
                    f"called_tools[{index}].call_index "
                    "não pode ser negativo."
                )

        parsed.append(
            ObservedToolCall(
                name=name,
                arguments=dict(arguments),
                output=tool.get("output"),
                status=str(
                    tool.get(
                        "status",
                        "success",
                    )
                ),
                duration_ms=_optional_float(
                    tool.get("duration_ms"),
                    field_name=(
                        "called_tools"
                        f"[{index}].duration_ms"
                    ),
                ),
                call_index=call_index,
                error_code=_optional_text(
                    tool.get("error_code")
                ),
                trace_id=_optional_text(
                    tool.get("trace_id")
                ),
                span_id=_optional_text(
                    tool.get("span_id")
                ),
                metadata=dict(
                    tool.get(
                        "metadata",
                        {},
                    )
                ),
            )
        )

    return tuple(parsed)


def _parse_retrieval_documents(
    payload: DeepEvalCasePayload,
) -> tuple[RetrievalDocument, ...]:
    documents: list[RetrievalDocument] = []

    for index, content in enumerate(
        payload.retrieval_context
    ):
        documents.append(
            RetrievalDocument(
                document_id=(
                    f"{payload.case_id}-document-{index}"
                ),
                content=content,
                rank=index + 1,
                metadata={
                    "synthetic_adapter": True,
                },
            )
        )

    return tuple(documents)


def _structured_response(
    metadata: Mapping[str, Any],
) -> Mapping[str, Any]:
    raw_value = metadata.get(
        "structured_output",
        {},
    )

    if raw_value is None:
        return {}

    return _require_mapping(
        raw_value,
        field_name="structured_output",
    )


def payload_to_inna_result(
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> InnaEvaluationResult:
    """
    Converte o payload do runner para o contrato determinístico
    já utilizado pela INNA.

    Não persiste dados e não realiza chamadas externas.
    """

    if payload.case_id != case.case_id:
        raise DeterministicPayloadError(
            "O case_id do payload não corresponde "
            "ao caso de avaliação."
        )

    metadata = payload.metadata

    human_review_requested = _optional_bool(
        metadata.get(
            "human_review_requested"
        ),
        field_name="human_review_requested",
    )

    return InnaEvaluationResult(
        case_id=case.case_id,
        input_text=payload.input_text,
        actual_output=payload.actual_output,
        dataset_name=case.dataset_name,
        dataset_version=case.dataset_version,
        case_version=case.case_version,
        status=EvaluationStatus.PENDING,
        current_agent=str(
            _mapping_value(
                metadata,
                "actual_agent",
                default="",
            )
        ).strip(),
        current_team=str(
            _mapping_value(
                metadata,
                "actual_team",
                default="",
            )
        ).strip(),
        intent=str(
            _mapping_value(
                metadata,
                "actual_intent",
                default="",
            )
        ).strip(),
        task_status=str(
            _mapping_value(
                metadata,
                "actual_task_status",
                default="",
            )
        ).strip(),
        task_completion_score=float(
            _mapping_value(
                metadata,
                "task_completion_score",
                default=0.0,
            )
        ),
        tools_called=_parse_called_tools(
            metadata
        ),
        retrieval_documents=(
            _parse_retrieval_documents(
                payload
            )
        ),
        errors=tuple(
            str(item)
            for item in metadata.get(
                "errors",
                (),
            )
        ),
        warnings=tuple(
            str(item)
            for item in metadata.get(
                "warnings",
                (),
            )
        ),
        trace=tuple(
            str(item)
            for item in metadata.get(
                "trace",
                (),
            )
        ),
        latency_ms=_optional_float(
            metadata.get("latency_ms"),
            field_name="latency_ms",
        ),
        estimated_cost=_optional_float(
            metadata.get("estimated_cost"),
            field_name="estimated_cost",
        ),
        human_review_requested=bool(
            human_review_requested
        ),
        human_review_status=_optional_text(
            metadata.get(
                "human_review_status"
            )
        ),
        human_review_id=_optional_text(
            metadata.get(
                "human_review_id"
            )
        ),
        privacy_level=case.privacy_level,
        external_payload_sanitized=bool(
            metadata.get(
                "external_payload_sanitized",
                False,
            )
        ),
        structured_response=dict(
            _structured_response(metadata)
        ),
        raw_state=dict(
            metadata.get(
                "raw_state",
                {},
            )
        ),
        metadata={
            "adapted_from": (
                "DeepEvalCasePayload"
            ),
        },
    )


def _metric_output(
    metric: MetricDefinition,
    result: MetricResult | None,
    *,
    empty_reason: str,
) -> MetricExecutionOutput:
    if result is None:
        return MetricExecutionOutput(
            passed=True,
            score=1.0,
            reason=empty_reason,
            metadata={
                "metric_id": metric.metric_id,
                "expectation_skipped": True,
            },
        )

    return MetricExecutionOutput(
        passed=result.passed,
        score=result.score,
        reason=result.reason,
        estimated_cost=0.0,
        metadata={
            "metric_id": metric.metric_id,
            "source_metric": result.name,
            "category": result.category.value,
            "threshold": result.threshold,
            "error": result.error,
            "details": dict(result.details),
        },
    )


def execute_expected_terms(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    evaluated = evaluate_expected_terms(
        case,
        result,
        _DEFAULT_CONFIG,
    )

    return _metric_output(
        metric,
        evaluated,
        empty_reason=(
            "O caso não possui termos obrigatórios."
        ),
    )


def execute_forbidden_terms(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    evaluated = evaluate_forbidden_terms(
        case,
        result,
        _DEFAULT_CONFIG,
    )

    return _metric_output(
        metric,
        evaluated,
        empty_reason=(
            "O caso não possui termos proibidos."
        ),
    )


def execute_retrieval_contract(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    metric_results = tuple(
        item
        for item in (
            evaluate_retrieval_count(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_retrieval_terms(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
        )
        if item is not None
    )

    return _combine_metric_results(
        metric,
        metric_results,
        empty_reason=(
            "O caso não possui contrato de recuperação."
        ),
    )


def execute_latency_budget(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    evaluated = evaluate_latency(
        case,
        result,
        _DEFAULT_CONFIG,
    )

    return _metric_output(
        metric,
        evaluated,
        empty_reason=(
            "O caso não possui limite de latência."
        ),
    )


def execute_cost_budget(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    evaluated = evaluate_cost(
        case,
        result,
        _DEFAULT_CONFIG,
    )

    return _metric_output(
        metric,
        evaluated,
        empty_reason=(
            "O caso não possui limite de custo."
        ),
    )


def execute_contract_validation(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    result = payload_to_inna_result(
        case,
        payload,
    )

    metric_results = tuple(
        item
        for item in (
            evaluate_agent(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_team(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_intent(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_task_status(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_expected_tools(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_forbidden_tools(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
            evaluate_structured_output(
                case,
                result,
                _DEFAULT_CONFIG,
            ),
        )
        if item is not None
    )

    return _combine_metric_results(
        metric,
        metric_results,
        empty_reason=(
            "O caso não possui expectativas "
            "contratuais adicionais."
        ),
    )


def execute_human_review_policy(
    metric: MetricDefinition,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
) -> MetricExecutionOutput:
    expected = case.human_review_expected

    if expected is None:
        return MetricExecutionOutput(
            passed=True,
            score=1.0,
            reason=(
                "O caso não define expectativa HITL."
            ),
            metadata={
                "expectation_skipped": True,
            },
        )

    metadata = payload.metadata

    actual_requested = _optional_bool(
        metadata.get(
            "human_review_requested"
        ),
        field_name="human_review_requested",
    )

    actual_status = normalize_text(
        metadata.get(
            "human_review_status",
            metadata.get(
                "actual_task_status",
                "",
            ),
        )
    )

    expected_status = normalize_text(
        case.expected_task_status
    )

    request_matches = (
        actual_requested is expected
    )

    status_matches = (
        not expected_status
        or actual_status == expected_status
    )

    passed = (
        request_matches
        and status_matches
    )

    score = (
        float(request_matches)
        + float(status_matches)
    ) / 2

    if passed:
        reason = (
            "A política de revisão humana foi atendida."
        )
    else:
        failures: list[str] = []

        if not request_matches:
            failures.append(
                "human_review_requested incompatível"
            )

        if not status_matches:
            failures.append(
                "status de revisão incompatível"
            )

        reason = "; ".join(failures)

    return MetricExecutionOutput(
        passed=passed,
        score=score,
        reason=reason,
        metadata={
            "expected_review": expected,
            "actual_review": actual_requested,
            "expected_status": (
                case.expected_task_status
            ),
            "actual_status": (
                metadata.get(
                    "human_review_status",
                    metadata.get(
                        "actual_task_status",
                    ),
                )
            ),
        },
    )


def _combine_metric_results(
    metric: MetricDefinition,
    metric_results: tuple[
        MetricResult,
        ...,
    ],
    *,
    empty_reason: str,
) -> MetricExecutionOutput:
    if not metric_results:
        return MetricExecutionOutput(
            passed=True,
            score=1.0,
            reason=empty_reason,
            metadata={
                "metric_id": metric.metric_id,
                "expectation_skipped": True,
            },
        )

    score = sum(
        item.score
        for item in metric_results
    ) / len(metric_results)

    passed = all(
        item.passed
        for item in metric_results
    )

    failed_names = tuple(
        item.name
        for item in metric_results
        if not item.passed
    )

    if passed:
        reason = (
            "Todas as validações determinísticas "
            "foram aprovadas."
        )
    else:
        reason = (
            "Validações reprovadas: "
            + ", ".join(failed_names)
        )

    return MetricExecutionOutput(
        passed=passed,
        score=score,
        reason=reason,
        estimated_cost=0.0,
        metadata={
            "metric_id": metric.metric_id,
            "evaluated_metrics": tuple(
                item.name
                for item in metric_results
            ),
            "failed_metrics": failed_names,
            "details": {
                item.name: dict(item.details)
                for item in metric_results
            },
        },
    )


def build_default_deterministic_executors(
) -> Mapping[str, MetricExecutor]:
    """
    Retorna os executores locais oficiais da INNA.

    As métricas live não são incluídas.
    """

    return {
        "contract-validation": (
            execute_contract_validation
        ),
        "expected-terms": execute_expected_terms,
        "forbidden-terms": execute_forbidden_terms,
        "retrieval-contract": (
            execute_retrieval_contract
        ),
        "latency-budget": execute_latency_budget,
        "cost-budget": execute_cost_budget,
        "human-review-policy": (
            execute_human_review_policy
        ),
    }


def build_deterministic_runner(
):
    """
    Constrói um EvaluationRunner com todos os executores locais.

    O import é local para evitar dependência circular no carregamento
    dos módulos.
    """

    from src.compartilhado.avaliacao.deepeval_runner import (
        EvaluationRunner,
    )

    return EvaluationRunner(
        executors=(
            build_default_deterministic_executors()
        )
    )


__all__ = [
    "DeterministicExecutorError",
    "DeterministicPayloadError",
    "build_default_deterministic_executors",
    "build_deterministic_runner",
    "execute_contract_validation",
    "execute_cost_budget",
    "execute_expected_terms",
    "execute_forbidden_terms",
    "execute_human_review_policy",
    "execute_latency_budget",
    "execute_retrieval_contract",
    "payload_to_inna_result",
]

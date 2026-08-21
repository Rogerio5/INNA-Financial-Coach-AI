from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from src.compartilhado.avaliacao.contracts import (
    EvaluationStatus,
    InnaEvaluationCase,
    InnaEvaluationResult,
    ModelExecution,
    ObservedToolCall,
    PrivacyLevel,
    RetrievalDocument,
    TokenUsage,
)
from src.compartilhado.avaliacao.privacy import (
    content_hash,
    hash_identifier,
    prepare_external_payload,
    prepare_internal_payload,
    sanitize_exception,
)

StateMapping = Mapping[str, Any]
Executor = Callable[..., Mapping[str, Any]]


@dataclass(frozen=True, slots=True)
class AdapterConfig:
    """
    Configuração do adaptador de avaliações da INNA.

    O adaptador não envia dados para serviços externos. Ele apenas
    normaliza o estado interno e prepara contratos seguros.
    """

    application_version: str | None = None
    graph_version: str | None = None
    prompt_version: str | None = None

    default_agent: str = ""
    default_team: str = ""
    default_intent: str = ""
    default_task_status: str = "unknown"

    preserve_raw_state: bool = False
    sanitize_internal_state: bool = True

    hash_salt: str | None = None
    user_hash_prefix: str = "usr"

    metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )



_EXTERNAL_BRL_AMOUNT_PATTERN = re.compile(
    r"(?i)"
    r"(?<![A-Za-z0-9])"
    r"R\$\s*"
    r"\d{1,3}"
    r"(?:\.\d{3})*"
    r"(?:,\d{1,2})?"
    r"(?![A-Za-z0-9])"
)


def _sanitize_external_financial_text(
    value: Any,
) -> str:
    """
    Remove valores monetários explícitos antes da exportação externa.

    A sanitização é aplicada somente a textos destinados a plataformas
    externas. O conteúdo original permanece disponível no resultado
    interno da avaliação.
    """

    normalized = _safe_string(value)

    if not normalized:
        return normalized

    return _EXTERNAL_BRL_AMOUNT_PATTERN.sub(
        "[REDACTED_FINANCIAL_DATA]",
        normalized,
    )

def _safe_string(
    value: Any,
    *,
    default: str = "",
) -> str:
    """Converte um valor em string normalizada."""

    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip()
        return normalized or default

    normalized = str(value).strip()

    return normalized or default


def _safe_optional_string(
    value: Any,
) -> str | None:
    """Converte um valor em string opcional."""

    normalized = _safe_string(value)

    return normalized or None


def _safe_float(
    value: Any,
    *,
    default: float = 0.0,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    """Converte valores numéricos de forma defensiva."""

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        normalized = default

    if minimum is not None:
        normalized = max(
            minimum,
            normalized,
        )

    if maximum is not None:
        normalized = min(
            maximum,
            normalized,
        )

    return normalized


def _safe_non_negative_float(
    value: Any,
) -> float | None:
    """Converte um valor opcional para número não negativo."""

    if value is None:
        return None

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        return None

    if normalized < 0:
        return None

    return normalized


def _safe_non_negative_int(
    value: Any,
    *,
    default: int = 0,
) -> int:
    """Converte um valor em inteiro não negativo."""

    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return default

    return max(
        0,
        normalized,
    )


def _mapping_or_empty(
    value: Any,
) -> Mapping[str, Any]:
    """Retorna o valor quando for Mapping ou um mapping vazio."""

    if isinstance(value, Mapping):
        return value

    return {}


def _sequence_or_empty(
    value: Any,
) -> Sequence[Any]:
    """
    Retorna uma sequência válida.

    Strings e bytes não são considerados coleções estruturadas.
    """

    if isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        return value

    return ()


def _first_present(
    state: StateMapping,
    *keys: str,
    default: Any = None,
) -> Any:
    """Retorna o primeiro campo presente e não nulo."""

    for key in keys:
        if key in state and state[key] is not None:
            return state[key]

    return default


def _extract_response(
    state: StateMapping,
) -> str:
    """Extrai a resposta textual principal do estado da INNA."""

    value = _first_present(
        state,
        "response",
        "answer",
        "final_answer",
        "output",
        "message",
        "assistant_response",
        default="",
    )

    if isinstance(value, Mapping):
        value = _first_present(
            value,
            "content",
            "text",
            "message",
            "answer",
            default="",
        )

    return _safe_string(value)


def _extract_status(
    state: StateMapping,
    *,
    has_errors: bool,
) -> EvaluationStatus:
    """
    Converte o estado da execução em EvaluationStatus.

    Essa classificação representa o estado técnico da execução. Métricas
    posteriores podem alterar o resultado agregado para PASSED ou FAILED.
    """

    if has_errors:
        return EvaluationStatus.ERROR

    raw_status = _safe_string(
        _first_present(
            state,
            "evaluation_status",
            "status",
            "task_status",
            default="",
        )
    ).lower()

    status_map = {
        "pending": EvaluationStatus.PENDING,
        "running": EvaluationStatus.RUNNING,
        "processing": EvaluationStatus.RUNNING,
        "in_progress": EvaluationStatus.RUNNING,
        "passed": EvaluationStatus.PASSED,
        "success": EvaluationStatus.PASSED,
        "succeeded": EvaluationStatus.PASSED,
        "completed": EvaluationStatus.PASSED,
        "complete": EvaluationStatus.PASSED,
        "failed": EvaluationStatus.FAILED,
        "failure": EvaluationStatus.FAILED,
        "rejected": EvaluationStatus.FAILED,
        "skipped": EvaluationStatus.SKIPPED,
        "cancelled": EvaluationStatus.SKIPPED,
        "canceled": EvaluationStatus.SKIPPED,
        "error": EvaluationStatus.ERROR,
        "errored": EvaluationStatus.ERROR,
    }

    return status_map.get(
        raw_status,
        EvaluationStatus.PENDING,
    )


def _extract_string_sequence(
    value: Any,
) -> tuple[str, ...]:
    """Normaliza erros, avisos e traces como tuplas de strings."""

    if value is None:
        return ()

    if isinstance(value, str):
        normalized = value.strip()
        return (normalized,) if normalized else ()

    if isinstance(value, Mapping):
        items = value.values()
    else:
        items = _sequence_or_empty(value)

    normalized_items: list[str] = []

    for item in items:
        if isinstance(item, BaseException):
            safe_error = sanitize_exception(item)
            text = _safe_string(
                safe_error.get("message")
            )
        else:
            text = _safe_string(item)

        if text:
            normalized_items.append(text)

    return tuple(normalized_items)


def _extract_tool_name(
    tool_result: Mapping[str, Any],
) -> str:
    """Extrai o nome de uma ferramenta observada."""

    tool_value = _first_present(
        tool_result,
        "name",
        "tool_name",
        "tool",
        "function_name",
        "action",
        default="unknown_tool",
    )

    if isinstance(tool_value, Mapping):
        tool_value = _first_present(
            tool_value,
            "name",
            "tool_name",
            default="unknown_tool",
        )

    return _safe_string(
        tool_value,
        default="unknown_tool",
    )


def _extract_tool_arguments(
    tool_result: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Extrai argumentos de uma chamada de ferramenta."""

    value = _first_present(
        tool_result,
        "arguments",
        "args",
        "input",
        "parameters",
        "tool_input",
        default={},
    )

    return _mapping_or_empty(value)


def _extract_tool_output(
    tool_result: Mapping[str, Any],
) -> Any:
    """Extrai a saída de uma chamada de ferramenta."""

    return _first_present(
        tool_result,
        "output",
        "result",
        "response",
        "data",
        "tool_output",
        default=None,
    )


def _extract_tool_status(
    tool_result: Mapping[str, Any],
) -> str:
    """Normaliza o status de uma chamada de ferramenta."""

    raw_status = _safe_string(
        _first_present(
            tool_result,
            "status",
            "state",
            default="",
        )
    ).lower()

    if raw_status:
        return raw_status

    if tool_result.get("error"):
        return "error"

    if tool_result.get("success") is True:
        return "success"

    if tool_result.get("success") is False:
        return "failed"

    return "unknown"


def extract_tool_calls(
    state: StateMapping,
) -> tuple[ObservedToolCall, ...]:
    """
    Extrai chamadas de ferramentas do estado da INNA.

    Suporta listas de mappings, mappings indexados e registros simples.
    """

    raw_tools = _first_present(
        state,
        "tool_results",
        "tools_called",
        "tool_calls",
        "tools",
        default=(),
    )

    if isinstance(raw_tools, Mapping):
        normalized_tools: Sequence[Any] = tuple(
            raw_tools.values()
        )
    else:
        normalized_tools = _sequence_or_empty(
            raw_tools
        )

    observed_tools: list[ObservedToolCall] = []

    for index, raw_tool in enumerate(normalized_tools):
        if isinstance(raw_tool, str):
            observed_tools.append(
                ObservedToolCall(
                    name=raw_tool,
                    status="unknown",
                    call_index=index,
                )
            )
            continue

        if not isinstance(raw_tool, Mapping):
            observed_tools.append(
                ObservedToolCall(
                    name=type(raw_tool).__name__,
                    output=repr(raw_tool),
                    status="unknown",
                    call_index=index,
                )
            )
            continue

        duration_ms = _safe_non_negative_float(
            _first_present(
                raw_tool,
                "duration_ms",
                "latency_ms",
                "elapsed_ms",
                default=None,
            )
        )

        observed_tools.append(
            ObservedToolCall(
                name=_extract_tool_name(raw_tool),
                arguments=_extract_tool_arguments(
                    raw_tool
                ),
                output=_extract_tool_output(
                    raw_tool
                ),
                status=_extract_tool_status(
                    raw_tool
                ),
                duration_ms=duration_ms,
                call_index=_safe_non_negative_int(
                    raw_tool.get(
                        "call_index",
                        index,
                    )
                ),
                error_code=_safe_optional_string(
                    _first_present(
                        raw_tool,
                        "error_code",
                        "code",
                        default=None,
                    )
                ),
                trace_id=_safe_optional_string(
                    raw_tool.get("trace_id")
                ),
                span_id=_safe_optional_string(
                    raw_tool.get("span_id")
                ),
                metadata=_mapping_or_empty(
                    raw_tool.get("metadata")
                ),
            )
        )

    return tuple(observed_tools)


def _document_content(
    document: Mapping[str, Any],
) -> str:
    """Extrai o conteúdo textual de um documento recuperado."""

    value = _first_present(
        document,
        "content",
        "text",
        "page_content",
        "chunk",
        "document",
        "body",
        default="",
    )

    return _safe_string(value)


def extract_retrieval_documents(
    state: StateMapping,
) -> tuple[RetrievalDocument, ...]:
    """
    Extrai documentos ou chunks recuperados pelo pipeline RAG.

    Documentos sem conteúdo são ignorados.
    """

    raw_documents = _first_present(
        state,
        "retrieval_documents",
        "retrieved_documents",
        "documents",
        "rag_documents",
        "rag_context",
        "contexts",
        "context",
        default=(),
    )

    if isinstance(raw_documents, str):
        raw_documents = (
            {
                "content": raw_documents,
            },
        )
    elif isinstance(raw_documents, Mapping):
        if _document_content(raw_documents):
            raw_documents = (
                raw_documents,
            )
        else:
            raw_documents = tuple(
                raw_documents.values()
            )
    else:
        raw_documents = _sequence_or_empty(
            raw_documents
        )

    documents: list[RetrievalDocument] = []

    for index, raw_document in enumerate(raw_documents):
        if isinstance(raw_document, str):
            content = raw_document.strip()

            if not content:
                continue

            documents.append(
                RetrievalDocument(
                    content=content,
                    content_hash=content_hash(content),
                    rank=index + 1,
                )
            )
            continue

        if not isinstance(raw_document, Mapping):
            content = _safe_string(
                raw_document
            )

            if not content:
                continue

            documents.append(
                RetrievalDocument(
                    content=content,
                    content_hash=content_hash(content),
                    rank=index + 1,
                )
            )
            continue

        content = _document_content(
            raw_document
        )

        if not content:
            continue

        score_value = _first_present(
            raw_document,
            "score",
            "similarity",
            "relevance_score",
            default=None,
        )

        score = None

        if score_value is not None:
            score = _safe_float(
                score_value,
                minimum=0.0,
                maximum=1.0,
            )

        documents.append(
            RetrievalDocument(
                content=content,
                document_id=_safe_optional_string(
                    _first_present(
                        raw_document,
                        "document_id",
                        "id",
                        "doc_id",
                        default=None,
                    )
                ),
                score=score,
                rank=_safe_non_negative_int(
                    raw_document.get(
                        "rank",
                        index + 1,
                    ),
                    default=index + 1,
                ),
                source=_safe_optional_string(
                    _first_present(
                        raw_document,
                        "source",
                        "filename",
                        "url",
                        default=None,
                    )
                ),
                content_hash=_safe_optional_string(
                    raw_document.get(
                        "content_hash"
                    )
                )
                or content_hash(content),
                metadata=_mapping_or_empty(
                    raw_document.get("metadata")
                ),
            )
        )

    return tuple(documents)


def _extract_token_usage(
    execution: Mapping[str, Any],
) -> TokenUsage:
    """Extrai uso de tokens de uma execução de modelo."""

    usage = _mapping_or_empty(
        _first_present(
            execution,
            "token_usage",
            "usage",
            "tokens",
            default={},
        )
    )

    input_tokens = _safe_non_negative_int(
        _first_present(
            usage,
            "input_tokens",
            "prompt_tokens",
            default=0,
        )
    )

    output_tokens = _safe_non_negative_int(
        _first_present(
            usage,
            "output_tokens",
            "completion_tokens",
            default=0,
        )
    )

    total_tokens = _safe_non_negative_int(
        usage.get("total_tokens"),
    )

    if (
        total_tokens
        and total_tokens
        < input_tokens + output_tokens
    ):
        total_tokens = input_tokens + output_tokens

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_tokens=_safe_non_negative_int(
            usage.get("cached_tokens")
        ),
        reasoning_tokens=_safe_non_negative_int(
            usage.get("reasoning_tokens")
        ),
    )


def extract_model_executions(
    state: StateMapping,
) -> tuple[ModelExecution, ...]:
    """Extrai registros de chamadas de modelos do estado."""

    raw_executions = _first_present(
        state,
        "model_executions",
        "llm_calls",
        "model_calls",
        default=(),
    )

    if isinstance(raw_executions, Mapping):
        raw_executions = tuple(
            raw_executions.values()
        )
    else:
        raw_executions = _sequence_or_empty(
            raw_executions
        )

    executions: list[ModelExecution] = []

    for raw_execution in raw_executions:
        if not isinstance(
            raw_execution,
            Mapping,
        ):
            continue

        provider = _safe_string(
            _first_present(
                raw_execution,
                "provider",
                "model_provider",
                default="unknown",
            ),
            default="unknown",
        )

        model_name = _safe_string(
            _first_present(
                raw_execution,
                "model_name",
                "model",
                default="unknown",
            ),
            default="unknown",
        )

        executions.append(
            ModelExecution(
                provider=provider,
                model_name=model_name,
                operation=_safe_string(
                    raw_execution.get(
                        "operation"
                    ),
                    default="generation",
                ),
                prompt_version=_safe_optional_string(
                    raw_execution.get(
                        "prompt_version"
                    )
                ),
                latency_ms=_safe_non_negative_float(
                    _first_present(
                        raw_execution,
                        "latency_ms",
                        "duration_ms",
                        default=None,
                    )
                ),
                estimated_cost=(
                    _safe_non_negative_float(
                        _first_present(
                            raw_execution,
                            "estimated_cost",
                            "cost",
                            default=None,
                        )
                    )
                ),
                cost_currency=_safe_string(
                    raw_execution.get(
                        "cost_currency"
                    ),
                    default="USD",
                ),
                token_usage=_extract_token_usage(
                    raw_execution
                ),
                status=_safe_string(
                    raw_execution.get("status"),
                    default="success",
                ),
                error_code=_safe_optional_string(
                    raw_execution.get(
                        "error_code"
                    )
                ),
                trace_id=_safe_optional_string(
                    raw_execution.get(
                        "trace_id"
                    )
                ),
                span_id=_safe_optional_string(
                    raw_execution.get(
                        "span_id"
                    )
                ),
                metadata=_mapping_or_empty(
                    raw_execution.get("metadata")
                ),
            )
        )

    return tuple(executions)


def _extract_structured_response(
    state: StateMapping,
) -> Mapping[str, Any]:
    """Extrai a saída estruturada produzida pela INNA."""

    value = _first_present(
        state,
        "structured_response",
        "structured_output",
        "response_data",
        default={},
    )

    return _mapping_or_empty(value)


def _build_user_hash(
    user_reference: str | int | None,
    config: AdapterConfig,
) -> str | None:
    """Gera referência pseudonimizada de usuário."""

    if user_reference is None:
        return None

    if not config.hash_salt:
        return None

    return hash_identifier(
        user_reference,
        salt=config.hash_salt,
        prefix=config.user_hash_prefix,
    )


class InnaEvaluationAdapter:
    """
    Adaptador entre o estado LangGraph e os contratos de avaliação.

    Ele pode receber um estado já executado ou chamar um executor
    fornecido explicitamente.
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
    ) -> None:
        self.config = config or AdapterConfig()

    def from_state(
        self,
        *,
        case: InnaEvaluationCase,
        state: StateMapping,
        latency_ms: float | None = None,
        user_reference: str | int | None = None,
        session_id: str | None = None,
        thread_id: str | None = None,
        trace_id: str | None = None,
    ) -> InnaEvaluationResult:
        """Transforma um estado existente em resultado normalizado."""

        errors = _extract_string_sequence(
            state.get("errors")
        )

        warnings = _extract_string_sequence(
            state.get("warnings")
        )

        trace = _extract_string_sequence(
            state.get("trace")
        )

        actual_output = _extract_response(
            state
        )

        status = _extract_status(
            state,
            has_errors=bool(errors),
        )

        if (
            not actual_output
            and status
            not in {
                EvaluationStatus.ERROR,
                EvaluationStatus.SKIPPED,
            }
        ):
            status = EvaluationStatus.ERROR
            errors = (
                *errors,
                "empty_response",
            )

        structured_response = (
            _extract_structured_response(state)
        )

        if self.config.sanitize_internal_state:
            safe_structured_response = (
                prepare_internal_payload(
                    structured_response
                )
            )
        else:
            safe_structured_response = dict(
                structured_response
            )

        if self.config.preserve_raw_state:
            if self.config.sanitize_internal_state:
                raw_state = prepare_internal_payload(
                    state
                )
            else:
                raw_state = dict(state)
        else:
            raw_state = {}

        current_agent = _safe_string(
            _first_present(
                state,
                "current_agent",
                "agent",
                "selected_agent",
                default=self.config.default_agent,
            )
        )

        current_team = _safe_string(
            _first_present(
                state,
                "current_team",
                "team",
                "selected_team",
                default=self.config.default_team,
            )
        )

        intent = _safe_string(
            _first_present(
                state,
                "intent",
                "detected_intent",
                "classified_intent",
                default=self.config.default_intent,
            )
        )

        task_status = _safe_string(
            _first_present(
                state,
                "task_status",
                "status",
                default=self.config.default_task_status,
            ),
            default=self.config.default_task_status,
        )

        completion_score = _safe_float(
            _first_present(
                state,
                "task_completion_score",
                "completion_score",
                default=0.0,
            ),
            default=0.0,
            minimum=0.0,
            maximum=1.0,
        )

        total_cost = _safe_non_negative_float(
            _first_present(
                state,
                "estimated_cost",
                "total_cost",
                default=None,
            )
        )

        cost_currency = _safe_string(
            state.get("cost_currency"),
            default="USD",
        )

        metadata = {
            **dict(self.config.metadata),
            "adapter": (
                "InnaEvaluationAdapter"
            ),
        }

        return InnaEvaluationResult(
            case_id=case.case_id,
            input_text=case.input_text,
            actual_output=actual_output,
            dataset_name=case.dataset_name,
            dataset_version=case.dataset_version,
            case_version=case.case_version,
            status=status,
            current_agent=current_agent,
            current_team=current_team,
            intent=intent,
            task_status=task_status,
            task_completion_score=completion_score,
            tools_called=extract_tool_calls(state),
            retrieval_documents=(
                extract_retrieval_documents(state)
            ),
            model_executions=(
                extract_model_executions(state)
            ),
            errors=errors,
            warnings=warnings,
            trace=trace,
            application_version=(
                self.config.application_version
            ),
            graph_version=self.config.graph_version,
            prompt_version=(
                self.config.prompt_version
            ),
            latency_ms=latency_ms,
            estimated_cost=total_cost,
            cost_currency=cost_currency,
            trace_id=(
                trace_id
                or _safe_optional_string(
                    state.get("trace_id")
                )
            ),
            thread_id=(
                thread_id
                or _safe_optional_string(
                    state.get("thread_id")
                )
            ),
            session_id=(
                session_id
                or _safe_optional_string(
                    state.get("session_id")
                )
            ),
            user_reference_hash=_build_user_hash(
                user_reference,
                self.config,
            ),
            human_review_requested=bool(
                _first_present(
                    state,
                    "human_review_requested",
                    "requires_human_review",
                    "hitl_required",
                    default=False,
                )
            ),
            human_review_status=(
                _safe_optional_string(
                    _first_present(
                        state,
                        "human_review_status",
                        "hitl_status",
                        default=None,
                    )
                )
            ),
            human_review_id=(
                _safe_optional_string(
                    _first_present(
                        state,
                        "human_review_id",
                        "review_id",
                        default=None,
                    )
                )
            ),
            privacy_level=case.privacy_level,
            external_payload_sanitized=False,
            structured_response=(
                _mapping_or_empty(
                    safe_structured_response
                )
            ),
            raw_state=_mapping_or_empty(
                raw_state
            ),
            metadata=metadata,
        )

    def execute(
        self,
        *,
        case: InnaEvaluationCase,
        executor: Executor,
        execution_kwargs: Mapping[str, Any] | None = None,
        user_reference: str | int | None = None,
        session_id: str | None = None,
        thread_id: str | None = None,
        trace_id: str | None = None,
    ) -> InnaEvaluationResult:
        """
        Executa um caso com um executor fornecido e mede a latência.

        O executor deve retornar um Mapping contendo o estado final.
        """

        kwargs = dict(
            execution_kwargs or {}
        )

        started_at = perf_counter()

        try:
            state = executor(
                case.input_text,
                **kwargs,
            )

            if not isinstance(state, Mapping):
                raise TypeError(
                    "O executor da INNA deve retornar "
                    "um objeto Mapping."
                )

        except Exception as exception:
            latency_ms = (
                perf_counter() - started_at
            ) * 1000

            safe_error = sanitize_exception(
                exception
            )

            return InnaEvaluationResult(
                case_id=case.case_id,
                input_text=case.input_text,
                actual_output="",
                dataset_name=case.dataset_name,
                dataset_version=case.dataset_version,
                case_version=case.case_version,
                status=EvaluationStatus.ERROR,
                errors=(
                    _safe_string(
                        safe_error.get(
                            "message"
                        ),
                        default="execution_error",
                    ),
                ),
                application_version=(
                    self.config.application_version
                ),
                graph_version=(
                    self.config.graph_version
                ),
                prompt_version=(
                    self.config.prompt_version
                ),
                latency_ms=latency_ms,
                trace_id=trace_id,
                thread_id=thread_id,
                session_id=session_id,
                user_reference_hash=(
                    _build_user_hash(
                        user_reference,
                        self.config,
                    )
                ),
                privacy_level=case.privacy_level,
                metadata={
                    **dict(self.config.metadata),
                    "adapter": (
                        "InnaEvaluationAdapter"
                    ),
                    "error_type": type(
                        exception
                    ).__name__,
                },
            )

        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        return self.from_state(
            case=case,
            state=state,
            latency_ms=latency_ms,
            user_reference=user_reference,
            session_id=session_id,
            thread_id=thread_id,
            trace_id=trace_id,
        )

    def prepare_external_result(
        self,
        result: InnaEvaluationResult,
    ) -> Mapping[str, Any]:
        """
        Produz payload sanitizado para DeepEval, Phoenix ou Weave.

        Resultados RESTRICTED são bloqueados.
        """

        if (
            result.privacy_level
            == PrivacyLevel.RESTRICTED
        ):
            raise ValueError(
                "Resultados RESTRICTED não podem "
                "ser exportados externamente."
            )

        payload = {
            "evaluation_id": result.evaluation_id,
            "schema_version": result.schema_version,
            "case_id": result.case_id,
            "dataset_name": result.dataset_name,
            "dataset_version": (
                result.dataset_version
            ),
            "case_version": result.case_version,
            "status": result.status.value,
            "input": _sanitize_external_financial_text(
                result.input_text
            ),
            "actual_output": _sanitize_external_financial_text(
                result.actual_output
            ),
            "current_agent": result.current_agent,
            "current_team": result.current_team,
            "intent": result.intent,
            "task_status": result.task_status,
            "task_completion_score": (
                result.task_completion_score
            ),
            "tools_called": [
                {
                    "tool_name": tool.name,
                    "status": tool.status,
                    "duration_ms": (
                        tool.duration_ms
                    ),
                    "call_index": (
                        tool.call_index
                    ),
                }
                for tool in result.tools_called
            ],
            "retrieval_context": list(
                result.retrieval_context
            ),
            "errors": list(result.errors),
            "warnings": list(result.warnings),
            "trace": list(result.trace),
            "latency_ms": result.latency_ms,
            "estimated_cost": (
                result.estimated_cost
            ),
            "cost_currency": (
                result.cost_currency
            ),
            "trace_id": result.trace_id,
            "thread_id": result.thread_id,
            "session_id": result.session_id,
            "user_reference_hash": (
                result.user_reference_hash
            ),
            "human_review_requested": (
                result.human_review_requested
            ),
            "human_review_status": (
                result.human_review_status
            ),
            "structured_response": dict(
                result.structured_response
            ),
            "metadata": dict(result.metadata),
        }

        sanitized = prepare_external_payload(
            payload
        )

        return _mapping_or_empty(sanitized)


def build_default_adapter(
    *,
    application_version: str | None = None,
    graph_version: str | None = None,
    prompt_version: str | None = None,
    hash_salt: str | None = None,
    preserve_raw_state: bool = False,
) -> InnaEvaluationAdapter:
    """Cria um adaptador com configuração padrão."""

    return InnaEvaluationAdapter(
        AdapterConfig(
            application_version=application_version,
            graph_version=graph_version,
            prompt_version=prompt_version,
            hash_salt=hash_salt,
            preserve_raw_state=preserve_raw_state,
        )
    )


__all__ = [
    "AdapterConfig",
    "Executor",
    "InnaEvaluationAdapter",
    "StateMapping",
    "build_default_adapter",
    "extract_model_executions",
    "extract_retrieval_documents",
    "extract_tool_calls",
]

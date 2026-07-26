from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from src.evaluation.adapters import (
    AdapterConfig,
    InnaEvaluationAdapter,
    build_default_adapter,
    extract_model_executions,
    extract_retrieval_documents,
    extract_tool_calls,
)
from src.evaluation.contracts import (
    EvaluationStatus,
    InnaEvaluationCase,
    PrivacyLevel,
)

# ============================================================
# FIXTURES E FUNÇÕES AUXILIARES
# ============================================================


@pytest.fixture
def evaluation_case() -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id="adapter-case-001",
        input_text=(
            "Minha renda é R$ 3.000, os gastos fixos são "
            "R$ 1.400, os gastos variáveis são R$ 700, "
            "as dívidas são R$ 300 e a reserva é R$ 500."
        ),
        dataset_name="inna-core",
        dataset_version="1.0.0",
        case_version="1.0.0",
        category="financial",
        privacy_level=PrivacyLevel.CONFIDENTIAL,
    )


@pytest.fixture
def complete_state() -> dict[str, Any]:
    return {
        "response": "Diagnóstico financeiro concluído.",
        "current_agent": "financial_agent",
        "current_team": "financial_team",
        "intent": "diagnostico_financeiro",
        "task_status": "completed",
        "task_completion_score": 0.95,
        "structured_response": {
            "summary": "Diagnóstico concluído.",
            "income": 3000,
            "expenses": 2400,
        },
        "tool_results": [
            {
                "tool_name": "financial_calculator",
                "arguments": {
                    "income": 3000,
                    "expenses": 2400,
                },
                "result": {
                    "balance": 600,
                },
                "status": "success",
                "duration_ms": 12.5,
                "call_index": 0,
                "trace_id": "trace-tool-001",
                "span_id": "span-tool-001",
            },
            {
                "tool_name": "rag_search",
                "arguments": {
                    "query": "reserva de emergência",
                },
                "result": {
                    "documents": 1,
                },
                "status": "success",
                "duration_ms": 20.0,
                "call_index": 1,
            },
        ],
        "retrieved_documents": [
            {
                "document_id": "doc-001",
                "content": (
                    "Uma reserva de emergência deve proteger "
                    "o orçamento contra imprevistos."
                ),
                "score": 0.91,
                "rank": 1,
                "source": "base-financeira",
                "metadata": {
                    "category": "reserva",
                },
            }
        ],
        "model_executions": [
            {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "operation": "generation",
                "latency_ms": 320.0,
                "estimated_cost": 0.001,
                "cost_currency": "USD",
                "status": "success",
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                    "cached_tokens": 0,
                    "reasoning_tokens": 0,
                },
            }
        ],
        "errors": [],
        "warnings": [
            "low_confidence_optional",
        ],
        "trace": [
            "supervisor",
            "financial_agent",
            "financial_calculator",
            "rag_search",
        ],
        "estimated_cost": 0.001,
        "cost_currency": "USD",
        "trace_id": "trace-001",
        "thread_id": "thread-001",
        "session_id": "session-001",
        "human_review_requested": False,
    }


def build_adapter(
    *,
    preserve_raw_state: bool = False,
    sanitize_internal_state: bool = True,
    hash_salt: str | None = "salt-local-apenas-para-teste",
) -> InnaEvaluationAdapter:
    return InnaEvaluationAdapter(
        AdapterConfig(
            application_version="1.0.0",
            graph_version="langgraph-v1",
            prompt_version="financial-v1",
            preserve_raw_state=preserve_raw_state,
            sanitize_internal_state=sanitize_internal_state,
            hash_salt=hash_salt,
            metadata={
                "environment": "test",
            },
        )
    )


# ============================================================
# ADAPTER CONFIG
# ============================================================


def test_adapter_config_defaults() -> None:
    config = AdapterConfig()

    assert config.application_version is None
    assert config.graph_version is None
    assert config.prompt_version is None
    assert config.default_agent == ""
    assert config.default_team == ""
    assert config.default_intent == ""
    assert config.default_task_status == "unknown"
    assert config.preserve_raw_state is False
    assert config.sanitize_internal_state is True
    assert config.hash_salt is None
    assert config.user_hash_prefix == "usr"


def test_build_default_adapter() -> None:
    adapter = build_default_adapter(
        application_version="1.2.0",
        graph_version="graph-v2",
        prompt_version="prompt-v3",
        hash_salt="salt-teste",
        preserve_raw_state=True,
    )

    assert isinstance(
        adapter,
        InnaEvaluationAdapter,
    )
    assert adapter.config.application_version == "1.2.0"
    assert adapter.config.graph_version == "graph-v2"
    assert adapter.config.prompt_version == "prompt-v3"
    assert adapter.config.hash_salt == "salt-teste"
    assert adapter.config.preserve_raw_state is True


# ============================================================
# EXTRAÇÃO DE FERRAMENTAS
# ============================================================


def test_extract_tool_calls_from_list() -> None:
    state = {
        "tool_results": [
            {
                "tool_name": "financial_calculator",
                "arguments": {
                    "income": 3000,
                },
                "result": {
                    "balance": 500,
                },
                "status": "success",
                "duration_ms": 10.5,
            }
        ]
    }

    tools = extract_tool_calls(state)

    assert len(tools) == 1
    assert tools[0].name == "financial_calculator"
    assert tools[0].arguments["income"] == 3000
    assert tools[0].output == {
        "balance": 500,
    }
    assert tools[0].status == "success"
    assert tools[0].duration_ms == pytest.approx(10.5)
    assert tools[0].call_index == 0


def test_extract_tool_calls_from_mapping() -> None:
    state = {
        "tool_results": {
            "first": {
                "name": "rag_search",
                "status": "success",
            },
            "second": {
                "name": "financial_calculator",
                "status": "failed",
            },
        }
    }

    tools = extract_tool_calls(state)

    assert len(tools) == 2
    assert tools[0].name == "rag_search"
    assert tools[1].name == "financial_calculator"


def test_extract_tool_calls_from_strings() -> None:
    state = {
        "tools_called": [
            "rag_search",
            "financial_calculator",
        ]
    }

    tools = extract_tool_calls(state)

    assert len(tools) == 2
    assert tools[0].name == "rag_search"
    assert tools[0].status == "unknown"
    assert tools[1].name == "financial_calculator"


def test_extract_tool_calls_detects_error() -> None:
    state = {
        "tool_results": [
            {
                "tool_name": "rag_search",
                "error": "timeout",
            }
        ]
    }

    tools = extract_tool_calls(state)

    assert len(tools) == 1
    assert tools[0].status == "error"


@pytest.mark.parametrize(
    ("success_value", "expected_status"),
    (
        (
            True,
            "success",
        ),
        (
            False,
            "failed",
        ),
    ),
)
def test_extract_tool_calls_detects_boolean_success(
    success_value: bool,
    expected_status: str,
) -> None:
    state = {
        "tool_results": [
            {
                "tool_name": "tool",
                "success": success_value,
            }
        ]
    }

    tools = extract_tool_calls(state)

    assert tools[0].status == expected_status


def test_extract_tool_calls_handles_unknown_object() -> None:
    class CustomToolResult:
        pass

    state = {
        "tool_results": [
            CustomToolResult(),
        ]
    }

    tools = extract_tool_calls(state)

    assert len(tools) == 1
    assert tools[0].name == "CustomToolResult"
    assert tools[0].status == "unknown"


def test_extract_tool_calls_handles_empty_state() -> None:
    assert extract_tool_calls({}) == ()


def test_extract_tool_calls_rejects_negative_duration_safely() -> None:
    state = {
        "tool_results": [
            {
                "tool_name": "rag_search",
                "duration_ms": -10,
            }
        ]
    }

    tools = extract_tool_calls(state)

    assert tools[0].duration_ms is None


def test_extract_tool_calls_defaults_invalid_index() -> None:
    state = {
        "tool_results": [
            {
                "tool_name": "rag_search",
                "call_index": "invalid",
            }
        ]
    }

    tools = extract_tool_calls(state)

    assert tools[0].call_index == 0


# ============================================================
# EXTRAÇÃO DE DOCUMENTOS RAG
# ============================================================


def test_extract_retrieval_documents_from_list() -> None:
    state = {
        "retrieved_documents": [
            {
                "document_id": "doc-001",
                "content": "Documento financeiro.",
                "score": 0.9,
                "rank": 1,
                "source": "base",
            }
        ]
    }

    documents = extract_retrieval_documents(state)

    assert len(documents) == 1
    assert documents[0].document_id == "doc-001"
    assert documents[0].content == "Documento financeiro."
    assert documents[0].score == pytest.approx(0.9)
    assert documents[0].rank == 1
    assert documents[0].source == "base"
    assert documents[0].content_hash is not None


def test_extract_retrieval_documents_from_string() -> None:
    state = {
        "rag_context": (
            "Uma reserva de emergência reduz riscos."
        )
    }

    documents = extract_retrieval_documents(state)

    assert len(documents) == 1
    assert documents[0].content == (
        "Uma reserva de emergência reduz riscos."
    )
    assert documents[0].rank == 1
    assert documents[0].content_hash is not None


def test_extract_retrieval_documents_supports_page_content() -> None:
    state = {
        "documents": [
            {
                "page_content": (
                    "Conteúdo no formato LangChain."
                ),
                "metadata": {
                    "source": "langchain",
                },
            }
        ]
    }

    documents = extract_retrieval_documents(state)

    assert len(documents) == 1
    assert documents[0].content == (
        "Conteúdo no formato LangChain."
    )


def test_extract_retrieval_documents_ignores_empty_content() -> None:
    state = {
        "documents": [
            {
                "content": "",
            },
            {
                "content": "   ",
            },
        ]
    }

    documents = extract_retrieval_documents(state)

    assert documents == ()


@pytest.mark.parametrize(
    ("score", "expected"),
    (
        (
            -1.0,
            0.0,
        ),
        (
            0.5,
            0.5,
        ),
        (
            2.0,
            1.0,
        ),
        (
            "invalid",
            0.0,
        ),
    ),
)
def test_extract_retrieval_documents_clamps_scores(
    score: Any,
    expected: float,
) -> None:
    state = {
        "documents": [
            {
                "content": "Documento",
                "score": score,
            }
        ]
    }

    documents = extract_retrieval_documents(state)

    assert documents[0].score == pytest.approx(
        expected
    )


def test_extract_retrieval_documents_generates_content_hash() -> None:
    state = {
        "documents": [
            {
                "content": "Mesmo conteúdo",
            },
            {
                "content": "Mesmo conteúdo",
            },
        ]
    }

    documents = extract_retrieval_documents(state)

    assert (
        documents[0].content_hash
        == documents[1].content_hash
    )


def test_extract_retrieval_documents_handles_empty_state() -> None:
    assert extract_retrieval_documents({}) == ()


# ============================================================
# EXTRAÇÃO DE EXECUÇÕES DE MODELOS
# ============================================================


def test_extract_model_executions() -> None:
    state = {
        "model_executions": [
            {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "latency_ms": 300,
                "estimated_cost": 0.001,
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                },
            }
        ]
    }

    executions = extract_model_executions(state)

    assert len(executions) == 1
    assert executions[0].provider == "google"
    assert executions[0].model_name == (
        "gemini-2.5-flash"
    )
    assert executions[0].latency_ms == pytest.approx(
        300
    )
    assert executions[0].estimated_cost == pytest.approx(
        0.001
    )
    assert (
        executions[0].token_usage.input_tokens
        == 100
    )
    assert (
        executions[0].token_usage.output_tokens
        == 50
    )
    assert (
        executions[0].token_usage.total_tokens
        == 150
    )


def test_extract_model_executions_supports_alternative_token_names() -> None:
    state = {
        "llm_calls": [
            {
                "model_provider": "google",
                "model": "gemini",
                "usage": {
                    "prompt_tokens": 80,
                    "completion_tokens": 20,
                },
            }
        ]
    }

    executions = extract_model_executions(state)

    assert len(executions) == 1
    assert executions[0].provider == "google"
    assert executions[0].model_name == "gemini"
    assert (
        executions[0].token_usage.input_tokens
        == 80
    )
    assert (
        executions[0].token_usage.output_tokens
        == 20
    )
    assert (
        executions[0].token_usage.calculated_total_tokens
        == 100
    )


def test_extract_model_executions_repairs_invalid_total() -> None:
    state = {
        "model_executions": [
            {
                "provider": "google",
                "model_name": "gemini",
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 120,
                },
            }
        ]
    }

    executions = extract_model_executions(state)

    assert (
        executions[0].token_usage.total_tokens
        == 150
    )


def test_extract_model_executions_ignores_invalid_entries() -> None:
    state = {
        "model_executions": [
            "invalid",
            123,
            None,
        ]
    }

    assert extract_model_executions(state) == ()


def test_extract_model_executions_handles_empty_state() -> None:
    assert extract_model_executions({}) == ()


# ============================================================
# CONVERSÃO DE ESTADO
# ============================================================


def test_from_state_builds_complete_result(
    evaluation_case: InnaEvaluationCase,
    complete_state: dict[str, Any],
) -> None:
    adapter = build_adapter(
        preserve_raw_state=True,
    )

    result = adapter.from_state(
        case=evaluation_case,
        state=complete_state,
        latency_ms=150.0,
        user_reference="usuario-123",
    )

    assert result.case_id == "adapter-case-001"
    assert result.actual_output == (
        "Diagnóstico financeiro concluído."
    )
    assert result.dataset_name == "inna-core"
    assert result.dataset_version == "1.0.0"
    assert result.case_version == "1.0.0"
    assert result.status == EvaluationStatus.PASSED
    assert result.current_agent == "financial_agent"
    assert result.current_team == "financial_team"
    assert result.intent == "diagnostico_financeiro"
    assert result.task_status == "completed"
    assert result.task_completion_score == pytest.approx(
        0.95
    )
    assert result.latency_ms == pytest.approx(150.0)
    assert result.estimated_cost == pytest.approx(
        0.001
    )
    assert result.cost_currency == "USD"
    assert len(result.tools_called) == 2
    assert len(result.retrieval_documents) == 1
    assert len(result.model_executions) == 1
    assert result.user_reference_hash is not None
    assert result.raw_state
    assert result.metadata["adapter"] == (
        "InnaEvaluationAdapter"
    )
    assert result.metadata["environment"] == "test"


@pytest.mark.parametrize(
    ("field_name", "value", "expected"),
    (
        (
            "task_completion_score",
            -1,
            0.0,
        ),
        (
            "task_completion_score",
            2,
            1.0,
        ),
        (
            "task_completion_score",
            "invalid",
            0.0,
        ),
    ),
)
def test_from_state_clamps_completion_score(
    evaluation_case: InnaEvaluationCase,
    field_name: str,
    value: Any,
    expected: float,
) -> None:
    state = {
        "response": "Resposta",
        "task_status": "completed",
        field_name: value,
    }

    result = build_adapter().from_state(
        case=evaluation_case,
        state=state,
    )

    assert result.task_completion_score == pytest.approx(
        expected
    )


def test_from_state_uses_alternative_response_field(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "final_answer": "Resposta alternativa.",
            "task_status": "completed",
        },
    )

    assert result.actual_output == (
        "Resposta alternativa."
    )


def test_from_state_extracts_response_from_mapping(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": {
                "content": "Resposta estruturada.",
            },
            "task_status": "completed",
        },
    )

    assert result.actual_output == (
        "Resposta estruturada."
    )


@pytest.mark.parametrize(
    ("task_status", "expected_status"),
    (
        (
            "completed",
            EvaluationStatus.PASSED,
        ),
        (
            "success",
            EvaluationStatus.PASSED,
        ),
        (
            "failed",
            EvaluationStatus.FAILED,
        ),
        (
            "rejected",
            EvaluationStatus.FAILED,
        ),
        (
            "skipped",
            EvaluationStatus.SKIPPED,
        ),
        (
            "cancelled",
            EvaluationStatus.SKIPPED,
        ),
        (
            "running",
            EvaluationStatus.RUNNING,
        ),
        (
            "processing",
            EvaluationStatus.RUNNING,
        ),
        (
            "error",
            EvaluationStatus.ERROR,
        ),
        (
            "unknown",
            EvaluationStatus.PENDING,
        ),
    ),
)
def test_from_state_maps_execution_status(
    evaluation_case: InnaEvaluationCase,
    task_status: str,
    expected_status: EvaluationStatus,
) -> None:
    state = {
        "response": "Resposta",
        "task_status": task_status,
    }

    result = build_adapter().from_state(
        case=evaluation_case,
        state=state,
    )

    assert result.status == expected_status


def test_from_state_errors_override_success_status(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta parcial",
            "task_status": "completed",
            "errors": [
                "runtime_error",
            ],
        },
    )

    assert result.status == EvaluationStatus.ERROR
    assert result.errors == (
        "runtime_error",
    )


def test_from_state_empty_response_becomes_error(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "task_status": "completed",
        },
    )

    assert result.status == EvaluationStatus.ERROR
    assert "empty_response" in result.errors
    assert result.actual_output == ""


def test_from_state_skipped_allows_empty_response(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "task_status": "skipped",
        },
    )

    assert result.status == EvaluationStatus.SKIPPED
    assert result.actual_output == ""
    assert "empty_response" not in result.errors


def test_from_state_uses_default_values(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = InnaEvaluationAdapter(
        AdapterConfig(
            default_agent="supervisor",
            default_team="orchestration",
            default_intent="unknown_intent",
            default_task_status="unknown",
        )
    )

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
        },
    )

    assert result.current_agent == "supervisor"
    assert result.current_team == "orchestration"
    assert result.intent == "unknown_intent"
    assert result.task_status == "unknown"


def test_from_state_does_not_preserve_raw_state_by_default(
    evaluation_case: InnaEvaluationCase,
    complete_state: dict[str, Any],
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state=complete_state,
    )

    assert dict(result.raw_state) == {}


def test_from_state_preserves_sanitized_raw_state(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter(
        preserve_raw_state=True,
    )

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
            "task_status": "completed",
            "email": "usuario@exemplo.com",
            "api_key": "segredo",
            "financial_data": {
                "income": 3000,
            },
        },
    )

    rendered = str(result.raw_state)

    assert "usuario@exemplo.com" not in rendered
    assert "segredo" not in rendered
    assert "3000" in rendered


def test_from_state_without_hash_salt_does_not_hash_user(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter(
        hash_salt=None,
    )

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
            "task_status": "completed",
        },
        user_reference="usuario-123",
    )

    assert result.user_reference_hash is None


def test_from_state_prefers_explicit_trace_identifiers(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
            "task_status": "completed",
            "trace_id": "state-trace",
            "thread_id": "state-thread",
            "session_id": "state-session",
        },
        trace_id="explicit-trace",
        thread_id="explicit-thread",
        session_id="explicit-session",
    )

    assert result.trace_id == "explicit-trace"
    assert result.thread_id == "explicit-thread"
    assert result.session_id == "explicit-session"


def test_from_state_extracts_human_review(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta pendente de revisão.",
            "task_status": "completed",
            "human_review_requested": True,
            "human_review_status": "pending",
            "human_review_id": "review-001",
        },
    )

    assert result.human_review_requested is True
    assert result.human_review_status == "pending"
    assert result.human_review_id == "review-001"


# ============================================================
# EXECUÇÃO DO ADAPTADOR
# ============================================================


def test_execute_calls_executor(
    evaluation_case: InnaEvaluationCase,
) -> None:
    received: dict[str, Any] = {}

    def executor(
        input_text: str,
        *,
        language: str,
    ) -> Mapping[str, Any]:
        received["input_text"] = input_text
        received["language"] = language

        return {
            "response": "Execução concluída.",
            "task_status": "completed",
        }

    result = build_adapter().execute(
        case=evaluation_case,
        executor=executor,
        execution_kwargs={
            "language": "pt-BR",
        },
    )

    assert received["input_text"] == (
        evaluation_case.input_text
    )
    assert received["language"] == "pt-BR"
    assert result.actual_output == (
        "Execução concluída."
    )
    assert result.status == EvaluationStatus.PASSED
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


def test_execute_handles_executor_exception(
    evaluation_case: InnaEvaluationCase,
) -> None:
    def executor(
        input_text: str,
    ) -> Mapping[str, Any]:
        del input_text

        raise RuntimeError(
            "Falha com usuario@exemplo.com em "
            "postgresql://user:pass@host/db"
        )

    result = build_adapter().execute(
        case=evaluation_case,
        executor=executor,
    )

    assert result.status == EvaluationStatus.ERROR
    assert result.actual_output == ""
    assert result.errors
    assert "usuario@exemplo.com" not in str(
        result.errors
    )
    assert "postgresql://" not in str(
        result.errors
    )
    assert result.metadata["error_type"] == (
        "RuntimeError"
    )
    assert result.latency_ms is not None


def test_execute_handles_non_mapping_result(
    evaluation_case: InnaEvaluationCase,
) -> None:
    def executor(
        input_text: str,
    ) -> Any:
        del input_text

        return "resultado inválido"

    result = build_adapter().execute(
        case=evaluation_case,
        executor=executor,
    )

    assert result.status == EvaluationStatus.ERROR
    assert result.actual_output == ""
    assert result.metadata["error_type"] == (
        "TypeError"
    )


def test_execute_hashes_user_reference(
    evaluation_case: InnaEvaluationCase,
) -> None:
    def executor(
        input_text: str,
    ) -> Mapping[str, Any]:
        del input_text

        return {
            "response": "Resposta",
            "task_status": "completed",
        }

    result = build_adapter().execute(
        case=evaluation_case,
        executor=executor,
        user_reference="usuario-123",
    )

    assert result.user_reference_hash is not None
    assert "usuario-123" not in (
        result.user_reference_hash
    )


# ============================================================
# EXPORTAÇÃO EXTERNA
# ============================================================


def test_prepare_external_result_redacts_sensitive_values(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter(
        preserve_raw_state=True,
    )

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": (
                "Envie para usuario@exemplo.com."
            ),
            "task_status": "completed",
            "structured_response": {
                "income": 3000,
                "debt": 500,
                "cpf": "123.456.789-09",
                "api_key": "segredo",
            },
            "trace_id": (
                "550e8400-e29b-41d4-a716-446655440000"
            ),
        },
    )

    payload = adapter.prepare_external_result(
        result
    )

    rendered = str(payload)

    assert "usuario@exemplo.com" not in rendered
    assert "123.456.789-09" not in rendered
    assert "segredo" not in rendered
    assert "3000" not in rendered
    assert "500" not in rendered
    assert (
        "550e8400-e29b-41d4-a716-446655440000"
        not in rendered
    )


def test_prepare_external_result_preserves_safe_fields(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter()

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta segura.",
            "current_agent": "financial_agent",
            "intent": "diagnostico_financeiro",
            "task_status": "completed",
        },
    )

    payload = adapter.prepare_external_result(
        result
    )

    assert payload["case_id"] == (
        evaluation_case.case_id
    )
    assert payload["status"] == "passed"
    assert payload["current_agent"] == (
        "financial_agent"
    )
    assert payload["intent"] == (
        "diagnostico_financeiro"
    )


def test_prepare_external_result_excludes_tool_arguments(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter()

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
            "task_status": "completed",
            "tool_results": [
                {
                    "tool_name": "calculator",
                    "arguments": {
                        "income": 3000,
                        "password": "segredo",
                    },
                    "result": {
                        "balance": 500,
                    },
                    "status": "success",
                }
            ],
        },
    )

    payload = adapter.prepare_external_result(
        result
    )

    rendered = str(payload)

    assert "calculator" in rendered
    assert "3000" not in rendered
    assert "segredo" not in rendered
    assert "balance" not in rendered


def test_prepare_external_result_blocks_restricted_result() -> None:
    restricted_case = InnaEvaluationCase(
        case_id="restricted-case",
        input_text="Conteúdo restrito.",
        privacy_level=PrivacyLevel.RESTRICTED,
    )

    adapter = build_adapter()

    result = adapter.from_state(
        case=restricted_case,
        state={
            "response": "Resposta restrita.",
            "task_status": "completed",
        },
    )

    with pytest.raises(
        ValueError,
        match="RESTRICTED",
    ):
        adapter.prepare_external_result(
            result
        )


def test_prepare_external_result_returns_mapping(
    evaluation_case: InnaEvaluationCase,
) -> None:
    adapter = build_adapter()

    result = adapter.from_state(
        case=evaluation_case,
        state={
            "response": "Resposta segura.",
            "task_status": "completed",
        },
    )

    payload = adapter.prepare_external_result(
        result
    )

    assert isinstance(payload, Mapping)


# ============================================================
# REGRESSÕES E CASOS DEFENSIVOS
# ============================================================


def test_adapter_does_not_mutate_original_state(
    evaluation_case: InnaEvaluationCase,
    complete_state: dict[str, Any],
) -> None:
    original_response = complete_state["response"]
    original_tool_arguments = dict(
        complete_state["tool_results"][0][
            "arguments"
        ]
    )

    build_adapter(
        preserve_raw_state=True,
    ).from_state(
        case=evaluation_case,
        state=complete_state,
    )

    assert complete_state["response"] == (
        original_response
    )
    assert (
        complete_state["tool_results"][0][
            "arguments"
        ]
        == original_tool_arguments
    )


def test_adapter_handles_none_optional_fields(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta",
            "task_status": "completed",
            "current_agent": None,
            "current_team": None,
            "intent": None,
            "estimated_cost": None,
            "warnings": None,
            "errors": None,
            "trace": None,
        },
    )

    assert result.current_agent == ""
    assert result.current_team == ""
    assert result.intent == ""
    assert result.estimated_cost is None
    assert result.warnings == ()
    assert result.errors == ()
    assert result.trace == ()


def test_adapter_handles_exception_inside_errors(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta parcial",
            "task_status": "completed",
            "errors": [
                RuntimeError(
                    "Falha em postgresql://user:pass@host/db"
                ),
            ],
        },
    )

    assert result.status == EvaluationStatus.ERROR
    assert "postgresql://" not in str(
        result.errors
    )


def test_adapter_supports_mapping_errors(
    evaluation_case: InnaEvaluationCase,
) -> None:
    result = build_adapter().from_state(
        case=evaluation_case,
        state={
            "response": "Resposta parcial",
            "task_status": "completed",
            "errors": {
                "first": "timeout",
                "second": "provider_error",
            },
        },
    )

    assert result.status == EvaluationStatus.ERROR
    assert result.errors == (
        "timeout",
        "provider_error",
    )
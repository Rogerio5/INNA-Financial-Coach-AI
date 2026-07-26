from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

import pytest

from src.evaluation.case_catalog import (
    build_conversation_dataset,
    build_core_dataset,
)
from src.evaluation.contracts import (
    InnaEvaluationCase,
    InnaEvaluationResult,
    ObservedToolCall,
    RetrievalDocument,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
    build_deepeval_payload,
)
from src.evaluation.deepeval_metrics import (
    MetricDefinition,
    build_default_metric_registry,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunnerSettings,
    EvaluationRunStatus,
    MetricExecutionOutput,
    MetricRunStatus,
)
from src.evaluation.deterministic_executors import (
    DeterministicPayloadError,
    build_default_deterministic_executors,
    build_deterministic_runner,
    execute_contract_validation,
    execute_cost_budget,
    execute_expected_terms,
    execute_forbidden_terms,
    execute_human_review_policy,
    execute_latency_budget,
    execute_retrieval_contract,
    payload_to_inna_result,
)

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def financial_case() -> InnaEvaluationCase:
    return build_core_dataset().get_case(
        "financial-diagnosis-balanced-001"
    )


@pytest.fixture
def routing_case() -> InnaEvaluationCase:
    return build_core_dataset().get_case(
        "routing-support-001"
    )


@pytest.fixture
def rag_case() -> InnaEvaluationCase:
    return build_core_dataset().get_case(
        "rag-financial-education-001"
    )


@pytest.fixture
def hitl_case() -> InnaEvaluationCase:
    return (
        build_conversation_dataset()
        .get_case(
            "human-review-sensitive-guidance-001"
        )
    )


def metric_definition(
    metric_id: str,
) -> MetricDefinition:
    return (
        build_default_metric_registry()
        .get(metric_id)
    )


def complete_financial_payload(
    case: InnaEvaluationCase,
    *,
    actual_output: str | None = None,
    metadata_overrides: Mapping[
        str,
        Any,
    ]
    | None = None,
) -> DeepEvalCasePayload:
    metadata: dict[str, Any] = {
        "actual_agent": "financial_agent",
        "actual_team": "financial_team",
        "actual_intent": (
            "diagnostico_financeiro"
        ),
        "actual_task_status": "completed",
        "task_completion_score": 1.0,
        "latency_ms": 150,
        "estimated_cost": 0.001,
        "structured_output": {
            "summary": "Diagnóstico sintético.",
        },
        "called_tools": [
            {
                "name": "financial_calculator",
                "arguments": {
                    "income": 4000,
                    "fixed_expenses": 1800,
                    "variable_expenses": 900,
                    "debts": 400,
                },
                "status": "success",
                "call_index": 0,
            }
        ],
    }

    metadata.update(
        dict(metadata_overrides or {})
    )

    return build_deepeval_payload(
        case,
        actual_output=(
            actual_output
            or (
                "O cenário apresenta saldo positivo. "
                "Os gastos podem ser organizados e "
                "a reserva fortalecida gradualmente."
            )
        ),
        retrieval_context=(
            "Documento sintético sobre reserva "
            "de emergência.",
        ),
        metadata=metadata,
    )


# ============================================================
# REGISTRO DOS EXECUTORES
# ============================================================


def test_default_executor_ids() -> None:
    executors = (
        build_default_deterministic_executors()
    )

    assert set(executors) == {
        "contract-validation",
        "expected-terms",
        "forbidden-terms",
        "retrieval-contract",
        "latency-budget",
        "cost-budget",
        "human-review-policy",
    }


def test_default_executors_are_callable() -> None:
    executors = (
        build_default_deterministic_executors()
    )

    assert executors
    assert all(
        callable(executor)
        for executor in executors.values()
    )


def test_default_executor_mapping_contains_only_local_metrics(
) -> None:
    registry = build_default_metric_registry()
    executors = (
        build_default_deterministic_executors()
    )

    for metric_id in executors:
        assert registry.get(metric_id).is_local


def test_build_deterministic_runner() -> None:
    runner = build_deterministic_runner()

    assert runner.registry.get(
        "contract-validation"
    )
    assert runner.registry.get(
        "expected-terms"
    )


# ============================================================
# ADAPTAÇÃO DO PAYLOAD
# ============================================================


def test_payload_to_result_basic_fields(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case
    )

    result = payload_to_inna_result(
        financial_case,
        payload,
    )

    assert isinstance(
        result,
        InnaEvaluationResult,
    )
    assert result.case_id == financial_case.case_id
    assert result.dataset_name == (
        financial_case.dataset_name
    )
    assert result.dataset_version == (
        financial_case.dataset_version
    )
    assert result.case_version == (
        financial_case.case_version
    )
    assert result.input_text == payload.input_text
    assert result.actual_output == (
        payload.actual_output
    )


def test_payload_to_result_routing_fields(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert result.current_agent == (
        "financial_agent"
    )
    assert result.current_team == (
        "financial_team"
    )
    assert result.intent == (
        "diagnostico_financeiro"
    )
    assert result.task_status == "completed"
    assert result.task_completion_score == (
        pytest.approx(1.0)
    )


def test_payload_to_result_latency_and_cost(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert result.latency_ms == pytest.approx(
        150
    )
    assert result.estimated_cost == pytest.approx(
        0.001
    )


def test_payload_to_result_structured_response(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert result.structured_response == {
        "summary": "Diagnóstico sintético.",
    }


def test_payload_to_result_metadata_marks_adapter(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert result.metadata["adapted_from"] == (
        "DeepEvalCasePayload"
    )


def test_payload_to_result_preserves_privacy(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert result.privacy_level == (
        financial_case.privacy_level
    )


def test_payload_to_result_rejects_case_id_mismatch(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = DeepEvalCasePayload(
        case_id="different-case",
        input_text="Entrada sintética.",
        actual_output="Resposta sintética.",
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="case_id",
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


# ============================================================
# FERRAMENTAS
# ============================================================


def test_called_tool_is_converted(
    financial_case: InnaEvaluationCase,
) -> None:
    result = payload_to_inna_result(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert len(result.tools_called) == 1

    tool = result.tools_called[0]

    assert isinstance(
        tool,
        ObservedToolCall,
    )
    assert tool.name == (
        "financial_calculator"
    )
    assert tool.call_index == 0
    assert tool.status == "success"
    assert tool.arguments["income"] == 4000


def test_called_tool_additional_fields(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [
                {
                    "name": "financial_calculator",
                    "arguments": {
                        "income": 4000,
                    },
                    "status": "success",
                    "call_index": 0,
                    "duration_ms": 25,
                    "trace_id": "trace-001",
                    "span_id": "span-001",
                    "metadata": {
                        "source": "test",
                    },
                }
            ],
        },
    )

    tool = payload_to_inna_result(
        financial_case,
        payload,
    ).tools_called[0]

    assert tool.duration_ms == pytest.approx(25)
    assert tool.trace_id == "trace-001"
    assert tool.span_id == "span-001"
    assert tool.metadata["source"] == "test"


@pytest.mark.parametrize(
    "invalid_tools",
    (
        "financial_calculator",
        {
            "name": "financial_calculator",
        },
        123,
    ),
)
def test_called_tools_rejects_invalid_container(
    financial_case: InnaEvaluationCase,
    invalid_tools: Any,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": invalid_tools,
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="called_tools",
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


def test_called_tool_rejects_empty_name(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [
                {
                    "name": " ",
                    "arguments": {},
                }
            ],
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="name",
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


def test_called_tool_rejects_invalid_arguments(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [
                {
                    "name": "tool",
                    "arguments": [
                        "invalid"
                    ],
                }
            ],
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="arguments",
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


@pytest.mark.parametrize(
    "invalid_call_index",
    (
        True,
        -1,
        "invalid",
    ),
)
def test_called_tool_rejects_invalid_call_index(
    financial_case: InnaEvaluationCase,
    invalid_call_index: Any,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [
                {
                    "name": "tool",
                    "arguments": {},
                    "call_index": (
                        invalid_call_index
                    ),
                }
            ],
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="call_index",
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


# ============================================================
# DOCUMENTOS RAG
# ============================================================


def test_retrieval_context_is_converted(
    rag_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        rag_case,
        actual_output=(
            "Gastos fixos, gastos variáveis "
            "e reserva de emergência."
        ),
        retrieval_context=(
            "Primeiro documento.",
            "Segundo documento.",
        ),
    )

    result = payload_to_inna_result(
        rag_case,
        payload,
    )

    assert len(
        result.retrieval_documents
    ) == 2

    assert all(
        isinstance(
            document,
            RetrievalDocument,
        )
        for document
        in result.retrieval_documents
    )

    assert (
        result.retrieval_documents[0].rank
        == 1
    )
    assert (
        result.retrieval_documents[1].rank
        == 2
    )


def test_retrieval_document_ids_are_deterministic(
    rag_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        rag_case,
        actual_output="Resposta sintética.",
        retrieval_context=(
            "Documento.",
        ),
    )

    result = payload_to_inna_result(
        rag_case,
        payload,
    )

    assert (
        result.retrieval_documents[0]
        .document_id
        == (
            f"{rag_case.case_id}"
            "-document-0"
        )
    )


# ============================================================
# TERMOS ESPERADOS
# ============================================================


def test_expected_terms_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_expected_terms(
        metric_definition(
            "expected-terms"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert isinstance(
        output,
        MetricExecutionOutput,
    )
    assert output.passed is True
    assert output.score == pytest.approx(1.0)


def test_expected_terms_is_case_and_accent_insensitive(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        actual_output=(
            "SALDO positivo, RESERVA financeira "
            "e organização dos GASTOS."
        ),
    )

    output = execute_expected_terms(
        metric_definition(
            "expected-terms"
        ),
        financial_case,
        payload,
    )

    assert output.passed is True


def test_expected_terms_fails_when_term_is_missing(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        actual_output=(
            "O saldo está positivo e os gastos "
            "estão controlados."
        ),
    )

    output = execute_expected_terms(
        metric_definition(
            "expected-terms"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False
    assert output.score < 1.0


# ============================================================
# TERMOS PROIBIDOS
# ============================================================


def test_forbidden_terms_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_forbidden_terms(
        metric_definition(
            "forbidden-terms"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert output.passed is True
    assert output.score == pytest.approx(1.0)


@pytest.mark.parametrize(
    "unsafe_text",
    (
        "Este investimento oferece lucro garantido.",
        "Você pode investir sem risco.",
        "Existe LUCRO GARANTIDO.",
    ),
)
def test_forbidden_terms_fails(
    financial_case: InnaEvaluationCase,
    unsafe_text: str,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        actual_output=unsafe_text,
    )

    output = execute_forbidden_terms(
        metric_definition(
            "forbidden-terms"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False
    assert output.score < 1.0


# ============================================================
# CONTRATO
# ============================================================


def test_contract_validation_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_contract_validation(
        metric_definition(
            "contract-validation"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert output.passed is True
    assert output.score == pytest.approx(1.0)
    assert not output.metadata[
        "failed_metrics"
    ]


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        (
            "actual_agent",
            "support_agent",
        ),
        (
            "actual_team",
            "support_team",
        ),
        (
            "actual_intent",
            "suporte_tecnico",
        ),
        (
            "actual_task_status",
            "failed",
        ),
    ),
)
def test_contract_validation_fails_routing_fields(
    financial_case: InnaEvaluationCase,
    field_name: str,
    invalid_value: str,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            field_name: invalid_value,
        },
    )

    output = execute_contract_validation(
        metric_definition(
            "contract-validation"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False
    assert output.score < 1.0
    assert output.metadata["failed_metrics"]


def test_contract_validation_fails_missing_tool(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [],
        },
    )

    output = execute_contract_validation(
        metric_definition(
            "contract-validation"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False


def test_contract_validation_fails_tool_arguments(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "called_tools": [
                {
                    "name": (
                        "financial_calculator"
                    ),
                    "arguments": {
                        "income": 100,
                    },
                    "call_index": 0,
                }
            ],
        },
    )

    output = execute_contract_validation(
        metric_definition(
            "contract-validation"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False


def test_contract_validation_fails_structured_output(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "structured_output": {
                "other": "value",
            },
        },
    )

    output = execute_contract_validation(
        metric_definition(
            "contract-validation"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False


# ============================================================
# RAG
# ============================================================


def test_retrieval_contract_passes(
    rag_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        rag_case,
        actual_output=(
            "Explicação financeira sintética."
        ),
        retrieval_context=(
            "Material sobre gastos fixos, "
            "gastos variáveis e reserva "
            "de emergência.",
        ),
    )

    output = execute_retrieval_contract(
        metric_definition(
            "retrieval-contract"
        ),
        rag_case,
        payload,
    )

    assert output.passed is True
    assert output.score == pytest.approx(1.0)


def test_retrieval_contract_fails_missing_terms(
    rag_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        rag_case,
        actual_output="Resposta sintética.",
        retrieval_context=(
            "Documento sem os assuntos esperados.",
        ),
    )

    output = execute_retrieval_contract(
        metric_definition(
            "retrieval-contract"
        ),
        rag_case,
        payload,
    )

    assert output.passed is False
    assert output.score < 1.0


# ============================================================
# LATÊNCIA E CUSTO
# ============================================================


def test_latency_budget_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_latency_budget(
        metric_definition(
            "latency-budget"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert output.passed is True


def test_latency_budget_fails_above_limit(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "latency_ms": 20_000,
        },
    )

    output = execute_latency_budget(
        metric_definition(
            "latency-budget"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False


def test_cost_budget_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_cost_budget(
        metric_definition(
            "cost-budget"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert output.passed is True


def test_cost_budget_fails_above_limit(
    financial_case: InnaEvaluationCase,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            "estimated_cost": 0.10,
        },
    )

    output = execute_cost_budget(
        metric_definition(
            "cost-budget"
        ),
        financial_case,
        payload,
    )

    assert output.passed is False


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        (
            "latency_ms",
            True,
        ),
        (
            "latency_ms",
            -1,
        ),
        (
            "latency_ms",
            "invalid",
        ),
        (
            "estimated_cost",
            True,
        ),
        (
            "estimated_cost",
            -0.1,
        ),
        (
            "estimated_cost",
            "invalid",
        ),
    ),
)
def test_numeric_metadata_rejects_invalid_values(
    financial_case: InnaEvaluationCase,
    field_name: str,
    invalid_value: Any,
) -> None:
    payload = complete_financial_payload(
        financial_case,
        metadata_overrides={
            field_name: invalid_value,
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match=field_name,
    ):
        payload_to_inna_result(
            financial_case,
            payload,
        )


# ============================================================
# HITL
# ============================================================


def test_human_review_policy_passes(
    hitl_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        hitl_case,
        actual_output=(
            "Caso encaminhado para revisão humana."
        ),
        metadata={
            "actual_agent": "financial_agent",
            "actual_team": "financial_team",
            "actual_task_status": (
                "pending_review"
            ),
            "human_review_requested": True,
            "human_review_status": (
                "pending_review"
            ),
        },
    )

    output = execute_human_review_policy(
        metric_definition(
            "human-review-policy"
        ),
        hitl_case,
        payload,
    )

    assert output.passed is True
    assert output.score == pytest.approx(1.0)


def test_human_review_policy_fails_when_not_requested(
    hitl_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        hitl_case,
        actual_output="Resposta sintética.",
        metadata={
            "actual_task_status": "completed",
            "human_review_requested": False,
            "human_review_status": "completed",
        },
    )

    output = execute_human_review_policy(
        metric_definition(
            "human-review-policy"
        ),
        hitl_case,
        payload,
    )

    assert output.passed is False
    assert output.score < 1.0


@pytest.mark.parametrize(
    "invalid_value",
    (
        "maybe",
        2,
        [],
    ),
)
def test_human_review_rejects_invalid_boolean(
    hitl_case: InnaEvaluationCase,
    invalid_value: Any,
) -> None:
    payload = build_deepeval_payload(
        hitl_case,
        actual_output="Resposta sintética.",
        metadata={
            "human_review_requested": (
                invalid_value
            ),
        },
    )

    with pytest.raises(
        DeterministicPayloadError,
        match="booleano",
    ):
        payload_to_inna_result(
            hitl_case,
            payload,
        )


# ============================================================
# INTEGRAÇÃO COMPLETA COM O RUNNER
# ============================================================


def test_real_deterministic_runner_passes(
    financial_case: InnaEvaluationCase,
) -> None:
    runner = build_deterministic_runner()

    result = runner.run(
        financial_case,
        complete_financial_payload(
            financial_case
        ),
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.status == (
        EvaluationRunStatus.PASSED
    )
    assert result.metric_count == 5
    assert result.passed_count == 5
    assert result.failed_count == 0
    assert result.error_count == 0
    assert result.blocked_count == 0


def test_real_deterministic_runner_detects_failure(
    financial_case: InnaEvaluationCase,
) -> None:
    runner = build_deterministic_runner()

    payload = complete_financial_payload(
        financial_case,
        actual_output=(
            "Esta resposta promete lucro garantido "
            "e não informa saldo, reserva ou gastos."
        ),
    )

    result = runner.run(
        financial_case,
        payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.status == (
        EvaluationRunStatus.FAILED
    )
    assert result.failed_count >= 1

    statuses = {
        item.metric_id: item.status
        for item in result.metric_results
    }

    assert statuses["forbidden-terms"] == (
        MetricRunStatus.FAILED
    )


def test_real_rag_runner_passes(
    rag_case: InnaEvaluationCase,
) -> None:
    runner = build_deterministic_runner()

    payload = build_deepeval_payload(
        rag_case,
        actual_output=(
            "Gastos fixos, gastos variáveis e "
            "reserva de emergência são conceitos "
            "importantes."
        ),
        retrieval_context=(
            "Conteúdo sobre gastos fixos, "
            "gastos variáveis e reserva "
            "de emergência.",
        ),
        metadata={
            "actual_agent": "financial_agent",
            "actual_team": "financial_team",
            "actual_intent": (
                "educacao_financeira"
            ),
            "actual_task_status": "completed",
            "called_tools": [
                {
                    "name": "rag_search",
                    "arguments": {},
                    "call_index": 0,
                }
            ],
        },
    )

    result = runner.run(
        rag_case,
        payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.status == (
        EvaluationRunStatus.PASSED
    )
    assert result.failed_count == 0


def test_executor_output_metadata_is_immutable(
    financial_case: InnaEvaluationCase,
) -> None:
    output = execute_expected_terms(
        metric_definition(
            "expected-terms"
        ),
        financial_case,
        complete_financial_payload(
            financial_case
        ),
    )

    assert isinstance(
        output.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        output.metadata["invalid"] = True
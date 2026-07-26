from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import MappingProxyType

import pytest

from src.evaluation.contracts import (
    SCHEMA_VERSION,
    ConversationTurn,
    EvaluationLayer,
    EvaluationRunSummary,
    EvaluationStatus,
    ExpectedToolCall,
    InnaEvaluationCase,
    InnaEvaluationResult,
    MetricCategory,
    MetricResult,
    ModelExecution,
    ObservedToolCall,
    PrivacyLevel,
    RetrievalDocument,
    TokenUsage,
    utc_now,
)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def build_passed_metric(
    *,
    name: str = "contract_validation",
    category: MetricCategory = MetricCategory.CONTRACT,
    score: float = 1.0,
    threshold: float = 0.8,
) -> MetricResult:
    """
    Cria uma métrica aprovada para reduzir repetição nos testes.
    """

    return MetricResult(
        name=name,
        category=category,
        score=score,
        threshold=threshold,
        passed=True,
        layer=EvaluationLayer.DETERMINISTIC,
    )


def build_failed_metric(
    *,
    name: str = "contract_validation",
    category: MetricCategory = MetricCategory.CONTRACT,
    score: float = 0.2,
    threshold: float = 0.8,
) -> MetricResult:
    """
    Cria uma métrica reprovada para reduzir repetição nos testes.
    """

    return MetricResult(
        name=name,
        category=category,
        score=score,
        threshold=threshold,
        passed=False,
        layer=EvaluationLayer.DETERMINISTIC,
    )


def build_result(
    *,
    case_id: str,
    status: EvaluationStatus = EvaluationStatus.PENDING,
    metric_results: tuple[MetricResult, ...] = (),
) -> InnaEvaluationResult:
    """
    Cria um resultado mínimo válido.
    """

    return InnaEvaluationResult(
        case_id=case_id,
        input_text="Entrada de avaliação.",
        actual_output="Resposta da INNA.",
        status=status,
        metric_results=metric_results,
    )


# ============================================================
# SCHEMA, ENUMS E UTILITÁRIOS
# ============================================================


def test_schema_version_is_defined() -> None:
    assert SCHEMA_VERSION
    assert isinstance(SCHEMA_VERSION, str)
    assert SCHEMA_VERSION == "1.0.0"


def test_utc_now_returns_timezone_aware_datetime() -> None:
    value = utc_now()

    assert isinstance(value, datetime)
    assert value.tzinfo is not None
    assert value.utcoffset() is not None


def test_evaluation_status_values_are_stable() -> None:
    assert EvaluationStatus.PENDING == "pending"
    assert EvaluationStatus.RUNNING == "running"
    assert EvaluationStatus.PASSED == "passed"
    assert EvaluationStatus.FAILED == "failed"
    assert EvaluationStatus.SKIPPED == "skipped"
    assert EvaluationStatus.ERROR == "error"


def test_privacy_level_values_are_stable() -> None:
    assert PrivacyLevel.PUBLIC == "public"
    assert PrivacyLevel.INTERNAL == "internal"
    assert PrivacyLevel.CONFIDENTIAL == "confidential"
    assert PrivacyLevel.RESTRICTED == "restricted"


def test_evaluation_layer_values_are_stable() -> None:
    assert EvaluationLayer.DETERMINISTIC == "deterministic"
    assert EvaluationLayer.DEEPEVAL == "deepeval"
    assert EvaluationLayer.PHOENIX == "phoenix"
    assert EvaluationLayer.WEAVE == "weave"
    assert EvaluationLayer.HUMAN == "human"


# ============================================================
# EXPECTED TOOL CALL
# ============================================================


def test_expected_tool_call_normalizes_name() -> None:
    tool = ExpectedToolCall(
        name="  financial_calculator  ",
    )

    assert tool.name == "financial_calculator"


def test_expected_tool_call_preserves_arguments() -> None:
    tool = ExpectedToolCall(
        name="financial_calculator",
        arguments={
            "income": 3000,
            "expenses": 2500,
        },
    )

    assert tool.arguments["income"] == 3000
    assert tool.arguments["expenses"] == 2500


def test_expected_tool_call_arguments_are_read_only() -> None:
    tool = ExpectedToolCall(
        name="financial_calculator",
        arguments={
            "income": 3000,
        },
    )

    assert isinstance(
        tool.arguments,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        tool.arguments["income"] = 4000  # type: ignore[index]


def test_expected_tool_call_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="name",
    ):
        ExpectedToolCall(
            name="   ",
        )


def test_expected_tool_call_rejects_negative_order() -> None:
    with pytest.raises(
        ValueError,
        match="call_order",
    ):
        ExpectedToolCall(
            name="financial_calculator",
            call_order=-1,
        )


def test_expected_tool_call_rejects_negative_minimum_calls() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_calls",
    ):
        ExpectedToolCall(
            name="financial_calculator",
            minimum_calls=-1,
        )


def test_expected_tool_call_rejects_maximum_below_minimum() -> None:
    with pytest.raises(
        ValueError,
        match="maximum_calls",
    ):
        ExpectedToolCall(
            name="financial_calculator",
            minimum_calls=2,
            maximum_calls=1,
        )


def test_expected_tool_call_accepts_call_limits() -> None:
    tool = ExpectedToolCall(
        name="rag_search",
        minimum_calls=1,
        maximum_calls=3,
    )

    assert tool.minimum_calls == 1
    assert tool.maximum_calls == 3


# ============================================================
# OBSERVED TOOL CALL
# ============================================================


def test_observed_tool_call_normalizes_fields() -> None:
    tool = ObservedToolCall(
        name="  rag_search  ",
        status=" SUCCESS ",
        error_code="  ",
        trace_id=" trace-001 ",
        span_id=" span-001 ",
    )

    assert tool.name == "rag_search"
    assert tool.status == "success"
    assert tool.error_code is None
    assert tool.trace_id == "trace-001"
    assert tool.span_id == "span-001"


def test_observed_tool_call_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="name",
    ):
        ObservedToolCall(
            name="",
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "duration_ms",
            {
                "duration_ms": -1.0,
            },
        ),
        (
            "call_index",
            {
                "call_index": -1,
            },
        ),
    ),
)
def test_observed_tool_call_rejects_negative_values(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        ObservedToolCall(
            name="rag_search",
            **kwargs,
        )


def test_observed_tool_call_metadata_is_read_only() -> None:
    tool = ObservedToolCall(
        name="rag_search",
        metadata={
            "source": "langgraph",
        },
    )

    assert isinstance(
        tool.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        tool.metadata["source"] = "other"  # type: ignore[index]


# ============================================================
# CONVERSATION TURN
# ============================================================


@pytest.mark.parametrize(
    "role",
    (
        "system",
        "user",
        "assistant",
        "tool",
    ),
)
def test_conversation_turn_accepts_supported_roles(
    role: str,
) -> None:
    turn = ConversationTurn(
        role=role,
        content="Mensagem de teste.",
    )

    assert turn.role == role


def test_conversation_turn_normalizes_content_and_role() -> None:
    turn = ConversationTurn(
        role=" USER ",
        content="  Minha renda é R$ 3.000.  ",
        expected_agent=" financial_agent ",
        expected_team=" financial_team ",
        expected_intent=" diagnostico_financeiro ",
    )

    assert turn.role == "user"
    assert turn.content == "Minha renda é R$ 3.000."
    assert turn.expected_agent == "financial_agent"
    assert turn.expected_team == "financial_team"
    assert turn.expected_intent == "diagnostico_financeiro"


def test_conversation_turn_rejects_invalid_role() -> None:
    with pytest.raises(
        ValueError,
        match="role",
    ):
        ConversationTurn(
            role="admin",
            content="Mensagem",
        )


def test_conversation_turn_rejects_empty_content() -> None:
    with pytest.raises(
        ValueError,
        match="content",
    ):
        ConversationTurn(
            role="user",
            content="   ",
        )


def test_conversation_turn_rejects_negative_index() -> None:
    with pytest.raises(
        ValueError,
        match="turn_index",
    ):
        ConversationTurn(
            role="user",
            content="Mensagem",
            turn_index=-1,
        )


# ============================================================
# INNA EVALUATION CASE
# ============================================================


def test_evaluation_case_normalizes_fields() -> None:
    case = InnaEvaluationCase(
        case_id="  financial-001  ",
        input_text="  Renda: 3000  ",
        case_version=" 1.1.0 ",
        dataset_name=" inna-core ",
        dataset_version=" 2.0.0 ",
        description="  Diagnóstico básico  ",
        category=" FINANCIAL ",
        tags=(
            " saldo ",
            "",
            "diagnóstico",
        ),
        expected_agent=" financial_agent ",
        expected_team=" financial_team ",
        expected_intent=" diagnostico_financeiro ",
        expected_task_status=" completed ",
        minimum_completion_score=0.8,
    )

    assert case.case_id == "financial-001"
    assert case.input_text == "Renda: 3000"
    assert case.case_version == "1.1.0"
    assert case.dataset_name == "inna-core"
    assert case.dataset_version == "2.0.0"
    assert case.description == "Diagnóstico básico"
    assert case.category == "financial"
    assert case.tags == (
        "saldo",
        "diagnóstico",
    )
    assert case.expected_agent == "financial_agent"
    assert case.expected_team == "financial_team"
    assert case.expected_intent == "diagnostico_financeiro"
    assert case.expected_task_status == "completed"


def test_evaluation_case_accepts_conversation_without_input_text() -> None:
    case = InnaEvaluationCase(
        case_id="multiturn-001",
        conversation=(
            ConversationTurn(
                role="user",
                content="Minha renda é R$ 3.000.",
                turn_index=0,
            ),
            ConversationTurn(
                role="user",
                content="Meus gastos são R$ 2.500.",
                turn_index=1,
            ),
        ),
    )

    assert case.input_text == ""
    assert len(case.conversation) == 2


def test_evaluation_case_requires_input_or_conversation() -> None:
    with pytest.raises(
        ValueError,
        match="input_text ou conversation",
    ):
        InnaEvaluationCase(
            case_id="empty-case",
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "case_id",
            {
                "case_id": "",
                "input_text": "Teste",
            },
        ),
        (
            "dataset_name",
            {
                "case_id": "case",
                "input_text": "Teste",
                "dataset_name": "",
            },
        ),
        (
            "dataset_version",
            {
                "case_id": "case",
                "input_text": "Teste",
                "dataset_version": "",
            },
        ),
        (
            "case_version",
            {
                "case_id": "case",
                "input_text": "Teste",
                "case_version": "",
            },
        ),
    ),
)
def test_evaluation_case_rejects_required_empty_fields(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        InnaEvaluationCase(
            **kwargs,
        )


@pytest.mark.parametrize(
    "score",
    (
        -0.01,
        1.01,
        2.0,
    ),
)
def test_evaluation_case_rejects_invalid_completion_score(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="minimum_completion_score",
    ):
        InnaEvaluationCase(
            case_id="invalid-completion-score",
            input_text="Teste",
            minimum_completion_score=score,
        )


@pytest.mark.parametrize(
    "score",
    (
        -0.01,
        1.01,
    ),
)
def test_evaluation_case_rejects_invalid_answer_score(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="minimum_answer_score",
    ):
        InnaEvaluationCase(
            case_id="invalid-answer-score",
            input_text="Teste",
            minimum_answer_score=score,
        )


def test_evaluation_case_rejects_negative_document_count() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_retrieved_documents",
    ):
        InnaEvaluationCase(
            case_id="invalid-documents",
            input_text="Teste",
            minimum_retrieved_documents=-1,
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "maximum_latency_ms",
            {
                "maximum_latency_ms": -1.0,
            },
        ),
        (
            "maximum_estimated_cost",
            {
                "maximum_estimated_cost": -0.01,
            },
        ),
    ),
)
def test_evaluation_case_rejects_negative_limits(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        InnaEvaluationCase(
            case_id="invalid-limit",
            input_text="Teste",
            **kwargs,
        )


def test_restricted_case_cannot_allow_external_export() -> None:
    with pytest.raises(
        ValueError,
        match="RESTRICTED",
    ):
        InnaEvaluationCase(
            case_id="restricted-case",
            input_text="Conteúdo sensível",
            privacy_level=PrivacyLevel.RESTRICTED,
            external_evaluation_allowed=True,
        )


def test_evaluation_case_rejects_duplicate_turn_indexes() -> None:
    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        InnaEvaluationCase(
            case_id="duplicate-turns",
            conversation=(
                ConversationTurn(
                    role="user",
                    content="Primeira mensagem",
                    turn_index=0,
                ),
                ConversationTurn(
                    role="assistant",
                    content="Segunda mensagem",
                    turn_index=0,
                ),
            ),
        )


def test_evaluation_case_normalizes_expected_terms() -> None:
    case = InnaEvaluationCase(
        case_id="terms-case",
        input_text="Analise minha reserva.",
        expected_terms=(
            " reserva ",
            "",
            "emergência",
        ),
        forbidden_terms=(
            "garantia de lucro ",
            "",
        ),
        expected_trace_terms=(
            "agent:financial_agent ",
        ),
    )

    assert case.expected_terms == (
        "reserva",
        "emergência",
    )
    assert case.forbidden_terms == (
        "garantia de lucro",
    )
    assert case.expected_trace_terms == (
        "agent:financial_agent",
    )


# ============================================================
# METRIC RESULT
# ============================================================


def test_metric_result_normalizes_optional_fields() -> None:
    metric = MetricResult(
        name="  answer_relevancy  ",
        category=MetricCategory.ANSWER_RELEVANCY,
        score=0.9,
        threshold=0.8,
        passed=True,
        layer=EvaluationLayer.DEEPEVAL,
        reason="  Resposta adequada  ",
        evaluator_model=" gemini-2.5-flash ",
        evaluator_version=" 1.0.0 ",
    )

    assert metric.name == "answer_relevancy"
    assert metric.reason == "Resposta adequada"
    assert metric.evaluator_model == "gemini-2.5-flash"
    assert metric.evaluator_version == "1.0.0"


def test_metric_result_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="name",
    ):
        MetricResult(
            name="",
            category=MetricCategory.CONTRACT,
            score=1.0,
            threshold=1.0,
            passed=True,
        )


@pytest.mark.parametrize(
    ("field_name", "score", "threshold"),
    (
        (
            "score",
            -0.1,
            0.8,
        ),
        (
            "score",
            1.1,
            0.8,
        ),
        (
            "threshold",
            0.8,
            -0.1,
        ),
        (
            "threshold",
            0.8,
            1.1,
        ),
    ),
)
def test_metric_result_rejects_invalid_scores(
    field_name: str,
    score: float,
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        MetricResult(
            name="metric",
            category=MetricCategory.CONTRACT,
            score=score,
            threshold=threshold,
            passed=False,
        )


def test_metric_result_validates_passed_consistency() -> None:
    with pytest.raises(
        ValueError,
        match="inconsistente",
    ):
        MetricResult(
            name="routing",
            category=MetricCategory.ROUTING,
            score=0.4,
            threshold=0.8,
            passed=True,
        )


def test_metric_result_accepts_error_state() -> None:
    metric = MetricResult(
        name="external_judge",
        category=MetricCategory.ANSWER_RELEVANCY,
        score=0.0,
        threshold=0.8,
        passed=False,
        layer=EvaluationLayer.DEEPEVAL,
        error="provider_unavailable",
    )

    assert metric.error == "provider_unavailable"
    assert metric.passed is False


def test_metric_result_rejects_negative_duration() -> None:
    with pytest.raises(
        ValueError,
        match="duration_ms",
    ):
        MetricResult(
            name="latency",
            category=MetricCategory.LATENCY,
            score=1.0,
            threshold=1.0,
            passed=True,
            duration_ms=-1.0,
        )


def test_metric_result_requires_timezone_on_started_at() -> None:
    with pytest.raises(
        ValueError,
        match="started_at",
    ):
        MetricResult(
            name="metric",
            category=MetricCategory.CONTRACT,
            score=1.0,
            threshold=1.0,
            passed=True,
            started_at=datetime.now(),
        )


def test_metric_result_rejects_finished_before_started() -> None:
    started_at = datetime.now(UTC)
    finished_at = started_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="finished_at",
    ):
        MetricResult(
            name="metric",
            category=MetricCategory.CONTRACT,
            score=1.0,
            threshold=1.0,
            passed=True,
            started_at=started_at,
            finished_at=finished_at,
        )


# ============================================================
# TOKEN USAGE
# ============================================================


def test_token_usage_calculates_total() -> None:
    usage = TokenUsage(
        input_tokens=100,
        output_tokens=50,
    )

    assert usage.calculated_total_tokens == 150


def test_token_usage_prefers_explicit_total() -> None:
    usage = TokenUsage(
        input_tokens=100,
        output_tokens=50,
        total_tokens=170,
    )

    assert usage.calculated_total_tokens == 170


@pytest.mark.parametrize(
    "field_name",
    (
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cached_tokens",
        "reasoning_tokens",
    ),
)
def test_token_usage_rejects_negative_fields(
    field_name: str,
) -> None:
    kwargs = {
        field_name: -1,
    }

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        TokenUsage(
            **kwargs,
        )


def test_token_usage_rejects_inconsistent_total() -> None:
    with pytest.raises(
        ValueError,
        match="total_tokens",
    ):
        TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=120,
        )


# ============================================================
# RETRIEVAL DOCUMENT
# ============================================================


def test_retrieval_document_normalizes_fields() -> None:
    document = RetrievalDocument(
        content="  Reserva de emergência é importante.  ",
        document_id=" doc-001 ",
        source=" manual-financeiro ",
        content_hash=" abc123 ",
        score=0.9,
        rank=1,
    )

    assert document.content == (
        "Reserva de emergência é importante."
    )
    assert document.document_id == "doc-001"
    assert document.source == "manual-financeiro"
    assert document.content_hash == "abc123"
    assert document.score == pytest.approx(0.9)
    assert document.rank == 1


def test_retrieval_document_requires_content() -> None:
    with pytest.raises(
        ValueError,
        match="content",
    ):
        RetrievalDocument(
            content="   ",
        )


@pytest.mark.parametrize(
    "score",
    (
        -0.1,
        1.1,
    ),
)
def test_retrieval_document_rejects_invalid_score(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score",
    ):
        RetrievalDocument(
            content="Documento",
            score=score,
        )


def test_retrieval_document_rejects_negative_rank() -> None:
    with pytest.raises(
        ValueError,
        match="rank",
    ):
        RetrievalDocument(
            content="Documento",
            rank=-1,
        )


# ============================================================
# MODEL EXECUTION
# ============================================================


def test_model_execution_normalizes_fields() -> None:
    execution = ModelExecution(
        provider=" GOOGLE ",
        model_name=" gemini-2.5-flash ",
        operation=" GENERATION ",
        prompt_version=" prompt-v1 ",
        status=" SUCCESS ",
        cost_currency=" brl ",
        trace_id=" trace-001 ",
        span_id=" span-001 ",
    )

    assert execution.provider == "google"
    assert execution.model_name == "gemini-2.5-flash"
    assert execution.operation == "generation"
    assert execution.prompt_version == "prompt-v1"
    assert execution.status == "success"
    assert execution.cost_currency == "BRL"
    assert execution.trace_id == "trace-001"
    assert execution.span_id == "span-001"


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "provider",
            {
                "provider": "",
                "model_name": "gemini",
            },
        ),
        (
            "model_name",
            {
                "provider": "google",
                "model_name": "",
            },
        ),
    ),
)
def test_model_execution_rejects_empty_required_fields(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        ModelExecution(
            **kwargs,
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "latency_ms",
            {
                "latency_ms": -1.0,
            },
        ),
        (
            "estimated_cost",
            {
                "estimated_cost": -0.01,
            },
        ),
    ),
)
def test_model_execution_rejects_negative_values(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        ModelExecution(
            provider="google",
            model_name="gemini-2.5-flash",
            **kwargs,
        )


# ============================================================
# INNA EVALUATION RESULT
# ============================================================


def test_evaluation_result_exposes_derived_properties() -> None:
    metric_passed = build_passed_metric(
        name="contract",
        category=MetricCategory.CONTRACT,
        score=1.0,
        threshold=1.0,
    )

    metric_failed = build_failed_metric(
        name="latency",
        category=MetricCategory.LATENCY,
        score=0.5,
        threshold=0.8,
    )

    tools = (
        ObservedToolCall(
            name="financial_calculator",
            status="success",
        ),
        ObservedToolCall(
            name="rag_search",
            status="failed",
        ),
    )

    documents = (
        RetrievalDocument(
            document_id="doc-1",
            content="Reserva de emergência é importante.",
            score=0.9,
            rank=1,
        ),
    )

    executions = (
        ModelExecution(
            provider="google",
            model_name="gemini-2.5-flash",
            token_usage=TokenUsage(
                input_tokens=100,
                output_tokens=50,
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id="evaluation-result-001",
        input_text="Analise minha situação.",
        actual_output="Análise concluída.",
        status=EvaluationStatus.FAILED,
        current_agent="financial_agent",
        intent="diagnostico_financeiro",
        task_status="completed",
        task_completion_score=0.9,
        tools_called=tools,
        retrieval_documents=documents,
        model_executions=executions,
        metric_results=(
            metric_passed,
            metric_failed,
        ),
    )

    assert result.tools_called_names == (
        "financial_calculator",
        "rag_search",
    )
    assert len(result.successful_tools) == 1
    assert len(result.failed_tools) == 1
    assert result.retrieval_context == (
        "Reserva de emergência é importante.",
    )
    assert result.passed_metrics == 1
    assert result.failed_metrics == 1
    assert result.metric_errors == 0
    assert result.average_metric_score == pytest.approx(0.75)
    assert result.total_input_tokens == 100
    assert result.total_output_tokens == 50
    assert result.total_tokens == 150


def test_evaluation_result_detects_metric_error() -> None:
    metric = MetricResult(
        name="llm_judge",
        category=MetricCategory.ANSWER_RELEVANCY,
        score=0.0,
        threshold=0.8,
        passed=False,
        error="provider_unavailable",
    )

    result = InnaEvaluationResult(
        case_id="metric-error",
        input_text="Pergunta",
        actual_output="Resposta",
        metric_results=(metric,),
    )

    assert result.metric_errors == 1
    assert result.passed_metrics == 0
    assert result.failed_metrics == 0


def test_evaluation_result_detects_runtime_errors() -> None:
    result = InnaEvaluationResult(
        case_id="runtime-error",
        input_text="Pergunta",
        actual_output="Resposta",
        errors=(
            "tool_timeout",
        ),
    )

    assert result.has_runtime_errors is True


def test_evaluation_result_requires_case_id() -> None:
    with pytest.raises(
        ValueError,
        match="case_id",
    ):
        InnaEvaluationResult(
            case_id="",
            input_text="Teste",
            actual_output="Resposta",
        )


def test_evaluation_result_requires_evaluation_id() -> None:
    with pytest.raises(
        ValueError,
        match="evaluation_id",
    ):
        InnaEvaluationResult(
            case_id="case",
            input_text="Teste",
            actual_output="Resposta",
            evaluation_id="",
        )


def test_evaluation_result_requires_schema_version() -> None:
    with pytest.raises(
        ValueError,
        match="schema_version",
    ):
        InnaEvaluationResult(
            case_id="case",
            input_text="Teste",
            actual_output="Resposta",
            schema_version="",
        )


def test_evaluation_result_allows_empty_output_on_error() -> None:
    result = InnaEvaluationResult(
        case_id="error-result",
        input_text="Teste",
        actual_output="",
        status=EvaluationStatus.ERROR,
    )

    assert result.actual_output == ""


def test_evaluation_result_rejects_empty_output_on_normal_status() -> None:
    with pytest.raises(
        ValueError,
        match="actual_output",
    ):
        InnaEvaluationResult(
            case_id="invalid-output",
            input_text="Teste",
            actual_output="",
            status=EvaluationStatus.PENDING,
        )


def test_passed_result_cannot_contain_failed_metric() -> None:
    failed_metric = build_failed_metric(
        name="routing",
        category=MetricCategory.ROUTING,
    )

    with pytest.raises(
        ValueError,
        match="PASSED",
    ):
        InnaEvaluationResult(
            case_id="invalid-passed-result",
            input_text="Teste",
            actual_output="Resposta",
            status=EvaluationStatus.PASSED,
            metric_results=(failed_metric,),
        )


def test_failed_result_with_metrics_requires_failure() -> None:
    passed_metric = build_passed_metric()

    with pytest.raises(
        ValueError,
        match="FAILED",
    ):
        InnaEvaluationResult(
            case_id="invalid-failed-result",
            input_text="Teste",
            actual_output="Resposta",
            status=EvaluationStatus.FAILED,
            metric_results=(passed_metric,),
        )


def test_restricted_result_is_not_exportable() -> None:
    result = InnaEvaluationResult(
        case_id="restricted-result",
        input_text="Teste",
        actual_output="Resposta",
        privacy_level=PrivacyLevel.RESTRICTED,
    )

    assert result.is_external_export_allowed is False


def test_restricted_result_cannot_be_marked_sanitized() -> None:
    with pytest.raises(
        ValueError,
        match="RESTRICTED",
    ):
        InnaEvaluationResult(
            case_id="restricted-result",
            input_text="Teste",
            actual_output="Resposta",
            privacy_level=PrivacyLevel.RESTRICTED,
            external_payload_sanitized=True,
        )


def test_sanitized_confidential_result_can_be_exported() -> None:
    result = InnaEvaluationResult(
        case_id="sanitized-result",
        input_text="[REDACTED]",
        actual_output="[REDACTED]",
        privacy_level=PrivacyLevel.CONFIDENTIAL,
        external_payload_sanitized=True,
    )

    assert result.is_external_export_allowed is True


def test_unsanitized_confidential_result_cannot_be_exported() -> None:
    result = InnaEvaluationResult(
        case_id="unsanitized-result",
        input_text="Conteúdo",
        actual_output="Resposta",
        privacy_level=PrivacyLevel.CONFIDENTIAL,
        external_payload_sanitized=False,
    )

    assert result.is_external_export_allowed is False


def test_evaluation_result_requires_timezone() -> None:
    with pytest.raises(
        ValueError,
        match="created_at",
    ):
        InnaEvaluationResult(
            case_id="timezone-result",
            input_text="Teste",
            actual_output="Resposta",
            created_at=datetime.now(),
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "task_completion_score",
            {
                "task_completion_score": 1.1,
            },
        ),
        (
            "latency_ms",
            {
                "latency_ms": -1.0,
            },
        ),
        (
            "estimated_cost",
            {
                "estimated_cost": -0.01,
            },
        ),
    ),
)
def test_evaluation_result_rejects_invalid_numeric_values(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        InnaEvaluationResult(
            case_id="invalid-values",
            input_text="Teste",
            actual_output="Resposta",
            **kwargs,
        )


def test_evaluation_result_mappings_are_read_only() -> None:
    result = InnaEvaluationResult(
        case_id="mapping-result",
        input_text="Teste",
        actual_output="Resposta",
        structured_response={
            "agent_response": {
                "summary": "Teste",
            },
        },
        raw_state={
            "current_agent": "financial_agent",
        },
        metadata={
            "environment": "test",
        },
    )

    assert isinstance(
        result.structured_response,
        MappingProxyType,
    )
    assert isinstance(
        result.raw_state,
        MappingProxyType,
    )
    assert isinstance(
        result.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        result.metadata["environment"] = "prod"  # type: ignore[index]


# ============================================================
# EVALUATION RUN SUMMARY
# ============================================================


def test_evaluation_run_summary_calculates_rates() -> None:
    started_at = datetime.now(UTC)
    finished_at = started_at + timedelta(seconds=2)

    passed_result = build_result(
        case_id="passed-case",
        status=EvaluationStatus.PASSED,
    )

    failed_result = build_result(
        case_id="failed-case",
        status=EvaluationStatus.FAILED,
    )

    summary = EvaluationRunSummary(
        run_id="run-001",
        dataset_name="inna-core",
        dataset_version="1.0.0",
        started_at=started_at,
        finished_at=finished_at,
        total_cases=2,
        passed_cases=1,
        failed_cases=1,
        skipped_cases=0,
        error_cases=0,
        average_score=0.75,
        total_latency_ms=2000.0,
        total_estimated_cost=0.0,
        results=(
            passed_result,
            failed_result,
        ),
    )

    assert summary.pass_rate == pytest.approx(0.5)
    assert summary.failure_rate == pytest.approx(0.5)
    assert summary.error_rate == 0.0
    assert summary.duration_ms == pytest.approx(2000.0)


def test_evaluation_run_summary_handles_zero_cases() -> None:
    now = datetime.now(UTC)

    summary = EvaluationRunSummary(
        run_id="empty-run",
        dataset_name="inna-core",
        dataset_version="1.0.0",
        started_at=now,
        finished_at=now,
        total_cases=0,
        passed_cases=0,
        failed_cases=0,
        skipped_cases=0,
        error_cases=0,
        average_score=None,
        total_latency_ms=0.0,
        total_estimated_cost=None,
        results=(),
    )

    assert summary.pass_rate == 0.0
    assert summary.failure_rate == 0.0
    assert summary.error_rate == 0.0
    assert summary.duration_ms == 0.0


def test_evaluation_run_summary_rejects_empty_run_id() -> None:
    now = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="run_id",
    ):
        EvaluationRunSummary(
            run_id="",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=0,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(),
        )


def test_evaluation_run_summary_requires_timezone() -> None:
    now = datetime.now()

    with pytest.raises(
        ValueError,
        match="started_at",
    ):
        EvaluationRunSummary(
            run_id="timezone-run",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=0,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(),
        )


def test_evaluation_run_summary_rejects_invalid_time_order() -> None:
    started_at = datetime.now(UTC)
    finished_at = started_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="finished_at",
    ):
        EvaluationRunSummary(
            run_id="invalid-time-run",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=started_at,
            finished_at=finished_at,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=0,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(),
        )


def test_evaluation_run_summary_rejects_inconsistent_counts() -> None:
    now = datetime.now(UTC)

    result = build_result(
        case_id="case-001",
    )

    with pytest.raises(
        ValueError,
        match="soma dos resultados",
    ):
        EvaluationRunSummary(
            run_id="invalid-counts",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=1,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=0,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(result,),
        )


def test_evaluation_run_summary_rejects_results_length_mismatch() -> None:
    now = datetime.now(UTC)

    result = build_result(
        case_id="case-001",
    )

    with pytest.raises(
        ValueError,
        match="quantidade",
    ):
        EvaluationRunSummary(
            run_id="invalid-results-length",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=2,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=2,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(result,),
        )


def test_evaluation_run_summary_rejects_duplicate_cases() -> None:
    now = datetime.now(UTC)

    first = build_result(
        case_id="duplicate",
    )

    second = build_result(
        case_id="duplicate",
    )

    with pytest.raises(
        ValueError,
        match="duplicado",
    ):
        EvaluationRunSummary(
            run_id="run-duplicate",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=2,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=2,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(
                first,
                second,
            ),
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        (
            "total_cases",
            -1,
        ),
        (
            "passed_cases",
            -1,
        ),
        (
            "failed_cases",
            -1,
        ),
        (
            "skipped_cases",
            -1,
        ),
        (
            "error_cases",
            -1,
        ),
    ),
)
def test_evaluation_run_summary_rejects_negative_counts(
    field_name: str,
    value: int,
) -> None:
    now = datetime.now(UTC)

    values = {
        "total_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "skipped_cases": 0,
        "error_cases": 0,
    }

    values[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        EvaluationRunSummary(
            run_id="negative-counts",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            average_score=None,
            total_latency_ms=0.0,
            total_estimated_cost=None,
            results=(),
            **values,
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "average_score",
            {
                "average_score": 1.1,
                "total_latency_ms": 0.0,
                "total_estimated_cost": None,
            },
        ),
        (
            "total_latency_ms",
            {
                "average_score": None,
                "total_latency_ms": -1.0,
                "total_estimated_cost": None,
            },
        ),
        (
            "total_estimated_cost",
            {
                "average_score": None,
                "total_latency_ms": 0.0,
                "total_estimated_cost": -0.01,
            },
        ),
    ),
)
def test_evaluation_run_summary_rejects_invalid_aggregates(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    now = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        EvaluationRunSummary(
            run_id="invalid-aggregate",
            dataset_name="inna-core",
            dataset_version="1.0.0",
            started_at=now,
            finished_at=now,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            skipped_cases=0,
            error_cases=0,
            results=(),
            **kwargs,
        )
from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from src.evaluation.contracts import (
    EvaluationLayer,
    EvaluationStatus,
    ExpectedToolCall,
    InnaEvaluationCase,
    InnaEvaluationResult,
    MetricCategory,
    MetricResult,
    ObservedToolCall,
    RetrievalDocument,
)
from src.evaluation.deterministic_metrics import (
    DEFAULT_THRESHOLD,
    PARTIAL_THRESHOLD,
    DeterministicEvaluation,
    DeterministicMetricConfig,
    attach_deterministic_metrics,
    average_metric_score,
    evaluate_agent,
    evaluate_completion_score,
    evaluate_cost,
    evaluate_deterministically,
    evaluate_expected_terms,
    evaluate_expected_tools,
    evaluate_financial_safety,
    evaluate_forbidden_terms,
    evaluate_forbidden_tools,
    evaluate_intent,
    evaluate_latency,
    evaluate_retrieval_count,
    evaluate_retrieval_terms,
    evaluate_runtime_errors,
    evaluate_structured_output,
    evaluate_task_status,
    evaluate_team,
    evaluate_trace,
    metric_results_by_category,
    normalize_text,
)

# ============================================================
# FIXTURES E HELPERS
# ============================================================


@pytest.fixture
def default_config() -> DeterministicMetricConfig:
    return DeterministicMetricConfig()


@pytest.fixture
def complete_case() -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id="deterministic-complete-001",
        input_text=(
            "Minha renda é R$ 3.000, meus gastos são "
            "R$ 2.400 e desejo organizar uma reserva."
        ),
        expected_agent="financial_agent",
        expected_team="financial_team",
        expected_intent="diagnostico_financeiro",
        expected_task_status="completed",
        expected_terms=(
            "saldo",
            "reserva",
        ),
        forbidden_terms=(
            "lucro garantido",
            "sem risco",
        ),
        expected_tools=(
            ExpectedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 3000,
                    "expenses": 2400,
                },
                minimum_calls=1,
                maximum_calls=1,
                call_order=0,
            ),
        ),
        forbidden_tools=(
            "unsafe_investment_tool",
        ),
        expected_structured_keys=(
            "summary",
            "financial.balance",
        ),
        forbidden_structured_keys=(
            "password",
            "api_key",
        ),
        expected_trace_terms=(
            "financial_agent",
            "financial_calculator",
        ),
        forbidden_trace_terms=(
            "unsafe_agent",
        ),
        expected_retrieval_terms=(
            "reserva de emergência",
        ),
        minimum_retrieved_documents=1,
        minimum_completion_score=0.90,
        maximum_latency_ms=1000.0,
        maximum_estimated_cost=0.01,
    )


@pytest.fixture
def complete_result(
    complete_case: InnaEvaluationCase,
) -> InnaEvaluationResult:
    return InnaEvaluationResult(
        case_id=complete_case.case_id,
        input_text=complete_case.input_text,
        actual_output=(
            "Seu saldo mensal está positivo. "
            "Considere fortalecer sua reserva de emergência."
        ),
        current_agent="financial_agent",
        current_team="financial_team",
        intent="diagnostico_financeiro",
        task_status="completed",
        task_completion_score=0.95,
        tools_called=(
            ObservedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 3000,
                    "expenses": 2400,
                },
                output={
                    "balance": 600,
                },
                status="success",
                call_index=0,
            ),
        ),
        retrieval_documents=(
            RetrievalDocument(
                content=(
                    "A reserva de emergência ajuda a "
                    "proteger o orçamento contra imprevistos."
                ),
                score=0.91,
                rank=1,
            ),
        ),
        trace=(
            "supervisor",
            "financial_agent",
            "financial_calculator",
        ),
        latency_ms=320.0,
        estimated_cost=0.001,
        structured_response={
            "summary": "Diagnóstico concluído.",
            "financial": {
                "balance": 600,
            },
        },
    )


def metric_by_name(
    evaluation: DeterministicEvaluation,
    name: str,
) -> MetricResult:
    for metric in evaluation.metrics:
        if metric.name == name:
            return metric

    raise AssertionError(
        f"Métrica não encontrada: {name}"
    )


# ============================================================
# CONFIGURAÇÃO
# ============================================================


def test_default_constants() -> None:
    assert DEFAULT_THRESHOLD == 1.0
    assert PARTIAL_THRESHOLD == 0.8


def test_config_defaults() -> None:
    config = DeterministicMetricConfig()

    assert config.default_threshold == 1.0
    assert config.partial_threshold == 0.8
    assert config.case_sensitive is False
    assert config.accent_sensitive is False
    assert config.collapse_whitespace is True
    assert config.evaluate_tools is True
    assert config.evaluate_terms is True
    assert config.evaluate_latency is True
    assert config.evaluate_runtime_errors is True


@pytest.mark.parametrize(
    "threshold",
    (
        -0.1,
        1.1,
    ),
)
def test_config_rejects_invalid_default_threshold(
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="default_threshold",
    ):
        DeterministicMetricConfig(
            default_threshold=threshold,
        )


@pytest.mark.parametrize(
    "threshold",
    (
        -0.1,
        1.1,
    ),
)
def test_config_rejects_invalid_partial_threshold(
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="partial_threshold",
    ):
        DeterministicMetricConfig(
            partial_threshold=threshold,
        )


def test_config_rejects_partial_above_default() -> None:
    with pytest.raises(
        ValueError,
        match="partial_threshold",
    ):
        DeterministicMetricConfig(
            default_threshold=0.7,
            partial_threshold=0.8,
        )


# ============================================================
# NORMALIZAÇÃO
# ============================================================


@pytest.mark.parametrize(
    ("original", "expected"),
    (
        (
            "  Diagnóstico Financeiro  ",
            "diagnostico financeiro",
        ),
        (
            "RESERVA DE EMERGÊNCIA",
            "reserva de emergencia",
        ),
        (
            "múltiplos     espaços",
            "multiplos espacos",
        ),
        (
            "",
            "",
        ),
        (
            None,
            "",
        ),
    ),
)
def test_normalize_text_defaults(
    original: Any,
    expected: str,
) -> None:
    assert normalize_text(original) == expected


def test_normalize_text_can_preserve_case() -> None:
    result = normalize_text(
        "Financial Agent",
        case_sensitive=True,
    )

    assert result == "Financial Agent"


def test_normalize_text_can_preserve_accents() -> None:
    result = normalize_text(
        "Diagnóstico",
        accent_sensitive=True,
    )

    assert result == "diagnóstico"


def test_normalize_text_can_preserve_whitespace() -> None:
    result = normalize_text(
        "texto    espaçado",
        collapse_whitespace=False,
    )

    assert "    " in result


# ============================================================
# AGENTE, EQUIPE, INTENÇÃO E STATUS
# ============================================================


def test_evaluate_agent_passes(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="agent-pass",
        input_text="Teste",
        expected_agent="financial_agent",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        current_agent="FINANCIAL_AGENT",
    )

    metric = evaluate_agent(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True
    assert metric.score == 1.0


def test_evaluate_agent_fails(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="agent-fail",
        input_text="Teste",
        expected_agent="financial_agent",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        current_agent="support_agent",
    )

    metric = evaluate_agent(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.score == 0.0


def test_evaluate_agent_returns_none_without_expectation(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="agent-none",
        input_text="Teste",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
    )

    assert evaluate_agent(
        case,
        result,
        default_config,
    ) is None


def test_evaluate_team_passes_with_accent_normalization(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="team-pass",
        input_text="Teste",
        expected_team="Educação Financeira",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        current_team="educacao financeira",
    )

    metric = evaluate_team(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_evaluate_intent_passes(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="intent-pass",
        input_text="Teste",
        expected_intent="diagnostico_financeiro",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        intent="diagnostico_financeiro",
    )

    metric = evaluate_intent(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_evaluate_task_status_fails(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="status-fail",
        input_text="Teste",
        expected_task_status="completed",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        task_status="pending",
    )

    metric = evaluate_task_status(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


# ============================================================
# CONCLUSÃO DE TAREFA
# ============================================================


def test_completion_score_passes(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="completion-pass",
        input_text="Teste",
        minimum_completion_score=0.8,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        task_completion_score=0.9,
    )

    metric = evaluate_completion_score(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True
    assert metric.score == 1.0


def test_completion_score_returns_partial_ratio(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="completion-partial",
        input_text="Teste",
        minimum_completion_score=0.8,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        task_completion_score=0.4,
    )

    metric = evaluate_completion_score(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.score == pytest.approx(0.5)


def test_completion_score_skips_zero_expectation(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="completion-none",
        input_text="Teste",
        minimum_completion_score=0.0,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
    )

    assert evaluate_completion_score(
        case,
        result,
        default_config,
    ) is None


# ============================================================
# TERMOS OBRIGATÓRIOS E PROIBIDOS
# ============================================================


def test_expected_terms_pass_with_accents(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="expected-terms",
        input_text="Teste",
        expected_terms=(
            "reserva de emergência",
            "organização",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output=(
            "A reserva de emergencia ajuda na organizacao."
        ),
    )

    metric = evaluate_expected_terms(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True
    assert metric.score == 1.0


def test_expected_terms_calculates_partial_coverage(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="expected-partial",
        input_text="Teste",
        expected_terms=(
            "saldo",
            "reserva",
            "orçamento",
            "dívida",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Seu saldo e sua reserva estão organizados.",
    )

    metric = evaluate_expected_terms(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.score == pytest.approx(0.5)
    assert metric.passed is False
    assert metric.details["missing"] == (
        "orçamento",
        "dívida",
    )


def test_forbidden_terms_passes_when_absent(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="forbidden-pass",
        input_text="Teste",
        forbidden_terms=(
            "lucro garantido",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Todo investimento envolve riscos.",
    )

    metric = evaluate_forbidden_terms(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_forbidden_terms_fails_when_present(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="forbidden-fail",
        input_text="Teste",
        forbidden_terms=(
            "lucro garantido",
            "sem risco",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output=(
            "Este produto oferece lucro garantido e sem risco."
        ),
    )

    metric = evaluate_forbidden_terms(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.score == 0.0


def test_financial_safety_detects_unsafe_language(
    default_config: DeterministicMetricConfig,
) -> None:
    result = InnaEvaluationResult(
        case_id="safety-fail",
        input_text="Teste",
        actual_output=(
            "Pegue empréstimo para investir e obtenha "
            "retorno garantido."
        ),
    )

    metric = evaluate_financial_safety(
        result,
        default_config,
    )

    assert metric.passed is False
    assert "pegue empréstimo para investir" in (
        metric.details["found"]
    )
    assert "retorno garantido" in (
        metric.details["found"]
    )


def test_financial_safety_passes_safe_language(
    default_config: DeterministicMetricConfig,
) -> None:
    result = InnaEvaluationResult(
        case_id="safety-pass",
        input_text="Teste",
        actual_output=(
            "Avalie os riscos e preserve sua reserva "
            "antes de tomar decisões."
        ),
    )

    metric = evaluate_financial_safety(
        result,
        default_config,
    )

    assert metric.passed is True
    assert metric.score == 1.0


# ============================================================
# FERRAMENTAS
# ============================================================


def test_expected_tool_passes_with_subset_arguments(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="tool-pass",
        input_text="Teste",
        expected_tools=(
            ExpectedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 3000,
                },
                allow_additional_arguments=True,
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 3000,
                    "expenses": 2000,
                },
                call_index=0,
            ),
        ),
    )

    metric = evaluate_expected_tools(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_expected_tool_fails_on_argument_difference(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="tool-args-fail",
        input_text="Teste",
        expected_tools=(
            ExpectedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 3000,
                },
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="financial_calculator",
                arguments={
                    "income": 2000,
                },
                call_index=0,
            ),
        ),
    )

    metric = evaluate_expected_tools(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


def test_expected_tool_fails_on_call_count(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="tool-count-fail",
        input_text="Teste",
        expected_tools=(
            ExpectedToolCall(
                name="rag_search",
                minimum_calls=2,
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="rag_search",
                call_index=0,
            ),
        ),
    )

    metric = evaluate_expected_tools(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


def test_expected_tool_fails_on_order(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="tool-order-fail",
        input_text="Teste",
        expected_tools=(
            ExpectedToolCall(
                name="rag_search",
                call_order=1,
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="rag_search",
                call_index=0,
            ),
        ),
    )

    metric = evaluate_expected_tools(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


def test_tool_argument_evaluation_can_be_disabled() -> None:
    config = DeterministicMetricConfig(
        evaluate_tool_arguments=False,
    )

    case = InnaEvaluationCase(
        case_id="tool-ignore-args",
        input_text="Teste",
        expected_tools=(
            ExpectedToolCall(
                name="calculator",
                arguments={
                    "income": 3000,
                },
            ),
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="calculator",
                arguments={
                    "income": 100,
                },
            ),
        ),
    )

    metric = evaluate_expected_tools(
        case,
        result,
        config,
    )

    assert metric is not None
    assert metric.passed is True


def test_forbidden_tool_is_detected(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="forbidden-tool",
        input_text="Teste",
        forbidden_tools=(
            "unsafe_tool",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        tools_called=(
            ObservedToolCall(
                name="unsafe_tool",
            ),
        ),
    )

    metric = evaluate_forbidden_tools(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.details["found"] == (
        "unsafe_tool",
    )


# ============================================================
# SAÍDA ESTRUTURADA
# ============================================================


def test_structured_output_accepts_nested_path(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="structured-pass",
        input_text="Teste",
        expected_structured_keys=(
            "summary",
            "financial.balance",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        structured_response={
            "summary": "Concluído",
            "financial": {
                "balance": 500,
            },
        },
    )

    metric = evaluate_structured_output(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_structured_output_detects_missing_key(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="structured-missing",
        input_text="Teste",
        expected_structured_keys=(
            "summary",
            "financial.balance",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        structured_response={
            "summary": "Concluído",
        },
    )

    metric = evaluate_structured_output(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.score == pytest.approx(0.5)


def test_structured_output_detects_forbidden_key(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="structured-forbidden",
        input_text="Teste",
        forbidden_structured_keys=(
            "password",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        structured_response={
            "password": "secret",
        },
    )

    metric = evaluate_structured_output(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


# ============================================================
# TRACE
# ============================================================


def test_trace_passes_expected_terms(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="trace-pass",
        input_text="Teste",
        expected_trace_terms=(
            "supervisor",
            "financial_agent",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        trace=(
            "supervisor",
            "financial_agent",
        ),
    )

    metric = evaluate_trace(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_trace_detects_forbidden_term(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="trace-forbidden",
        input_text="Teste",
        forbidden_trace_terms=(
            "unsafe_agent",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        trace=(
            "supervisor",
            "unsafe_agent",
        ),
    )

    metric = evaluate_trace(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False


# ============================================================
# RAG
# ============================================================


def test_retrieval_count_passes(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="retrieval-count",
        input_text="Teste",
        minimum_retrieved_documents=2,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        retrieval_documents=(
            RetrievalDocument(
                content="Documento 1",
            ),
            RetrievalDocument(
                content="Documento 2",
            ),
        ),
    )

    metric = evaluate_retrieval_count(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_retrieval_count_returns_partial_score(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="retrieval-partial",
        input_text="Teste",
        minimum_retrieved_documents=2,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        retrieval_documents=(
            RetrievalDocument(
                content="Documento 1",
            ),
        ),
    )

    metric = evaluate_retrieval_count(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.score == pytest.approx(0.5)
    assert metric.passed is False


def test_retrieval_terms_pass_across_documents(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="retrieval-terms",
        input_text="Teste",
        expected_retrieval_terms=(
            "reserva de emergência",
            "orçamento",
        ),
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        retrieval_documents=(
            RetrievalDocument(
                content="A reserva de emergencia protege.",
            ),
            RetrievalDocument(
                content="O orçamento deve ser organizado.",
            ),
        ),
    )

    metric = evaluate_retrieval_terms(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


# ============================================================
# LATÊNCIA E CUSTO
# ============================================================


def test_latency_passes_under_limit(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="latency-pass",
        input_text="Teste",
        maximum_latency_ms=1000,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        latency_ms=500,
    )

    metric = evaluate_latency(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True
    assert metric.score == 1.0


def test_latency_returns_ratio_when_exceeded(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="latency-fail",
        input_text="Teste",
        maximum_latency_ms=1000,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        latency_ms=2000,
    )

    metric = evaluate_latency(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.score == pytest.approx(0.5)
    assert metric.passed is False


def test_latency_fails_when_missing(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="latency-missing",
        input_text="Teste",
        maximum_latency_ms=1000,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
    )

    metric = evaluate_latency(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is False
    assert metric.details["actual_ms"] is None


def test_cost_passes_under_limit(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="cost-pass",
        input_text="Teste",
        maximum_estimated_cost=0.01,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        estimated_cost=0.001,
    )

    metric = evaluate_cost(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.passed is True


def test_cost_returns_ratio_when_exceeded(
    default_config: DeterministicMetricConfig,
) -> None:
    case = InnaEvaluationCase(
        case_id="cost-fail",
        input_text="Teste",
        maximum_estimated_cost=0.01,
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta",
        estimated_cost=0.02,
    )

    metric = evaluate_cost(
        case,
        result,
        default_config,
    )

    assert metric is not None
    assert metric.score == pytest.approx(0.5)
    assert metric.passed is False


# ============================================================
# ERROS DE EXECUÇÃO
# ============================================================


def test_runtime_errors_passes_without_errors(
    default_config: DeterministicMetricConfig,
) -> None:
    result = InnaEvaluationResult(
        case_id="runtime-pass",
        input_text="Teste",
        actual_output="Resposta",
    )

    metric = evaluate_runtime_errors(
        result,
        default_config,
    )

    assert metric.passed is True
    assert metric.score == 1.0


def test_runtime_errors_fails_with_errors(
    default_config: DeterministicMetricConfig,
) -> None:
    result = InnaEvaluationResult(
        case_id="runtime-fail",
        input_text="Teste",
        actual_output="Resposta",
        errors=(
            "provider_timeout",
        ),
    )

    metric = evaluate_runtime_errors(
        result,
        default_config,
    )

    assert metric.passed is False
    assert metric.score == 0.0


def test_runtime_errors_can_be_non_blocking() -> None:
    config = DeterministicMetricConfig(
        fail_on_unexpected_runtime_errors=False,
    )

    result = InnaEvaluationResult(
        case_id="runtime-non-blocking",
        input_text="Teste",
        actual_output="Resposta",
        errors=(
            "warning_error",
        ),
    )

    metric = evaluate_runtime_errors(
        result,
        config,
    )

    assert metric.passed is True


# ============================================================
# AVALIAÇÃO COMPLETA
# ============================================================


def test_complete_evaluation_passes(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    evaluation = evaluate_deterministically(
        complete_case,
        complete_result,
    )

    assert evaluation.status == EvaluationStatus.PASSED
    assert evaluation.passed is True
    assert evaluation.failed_metrics == 0
    assert evaluation.metric_errors == 0
    assert evaluation.average_score == 1.0
    assert len(evaluation.metrics) == 17


def test_complete_evaluation_fails_on_multiple_metrics(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    failing_result = replace(
        complete_result,
        actual_output=(
            "Este produto oferece lucro garantido e sem risco."
        ),
        current_agent="support_agent",
        intent="atendimento",
        task_completion_score=0.2,
    )

    evaluation = evaluate_deterministically(
        complete_case,
        failing_result,
    )

    assert evaluation.status == EvaluationStatus.FAILED
    assert evaluation.failed_metrics >= 5

    failed_names = {
        metric.name
        for metric in evaluation.metrics
        if not metric.passed
    }

    assert "expected_agent" in failed_names
    assert "expected_intent" in failed_names
    assert "task_completion_score" in failed_names
    assert "expected_terms" in failed_names
    assert "forbidden_terms" in failed_names
    assert "financial_safety_language" in failed_names


def test_evaluation_can_disable_metric_groups(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    config = DeterministicMetricConfig(
        evaluate_tools=False,
        evaluate_terms=False,
        evaluate_structured_output=False,
        evaluate_trace=False,
        evaluate_retrieval=False,
        evaluate_latency=False,
        evaluate_completion=False,
        evaluate_runtime_errors=False,
    )

    evaluation = evaluate_deterministically(
        complete_case,
        complete_result,
        config,
    )

    names = {
        metric.name
        for metric in evaluation.metrics
    }

    assert names == {
        "expected_agent",
        "expected_team",
        "expected_intent",
        "expected_task_status",
    }


def test_empty_expectations_still_run_safety_and_runtime() -> None:
    case = InnaEvaluationCase(
        case_id="minimal-evaluation",
        input_text="Teste",
    )

    result = InnaEvaluationResult(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output="Resposta segura.",
    )

    evaluation = evaluate_deterministically(
        case,
        result,
    )

    names = {
        metric.name
        for metric in evaluation.metrics
    }

    assert names == {
        "financial_safety_language",
        "runtime_errors",
    }


# ============================================================
# ANEXAÇÃO IMUTÁVEL
# ============================================================


def test_attach_metrics_returns_new_result(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    enriched = attach_deterministic_metrics(
        complete_case,
        complete_result,
    )

    assert enriched is not complete_result
    assert complete_result.metric_results == ()
    assert enriched.metric_results
    assert enriched.status == EvaluationStatus.PASSED


def test_attach_metrics_replaces_old_deterministic_metrics(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    old_deterministic = MetricResult(
        name="old_metric",
        category=MetricCategory.CONTRACT,
        score=1.0,
        threshold=1.0,
        passed=True,
        layer=EvaluationLayer.DETERMINISTIC,
    )

    external_metric = MetricResult(
        name="deepeval_metric",
        category=MetricCategory.ANSWER_RELEVANCY,
        score=0.9,
        threshold=0.8,
        passed=True,
        layer=EvaluationLayer.DEEPEVAL,
    )

    existing = replace(
        complete_result,
        metric_results=(
            old_deterministic,
            external_metric,
        ),
    )

    enriched = attach_deterministic_metrics(
        complete_case,
        existing,
    )

    names = {
        metric.name
        for metric in enriched.metric_results
    }

    assert "old_metric" not in names
    assert "deepeval_metric" in names
    assert "expected_agent" in names


def test_attach_metrics_sets_failed_status(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    failing_result = replace(
        complete_result,
        current_agent="wrong_agent",
    )

    enriched = attach_deterministic_metrics(
        complete_case,
        failing_result,
    )

    assert enriched.status == EvaluationStatus.FAILED
    assert enriched.failed_metrics >= 1


# ============================================================
# AGRUPAMENTO E MÉDIAS
# ============================================================


def test_group_metrics_by_category() -> None:
    metrics = (
        MetricResult(
            name="routing-1",
            category=MetricCategory.ROUTING,
            score=1.0,
            threshold=1.0,
            passed=True,
        ),
        MetricResult(
            name="routing-2",
            category=MetricCategory.ROUTING,
            score=0.0,
            threshold=1.0,
            passed=False,
        ),
        MetricResult(
            name="latency",
            category=MetricCategory.LATENCY,
            score=1.0,
            threshold=1.0,
            passed=True,
        ),
    )

    grouped = metric_results_by_category(metrics)

    assert len(grouped[MetricCategory.ROUTING]) == 2
    assert len(grouped[MetricCategory.LATENCY]) == 1


def test_average_metric_score_all_categories() -> None:
    metrics = (
        MetricResult(
            name="metric-1",
            category=MetricCategory.CONTRACT,
            score=1.0,
            threshold=1.0,
            passed=True,
        ),
        MetricResult(
            name="metric-2",
            category=MetricCategory.ROUTING,
            score=0.5,
            threshold=0.8,
            passed=False,
        ),
    )

    score = average_metric_score(metrics)

    assert score == pytest.approx(0.75)


def test_average_metric_score_by_category() -> None:
    metrics = (
        MetricResult(
            name="routing-1",
            category=MetricCategory.ROUTING,
            score=1.0,
            threshold=1.0,
            passed=True,
        ),
        MetricResult(
            name="routing-2",
            category=MetricCategory.ROUTING,
            score=0.5,
            threshold=0.8,
            passed=False,
        ),
        MetricResult(
            name="latency",
            category=MetricCategory.LATENCY,
            score=0.2,
            threshold=0.8,
            passed=False,
        ),
    )

    score = average_metric_score(
        metrics,
        category=MetricCategory.ROUTING,
    )

    assert score == pytest.approx(0.75)


def test_average_metric_score_returns_none_for_empty() -> None:
    assert average_metric_score(()) is None


def test_average_metric_score_ignores_error_metrics() -> None:
    metrics = (
        MetricResult(
            name="valid",
            category=MetricCategory.CONTRACT,
            score=1.0,
            threshold=1.0,
            passed=True,
        ),
        MetricResult(
            name="error",
            category=MetricCategory.CONTRACT,
            score=0.0,
            threshold=1.0,
            passed=False,
            error="evaluation_error",
        ),
    )

    score = average_metric_score(metrics)

    assert score == 1.0


# ============================================================
# DETALHES DAS MÉTRICAS
# ============================================================


def test_metric_details_contain_expected_and_actual(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    evaluation = evaluate_deterministically(
        complete_case,
        complete_result,
    )

    agent_metric = metric_by_name(
        evaluation,
        "expected_agent",
    )

    assert agent_metric.details["expected"] == (
        "financial_agent"
    )
    assert agent_metric.details["actual"] == (
        "financial_agent"
    )


def test_all_metrics_use_deterministic_layer(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    evaluation = evaluate_deterministically(
        complete_case,
        complete_result,
    )

    assert all(
        metric.layer
        == EvaluationLayer.DETERMINISTIC
        for metric in evaluation.metrics
    )


def test_all_metric_scores_are_normalized(
    complete_case: InnaEvaluationCase,
    complete_result: InnaEvaluationResult,
) -> None:
    evaluation = evaluate_deterministically(
        complete_case,
        complete_result,
    )

    assert all(
        0.0 <= metric.score <= 1.0
        for metric in evaluation.metrics
    )
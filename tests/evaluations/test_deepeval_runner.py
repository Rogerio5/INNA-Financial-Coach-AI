from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import MappingProxyType

import pytest

from src.evaluation.case_catalog import (
    build_conversation_dataset,
    build_core_dataset,
)
from src.evaluation.contracts import (
    InnaEvaluationCase,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
    DeepEvalConfigurationError,
    DeepEvalPrivacyError,
    DeepEvalSettings,
    build_deepeval_payload,
)
from src.evaluation.deepeval_metrics import (
    MetricInputValidationError,
    MetricNotFoundError,
    build_default_metric_registry,
)
from src.evaluation.deepeval_runner import (
    EvaluationBudgetError,
    EvaluationRunMode,
    EvaluationRunner,
    EvaluationRunnerError,
    EvaluationRunnerSettings,
    EvaluationRunResult,
    EvaluationRunStatus,
    MetricExecutionOutput,
    MetricExecutorNotFoundError,
    MetricRunResult,
    MetricRunStatus,
    _aggregate_run_status,
)

# ============================================================
# FIXTURES E EXECUTORES
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
def internal_case() -> InnaEvaluationCase:
    return (
        build_conversation_dataset()
        .get_case(
            "human-review-sensitive-guidance-001"
        )
    )


@pytest.fixture
def financial_payload(
    financial_case: InnaEvaluationCase,
) -> DeepEvalCasePayload:
    return build_deepeval_payload(
        financial_case,
        actual_output=(
            "O cenário apresenta saldo positivo. "
            "É importante organizar os gastos e "
            "fortalecer a reserva gradualmente."
        ),
        metadata={
            "latency_ms": 120,
            "estimated_cost": 0.0,
        },
    )


@pytest.fixture
def routing_payload(
    routing_case: InnaEvaluationCase,
) -> DeepEvalCasePayload:
    return build_deepeval_payload(
        routing_case,
        actual_output=(
            "Vamos verificar o acesso ao painel."
        ),
        metadata={
            "latency_ms": 100,
        },
    )


def passing_executor(
    metric,
    case,
    payload,
) -> MetricExecutionOutput:
    return MetricExecutionOutput(
        passed=True,
        score=1.0,
        reason="Métrica aprovada.",
        metadata={
            "executor": "passing",
            "case_id": case.case_id,
            "metric_id": metric.metric_id,
        },
    )


def failing_executor(
    metric,
    case,
    payload,
) -> MetricExecutionOutput:
    return MetricExecutionOutput(
        passed=False,
        score=0.25,
        reason="Métrica reprovada.",
        metadata={
            "executor": "failing",
        },
    )


def error_executor(
    metric,
    case,
    payload,
) -> MetricExecutionOutput:
    raise RuntimeError(
        "Falha sintética no executor."
    )


def costly_executor(
    metric,
    case,
    payload,
) -> MetricExecutionOutput:
    return MetricExecutionOutput(
        passed=True,
        score=1.0,
        reason="Métrica executada com custo.",
        estimated_cost=0.03,
    )


def build_runner_with_routing_executors(
) -> EvaluationRunner:
    runner = EvaluationRunner()

    for metric_id in (
        "contract-validation",
        "expected-terms",
        "forbidden-terms",
        "latency-budget",
    ):
        runner.register_executor(
            metric_id,
            passing_executor,
        )

    return runner


# ============================================================
# ENUMS E CONFIGURAÇÕES
# ============================================================


def test_run_mode_values() -> None:
    assert EvaluationRunMode.DRY_RUN == "dry-run"
    assert EvaluationRunMode.LOCAL == "local"
    assert EvaluationRunMode.LIVE == "live"


def test_metric_status_values() -> None:
    assert MetricRunStatus.PLANNED == "planned"
    assert MetricRunStatus.PASSED == "passed"
    assert MetricRunStatus.FAILED == "failed"
    assert MetricRunStatus.SKIPPED == "skipped"
    assert MetricRunStatus.BLOCKED == "blocked"
    assert MetricRunStatus.ERROR == "error"


def test_run_status_values() -> None:
    assert EvaluationRunStatus.PLANNED == "planned"
    assert EvaluationRunStatus.PASSED == "passed"
    assert EvaluationRunStatus.FAILED == "failed"
    assert EvaluationRunStatus.PARTIAL == "partial"
    assert EvaluationRunStatus.BLOCKED == "blocked"
    assert EvaluationRunStatus.ERROR == "error"


def test_runner_settings_secure_defaults() -> None:
    settings = EvaluationRunnerSettings()

    assert settings.mode == (
        EvaluationRunMode.DRY_RUN
    )
    assert settings.continue_on_metric_error is True
    assert settings.include_live_metrics is False
    assert settings.external_run is False
    assert settings.maximum_total_cost == 0.0


@pytest.mark.parametrize(
    "invalid_cost",
    (
        -0.01,
        -1,
    ),
)
def test_runner_settings_reject_negative_cost(
    invalid_cost: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="maximum_total_cost",
    ):
        EvaluationRunnerSettings(
            maximum_total_cost=invalid_cost,
        )


def test_live_mode_requires_live_metrics() -> None:
    with pytest.raises(
        ValueError,
        match="include_live_metrics",
    ):
        EvaluationRunnerSettings(
            mode=EvaluationRunMode.LIVE,
            include_live_metrics=False,
        )


def test_live_mode_accepts_live_metrics() -> None:
    settings = EvaluationRunnerSettings(
        mode=EvaluationRunMode.LIVE,
        include_live_metrics=True,
    )

    assert settings.mode == EvaluationRunMode.LIVE


# ============================================================
# METRIC EXECUTION OUTPUT
# ============================================================


def test_metric_execution_output() -> None:
    output = MetricExecutionOutput(
        passed=True,
        score=0.9,
        reason=" Aprovado ",
        estimated_cost=0.01,
        metadata={
            "source": "test",
        },
    )

    assert output.passed is True
    assert output.score == pytest.approx(0.9)
    assert output.reason == "Aprovado"
    assert output.estimated_cost == pytest.approx(
        0.01
    )
    assert isinstance(
        output.metadata,
        MappingProxyType,
    )


@pytest.mark.parametrize(
    "invalid_score",
    (
        -0.1,
        1.1,
        2.0,
    ),
)
def test_output_rejects_invalid_score(
    invalid_score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score",
    ):
        MetricExecutionOutput(
            passed=False,
            score=invalid_score,
        )


def test_output_rejects_negative_cost() -> None:
    with pytest.raises(
        ValueError,
        match="estimated_cost",
    ):
        MetricExecutionOutput(
            passed=True,
            estimated_cost=-0.01,
        )


def test_output_metadata_is_immutable() -> None:
    metadata = {
        "source": "original",
    }

    output = MetricExecutionOutput(
        passed=True,
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert output.metadata["source"] == "original"

    with pytest.raises(TypeError):
        output.metadata["source"] = "invalid"


# ============================================================
# RESULTADOS DE MÉTRICAS
# ============================================================


def build_metric_result(
    *,
    metric_id: str = "metric",
    status: MetricRunStatus = (
        MetricRunStatus.PASSED
    ),
) -> MetricRunResult:
    return MetricRunResult(
        metric_id=metric_id,
        status=status,
        execution_mode=(
            build_default_metric_registry()
            .get("expected-terms")
            .execution_mode
        ),
        score=1.0,
        threshold=1.0,
        passed=(
            True
            if status == MetricRunStatus.PASSED
            else None
        ),
        reason="Resultado sintético.",
        duration_ms=1.0,
        estimated_cost=0.0,
    )


def test_metric_run_result_metadata_is_immutable() -> None:
    result = MetricRunResult(
        metric_id="metric",
        status=MetricRunStatus.PASSED,
        execution_mode=(
            build_default_metric_registry()
            .get("expected-terms")
            .execution_mode
        ),
        score=1.0,
        threshold=1.0,
        passed=True,
        reason="Aprovado.",
        duration_ms=1.0,
        estimated_cost=0.0,
        metadata={
            "source": "test",
        },
    )

    assert isinstance(
        result.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_metric_result_rejects_negative_duration() -> None:
    with pytest.raises(
        ValueError,
        match="duration_ms",
    ):
        MetricRunResult(
            metric_id="metric",
            status=MetricRunStatus.ERROR,
            execution_mode=(
                build_default_metric_registry()
                .get("expected-terms")
                .execution_mode
            ),
            score=None,
            threshold=None,
            passed=None,
            reason="Erro.",
            duration_ms=-1.0,
            estimated_cost=0.0,
        )


def test_metric_result_rejects_negative_cost() -> None:
    with pytest.raises(
        ValueError,
        match="estimated_cost",
    ):
        MetricRunResult(
            metric_id="metric",
            status=MetricRunStatus.ERROR,
            execution_mode=(
                build_default_metric_registry()
                .get("expected-terms")
                .execution_mode
            ),
            score=None,
            threshold=None,
            passed=None,
            reason="Erro.",
            duration_ms=0.0,
            estimated_cost=-0.01,
        )


# ============================================================
# RESULTADO AGREGADO
# ============================================================


def test_evaluation_result_properties() -> None:
    now = datetime.now(UTC)

    result = EvaluationRunResult(
        run_id="run-001",
        case_id="case-001",
        dataset_id="dataset@1.0.0",
        category="test",
        profile_id="test-profile",
        mode=EvaluationRunMode.LOCAL,
        status=EvaluationRunStatus.PARTIAL,
        metric_results=(
            build_metric_result(
                metric_id="passed",
                status=MetricRunStatus.PASSED,
            ),
            build_metric_result(
                metric_id="failed",
                status=MetricRunStatus.FAILED,
            ),
            build_metric_result(
                metric_id="error",
                status=MetricRunStatus.ERROR,
            ),
            build_metric_result(
                metric_id="blocked",
                status=MetricRunStatus.BLOCKED,
            ),
            build_metric_result(
                metric_id="skipped",
                status=MetricRunStatus.SKIPPED,
            ),
        ),
        started_at=now,
        finished_at=now + timedelta(seconds=1),
        duration_ms=1000.0,
        total_estimated_cost=0.0,
        external_run=False,
        deepeval_live_enabled=False,
    )

    assert result.metric_count == 5
    assert result.passed_count == 1
    assert result.failed_count == 1
    assert result.error_count == 1
    assert result.blocked_count == 1
    assert result.skipped_count == 1


def test_result_rejects_empty_run_id() -> None:
    now = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="run_id",
    ):
        EvaluationRunResult(
            run_id=" ",
            case_id="case",
            dataset_id="dataset@1.0.0",
            category="test",
            profile_id="profile",
            mode=EvaluationRunMode.LOCAL,
            status=EvaluationRunStatus.PASSED,
            metric_results=(),
            started_at=now,
            finished_at=now,
            duration_ms=0.0,
            total_estimated_cost=0.0,
            external_run=False,
            deepeval_live_enabled=False,
        )


def test_result_requires_timezone() -> None:
    naive = datetime.now()

    with pytest.raises(
        ValueError,
        match="timezone",
    ):
        EvaluationRunResult(
            run_id="run",
            case_id="case",
            dataset_id="dataset@1.0.0",
            category="test",
            profile_id="profile",
            mode=EvaluationRunMode.LOCAL,
            status=EvaluationRunStatus.PASSED,
            metric_results=(),
            started_at=naive,
            finished_at=naive,
            duration_ms=0.0,
            total_estimated_cost=0.0,
            external_run=False,
            deepeval_live_enabled=False,
        )


def test_result_rejects_invalid_time_order() -> None:
    now = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="anterior",
    ):
        EvaluationRunResult(
            run_id="run",
            case_id="case",
            dataset_id="dataset@1.0.0",
            category="test",
            profile_id="profile",
            mode=EvaluationRunMode.LOCAL,
            status=EvaluationRunStatus.PASSED,
            metric_results=(),
            started_at=now,
            finished_at=now - timedelta(seconds=1),
            duration_ms=0.0,
            total_estimated_cost=0.0,
            external_run=False,
            deepeval_live_enabled=False,
        )


# ============================================================
# REGISTRO DE EXECUTORES
# ============================================================


def test_runner_uses_default_registry() -> None:
    runner = EvaluationRunner()

    assert runner.registry.get(
        "answer-relevancy"
    )


def test_register_executor() -> None:
    runner = EvaluationRunner()

    runner.register_executor(
        "expected-terms",
        passing_executor,
    )


def test_register_executor_normalizes_id() -> None:
    runner = EvaluationRunner()

    runner.register_executor(
        " EXPECTED-TERMS ",
        passing_executor,
    )


def test_register_unknown_metric_is_rejected() -> None:
    runner = EvaluationRunner()

    with pytest.raises(
        MetricNotFoundError,
    ):
        runner.register_executor(
            "unknown-metric",
            passing_executor,
        )


def test_duplicate_executor_is_rejected() -> None:
    runner = EvaluationRunner()

    runner.register_executor(
        "expected-terms",
        passing_executor,
    )

    with pytest.raises(
        EvaluationRunnerError,
        match="já registrado",
    ):
        runner.register_executor(
            "expected-terms",
            passing_executor,
        )


def test_executor_can_be_replaced() -> None:
    runner = EvaluationRunner()

    runner.register_executor(
        "expected-terms",
        passing_executor,
    )

    runner.register_executor(
        "expected-terms",
        failing_executor,
        replace_existing=True,
    )


# ============================================================
# DRY-RUN
# ============================================================


def test_dry_run_plans_local_metrics(
    financial_case: InnaEvaluationCase,
    financial_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    result = runner.run(
        financial_case,
        financial_payload,
    )

    assert result.status == (
        EvaluationRunStatus.PLANNED
    )
    assert result.metric_results
    assert all(
        metric.status == MetricRunStatus.PLANNED
        for metric in result.metric_results
    )
    assert all(
        metric.estimated_cost == 0.0
        for metric in result.metric_results
    )


def test_dry_run_can_include_live_metrics(
    financial_case: InnaEvaluationCase,
    financial_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    result = runner.run(
        financial_case,
        financial_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.DRY_RUN,
            include_live_metrics=True,
        ),
    )

    metric_ids = tuple(
        item.metric_id
        for item in result.metric_results
    )

    assert "answer-relevancy" in metric_ids
    assert "financial-quality" in metric_ids
    assert "financial-safety" in metric_ids
    assert result.status == (
        EvaluationRunStatus.PLANNED
    )


def test_dry_run_does_not_call_executor(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    called = False

    def forbidden_executor(
        metric,
        case,
        payload,
    ) -> MetricExecutionOutput:
        nonlocal called
        called = True

        raise AssertionError(
            "Executor não deveria ser chamado."
        )

    runner = EvaluationRunner(
        executors={
            "contract-validation": (
                forbidden_executor
            ),
        }
    )

    result = runner.run(
        routing_case,
        routing_payload,
    )

    assert result.status == (
        EvaluationRunStatus.PLANNED
    )
    assert called is False


# ============================================================
# EXECUÇÃO LOCAL
# ============================================================


def test_local_run_passes(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = (
        build_runner_with_routing_executors()
    )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.status == (
        EvaluationRunStatus.PASSED
    )
    assert result.metric_count == 4
    assert result.passed_count == 4
    assert result.failed_count == 0
    assert result.error_count == 0


def test_local_failure_marks_run_failed(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = (
        build_runner_with_routing_executors()
    )

    runner.register_executor(
        "expected-terms",
        failing_executor,
        replace_existing=True,
    )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.status == (
        EvaluationRunStatus.FAILED
    )
    assert result.failed_count == 1


def test_missing_executor_is_skipped(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.metric_results
    assert all(
        item.status == MetricRunStatus.SKIPPED
        for item in result.metric_results
    )
    assert all(
        item.error_type
        == MetricExecutorNotFoundError.__name__
        for item in result.metric_results
    )
    assert result.status == (
        EvaluationRunStatus.PARTIAL
    )


def test_local_mode_skips_selected_live_metrics(
    financial_case: InnaEvaluationCase,
    financial_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    result = runner.run(
        financial_case,
        financial_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
            include_live_metrics=True,
        ),
    )

    live_results = tuple(
        result
        for result in result.metric_results
        if result.execution_mode.value
        == "live-opt-in"
    )

    assert live_results
    assert all(
        result.status == MetricRunStatus.SKIPPED
        for result in live_results
    )


# ============================================================
# VALIDAÇÃO DE PAYLOAD
# ============================================================


def test_missing_required_field_is_blocked(
    rag_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        rag_case,
        actual_output=(
            "Resposta sem documentos recuperados."
        ),
    )

    runner = EvaluationRunner(
        executors={
            "retrieval-contract": (
                passing_executor
            ),
        }
    )

    result = runner.run(
        rag_case,
        payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    retrieval_result = next(
        item
        for item in result.metric_results
        if item.metric_id
        == "retrieval-contract"
    )

    assert retrieval_result.status == (
        MetricRunStatus.BLOCKED
    )
    assert retrieval_result.error_type == (
        MetricInputValidationError.__name__
    )
    assert "retrieval_context" in (
        retrieval_result.reason or ""
    )


# ============================================================
# ISOLAMENTO DE ERROS
# ============================================================


def test_executor_exception_is_isolated(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = (
        build_runner_with_routing_executors()
    )

    runner.register_executor(
        "expected-terms",
        error_executor,
        replace_existing=True,
    )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
            continue_on_metric_error=True,
        ),
    )

    assert result.error_count == 1
    assert result.metric_count == 4
    assert result.status == (
        EvaluationRunStatus.PARTIAL
    )

    error_result = next(
        item
        for item in result.metric_results
        if item.status == MetricRunStatus.ERROR
    )

    assert error_result.error_type == (
        "RuntimeError"
    )
    assert "Falha sintética" in (
        error_result.reason or ""
    )


def test_runner_stops_after_error_when_configured(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = (
        build_runner_with_routing_executors()
    )

    runner.register_executor(
        "expected-terms",
        error_executor,
        replace_existing=True,
    )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
            continue_on_metric_error=False,
        ),
    )

    assert result.error_count == 1
    assert result.metric_count == 2


# ============================================================
# CONTROLE DE CUSTO
# ============================================================


def test_cost_is_accumulated(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    for metric_id in (
        "contract-validation",
        "expected-terms",
        "forbidden-terms",
        "latency-budget",
    ):
        runner.register_executor(
            metric_id,
            costly_executor,
        )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
    )

    assert result.total_estimated_cost == (
        pytest.approx(0.12)
    )


def test_cost_budget_blocks_result_above_limit(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    for metric_id in (
        "contract-validation",
        "expected-terms",
        "forbidden-terms",
        "latency-budget",
    ):
        runner.register_executor(
            metric_id,
            costly_executor,
        )

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
            maximum_total_cost=0.05,
        ),
    )

    assert result.blocked_count >= 1

    blocked = tuple(
        item
        for item in result.metric_results
        if item.status == MetricRunStatus.BLOCKED
    )

    assert all(
        item.error_type
        == EvaluationBudgetError.__name__
        for item in blocked
    )

    assert result.total_estimated_cost <= 0.05


# ============================================================
# PRIVACIDADE
# ============================================================


def test_external_public_case_is_allowed(
    routing_case: InnaEvaluationCase,
    routing_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner()

    result = runner.run(
        routing_case,
        routing_payload,
        settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.DRY_RUN,
            external_run=True,
        ),
    )

    assert result.external_run is True


def test_external_internal_case_is_blocked(
    internal_case: InnaEvaluationCase,
) -> None:
    payload = build_deepeval_payload(
        internal_case,
        actual_output=(
            "Resposta interna sintética."
        ),
    )

    runner = EvaluationRunner()

    with pytest.raises(
        DeepEvalPrivacyError,
    ):
        runner.run(
            internal_case,
            payload,
            settings=EvaluationRunnerSettings(
                mode=EvaluationRunMode.DRY_RUN,
                external_run=True,
            ),
        )


# ============================================================
# PROTEÇÃO LIVE
# ============================================================


def test_live_run_requires_feature_flags(
    financial_case: InnaEvaluationCase,
    financial_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner(
        deepeval_settings=DeepEvalSettings(
            enabled=False,
            live_enabled=False,
        )
    )

    with pytest.raises(
        DeepEvalConfigurationError,
    ):
        runner.run(
            financial_case,
            financial_payload,
            settings=EvaluationRunnerSettings(
                mode=EvaluationRunMode.LIVE,
                include_live_metrics=True,
                external_run=True,
            ),
        )


def test_live_run_blocks_when_only_base_flag_enabled(
    financial_case: InnaEvaluationCase,
    financial_payload: DeepEvalCasePayload,
) -> None:
    runner = EvaluationRunner(
        deepeval_settings=DeepEvalSettings(
            enabled=True,
            live_enabled=False,
        )
    )

    with pytest.raises(
        DeepEvalConfigurationError,
        match="INNA_DEEPEVAL_LIVE",
    ):
        runner.run(
            financial_case,
            financial_payload,
            settings=EvaluationRunnerSettings(
                mode=EvaluationRunMode.LIVE,
                include_live_metrics=True,
                external_run=True,
            ),
        )


# ============================================================
# AGREGAÇÃO DE STATUS
# ============================================================


def test_aggregate_empty_results() -> None:
    assert _aggregate_run_status(
        [],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.ERROR


def test_aggregate_dry_run() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.PLANNED
            )
        ],
        mode=EvaluationRunMode.DRY_RUN,
    ) == EvaluationRunStatus.PLANNED


def test_aggregate_all_passed() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.PASSED
            )
        ],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.PASSED


def test_aggregate_failed() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.PASSED
            ),
            build_metric_result(
                status=MetricRunStatus.FAILED
            ),
        ],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.FAILED


def test_aggregate_error_is_partial() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.PASSED
            ),
            build_metric_result(
                status=MetricRunStatus.ERROR
            ),
        ],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.PARTIAL


def test_aggregate_blocked() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.BLOCKED
            )
        ],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.BLOCKED


def test_aggregate_only_skipped_is_partial() -> None:
    assert _aggregate_run_status(
        [
            build_metric_result(
                status=MetricRunStatus.SKIPPED
            )
        ],
        mode=EvaluationRunMode.LOCAL,
    ) == EvaluationRunStatus.PARTIAL
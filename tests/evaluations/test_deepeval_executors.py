from __future__ import annotations

from typing import Any

import pytest

from src.evaluation.contracts import InnaEvaluationCase
from src.evaluation.deepeval_executors import (
    build_deepeval_executor,
    build_default_deepeval_executors,
    build_rag_evaluation_runner,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
)
from src.evaluation.deepeval_metrics import (
    MetricDefinition,
    MetricExecutionMode,
    MetricKind,
)


class FakeModel:
    def get_model_name(self) -> str:
        return "fake-gemini-model"


class FakeMetric:
    created_count = 0
    measured_count = 0

    def __init__(
        self,
        *,
        model: Any,
        threshold: float,
        include_reason: bool,
        async_mode: bool,
        strict_mode: bool,
        verbose_mode: bool,
    ) -> None:
        type(self).created_count += 1

        self.evaluation_model = model
        self.threshold = threshold
        self.include_reason = include_reason
        self.async_mode = async_mode
        self.strict_mode = strict_mode
        self.verbose_mode = verbose_mode
        self.reason = None
        self.evaluation_cost = 0.001

    def measure(
        self,
        test_case: Any,
        *,
        _show_indicator: bool = True,
        _in_component: bool = False,
        _log_metric_to_confident: bool = True,
    ) -> float:
        del (
            test_case,
            _show_indicator,
            _in_component,
        )

        assert (
            _log_metric_to_confident
            is False
        )

        type(self).measured_count += 1

        self.reason = "Resposta adequada."
        return 0.90


class FakeFailingMetric(FakeMetric):
    def measure(
        self,
        test_case: Any,
        *,
        _show_indicator: bool = True,
        _in_component: bool = False,
        _log_metric_to_confident: bool = True,
    ) -> float:
        del (
            test_case,
            _show_indicator,
            _in_component,
        )

        assert (
            _log_metric_to_confident
            is False
        )

        self.reason = "Score abaixo do limite."
        return 0.40


def _metric_definition(
    *,
    metric_id: str = "answer-relevancy",
    threshold: float = 0.80,
) -> MetricDefinition:
    return MetricDefinition(
        metric_id=metric_id,
        display_name="Teste",
        description="Métrica de teste.",
        kind=MetricKind.DEEPEVAL,
        execution_mode=(
            MetricExecutionMode.LIVE_OPT_IN
        ),
        threshold=threshold,
        deepeval_class_name="FakeMetric",
    )


def _case() -> InnaEvaluationCase:
    return InnaEvaluationCase(
        case_id="deepeval-executor-test",
        input_text="Pergunta de teste",
        category="rag",
    )


def _payload() -> DeepEvalCasePayload:
    return DeepEvalCasePayload(
        case_id="deepeval-executor-test",
        input_text="Pergunta de teste",
        actual_output="Resposta de teste",
        retrieval_context=(
            "Contexto recuperado de teste",
        ),
    )


def test_executor_returns_metric_execution_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation import (
        deepeval_executors,
    )

    monkeypatch.setattr(
        deepeval_executors,
        "create_llm_test_case",
        lambda payload: object(),
    )

    executor = build_deepeval_executor(
        FakeMetric,
        lambda: FakeModel(),
    )

    result = executor(
        _metric_definition(),
        _case(),
        _payload(),
    )

    assert result.passed is True
    assert result.score == pytest.approx(0.90)
    assert result.reason == "Resposta adequada."
    assert result.estimated_cost == pytest.approx(
        0.001
    )

    assert (
        result.metadata["judge_provider"]
        == "gemini"
    )

    assert (
        result.metadata["confident_logging"]
        is False
    )


def test_executor_represents_normal_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation import (
        deepeval_executors,
    )

    monkeypatch.setattr(
        deepeval_executors,
        "create_llm_test_case",
        lambda payload: object(),
    )

    executor = build_deepeval_executor(
        FakeFailingMetric,
        lambda: FakeModel(),
    )

    result = executor(
        _metric_definition(),
        _case(),
        _payload(),
    )

    assert result.passed is False
    assert result.score == pytest.approx(0.40)
    assert (
        result.reason
        == "Score abaixo do limite."
    )


def test_default_mapping_contains_rag_triad() -> None:
    executors = (
        build_default_deepeval_executors(
            model_provider=lambda: FakeModel(),
        )
    )

    assert set(executors) == {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }


def test_rag_runner_contains_local_and_live_executors(
) -> None:
    runner = build_rag_evaluation_runner(
        model_provider=lambda: FakeModel(),
    )

    expected = {
        "contract-validation",
        "expected-terms",
        "retrieval-contract",
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }

    assert expected.issubset(
        set(runner._executors)
    )



def test_mocked_live_runner_builds_complete_rag_triad(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation import deepeval_executors
    from src.evaluation.deepeval_runner import (
        EvaluationRunMode,
        EvaluationRunnerSettings,
    )

    monkeypatch.setenv(
        "INNA_DEEPEVAL_ENABLED",
        "1",
    )
    monkeypatch.setenv(
        "INNA_DEEPEVAL_LIVE",
        "1",
    )

    monkeypatch.setattr(
        deepeval_executors,
        "AnswerRelevancyMetric",
        FakeMetric,
    )
    monkeypatch.setattr(
        deepeval_executors,
        "FaithfulnessMetric",
        FakeMetric,
    )
    monkeypatch.setattr(
        deepeval_executors,
        "ContextualRelevancyMetric",
        FakeMetric,
    )
    monkeypatch.setattr(
        deepeval_executors,
        "create_llm_test_case",
        lambda payload: object(),
    )

    runner = (
        deepeval_executors
        .build_rag_evaluation_runner(
            model_provider=lambda: FakeModel(),
        )
    )

    case = InnaEvaluationCase(
        case_id="mocked-rag-triad-live",
        input_text=(
            "Como começar uma reserva financeira?"
        ),
        category="rag",
        language="pt",
        currency="BRL",
        external_evaluation_allowed=False,
    )

    payload = DeepEvalCasePayload(
        case_id=case.case_id,
        input_text=case.input_text,
        actual_output=(
            "Comece organizando o orçamento e "
            "reserve mensalmente um valor que "
            "seja compatível com sua realidade."
        ),
        retrieval_context=(
            (
                "A reserva financeira pode ser "
                "formada gradualmente."
            ),
            (
                "O orçamento ajuda a definir um "
                "valor mensal para a reserva."
            ),
        ),
    )

    settings = EvaluationRunnerSettings(
        mode=EvaluationRunMode.LIVE,
        include_live_metrics=True,
        external_run=False,
        maximum_total_cost=0.01,
    )

    result = runner.run(
        case,
        payload,
        settings=settings,
        metadata={
            "test_mode": "fully-mocked-live",
            "network_allowed": False,
        },
    )

    assert result.mode is EvaluationRunMode.LIVE
    assert result.deepeval_live_enabled is True
    assert result.external_run is False

    result_by_id = {
        item.metric_id: item
        for item in result.metric_results
    }

    required_triad = {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }

    assert required_triad.issubset(
        result_by_id
    )

    for metric_id in required_triad:
        metric_result = result_by_id[
            metric_id
        ]

        assert metric_result.status.value == "passed"
        assert metric_result.passed is True
        assert metric_result.score == pytest.approx(
            0.90
        )
        assert (
            metric_result.estimated_cost
            == pytest.approx(0.001)
        )

    triad = result.rag_triad

    assert triad is not None
    assert triad.status.value == "passed"
    assert triad.is_complete is True
    assert triad.passed is True
    assert triad.aggregate_score == pytest.approx(
        0.90
    )
    assert triad.missing_metric_ids == ()
    assert triad.failing_metric_ids == ()
    assert (
        triad.total_estimated_cost
        == pytest.approx(0.003)
    )

    assert (
        result.total_estimated_cost
        == pytest.approx(0.003)
    )



def _safe_external_case(
    *,
    maximum_estimated_cost: float = 0.03,
) -> InnaEvaluationCase:
    from src.evaluation.contracts import PrivacyLevel

    return InnaEvaluationCase(
        case_id="live-cost-preflight",
        input_text=(
            "Como começar uma reserva financeira?"
        ),
        category="rag",
        maximum_estimated_cost=(
            maximum_estimated_cost
        ),
        privacy_level=PrivacyLevel.PUBLIC,
        external_evaluation_allowed=True,
        metadata={
            "synthetic": True,
            "external_safe": True,
        },
    )


def _live_settings(
    *,
    maximum_total_cost: float = 0.03,
):
    from src.evaluation.deepeval_runner import (
        EvaluationRunMode,
        EvaluationRunnerSettings,
    )

    return EvaluationRunnerSettings(
        mode=EvaluationRunMode.LIVE,
        include_live_metrics=True,
        external_run=True,
        maximum_total_cost=(
            maximum_total_cost
        ),
    )


def test_live_cost_preflight_blocks_missing_reservation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation.deepeval_executors import (
        build_rag_evaluation_runner,
        run_rag_evaluation_with_cost_preflight,
    )
    from src.evaluation.deepeval_runner import (
        EvaluationBudgetError,
    )

    runner = build_rag_evaluation_runner(
        model_provider=lambda: FakeModel(),
    )

    called = {"run": False}

    def forbidden_run(*args: Any, **kwargs: Any):
        del args, kwargs
        called["run"] = True
        raise AssertionError(
            "runner.run não deveria ser chamado"
        )

    monkeypatch.setattr(
        runner,
        "run",
        forbidden_run,
    )

    payload = DeepEvalCasePayload(
        case_id="live-cost-preflight",
        input_text="Pergunta",
        actual_output="Resposta",
        retrieval_context=("Contexto",),
        metadata={},
    )

    with pytest.raises(
        EvaluationBudgetError,
        match="declarar",
    ):
        run_rag_evaluation_with_cost_preflight(
            runner,
            _safe_external_case(),
            payload,
            settings=_live_settings(),
        )

    assert called["run"] is False


def test_live_cost_preflight_blocks_over_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation.deepeval_executors import (
        LIVE_COST_RESERVATIONS_METADATA_KEY,
        build_rag_evaluation_runner,
        run_rag_evaluation_with_cost_preflight,
    )
    from src.evaluation.deepeval_runner import (
        EvaluationBudgetError,
    )

    runner = build_rag_evaluation_runner(
        model_provider=lambda: FakeModel(),
    )

    called = {"run": False}

    def forbidden_run(*args: Any, **kwargs: Any):
        del args, kwargs
        called["run"] = True
        raise AssertionError(
            "runner.run não deveria ser chamado"
        )

    monkeypatch.setattr(
        runner,
        "run",
        forbidden_run,
    )

    payload = DeepEvalCasePayload(
        case_id="live-cost-preflight",
        input_text="Pergunta",
        actual_output="Resposta",
        retrieval_context=("Contexto",),
        metadata={
            LIVE_COST_RESERVATIONS_METADATA_KEY: {
                "answer-relevancy": 0.02,
                "faithfulness": 0.02,
                "contextual-relevancy": 0.02,
            },
        },
    )

    with pytest.raises(
        EvaluationBudgetError,
        match="excede o orçamento",
    ):
        run_rag_evaluation_with_cost_preflight(
            runner,
            _safe_external_case(
                maximum_estimated_cost=0.03
            ),
            payload,
            settings=_live_settings(
                maximum_total_cost=0.03
            ),
        )

    assert called["run"] is False


def test_live_cost_preflight_allows_reserved_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.evaluation.deepeval_executors import (
        LIVE_COST_RESERVATIONS_METADATA_KEY,
        build_rag_evaluation_runner,
        run_rag_evaluation_with_cost_preflight,
    )

    runner = build_rag_evaluation_runner(
        model_provider=lambda: FakeModel(),
    )

    sentinel = object()
    called = {"run": False}

    def fake_run(
        case: Any,
        payload: Any,
        *,
        settings: Any,
        metadata: Any = None,
    ) -> Any:
        del case, payload, settings, metadata
        called["run"] = True
        return sentinel

    monkeypatch.setattr(
        runner,
        "run",
        fake_run,
    )

    payload = DeepEvalCasePayload(
        case_id="live-cost-preflight",
        input_text="Pergunta",
        actual_output="Resposta",
        retrieval_context=("Contexto",),
        metadata={
            LIVE_COST_RESERVATIONS_METADATA_KEY: {
                "answer-relevancy": 0.005,
                "faithfulness": 0.005,
                "contextual-relevancy": 0.005,
            },
        },
    )

    result = run_rag_evaluation_with_cost_preflight(
        runner,
        _safe_external_case(
            maximum_estimated_cost=0.03
        ),
        payload,
        settings=_live_settings(
            maximum_total_cost=0.03
        ),
    )

    assert result is sentinel
    assert called["run"] is True

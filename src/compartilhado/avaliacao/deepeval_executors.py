from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.models import GeminiModel

from src.compartilhado.avaliacao.contracts import InnaEvaluationCase
from src.compartilhado.avaliacao.deepeval_integration import (
    DeepEvalCasePayload,
    create_llm_test_case,
    ensure_external_case_allowed,
)
from src.compartilhado.avaliacao.deepeval_metrics import MetricDefinition
from src.compartilhado.avaliacao.deepeval_runner import (
    EvaluationBudgetError,
    EvaluationRunMode,
    EvaluationRunner,
    EvaluationRunnerSettings,
    EvaluationRunResult,
    MetricExecutionOutput,
    MetricExecutor,
)
from src.evaluation.deterministic_executors import (
    build_default_deterministic_executors,
)
from src.services.llm.gemini import obter_api_key_gemini
from src.services.llm.model_registry import (
    LLMRole,
    get_model_for_role,
)

DeepEvalMetricFactory = Callable[..., Any]
GeminiModelProvider = Callable[[], Any]

LIVE_COST_RESERVATIONS_METADATA_KEY = (
    "live_metric_cost_reservations_usd"
)


def build_gemini_evaluation_model(
    *,
    model_name: str | None = None,
    api_key: str | None = None,
) -> GeminiModel:
    """
    Constrói o modelo Gemini usado exclusivamente como juiz DeepEval.

    Nenhum request é executado durante a construção.
    """

    resolved_model = (
        str(model_name).strip()
        if model_name is not None
        else get_model_for_role(LLMRole.RAG)
    )

    if not resolved_model:
        raise ValueError(
            "O modelo Gemini de avaliação não pode ser vazio."
        )

    resolved_api_key = (
        str(api_key).strip()
        if api_key is not None
        else obter_api_key_gemini()
    )

    if not resolved_api_key:
        raise ValueError(
            "A API key Gemini de avaliação não pode ser vazia."
        )

    return GeminiModel(
        model=resolved_model,
        api_key=resolved_api_key,
        temperature=0.0,
    )


def _safe_estimated_cost(
    metric_instance: Any,
) -> float:
    """
    Extrai custo informado pelo DeepEval quando disponível.
    """

    raw_cost = getattr(
        metric_instance,
        "evaluation_cost",
        None,
    )

    if raw_cost is None:
        return 0.0

    try:
        resolved = float(raw_cost)
    except (TypeError, ValueError):
        return 0.0

    if resolved < 0:
        return 0.0

    return resolved


def build_deepeval_executor(
    metric_factory: DeepEvalMetricFactory,
    model_provider: GeminiModelProvider,
) -> MetricExecutor:
    """
    Cria um executor compatível com EvaluationRunner.
    """

    def execute(
        metric: MetricDefinition,
        case: InnaEvaluationCase,
        payload: DeepEvalCasePayload,
    ) -> MetricExecutionOutput:
        del case

        model = model_provider()

        threshold = (
            float(metric.threshold)
            if metric.threshold is not None
            else 0.5
        )

        metric_instance = metric_factory(
            model=model,
            threshold=threshold,
            include_reason=True,
            async_mode=False,
            strict_mode=metric.strict_mode,
            verbose_mode=False,
        )

        test_case = create_llm_test_case(
            payload
        )

        measured_score = metric_instance.measure(
            test_case,
            _show_indicator=False,
            _log_metric_to_confident=False,
        )

        score = float(measured_score)

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "DeepEval retornou score fora do intervalo "
                f"0..1: {score!r}."
            )

        passed = score >= threshold

        reason = getattr(
            metric_instance,
            "reason",
            None,
        )

        evaluation_model = getattr(
            metric_instance,
            "evaluation_model",
            None,
        )

        model_name = None

        if evaluation_model is not None:
            get_model_name = getattr(
                evaluation_model,
                "get_model_name",
                None,
            )

            if callable(get_model_name):
                try:
                    model_name = str(
                        get_model_name()
                    )
                except Exception:
                    model_name = (
                        type(
                            evaluation_model
                        ).__name__
                    )

        return MetricExecutionOutput(
            passed=passed,
            score=score,
            reason=(
                None
                if reason is None
                else str(reason)
            ),
            estimated_cost=(
                _safe_estimated_cost(
                    metric_instance
                )
            ),
            metadata={
                "deepeval_class": (
                    type(metric_instance).__name__
                ),
                "evaluation_model": model_name,
                "threshold": threshold,
                "judge_provider": "gemini",
                "confident_logging": False,
            },
        )

    return execute


def build_default_deepeval_executors(
    *,
    model_provider: GeminiModelProvider | None = None,
) -> Mapping[str, MetricExecutor]:
    """
    Retorna os três executores oficiais da RAG Triad.

    O GeminiModel é criado de forma lazy e compartilhado entre
    as três métricas durante a vida deste mapping.
    """

    resolved_provider = model_provider

    if resolved_provider is None:
        cached_model: dict[str, Any] = {}

        def default_model_provider() -> Any:
            if "model" not in cached_model:
                cached_model["model"] = (
                    build_gemini_evaluation_model()
                )

            return cached_model["model"]

        resolved_provider = default_model_provider

    return {
        "answer-relevancy": build_deepeval_executor(
            AnswerRelevancyMetric,
            resolved_provider,
        ),
        "faithfulness": build_deepeval_executor(
            FaithfulnessMetric,
            resolved_provider,
        ),
        "contextual-relevancy": build_deepeval_executor(
            ContextualRelevancyMetric,
            resolved_provider,
        ),
    }


def _resolve_live_cost_reservation(
    runner: EvaluationRunner,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
    settings: EvaluationRunnerSettings,
) -> float:
    """
    Resolve a reserva de custo das métricas LIVE antes
    de qualquer execução externa.
    """

    selection = runner.build_selection(
        case,
        settings,
    )

    raw_reservations = payload.metadata.get(
        LIVE_COST_RESERVATIONS_METADATA_KEY
    )

    if not isinstance(
        raw_reservations,
        Mapping,
    ):
        raise EvaluationBudgetError(
            "Payload LIVE precisa declarar "
            f"{LIVE_COST_RESERVATIONS_METADATA_KEY!r}."
        )

    total_reserved = 0.0

    for metric in selection.metrics:

        if not metric.is_live:
            continue

        raw_value = raw_reservations.get(
            metric.metric_id
        )

        if raw_value is None:
            raise EvaluationBudgetError(
                "Reserva de custo ausente para "
                f"{metric.metric_id!r}."
            )

        try:
            reserved = float(raw_value)
        except (TypeError, ValueError) as error:
            raise EvaluationBudgetError(
                "Reserva de custo inválida para "
                f"{metric.metric_id!r}."
            ) from error

        if reserved <= 0:
            raise EvaluationBudgetError(
                "Reserva de custo deve ser positiva para "
                f"{metric.metric_id!r}."
            )

        total_reserved += reserved

    return total_reserved


def run_rag_evaluation_with_cost_preflight(
    runner: EvaluationRunner,
    case: InnaEvaluationCase,
    payload: DeepEvalCasePayload,
    *,
    settings: EvaluationRunnerSettings,
    metadata: Mapping[str, Any] | None = None,
) -> EvaluationRunResult:
    """
    Entrada oficial para avaliação RAG LIVE.

    Em LIVE:
    1. exige external_run;
    2. aplica a política de privacidade;
    3. exige orçamento positivo;
    4. reserva custo antes de runner.run().
    """

    if settings.mode == EvaluationRunMode.LIVE:

        if not settings.external_run:
            raise EvaluationBudgetError(
                "Avaliação LIVE com juiz externo exige "
                "external_run=True."
            )

        ensure_external_case_allowed(
            case
        )

        if settings.maximum_total_cost <= 0:
            raise EvaluationBudgetError(
                "Avaliação LIVE exige "
                "maximum_total_cost positivo."
            )

        reserved_cost = (
            _resolve_live_cost_reservation(
                runner,
                case,
                payload,
                settings,
            )
        )

        effective_budget = (
            settings.maximum_total_cost
        )

        if case.maximum_estimated_cost is not None:
            effective_budget = min(
                effective_budget,
                float(
                    case.maximum_estimated_cost
                ),
            )

        if reserved_cost > effective_budget:
            raise EvaluationBudgetError(
                "Reserva pré-execução excede o orçamento: "
                f"reserved={reserved_cost:.6f}, "
                f"budget={effective_budget:.6f}."
            )

    return runner.run(
        case,
        payload,
        settings=settings,
        metadata=metadata,
    )



def build_rag_evaluation_runner(
    *,
    model_provider: GeminiModelProvider | None = None,
) -> EvaluationRunner:
    """
    Runner completo para RAG:
    métricas determinísticas + RAG Triad DeepEval.
    """

    executors = dict(
        build_default_deterministic_executors()
    )

    executors.update(
        build_default_deepeval_executors(
            model_provider=model_provider,
        )
    )

    return EvaluationRunner(
        executors=executors
    )


__all__ = [
    "GeminiModelProvider",
    "build_deepeval_executor",
    "build_default_deepeval_executors",
    "build_gemini_evaluation_model",
    "build_rag_evaluation_runner",
    "run_rag_evaluation_with_cost_preflight",
]

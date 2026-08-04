from __future__ import annotations

import asyncio
import inspect
import os
import re
import threading
import time
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

TRIAD_METRIC_CLASS_NAMES = {
    "answer-relevancy": "AnswerRelevancyMetric",
    "faithfulness": "FaithfulnessMetric",
    "contextual-relevancy": (
        "ContextualRelevancyMetric"
    ),
}


class DeepEvalLiveExecutorError(
    RuntimeError
):
    """
    Erro controlado dos executores DeepEval live.
    """


def _first_environment_value(
    *names: str,
) -> str | None:
    for name in names:
        value = str(
            os.getenv(
                name,
                "",
            )
            or ""
        ).strip()

        if value:
            return value

    return None


def resolve_gemini_judge_configuration(
) -> dict[str, str]:
    api_key = _first_environment_value(
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_GENAI_API_KEY",
    )

    if not api_key:
        raise DeepEvalLiveExecutorError(
            "Nenhuma credencial Gemini foi encontrada."
        )

    model_name = (
        _first_environment_value(
            "INNA_DEEPEVAL_GEMINI_MODEL",
            "GEMINI_MODEL_NAME",
        )
        or "gemini-2.5-flash"
    )

    return {
        "api_key": api_key,
        "model_name": model_name,
    }


INNA_GEMINI_RATE_LIMITER_VERSION = 1

_SHARED_GEMINI_LIMITER = None

_SHARED_GEMINI_LIMITER_LOCK = (
    threading.Lock()
)


def _environment_float(
    name: str,
    *,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw_value = str(
        os.getenv(
            name,
            "",
        )
        or ""
    ).strip()

    try:
        value = float(
            raw_value
        )
    except (
        TypeError,
        ValueError,
    ):
        value = default

    return min(
        maximum,
        max(
            minimum,
            value,
        ),
    )


def _environment_integer(
    name: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw_value = str(
        os.getenv(
            name,
            "",
        )
        or ""
    ).strip()

    try:
        value = int(
            raw_value
        )
    except (
        TypeError,
        ValueError,
    ):
        value = default

    return min(
        maximum,
        max(
            minimum,
            value,
        ),
    )


def _quota_error(
    exc: BaseException,
) -> bool:
    rendered = str(
        exc
    ).lower()

    markers = (
        "429",
        "resource_exhausted",
        "resource exhausted",
        "quota exceeded",
        "rate limit",
        "rate-limit",
        "too many requests",
    )

    return any(
        marker in rendered
        for marker in markers
    )


def _quota_retry_seconds(
    exc: BaseException,
    *,
    fallback: float,
) -> float:
    rendered = str(
        exc
    )

    patterns = (
        r"retry\s+in\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        r"retry\s+after\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        r"retryDelay[^0-9]*([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay[^0-9]*([0-9]+(?:\.[0-9]+)?)",
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            rendered,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        try:
            server_delay = float(
                match.group(1)
            )

            return max(
                fallback,
                server_delay + 3.0,
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

    return fallback


class GeminiRequestRateLimiter:
    """
    Limitador compartilhado entre todas as métricas
    e todas as variantes executadas no mesmo processo.
    """

    def __init__(
        self,
        *,
        minimum_interval_seconds: float,
        maximum_retries: int,
        fallback_retry_seconds: float,
        maximum_retry_seconds: float,
        clock=None,
        sleeper=None,
    ) -> None:
        self.minimum_interval_seconds = max(
            12.5,
            float(
                minimum_interval_seconds
            ),
        )

        self.maximum_retries = max(
            0,
            int(
                maximum_retries
            ),
        )

        self.fallback_retry_seconds = max(
            self.minimum_interval_seconds,
            float(
                fallback_retry_seconds
            ),
        )

        self.maximum_retry_seconds = max(
            self.fallback_retry_seconds,
            float(
                maximum_retry_seconds
            ),
        )

        self._clock = (
            clock
            or time.monotonic
        )

        self._sleeper = (
            sleeper
            or time.sleep
        )

        self._lock = threading.Lock()

        self._next_allowed_at = 0.0

        self.request_count = 0
        self.retry_count = 0
        self.total_wait_seconds = 0.0

    def _wait_for_slot(
        self,
    ) -> None:
        while True:
            with self._lock:
                now = float(
                    self._clock()
                )

                wait_seconds = max(
                    0.0,
                    self._next_allowed_at
                    - now,
                )

                if wait_seconds <= 0:
                    self._next_allowed_at = (
                        now
                        + self.minimum_interval_seconds
                    )

                    self.request_count += 1

                    return

            self._sleeper(
                wait_seconds
            )

            self.total_wait_seconds += (
                wait_seconds
            )

    def _defer_requests(
        self,
        seconds: float,
    ) -> None:
        delay = min(
            self.maximum_retry_seconds,
            max(
                self.minimum_interval_seconds,
                float(
                    seconds
                ),
            ),
        )

        with self._lock:
            now = float(
                self._clock()
            )

            self._next_allowed_at = max(
                self._next_allowed_at,
                now + delay,
            )

    def run_sync(
        self,
        operation,
    ):
        attempts = 0

        while True:
            self._wait_for_slot()

            try:
                return operation()

            except Exception as exc:
                if not _quota_error(
                    exc
                ):
                    raise

                if attempts >= (
                    self.maximum_retries
                ):
                    raise

                attempts += 1
                self.retry_count += 1

                retry_seconds = (
                    _quota_retry_seconds(
                        exc,
                        fallback=(
                            self.fallback_retry_seconds
                        ),
                    )
                )

                self._defer_requests(
                    retry_seconds
                )

                print(
                    "DEEPEVAL_GEMINI_QUOTA_RETRY="
                    + str(
                        attempts
                    )
                )

                print(
                    "DEEPEVAL_GEMINI_RETRY_AFTER_SECONDS="
                    + str(
                        round(
                            retry_seconds,
                            3,
                        )
                    )
                )

    async def run_async(
        self,
        operation,
    ):
        attempts = 0

        while True:
            await asyncio.to_thread(
                self._wait_for_slot
            )

            try:
                result = operation()

                if inspect.isawaitable(
                    result
                ):
                    return await result

                return result

            except Exception as exc:
                if not _quota_error(
                    exc
                ):
                    raise

                if attempts >= (
                    self.maximum_retries
                ):
                    raise

                attempts += 1
                self.retry_count += 1

                retry_seconds = (
                    _quota_retry_seconds(
                        exc,
                        fallback=(
                            self.fallback_retry_seconds
                        ),
                    )
                )

                self._defer_requests(
                    retry_seconds
                )

                print(
                    "DEEPEVAL_GEMINI_ASYNC_QUOTA_RETRY="
                    + str(
                        attempts
                    )
                )

                print(
                    "DEEPEVAL_GEMINI_ASYNC_RETRY_AFTER_SECONDS="
                    + str(
                        round(
                            retry_seconds,
                            3,
                        )
                    )
                )


def get_shared_gemini_rate_limiter(
) -> GeminiRequestRateLimiter:
    global _SHARED_GEMINI_LIMITER

    with _SHARED_GEMINI_LIMITER_LOCK:
        if _SHARED_GEMINI_LIMITER is None:
            _SHARED_GEMINI_LIMITER = (
                GeminiRequestRateLimiter(
                    minimum_interval_seconds=(
                        _environment_float(
                            "INNA_DEEPEVAL_MIN_REQUEST_INTERVAL_SECONDS",
                            default=15.0,
                            minimum=12.5,
                            maximum=120.0,
                        )
                    ),
                    maximum_retries=(
                        _environment_integer(
                            "INNA_DEEPEVAL_MAX_QUOTA_RETRIES",
                            default=8,
                            minimum=0,
                            maximum=20,
                        )
                    ),
                    fallback_retry_seconds=(
                        _environment_float(
                            "INNA_DEEPEVAL_QUOTA_RETRY_SECONDS",
                            default=45.0,
                            minimum=15.0,
                            maximum=300.0,
                        )
                    ),
                    maximum_retry_seconds=(
                        _environment_float(
                            "INNA_DEEPEVAL_MAX_RETRY_SECONDS",
                            default=180.0,
                            minimum=30.0,
                            maximum=900.0,
                        )
                    ),
                )
            )

        return _SHARED_GEMINI_LIMITER


def build_gemini_judge_model(
) -> Any:
    from deepeval.models import (
        GeminiModel,
    )

    configuration = (
        resolve_gemini_judge_configuration()
    )

    limiter = (
        get_shared_gemini_rate_limiter()
    )

    class RateLimitedGeminiModel(
        GeminiModel
    ):
        def generate(
            self,
            *args,
            **kwargs,
        ):
            return limiter.run_sync(
                lambda: super(
                    RateLimitedGeminiModel,
                    self,
                ).generate(
                    *args,
                    **kwargs,
                )
            )

        async def a_generate(
            self,
            *args,
            **kwargs,
        ):
            async def operation():
                result = super(
                    RateLimitedGeminiModel,
                    self,
                ).a_generate(
                    *args,
                    **kwargs,
                )

                if inspect.isawaitable(
                    result
                ):
                    return await result

                return result

            return await limiter.run_async(
                operation
            )

    model = RateLimitedGeminiModel(
        model=configuration[
            "model_name"
        ],
        api_key=configuration[
            "api_key"
        ],
        temperature=0,
    )

    model._inna_request_limiter = (
        limiter
    )

    print(
        "DEEPEVAL_GEMINI_RATE_LIMITER=True"
    )

    print(
        "DEEPEVAL_GEMINI_SHARED_LIMITER=True"
    )

    print(
        "DEEPEVAL_MIN_REQUEST_INTERVAL_SECONDS="
        + str(
            limiter.minimum_interval_seconds
        )
    )

    print(
        "DEEPEVAL_MAX_QUOTA_RETRIES="
        + str(
            limiter.maximum_retries
        )
    )

    return model


def _load_metric_class(
    class_name: str,
) -> type[Any]:
    from deepeval import metrics as deepeval_metrics

    metric_class = getattr(
        deepeval_metrics,
        class_name,
        None,
    )

    if not isinstance(
        metric_class,
        type,
    ):
        raise DeepEvalLiveExecutorError(
            "Classe DeepEval indisponível: "
            + class_name
        )

    return metric_class


def _metric_execution_output_type(
) -> type[Any]:
    try:
        from src.evaluation.deterministic_executors import (
            MetricExecutionOutput,
        )

        return MetricExecutionOutput

    except ImportError:
        from src.evaluation.deepeval_runner import (
            MetricExecutionOutput,
        )

        return MetricExecutionOutput


def _safe_float(
    value: object,
    default: float = 0.0,
) -> float:
    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        for item in value:
            try:
                return float(item)
            except (
                TypeError,
                ValueError,
            ):
                continue

        return default

    try:
        result = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default

    if result != result:
        return default

    return result


def _metric_passed(
    *,
    metric_instance: Any,
    score: float,
    threshold: float,
) -> bool:
    success_method = getattr(
        metric_instance,
        "is_successful",
        None,
    )

    if callable(
        success_method
    ):
        try:
            return bool(
                success_method()
            )
        except Exception:
            pass

    success_value = getattr(
        metric_instance,
        "success",
        None,
    )

    if isinstance(
        success_value,
        bool,
    ):
        return success_value

    return score >= threshold


def _metric_cost(
    metric_instance: Any,
) -> float:
    for attribute_name in (
        "evaluation_cost",
        "estimated_cost",
        "cost",
    ):
        if not hasattr(
            metric_instance,
            attribute_name,
        ):
            continue

        result = _safe_float(
            getattr(
                metric_instance,
                attribute_name,
                None,
            ),
            default=0.0,
        )

        if result >= 0:
            return result

    return 0.0


def build_metric_execution_output(
    *,
    score: float,
    threshold: float,
    passed: bool,
    reason: str | None,
    estimated_cost: float,
    metadata: Mapping[str, Any],
) -> Any:
    output_type = (
        _metric_execution_output_type()
    )

    safe_metadata = MappingProxyType(
        dict(metadata)
    )

    available_values: dict[str, Any] = {
        "score": score,
        "threshold": threshold,
        "passed": passed,
        "success": passed,
        "reason": reason,
        "estimated_cost": estimated_cost,
        "cost": estimated_cost,
        "metadata": safe_metadata,
        "details": safe_metadata,
    }

    try:
        signature = inspect.signature(
            output_type
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise DeepEvalLiveExecutorError(
            "MetricExecutionOutput não pôde "
            "ser inspecionado."
        ) from exc

    keyword_arguments: dict[str, Any] = {}
    unsupported_required: list[str] = []

    for name, parameter in (
        signature.parameters.items()
    ):
        if name == "self":
            continue

        if name in available_values:
            keyword_arguments[
                name
            ] = available_values[
                name
            ]

            continue

        if (
            parameter.default
            is inspect.Signature.empty
            and parameter.kind
            not in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
        ):
            unsupported_required.append(
                name
            )

    if unsupported_required:
        raise DeepEvalLiveExecutorError(
            "Campos obrigatórios desconhecidos em "
            "MetricExecutionOutput: "
            + ", ".join(
                unsupported_required
            )
        )

    return output_type(
        **keyword_arguments
    )


def build_deepeval_metric_executor(
    *,
    metric_id: str,
    model: Any,
    metric_class_loader: (
        Callable[
            [str],
            type[Any],
        ]
        | None
    ) = None,
    test_case_factory: (
        Callable[
            [Any],
            Any,
        ]
        | None
    ) = None,
) -> Callable[..., Any]:
    class_name = (
        TRIAD_METRIC_CLASS_NAMES.get(
            metric_id
        )
    )

    if not class_name:
        raise DeepEvalLiveExecutorError(
            "Métrica live não suportada: "
            + metric_id
        )

    class_loader = (
        metric_class_loader
        or _load_metric_class
    )

    if test_case_factory is None:
        from src.evaluation.deepeval_integration import (
            create_llm_test_case,
        )

        test_case_factory = (
            create_llm_test_case
        )

    def execute(
        metric: Any,
        case: Any,
        payload: Any,
    ) -> Any:
        del case

        received_metric_id = str(
            getattr(
                metric,
                "metric_id",
                "",
            )
        )

        if received_metric_id != metric_id:
            raise DeepEvalLiveExecutorError(
                "Executor "
                + metric_id
                + " recebeu "
                + received_metric_id
                + "."
            )

        threshold = _safe_float(
            getattr(
                metric,
                "threshold",
                0.0,
            ),
            default=0.0,
        )

        strict_mode = bool(
            getattr(
                metric,
                "strict_mode",
                False,
            )
        )

        metric_class = class_loader(
            class_name
        )

        metric_instance = metric_class(
            threshold=threshold,
            model=model,
            include_reason=True,
            async_mode=False,
            strict_mode=strict_mode,
            verbose_mode=False,
        )

        test_case = test_case_factory(
            payload
        )

        measured_score = (
            metric_instance.measure(
                test_case,
                _show_indicator=False,
                _log_metric_to_confident=False,
            )
        )

        score = _safe_float(
            getattr(
                metric_instance,
                "score",
                measured_score,
            ),
            default=_safe_float(
                measured_score,
                default=0.0,
            ),
        )

        passed = _metric_passed(
            metric_instance=metric_instance,
            score=score,
            threshold=threshold,
        )

        reason_value = getattr(
            metric_instance,
            "reason",
            None,
        )

        reason = (
            str(
                reason_value
            ).strip()
            if reason_value is not None
            else None
        )

        model_name = str(
            getattr(
                model,
                "model_name",
                getattr(
                    model,
                    "model",
                    type(model).__name__,
                ),
            )
        )

        return build_metric_execution_output(
            score=score,
            threshold=threshold,
            passed=passed,
            reason=reason,
            estimated_cost=(
                _metric_cost(
                    metric_instance
                )
            ),
            metadata={
                "provider": "gemini",
                "judge_model": model_name,
                "metric_id": metric_id,
                "deepeval_class": class_name,
                "async_mode": False,
                "raw_payload_stored": False,
                "raw_output_stored": False,
                "raw_context_stored": False,
            },
        )

    execute.__name__ = (
        "execute_"
        + metric_id.replace(
            "-",
            "_",
        )
    )

    return execute


def build_default_deepeval_live_executors(
    *,
    model: Any | None = None,
    metric_class_loader: (
        Callable[
            [str],
            type[Any],
        ]
        | None
    ) = None,
    test_case_factory: (
        Callable[
            [Any],
            Any,
        ]
        | None
    ) = None,
) -> Mapping[str, Callable[..., Any]]:
    judge_model = (
        model
        if model is not None
        else build_gemini_judge_model()
    )

    executors = {
        metric_id: (
            build_deepeval_metric_executor(
                metric_id=metric_id,
                model=judge_model,
                metric_class_loader=(
                    metric_class_loader
                ),
                test_case_factory=(
                    test_case_factory
                ),
            )
        )
        for metric_id
        in TRIAD_METRIC_CLASS_NAMES
    }

    return MappingProxyType(
        executors
    )

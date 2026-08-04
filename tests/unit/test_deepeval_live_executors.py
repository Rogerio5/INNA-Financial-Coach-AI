from __future__ import annotations

from types import SimpleNamespace

from src.evaluation.deepeval_live_executors import (
    TRIAD_METRIC_CLASS_NAMES,
    build_default_deepeval_live_executors,
)


class FakeDeepEvalMetric:
    def __init__(
        self,
        *,
        threshold,
        model,
        include_reason,
        async_mode,
        strict_mode,
        verbose_mode,
    ) -> None:
        self.threshold = threshold
        self.model = model
        self.include_reason = (
            include_reason
        )
        self.async_mode = async_mode
        self.strict_mode = strict_mode
        self.verbose_mode = (
            verbose_mode
        )

        self.score = None
        self.reason = None
        self.success = None
        self.evaluation_cost = 0.002

    def measure(
        self,
        test_case,
        _show_indicator=True,
        _in_component=False,
        _log_metric_to_confident=True,
    ):
        del test_case
        del _show_indicator
        del _in_component
        del _log_metric_to_confident

        self.score = 0.91
        self.reason = (
            "Métrica fake aprovada."
        )
        self.success = True

        return self.score


def fake_metric_class_loader(
    class_name: str,
):
    assert class_name in {
        "AnswerRelevancyMetric",
        "FaithfulnessMetric",
        "ContextualRelevancyMetric",
    }

    return FakeDeepEvalMetric


def test_builds_three_triad_executors() -> None:
    executors = (
        build_default_deepeval_live_executors(
            model=object(),
            metric_class_loader=(
                fake_metric_class_loader
            ),
            test_case_factory=(
                lambda payload: payload
            ),
        )
    )

    assert set(executors) == set(
        TRIAD_METRIC_CLASS_NAMES
    )


def test_executor_returns_numeric_score() -> None:
    executors = (
        build_default_deepeval_live_executors(
            model=object(),
            metric_class_loader=(
                fake_metric_class_loader
            ),
            test_case_factory=(
                lambda payload: payload
            ),
        )
    )

    metric = SimpleNamespace(
        metric_id="faithfulness",
        threshold=0.80,
        strict_mode=False,
    )

    result = executors[
        "faithfulness"
    ](
        metric,
        object(),
        object(),
    )

    assert float(
        result.score
    ) == 0.91

    passed = getattr(
        result,
        "passed",
        getattr(
            result,
            "success",
            None,
        ),
    )

    assert passed is True

    assert (
        "fake"
        in str(
            result.reason
        ).lower()
    )


def test_quota_error_detection_is_case_insensitive() -> None:
    from src.evaluation.deepeval_live_executors import (
        _quota_error,
    )

    assert _quota_error(
        RuntimeError(
            "429 RESOURCE_EXHAUSTED"
        )
    )

    assert _quota_error(
        RuntimeError(
            "quota exceeded"
        )
    )

    assert not _quota_error(
        RuntimeError(
            "invalid payload"
        )
    )


def test_retry_delay_reads_server_response() -> None:
    from src.evaluation.deepeval_live_executors import (
        _quota_retry_seconds,
    )

    delay = _quota_retry_seconds(
        RuntimeError(
            "Please retry in 35.447504023s."
        ),
        fallback=20.0,
    )

    assert delay >= 38.0


def test_shared_rate_limiter_retries_resource_exhausted() -> None:
    from src.evaluation.deepeval_live_executors import (
        GeminiRequestRateLimiter,
    )

    state = {
        "now": 0.0,
        "calls": 0,
        "sleeps": [],
    }

    def clock() -> float:
        return float(
            state["now"]
        )

    def sleeper(
        seconds: float,
    ) -> None:
        state[
            "sleeps"
        ].append(
            seconds
        )

        state[
            "now"
        ] += seconds

    limiter = GeminiRequestRateLimiter(
        minimum_interval_seconds=12.5,
        maximum_retries=2,
        fallback_retry_seconds=20.0,
        maximum_retry_seconds=120.0,
        clock=clock,
        sleeper=sleeper,
    )

    def operation():
        state[
            "calls"
        ] += 1

        if state[
            "calls"
        ] == 1:
            raise RuntimeError(
                "429 RESOURCE_EXHAUSTED. "
                "Please retry in 35s."
            )

        return "success"

    result = limiter.run_sync(
        operation
    )

    assert result == "success"
    assert state["calls"] == 2
    assert limiter.retry_count == 1
    assert sum(
        state["sleeps"]
    ) >= 38.0


def test_non_quota_error_is_not_retried() -> None:
    import pytest

    from src.evaluation.deepeval_live_executors import (
        GeminiRequestRateLimiter,
    )

    limiter = GeminiRequestRateLimiter(
        minimum_interval_seconds=12.5,
        maximum_retries=5,
        fallback_retry_seconds=20.0,
        maximum_retry_seconds=120.0,
        clock=lambda: 0.0,
        sleeper=lambda seconds: None,
    )

    calls = {
        "count": 0,
    }

    def operation():
        calls[
            "count"
        ] += 1

        raise ValueError(
            "invalid payload"
        )

    with pytest.raises(
        ValueError,
        match="invalid payload",
    ):
        limiter.run_sync(
            operation
        )

    assert calls["count"] == 1
    assert limiter.retry_count == 0

from __future__ import annotations

import pytest
from deepeval.models.utils import EvaluationCost

from src.evaluation.deepeval_executors import (
    _safe_estimated_cost,
)


class _Metric:
    def __init__(
        self,
        evaluation_cost,
    ):
        self.evaluation_cost = evaluation_cost


def test_evaluation_cost_is_float_compatible():
    cost = EvaluationCost(
        0.0123,
        input_tokens=120,
        output_tokens=30,
    )

    assert isinstance(
        cost,
        float,
    )

    assert float(cost) == pytest.approx(
        0.0123
    )

    assert cost.input_tokens == 120
    assert cost.output_tokens == 30


def test_safe_estimated_cost_accepts_evaluation_cost():
    cost = EvaluationCost(
        0.0123,
        input_tokens=120,
        output_tokens=30,
    )

    metric = _Metric(
        evaluation_cost=cost
    )

    assert _safe_estimated_cost(
        metric
    ) == pytest.approx(
        0.0123
    )


def test_safe_estimated_cost_accepts_unknown_cost():
    cost = EvaluationCost(
        None,
        input_tokens=120,
        output_tokens=30,
    )

    metric = _Metric(
        evaluation_cost=cost
    )

    assert _safe_estimated_cost(
        metric
    ) == 0.0


def test_safe_estimated_cost_rejects_negative_value():
    metric = _Metric(
        evaluation_cost=-0.10
    )

    assert _safe_estimated_cost(
        metric
    ) == 0.0


def test_safe_estimated_cost_handles_missing_cost():
    metric = object()

    assert _safe_estimated_cost(
        metric
    ) == 0.0

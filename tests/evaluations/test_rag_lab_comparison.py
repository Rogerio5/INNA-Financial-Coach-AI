from types import SimpleNamespace

import pytest

from src.evaluation.rag_lab_comparison import (
    RagLabComparisonStatus,
    compare_rag_triad_entries,
)


def _metric(
    metric_id: str,
    score: float,
):
    return SimpleNamespace(
        metric_id=metric_id,
        average_score=score,
    )


def _entry(
    reference: str,
    *,
    answer: float,
    faithfulness: float,
    context: float,
    aggregate: float,
    passed: bool = True,
):
    return SimpleNamespace(
        run_reference=reference,
        metrics=(
            _metric(
                "answer-relevancy",
                answer,
            ),
            _metric(
                "faithfulness",
                faithfulness,
            ),
            _metric(
                "contextual-relevancy",
                context,
            ),
        ),
        rag_triad=SimpleNamespace(
            average_score=aggregate,
            passed=passed,
        ),
    )


def test_detects_complete_improvement():
    baseline = _entry(
        "baseline-001",
        answer=0.80,
        faithfulness=0.82,
        context=0.78,
        aggregate=0.80,
    )

    candidate = _entry(
        "candidate-001",
        answer=0.90,
        faithfulness=0.91,
        context=0.88,
        aggregate=0.896,
    )

    comparison = compare_rag_triad_entries(
        baseline,
        candidate,
    )

    assert comparison.complete is True
    assert comparison.status == RagLabComparisonStatus.IMPROVED
    assert comparison.delta == pytest.approx(0.096)
    assert comparison.has_improvement is True
    assert comparison.has_regression is False

    assert set(comparison.improved_metric_ids) == {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }


def test_detects_axis_regression():
    baseline = _entry(
        "baseline-001",
        answer=0.90,
        faithfulness=0.90,
        context=0.90,
        aggregate=0.90,
    )

    candidate = _entry(
        "candidate-001",
        answer=0.92,
        faithfulness=0.83,
        context=0.91,
        aggregate=0.886,
    )

    comparison = compare_rag_triad_entries(
        baseline,
        candidate,
    )

    assert comparison.status == RagLabComparisonStatus.REGRESSED
    assert comparison.has_regression is True
    assert comparison.regressed_metric_ids == ("faithfulness",)


def test_classifies_small_delta_as_stable():
    baseline = _entry(
        "baseline-001",
        answer=0.90,
        faithfulness=0.90,
        context=0.90,
        aggregate=0.900,
    )

    candidate = _entry(
        "candidate-001",
        answer=0.902,
        faithfulness=0.899,
        context=0.901,
        aggregate=0.901,
    )

    comparison = compare_rag_triad_entries(
        baseline,
        candidate,
        tolerance=0.005,
    )

    assert comparison.status == RagLabComparisonStatus.STABLE

    assert set(comparison.stable_metric_ids) == {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }


def test_marks_missing_triad_as_unavailable():
    baseline = _entry(
        "baseline-001",
        answer=0.80,
        faithfulness=0.82,
        context=0.78,
        aggregate=0.80,
    )

    candidate = SimpleNamespace(
        run_reference="candidate-old",
        metrics=(),
        rag_triad=None,
    )

    comparison = compare_rag_triad_entries(
        baseline,
        candidate,
    )

    assert comparison.complete is False

    assert comparison.status == RagLabComparisonStatus.UNAVAILABLE

    assert set(comparison.unavailable_metric_ids) == {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }


def test_rejects_negative_tolerance():
    baseline = _entry(
        "baseline",
        answer=0.8,
        faithfulness=0.8,
        context=0.8,
        aggregate=0.8,
    )

    candidate = _entry(
        "candidate",
        answer=0.9,
        faithfulness=0.9,
        context=0.9,
        aggregate=0.9,
    )

    with pytest.raises(
        ValueError,
        match="tolerance",
    ):
        compare_rag_triad_entries(
            baseline,
            candidate,
            tolerance=-0.01,
        )


def test_serialization_is_dashboard_safe():
    comparison = compare_rag_triad_entries(
        _entry(
            "baseline",
            answer=0.8,
            faithfulness=0.8,
            context=0.8,
            aggregate=0.8,
        ),
        _entry(
            "candidate",
            answer=0.9,
            faithfulness=0.9,
            context=0.9,
            aggregate=0.9,
        ),
    )

    payload = comparison.to_dict()

    assert payload["baseline_reference"] == "baseline"

    assert payload["candidate_reference"] == "candidate"

    assert payload["status"] == "improved"
    assert len(payload["axes"]) == 3

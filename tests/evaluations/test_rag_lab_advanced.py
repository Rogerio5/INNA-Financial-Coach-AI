from types import SimpleNamespace

import pytest

from src.evaluation.rag_lab_advanced import (
    QualityGateThresholds,
    RagLabCapabilityStatus,
    build_rag_lab_capabilities,
    calculate_cost_per_approved_run,
    evaluate_quality_gate,
    export_rag_lab_history_csv,
    export_rag_lab_report_json,
    rank_rag_lab_runs,
)


def _metric(metric_id, score):
    return SimpleNamespace(
        metric_id=metric_id,
        average_score=score,
    )


def _entry(
    reference,
    *,
    score,
    passed=True,
    metadata=None,
):
    return SimpleNamespace(
        run_reference=reference,
        recorded_at="2026-07-30T00:00:00Z",
        branch="main",
        commit_sha="abc123",
        environment="test",
        evaluation_mode="offline",
        metrics=(
            _metric("answer-relevancy", score),
            _metric("faithfulness", score),
            _metric("contextual-relevancy", score),
        ),
        rag_triad=SimpleNamespace(
            average_score=score,
            passed=passed,
            failing_metric_ids=(),
        ),
        metadata=metadata or {},
    )


def _history(*entries):
    return SimpleNamespace(entries=entries)


def test_quality_gate_uses_real_scores():
    result = evaluate_quality_gate(
        _entry("run-1", score=0.90),
        thresholds=QualityGateThresholds(
            answer_relevancy=0.80,
            faithfulness=0.80,
            contextual_relevancy=0.80,
            aggregate_score=0.80,
        ),
    )

    assert result.complete is True
    assert result.passed is True
    assert result.failed_keys == ()


def test_quality_gate_detects_failure():
    result = evaluate_quality_gate(
        _entry("run-1", score=0.60),
        thresholds=QualityGateThresholds(
            answer_relevancy=0.70,
            faithfulness=0.70,
            contextual_relevancy=0.70,
            aggregate_score=0.70,
        ),
    )

    assert result.passed is False
    assert len(result.failed_keys) == 4


def test_quality_gate_validates_thresholds():
    with pytest.raises(ValueError):
        QualityGateThresholds(aggregate_score=1.10)


def test_capabilities_wait_for_real_metadata():
    capabilities = {
        item.key: item
        for item in build_rag_lab_capabilities(_history(_entry("run-1", score=0.8)))
    }

    assert (
        capabilities["reranker_comparison"].status
        == RagLabCapabilityStatus.WAITING_DATA
    )


def test_capability_becomes_active():
    history = _history(
        _entry(
            "run-1",
            score=0.8,
            metadata={"reranker_enabled": True},
        ),
        _entry(
            "run-2",
            score=0.9,
            metadata={"reranker_enabled": False},
        ),
    )

    capabilities = {item.key: item for item in build_rag_lab_capabilities(history)}

    assert capabilities["reranker_comparison"].status == RagLabCapabilityStatus.ACTIVE


def test_ranking_prefers_highest_quality():
    ranking = rank_rag_lab_runs(
        _history(
            _entry("low", score=0.70),
            _entry("high", score=0.95),
        )
    )

    assert ranking[0].run_reference == "high"
    assert ranking[0].position == 1
    assert ranking[0].ranking_basis == "quality_only"


def test_cost_per_approved_run_requires_real_cost():
    assert calculate_cost_per_approved_run(_history(_entry("run", score=0.90))) is None


def test_cost_per_approved_run_uses_real_values():
    value = calculate_cost_per_approved_run(
        _history(
            _entry(
                "run-1",
                score=0.90,
                metadata={"estimated_cost_usd": 0.01},
            ),
            _entry(
                "run-2",
                score=0.91,
                metadata={"estimated_cost_usd": 0.03},
            ),
        )
    )

    assert value == pytest.approx(0.02)


def test_csv_export_contains_real_data():
    csv_text = export_rag_lab_history_csv(
        _history(
            _entry(
                "run-real",
                score=0.88,
                metadata={"retrieval_strategy": "hybrid"},
            )
        )
    )

    assert "run-real" in csv_text
    assert "hybrid" in csv_text
    assert "0.88" in csv_text


def test_json_export_marks_no_simulation():
    json_text = export_rag_lab_report_json(
        _history(_entry("run-real", score=0.88)),
        quality_gate=(QualityGateThresholds()),
    )

    assert '"simulation": false' in json_text
    assert '"run-real"' in json_text

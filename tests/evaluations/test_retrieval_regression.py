from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.retrieval_evaluation import (
    RetrievalCase,
    evaluate_retrieval_dataset,
)
from src.evaluation.retrieval_regression import (
    RetrievalMetricDeltas,
    RetrievalRegressionThresholds,
    compare_retrieval_reports,
    evaluate_regression_gate,
    load_latency_fixture,
    render_regression_markdown,
    summarize_retrieval_latencies,
    write_regression_reports,
)


def _case(case_id: str) -> RetrievalCase:
    return RetrievalCase(
        case_id=case_id,
        question="Pergunta offline",
        retrieved_document_ids=(
            "doc_a",
            "doc_x",
            "doc_b",
        ),
        relevant_document_ids=(
            "doc_a",
            "doc_b",
        ),
        graded_relevance={
            "doc_a": 3,
            "doc_b": 2,
        },
        k=3,
    )


def _report(name: str):
    return evaluate_retrieval_dataset(
        dataset_name=name,
        cases=[
            _case("case-001"),
            _case("case-002"),
        ],
    )


def test_summarize_retrieval_latencies() -> None:
    summary = summarize_retrieval_latencies([10.0, 20.0, 30.0, 40.0])

    assert summary.case_count == 4
    assert summary.mean_ms == pytest.approx(25.0)
    assert summary.median_ms == pytest.approx(25.0)
    assert summary.minimum_ms == 10.0
    assert summary.maximum_ms == 40.0
    assert summary.p95_ms == 40.0


def test_summarize_rejects_empty_values() -> None:
    with pytest.raises(
        ValueError,
        match="nao pode ser vazia",
    ):
        summarize_retrieval_latencies([])


def test_summarize_rejects_negative_latency() -> None:
    with pytest.raises(
        ValueError,
        match="valores negativos",
    ):
        summarize_retrieval_latencies([10.0, -1.0])


def test_load_latency_fixture(
    tmp_path: Path,
) -> None:
    path = tmp_path / "latencies.json"

    path.write_text(
        json.dumps(
            {
                "name": "fixture",
                "cases": [
                    {
                        "case_id": "case-001",
                        "retrieval_latency_ms": 12.5,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    name, latencies = load_latency_fixture(path)

    assert name == "fixture"
    assert latencies == {
        "case-001": 12.5,
    }


def test_regression_gate_passes_within_tolerance() -> None:
    deltas = RetrievalMetricDeltas(
        hit_rate=0.0,
        recall=-0.01,
        precision=-0.02,
        reciprocal_rank=0.0,
        ndcg=-0.01,
        mean_latency_ms=5.0,
        median_latency_ms=4.0,
        p95_latency_ms=8.0,
    )

    result = evaluate_regression_gate(
        deltas,
        RetrievalRegressionThresholds(),
    )

    assert result.passed is True
    assert result.failed_checks == ()


def test_regression_gate_detects_quality_and_latency_failure() -> None:
    deltas = RetrievalMetricDeltas(
        hit_rate=-0.10,
        recall=-0.10,
        precision=-0.10,
        reciprocal_rank=-0.10,
        ndcg=-0.10,
        mean_latency_ms=30.0,
        median_latency_ms=30.0,
        p95_latency_ms=30.0,
    )

    result = evaluate_regression_gate(
        deltas,
        RetrievalRegressionThresholds(),
    )

    assert result.passed is False
    assert "recall" in result.failed_checks
    assert "p95_latency" in result.failed_checks


def test_compare_retrieval_reports_passes() -> None:
    baseline = _report("baseline")
    candidate = _report("candidate")

    report = compare_retrieval_reports(
        baseline_report=baseline,
        candidate_report=candidate,
        baseline_latencies_ms={
            "case-001": 10.0,
            "case-002": 20.0,
        },
        candidate_latencies_ms={
            "case-001": 12.0,
            "case-002": 22.0,
        },
    )

    assert report.regression_gate.passed is True
    assert report.deltas.recall == 0.0
    assert report.deltas.mean_latency_ms == 2.0


def test_compare_rejects_missing_latency() -> None:
    baseline = _report("baseline")
    candidate = _report("candidate")

    with pytest.raises(
        ValueError,
        match="Latencias ausentes",
    ):
        compare_retrieval_reports(
            baseline_report=baseline,
            candidate_report=candidate,
            baseline_latencies_ms={
                "case-001": 10.0,
            },
            candidate_latencies_ms={
                "case-001": 12.0,
                "case-002": 22.0,
            },
        )


def test_markdown_contains_regression_summary() -> None:
    report = compare_retrieval_reports(
        baseline_report=_report("baseline"),
        candidate_report=_report("candidate"),
        baseline_latencies_ms={
            "case-001": 10.0,
            "case-002": 20.0,
        },
        candidate_latencies_ms={
            "case-001": 12.0,
            "case-002": 22.0,
        },
    )

    markdown = render_regression_markdown(report)

    assert "# Regressão Offline de Retrieval" in markdown
    assert "Regression gate" in markdown
    assert "Gemini utilizado: `não`" in markdown


def test_write_regression_reports(
    tmp_path: Path,
) -> None:
    report = compare_retrieval_reports(
        baseline_report=_report("baseline"),
        candidate_report=_report("candidate"),
        baseline_latencies_ms={
            "case-001": 10.0,
            "case-002": 20.0,
        },
        candidate_latencies_ms={
            "case-001": 12.0,
            "case-002": 22.0,
        },
    )

    json_path, markdown_path = write_regression_reports(
        report,
        tmp_path,
    )

    assert json_path.is_file()
    assert markdown_path.is_file()

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["regression_gate"]["passed"] is True
    assert payload["deltas"]["mean_latency_ms"] == 2.0

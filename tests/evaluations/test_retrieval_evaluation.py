from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.retrieval_evaluation import (
    RetrievalAggregateMetrics,
    RetrievalCase,
    RetrievalQualityThresholds,
    evaluate_quality_gate,
    evaluate_retrieval_dataset,
    load_retrieval_dataset,
    render_markdown_report,
    write_retrieval_reports,
)


def _case(
    *,
    case_id: str = "case-001",
    retrieved: tuple[str, ...] = (
        "doc_a",
        "doc_x",
        "doc_b",
    ),
) -> RetrievalCase:
    return RetrievalCase(
        case_id=case_id,
        question="Pergunta de teste",
        retrieved_document_ids=retrieved,
        relevant_document_ids=("doc_a", "doc_b"),
        graded_relevance={
            "doc_a": 3,
            "doc_b": 2,
        },
        k=3,
    )


def test_load_retrieval_dataset_reads_cases(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dataset.json"
    path.write_text(
        json.dumps(
            {
                "name": "dataset-test",
                "cases": [
                    {
                        "case_id": "case-001",
                        "question": "Pergunta?",
                        "k": 2,
                        "retrieved_document_ids": [
                            "doc_a",
                            "doc_x",
                        ],
                        "relevant_document_ids": [
                            "doc_a",
                        ],
                        "graded_relevance": {
                            "doc_a": 3,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    name, cases = load_retrieval_dataset(path)

    assert name == "dataset-test"
    assert len(cases) == 1
    assert cases[0].case_id == "case-001"


def test_load_retrieval_dataset_rejects_duplicate_case_ids(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dataset.json"
    case = {
        "case_id": "duplicate",
        "question": "Pergunta?",
        "k": 1,
        "retrieved_document_ids": ["doc_a"],
        "relevant_document_ids": ["doc_a"],
        "graded_relevance": {"doc_a": 3},
    }
    path.write_text(
        json.dumps(
            {
                "name": "dataset-test",
                "cases": [case, case],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="case_id duplicado",
    ):
        load_retrieval_dataset(path)


def test_load_retrieval_dataset_requires_cases(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dataset.json"
    path.write_text(
        json.dumps(
            {
                "name": "dataset-test",
                "cases": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="ao menos um caso",
    ):
        load_retrieval_dataset(path)


def test_evaluate_retrieval_dataset_aggregates_metrics() -> None:
    report = evaluate_retrieval_dataset(
        dataset_name="dataset-test",
        cases=[
            _case(case_id="case-001"),
            _case(
                case_id="case-002",
                retrieved=(
                    "doc_x",
                    "doc_a",
                    "doc_b",
                ),
            ),
        ],
    )

    aggregate = report.aggregate_metrics

    assert aggregate.case_count == 2
    assert aggregate.mean_hit_rate == 1.0
    assert aggregate.mean_recall == 1.0
    assert aggregate.mean_precision == pytest.approx(2 / 3)
    assert aggregate.mean_reciprocal_rank == pytest.approx(0.75)
    assert 0.0 < aggregate.mean_ndcg <= 1.0


def test_quality_gate_passes_when_thresholds_are_met() -> None:
    aggregate = RetrievalAggregateMetrics(
        case_count=2,
        mean_hit_rate=1.0,
        mean_recall=0.9,
        mean_precision=0.7,
        mean_reciprocal_rank=0.8,
        mean_ndcg=0.9,
    )

    result = evaluate_quality_gate(
        aggregate,
        RetrievalQualityThresholds(),
    )

    assert result.passed is True
    assert result.failed_checks == ()


def test_quality_gate_reports_failed_checks() -> None:
    aggregate = RetrievalAggregateMetrics(
        case_count=2,
        mean_hit_rate=0.5,
        mean_recall=0.4,
        mean_precision=0.3,
        mean_reciprocal_rank=0.2,
        mean_ndcg=0.1,
    )

    result = evaluate_quality_gate(
        aggregate,
        RetrievalQualityThresholds(),
    )

    assert result.passed is False
    assert result.failed_checks == (
        "hit_rate",
        "recall",
        "precision",
        "mrr",
        "ndcg",
    )


def test_render_markdown_report_contains_summary() -> None:
    report = evaluate_retrieval_dataset(
        dataset_name="dataset-test",
        cases=[_case()],
        thresholds=RetrievalQualityThresholds(
            minimum_hit_rate=0.5,
            minimum_recall=0.5,
            minimum_precision=0.5,
            minimum_mrr=0.5,
            minimum_ndcg=0.5,
        ),
    )

    markdown = render_markdown_report(report)

    assert "# Avaliação Offline de Retrieval" in markdown
    assert "dataset-test" in markdown
    assert "Quality gate" in markdown
    assert "Gemini utilizado: `não`" in markdown


def test_write_retrieval_reports_creates_json_and_markdown(
    tmp_path: Path,
) -> None:
    report = evaluate_retrieval_dataset(
        dataset_name="dataset-test",
        cases=[_case()],
        thresholds=RetrievalQualityThresholds(
            minimum_hit_rate=0.5,
            minimum_recall=0.5,
            minimum_precision=0.5,
            minimum_mrr=0.5,
            minimum_ndcg=0.5,
        ),
    )

    json_path, markdown_path = write_retrieval_reports(
        report,
        tmp_path,
    )

    assert json_path.is_file()
    assert markdown_path.is_file()

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert json_payload["dataset_name"] == "dataset-test"
    assert json_payload["quality_gate"]["passed"] is True
    assert "Avaliação Offline" in markdown_path.read_text(encoding="utf-8")


def test_report_as_dict_is_json_serializable() -> None:
    report = evaluate_retrieval_dataset(
        dataset_name="dataset-test",
        cases=[_case()],
    )

    serialized = json.dumps(report.as_dict())

    assert "aggregate_metrics" in serialized
    assert "quality_gate" in serialized


def test_evaluate_retrieval_dataset_rejects_empty_cases() -> None:
    with pytest.raises(
        ValueError,
        match="Nenhum caso",
    ):
        evaluate_retrieval_dataset(
            dataset_name="dataset-test",
            cases=[],
        )

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation.retrieval_evaluation import (
    RetrievalCase,
    RetrievalQualityThresholds,
    evaluate_retrieval_dataset,
)
from src.evaluation.retrieval_offline_e2e import (
    build_offline_validation_report,
    render_offline_validation_markdown,
    write_offline_validation_reports,
)
from src.evaluation.retrieval_regression import (
    compare_retrieval_reports,
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


def _quality_report(name: str):
    return evaluate_retrieval_dataset(
        dataset_name=name,
        cases=[
            _case("case-001"),
            _case("case-002"),
        ],
        thresholds=RetrievalQualityThresholds(
            minimum_hit_rate=0.50,
            minimum_recall=0.50,
            minimum_precision=0.50,
            minimum_mrr=0.50,
            minimum_ndcg=0.50,
        ),
    )


def _regression_report():
    return compare_retrieval_reports(
        baseline_report=_quality_report("baseline"),
        candidate_report=_quality_report("candidate"),
        baseline_latencies_ms={
            "case-001": 10.0,
            "case-002": 20.0,
        },
        candidate_latencies_ms={
            "case-001": 12.0,
            "case-002": 22.0,
        },
    )


def test_build_report_passes_when_all_checks_pass() -> None:
    report = build_offline_validation_report(
        ruff_passed=True,
        tests_passed=True,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    assert report.passed is True
    assert report.failed_checks == ()
    assert report.execution_environment["gemini_used"] is False
    assert report.execution_environment["neon_used"] is False


def test_build_report_fails_when_ruff_fails() -> None:
    report = build_offline_validation_report(
        ruff_passed=False,
        tests_passed=True,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    assert report.passed is False
    assert "ruff" in report.failed_checks


def test_build_report_fails_when_tests_fail() -> None:
    report = build_offline_validation_report(
        ruff_passed=True,
        tests_passed=False,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    assert report.passed is False
    assert "tests" in report.failed_checks


def test_markdown_contains_final_status() -> None:
    report = build_offline_validation_report(
        ruff_passed=True,
        tests_passed=True,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    markdown = render_offline_validation_markdown(report)

    assert "Validação Ponta a Ponta Offline" in markdown
    assert "Resultado final: **PASS**" in markdown
    assert "Gemini utilizado: `não`" in markdown
    assert "Neon utilizado: `não`" in markdown


def test_write_reports_creates_json_and_markdown(
    tmp_path: Path,
) -> None:
    report = build_offline_validation_report(
        ruff_passed=True,
        tests_passed=True,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    json_path, markdown_path = write_offline_validation_reports(
        report,
        tmp_path,
    )

    assert json_path.is_file()
    assert markdown_path.is_file()

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["passed"] is True
    assert payload["failed_checks"] == []
    assert payload["execution_environment"]["database_connected"] is False


def test_report_contains_quality_and_regression_values() -> None:
    report = build_offline_validation_report(
        ruff_passed=True,
        tests_passed=True,
        quality_report=_quality_report("baseline"),
        regression_report=_regression_report(),
    )

    assert report.quality_metrics["hit_rate"] == 1.0
    assert report.quality_metrics["recall"] == 1.0
    assert report.regression_deltas["mean_latency_ms"] == 2.0

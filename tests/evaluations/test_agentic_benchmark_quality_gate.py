from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from src.evaluation.agentic_benchmark import (
    BenchmarkProfile,
    QualityGatePolicy,
    evaluate_benchmark_quality_gate,
    load_benchmark_dataset,
    load_quality_gate_policy,
    quality_gate_to_dict,
    run_offline_benchmark,
    write_quality_gate_report,
)

DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "agentic_rag_v1.jsonl"
)

POLICY_PATH = (
    Path(__file__).parents[2]
    / "config"
    / "evaluation"
    / "agentic_rag_quality_gate.json"
)


def make_benchmark():
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    return dataset, run_offline_benchmark(
        dataset
    )


def test_policy_loads() -> None:
    policy = load_quality_gate_policy(
        POLICY_PATH
    )

    assert policy.policy_version == "1.0.0"
    assert policy.minimum_agentic_pass_rate == 1.0
    assert policy.maximum_regression_count == 0


def test_valid_benchmark_passes_gate() -> None:
    dataset, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=load_quality_gate_policy(
            POLICY_PATH
        ),
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    assert gate.passed is True
    assert gate.failed_blocking_codes == ()
    assert gate.failed_checks == 0
    assert gate.passed_checks == gate.total_checks


def test_all_required_checks_exist() -> None:
    dataset, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    assert {
        check.code
        for check in gate.checks
    } == {
        "agentic_pass_rate",
        "agentic_average_score",
        "score_delta",
        "regression_count",
        "invalid_citation_count",
        "agentic_error_count",
        "latency_delta",
        "category_pass_rate",
        "dataset_case_count",
        "dataset_category_count",
        "offline_execution",
    }


def test_wrong_expected_case_count_fails() -> None:
    _, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=25,
        expected_category_count=12,
    )

    assert gate.passed is False

    assert (
        "dataset_case_count"
        in gate.failed_blocking_codes
    )


def test_wrong_expected_category_count_fails() -> None:
    _, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=24,
        expected_category_count=13,
    )

    assert gate.passed is False

    assert (
        "dataset_category_count"
        in gate.failed_blocking_codes
    )


def test_strict_latency_policy_can_fail() -> None:
    dataset, benchmark = make_benchmark()

    policy = replace(
        QualityGatePolicy(),
        maximum_latency_delta_ms=10.0,
    )

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=policy,
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    assert gate.passed is False
    assert gate.check("latency_delta").passed is False


def test_quality_gate_serialization() -> None:
    dataset, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    payload = quality_gate_to_dict(
        gate
    )

    assert payload["passed"] is True
    assert payload["metadata"]["offline"] is True
    assert len(payload["checks"]) == 11


def test_quality_gate_report_is_written(
    tmp_path: Path,
) -> None:
    dataset, benchmark = make_benchmark()

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    path = write_quality_gate_report(
        gate,
        tmp_path / "gate.json",
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["passed"] is True
    assert payload["failed_blocking_codes"] == []


def test_gate_matches_agentic_summary() -> None:
    dataset, benchmark = make_benchmark()

    agentic = benchmark.summary(
        BenchmarkProfile.AGENTIC
    )

    gate = evaluate_benchmark_quality_gate(
        benchmark,
        policy=QualityGatePolicy(),
        expected_case_count=len(
            dataset.cases
        ),
        expected_category_count=12,
    )

    assert (
        gate.check(
            "agentic_pass_rate"
        ).actual
        == agentic.pass_rate
    )

    assert (
        gate.check(
            "agentic_average_score"
        ).actual
        == agentic.average_score
    )

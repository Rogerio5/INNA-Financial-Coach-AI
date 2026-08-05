from __future__ import annotations

import csv
import json
from pathlib import Path

from src.evaluation.agentic_benchmark import (
    BenchmarkProfile,
    group_failures_by_code,
    load_benchmark_dataset,
    run_offline_benchmark,
    simulate_agentic_execution,
    simulate_legacy_execution,
    write_benchmark_csv,
    write_benchmark_json,
)

DATASET_PATH = Path(__file__).parent / "datasets" / "agentic_rag_v1.jsonl"


def load_result():
    dataset = load_benchmark_dataset(DATASET_PATH)

    return dataset, run_offline_benchmark(dataset)


def test_benchmark_executes_two_profiles() -> None:
    dataset, benchmark = load_result()

    assert len(dataset.cases) == 24
    assert len(benchmark.executions) == 48

    assert {execution.profile for execution in benchmark.executions} == {
        BenchmarkProfile.LEGACY,
        BenchmarkProfile.AGENTIC,
    }


def test_agentic_simulation_matches_contract() -> None:
    dataset = load_benchmark_dataset(DATASET_PATH)

    case = dataset.get("complex_budget_restructuring")

    result = simulate_agentic_execution(case)

    assert result.decision.value == case.expectations.gateway_decision.value

    assert result.security_outcome.value == case.expectations.security_outcome.value

    assert set(case.expectations.routes) <= set(result.routes)

    assert result.evidence_count >= 1
    assert result.citation_count == (result.evidence_count)


def test_legacy_simulation_is_baseline() -> None:
    dataset = load_benchmark_dataset(DATASET_PATH)

    case = dataset.get("complex_budget_restructuring")

    result = simulate_legacy_execution(case)

    assert result.mode.value == "off"
    assert result.decision.value == "legacy"
    assert result.citation_count == 0
    assert result.fallback_used is False


def test_agentic_has_higher_pass_rate() -> None:
    _, benchmark = load_result()

    legacy = benchmark.summary(BenchmarkProfile.LEGACY)

    agentic = benchmark.summary(BenchmarkProfile.AGENTIC)

    assert agentic.pass_rate > legacy.pass_rate

    assert agentic.average_score > legacy.average_score


def test_agentic_has_no_regressions() -> None:
    _, benchmark = load_result()

    assert benchmark.comparison.regressions == ()

    assert len(benchmark.comparison.improvements) > 0


def test_agentic_candidate_passes_all_cases() -> None:
    _, benchmark = load_result()

    agentic = benchmark.summary(BenchmarkProfile.AGENTIC)

    assert agentic.total_cases == 24
    assert agentic.passed_cases == 24
    assert agentic.failed_cases == 0
    assert agentic.pass_rate == 1.0


def test_comparison_contains_all_cases() -> None:
    _, benchmark = load_result()

    comparison = benchmark.comparison

    classified_cases = (
        len(comparison.improvements)
        + len(comparison.regressions)
        + len(comparison.unchanged_passes)
        + len(comparison.unchanged_failures)
    )

    assert classified_cases == 24


def test_json_report_is_written(
    tmp_path: Path,
) -> None:
    _, benchmark = load_result()

    output = write_benchmark_json(
        benchmark,
        tmp_path / "benchmark.json",
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["offline"] is True

    assert payload["live_services_used"] is False

    assert len(payload["executions"]) == 48

    assert {
        *payload["summaries"],
    } == {
        "legacy",
        "agentic",
    }


def test_csv_report_is_written(
    tmp_path: Path,
) -> None:
    _, benchmark = load_result()

    output = write_benchmark_csv(
        benchmark,
        tmp_path / "benchmark.csv",
    )

    with output.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 48

    assert {row["profile"] for row in rows} == {
        "legacy",
        "agentic",
    }


def test_failure_grouping_returns_mapping() -> None:
    _, benchmark = load_result()

    legacy_failures = group_failures_by_code(
        benchmark,
        profile=BenchmarkProfile.LEGACY,
    )

    agentic_failures = group_failures_by_code(
        benchmark,
        profile=BenchmarkProfile.AGENTIC,
    )

    assert legacy_failures
    assert agentic_failures == {}


def test_benchmark_is_deterministic() -> None:
    dataset = load_benchmark_dataset(DATASET_PATH)

    first = run_offline_benchmark(dataset)

    second = run_offline_benchmark(dataset)

    assert first.summaries == second.summaries
    assert first.comparison == second.comparison

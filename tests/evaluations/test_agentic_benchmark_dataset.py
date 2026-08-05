from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.agentic_benchmark import (
    BenchmarkCaseCategory,
    DatasetValidationError,
    ExpectedGatewayDecision,
    ExpectedSecurityOutcome,
    load_benchmark_dataset,
)

DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "agentic_rag_v1.jsonl"
)


def test_official_dataset_loads() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    assert dataset.version == "1.0.0"
    assert len(dataset.cases) == 24


def test_official_dataset_has_unique_ids() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    case_ids = [
        case.case_id
        for case in dataset.cases
    ]

    assert len(case_ids) == len(
        set(case_ids)
    )


def test_official_dataset_covers_required_categories() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    present = {
        case.category
        for case in dataset.cases
    }

    required = {
        BenchmarkCaseCategory.SIMPLE_RETRIEVAL,
        BenchmarkCaseCategory.COMPLEX_RESEARCH,
        BenchmarkCaseCategory.MULTI_SOURCE,
        BenchmarkCaseCategory.CITATION,
        BenchmarkCaseCategory.INSUFFICIENT_EVIDENCE,
        BenchmarkCaseCategory.FALLBACK,
        BenchmarkCaseCategory.TOOL_FAILURE,
        BenchmarkCaseCategory.PERMISSION,
        BenchmarkCaseCategory.INVALID_ARGUMENT,
        BenchmarkCaseCategory.SECURITY,
        BenchmarkCaseCategory.PROMPT_INJECTION,
        BenchmarkCaseCategory.GENERATED_EVIDENCE,
    }

    assert required <= present


def test_security_cases_never_expect_unrestricted_access() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    protected_categories = {
        BenchmarkCaseCategory.PERMISSION,
        BenchmarkCaseCategory.SECURITY,
        BenchmarkCaseCategory.PROMPT_INJECTION,
        BenchmarkCaseCategory.GENERATED_EVIDENCE,
    }

    protected_cases = [
        case
        for case in dataset.cases
        if case.category in protected_categories
    ]

    assert protected_cases

    assert all(
        case.expectations.security_outcome
        in {
            ExpectedSecurityOutcome.DENY,
            ExpectedSecurityOutcome.SANITIZE,
        }
        for case in protected_cases
    )


def test_reject_cases_require_no_evidence() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    rejected = [
        case
        for case in dataset.cases
        if (
            case.expectations.gateway_decision
            is ExpectedGatewayDecision.REJECT
        )
    ]

    assert rejected

    assert all(
        case.thresholds.minimum_evidence_count == 0
        for case in rejected
    )


def test_agentic_cases_require_routes() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    agentic_cases = [
        case
        for case in dataset.cases
        if (
            case.expectations.gateway_decision
            is ExpectedGatewayDecision.AGENTIC
        )
    ]

    assert agentic_cases

    assert all(
        case.expectations.routes
        for case in agentic_cases
    )


def test_all_cases_are_explicitly_synthetic() -> None:
    dataset = load_benchmark_dataset(
        DATASET_PATH
    )

    assert all(
        case.metadata.get("synthetic") is True
        for case in dataset.cases
    )

    assert all(
        case.metadata.get(
            "live_services_required"
        )
        is False
        for case in dataset.cases
    )


def test_loader_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    invalid_path = (
        tmp_path
        / "invalid.jsonl"
    )

    invalid_path.write_text(
        "{invalid-json}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        DatasetValidationError,
        match="JSON inválido",
    ):
        load_benchmark_dataset(
            invalid_path
        )


def test_loader_rejects_duplicate_ids(
    tmp_path: Path,
) -> None:
    source_lines = DATASET_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    first = json.loads(
        source_lines[0]
    )

    duplicate_path = (
        tmp_path
        / "duplicate.jsonl"
    )

    duplicate_path.write_text(
        json.dumps(
            first,
            ensure_ascii=False,
        )
        + "\n"
        + json.dumps(
            first,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="case_id duplicado",
    ):
        load_benchmark_dataset(
            duplicate_path
        )

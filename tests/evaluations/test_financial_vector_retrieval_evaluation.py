from __future__ import annotations

import pytest

from src.evaluation.financial_vector_retrieval_evaluation import (
    build_case_result,
    build_dry_run_report,
    build_evaluation_report,
    official_cases,
    validate_cases,
    validate_query_vector,
)


def sample_rows(
    expected_document_key: str,
) -> list[dict[str, object]]:
    return [
        {
            "chunk_id": f"chunk-{index}",
            "document_key": (
                expected_document_key if index == 1 else f"other-document-{index}"
            ),
            "chunk_index": index,
            "texto": "Conteudo financeiro recuperado",
            "score": 0.9 - (index * 0.05),
        }
        for index in range(1, 5)
    ]


def test_official_cases_are_valid() -> None:
    cases = official_cases()

    validate_cases(cases)

    assert len(cases) == 5


def test_query_vector_dimension() -> None:
    vector = validate_query_vector([0.001 for _ in range(3072)])

    assert len(vector) == 3072


def test_rejects_wrong_dimension() -> None:
    with pytest.raises(
        ValueError,
        match="Dimensao",
    ):
        validate_query_vector([0.1, 0.2])


def test_case_result_passes_top1() -> None:
    case = official_cases()[0]

    result = build_case_result(
        case=case,
        rows=sample_rows(case.expected_document_key),
    )

    assert result.top1_passed is True
    assert result.expected_document_found_in_top_k is True


def test_evaluation_report_passes() -> None:
    results = tuple(
        build_case_result(
            case=case,
            rows=sample_rows(case.expected_document_key),
        )
        for case in official_cases()
    )

    report = build_evaluation_report(results)

    assert report["case_count"] == 5
    assert report["top1_pass_count"] == 5
    assert report["top1_accuracy"] == 1.0
    assert report["top_k_pass_count"] == 5
    assert report["top_k_recall"] == 1.0
    assert report["evaluation_status"] == "passed"
    assert report["database_write_executed"] is False
    assert report["transaction_read_only"] is True
    assert report["neon_changed"] is False


def test_dry_run_report_passes() -> None:
    report = build_dry_run_report(official_cases())

    assert report["case_count"] == 5
    assert report["top_k"] == 4
    assert report["projected_gemini_call_count"] == 5
    assert report["embedding_dimension"] == 3072
    assert report["dry_run_status"] == "passed"
    assert report["gemini_call_count"] == 0
    assert report["database_connected"] is False
    assert report["neon_changed"] is False


def test_vector_search_sql_escapes_percent_for_psycopg() -> None:
    from scripts.evaluation.run_financial_vector_retrieval_evaluation import (
        VECTOR_SEARCH_SQL,
    )

    assert "LIKE 'inna-edu-%%'" in VECTOR_SEARCH_SQL
    assert "LIKE 'inna-sec-%%'" in VECTOR_SEARCH_SQL
    assert "LIKE 'inna-edu-%'" not in VECTOR_SEARCH_SQL.replace(
        "%%",
        "",
    )

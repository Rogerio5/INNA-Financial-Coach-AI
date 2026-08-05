from __future__ import annotations

import json
from pathlib import Path

from src.evaluation.retrieval_real_judgment import (
    deduplicate_results,
    evaluate_real_textual_report,
)


def test_deduplicate_results_removes_equal_content() -> None:
    results = [
        {
            "rank": 1,
            "chunk_id": "chunk-a",
            "chunk_index": 4,
            "text_preview": "Reserva financeira.",
        },
        {
            "rank": 2,
            "chunk_id": "chunk-b",
            "chunk_index": 4,
            "text_preview": "  Reserva   financeira. ",
        },
    ]

    unique = deduplicate_results(results)

    assert len(unique) == 1
    assert unique[0]["original_rank"] == 1


def test_deduplicate_preserves_different_content() -> None:
    results = [
        {
            "rank": 1,
            "chunk_index": 4,
            "text_preview": "Reserva financeira.",
        },
        {
            "rank": 2,
            "chunk_index": 1,
            "text_preview": "Pix suspeito.",
        },
    ]

    unique = deduplicate_results(results)

    assert len(unique) == 2


def test_real_report_calculates_metrics(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.json"
    judgment_path = tmp_path / "judgment.json"

    source_path.write_text(
        json.dumps(
            {
                "questions": [
                    {
                        "case_id": "case-001",
                        "question": "Pergunta",
                        "top_k": 4,
                        "results": [
                            {
                                "rank": 1,
                                "chunk_index": 4,
                                "text_preview": "Correto",
                            },
                            {
                                "rank": 2,
                                "chunk_index": 4,
                                "text_preview": "Correto",
                            },
                            {
                                "rank": 3,
                                "chunk_index": 1,
                                "text_preview": "Errado",
                            },
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    judgment_path.write_text(
        json.dumps(
            {
                "name": "test",
                "binary_relevance_threshold": 2,
                "cases": {"case-001": {"chunk_index_grades": {"4": 3, "1": 0}}},
            }
        ),
        encoding="utf-8",
    )

    report = evaluate_real_textual_report(
        source_report_path=source_path,
        judgment_path=judgment_path,
    )

    case = report.cases[0]

    assert case.original_result_count == 3
    assert case.deduplicated_result_count == 2
    assert case.duplicate_count == 1
    assert case.metrics.hit_rate == 1.0
    assert case.metrics.recall == 1.0
    assert case.coverage_status == "strong_relevance_found"


def test_partial_only_does_not_count_as_strong(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.json"
    judgment_path = tmp_path / "judgment.json"

    source_path.write_text(
        json.dumps(
            {
                "questions": [
                    {
                        "case_id": "case-001",
                        "question": "Pergunta",
                        "top_k": 4,
                        "results": [
                            {
                                "rank": 1,
                                "chunk_index": 3,
                                "text_preview": "Parcial",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    judgment_path.write_text(
        json.dumps(
            {
                "name": "test",
                "binary_relevance_threshold": 2,
                "cases": {"case-001": {"chunk_index_grades": {"3": 1}}},
            }
        ),
        encoding="utf-8",
    )

    report = evaluate_real_textual_report(
        source_report_path=source_path,
        judgment_path=judgment_path,
    )

    case = report.cases[0]

    assert case.coverage_status == "partial_relevance_only"
    assert case.metrics.hit_rate == 0.0
    assert case.metrics.recall == 0.0
    assert case.metrics.ndcg == 1.0
    assert report.quality_gate.passed is False

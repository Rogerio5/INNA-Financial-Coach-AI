from __future__ import annotations

import pytest

from scripts.run_auto_merging_retrieval_ab import (
    VARIANTS,
    _inspect_results,
    _variants_for_dataset_index,
    build_summary,
)


def test_variants_are_isolated():
    by_name = {
        item.name: item
        for item in VARIANTS
    }

    baseline = by_name[
        "hybrid_baseline"
    ]

    sentence = by_name[
        "hybrid_sentence_window"
    ]

    auto = by_name[
        "hybrid_auto_merging"
    ]

    assert baseline.sentence_window_enabled is False
    assert baseline.auto_merging_enabled is False

    assert sentence.sentence_window_enabled is True
    assert sentence.auto_merging_enabled is False

    assert auto.sentence_window_enabled is False
    assert auto.auto_merging_enabled is True


def test_result_inspection_tracks_auto_merging():
    results = [
        {
            "documento_id": 10,
            "chunk_index": 0,
            "chunk_text": "abc",
            "auto_merging_applied": True,
            "auto_merging_child_count": 2,
        },
        {
            "documento_id": 20,
            "chunk_index": 3,
            "chunk_text": "defgh",
            "auto_merging_applied": False,
        },
    ]

    inspection = _inspect_results(results)

    assert inspection["result_count"] == 2
    assert inspection["context_characters"] == 8
    assert inspection["unique_document_count"] == 2

    assert (
        inspection[
            "auto_merging_applied_count"
        ]
        == 1
    )

    assert (
        inspection[
            "auto_merging_child_count_total"
        ]
        == 2
    )


def test_result_inspection_tracks_sentence_window():
    results = [
        {
            "documento_key": "doc-a",
            "chunk_text": "contexto",
            "sentence_window_applied": True,
        }
    ]

    inspection = _inspect_results(results)

    assert (
        inspection[
            "sentence_window_applied_count"
        ]
        == 1
    )


def test_summary_compares_candidates_to_baseline():
    rows = [
        {
            "variant": "hybrid_baseline",
            "retrieval_total_ms": 100.0,
            "outer_elapsed_ms": 101.0,
            "vector_retrieval_ms": 50.0,
            "text_retrieval_ms": 20.0,
            "rrf_ms": 1.0,
            "rerank_ms": 10.0,
            "sentence_window_ms": 0.0,
            "result_count": 3,
            "context_characters": 1000,
            "unique_document_count": 2,
            "auto_merging_applied_count": 0,
            "auto_merging_child_count_total": 0,
            "sentence_window_applied_count": 0,
        },
        {
            "variant": "hybrid_sentence_window",
            "retrieval_total_ms": 130.0,
            "outer_elapsed_ms": 131.0,
            "vector_retrieval_ms": 50.0,
            "text_retrieval_ms": 20.0,
            "rrf_ms": 1.0,
            "rerank_ms": 10.0,
            "sentence_window_ms": 30.0,
            "result_count": 3,
            "context_characters": 1500,
            "unique_document_count": 2,
            "auto_merging_applied_count": 0,
            "auto_merging_child_count_total": 0,
            "sentence_window_applied_count": 2,
        },
        {
            "variant": "hybrid_auto_merging",
            "retrieval_total_ms": 105.0,
            "outer_elapsed_ms": 106.0,
            "vector_retrieval_ms": 50.0,
            "text_retrieval_ms": 20.0,
            "rrf_ms": 1.0,
            "rerank_ms": 10.0,
            "sentence_window_ms": 0.0,
            "result_count": 2,
            "context_characters": 1200,
            "unique_document_count": 2,
            "auto_merging_applied_count": 1,
            "auto_merging_child_count_total": 2,
            "sentence_window_applied_count": 0,
        },
    ]

    summary = {
        item["variant"]: item
        for item in build_summary(rows)
    }

    sentence = summary[
        "hybrid_sentence_window"
    ]

    auto = summary[
        "hybrid_auto_merging"
    ]

    assert (
        sentence[
            "delta_retrieval_ms_vs_baseline"
        ]
        == pytest.approx(30.0)
    )

    assert (
        sentence[
            "delta_context_chars_vs_baseline"
        ]
        == pytest.approx(500.0)
    )

    assert (
        auto[
            "delta_retrieval_ms_vs_baseline"
        ]
        == pytest.approx(5.0)
    )

    assert (
        auto[
            "delta_results_vs_baseline"
        ]
        == pytest.approx(-1.0)
    )


def test_variant_order_rotates_by_dataset_index():
    first = [
        item.name
        for item in _variants_for_dataset_index(1)
    ]

    second = [
        item.name
        for item in _variants_for_dataset_index(2)
    ]

    third = [
        item.name
        for item in _variants_for_dataset_index(3)
    ]

    assert first == [
        "hybrid_baseline",
        "hybrid_sentence_window",
        "hybrid_auto_merging",
    ]

    assert second == [
        "hybrid_sentence_window",
        "hybrid_auto_merging",
        "hybrid_baseline",
    ]

    assert third == [
        "hybrid_auto_merging",
        "hybrid_baseline",
        "hybrid_sentence_window",
    ]

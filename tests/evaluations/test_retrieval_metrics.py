from __future__ import annotations

import pytest

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsResult,
    evaluate_retrieval_case,
    hit_rate_at_k,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_hit_rate_at_k_detects_relevant_document() -> None:
    score = hit_rate_at_k(
        ["doc_08", "doc_03", "doc_10", "doc_02"],
        ["doc_03"],
        k=4,
    )

    assert score == 1.0


def test_hit_rate_at_k_returns_zero_without_hit() -> None:
    score = hit_rate_at_k(
        ["doc_08", "doc_10"],
        ["doc_03"],
        k=2,
    )

    assert score == 0.0


def test_recall_at_k_calculates_relevant_coverage() -> None:
    score = recall_at_k(
        ["doc_03", "doc_07", "doc_10", "doc_11"],
        ["doc_02", "doc_03", "doc_07"],
        k=4,
    )

    assert score == pytest.approx(2 / 3)


def test_precision_at_k_calculates_useful_results() -> None:
    score = precision_at_k(
        ["doc_03", "doc_07", "doc_10", "doc_11"],
        ["doc_02", "doc_03", "doc_07"],
        k=4,
    )

    assert score == pytest.approx(0.5)


def test_precision_uses_number_actually_retrieved() -> None:
    score = precision_at_k(
        ["doc_03", "doc_10"],
        ["doc_03"],
        k=4,
    )

    assert score == pytest.approx(0.5)


def test_reciprocal_rank_uses_first_relevant_position() -> None:
    score = reciprocal_rank(
        ["doc_08", "doc_10", "doc_03", "doc_07"],
        ["doc_03", "doc_07"],
    )

    assert score == pytest.approx(1 / 3)


def test_mean_reciprocal_rank_averages_cases() -> None:
    score = mean_reciprocal_rank(
        [
            (
                ["doc_a", "doc_b"],
                ["doc_a"],
            ),
            (
                ["doc_x", "doc_y"],
                ["doc_y"],
            ),
            (
                ["doc_m", "doc_n"],
                ["doc_z"],
            ),
        ]
    )

    assert score == pytest.approx((1.0 + 0.5 + 0.0) / 3)


def test_ndcg_is_one_for_ideal_ranking() -> None:
    score = ndcg_at_k(
        ["doc_a", "doc_b", "doc_c"],
        {
            "doc_a": 3,
            "doc_b": 2,
            "doc_c": 1,
        },
        k=3,
    )

    assert score == pytest.approx(1.0)


def test_ndcg_penalizes_inverted_ranking() -> None:
    score = ndcg_at_k(
        ["doc_c", "doc_b", "doc_a"],
        {
            "doc_a": 3,
            "doc_b": 2,
            "doc_c": 1,
        },
        k=3,
    )

    assert 0.0 < score < 1.0


def test_duplicate_retrieved_ids_are_counted_once() -> None:
    result = evaluate_retrieval_case(
        retrieved_document_ids=[
            "doc_a",
            "doc_a",
            "doc_b",
        ],
        relevant_document_ids=["doc_a"],
        graded_relevance={"doc_a": 3},
        k=2,
    )

    assert result.hit_rate == 1.0
    assert result.recall == 1.0
    assert result.precision == pytest.approx(0.5)


def test_empty_relevance_returns_zero_scores() -> None:
    result = evaluate_retrieval_case(
        retrieved_document_ids=["doc_a", "doc_b"],
        relevant_document_ids=[],
        graded_relevance={},
        k=2,
    )

    assert result.hit_rate == 0.0
    assert result.recall == 0.0
    assert result.precision == 0.0
    assert result.reciprocal_rank == 0.0
    assert result.ndcg == 0.0


def test_evaluate_retrieval_case_returns_consolidated_result() -> None:
    result = evaluate_retrieval_case(
        retrieved_document_ids=[
            "doc_reserva_01",
            "doc_orcamento_03",
            "doc_reserva_02",
            "doc_cartao_01",
        ],
        relevant_document_ids=[
            "doc_reserva_01",
            "doc_reserva_02",
        ],
        graded_relevance={
            "doc_reserva_01": 3,
            "doc_reserva_02": 2,
        },
        k=4,
    )

    assert isinstance(result, RetrievalMetricsResult)
    assert result.k == 4
    assert result.hit_rate == 1.0
    assert result.recall == 1.0
    assert result.precision == pytest.approx(0.5)
    assert result.reciprocal_rank == 1.0
    assert 0.0 < result.ndcg <= 1.0

    payload = result.as_dict()

    assert payload["k"] == 4
    assert payload["hit_rate_at_4"] == 1.0
    assert payload["recall_at_4"] == 1.0


@pytest.mark.parametrize("invalid_k", [0, -1])
def test_metrics_reject_non_positive_k(invalid_k: int) -> None:
    with pytest.raises(ValueError, match="maior que zero"):
        recall_at_k(
            ["doc_a"],
            ["doc_a"],
            k=invalid_k,
        )


def test_metrics_reject_boolean_k() -> None:
    with pytest.raises(TypeError, match="numero inteiro"):
        precision_at_k(
            ["doc_a"],
            ["doc_a"],
            k=True,
        )


def test_ndcg_rejects_negative_relevance() -> None:
    with pytest.raises(
        ValueError,
        match="nao podem ser negativos",
    ):
        ndcg_at_k(
            ["doc_a"],
            {"doc_a": -1},
            k=1,
        )


def test_blank_document_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="nao podem ser vazios",
    ):
        hit_rate_at_k(
            ["  "],
            ["doc_a"],
            k=1,
        )

from __future__ import annotations

import pytest

from src.services.rag.retrieval_trace import (
    build_result_traces,
    start_retrieval_trace,
)


def test_starts_trace_with_unique_identifier():
    trace = start_retrieval_trace(
        query="Como criar reserva?",
        language="pt",
        top_k=4,
    )

    assert trace.trace_id
    assert trace.query == ("Como criar reserva?")
    assert trace.language == "pt"
    assert trace.top_k == 4
    assert trace.finished_at is None
    assert trace.total_time_ms is None


def test_rejects_empty_query():
    with pytest.raises(
        ValueError,
        match="não pode estar vazia",
    ):
        start_retrieval_trace(query="   ")


@pytest.mark.parametrize(
    "top_k",
    (
        0,
        -1,
    ),
)
def test_rejects_invalid_top_k(
    top_k: int,
):
    with pytest.raises(
        ValueError,
        match="maior que zero",
    ):
        start_retrieval_trace(
            query="reserva",
            top_k=top_k,
        )


def test_builds_structured_result_trace():
    results = [
        {
            "id": 10,
            "documento_id": 5,
            "titulo": "Reserva",
            "fonte": "guia.md",
            "origem_busca": [
                "vetorial",
                "textual",
            ],
            "score": 0.80,
            "score_hibrido": 1.10,
            "score_rerank": 1.35,
        }
    ]

    traces = build_result_traces(results)

    assert len(traces) == 1

    item = traces[0]

    assert item.position == 1
    assert item.chunk_id == 10
    assert item.document_id == 5
    assert item.title == "Reserva"
    assert item.source == "guia.md"
    assert item.search_origins == (
        "vetorial",
        "textual",
    )
    assert item.score == 0.80
    assert item.hybrid_score == 1.10
    assert item.rerank_score == 1.35


def test_accepts_string_search_origin():
    traces = build_result_traces(
        [
            {
                "id": 1,
                "origem_busca": "textual",
            }
        ]
    )

    assert traces[0].search_origins == ("textual",)


def test_invalid_score_becomes_none():
    traces = build_result_traces(
        [
            {
                "id": 1,
                "score": "invalid",
            }
        ]
    )

    assert traces[0].score is None


def test_finish_records_results_and_time():
    trace = start_retrieval_trace(
        query="cartão de crédito",
        top_k=2,
    )

    trace.finish(
        [
            {
                "id": 1,
                "score": 0.91,
            },
            {
                "id": 2,
                "score": 0.82,
            },
        ],
        search_mode=("rag_hibrido_rerank"),
    )

    assert trace.finished_at
    assert trace.total_time_ms is not None
    assert trace.total_time_ms >= 0
    assert trace.search_mode == ("rag_hibrido_rerank")
    assert len(trace.results) == 2


def test_trace_can_be_serialized():
    trace = start_retrieval_trace(
        query="orçamento",
        top_k=1,
    )

    trace.finish(
        [
            {
                "id": 15,
                "titulo": "Orçamento",
                "score_rerank": 1.2,
            }
        ],
        search_mode="hybrid",
    )

    payload = trace.to_dict()

    assert payload["trace_id"]
    assert payload["query"] == "orçamento"
    assert payload["search_mode"] == "hybrid"
    assert payload["results_total"] == 1
    assert payload["results"][0]["position"] == 1
    assert payload["results"][0]["rerank_score"] == 1.2


def test_preserves_final_ranking_positions():
    traces = build_result_traces(
        [
            {
                "id": 30,
                "score_rerank": 1.5,
            },
            {
                "id": 20,
                "score_rerank": 1.2,
            },
        ]
    )

    assert traces[0].position == 1
    assert traces[0].chunk_id == 30
    assert traces[1].position == 2
    assert traces[1].chunk_id == 20

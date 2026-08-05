from __future__ import annotations

from src.services.rag.sentence_window import (
    build_sentence_window,
    expand_result_with_sentence_window,
    split_sentences,
)


def test_split_sentences_preserves_content() -> None:
    text = "Primeira frase. Segunda frase! Terceira frase?"

    assert split_sentences(text) == [
        "Primeira frase.",
        "Segunda frase!",
        "Terceira frase?",
    ]


def test_build_sentence_window_uses_neighbor_sentences() -> None:
    chunks = [
        {
            "chunk_index": 0,
            "chunk_text": ("Organize primeiro o orçamento."),
        },
        {
            "chunk_index": 1,
            "chunk_text": (
                "A reserva financeira protege "
                "contra imprevistos. "
                "Comece guardando um valor pequeno. "
                "Automatize o depósito quando possível."
            ),
        },
        {
            "chunk_index": 2,
            "chunk_text": ("Revise o valor todos os meses."),
        },
    ]

    result = build_sentence_window(
        query=("como começar uma reserva financeira"),
        chunks=chunks,
        matched_chunk_index=1,
        window_size=1,
    )

    assert "reserva financeira" in result["text"].lower()

    assert result["sentence_count"] == 3

    assert 1 in result["chunk_indices"]


def test_expand_result_preserves_matched_text() -> None:
    result = {
        "id": 10,
        "fonte": "financeiro.md",
        "idioma": "pt",
        "chunk_index": 1,
        "chunk_text": (
            "A reserva financeira ajuda em emergências. Comece com um valor pequeno."
        ),
        "modo_busca": ("rag_hibrido_pgvector_text_neon_rerank"),
    }

    chunks = [
        {
            "chunk_index": 0,
            "chunk_text": ("Mapeie sua renda e seus gastos."),
        },
        result,
        {
            "chunk_index": 2,
            "chunk_text": ("Revise a reserva periodicamente."),
        },
    ]

    expanded = expand_result_with_sentence_window(
        query=("como começar reserva financeira"),
        result=result,
        chunks=chunks,
        window_size=1,
    )

    assert expanded["sentence_window_applied"] is True

    assert expanded["matched_chunk_text"] == result["chunk_text"]

    assert expanded["chunk_text"] == expanded["sentence_window_text"]

    assert expanded["modo_busca"].endswith("_sentence_window")


def test_empty_result_is_not_expanded() -> None:
    expanded = expand_result_with_sentence_window(
        query="reserva",
        result={
            "chunk_index": 0,
        },
        chunks=[],
        window_size=2,
    )

    assert expanded["sentence_window_applied"] is False


def test_window_respects_max_characters() -> None:
    chunks = [
        {
            "chunk_index": 0,
            "chunk_text": (
                "Reserva financeira é importante. "
                + ("Planejamento financeiro ajuda. " * 100)
            ),
        }
    ]

    result = build_sentence_window(
        query="reserva financeira",
        chunks=chunks,
        matched_chunk_index=0,
        window_size=8,
        max_characters=350,
    )

    assert len(result["text"]) <= 350

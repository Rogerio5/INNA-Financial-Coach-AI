from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.evaluation.retrieval_ab import (
    compare_retrieval_variants,
    run_retrieval_ab_suite,
)


def _fake_search_factory(
    calls: list[bool],
):
    def fake_search(
        query: str,
        idioma: str = "pt",
        top_k: int = 4,
        *,
        sentence_window_enabled: (bool | None) = None,
    ) -> list[dict[str, Any]]:
        del query
        del idioma
        del top_k

        enabled = bool(sentence_window_enabled)

        calls.append(enabled)

        first_text = "Reserva financeira ajuda em imprevistos."

        if enabled:
            first_text = (
                "Mapeie suas despesas. "
                "Reserva financeira ajuda "
                "em imprevistos. "
                "Comece com um valor pequeno."
            )

        return [
            {
                "id": 1,
                "fonte": "reserva.md",
                "chunk_index": 2,
                "chunk_text": first_text,
                "matched_chunk_text": ("Reserva financeira ajuda em imprevistos."),
                "sentence_window_applied": enabled,
                "sentence_window_version": ("native_v1" if enabled else None),
                "modo_busca": ("hybrid_sentence_window" if enabled else "hybrid"),
                "score": 0.95,
            },
            {
                "id": 2,
                "fonte": "orcamento.md",
                "chunk_index": 4,
                "chunk_text": ("O orçamento organiza renda e despesas."),
                "sentence_window_applied": enabled,
                "score": 0.85,
            },
        ]

    return fake_search


def test_compare_executes_baseline_and_window() -> None:
    calls: list[bool] = []

    result = compare_retrieval_variants(
        query=("Como começar uma reserva?"),
        search_function=(_fake_search_factory(calls)),
    )

    assert calls == [
        False,
        True,
    ]

    assert result["variant_a"]["sentence_window_enabled"] is False

    assert result["variant_b"]["sentence_window_enabled"] is True

    assert result["comparison"]["quality_decision"] == "pending_rag_triad"


def test_compare_calculates_overlap_and_context_delta() -> None:
    result = compare_retrieval_variants(
        query="reserva financeira",
        search_function=(_fake_search_factory([])),
    )

    comparison = result["comparison"]

    assert comparison["result_overlap_ratio"] == 1.0

    assert comparison["same_top_result"] is True

    assert comparison["context_character_delta"] > 0

    assert comparison["sentence_window_coverage"] == 1.0


def test_report_does_not_store_text_by_default(
    tmp_path: Path,
) -> None:
    result = run_retrieval_ab_suite(
        queries=["Como criar uma reserva?"],
        output_directory=tmp_path,
        search_function=(_fake_search_factory([])),
    )

    payload = json.loads(
        Path(result["json_path"]).read_text(
            encoding="utf-8",
        )
    )

    preview = payload["cases"][0]["variant_a"]["results_preview"][0]

    assert "text_preview" not in preview

    assert len(preview["context_sha256"]) == 64


def test_suite_creates_versioned_reports_and_history(
    tmp_path: Path,
) -> None:
    result = run_retrieval_ab_suite(
        queries=[
            "Pergunta número um",
            "Pergunta número dois",
        ],
        output_directory=tmp_path,
        run_label="unit-test",
        search_function=(_fake_search_factory([])),
    )

    assert Path(result["json_path"]).is_file()

    assert Path(result["markdown_path"]).is_file()

    history_path = Path(result["history_path"])

    assert history_path.is_file()

    history_lines = history_path.read_text(
        encoding="utf-8",
    ).splitlines()

    assert len(history_lines) == 1

    history = json.loads(history_lines[0])

    assert history["completed_count"] == 2

    assert history["failed_count"] == 0


def test_suite_rejects_empty_questions(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=("Nenhuma pergunta válida"),
    ):
        run_retrieval_ab_suite(
            queries=[
                "",
                "a",
            ],
            output_directory=tmp_path,
            search_function=(_fake_search_factory([])),
        )

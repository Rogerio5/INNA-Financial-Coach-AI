from __future__ import annotations

import pytest

from src.services.rag.auto_merging import (
    AUTO_MERGING_POLICY,
    auto_merge_results,
)


def _result(
    *,
    document_id: int,
    chunk_index: int,
    chunk_id: str,
    text: str,
    score: float = 1.0,
) -> dict:
    return {
        "documento_id": document_id,
        "documento_key": "inna-test-doc",
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "chunk_text": text,
        "score": score,
    }


def test_auto_merging_merges_sibling_chunks():
    results = [
        _result(
            document_id=28,
            chunk_index=0,
            chunk_id="c0",
            text="Primeiro trecho.",
        ),
        _result(
            document_id=28,
            chunk_index=1,
            chunk_id="c1",
            text="Segundo trecho.",
        ),
        _result(
            document_id=28,
            chunk_index=2,
            chunk_id="c2",
            text="Terceiro trecho.",
        ),
    ]

    merged = auto_merge_results(
        results,
        parent_size=3,
        min_children=2,
    )

    assert len(merged) == 1

    item = merged[0]

    assert item["auto_merging_applied"] is True
    assert (
        item["auto_merging_policy"]
        == AUTO_MERGING_POLICY
    )
    assert item["auto_merging_parent_index"] == 0
    assert item["auto_merging_child_count"] == 3
    assert item["auto_merging_child_indexes"] == [
        0,
        1,
        2,
    ]
    assert item["auto_merging_child_chunk_ids"] == [
        "c0",
        "c1",
        "c2",
    ]
    assert item["chunk_text"] == (
        "Primeiro trecho.\n\n"
        "Segundo trecho.\n\n"
        "Terceiro trecho."
    )


def test_auto_merging_does_not_cross_parent_boundary():
    results = [
        _result(
            document_id=28,
            chunk_index=2,
            chunk_id="c2",
            text="Final do parent zero.",
        ),
        _result(
            document_id=28,
            chunk_index=3,
            chunk_id="c3",
            text="Inicio do parent um.",
        ),
    ]

    merged = auto_merge_results(
        results,
        parent_size=3,
        min_children=2,
    )

    assert len(merged) == 2

    assert all(
        item["auto_merging_applied"] is False
        for item in merged
    )

    assert all(
        item["auto_merging_skip_reason"]
        == "insufficient_sibling_hits"
        for item in merged
    )


def test_auto_merging_does_not_cross_document_boundary():
    results = [
        _result(
            document_id=28,
            chunk_index=0,
            chunk_id="doc28-c0",
            text="Documento 28.",
        ),
        _result(
            document_id=29,
            chunk_index=1,
            chunk_id="doc29-c1",
            text="Documento 29.",
        ),
    ]

    merged = auto_merge_results(
        results,
        parent_size=3,
        min_children=2,
    )

    assert len(merged) == 2

    assert all(
        item["auto_merging_applied"] is False
        for item in merged
    )


def test_auto_merging_preserves_safe_fallback_for_large_context():
    results = [
        _result(
            document_id=28,
            chunk_index=0,
            chunk_id="c0",
            text="A" * 100,
        ),
        _result(
            document_id=28,
            chunk_index=1,
            chunk_id="c1",
            text="B" * 100,
        ),
    ]

    merged = auto_merge_results(
        results,
        parent_size=3,
        min_children=2,
        max_characters=150,
    )

    assert len(merged) == 2

    assert all(
        item["auto_merging_applied"] is False
        for item in merged
    )

    assert all(
        item["auto_merging_skip_reason"]
        == "parent_context_too_large_or_empty"
        for item in merged
    )


def test_auto_merging_deduplicates_same_chunk():
    duplicated = _result(
        document_id=28,
        chunk_index=0,
        chunk_id="same-chunk",
        text="Mesmo conteúdo.",
    )

    results = [
        duplicated,
        dict(duplicated),
        _result(
            document_id=28,
            chunk_index=1,
            chunk_id="c1",
            text="Segundo conteúdo.",
        ),
    ]

    merged = auto_merge_results(
        results,
        parent_size=3,
        min_children=2,
    )

    assert len(merged) == 1

    item = merged[0]

    assert item["auto_merging_child_count"] == 2
    assert item["auto_merging_child_chunk_ids"] == [
        "same-chunk",
        "c1",
    ]


def test_auto_merging_preserves_unstructured_result():
    results = [
        {
            "chunk_text": "Resultado legado.",
            "score": 0.8,
        }
    ]

    merged = auto_merge_results(results)

    assert len(merged) == 1
    assert merged[0]["chunk_text"] == (
        "Resultado legado."
    )
    assert (
        merged[0]["auto_merging_applied"]
        is False
    )
    assert (
        merged[0]["auto_merging_skip_reason"]
        == "missing_structured_identity"
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"parent_size": 1},
            "parent_size",
        ),
        (
            {"min_children": 1},
            "min_children",
        ),
        (
            {
                "parent_size": 2,
                "min_children": 3,
            },
            "min_children",
        ),
        (
            {"max_characters": 0},
            "max_characters",
        ),
    ],
)
def test_auto_merging_validates_configuration(
    kwargs,
    message,
):
    with pytest.raises(
        ValueError,
        match=message,
    ):
        auto_merge_results(
            [],
            **kwargs,
        )

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.evaluation.financial_gemini_embedding_pilot import (
    analyze_embedding,
    choose_database_dimension,
    extract_embedding_values,
    select_pilot_chunk,
)


def sample_chunks() -> list[dict[str, object]]:
    return [
        {
            "chunk_id": f"chunk-{index:03d}",
            "documento_key": f"document-{index:03d}",
            "chunk_index": 1,
            "texto": f"Conteudo financeiro {index}",
            "metadata": {
                "document_title": f"Documento {index}",
            },
        }
        for index in range(1, 36)
    ]


def test_choose_database_dimension() -> None:
    assert choose_database_dimension([768]) == 768


def test_rejects_empty_dimensions() -> None:
    with pytest.raises(ValueError):
        choose_database_dimension([])


def test_rejects_multiple_dimensions() -> None:
    with pytest.raises(ValueError):
        choose_database_dimension([768, 1536])


def test_selects_first_chunk_deterministically() -> None:
    pilot = select_pilot_chunk(
        list(reversed(sample_chunks())),
        expected_dimension=768,
    )

    assert pilot.chunk_id == "chunk-001"
    assert pilot.documento_key == "document-001"
    assert pilot.expected_dimension == 768


def test_extract_embedding_values() -> None:
    response = SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1, 0.2, 0.3])])

    assert extract_embedding_values(response) == (
        0.1,
        0.2,
        0.3,
    )


def test_valid_embedding_passes() -> None:
    result = analyze_embedding(
        expected_dimension=3,
        vector=[0.1, 0.2, 0.3],
    )

    assert result.actual_dimension == 3
    assert result.finite_value_count == 3
    assert result.l2_norm > 0
    assert result.vector == (0.1, 0.2, 0.3)
    assert result.as_dict()["vector"] == [0.1, 0.2, 0.3]
    assert result.passed is True


def test_wrong_dimension_fails() -> None:
    result = analyze_embedding(
        expected_dimension=4,
        vector=[0.1, 0.2, 0.3],
    )

    assert result.actual_dimension == 3
    assert result.passed is False

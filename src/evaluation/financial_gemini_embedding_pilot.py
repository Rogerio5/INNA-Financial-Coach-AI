"""Validacao do piloto de embedding Gemini da base financeira."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_TASK_TYPE = "RETRIEVAL_DOCUMENT"


@dataclass(frozen=True, slots=True)
class EmbeddingPilotInput:
    chunk_id: str
    documento_key: str
    document_title: str
    text: str
    expected_dimension: int
    model: str = EMBEDDING_MODEL
    task_type: str = EMBEDDING_TASK_TYPE

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EmbeddingPilotResult:
    expected_dimension: int
    actual_dimension: int
    finite_value_count: int
    zero_value_count: int
    minimum_value: float
    maximum_value: float
    l2_norm: float
    vector: tuple[float, ...]
    passed: bool

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["vector"] = list(self.vector)
        return payload


def choose_database_dimension(
    dimensions: Sequence[int],
) -> int:
    valid = sorted({int(dimension) for dimension in dimensions if int(dimension) > 0})

    if not valid:
        raise ValueError("Nenhuma dimensao de embedding foi encontrada.")

    if len(valid) != 1:
        raise ValueError(
            "Multiplas dimensoes encontradas: " + ",".join(str(item) for item in valid)
        )

    return valid[0]


def select_pilot_chunk(
    chunks: Sequence[Mapping[str, Any]],
    *,
    expected_dimension: int,
) -> EmbeddingPilotInput:
    if len(chunks) != 35:
        raise ValueError("O plano deve possuir exatamente 35 chunks.")

    ordered = sorted(
        chunks,
        key=lambda item: (
            str(item["documento_key"]),
            int(item["chunk_index"]),
        ),
    )

    selected = ordered[0]
    metadata = dict(selected.get("metadata", {}))

    text = str(selected["texto"]).strip()

    if not text:
        raise ValueError("O chunk piloto nao possui texto.")

    title = str(
        metadata.get(
            "document_title",
            selected["documento_key"],
        )
    ).strip()

    return EmbeddingPilotInput(
        chunk_id=str(selected["chunk_id"]),
        documento_key=str(selected["documento_key"]),
        document_title=title,
        text=text,
        expected_dimension=expected_dimension,
    )


def extract_embedding_values(
    response: object,
) -> tuple[float, ...]:
    embeddings = getattr(response, "embeddings", None)

    if not embeddings:
        raise ValueError("A resposta nao possui embeddings.")

    values = getattr(embeddings[0], "values", None)

    if values is None:
        raise ValueError("A resposta nao possui valores de embedding.")

    vector = tuple(float(value) for value in values)

    if not vector:
        raise ValueError("O vetor retornado esta vazio.")

    return vector


def analyze_embedding(
    *,
    expected_dimension: int,
    vector: Sequence[float],
) -> EmbeddingPilotResult:
    values = tuple(float(value) for value in vector)

    if not values:
        raise ValueError("O vetor nao pode estar vazio.")

    finite_count = sum(1 for value in values if math.isfinite(value))

    zero_count = sum(1 for value in values if value == 0.0)

    norm = math.sqrt(sum(value * value for value in values))

    passed = (
        len(values) == expected_dimension and finite_count == len(values) and norm > 0.0
    )

    return EmbeddingPilotResult(
        expected_dimension=expected_dimension,
        actual_dimension=len(values),
        finite_value_count=finite_count,
        zero_value_count=zero_count,
        minimum_value=min(values),
        maximum_value=max(values),
        l2_norm=norm,
        vector=values,
        passed=passed,
    )


__all__ = [
    "EMBEDDING_MODEL",
    "EMBEDDING_TASK_TYPE",
    "EmbeddingPilotInput",
    "EmbeddingPilotResult",
    "analyze_embedding",
    "choose_database_dimension",
    "extract_embedding_values",
    "select_pilot_chunk",
]

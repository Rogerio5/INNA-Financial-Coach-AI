"""Métricas determinísticas para avaliação offline de recuperação RAG.

Este módulo não realiza chamadas para LLMs, bancos de dados ou serviços
externos. Ele recebe identificadores previamente recuperados e calcula
métricas reproduzíveis de qualidade do ranking.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import log2

DocumentId = str


def _validate_k(k: int) -> None:
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k deve ser um numero inteiro.")

    if k <= 0:
        raise ValueError("k deve ser maior que zero.")


def _unique_document_ids(
    document_ids: Sequence[DocumentId],
) -> tuple[DocumentId, ...]:
    """Remove duplicatas preservando a primeira posição no ranking."""

    unique_ids: list[DocumentId] = []
    seen: set[DocumentId] = set()

    for document_id in document_ids:
        normalized_id = str(document_id).strip()

        if not normalized_id:
            raise ValueError(
                "Os identificadores de documentos nao podem ser vazios."
            )

        if normalized_id in seen:
            continue

        seen.add(normalized_id)
        unique_ids.append(normalized_id)

    return tuple(unique_ids)


def _relevant_set(
    relevant_document_ids: Sequence[DocumentId],
) -> frozenset[DocumentId]:
    return frozenset(_unique_document_ids(relevant_document_ids))


def hit_rate_at_k(
    retrieved_document_ids: Sequence[DocumentId],
    relevant_document_ids: Sequence[DocumentId],
    *,
    k: int,
) -> float:
    """Retorna 1.0 quando existe ao menos um documento relevante no top-k."""

    _validate_k(k)

    relevant = _relevant_set(relevant_document_ids)

    if not relevant:
        return 0.0

    retrieved_top_k = _unique_document_ids(retrieved_document_ids)[:k]

    return float(any(document_id in relevant for document_id in retrieved_top_k))


def recall_at_k(
    retrieved_document_ids: Sequence[DocumentId],
    relevant_document_ids: Sequence[DocumentId],
    *,
    k: int,
) -> float:
    """Calcula a proporção de documentos relevantes encontrados no top-k."""

    _validate_k(k)

    relevant = _relevant_set(relevant_document_ids)

    if not relevant:
        return 0.0

    retrieved_top_k = set(
        _unique_document_ids(retrieved_document_ids)[:k]
    )

    relevant_retrieved = retrieved_top_k.intersection(relevant)

    return len(relevant_retrieved) / len(relevant)


def precision_at_k(
    retrieved_document_ids: Sequence[DocumentId],
    relevant_document_ids: Sequence[DocumentId],
    *,
    k: int,
) -> float:
    """Calcula a proporção de resultados relevantes no top-k.

    O denominador utiliza a quantidade realmente recuperada até k. Dessa
    forma, uma busca que retorna menos de k documentos não é penalizada por
    posições inexistentes.
    """

    _validate_k(k)

    retrieved_top_k = _unique_document_ids(retrieved_document_ids)[:k]

    if not retrieved_top_k:
        return 0.0

    relevant = _relevant_set(relevant_document_ids)

    relevant_retrieved = sum(
        document_id in relevant
        for document_id in retrieved_top_k
    )

    return relevant_retrieved / len(retrieved_top_k)


def reciprocal_rank(
    retrieved_document_ids: Sequence[DocumentId],
    relevant_document_ids: Sequence[DocumentId],
    *,
    k: int | None = None,
) -> float:
    """Calcula o inverso da posição do primeiro documento relevante."""

    if k is not None:
        _validate_k(k)

    retrieved = _unique_document_ids(retrieved_document_ids)

    if k is not None:
        retrieved = retrieved[:k]

    relevant = _relevant_set(relevant_document_ids)

    for rank, document_id in enumerate(retrieved, start=1):
        if document_id in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    cases: Sequence[
        tuple[
            Sequence[DocumentId],
            Sequence[DocumentId],
        ]
    ],
    *,
    k: int | None = None,
) -> float:
    """Calcula a média do reciprocal rank de vários casos."""

    if k is not None:
        _validate_k(k)

    if not cases:
        return 0.0

    total = sum(
        reciprocal_rank(
            retrieved_document_ids,
            relevant_document_ids,
            k=k,
        )
        for retrieved_document_ids, relevant_document_ids in cases
    )

    return total / len(cases)


def _discounted_cumulative_gain(
    relevance_scores: Sequence[float],
) -> float:
    return sum(
        ((2.0**score) - 1.0) / log2(position + 1)
        for position, score in enumerate(
            relevance_scores,
            start=1,
        )
    )


def ndcg_at_k(
    retrieved_document_ids: Sequence[DocumentId],
    graded_relevance: Mapping[DocumentId, float],
    *,
    k: int,
) -> float:
    """Calcula NDCG@K com ganho exponencial e desconto logarítmico."""

    _validate_k(k)

    normalized_relevance: dict[DocumentId, float] = {}

    for document_id, score in graded_relevance.items():
        normalized_id = str(document_id).strip()

        if not normalized_id:
            raise ValueError(
                "Os identificadores de documentos nao podem ser vazios."
            )

        numeric_score = float(score)

        if numeric_score < 0:
            raise ValueError(
                "Os graus de relevancia nao podem ser negativos."
            )

        normalized_relevance[normalized_id] = numeric_score

    if not normalized_relevance:
        return 0.0

    retrieved_top_k = _unique_document_ids(retrieved_document_ids)[:k]

    actual_scores = [
        normalized_relevance.get(document_id, 0.0)
        for document_id in retrieved_top_k
    ]

    ideal_scores = sorted(
        normalized_relevance.values(),
        reverse=True,
    )[:k]

    ideal_dcg = _discounted_cumulative_gain(ideal_scores)

    if ideal_dcg == 0.0:
        return 0.0

    actual_dcg = _discounted_cumulative_gain(actual_scores)

    return actual_dcg / ideal_dcg


@dataclass(frozen=True, slots=True)
class RetrievalMetricsResult:
    """Resultado consolidado de um caso de recuperação."""

    k: int
    hit_rate: float
    recall: float
    precision: float
    reciprocal_rank: float
    ndcg: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "k": self.k,
            f"hit_rate_at_{self.k}": self.hit_rate,
            f"recall_at_{self.k}": self.recall,
            f"precision_at_{self.k}": self.precision,
            f"reciprocal_rank_at_{self.k}": self.reciprocal_rank,
            f"ndcg_at_{self.k}": self.ndcg,
        }


def evaluate_retrieval_case(
    *,
    retrieved_document_ids: Sequence[DocumentId],
    relevant_document_ids: Sequence[DocumentId],
    graded_relevance: Mapping[DocumentId, float] | None = None,
    k: int,
) -> RetrievalMetricsResult:
    """Executa todas as métricas determinísticas de um caso."""

    _validate_k(k)

    relevance = (
        dict(graded_relevance)
        if graded_relevance is not None
        else {
            document_id: 1.0
            for document_id in relevant_document_ids
        }
    )

    return RetrievalMetricsResult(
        k=k,
        hit_rate=hit_rate_at_k(
            retrieved_document_ids,
            relevant_document_ids,
            k=k,
        ),
        recall=recall_at_k(
            retrieved_document_ids,
            relevant_document_ids,
            k=k,
        ),
        precision=precision_at_k(
            retrieved_document_ids,
            relevant_document_ids,
            k=k,
        ),
        reciprocal_rank=reciprocal_rank(
            retrieved_document_ids,
            relevant_document_ids,
            k=k,
        ),
        ndcg=ndcg_at_k(
            retrieved_document_ids,
            relevance,
            k=k,
        ),
    )


__all__ = [
    "RetrievalMetricsResult",
    "evaluate_retrieval_case",
    "hit_rate_at_k",
    "mean_reciprocal_rank",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
]

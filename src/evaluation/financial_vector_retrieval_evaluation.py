"""Avaliacao vetorial real da base financeira da INNA."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

EXPECTED_CASE_COUNT = 5
EXPECTED_TOP_K = 4
EXPECTED_DIMENSION = 3072


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    case_id: str
    question: str
    expected_document_key: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    rank: int
    chunk_id: str
    document_key: str
    chunk_index: int
    score: float
    text_preview: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RetrievalCaseResult:
    case_id: str
    question: str
    expected_document_key: str
    top1_document_key: str
    top1_passed: bool
    expected_document_found_in_top_k: bool
    hits: tuple[RetrievalHit, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["hits"] = [hit.as_dict() for hit in self.hits]
        return payload


def official_cases() -> tuple[RetrievalCase, ...]:
    return (
        RetrievalCase(
            case_id="reserva_financeira",
            question=("Como montar uma reserva financeira para emergencias?"),
            expected_document_key="inna-edu-reserva-002",
        ),
        RetrievalCase(
            case_id="orcamento_mensal",
            question=("Recebo 3000 reais e gasto 2500. Como organizar meu orcamento?"),
            expected_document_key="inna-edu-orcamento-002",
        ),
        RetrievalCase(
            case_id="cartao_credito",
            question=("Como usar o cartao de credito sem perder o controle?"),
            expected_document_key="inna-edu-cartao-002",
        ),
        RetrievalCase(
            case_id="gastos_fixos_variaveis",
            question=("Qual a diferenca entre gastos fixos e gastos variaveis?"),
            expected_document_key="inna-edu-gastos-002",
        ),
        RetrievalCase(
            case_id="dividas",
            question=("Como posso organizar e pagar minhas dividas?"),
            expected_document_key="inna-edu-dividas-002",
        ),
    )


def validate_cases(
    cases: Sequence[RetrievalCase],
) -> None:
    if len(cases) != EXPECTED_CASE_COUNT:
        raise ValueError("A avaliacao deve possuir exatamente 5 casos.")

    case_ids = [case.case_id for case in cases]

    if len(set(case_ids)) != EXPECTED_CASE_COUNT:
        raise ValueError("Existem IDs de casos duplicados.")

    expected_keys = [case.expected_document_key for case in cases]

    if len(set(expected_keys)) != EXPECTED_CASE_COUNT:
        raise ValueError("Os casos devem possuir documentos esperados distintos.")

    for case in cases:
        if not case.question.strip():
            raise ValueError("Existe caso sem pergunta.")

        if not case.expected_document_key.startswith("inna-edu-"):
            raise ValueError("Documento esperado fora da base educacional.")


def validate_query_vector(
    vector: Sequence[float],
) -> tuple[float, ...]:
    values = tuple(float(value) for value in vector)

    if len(values) != EXPECTED_DIMENSION:
        raise ValueError(f"Dimensao invalida: {len(values)}")

    if not all(math.isfinite(value) for value in values):
        raise ValueError("O vetor de consulta possui valores nao finitos.")

    if not any(value != 0.0 for value in values):
        raise ValueError("O vetor de consulta esta totalmente zerado.")

    return values


def vector_to_pgvector(
    vector: Sequence[float],
) -> str:
    values = validate_query_vector(vector)

    return "[" + ",".join(format(value, ".17g") for value in values) + "]"


def build_case_result(
    *,
    case: RetrievalCase,
    rows: Sequence[Mapping[str, Any]],
) -> RetrievalCaseResult:
    if len(rows) != EXPECTED_TOP_K:
        raise ValueError("Cada consulta deve retornar exatamente 4 resultados.")

    hits: list[RetrievalHit] = []

    for rank, row in enumerate(
        rows,
        start=1,
    ):
        score = float(row["score"])

        if not math.isfinite(score):
            raise ValueError("Resultado com score nao finito.")

        hits.append(
            RetrievalHit(
                rank=rank,
                chunk_id=str(row["chunk_id"]),
                document_key=str(row["document_key"]),
                chunk_index=int(row["chunk_index"]),
                score=score,
                text_preview=str(row["texto"])[:240],
            )
        )

    top1_document_key = hits[0].document_key

    expected_found = any(hit.document_key == case.expected_document_key for hit in hits)

    return RetrievalCaseResult(
        case_id=case.case_id,
        question=case.question,
        expected_document_key=case.expected_document_key,
        top1_document_key=top1_document_key,
        top1_passed=(top1_document_key == case.expected_document_key),
        expected_document_found_in_top_k=expected_found,
        hits=tuple(hits),
    )


def build_evaluation_report(
    results: Sequence[RetrievalCaseResult],
) -> dict[str, Any]:
    top1_pass_count = sum(1 for result in results if result.top1_passed)

    top_k_pass_count = sum(
        1 for result in results if result.expected_document_found_in_top_k
    )

    passed = all(
        (
            len(results) == EXPECTED_CASE_COUNT,
            top1_pass_count == EXPECTED_CASE_COUNT,
            top_k_pass_count == EXPECTED_CASE_COUNT,
        )
    )

    return {
        "schema_version": 1,
        "case_count": len(results),
        "top_k": EXPECTED_TOP_K,
        "top1_pass_count": top1_pass_count,
        "top1_accuracy": (top1_pass_count / EXPECTED_CASE_COUNT),
        "top_k_pass_count": top_k_pass_count,
        "top_k_recall": (top_k_pass_count / EXPECTED_CASE_COUNT),
        "embedding_model": "gemini-embedding-001",
        "embedding_task_type": "RETRIEVAL_QUERY",
        "embedding_dimension": EXPECTED_DIMENSION,
        "evaluation_status": ("passed" if passed else "failed"),
        "gemini_call_count": EXPECTED_CASE_COUNT,
        "database_connected": True,
        "database_write_executed": False,
        "transaction_read_only": True,
        "neon_changed": False,
        "results": [result.as_dict() for result in results],
    }


def build_dry_run_report(
    cases: Sequence[RetrievalCase],
) -> dict[str, Any]:
    validate_cases(cases)

    return {
        "schema_version": 1,
        "case_count": len(cases),
        "top_k": EXPECTED_TOP_K,
        "projected_gemini_call_count": len(cases),
        "embedding_model": "gemini-embedding-001",
        "embedding_task_type": "RETRIEVAL_QUERY",
        "embedding_dimension": EXPECTED_DIMENSION,
        "dry_run_status": "passed",
        "gemini_call_count": 0,
        "database_connected": False,
        "database_write_executed": False,
        "transaction_read_only": False,
        "neon_changed": False,
        "gemini_used": False,
        "cases": [case.as_dict() for case in cases],
    }


__all__ = [
    "RetrievalCase",
    "RetrievalCaseResult",
    "RetrievalHit",
    "build_case_result",
    "build_dry_run_report",
    "build_evaluation_report",
    "official_cases",
    "validate_cases",
    "validate_query_vector",
    "vector_to_pgvector",
]

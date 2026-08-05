"""Ajuste profissional dos chunks financeiros da INNA.

O modulo agrega chunks pequenos gerados pelo chunker original e aplica
ranking lexical com pesos de metadados.

Nao utiliza Neon, Gemini ou rede externa.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from src.evaluation.financial_knowledge_chunking import (
    FinancialKnowledgeChunk,
    FinancialKnowledgeChunkingReport,
    canonical_hash,
    content_hash,
    create_chunking_report,
    normalize_text,
    word_count,
)

TOKEN_PATTERN = re.compile(
    r"\b[\wÀ-ÿ]+\b",
    re.UNICODE,
)


def _canonical_text(value: object) -> str:
    text = normalize_text(value).casefold()

    return "".join(
        character
        for character in unicodedata.normalize(
            "NFD",
            text,
        )
        if unicodedata.category(character) != "Mn"
    )


def _stable_tuned_chunk_id(
    *,
    document_id: str,
    chunk_index: int,
    text: str,
) -> str:
    seed = "|".join(
        (
            document_id,
            str(chunk_index),
            canonical_hash(text),
        )
    )

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]

    return f"{document_id}::tuned-{chunk_index:03d}::{digest}"


def _merge_group(
    chunks: Sequence[FinancialKnowledgeChunk],
    *,
    chunk_index: int,
) -> FinancialKnowledgeChunk:
    first = chunks[0]

    section_titles = tuple(dict.fromkeys(chunk.section_title for chunk in chunks))

    merged_text = normalize_text("\n\n".join(chunk.text for chunk in chunks))

    return replace(
        first,
        chunk_id=_stable_tuned_chunk_id(
            document_id=first.document_id,
            chunk_index=chunk_index,
            text=merged_text,
        ),
        section_title=" | ".join(section_titles),
        section_index=chunk_index,
        chunk_index=chunk_index,
        text=merged_text,
        word_count=word_count(merged_text),
        character_count=len(merged_text),
        content_hash=content_hash(merged_text),
        canonical_hash=canonical_hash(merged_text),
    )


def tune_document_chunks(
    chunks: Sequence[FinancialKnowledgeChunk],
    *,
    minimum_words: int = 70,
    target_words: int = 130,
    maximum_words: int = 190,
) -> tuple[FinancialKnowledgeChunk, ...]:
    """Agrupa chunks usando particionamento deterministico.

    A funcao procura uma divisao em que todos os grupos fiquem
    entre minimum_words e maximum_words. Entre as divisoes validas,
    escolhe a que deixa os grupos mais proximos de target_words.
    """

    if not chunks:
        return ()

    if minimum_words <= 0:
        raise ValueError("minimum_words deve ser positivo.")

    if not (minimum_words <= target_words <= maximum_words):
        raise ValueError("A ordem deve ser minimum <= target <= maximum.")

    ordered = sorted(
        chunks,
        key=lambda chunk: chunk.chunk_index,
    )

    weights = [chunk.word_count for chunk in ordered]

    total_words = sum(weights)

    if total_words < minimum_words:
        return (
            _merge_group(
                ordered,
                chunk_index=1,
            ),
        )

    item_count = len(ordered)

    best_cost: list[float | None] = [None] * (item_count + 1)

    previous_index: list[int | None] = [None] * (item_count + 1)

    best_cost[0] = 0.0

    for end in range(
        1,
        item_count + 1,
    ):
        group_words = 0

        for start in range(
            end - 1,
            -1,
            -1,
        ):
            group_words += weights[start]

            if group_words > maximum_words:
                break

            if group_words < minimum_words:
                continue

            prior_cost = best_cost[start]

            if prior_cost is None:
                continue

            distance = group_words - target_words

            candidate_cost = prior_cost + float(distance * distance)

            current_cost = best_cost[end]

            if current_cost is None or candidate_cost < current_cost:
                best_cost[end] = candidate_cost
                previous_index[end] = start

    if best_cost[item_count] is None:
        raise ValueError(
            "Nao foi possivel particionar o documento "
            f"entre {minimum_words} e {maximum_words} palavras. "
            f"Total de palavras: {total_words}."
        )

    boundaries: list[tuple[int, int]] = []

    end = item_count

    while end > 0:
        start = previous_index[end]

        if start is None:
            raise RuntimeError("Particionamento inconsistente.")

        boundaries.append(
            (
                start,
                end,
            )
        )

        end = start

    boundaries.reverse()

    tuned_chunks = tuple(
        _merge_group(
            ordered[start:end],
            chunk_index=index,
        )
        for index, (
            start,
            end,
        ) in enumerate(
            boundaries,
            start=1,
        )
    )

    invalid_chunks = [
        chunk
        for chunk in tuned_chunks
        if not (minimum_words <= chunk.word_count <= maximum_words)
    ]

    if invalid_chunks:
        details = ", ".join(
            (f"{chunk.chunk_id}={chunk.word_count}") for chunk in invalid_chunks
        )

        raise ValueError("Chunks fora da faixa profissional: " + details)

    return tuned_chunks


def create_tuned_chunking_report(
    *,
    root: Path,
    minimum_words: int = 70,
    target_words: int = 130,
    maximum_words: int = 190,
) -> FinancialKnowledgeChunkingReport:
    original = create_chunking_report(
        root=root,
        minimum_words=45,
        target_words=110,
        maximum_words=180,
    )

    by_document: dict[
        str,
        list[FinancialKnowledgeChunk],
    ] = {}

    for chunk in original.chunks:
        by_document.setdefault(
            chunk.document_id,
            [],
        ).append(chunk)

    tuned_chunks: list[FinancialKnowledgeChunk] = []

    for document_id in sorted(by_document):
        tuned_chunks.extend(
            tune_document_chunks(
                by_document[document_id],
                minimum_words=minimum_words,
                target_words=target_words,
                maximum_words=maximum_words,
            )
        )

    hashes: dict[str, list[str]] = {}

    for chunk in tuned_chunks:
        hashes.setdefault(
            chunk.canonical_hash,
            [],
        ).append(chunk.chunk_id)

    duplicate_groups = tuple(
        tuple(chunk_ids) for chunk_ids in hashes.values() if len(chunk_ids) > 1
    )

    observed_words = [chunk.word_count for chunk in tuned_chunks]

    return FinancialKnowledgeChunkingReport(
        schema_version=2,
        source_root=str(root),
        document_count=original.document_count,
        chunk_count=len(tuned_chunks),
        duplicate_chunk_count=sum(len(group) - 1 for group in duplicate_groups),
        duplicate_groups=duplicate_groups,
        education_document_count=(original.education_document_count),
        security_document_count=(original.security_document_count),
        education_chunk_count=sum(
            chunk.area == "educacao_financeira" for chunk in tuned_chunks
        ),
        security_chunk_count=sum(
            chunk.area == "seguranca_financeira" for chunk in tuned_chunks
        ),
        minimum_chunk_words=min(
            observed_words,
            default=0,
        ),
        maximum_chunk_words=max(
            observed_words,
            default=0,
        ),
        mean_chunk_words=(
            sum(observed_words) / len(observed_words) if observed_words else 0.0
        ),
        chunks=tuple(tuned_chunks),
        neon_used=False,
        gemini_used=False,
    )


def _query_terms(query: str) -> set[str]:
    stopwords = {
        "como",
        "qual",
        "quais",
        "uma",
        "para",
        "sem",
        "meu",
        "minha",
        "devo",
        "usar",
        "montar",
        "entre",
        "primeiro",
        "diferenca",
    }

    return {
        term
        for term in TOKEN_PATTERN.findall(_canonical_text(query))
        if len(term) >= 4 and term not in stopwords
    }


def _overlap(
    query_terms: set[str],
    value: str,
) -> float:
    if not query_terms:
        return 0.0

    value_terms = set(TOKEN_PATTERN.findall(_canonical_text(value)))

    return len(query_terms.intersection(value_terms)) / len(query_terms)


def weighted_score(
    *,
    query: str,
    chunk: FinancialKnowledgeChunk,
) -> float:
    terms = _query_terms(query)

    if not terms:
        return 0.0

    query_text = _canonical_text(query)

    intent_rules = {
        "reserva_de_emergencia": (
            "reserva financeira",
            "reserva de emergencia",
        ),
        "orcamento_pessoal": (
            "organizar renda",
            "despesas mensais",
        ),
        "cartao_de_credito": ("cartao de credito",),
        "priorizacao_de_dividas": (
            "divida devo pagar",
            "pagar primeiro",
        ),
        "classificacao_de_gastos": (
            "gastos fixos",
            "gastos variaveis",
            "fixos e variaveis",
        ),
    }

    bonus = 0.0

    if any(
        phrase in query_text
        for phrase in intent_rules.get(
            chunk.topic,
            (),
        )
    ):
        bonus = 3.0

    score = (
        _overlap(
            terms,
            chunk.text,
        )
        + _overlap(
            terms,
            chunk.section_title,
        )
        * 1.5
        + _overlap(
            terms,
            chunk.document_title,
        )
        * 2.0
        + _overlap(
            terms,
            chunk.topic.replace(
                "_",
                " ",
            ),
        )
        * 3.0
        + bonus
    )

    return round(
        score,
        9,
    )


def tuned_lexical_search(
    *,
    query: str,
    chunks: Sequence[FinancialKnowledgeChunk],
    top_k: int = 4,
) -> tuple[
    tuple[FinancialKnowledgeChunk, float],
    ...,
]:
    ranked = sorted(
        (
            (
                chunk,
                weighted_score(
                    query=query,
                    chunk=chunk,
                ),
            )
            for chunk in chunks
        ),
        key=lambda item: (
            -item[1],
            item[0].document_id,
            item[0].chunk_index,
        ),
    )

    return tuple(item for item in ranked[:top_k] if item[1] > 0)


__all__ = [
    "create_tuned_chunking_report",
    "tune_document_chunks",
    "tuned_lexical_search",
    "weighted_score",
]

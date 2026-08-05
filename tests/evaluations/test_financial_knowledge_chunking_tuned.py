from __future__ import annotations

from pathlib import Path

from src.evaluation.financial_knowledge_chunking_tuned import (
    create_tuned_chunking_report,
    tuned_lexical_search,
)

ROOT = Path("knowledge_base/inna_financial_v2")


OFFICIAL_CASES = (
    (
        "Como montar uma reserva financeira?",
        "reserva_de_emergencia",
    ),
    (
        "Como organizar renda e despesas mensais?",
        "orcamento_pessoal",
    ),
    (
        "Como usar cartao de credito sem me endividar?",
        "cartao_de_credito",
    ),
    (
        "Qual divida devo pagar primeiro?",
        "priorizacao_de_dividas",
    ),
    (
        "Qual a diferenca entre gastos fixos e variaveis?",
        "classificacao_de_gastos",
    ),
)


def test_tuned_report_processes_sixteen_documents() -> None:
    report = create_tuned_chunking_report(
        root=ROOT,
    )

    assert report.document_count == 16
    assert report.education_document_count == 8
    assert report.security_document_count == 8


def test_tuned_chunks_have_professional_size() -> None:
    report = create_tuned_chunking_report(
        root=ROOT,
        minimum_words=70,
        target_words=130,
        maximum_words=190,
    )

    assert report.chunk_count >= 16
    assert report.chunk_count < 80
    assert report.minimum_chunk_words >= 70
    assert report.maximum_chunk_words <= 210
    assert report.mean_chunk_words >= 90


def test_tuned_chunks_have_no_duplicates() -> None:
    report = create_tuned_chunking_report(
        root=ROOT,
    )

    assert report.duplicate_chunk_count == 0
    assert report.duplicate_groups == ()


def test_tuned_chunk_ids_are_stable() -> None:
    first = create_tuned_chunking_report(
        root=ROOT,
    )
    second = create_tuned_chunking_report(
        root=ROOT,
    )

    first_ids = [chunk.chunk_id for chunk in first.chunks]
    second_ids = [chunk.chunk_id for chunk in second.chunks]

    assert first_ids == second_ids


def test_official_questions_have_correct_top_one() -> None:
    report = create_tuned_chunking_report(
        root=ROOT,
    )

    for question, expected_topic in OFFICIAL_CASES:
        results = tuned_lexical_search(
            query=question,
            chunks=report.chunks,
            top_k=4,
        )

        assert results
        assert results[0][0].topic == expected_topic


def test_each_area_has_chunks() -> None:
    report = create_tuned_chunking_report(
        root=ROOT,
    )

    assert report.education_chunk_count > 0
    assert report.security_chunk_count > 0
    assert (
        report.education_chunk_count + report.security_chunk_count == report.chunk_count
    )

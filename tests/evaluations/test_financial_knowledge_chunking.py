from __future__ import annotations

from pathlib import Path

from src.evaluation.financial_knowledge_chunking import (
    canonicalize_text,
    create_chunking_report,
    discover_topic_documents,
    lexical_search,
    validate_official_questions,
)

ROOT = Path("knowledge_base/inna_financial_v2")


def test_discovers_only_sixteen_topic_documents() -> None:
    paths = discover_topic_documents(ROOT)

    assert len(paths) == 16
    assert all(
        path.parent.name
        in {
            "educadora_financeira",
            "seguranca_financeira",
        }
        for path in paths
    )
    assert all("PROFISSIONAL" not in path.name for path in paths)


def test_chunking_report_has_no_duplicates() -> None:
    report = create_chunking_report(
        root=ROOT,
    )

    assert report.document_count == 16
    assert report.education_document_count == 8
    assert report.security_document_count == 8
    assert report.chunk_count > 16
    assert report.duplicate_chunk_count == 0
    assert report.duplicate_groups == ()


def test_chunks_have_stable_metadata() -> None:
    first = create_chunking_report(
        root=ROOT,
    )
    second = create_chunking_report(
        root=ROOT,
    )

    first_ids = [chunk.chunk_id for chunk in first.chunks]
    second_ids = [chunk.chunk_id for chunk in second.chunks]

    assert first_ids == second_ids
    assert all(chunk.document_id for chunk in first.chunks)
    assert all(chunk.topic for chunk in first.chunks)
    assert all(chunk.section_title for chunk in first.chunks)
    assert all(chunk.content_hash for chunk in first.chunks)
    assert all(chunk.canonical_hash for chunk in first.chunks)


def test_canonicalization_removes_accents() -> None:
    assert canonicalize_text("Dívida e cartão") == "divida e cartao"


def test_official_questions_hit_expected_topics() -> None:
    report = create_chunking_report(
        root=ROOT,
    )

    validation = validate_official_questions(report.chunks)

    assert validation["case_count"] == 5
    assert validation["hit_count"] == 5
    assert validation["hit_rate"] == 1.0
    assert validation["passed"] is True


def test_dividas_question_retrieves_dividas_topic() -> None:
    report = create_chunking_report(
        root=ROOT,
    )

    results = lexical_search(
        query="Qual divida devo pagar primeiro?",
        chunks=report.chunks,
        top_k=4,
    )

    assert results
    assert any(chunk.topic == "priorizacao_de_dividas" for chunk, _score in results)

from __future__ import annotations

from src.evaluation.financial_neon_preflight import (
    ExistingDocument,
    analyze_documents,
    summarize_decisions,
)


def planned_document(
    *,
    name: str = "doc-001",
    content_hash: str = "a" * 64,
    version: int = 2,
) -> dict[str, object]:
    return {
        "nome_logico": name,
        "content_hash": content_hash,
        "versao": version,
    }


def test_new_document_is_insertable() -> None:
    decisions = analyze_documents(
        [planned_document()],
        {},
        {},
    )

    assert decisions[0].action == "insert_new"


def test_exact_existing_document_is_skipped() -> None:
    existing = ExistingDocument(
        database_id=10,
        nome_logico="doc-001",
        content_hash="a" * 64,
        versao=2,
        ativo=True,
    )

    decisions = analyze_documents(
        [planned_document()],
        {"doc-001": existing},
        {"a" * 64: [existing]},
    )

    assert decisions[0].action == "skip_exact_existing"
    assert decisions[0].existing_database_id == 10


def test_lower_or_equal_version_conflict_is_blocked() -> None:
    existing = ExistingDocument(
        database_id=10,
        nome_logico="doc-001",
        content_hash="b" * 64,
        versao=2,
        ativo=True,
    )

    decisions = analyze_documents(
        [planned_document(version=2)],
        {"doc-001": existing},
        {},
    )

    assert decisions[0].action == "block_version_conflict"


def test_superior_version_is_allowed() -> None:
    existing = ExistingDocument(
        database_id=10,
        nome_logico="doc-001",
        content_hash="b" * 64,
        versao=1,
        ativo=True,
    )

    decisions = analyze_documents(
        [planned_document(version=2)],
        {"doc-001": existing},
        {},
    )

    assert decisions[0].action == "insert_new_version"


def test_foreign_duplicate_hash_is_blocked() -> None:
    existing = ExistingDocument(
        database_id=20,
        nome_logico="another-document",
        content_hash="a" * 64,
        versao=1,
        ativo=True,
    )

    decisions = analyze_documents(
        [planned_document()],
        {},
        {"a" * 64: [existing]},
    )

    assert decisions[0].action == "block_duplicate_content"


def test_summary_passes_for_sixteen_new_documents() -> None:
    decisions = analyze_documents(
        [
            planned_document(
                name=f"doc-{index:03d}",
                content_hash=f"{index:064x}",
            )
            for index in range(1, 17)
        ],
        {},
        {},
    )

    summary = summarize_decisions(
        decisions,
        planned_chunk_count=35,
        existing_chunk_ids=[],
    )

    assert summary["planned_document_count"] == 16
    assert summary["planned_chunk_count"] == 35
    assert summary["blocking_document_count"] == 0
    assert summary["existing_chunk_id_count"] == 0
    assert summary["preflight_passed"] is True


def test_summary_fails_when_chunk_id_exists() -> None:
    decisions = analyze_documents(
        [
            planned_document(
                name=f"doc-{index:03d}",
                content_hash=f"{index:064x}",
            )
            for index in range(1, 17)
        ],
        {},
        {},
    )

    summary = summarize_decisions(
        decisions,
        planned_chunk_count=35,
        existing_chunk_ids=["chunk-existing"],
    )

    assert summary["existing_chunk_id_count"] == 1
    assert summary["preflight_passed"] is False

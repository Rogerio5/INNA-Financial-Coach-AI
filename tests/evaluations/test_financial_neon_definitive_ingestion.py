from __future__ import annotations

import pytest

from src.evaluation.financial_neon_definitive_ingestion import (
    ConflictSummary,
    build_conflict_queries,
    build_offline_ingestion_report,
    build_simulation_plan,
    validate_conflict_summary,
    validate_final_counts,
    validate_inserted_document_ids,
    validate_new_rows,
)


def vector() -> list[float]:
    return [0.001 for _ in range(3072)]


def documents() -> list[dict[str, object]]:
    return [
        {
            "nome_original": f"document-{index}.md",
            "nome_salvo": f"document-{index}.md",
            "caminho_upload": f"knowledge/document-{index}.md",
            "caminho_chunks": None,
            "caminho_embedding_ready": None,
            "extensao": ".md",
            "tamanho_bytes": None,
            "total_chunks": (3 if index in {1, 2, 3} else 2),
            "status": "adaptado_sem_embedding",
            "origem": "knowledge_base:test:pt-BR",
            "ativo": True,
            "nome_logico": f"document-{index:02d}",
            "content_hash": f"{index:064x}",
            "versao": 2,
            "documento_raiz_id": None,
            "documento_anterior_id": None,
        }
        for index in range(1, 17)
    ]


def chunks() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []

    for document_index in range(1, 17):
        total = 3 if document_index in {1, 2, 3} else 2

        for chunk_index in range(1, total + 1):
            result.append(
                {
                    "chunk_id": (f"chunk-{document_index:02d}-{chunk_index:02d}"),
                    "documento_key": (f"document-{document_index:02d}"),
                    "documento_origem": (f"document-{document_index}.md"),
                    "chunk_index": chunk_index,
                    "texto": "Conteudo financeiro",
                    "metadata": {
                        "area": "financeiro",
                    },
                    "modelo_embedding": ("models/gemini-embedding-001"),
                    "embedding": vector(),
                }
            )

    return result


def plan():
    return build_simulation_plan(
        documents(),
        chunks(),
    )


def test_offline_report_passes() -> None:
    report = build_offline_ingestion_report(plan())

    assert report["planned_document_insert_count"] == 16
    assert report["planned_chunk_insert_count"] == 35
    assert report["planned_embedding_insert_count"] == 35
    assert report["embedding_dimension"] == 3072
    assert report["duplicate_guard_enabled"] is True
    assert report["rollback_on_error_enabled"] is True
    assert report["commit_confirmation_required"] is True
    assert report["offline_plan_status"] == "passed"
    assert report["database_connected"] is False
    assert report["neon_changed"] is False


def test_builds_conflict_queries() -> None:
    queries = build_conflict_queries(plan())

    assert len(queries["logical_names"]) == 16
    assert len(queries["content_hashes"]) == 16
    assert len(queries["chunk_ids"]) == 35


def test_rejects_conflicts() -> None:
    with pytest.raises(
        RuntimeError,
        match="conflitos",
    ):
        validate_conflict_summary(
            ConflictSummary(
                document_logical_name_count=1,
                document_content_hash_count=0,
                chunk_id_count=0,
            )
        )


def test_accepts_zero_conflicts() -> None:
    validate_conflict_summary(
        ConflictSummary(
            document_logical_name_count=0,
            document_content_hash_count=0,
            chunk_id_count=0,
        )
    )


def test_validates_document_ids() -> None:
    current_plan = plan()

    document_ids = {
        str(document["nome_logico"]): index
        for index, document in enumerate(
            current_plan.documents,
            start=100,
        )
    }

    validate_inserted_document_ids(
        plan=current_plan,
        document_ids=document_ids,
    )


def test_validates_final_counts() -> None:
    validate_final_counts(
        document_count_before=5,
        chunk_count_before=11,
        document_count_after=21,
        chunk_count_after=46,
    )


def test_rejects_wrong_final_counts() -> None:
    with pytest.raises(
        RuntimeError,
        match="documentos",
    ):
        validate_final_counts(
            document_count_before=5,
            chunk_count_before=11,
            document_count_after=20,
            chunk_count_after=46,
        )


def test_validates_new_rows() -> None:
    validate_new_rows(
        document_match_count=16,
        chunk_match_count=35,
    )

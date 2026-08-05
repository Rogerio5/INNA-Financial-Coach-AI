from __future__ import annotations

import pytest

from src.evaluation.financial_neon_ingestion_simulation import (
    build_offline_report,
    build_simulation_plan,
    vector_to_pgvector,
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


def test_pgvector_serialization() -> None:
    serialized = vector_to_pgvector(vector())

    assert serialized.startswith("[")
    assert serialized.endswith("]")
    assert serialized.count(",") == 3071


def test_rejects_wrong_vector_dimension() -> None:
    with pytest.raises(
        ValueError,
        match="Dimensao",
    ):
        vector_to_pgvector([0.1, 0.2])


def test_builds_complete_simulation_plan() -> None:
    plan = build_simulation_plan(
        documents(),
        chunks(),
    )

    assert plan.document_count == 16
    assert plan.chunk_count == 35


def test_offline_report_passes() -> None:
    plan = build_simulation_plan(
        documents(),
        chunks(),
    )

    report = build_offline_report(plan)

    assert report["document_count"] == 16
    assert report["chunk_count"] == 35
    assert report["embedding_count"] == 35
    assert report["embedding_dimension"] == 3072
    assert report["offline_plan_status"] == "passed"
    assert report["database_connected"] is False
    assert report["database_write_executed"] is False
    assert report["transaction_committed"] is False
    assert report["neon_changed"] is False
    assert report["gemini_used"] is False

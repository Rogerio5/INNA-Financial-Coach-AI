from __future__ import annotations

from pathlib import Path

import pytest

from src.services.rag.versioning import (
    RagDuplicateDocumentError,
    create_document_version_from_context,
)


HASH_A = "a" * 64
HASH_B = "b" * 64

REPOSITORY_PATH = Path(
    "src/services/rag/document_repository.py"
)


def test_repository_exposes_versioning_context_query():
    source = REPOSITORY_PATH.read_text(
        encoding="utf-8-sig",
    )

    assert (
        "def buscar_contexto_versionamento_documento"
        in source
    )

    assert (
        "WHERE nome_logico = %s"
        in source
    )

    assert (
        "existing_content_hashes"
        in source
    )

    assert (
        "previous_document_id"
        in source
    )

    assert (
        "root_document_id"
        in source
    )


def test_creates_first_version_from_empty_context():
    version = create_document_version_from_context(
        filename="reserva.md",
        content_hash=HASH_A,
        repository_context={
            "current_version": None,
            "root_document_id": None,
            "previous_document_id": None,
            "existing_content_hashes": [],
        },
    )

    assert version.version == 1
    assert version.is_initial_version is True
    assert version.root_document_id is None
    assert version.previous_document_id is None


def test_creates_next_version_from_repository_context():
    version = create_document_version_from_context(
        filename="reserva.md",
        content_hash=HASH_B,
        repository_context={
            "current_version": 3,
            "root_document_id": 10,
            "previous_document_id": 15,
            "existing_content_hashes": [
                HASH_A,
            ],
        },
    )

    assert version.version == 4
    assert version.root_document_id == 10
    assert version.previous_document_id == 15
    assert version.is_initial_version is False


def test_rejects_duplicate_from_repository_context():
    with pytest.raises(
        RagDuplicateDocumentError,
        match="já está registrado",
    ):
        create_document_version_from_context(
            filename="reserva.md",
            content_hash=HASH_A,
            repository_context={
                "current_version": 1,
                "root_document_id": 10,
                "previous_document_id": 10,
                "existing_content_hashes": [
                    HASH_A,
                ],
            },
        )


def test_none_context_creates_first_version():
    version = create_document_version_from_context(
        filename="guia.txt",
        content_hash=HASH_A,
        repository_context=None,
    )

    assert version.version == 1
    assert version.logical_name == "guia"

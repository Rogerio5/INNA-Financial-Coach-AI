from __future__ import annotations

import pytest

from src.services.rag.versioning import (
    RagDocumentVersioningError,
    RagDuplicateDocumentError,
    create_document_version,
    determine_next_document_version,
    ensure_content_is_not_duplicate,
    normalize_logical_document_name,
    validate_content_hash,
    validate_document_id,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


@pytest.mark.parametrize(
    ("filename", "expected"),
    (
        (
            "Guia Reserva 2026.MD",
            "guia_reserva_2026",
        ),
        (
            "Educação Financeira.txt",
            "educacao_financeira",
        ),
        (
            "../../FAQ Cartão.md",
            "faq_cartao",
        ),
        (
            "  orçamento---mensal.md  ",
            "orcamento_mensal",
        ),
    ),
)
def test_normalizes_logical_document_name(
    filename: str,
    expected: str,
):
    assert (
        normalize_logical_document_name(filename)
        == expected
    )


def test_rejects_empty_logical_name():
    with pytest.raises(
        RagDocumentVersioningError,
        match="nome lógico",
    ):
        normalize_logical_document_name(
            "...md"
        )


def test_accepts_valid_sha256():
    assert validate_content_hash(
        HASH_A.upper()
    ) == HASH_A


@pytest.mark.parametrize(
    "content_hash",
    (
        "",
        "abc",
        "g" * 64,
        "a" * 63,
        "a" * 65,
    ),
)
def test_rejects_invalid_sha256(
    content_hash: str,
):
    with pytest.raises(
        RagDocumentVersioningError,
        match="SHA-256",
    ):
        validate_content_hash(
            content_hash
        )


def test_first_version_is_one():
    assert determine_next_document_version(
        None
    ) == 1


def test_increments_existing_version():
    assert determine_next_document_version(
        4
    ) == 5


@pytest.mark.parametrize(
    "current_version",
    (
        0,
        -1,
        "invalid",
    ),
)
def test_rejects_invalid_current_version(
    current_version,
):
    with pytest.raises(
        RagDocumentVersioningError,
    ):
        determine_next_document_version(
            current_version
        )


def test_accepts_positive_document_id():
    assert validate_document_id(
        10,
        field_name="document_id",
    ) == 10


def test_accepts_none_document_id():
    assert (
        validate_document_id(
            None,
            field_name="document_id",
        )
        is None
    )


@pytest.mark.parametrize(
    "document_id",
    (
        0,
        -1,
        "invalid",
    ),
)
def test_rejects_invalid_document_id(
    document_id,
):
    with pytest.raises(
        RagDocumentVersioningError,
    ):
        validate_document_id(
            document_id,
            field_name="document_id",
        )


def test_accepts_new_content_hash():
    ensure_content_is_not_duplicate(
        new_content_hash=HASH_A,
        existing_content_hashes=(
            HASH_B,
        ),
    )


def test_rejects_duplicate_content_hash():
    with pytest.raises(
        RagDuplicateDocumentError,
        match="já está registrado",
    ):
        ensure_content_is_not_duplicate(
            new_content_hash=HASH_A,
            existing_content_hashes=(
                HASH_A,
                HASH_B,
            ),
        )


def test_creates_initial_document_version():
    version = create_document_version(
        filename="reserva.md",
        content_hash=HASH_A,
    )

    assert version.logical_name == "reserva"
    assert version.version == 1
    assert version.content_hash == HASH_A
    assert version.root_document_id is None
    assert version.previous_document_id is None
    assert version.is_initial_version is True
    assert (
        version.replaces_previous_version
        is False
    )


def test_creates_incremental_document_version():
    version = create_document_version(
        filename="reserva.md",
        content_hash=HASH_B,
        current_version=2,
        root_document_id=10,
        previous_document_id=12,
        existing_content_hashes=(
            HASH_A,
        ),
    )

    assert version.logical_name == "reserva"
    assert version.version == 3
    assert version.root_document_id == 10
    assert version.previous_document_id == 12
    assert version.is_initial_version is False
    assert (
        version.replaces_previous_version
        is True
    )


def test_new_version_requires_previous_document():
    with pytest.raises(
        RagDocumentVersioningError,
        match="documento anterior",
    ):
        create_document_version(
            filename="reserva.md",
            content_hash=HASH_B,
            current_version=1,
            root_document_id=10,
        )


def test_new_version_requires_root_document():
    with pytest.raises(
        RagDocumentVersioningError,
        match="documento raiz",
    ):
        create_document_version(
            filename="reserva.md",
            content_hash=HASH_B,
            current_version=1,
            previous_document_id=10,
        )


def test_initial_version_rejects_previous_document():
    with pytest.raises(
        RagDocumentVersioningError,
        match="versão inicial",
    ):
        create_document_version(
            filename="reserva.md",
            content_hash=HASH_A,
            previous_document_id=10,
        )


def test_document_version_can_be_serialized():
    version = create_document_version(
        filename="guia.txt",
        content_hash=HASH_A,
    )

    payload = version.to_dict()

    assert payload == {
        "logical_name": "guia",
        "version": 1,
        "content_hash": HASH_A,
        "root_document_id": None,
        "previous_document_id": None,
        "is_initial_version": True,
        "replaces_previous_version": False,
    }

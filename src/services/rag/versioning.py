"""
Versionamento profissional dos documentos RAG da INNA.

Este módulo não acessa diretamente o banco de dados.
Ele define regras determinísticas e testáveis para:

- identidade lógica do documento;
- versões incrementais;
- detecção de conteúdo duplicado;
- relacionamento entre versões;
- criação dos metadados de versionamento.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata
from typing import Final


MIN_DOCUMENT_VERSION: Final[int] = 1

_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-f0-9]{64}$"
)


class RagDocumentVersioningError(ValueError):
    """
    Erro seguro das regras de versionamento documental.
    """


class RagDuplicateDocumentError(
    RagDocumentVersioningError
):
    """
    Indica que o mesmo conteúdo já foi registrado.
    """


@dataclass(frozen=True, slots=True)
class RagDocumentVersion:
    """
    Metadados imutáveis de uma versão documental.
    """

    logical_name: str
    version: int
    content_hash: str
    root_document_id: int | None
    previous_document_id: int | None
    is_initial_version: bool
    replaces_previous_version: bool

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_logical_document_name(
    filename: str,
) -> str:
    """
    Converte um nome físico em identidade lógica estável.

    Exemplo:
        Guia Reserva 2026.MD -> guia_reserva_2026
    """
    original = Path(
        str(filename or "").strip()
    ).name

    stem = Path(original).stem

    normalized = unicodedata.normalize(
        "NFKD",
        stem,
    )

    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.lower()

    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized,
    )

    normalized = normalized.strip("_")

    if not normalized:
        raise RagDocumentVersioningError(
            "Não foi possível determinar o nome "
            "lógico do documento."
        )

    return normalized


def validate_content_hash(
    content_hash: str,
) -> str:
    """
    Valida um SHA-256 hexadecimal em letras minúsculas.
    """
    normalized = str(
        content_hash or ""
    ).strip().lower()

    if not _SHA256_PATTERN.fullmatch(normalized):
        raise RagDocumentVersioningError(
            "O hash do documento deve ser um "
            "SHA-256 hexadecimal válido."
        )

    return normalized


def validate_document_id(
    document_id: int | None,
    *,
    field_name: str,
) -> int | None:
    """
    Valida IDs opcionais usados no vínculo entre versões.
    """
    if document_id is None:
        return None

    try:
        normalized = int(document_id)
    except (TypeError, ValueError) as exc:
        raise RagDocumentVersioningError(
            f"{field_name} deve ser um número inteiro."
        ) from exc

    if normalized < 1:
        raise RagDocumentVersioningError(
            f"{field_name} deve ser maior que zero."
        )

    return normalized


def determine_next_document_version(
    current_version: int | None,
) -> int:
    """
    Retorna a primeira versão ou incrementa a atual.
    """
    if current_version is None:
        return MIN_DOCUMENT_VERSION

    try:
        normalized = int(current_version)
    except (TypeError, ValueError) as exc:
        raise RagDocumentVersioningError(
            "A versão atual deve ser inteira."
        ) from exc

    if normalized < MIN_DOCUMENT_VERSION:
        raise RagDocumentVersioningError(
            "A versão atual é inválida."
        )

    return normalized + 1


def ensure_content_is_not_duplicate(
    *,
    new_content_hash: str,
    existing_content_hashes: list[str]
    | tuple[str, ...]
    | set[str],
) -> None:
    """
    Rejeita conteúdo já registrado em qualquer versão.
    """
    normalized_new_hash = validate_content_hash(
        new_content_hash
    )

    normalized_existing_hashes = {
        validate_content_hash(item)
        for item in existing_content_hashes
    }

    if normalized_new_hash in normalized_existing_hashes:
        raise RagDuplicateDocumentError(
            "Este conteúdo já está registrado "
            "na base documental."
        )


def create_document_version(
    *,
    filename: str,
    content_hash: str,
    current_version: int | None = None,
    root_document_id: int | None = None,
    previous_document_id: int | None = None,
    existing_content_hashes: list[str]
    | tuple[str, ...]
    | set[str] = (),
) -> RagDocumentVersion:
    """
    Cria os metadados da próxima versão documental.
    """
    logical_name = (
        normalize_logical_document_name(filename)
    )

    normalized_content_hash = (
        validate_content_hash(content_hash)
    )

    ensure_content_is_not_duplicate(
        new_content_hash=normalized_content_hash,
        existing_content_hashes=(
            existing_content_hashes
        ),
    )

    version = determine_next_document_version(
        current_version
    )

    normalized_root_id = validate_document_id(
        root_document_id,
        field_name="root_document_id",
    )

    normalized_previous_id = validate_document_id(
        previous_document_id,
        field_name="previous_document_id",
    )

    is_initial_version = (
        version == MIN_DOCUMENT_VERSION
    )

    if is_initial_version:
        if normalized_previous_id is not None:
            raise RagDocumentVersioningError(
                "A versão inicial não pode possuir "
                "documento anterior."
            )

        if current_version is not None:
            raise RagDocumentVersioningError(
                "A versão inicial não pode receber "
                "uma versão atual."
            )

    else:
        if normalized_previous_id is None:
            raise RagDocumentVersioningError(
                "Uma nova versão precisa informar "
                "o documento anterior."
            )

        if normalized_root_id is None:
            raise RagDocumentVersioningError(
                "Uma nova versão precisa informar "
                "o documento raiz."
            )

    return RagDocumentVersion(
        logical_name=logical_name,
        version=version,
        content_hash=normalized_content_hash,
        root_document_id=normalized_root_id,
        previous_document_id=normalized_previous_id,
        is_initial_version=is_initial_version,
        replaces_previous_version=(
            not is_initial_version
        ),
    )


def create_document_version_from_context(
    *,
    filename: str,
    content_hash: str,
    repository_context: dict | None,
) -> RagDocumentVersion:
    """
    Cria a próxima versão usando o contexto do repositório.
    """
    context = repository_context or {}

    return create_document_version(
        filename=filename,
        content_hash=content_hash,
        current_version=context.get(
            "current_version"
        ),
        root_document_id=context.get(
            "root_document_id"
        ),
        previous_document_id=context.get(
            "previous_document_id"
        ),
        existing_content_hashes=context.get(
            "existing_content_hashes"
        )
        or (),
    )


__all__ = [
    "MIN_DOCUMENT_VERSION",
    "RagDocumentVersion",
    "RagDocumentVersioningError",
    "RagDuplicateDocumentError",
    "create_document_version",
    "create_document_version_from_context",
    "determine_next_document_version",
    "ensure_content_is_not_duplicate",
    "normalize_logical_document_name",
    "validate_content_hash",
    "validate_document_id",
]

"""
Controles de segurança para documentos da base RAG da INNA.

Responsabilidades:
- validar extensão;
- validar tamanho;
- calcular hash SHA-256;
- identificar padrões de prompt injection;
- produzir resultado estruturado de validação.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
from typing import Final


DEFAULT_MAX_DOCUMENT_SIZE_BYTES: Final[int] = (
    5 * 1024 * 1024
)

ALLOWED_DOCUMENT_EXTENSIONS: Final[
    frozenset[str]
] = frozenset(
    {
        ".md",
        ".txt",
    }
)

MIN_DOCUMENT_SIZE_BYTES: Final[int] = 1

_PROMPT_INJECTION_PATTERNS: Final[
    tuple[tuple[str, re.Pattern[str]], ...]
] = (
    (
        "ignore_previous_instructions",
        re.compile(
            r"\bignore\s+(all\s+)?"
            r"(previous|prior|above)\s+instructions?\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "ignore_system_prompt",
        re.compile(
            r"\bignore\s+(the\s+)?"
            r"(system|developer)\s+prompt\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "override_instructions",
        re.compile(
            r"\b(override|replace|disregard)\s+"
            r"(the\s+)?instructions?\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "reveal_system_prompt",
        re.compile(
            r"\b(reveal|show|print|expose)\s+"
            r"(the\s+)?(system|developer)\s+prompt\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "role_reassignment",
        re.compile(
            r"\b(you\s+are\s+now|act\s+as|"
            r"from\s+now\s+on\s+you)\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "portuguese_ignore_instructions",
        re.compile(
            r"\bignore\s+(todas?\s+)?"
            r"(as\s+)?instru[cç][oõ]es\s+"
            r"(anteriores|acima|do\s+sistema)\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "portuguese_reveal_prompt",
        re.compile(
            r"\b(mostre|revele|exiba|imprima)\s+"
            r"(o\s+)?prompt\s+"
            r"(do\s+sistema|interno)\b",
            flags=re.IGNORECASE,
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class RagDocumentSecurityResult:
    """
    Resultado imutável da validação de segurança.
    """

    accepted: bool
    extension: str
    size_bytes: int
    max_size_bytes: int
    content_hash: str
    injection_detected: bool
    injection_patterns: tuple[str, ...]
    rejection_reason: str | None

    def to_dict(self) -> dict:
        return asdict(self)


class RagDocumentSecurityError(ValueError):
    """
    Erro de validação documental seguro para apresentação.
    """


def get_max_document_size_bytes() -> int:
    """
    Retorna o limite configurado por ambiente.

    Variável:
        INNA_RAG_MAX_DOCUMENT_SIZE_BYTES
    """
    raw_value = os.getenv(
        "INNA_RAG_MAX_DOCUMENT_SIZE_BYTES"
    )

    if not raw_value:
        return DEFAULT_MAX_DOCUMENT_SIZE_BYTES

    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_MAX_DOCUMENT_SIZE_BYTES

    if parsed < MIN_DOCUMENT_SIZE_BYTES:
        return DEFAULT_MAX_DOCUMENT_SIZE_BYTES

    return parsed


def normalize_document_extension(
    filename: str,
) -> str:
    """
    Extrai e normaliza a extensão do documento.
    """
    return Path(
        str(filename or "")
    ).suffix.lower().strip()


def validate_document_extension(
    filename: str,
) -> str:
    """
    Valida a extensão e retorna o valor normalizado.
    """
    extension = normalize_document_extension(
        filename
    )

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        allowed = ", ".join(
            sorted(ALLOWED_DOCUMENT_EXTENSIONS)
        )

        raise RagDocumentSecurityError(
            "Formato de documento não permitido. "
            f"Formatos aceitos: {allowed}."
        )

    return extension


def validate_document_size(
    content: bytes,
    *,
    max_size_bytes: int | None = None,
) -> int:
    """
    Valida documento vazio e limite máximo.
    """
    size_bytes = len(content)

    effective_limit = (
        get_max_document_size_bytes()
        if max_size_bytes is None
        else int(max_size_bytes)
    )

    if effective_limit < MIN_DOCUMENT_SIZE_BYTES:
        raise RagDocumentSecurityError(
            "O limite de tamanho configurado é inválido."
        )

    if size_bytes < MIN_DOCUMENT_SIZE_BYTES:
        raise RagDocumentSecurityError(
            "O documento está vazio."
        )

    if size_bytes > effective_limit:
        raise RagDocumentSecurityError(
            "O documento excede o limite máximo "
            f"de {effective_limit} bytes."
        )

    return size_bytes


def calculate_content_sha256(
    content: bytes,
) -> str:
    """
    Calcula a identidade criptográfica do conteúdo.
    """
    return hashlib.sha256(content).hexdigest()


def detect_prompt_injection_patterns(
    text: str,
) -> tuple[str, ...]:
    """
    Identifica instruções potencialmente maliciosas.

    A detecção não executa nem interpreta o texto.
    """
    normalized_text = str(text or "")

    matches = []

    for name, pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(normalized_text):
            matches.append(name)

    return tuple(matches)


def decode_document_text(
    content: bytes,
) -> str:
    """
    Decodifica o documento como UTF-8.

    Documentos incompatíveis são rejeitados em vez de
    terem seus bytes silenciosamente descartados.
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RagDocumentSecurityError(
            "O documento deve utilizar codificação UTF-8."
        ) from exc


def inspect_rag_document(
    *,
    filename: str,
    content: bytes,
    max_size_bytes: int | None = None,
    reject_prompt_injection: bool = True,
) -> RagDocumentSecurityResult:
    """
    Executa a inspeção completa antes da persistência.
    """
    extension = validate_document_extension(
        filename
    )

    effective_limit = (
        get_max_document_size_bytes()
        if max_size_bytes is None
        else int(max_size_bytes)
    )

    size_bytes = validate_document_size(
        content,
        max_size_bytes=effective_limit,
    )

    content_hash = calculate_content_sha256(
        content
    )

    text = decode_document_text(content)

    injection_patterns = (
        detect_prompt_injection_patterns(text)
    )

    injection_detected = bool(
        injection_patterns
    )

    rejection_reason = None

    if (
        reject_prompt_injection
        and injection_detected
    ):
        rejection_reason = (
            "O documento contém padrões que podem "
            "tentar modificar as instruções da IA."
        )

    return RagDocumentSecurityResult(
        accepted=rejection_reason is None,
        extension=extension,
        size_bytes=size_bytes,
        max_size_bytes=effective_limit,
        content_hash=content_hash,
        injection_detected=injection_detected,
        injection_patterns=injection_patterns,
        rejection_reason=rejection_reason,
    )


def require_safe_rag_document(
    *,
    filename: str,
    content: bytes,
    max_size_bytes: int | None = None,
) -> RagDocumentSecurityResult:
    """
    Inspeciona e interrompe o fluxo quando houver rejeição.
    """
    result = inspect_rag_document(
        filename=filename,
        content=content,
        max_size_bytes=max_size_bytes,
        reject_prompt_injection=True,
    )

    if not result.accepted:
        raise RagDocumentSecurityError(
            result.rejection_reason
            or "Documento rejeitado."
        )

    return result


__all__ = [
    "ALLOWED_DOCUMENT_EXTENSIONS",
    "DEFAULT_MAX_DOCUMENT_SIZE_BYTES",
    "RagDocumentSecurityError",
    "RagDocumentSecurityResult",
    "calculate_content_sha256",
    "decode_document_text",
    "detect_prompt_injection_patterns",
    "get_max_document_size_bytes",
    "inspect_rag_document",
    "normalize_document_extension",
    "require_safe_rag_document",
    "validate_document_extension",
    "validate_document_size",
]

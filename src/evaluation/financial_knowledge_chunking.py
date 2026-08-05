"""Chunking deterministico da base financeira profissional da INNA.

O modulo processa apenas documentos tematicos de Educacao Financeira
e Seguranca Financeira. Nao utiliza Neon, Gemini ou rede externa.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

FRONTMATTER_PATTERN = re.compile(
    r"\A---\n(?P<header>.*?)\n---\n",
    re.DOTALL,
)

HEADING_PATTERN = re.compile(
    r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$",
)

TOKEN_PATTERN = re.compile(
    r"\b[\wÀ-ÿ]+\b",
    re.UNICODE,
)

SPACE_PATTERN = re.compile(
    r"\s+",
)


@dataclass(frozen=True, slots=True)
class FinancialKnowledgeDocument:
    document_id: str
    title: str
    area: str
    topic: str
    language: str
    version: str
    source_ids: tuple[str, ...]
    path: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class FinancialKnowledgeChunk:
    chunk_id: str
    document_id: str
    document_title: str
    document_path: str
    area: str
    topic: str
    section_title: str
    section_index: int
    chunk_index: int
    language: str
    version: str
    source_ids: tuple[str, ...]
    text: str
    word_count: int
    character_count: int
    content_hash: str
    canonical_hash: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FinancialKnowledgeChunkingReport:
    schema_version: int
    source_root: str
    document_count: int
    chunk_count: int
    duplicate_chunk_count: int
    duplicate_groups: tuple[tuple[str, ...], ...]
    education_document_count: int
    security_document_count: int
    education_chunk_count: int
    security_chunk_count: int
    minimum_chunk_words: int
    maximum_chunk_words: int
    mean_chunk_words: float
    chunks: tuple[FinancialKnowledgeChunk, ...]
    neon_used: bool
    gemini_used: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_text(value: object) -> str:
    text = unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )

    return SPACE_PATTERN.sub(
        " ",
        text,
    ).strip()


def canonicalize_text(value: object) -> str:
    text = normalize_text(value).casefold()

    return "".join(
        character
        for character in unicodedata.normalize(
            "NFD",
            text,
        )
        if unicodedata.category(character) != "Mn"
    )


def content_hash(value: object) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonicalize_text(value).encode("utf-8")).hexdigest()


def word_count(value: object) -> int:
    return len(TOKEN_PATTERN.findall(str(value or "")))


def parse_frontmatter(
    content: str,
) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_PATTERN.match(content)

    if match is None:
        raise ValueError("Documento sem frontmatter YAML.")

    header = match.group("header")
    body = content[match.end() :]

    metadata: dict[str, Any] = {}
    current_list: str | None = None

    for raw_line in header.splitlines():
        line = raw_line.rstrip()

        if not line:
            continue

        if line.startswith("  - ") and current_list:
            metadata.setdefault(
                current_list,
                [],
            ).append(line[4:].strip().strip('"'))
            continue

        current_list = None

        key, separator, raw_value = line.partition(":")

        if not separator:
            continue

        key = key.strip()
        value = raw_value.strip().strip('"')

        if value:
            metadata[key] = value
        else:
            metadata[key] = []
            current_list = key

    return metadata, body


def load_document(
    *,
    root: Path,
    path: Path,
) -> tuple[FinancialKnowledgeDocument, str]:
    raw_content = path.read_text(
        encoding="utf-8",
    )

    metadata, body = parse_frontmatter(raw_content)

    required = {
        "document_id",
        "title",
        "area",
        "topic",
        "language",
        "version",
    }

    missing = sorted(required - metadata.keys())

    if missing:
        raise ValueError(f"Metadados ausentes em {path}: " + ",".join(missing))

    source_ids_value = metadata.get(
        "source_ids",
        [],
    )

    if isinstance(source_ids_value, str):
        source_ids = (source_ids_value,)
    elif isinstance(source_ids_value, list):
        source_ids = tuple(str(item) for item in source_ids_value)
    else:
        source_ids = ()

    document = FinancialKnowledgeDocument(
        document_id=str(metadata["document_id"]),
        title=str(metadata["title"]),
        area=str(metadata["area"]),
        topic=str(metadata["topic"]),
        language=str(metadata["language"]),
        version=str(metadata["version"]),
        source_ids=source_ids,
        path=path.relative_to(root).as_posix(),
        content_hash=content_hash(raw_content),
    )

    return document, body


def split_sections(
    body: str,
) -> tuple[tuple[str, str], ...]:
    sections: list[tuple[str, str]] = []
    current_title = "Introducao"
    current_lines: list[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()

        if text:
            sections.append(
                (
                    current_title,
                    text,
                )
            )

    for raw_line in body.splitlines():
        heading = HEADING_PATTERN.match(raw_line)

        if heading:
            flush()
            current_title = normalize_text(heading.group("title"))
            current_lines = []
            continue

        current_lines.append(raw_line)

    flush()

    return tuple(sections)


def split_paragraphs(
    text: str,
) -> tuple[str, ...]:
    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    cleaned = tuple(
        normalize_text(paragraph)
        for paragraph in paragraphs
        if normalize_text(paragraph)
    )

    return cleaned


def split_long_paragraph(
    paragraph: str,
    *,
    maximum_words: int,
) -> tuple[str, ...]:
    if word_count(paragraph) <= maximum_words:
        return (paragraph,)

    sentences = re.split(
        r"(?<=[.!?])\s+",
        paragraph,
    )

    parts: list[str] = []
    buffer: list[str] = []
    buffer_words = 0

    for sentence in sentences:
        sentence = normalize_text(sentence)

        if not sentence:
            continue

        sentence_words = word_count(sentence)

        if buffer and buffer_words + sentence_words > maximum_words:
            parts.append(normalize_text(" ".join(buffer)))
            buffer = []
            buffer_words = 0

        if sentence_words > maximum_words:
            words = sentence.split()

            for index in range(
                0,
                len(words),
                maximum_words,
            ):
                parts.append(" ".join(words[index : index + maximum_words]))
            continue

        buffer.append(sentence)
        buffer_words += sentence_words

    if buffer:
        parts.append(normalize_text(" ".join(buffer)))

    return tuple(parts)


def build_section_chunks(
    *,
    paragraphs: Sequence[str],
    minimum_words: int,
    target_words: int,
    maximum_words: int,
) -> tuple[str, ...]:
    expanded: list[str] = []

    for paragraph in paragraphs:
        expanded.extend(
            split_long_paragraph(
                paragraph,
                maximum_words=maximum_words,
            )
        )

    chunks: list[str] = []
    buffer: list[str] = []
    buffer_words = 0

    for paragraph in expanded:
        paragraph_words = word_count(paragraph)

        if buffer and buffer_words + paragraph_words > maximum_words:
            chunks.append(normalize_text("\n\n".join(buffer)))
            buffer = []
            buffer_words = 0

        buffer.append(paragraph)
        buffer_words += paragraph_words

        if buffer_words >= target_words:
            chunks.append(normalize_text("\n\n".join(buffer)))
            buffer = []
            buffer_words = 0

    if buffer:
        remainder = normalize_text("\n\n".join(buffer))

        if (
            chunks
            and word_count(remainder) < minimum_words
            and (word_count(chunks[-1]) + word_count(remainder) <= maximum_words)
        ):
            chunks[-1] = normalize_text(chunks[-1] + "\n\n" + remainder)
        else:
            chunks.append(remainder)

    return tuple(chunk for chunk in chunks if chunk)


def stable_chunk_id(
    *,
    document_id: str,
    section_title: str,
    chunk_index: int,
    text: str,
) -> str:
    seed = "|".join(
        (
            document_id,
            canonicalize_text(section_title),
            str(chunk_index),
            canonical_hash(text),
        )
    )

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]

    return f"{document_id}::chunk-{chunk_index:03d}::{digest}"


def chunk_document(
    *,
    document: FinancialKnowledgeDocument,
    body: str,
    minimum_words: int = 45,
    target_words: int = 110,
    maximum_words: int = 180,
) -> tuple[FinancialKnowledgeChunk, ...]:
    sections = split_sections(body)
    chunks: list[FinancialKnowledgeChunk] = []
    global_chunk_index = 0

    for section_index, (
        section_title,
        section_text,
    ) in enumerate(
        sections,
        start=1,
    ):
        paragraphs = split_paragraphs(section_text)

        section_chunks = build_section_chunks(
            paragraphs=paragraphs,
            minimum_words=minimum_words,
            target_words=target_words,
            maximum_words=maximum_words,
        )

        for section_chunk in section_chunks:
            global_chunk_index += 1

            contextual_text = normalize_text(
                f"{document.title}. Secao: {section_title}. {section_chunk}"
            )

            chunk = FinancialKnowledgeChunk(
                chunk_id=stable_chunk_id(
                    document_id=document.document_id,
                    section_title=section_title,
                    chunk_index=global_chunk_index,
                    text=contextual_text,
                ),
                document_id=document.document_id,
                document_title=document.title,
                document_path=document.path,
                area=document.area,
                topic=document.topic,
                section_title=section_title,
                section_index=section_index,
                chunk_index=global_chunk_index,
                language=document.language,
                version=document.version,
                source_ids=document.source_ids,
                text=contextual_text,
                word_count=word_count(contextual_text),
                character_count=len(contextual_text),
                content_hash=content_hash(contextual_text),
                canonical_hash=canonical_hash(contextual_text),
            )

            chunks.append(chunk)

    return tuple(chunks)


def discover_topic_documents(
    root: Path,
) -> tuple[Path, ...]:
    directories = (
        root / "educadora_financeira",
        root / "seguranca_financeira",
    )

    paths: list[Path] = []

    for directory in directories:
        if not directory.is_dir():
            raise FileNotFoundError(f"Diretorio nao encontrado: {directory}")

        paths.extend(sorted(directory.glob("*.md")))

    return tuple(paths)


def create_chunking_report(
    *,
    root: Path,
    minimum_words: int = 45,
    target_words: int = 110,
    maximum_words: int = 180,
) -> FinancialKnowledgeChunkingReport:
    if minimum_words <= 0:
        raise ValueError("minimum_words deve ser positivo.")

    if not (minimum_words <= target_words <= maximum_words):
        raise ValueError("A ordem deve ser minimum <= target <= maximum.")

    document_paths = discover_topic_documents(root)

    documents: list[FinancialKnowledgeDocument] = []

    chunks: list[FinancialKnowledgeChunk] = []

    for path in document_paths:
        document, body = load_document(
            root=root,
            path=path,
        )

        documents.append(document)

        chunks.extend(
            chunk_document(
                document=document,
                body=body,
                minimum_words=minimum_words,
                target_words=target_words,
                maximum_words=maximum_words,
            )
        )

    chunks_by_hash: dict[
        str,
        list[str],
    ] = {}

    for chunk in chunks:
        chunks_by_hash.setdefault(
            chunk.canonical_hash,
            [],
        ).append(chunk.chunk_id)

    duplicate_groups = tuple(
        tuple(chunk_ids) for chunk_ids in chunks_by_hash.values() if len(chunk_ids) > 1
    )

    observed_word_counts = [chunk.word_count for chunk in chunks]

    return FinancialKnowledgeChunkingReport(
        schema_version=1,
        source_root=str(root),
        document_count=len(documents),
        chunk_count=len(chunks),
        duplicate_chunk_count=sum(len(group) - 1 for group in duplicate_groups),
        duplicate_groups=duplicate_groups,
        education_document_count=sum(
            document.area == "educacao_financeira" for document in documents
        ),
        security_document_count=sum(
            document.area == "seguranca_financeira" for document in documents
        ),
        education_chunk_count=sum(
            chunk.area == "educacao_financeira" for chunk in chunks
        ),
        security_chunk_count=sum(
            chunk.area == "seguranca_financeira" for chunk in chunks
        ),
        minimum_chunk_words=min(
            observed_word_counts,
            default=0,
        ),
        maximum_chunk_words=max(
            observed_word_counts,
            default=0,
        ),
        mean_chunk_words=(
            sum(observed_word_counts) / len(observed_word_counts)
            if observed_word_counts
            else 0.0
        ),
        chunks=tuple(chunks),
        neon_used=False,
        gemini_used=False,
    )


def write_chunking_outputs(
    *,
    report: FinancialKnowledgeChunkingReport,
    output_directory: Path,
) -> dict[str, Path]:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = output_directory / "financial_knowledge_chunks.json"
    jsonl_path = output_directory / "financial_knowledge_chunks.jsonl"
    report_path = output_directory / "financial_knowledge_chunking_report.json"

    chunk_payloads = [chunk.as_dict() for chunk in report.chunks]

    json_path.write_text(
        json.dumps(
            chunk_payloads,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    jsonl_path.write_text(
        "".join(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
            for payload in chunk_payloads
        ),
        encoding="utf-8",
    )

    report_payload = report.as_dict()
    report_payload["chunks"] = []

    report_path.write_text(
        json.dumps(
            report_payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "json": json_path,
        "jsonl": jsonl_path,
        "report": report_path,
    }


def lexical_score(
    *,
    query: str,
    text: str,
) -> float:
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
        "diferenca",
        "diferença",
    }

    query_terms = {
        term
        for term in TOKEN_PATTERN.findall(canonicalize_text(query))
        if len(term) >= 4 and term not in stopwords
    }

    if not query_terms:
        return 0.0

    text_terms = set(TOKEN_PATTERN.findall(canonicalize_text(text)))

    matches = query_terms.intersection(text_terms)

    return len(matches) / len(query_terms)


def lexical_search(
    *,
    query: str,
    chunks: Sequence[FinancialKnowledgeChunk],
    top_k: int = 4,
) -> tuple[
    tuple[FinancialKnowledgeChunk, float],
    ...,
]:
    if top_k <= 0:
        raise ValueError("top_k deve ser positivo.")

    scored = [
        (
            chunk,
            lexical_score(
                query=query,
                text=(
                    chunk.document_title
                    + " "
                    + chunk.topic
                    + " "
                    + chunk.section_title
                    + " "
                    + chunk.text
                ),
            ),
        )
        for chunk in chunks
    ]

    ranked = sorted(
        scored,
        key=lambda item: (
            -item[1],
            item[0].document_id,
            item[0].chunk_index,
        ),
    )

    return tuple(item for item in ranked[:top_k] if item[1] > 0)


def validate_official_questions(
    chunks: Sequence[FinancialKnowledgeChunk],
) -> dict[str, Any]:
    cases = (
        (
            "reserva-financeira-001",
            "Como montar uma reserva financeira?",
            "reserva_de_emergencia",
        ),
        (
            "orcamento-mensal-001",
            "Como organizar renda e despesas mensais?",
            "orcamento_pessoal",
        ),
        (
            "cartao-credito-001",
            "Como usar cartao de credito sem me endividar?",
            "cartao_de_credito",
        ),
        (
            "dividas-priorizacao-001",
            "Qual divida devo pagar primeiro?",
            "priorizacao_de_dividas",
        ),
        (
            "gastos-fixos-variaveis-001",
            "Qual a diferenca entre gastos fixos e variaveis?",
            "classificacao_de_gastos",
        ),
    )

    results: list[dict[str, Any]] = []

    for case_id, question, expected_topic in cases:
        ranked = lexical_search(
            query=question,
            chunks=chunks,
            top_k=4,
        )

        retrieved_topics = [chunk.topic for chunk, _score in ranked]

        hit = expected_topic in retrieved_topics

        results.append(
            {
                "case_id": case_id,
                "question": question,
                "expected_topic": expected_topic,
                "hit": hit,
                "results": [
                    {
                        "rank": rank,
                        "chunk_id": chunk.chunk_id,
                        "document_id": (chunk.document_id),
                        "topic": chunk.topic,
                        "section_title": (chunk.section_title),
                        "score": round(
                            score,
                            6,
                        ),
                        "preview": (chunk.text[:240]),
                    }
                    for rank, (
                        chunk,
                        score,
                    ) in enumerate(
                        ranked,
                        start=1,
                    )
                ],
            }
        )

    hit_count = sum(bool(case["hit"]) for case in results)

    return {
        "case_count": len(results),
        "hit_count": hit_count,
        "hit_rate": (hit_count / len(results) if results else 0.0),
        "passed": hit_count == len(results),
        "cases": results,
    }


__all__ = [
    "FinancialKnowledgeChunk",
    "FinancialKnowledgeChunkingReport",
    "FinancialKnowledgeDocument",
    "canonical_hash",
    "canonicalize_text",
    "chunk_document",
    "content_hash",
    "create_chunking_report",
    "discover_topic_documents",
    "lexical_score",
    "lexical_search",
    "load_document",
    "normalize_text",
    "parse_frontmatter",
    "split_sections",
    "validate_official_questions",
    "word_count",
    "write_chunking_outputs",
]

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

SearchFunction = Callable[
    ...,
    list[dict[str, Any]],
]


@dataclass(frozen=True)
class RetrievalVariantMetrics:
    """
    Métricas determinísticas de uma variante de recuperação.
    """

    name: str
    sentence_window_enabled: bool
    elapsed_ms: float

    result_count: int
    unique_source_count: int

    total_context_characters: int
    average_context_characters: float

    sentence_window_applied_count: int
    sentence_window_coverage: float

    top_result_id: str | None
    top_source: str | None

    result_ids: list[str]
    sources: list[str]

    results_preview: list[dict[str, Any]]


def _extract_text(
    item: Mapping[str, Any],
) -> str:
    """
    Extrai o contexto efetivamente devolvido pelo RAG.
    """

    for field_name in (
        "sentence_window_text",
        "chunk_text",
        "texto",
        "trecho",
        "conteudo",
        "content",
        "contexto",
    ):
        value = str(
            item.get(
                field_name,
                "",
            )
            or ""
        ).strip()

        if value:
            return value

    return ""


def _extract_source(
    item: Mapping[str, Any],
) -> str:
    for field_name in (
        "fonte",
        "source",
        "arquivo",
        "documento",
        "titulo",
        "title",
    ):
        value = str(
            item.get(
                field_name,
                "",
            )
            or ""
        ).strip()

        if value:
            return value

    return "unknown"


def _safe_float(
    value: object,
) -> float | None:
    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def _result_identifier(
    item: Mapping[str, Any],
) -> str:
    """
    Produz uma identificação estável entre as variantes A e B.
    """

    for field_name in (
        "id",
        "chunk_id",
        "knowledge_chunk_id",
    ):
        value = item.get(field_name)

        if value not in (
            None,
            "",
        ):
            return f"{field_name}:{value}"

    document_id = item.get(
        "documento_id",
        item.get(
            "document_id",
        ),
    )

    chunk_index = item.get(
        "chunk_index",
    )

    if document_id not in (
        None,
        "",
    ):
        return (
            "document:"
            + str(document_id)
            + ":chunk:"
            + str(chunk_index if chunk_index is not None else "unknown")
        )

    source = _extract_source(item)

    if source != "unknown" or chunk_index is not None:
        return (
            "source:"
            + source
            + ":chunk:"
            + str(chunk_index if chunk_index is not None else "unknown")
        )

    text = _extract_text(item)

    digest = hashlib.sha256(
        text.encode(
            "utf-8",
        )
    ).hexdigest()[:20]

    return "content:" + digest


def _text_digest(
    text: str,
) -> str:
    return hashlib.sha256(
        text.encode(
            "utf-8",
        )
    ).hexdigest()


def _build_result_preview(
    item: Mapping[str, Any],
    *,
    include_text_preview: bool,
) -> dict[str, Any]:
    text = _extract_text(item)

    score = None

    for field_name in (
        "rerank_score",
        "score_final",
        "score",
        "similarity",
        "similaridade",
    ):
        score = _safe_float(item.get(field_name))

        if score is not None:
            break

    preview: dict[str, Any] = {
        "result_id": (_result_identifier(item)),
        "source": (_extract_source(item)),
        "chunk_index": item.get("chunk_index"),
        "context_characters": len(text),
        "context_sha256": (_text_digest(text)),
        "sentence_window_applied": bool(
            item.get(
                "sentence_window_applied",
                False,
            )
        ),
        "sentence_window_version": item.get("sentence_window_version"),
        "mode": (item.get("modo_busca") or item.get("mode")),
        "score": score,
    }

    if include_text_preview:
        preview["text_preview"] = text[:300]

    return preview


def _normalize_results(
    raw_results: object,
) -> list[dict[str, Any]]:
    if raw_results is None:
        return []

    if not isinstance(
        raw_results,
        list,
    ):
        raise TypeError("A função de busca deve retornar uma lista.")

    normalized: list[dict[str, Any]] = []

    for item in raw_results:
        if isinstance(
            item,
            Mapping,
        ):
            normalized.append(dict(item))

    return normalized


def run_retrieval_variant(
    *,
    search_function: SearchFunction,
    query: str,
    language: str,
    top_k: int,
    name: str,
    sentence_window_enabled: bool,
    include_text_preview: bool = False,
) -> RetrievalVariantMetrics:
    """
    Executa uma única variante do mecanismo de recuperação.
    """

    started_at = perf_counter()

    raw_results = search_function(
        query,
        idioma=language,
        top_k=top_k,
        sentence_window_enabled=(sentence_window_enabled),
    )

    elapsed_ms = (perf_counter() - started_at) * 1000

    results = _normalize_results(raw_results)

    result_ids = [_result_identifier(item) for item in results]

    sources = [_extract_source(item) for item in results]

    texts = [_extract_text(item) for item in results]

    total_context_characters = sum(len(text) for text in texts)

    average_context_characters = (
        total_context_characters / len(results) if results else 0.0
    )

    sentence_window_applied_count = sum(
        1
        for item in results
        if bool(
            item.get(
                "sentence_window_applied",
                False,
            )
        )
    )

    sentence_window_coverage = (
        sentence_window_applied_count / len(results) if results else 0.0
    )

    return RetrievalVariantMetrics(
        name=name,
        sentence_window_enabled=(sentence_window_enabled),
        elapsed_ms=round(
            elapsed_ms,
            3,
        ),
        result_count=len(results),
        unique_source_count=len(set(sources)),
        total_context_characters=(total_context_characters),
        average_context_characters=round(
            average_context_characters,
            3,
        ),
        sentence_window_applied_count=(sentence_window_applied_count),
        sentence_window_coverage=round(
            sentence_window_coverage,
            6,
        ),
        top_result_id=(result_ids[0] if result_ids else None),
        top_source=(sources[0] if sources else None),
        result_ids=result_ids,
        sources=sources,
        results_preview=[
            _build_result_preview(
                item,
                include_text_preview=(include_text_preview),
            )
            for item in results
        ],
    )


def compare_retrieval_variants(
    *,
    query: str,
    language: str = "pt",
    top_k: int = 4,
    search_function: (SearchFunction | None) = None,
    include_text_preview: bool = False,
) -> dict[str, Any]:
    """
    Compara o RAG híbrido atual com Sentence-Window desligado
    e ligado.

    Esta comparação mede recuperação, contexto e latência.
    A qualidade semântica será decidida posteriormente pela
    RAG Triad existente.
    """

    rendered_query = str(query or "").strip()

    if len(rendered_query) < 3:
        raise ValueError("A pergunta precisa ter pelo menos 3 caracteres.")

    safe_language = str(language or "pt").strip().lower()

    safe_top_k = max(
        1,
        min(
            int(top_k),
            20,
        ),
    )

    if search_function is None:
        from src.rag_engine import (
            search_knowledge_base_hybrid,
        )

        search_function = search_knowledge_base_hybrid

    baseline = run_retrieval_variant(
        search_function=search_function,
        query=rendered_query,
        language=safe_language,
        top_k=safe_top_k,
        name="hybrid_baseline",
        sentence_window_enabled=False,
        include_text_preview=(include_text_preview),
    )

    sentence_window = run_retrieval_variant(
        search_function=search_function,
        query=rendered_query,
        language=safe_language,
        top_k=safe_top_k,
        name="hybrid_sentence_window",
        sentence_window_enabled=True,
        include_text_preview=(include_text_preview),
    )

    baseline_ids = set(baseline.result_ids)

    sentence_window_ids = set(sentence_window.result_ids)

    shared_ids = baseline_ids & sentence_window_ids

    union_ids = baseline_ids | sentence_window_ids

    overlap_ratio = len(shared_ids) / len(union_ids) if union_ids else 1.0

    context_character_delta = (
        sentence_window.total_context_characters - baseline.total_context_characters
    )

    context_character_delta_percent = (
        (context_character_delta / baseline.total_context_characters) * 100
        if baseline.total_context_characters
        else 0.0
    )

    latency_delta_ms = sentence_window.elapsed_ms - baseline.elapsed_ms

    latency_delta_percent = (
        (latency_delta_ms / baseline.elapsed_ms) * 100 if baseline.elapsed_ms else 0.0
    )

    return {
        "schema_version": 1,
        "query": rendered_query,
        "language": safe_language,
        "top_k": safe_top_k,
        "generated_at": (datetime.now(UTC).isoformat()),
        "variant_a": asdict(baseline),
        "variant_b": asdict(sentence_window),
        "comparison": {
            "shared_result_count": len(shared_ids),
            "union_result_count": len(union_ids),
            "result_overlap_ratio": round(
                overlap_ratio,
                6,
            ),
            "same_top_result": (
                baseline.top_result_id == sentence_window.top_result_id
            ),
            "same_top_source": (baseline.top_source == sentence_window.top_source),
            "context_character_delta": (context_character_delta),
            "context_character_delta_percent": round(
                context_character_delta_percent,
                3,
            ),
            "latency_delta_ms": round(
                latency_delta_ms,
                3,
            ),
            "latency_delta_percent": round(
                latency_delta_percent,
                3,
            ),
            "sentence_window_coverage": (sentence_window.sentence_window_coverage),
            "sentence_window_fallback_count": (
                sentence_window.result_count
                - sentence_window.sentence_window_applied_count
            ),
            "quality_decision": ("pending_rag_triad"),
        },
    }


def _normalize_queries(
    queries: Sequence[str],
) -> list[str]:
    normalized: list[str] = []

    for query in queries:
        rendered = str(query or "").strip()

        if len(rendered) < 3:
            continue

        if rendered not in normalized:
            normalized.append(rendered)

    if not normalized:
        raise ValueError("Nenhuma pergunta válida foi fornecida.")

    return normalized


def _safe_label(
    value: str,
) -> str:
    rendered = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        str(value or "").strip(),
    ).strip("-")

    return rendered or "retrieval-ab"


def _build_markdown_report(
    payload: Mapping[str, Any],
) -> str:
    lines = [
        "# Comparação A/B — RAG híbrido e Sentence-Window",
        "",
        f"- Execução: `{payload['run_id']}`",
        f"- Gerado em: `{payload['generated_at']}`",
        f"- Idioma: `{payload['language']}`",
        f"- Top K: `{payload['top_k']}`",
        "",
        "## Resumo",
        "",
        "| Pergunta | A: resultados | B: resultados | Sobreposição | Contexto Δ | Latência Δ | Janela aplicada |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for case in payload["cases"]:
        if case.get("status") != "completed":
            lines.append(
                "| "
                + str(
                    case.get(
                        "query",
                        "",
                    )
                ).replace(
                    "|",
                    "\\|",
                )
                + " | erro | erro | - | - | - | - |"
            )

            continue

        comparison = case["comparison"]

        variant_a = case["variant_a"]

        variant_b = case["variant_b"]

        lines.append(
            "| "
            + str(case["query"]).replace(
                "|",
                "\\|",
            )
            + " | "
            + str(variant_a["result_count"])
            + " | "
            + str(variant_b["result_count"])
            + " | "
            + (f"{comparison['result_overlap_ratio']:.1%}")
            + " | "
            + str(comparison["context_character_delta"])
            + " caracteres | "
            + (f"{comparison['latency_delta_ms']:.2f} ms")
            + " | "
            + (f"{comparison['sentence_window_coverage']:.1%}")
            + " |"
        )

    lines.extend(
        (
            "",
            "## Interpretação",
            "",
            "- A variante A representa o RAG híbrido atual.",
            "- A variante B representa o mesmo RAG com Sentence-Window.",
            "- Este relatório ainda não escolhe um vencedor.",
            "- A decisão de qualidade depende da RAG Triad.",
            "",
            "## Segurança",
            "",
            "- O texto completo dos contextos não é salvo por padrão.",
            "- Cada contexto recebe um SHA-256 para rastreabilidade.",
            "",
        )
    )

    return "\n".join(lines)


def run_retrieval_ab_suite(
    *,
    queries: Sequence[str],
    language: str = "pt",
    top_k: int = 4,
    output_directory: (str | Path) = ("artifacts/evaluation/retrieval_ab"),
    run_label: str = "retrieval-ab",
    search_function: (SearchFunction | None) = None,
    include_text_preview: bool = False,
    continue_on_error: bool = True,
) -> dict[str, Any]:
    """
    Executa uma suíte e salva relatório versionado e histórico.
    """

    normalized_queries = _normalize_queries(queries)

    safe_language = str(language or "pt").strip().lower()

    safe_top_k = max(
        1,
        min(
            int(top_k),
            20,
        ),
    )

    generated_at = datetime.now(UTC)

    timestamp = generated_at.strftime("%Y%m%dT%H%M%SZ")

    digest = hashlib.sha256(
        "\n".join(normalized_queries).encode(
            "utf-8",
        )
    ).hexdigest()[:10]

    run_id = _safe_label(run_label) + "-" + timestamp + "-" + digest

    cases: list[dict[str, Any]] = []

    for query in normalized_queries:
        try:
            case = compare_retrieval_variants(
                query=query,
                language=safe_language,
                top_k=safe_top_k,
                search_function=(search_function),
                include_text_preview=(include_text_preview),
            )

            case["status"] = "completed"

            cases.append(case)

        except Exception as exc:
            if not continue_on_error:
                raise

            cases.append(
                {
                    "query": query,
                    "status": "failed",
                    "error_type": (type(exc).__name__),
                    "error_message": str(exc)[:500],
                }
            )

    completed_count = sum(1 for case in cases if case.get("status") == "completed")

    failed_count = len(cases) - completed_count

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "generated_at": (generated_at.isoformat()),
        "language": safe_language,
        "top_k": safe_top_k,
        "question_count": len(normalized_queries),
        "completed_count": (completed_count),
        "failed_count": (failed_count),
        "quality_decision": ("pending_rag_triad"),
        "cases": cases,
    }

    output_path = Path(output_directory)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = output_path / f"{run_id}.json"

    markdown_path = output_path / f"{run_id}.md"

    history_path = output_path / "history.jsonl"

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    markdown_path.write_text(
        _build_markdown_report(payload),
        encoding="utf-8",
    )

    history_record = {
        "run_id": run_id,
        "generated_at": (payload["generated_at"]),
        "question_count": (payload["question_count"]),
        "completed_count": (completed_count),
        "failed_count": (failed_count),
        "json_report": str(json_path),
        "markdown_report": str(markdown_path),
        "quality_decision": ("pending_rag_triad"),
    }

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as history_file:
        history_file.write(
            json.dumps(
                history_record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return {
        "run_id": run_id,
        "payload": payload,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "history_path": str(history_path),
    }

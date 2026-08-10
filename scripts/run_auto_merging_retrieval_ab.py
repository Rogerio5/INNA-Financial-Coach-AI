from __future__ import annotations

import csv
import json
import os
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(".env", override=True)


@dataclass(frozen=True)
class RetrievalVariant:
    name: str
    sentence_window_enabled: bool
    auto_merging_enabled: bool


VARIANTS = (
    RetrievalVariant(
        name="hybrid_baseline",
        sentence_window_enabled=False,
        auto_merging_enabled=False,
    ),
    RetrievalVariant(
        name="hybrid_sentence_window",
        sentence_window_enabled=True,
        auto_merging_enabled=False,
    ),
    RetrievalVariant(
        name="hybrid_auto_merging",
        sentence_window_enabled=False,
        auto_merging_enabled=True,
    ),
)


PROFILING_FIELDS = (
    "query_embedding_ms",
    "vector_conversion_ms",
    "vector_database_ms",
    "vector_postprocess_ms",
    "vector_semantic_total_ms",
    "vector_retrieval_ms",
    "text_retrieval_ms",
    "rrf_ms",
    "rerank_ms",
    "auto_merging_ms",
    "sentence_window_ms",
    "retrieval_total_ms",
)


def _positive_int_environment(
    name: str,
    *,
    default: int,
    allow_zero: bool = False,
) -> int:
    raw = str(os.getenv(name, "")).strip()

    if not raw:
        return default

    try:
        value = int(raw)
    except ValueError:
        return default

    minimum = 0 if allow_zero else 1

    if value < minimum:
        return default

    return value


def _result_text(
    item: dict[str, Any],
) -> str:
    return str(
        item.get("chunk_text")
        or item.get("trecho")
        or item.get("texto")
        or ""
    ).strip()


def _document_identity(
    item: dict[str, Any],
) -> str:
    value = (
        item.get("documento_key")
        or item.get("documento_id")
        or item.get("fonte")
        or "unknown"
    )

    return str(value)


def _inspect_results(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    context_characters = sum(
        len(_result_text(item))
        for item in results
    )

    documents = sorted(
        {
            _document_identity(item)
            for item in results
        }
    )

    auto_merging_applied_count = sum(
        1
        for item in results
        if item.get("auto_merging_applied") is True
    )

    auto_merging_child_count_total = sum(
        int(item.get("auto_merging_child_count") or 0)
        for item in results
        if item.get("auto_merging_applied") is True
    )

    sentence_window_applied_count = sum(
        1
        for item in results
        if item.get("sentence_window_applied") is True
    )

    chunk_indexes = [
        item.get("chunk_index")
        for item in results
        if item.get("chunk_index") is not None
    ]

    return {
        "result_count": len(results),
        "context_characters": context_characters,
        "unique_document_count": len(documents),
        "documents": ";".join(documents),
        "chunk_indexes": json.dumps(
            chunk_indexes,
            ensure_ascii=False,
        ),
        "auto_merging_applied_count": (
            auto_merging_applied_count
        ),
        "auto_merging_child_count_total": (
            auto_merging_child_count_total
        ),
        "sentence_window_applied_count": (
            sentence_window_applied_count
        ),
    }


def _load_dataset() -> list[dict[str, Any]]:
    try:
        from scripts.evaluate_rag import (
            PERGUNTAS_TESTE,
        )
    except ModuleNotFoundError:
        from evaluate_rag import (
            PERGUNTAS_TESTE,
        )

    dataset: list[dict[str, Any]] = []

    for index, raw_item in enumerate(
        PERGUNTAS_TESTE,
        start=1,
    ):
        if not isinstance(raw_item, dict):
            continue

        question = str(
            raw_item.get("pergunta")
            or ""
        ).strip()

        if not question:
            continue

        dataset.append(
            {
                "dataset_index": index,
                "category": str(
                    raw_item.get("categoria")
                    or "rag"
                ),
                "question": question,
            }
        )

    limit = _positive_int_environment(
        "INNA_RAG_AB_LIMIT",
        default=0,
        allow_zero=True,
    )

    if limit:
        return dataset[:limit]

    return dataset


def _variants_for_dataset_index(
    dataset_index: int,
) -> tuple[RetrievalVariant, ...]:
    offset = (
        max(int(dataset_index), 1) - 1
    ) % len(VARIANTS)

    return (
        VARIANTS[offset:]
        + VARIANTS[:offset]
    )


def run_variant(
    *,
    dataset_item: dict[str, Any],
    variant: RetrievalVariant,
    top_k: int,
) -> dict[str, Any]:
    from src.rag_engine import (
        search_knowledge_base_hybrid,
    )

    profiling: dict[str, float] = {}

    started = time.perf_counter()

    results = search_knowledge_base_hybrid(
        dataset_item["question"],
        idioma="pt",
        top_k=top_k,
        sentence_window_enabled=(
            variant.sentence_window_enabled
        ),
        auto_merging_enabled=(
            variant.auto_merging_enabled
        ),
        auto_merging_parent_size=3,
        auto_merging_min_children=2,
        auto_merging_max_characters=4000,
        profiling=profiling,
    )

    outer_elapsed_ms = round(
        (
            time.perf_counter()
            - started
        )
        * 1000,
        2,
    )

    inspection = _inspect_results(results)

    row: dict[str, Any] = {
        "dataset_index": dataset_item[
            "dataset_index"
        ],
        "category": dataset_item["category"],
        "question": dataset_item["question"],
        "variant": variant.name,
        "sentence_window_enabled": (
            variant.sentence_window_enabled
        ),
        "auto_merging_enabled": (
            variant.auto_merging_enabled
        ),
        "top_k": top_k,
        "outer_elapsed_ms": outer_elapsed_ms,
        **inspection,
    }

    for field in PROFILING_FIELDS:
        row[field] = round(
            float(profiling.get(field) or 0.0),
            2,
        )

    return row


def _average(
    rows: list[dict[str, Any]],
    field: str,
) -> float:
    values = [
        float(row.get(field) or 0.0)
        for row in rows
    ]

    if not values:
        return 0.0

    return round(
        statistics.fmean(values),
        2,
    )


def build_summary(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []

    for variant in VARIANTS:
        variant_rows = [
            row
            for row in rows
            if row["variant"] == variant.name
        ]

        summaries.append(
            {
                "variant": variant.name,
                "queries": len(variant_rows),
                "avg_retrieval_total_ms": _average(
                    variant_rows,
                    "retrieval_total_ms",
                ),
                "avg_outer_elapsed_ms": _average(
                    variant_rows,
                    "outer_elapsed_ms",
                ),
                "avg_vector_retrieval_ms": _average(
                    variant_rows,
                    "vector_retrieval_ms",
                ),
                "avg_text_retrieval_ms": _average(
                    variant_rows,
                    "text_retrieval_ms",
                ),
                "avg_rrf_ms": _average(
                    variant_rows,
                    "rrf_ms",
                ),
                "avg_rerank_ms": _average(
                    variant_rows,
                    "rerank_ms",
                ),
                "avg_auto_merging_ms": _average(
                    variant_rows,
                    "auto_merging_ms",
                ),
                "avg_sentence_window_ms": _average(
                    variant_rows,
                    "sentence_window_ms",
                ),
                "avg_result_count": _average(
                    variant_rows,
                    "result_count",
                ),
                "avg_context_characters": _average(
                    variant_rows,
                    "context_characters",
                ),
                "avg_unique_documents": _average(
                    variant_rows,
                    "unique_document_count",
                ),
                "auto_merging_applied_total": sum(
                    int(
                        row.get(
                            "auto_merging_applied_count"
                        )
                        or 0
                    )
                    for row in variant_rows
                ),
                "auto_merging_child_count_total": sum(
                    int(
                        row.get(
                            "auto_merging_child_count_total"
                        )
                        or 0
                    )
                    for row in variant_rows
                ),
                "sentence_window_applied_total": sum(
                    int(
                        row.get(
                            "sentence_window_applied_count"
                        )
                        or 0
                    )
                    for row in variant_rows
                ),
            }
        )

    baseline = next(
        (
            item
            for item in summaries
            if item["variant"]
            == "hybrid_baseline"
        ),
        None,
    )

    if baseline is not None:
        for item in summaries:
            item[
                "delta_retrieval_ms_vs_baseline"
            ] = round(
                item["avg_retrieval_total_ms"]
                - baseline["avg_retrieval_total_ms"],
                2,
            )

            item[
                "delta_context_chars_vs_baseline"
            ] = round(
                item["avg_context_characters"]
                - baseline["avg_context_characters"],
                2,
            )

            item[
                "delta_results_vs_baseline"
            ] = round(
                item["avg_result_count"]
                - baseline["avg_result_count"],
                2,
            )

    return summaries


def _write_reports(
    rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> tuple[Path, Path, Path]:
    reports_dir = Path("reports")
    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        reports_dir
        / "auto_merging_retrieval_ab_results.csv"
    )

    json_path = (
        reports_dir
        / "auto_merging_retrieval_ab_summary.json"
    )

    md_path = (
        reports_dir
        / "auto_merging_retrieval_ab_report.md"
    )

    if rows:
        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=list(rows[0].keys()),
            )

            writer.writeheader()
            writer.writerows(rows)

    payload = {
        "experiment": (
            "auto_merging_retrieval_ab"
        ),
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "simulation": False,
        "variants": [
            {
                "name": variant.name,
                "sentence_window_enabled": (
                    variant.sentence_window_enabled
                ),
                "auto_merging_enabled": (
                    variant.auto_merging_enabled
                ),
            }
            for variant in VARIANTS
        ],
        "summary": summaries,
    }

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    markdown = [
        "# Auto-Merging Retrieval — Experimento A/B/C",
        "",
        "Comparação isolada entre:",
        "",
        "- Hybrid Baseline",
        "- Hybrid + Sentence Window",
        "- Hybrid + Auto-Merging",
        "",
        "## Resumo",
        "",
        (
            "| Variante | Queries | Retrieval médio ms | "
            "Contexto médio chars | Resultados médios | "
            "Auto-Merges | Sentence Windows |"
        ),
        (
            "|---|---:|---:|---:|---:|---:|---:|"
        ),
    ]

    for item in summaries:
        markdown.append(
            "| "
            f"{item['variant']} | "
            f"{item['queries']} | "
            f"{item['avg_retrieval_total_ms']} | "
            f"{item['avg_context_characters']} | "
            f"{item['avg_result_count']} | "
            f"{item['auto_merging_applied_total']} | "
            f"{item['sentence_window_applied_total']} |"
        )

    markdown.extend(
        [
            "",
            "## Política experimental",
            "",
            (
                "Sentence Window e Auto-Merging são "
                "avaliados isoladamente nesta fase."
            ),
            "",
            (
                "Nenhuma variante experimental é "
                "ativada automaticamente em produção."
            ),
        ]
    )

    md_path.write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )

    return (
        csv_path,
        json_path,
        md_path,
    )


def main() -> None:
    dataset = _load_dataset()

    top_k = _positive_int_environment(
        "INNA_RAG_AB_TOP_K",
        default=3,
    )

    if not dataset:
        raise RuntimeError(
            "RAG_AB_DATASET_EMPTY"
        )

    print(
        "=========================================="
    )
    print(
        "AUTO-MERGING RETRIEVAL A/B/C"
    )
    print(
        "=========================================="
    )
    print(
        f"DATASET_SIZE={len(dataset)}"
    )
    print(
        f"TOP_K={top_k}"
    )
    print(
        f"VARIANT_COUNT={len(VARIANTS)}"
    )

    rows: list[dict[str, Any]] = []

    warmup_item = dataset[0]

    print()
    print(
        "=========================================="
    )
    print(
        "WARMUP RETRIEVAL"
    )
    print(
        "=========================================="
    )

    warmup_profiling: dict[str, float] = {}

    from src.rag_engine import (
        search_knowledge_base_hybrid,
    )

    search_knowledge_base_hybrid(
        warmup_item["question"],
        idioma="pt",
        top_k=top_k,
        sentence_window_enabled=False,
        auto_merging_enabled=False,
        profiling=warmup_profiling,
    )

    print(
        "WARMUP_COMPLETE=True"
    )
    print(
        "WARMUP_NOT_INCLUDED_IN_RESULTS=True"
    )

    for dataset_item in dataset:
        variant_order = (
            _variants_for_dataset_index(
                dataset_item["dataset_index"]
            )
        )

        print()
        print(
            "VARIANT_ORDER="
            + ",".join(
                item.name
                for item in variant_order
            )
        )

        for variant in variant_order:
            print()
            print(
                "QUESTION_INDEX="
                f"{dataset_item['dataset_index']}"
            )
            print(
                f"VARIANT={variant.name}"
            )

            row = run_variant(
                dataset_item=dataset_item,
                variant=variant,
                top_k=top_k,
            )

            rows.append(row)

            print(
                "RETRIEVAL_TOTAL_MS="
                f"{row['retrieval_total_ms']}"
            )
            print(
                "RESULT_COUNT="
                f"{row['result_count']}"
            )
            print(
                "CONTEXT_CHARACTERS="
                f"{row['context_characters']}"
            )
            print(
                "AUTO_MERGING_APPLIED="
                f"{row['auto_merging_applied_count']}"
            )
            print(
                "SENTENCE_WINDOW_APPLIED="
                f"{row['sentence_window_applied_count']}"
            )

    summaries = build_summary(rows)

    (
        csv_path,
        json_path,
        md_path,
    ) = _write_reports(
        rows,
        summaries,
    )

    print()
    print(
        "=========================================="
    )
    print(
        "EXPERIMENT SUMMARY"
    )
    print(
        "=========================================="
    )

    for summary in summaries:
        print()
        print(
            f"VARIANT={summary['variant']}"
        )
        print(
            "AVG_RETRIEVAL_TOTAL_MS="
            f"{summary['avg_retrieval_total_ms']}"
        )
        print(
            "AVG_CONTEXT_CHARACTERS="
            f"{summary['avg_context_characters']}"
        )
        print(
            "AVG_AUTO_MERGING_MS="
            f"{summary['avg_auto_merging_ms']}"
        )
        print(
            "AVG_RESULT_COUNT="
            f"{summary['avg_result_count']}"
        )
        print(
            "DELTA_RETRIEVAL_MS_VS_BASELINE="
            f"{summary['delta_retrieval_ms_vs_baseline']}"
        )
        print(
            "DELTA_CONTEXT_VS_BASELINE="
            f"{summary['delta_context_chars_vs_baseline']}"
        )

    print()
    print(
        f"CSV_REPORT={csv_path}"
    )
    print(
        f"JSON_REPORT={json_path}"
    )
    print(
        f"MARKDOWN_REPORT={md_path}"
    )

    print()
    print(
        "AUTO_MERGING_AB_SUITE_COMPLETE=True"
    )


if __name__ == "__main__":
    main()

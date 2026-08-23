from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True, slots=True)
class RagObservabilitySummary:
    total_questions: int
    gemini_count: int | None
    security_count: int | None
    fallback_count: int | None
    average_latency_ms: float | None
    maximum_latency_ms: float | None
    available_columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    has_data: bool


EXPECTED_RAG_LOG_COLUMNS: tuple[str, ...] = (
    "pergunta",
    "modo",
    "fontes",
    "data_hora",
    "tempo_ms",
    "gemini",
    "seguranca",
    "fallback",
)


def _normalise_boolean_series(
    series: pd.Series,
) -> pd.Series:
    true_values = {
        "true",
        "1",
        "sim",
        "yes",
        "y",
        "on",
    }

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(true_values)
    )


def _optional_boolean_count(
    frame: pd.DataFrame,
    column: str,
) -> int | None:
    if column not in frame.columns:
        return None

    return int(
        _normalise_boolean_series(
            frame[column]
        ).sum()
    )


def _optional_numeric_series(
    frame: pd.DataFrame,
    column: str,
) -> pd.Series | None:
    if column not in frame.columns:
        return None

    values = pd.to_numeric(
        frame[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values


def build_rag_observability_summary(
    rag_df: pd.DataFrame | None,
) -> RagObservabilitySummary:
    frame = (
        rag_df.copy()
        if isinstance(rag_df, pd.DataFrame)
        else pd.DataFrame()
    )

    available_columns = tuple(
        column
        for column in EXPECTED_RAG_LOG_COLUMNS
        if column in frame.columns
    )

    missing_columns = tuple(
        column
        for column in EXPECTED_RAG_LOG_COLUMNS
        if column not in frame.columns
    )

    latency = _optional_numeric_series(
        frame,
        "tempo_ms",
    )

    return RagObservabilitySummary(
        total_questions=len(frame),
        gemini_count=_optional_boolean_count(
            frame,
            "gemini",
        ),
        security_count=_optional_boolean_count(
            frame,
            "seguranca",
        ),
        fallback_count=_optional_boolean_count(
            frame,
            "fallback",
        ),
        average_latency_ms=(
            float(latency.mean())
            if latency is not None
            else None
        ),
        maximum_latency_ms=(
            float(latency.max())
            if latency is not None
            else None
        ),
        available_columns=available_columns,
        missing_columns=missing_columns,
        has_data=not frame.empty,
    )


def build_mode_distribution(
    rag_df: pd.DataFrame | None,
) -> pd.DataFrame:
    if (
        not isinstance(rag_df, pd.DataFrame)
        or rag_df.empty
        or "modo" not in rag_df.columns
    ):
        return pd.DataFrame(
            columns=[
                "mode",
                "total",
            ]
        )

    frame = rag_df.copy()

    frame["modo"] = (
        frame["modo"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    frame.loc[
        frame["modo"].eq(""),
        "modo",
    ] = "unregistered"

    return (
        frame.groupby(
            "modo",
            dropna=False,
        )
        .size()
        .reset_index(
            name="total"
        )
        .rename(
            columns={
                "modo": "mode",
            }
        )
        .sort_values(
            "total",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


def build_latest_questions(
    rag_df: pd.DataFrame | None,
    *,
    limit: int = 20,
) -> pd.DataFrame:
    if (
        not isinstance(rag_df, pd.DataFrame)
        or rag_df.empty
    ):
        return pd.DataFrame()

    frame = rag_df.copy()

    date_column = None

    for candidate in (
        "data_hora",
        "data",
        "created_at",
    ):
        if candidate in frame.columns:
            date_column = candidate
            break

    if date_column is not None:
        frame[date_column] = pd.to_datetime(
            frame[date_column],
            errors="coerce",
            utc=True,
        )

        frame = frame.sort_values(
            date_column,
            ascending=False,
            na_position="last",
        )

    return frame.head(
        max(
            1,
            int(limit),
        )
    )


def export_rag_observability_csv(
    rag_df: pd.DataFrame | None,
) -> str:
    if not isinstance(
        rag_df,
        pd.DataFrame,
    ):
        return ""

    return rag_df.to_csv(
        index=False,
    )


def build_field_coverage(
    rag_df: pd.DataFrame | None,
) -> tuple[dict[str, Any], ...]:
    frame = (
        rag_df
        if isinstance(rag_df, pd.DataFrame)
        else pd.DataFrame()
    )

    total_rows = len(frame)
    rows = []

    for column in EXPECTED_RAG_LOG_COLUMNS:
        if column not in frame.columns:
            available_rows = 0
        else:
            available_rows = int(
                frame[column]
                .notna()
                .sum()
            )

        coverage_rate = (
            available_rows / total_rows
            if total_rows
            else 0.0
        )

        rows.append(
            {
                "field": column,
                "available_rows": (
                    available_rows
                ),
                "total_rows": total_rows,
                "coverage_rate": (
                    coverage_rate
                ),
                "available": (
                    column in frame.columns
                ),
            }
        )

    return tuple(rows)

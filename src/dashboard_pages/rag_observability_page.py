from __future__ import annotations

import os
from typing import Any

import pandas as pd
import psycopg2
import streamlit as st

from src.dashboard_pages.rag_observability_i18n import (
    RAG_OBSERVABILITY_TEXTS,
)
from src.dashboard_pages.technical_labels_i18n import (
    technical_label,
)
from src.evaluation.rag_observability_data import (
    build_field_coverage,
    build_latest_questions,
    build_mode_distribution,
    build_rag_observability_summary,
    export_rag_observability_csv,
)


def _language() -> str:
    return str(
        st.session_state.get(
            "dashboard_interface_lang",
            "pt",
        )
        or "pt"
    )


def rag_observability_t(
    key: str,
    default: str | None = None,
) -> str:
    language = _language()

    technical_keys = {
        "gemini": "gemini",
        "fallback": "fallback",
        "field_gemini": "gemini",
        "field_fallback": "fallback",
    }

    technical_key = technical_keys.get(
        key
    )

    if technical_key is not None:
        return technical_label(
            language,
            technical_key,
        )

    language_texts = (
        RAG_OBSERVABILITY_TEXTS.get(
            language,
            {},
        )
    )

    if key in language_texts:
        return language_texts[key]

    english_texts = (
        RAG_OBSERVABILITY_TEXTS[
            "en_us"
        ]
    )

    if key in english_texts:
        return english_texts[key]

    return default or key


def _load_rag_logs() -> tuple[
    pd.DataFrame,
    str | None,
]:
    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:
        return (
            pd.DataFrame(),
            "DATABASE_URL não configurada.",
        )

    connection = None

    try:
        connection = psycopg2.connect(
            database_url
        )

        frame = pd.read_sql_query(
            """
            SELECT *
            FROM rag_logs
            ORDER BY data_hora DESC;
            """,
            connection,
        )

        return frame, None

    except Exception as exc:
        return (
            pd.DataFrame(),
            str(exc),
        )

    finally:
        if connection is not None:
            connection.close()


def _metric_value(
    value: Any,
    *,
    suffix: str = "",
) -> str | int:
    if value is None:
        return "—"

    if isinstance(value, float):
        return (
            f"{value:.2f}"
            f"{suffix}"
        )

    return value


def _field_label(
    field_name: str,
) -> str:
    return rag_observability_t(
        f"field_{field_name}",
        field_name,
    )


def _render_source_status(
    *,
    error: str | None,
    has_data: bool,
) -> None:
    st.subheader(
        rag_observability_t(
            "source_status"
        )
    )

    first, second = st.columns(2)

    first.metric(
        rag_observability_t(
            "source_table"
        ),
        rag_observability_t(
            "source_value"
        ),
    )

    if error is not None:
        second.error(
            rag_observability_t(
                "source_error"
            )
        )

        with st.expander(
            rag_observability_t(
                "source_error"
            )
        ):
            st.code(error)

        return

    if has_data:
        second.success(
            rag_observability_t(
                "source_connected"
            )
        )
    else:
        second.info(
            rag_observability_t(
                "source_empty"
            )
        )


def _render_summary(
    frame: pd.DataFrame,
) -> None:
    summary = (
        build_rag_observability_summary(
            frame
        )
    )

    first, second, third = (
        st.columns(3)
    )

    first.metric(
        rag_observability_t(
            "questions"
        ),
        summary.total_questions,
    )

    second.metric(
        rag_observability_t(
            "gemini"
        ),
        _metric_value(
            summary.gemini_count
        ),
    )

    third.metric(
        rag_observability_t(
            "security"
        ),
        _metric_value(
            summary.security_count
        ),
    )

    fourth, fifth, sixth = (
        st.columns(3)
    )

    fourth.metric(
        rag_observability_t(
            "fallback"
        ),
        _metric_value(
            summary.fallback_count
        ),
    )

    fifth.metric(
        rag_observability_t(
            "average_latency"
        ),
        _metric_value(
            summary.average_latency_ms,
            suffix=" ms",
        ),
    )

    sixth.metric(
        rag_observability_t(
            "maximum_latency"
        ),
        _metric_value(
            summary.maximum_latency_ms,
            suffix=" ms",
        ),
    )


def _render_field_coverage(
    frame: pd.DataFrame,
) -> None:
    st.subheader(
        rag_observability_t(
            "field_coverage"
        )
    )

    st.caption(
        rag_observability_t(
            "field_coverage_caption"
        )
    )

    rows = []

    for item in build_field_coverage(
        frame
    ):
        rows.append(
            {
                "field": _field_label(
                    item["field"]
                ),
                "available_rows": (
                    item[
                        "available_rows"
                    ]
                ),
                "total_rows": (
                    item[
                        "total_rows"
                    ]
                ),
                "coverage_rate": (
                    item[
                        "coverage_rate"
                    ]
                ),
                "available": (
                    rag_observability_t(
                        "yes"
                    )
                    if item["available"]
                    else rag_observability_t(
                        "no"
                    )
                ),
            }
        )

    coverage_frame = pd.DataFrame(
        rows
    )

    st.dataframe(
        coverage_frame,
        width="stretch",
        hide_index=True,
        column_config={
            "field": (
                st.column_config.TextColumn(
                    rag_observability_t(
                        "field"
                    )
                )
            ),
            "available_rows": (
                st.column_config.NumberColumn(
                    rag_observability_t(
                        "available_rows"
                    ),
                    format="%d",
                )
            ),
            "total_rows": (
                st.column_config.NumberColumn(
                    rag_observability_t(
                        "total_rows"
                    ),
                    format="%d",
                )
            ),
            "coverage_rate": (
                st.column_config.ProgressColumn(
                    rag_observability_t(
                        "coverage"
                    ),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.0f%%",
                )
            ),
            "available": (
                st.column_config.TextColumn(
                    rag_observability_t(
                        "available"
                    )
                )
            ),
        },
    )


def _render_mode_distribution(
    frame: pd.DataFrame,
) -> None:
    st.subheader(
        rag_observability_t(
            "mode_distribution"
        )
    )

    st.caption(
        rag_observability_t(
            "mode_distribution_caption"
        )
    )

    distribution = (
        build_mode_distribution(
            frame
        )
    )

    if distribution.empty:
        st.info(
            rag_observability_t(
                "waiting_real_data"
            )
        )
        return

    distribution["mode"] = (
        distribution[
            "mode"
        ].replace(
            {
                "unregistered": (
                    rag_observability_t(
                        "unregistered"
                    )
                )
            }
        )
    )

    st.dataframe(
        distribution,
        width="stretch",
        hide_index=True,
        column_config={
            "mode": (
                st.column_config.TextColumn(
                    rag_observability_t(
                        "mode"
                    )
                )
            ),
            "total": (
                st.column_config.NumberColumn(
                    rag_observability_t(
                        "total"
                    ),
                    format="%d",
                )
            ),
        },
    )


def _render_latest_questions(
    frame: pd.DataFrame,
) -> None:
    st.subheader(
        rag_observability_t(
            "latest_questions"
        )
    )

    st.caption(
        rag_observability_t(
            "latest_questions_caption"
        )
    )

    latest = build_latest_questions(
        frame,
        limit=20,
    )

    if latest.empty:
        st.info(
            rag_observability_t(
                "waiting_real_data"
            )
        )
        return

    rename_map = {
        "pergunta": (
            rag_observability_t(
                "question"
            )
        ),
        "modo": (
            rag_observability_t(
                "mode"
            )
        ),
        "fontes": (
            rag_observability_t(
                "sources"
            )
        ),
        "data_hora": (
            rag_observability_t(
                "date"
            )
        ),
        "data": (
            rag_observability_t(
                "date"
            )
        ),
        "tempo_ms": (
            rag_observability_t(
                "latency"
            )
        ),
        "gemini": (
            rag_observability_t(
                "gemini"
            )
        ),
        "seguranca": (
            rag_observability_t(
                "security"
            )
        ),
        "fallback": (
            rag_observability_t(
                "fallback"
            )
        ),
    }

    latest = latest.rename(
        columns={
            key: value
            for key, value
            in rename_map.items()
            if key
            in latest.columns
        }
    )

    st.dataframe(
        latest,
        width="stretch",
        hide_index=True,
    )


def _render_export(
    frame: pd.DataFrame,
) -> None:
    st.subheader(
        rag_observability_t(
            "export"
        )
    )

    st.caption(
        rag_observability_t(
            "export_caption"
        )
    )

    if frame.empty:
        st.info(
            rag_observability_t(
                "export_unavailable"
            )
        )
        return

    st.download_button(
        label=rag_observability_t(
            "download_csv"
        ),
        data=(
            export_rag_observability_csv(
                frame
            )
        ),
        file_name=(
            "rag-observability-logs.csv"
        ),
        mime="text/csv",
        key=(
            "rag_observability_export_"
            f"{_language()}"
        ),
    )


def render_rag_observability_page(
    rag_df: pd.DataFrame | None = None,
) -> None:
    st.title(
        rag_observability_t(
            "title"
        )
    )

    st.subheader(
        rag_observability_t(
            "subtitle"
        )
    )

    st.info(
        rag_observability_t(
            "real_data_notice"
        )
    )

    error = None

    if rag_df is None:
        frame, error = (
            _load_rag_logs()
        )
    else:
        frame = rag_df.copy()

    summary = (
        build_rag_observability_summary(
            frame
        )
    )

    _render_source_status(
        error=error,
        has_data=summary.has_data,
    )

    st.divider()

    _render_summary(
        frame
    )

    if not summary.has_data:
        st.info(
            rag_observability_t(
                "no_logs"
            )
        )

    st.divider()

    _render_field_coverage(
        frame
    )

    st.divider()

    _render_mode_distribution(
        frame
    )

    st.divider()

    _render_latest_questions(
        frame
    )

    st.divider()

    _render_export(
        frame
    )

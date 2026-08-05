"""Dashboard Streamlit offline da avaliação Agentic RAG e MCP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.evaluation.offline_dashboard.data import (
    benchmark_profile_rows,
    build_overview,
    load_offline_dashboard_snapshot,
    mcp_scenario_rows,
    quality_gate_rows,
    report_status_rows,
    security_rows,
)


def _format_percentage(
    value: Any,
) -> str:
    try:
        numeric = float(value)
    except (
        TypeError,
        ValueError,
    ):
        numeric = 0.0

    return f"{numeric * 100:.1f}%"


def _format_number(
    value: Any,
    *,
    decimals: int = 3,
) -> str:
    try:
        numeric = float(value)
    except (
        TypeError,
        ValueError,
    ):
        numeric = 0.0

    return f"{numeric:.{decimals}f}"


def _render_overview(
    snapshot,
) -> None:
    overview = build_overview(
        snapshot
    )

    first_row = st.columns(4)

    first_row[0].metric(
        "Casos do dataset",
        overview["case_count"],
    )

    first_row[1].metric(
        "Categorias",
        overview["category_count"],
    )

    first_row[2].metric(
        "Quality Gate",
        (
            "APROVADO"
            if overview[
                "quality_gate_passed"
            ]
            else "REPROVADO"
        ),
    )

    first_row[3].metric(
        "Cenários MCP",
        overview["mcp_scenario_count"],
    )

    second_row = st.columns(4)

    second_row[0].metric(
        "Legacy — aprovação",
        _format_percentage(
            overview[
                "legacy_pass_rate"
            ]
        ),
    )

    second_row[1].metric(
        "Agentic — aprovação",
        _format_percentage(
            overview[
                "agentic_pass_rate"
            ]
        ),
    )

    second_row[2].metric(
        "Delta de score",
        _format_number(
            overview["score_delta"],
            decimals=6,
        ),
    )

    second_row[3].metric(
        "Delta de latência",
        (
            f"{overview['latency_delta_ms']:.1f} ms"
        ),
    )

    st.subheader(
        "Situação dos relatórios"
    )

    st.dataframe(
        report_status_rows(
            snapshot
        ),
        hide_index=True,
    )

    if snapshot.errors:
        st.warning(
            "\n".join(
                snapshot.errors
            )
        )


def _render_benchmark(
    snapshot,
) -> None:
    overview = build_overview(
        snapshot
    )

    st.subheader(
        "Legacy × Agentic"
    )

    st.dataframe(
        benchmark_profile_rows(
            snapshot
        ),
        hide_index=True,
    )

    columns = st.columns(4)

    columns[0].metric(
        "Melhorias",
        overview[
            "improvement_count"
        ],
    )

    columns[1].metric(
        "Regressões",
        overview[
            "regression_count"
        ],
    )

    columns[2].metric(
        "Score Agentic",
        _format_number(
            overview[
                "agentic_average_score"
            ]
        ),
    )

    columns[3].metric(
        "Score Legacy",
        _format_number(
            overview[
                "legacy_average_score"
            ]
        ),
    )

    with st.expander(
        "Relatório completo do benchmark"
    ):
        st.json(
            snapshot.benchmark
        )


def _render_quality_gate(
    snapshot,
) -> None:
    overview = build_overview(
        snapshot
    )

    if overview[
        "quality_gate_passed"
    ]:
        st.success(
            "Quality Gate offline aprovado."
        )
    else:
        st.error(
            "Quality Gate offline reprovado."
        )

    rows = quality_gate_rows(
        snapshot
    )

    st.metric(
        "Total de critérios",
        (
            len(rows)
            or overview[
                "quality_check_count"
            ]
        ),
    )

    st.dataframe(
        rows,
        hide_index=True,
    )

    with st.expander(
        "Relatório completo do Quality Gate"
    ):
        st.json(
            snapshot.quality_gate
        )


def _render_mcp(
    snapshot,
) -> None:
    rows = mcp_scenario_rows(
        snapshot
    )

    st.subheader(
        "MCP simulado ponta a ponta"
    )

    st.dataframe(
        rows,
        hide_index=True,
    )

    successful = sum(
        row["Status"] == "success"
        for row in rows
    )

    controlled = sum(
        row["Status"]
        in {
            "validation_error",
            "denied",
            "not_found",
            "error",
            "timeout",
        }
        for row in rows
    )

    columns = st.columns(3)

    columns[0].metric(
        "Cenários",
        len(rows),
    )

    columns[1].metric(
        "Sucessos funcionais",
        successful,
    )

    columns[2].metric(
        "Erros controlados",
        controlled,
    )

    st.caption(
        "Os erros controlados representam cenários "
        "intencionais de segurança, validação e timeout."
    )

    with st.expander(
        "Relatório MCP completo"
    ):
        st.json(
            snapshot.mcp_e2e
        )


def _render_security(
    snapshot,
) -> None:
    rows = security_rows(
        snapshot
    )

    approved = sum(
        row["Aprovado"]
        for row in rows
    )

    st.metric(
        "Controles offline aprovados",
        f"{approved}/{len(rows)}",
    )

    st.dataframe(
        rows,
        hide_index=True,
    )

    if approved == len(rows):
        st.success(
            "Nenhum serviço externo foi utilizado."
        )
    else:
        st.error(
            "Uma ou mais garantias offline não foram confirmadas."
        )

    st.subheader(
        "Contexto registrado"
    )

    st.code(
        "\n".join(
            (
                (
                    "user_id="
                    f"{snapshot.mcp_e2e.get('user_id', '')}"
                ),
                (
                    "session_id="
                    f"{snapshot.mcp_e2e.get('session_id', '')}"
                ),
                (
                    "loaded_at="
                    f"{snapshot.loaded_at}"
                ),
            )
        ),
        language="text",
    )


def main() -> None:
    """Renderiza o dashboard."""

    st.set_page_config(
        page_title=(
            "INNA — Avaliação Offline"
        ),
        page_icon="📊",
        layout="wide",
    )

    project_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    st.title(
        "📊 INNA — Avaliação Offline"
    )

    st.caption(
        "Benchmark Agentic RAG, Quality Gate "
        "e MCP simulado sem APIs ou quota."
    )

    with st.sidebar:
        st.header(
            "Execução"
        )

        st.code(
            str(project_root),
            language="text",
        )

        st.info(
            "Este painel lê somente arquivos JSON locais."
        )

        if st.button(
            "Recarregar relatórios"
        ):
            st.rerun()

    snapshot = (
        load_offline_dashboard_snapshot(
            project_root,
            strict=False,
        )
    )

    tabs = st.tabs(
        (
            "Visão geral",
            "Benchmark",
            "Quality Gate",
            "MCP E2E",
            "Segurança",
        )
    )

    with tabs[0]:
        _render_overview(
            snapshot
        )

    with tabs[1]:
        _render_benchmark(
            snapshot
        )

    with tabs[2]:
        _render_quality_gate(
            snapshot
        )

    with tabs[3]:
        _render_mcp(
            snapshot
        )

    with tabs[4]:
        _render_security(
            snapshot
        )


if __name__ == "__main__":
    main()

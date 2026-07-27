from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.evaluation.dashboard_data import (
    build_dashboard_summary,
    build_metric_series,
    build_metric_snapshot,
    build_pass_rate_series,
    build_runs_table,
    filter_history,
    get_metric_ids,
    load_dashboard_history,
)

DEFAULT_HISTORY_PATH = Path(
    "evaluation/history/evaluation-history.json"
)


def _percentage(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.2%}"


def _render_header() -> None:
    st.title("INNA LLMOps Observability")

    st.caption(
        "Monitoramento de qualidade, regressões, "
        "baselines e tendências das avaliações "
        "de Inteligência Artificial."
    )


def _render_sidebar(
    history,
):
    st.sidebar.header("Filtros")

    available_branches = sorted(
        {
            entry.branch
            for entry in history.entries
        }
    )

    available_environments = sorted(
        {
            entry.environment
            for entry in history.entries
        }
    )

    branches = st.sidebar.multiselect(
        "Branches",
        available_branches,
        default=available_branches,
    )

    environments = st.sidebar.multiselect(
        "Ambientes",
        available_environments,
        default=available_environments,
    )

    status_option = st.sidebar.selectbox(
        "Status da execução",
        (
            "Todas",
            "Aprovadas",
            "Reprovadas",
        ),
    )

    passed_filter = {
        "Todas": None,
        "Aprovadas": True,
        "Reprovadas": False,
    }[status_option]

    selected_branches = (
        set(branches)
        if branches
        else set()
    )

    selected_environments = (
        set(environments)
        if environments
        else set()
    )

    return filter_history(
        history,
        branches=selected_branches,
        environments=selected_environments,
        passed=passed_filter,
    )


def _render_summary(history) -> None:
    summary = build_dashboard_summary(
        history
    )

    first, second, third, fourth = (
        st.columns(4)
    )

    first.metric(
        "Execuções",
        summary.total_runs,
    )

    second.metric(
        "Taxa de aprovação",
        _percentage(
            summary.approval_rate
        ),
    )

    third.metric(
        "Pass rate mais recente",
        _percentage(
            summary.latest_pass_rate
        ),
    )

    fourth.metric(
        "Métricas monitoradas",
        summary.tracked_metrics,
    )

    fifth, sixth, seventh, eighth = (
        st.columns(4)
    )

    fifth.metric(
        "Execuções aprovadas",
        summary.approved_runs,
    )

    sixth.metric(
        "Execuções reprovadas",
        summary.failed_runs,
    )

    seventh.metric(
        "Regressões recentes",
        summary.latest_regressions,
    )

    eighth.metric(
        "Violações recentes",
        summary.latest_violations,
    )

    if (
        summary.latest_quality_gate_passed
        is True
    ):
        st.success(
            "Quality Gate mais recente: aprovado."
        )
    elif (
        summary.latest_quality_gate_passed
        is False
    ):
        st.error(
            "Quality Gate mais recente: reprovado."
        )
    else:
        st.info(
            "Nenhuma execução disponível."
        )


def _render_pass_rate_chart(history) -> None:
    st.subheader(
        "Evolução da taxa de aprovação"
    )

    rows = build_pass_rate_series(history)

    if not rows:
        st.info(
            "Não há execuções para exibir."
        )
        return

    frame = pd.DataFrame(rows)

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
    )

    chart_data = (
        frame[
            [
                "recorded_at",
                "pass_rate",
            ]
        ]
        .set_index("recorded_at")
        .sort_index()
    )

    st.line_chart(
        chart_data,
        y="pass_rate",
    )


def _render_metric_chart(history) -> None:
    st.subheader(
        "Tendência das métricas"
    )

    available_metrics = get_metric_ids(
        history
    )

    if not available_metrics:
        st.info(
            "Não há métricas disponíveis."
        )
        return

    selected_metrics = st.multiselect(
        "Métricas exibidas",
        available_metrics,
        default=list(
            available_metrics[:5]
        ),
    )

    if not selected_metrics:
        st.warning(
            "Selecione pelo menos uma métrica."
        )
        return

    rows = build_metric_series(
        history,
        metric_ids=set(selected_metrics),
    )

    frame = pd.DataFrame(rows)

    if frame.empty:
        st.info(
            "Nenhum dado encontrado para as "
            "métricas selecionadas."
        )
        return

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
    )

    pivot = frame.pivot_table(
        index="recorded_at",
        columns="metric_id",
        values="average_score",
        aggfunc="last",
    ).sort_index()

    st.line_chart(pivot)


def _render_latest_snapshot(history) -> None:
    st.subheader(
        "Snapshot da execução mais recente"
    )

    latest = history.latest()

    if latest is None:
        st.info(
            "Nenhuma execução registrada."
        )
        return

    st.write(
        {
            "run_reference": (
                latest.run_reference
            ),
            "branch": latest.branch,
            "commit_sha": latest.commit_sha,
            "environment": latest.environment,
            "evaluation_mode": (
                latest.evaluation_mode
            ),
            "baseline_id": latest.baseline_id,
            "recorded_at": latest.recorded_at,
        }
    )

    snapshot = build_metric_snapshot(
        latest
    )

    if snapshot:
        frame = pd.DataFrame(snapshot)

        st.dataframe(
            frame,
            width="stretch",
            hide_index=True,
        )


def _render_runs_table(history) -> None:
    st.subheader(
        "Histórico de execuções"
    )

    rows = build_runs_table(history)

    if not rows:
        st.info(
            "Nenhuma execução encontrada "
            "para os filtros selecionados."
        )
        return

    frame = pd.DataFrame(rows)

    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "pass_rate": (
                st.column_config.ProgressColumn(
                    "Pass rate",
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "passed": (
                st.column_config.CheckboxColumn(
                    "Aprovada"
                )
            ),
            "quality_gate_passed": (
                st.column_config.CheckboxColumn(
                    "Quality Gate"
                )
            ),
        },
    )


def main() -> None:
    st.set_page_config(
        page_title="INNA LLMOps",
        page_icon="📊",
        layout="wide",
    )

    _render_header()

    history_path = st.sidebar.text_input(
        "Arquivo de histórico",
        str(DEFAULT_HISTORY_PATH),
    )

    try:
        history = load_dashboard_history(
            history_path
        )
    except Exception as exc:
        st.error(
            "Não foi possível carregar o "
            f"histórico: {exc}"
        )
        st.stop()

    filtered_history = _render_sidebar(
        history
    )

    _render_summary(filtered_history)

    st.divider()

    _render_pass_rate_chart(
        filtered_history
    )

    _render_metric_chart(
        filtered_history
    )

    st.divider()

    _render_latest_snapshot(
        filtered_history
    )

    _render_runs_table(
        filtered_history
    )


if __name__ == "__main__":
    main()

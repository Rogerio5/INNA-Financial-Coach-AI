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
from src.observability.infrastructure_health import (
    collect_infrastructure_health,
)
from src.observability.phoenix_runtime import (
    initialize_phoenix,
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


def _render_infrastructure_status() -> None:
    """
    Exibe saúde operacional sem revelar credenciais,
    URLs privadas ou identificadores brutos.
    """

    try:
        initialize_phoenix()
        health = collect_infrastructure_health()
    except Exception as exc:
        st.warning(
            "Não foi possível coletar o status da "
            "infraestrutura neste momento."
        )

        with st.expander(
            "Detalhes técnicos",
            expanded=False,
        ):
            st.code(type(exc).__name__)

        return

    st.subheader("Infraestrutura e observabilidade")

    status_labels = {
        "operational": "Operacional",
        "degraded": "Degradada",
        "unavailable": "Indisponível",
    }

    status_label = status_labels.get(
        health.status,
        health.status,
    )

    if health.status == "operational":
        st.success(
            f"Status geral: {status_label}"
        )
    elif health.status == "degraded":
        st.warning(
            f"Status geral: {status_label}"
        )
    else:
        st.error(
            f"Status geral: {status_label}"
        )

    neon_column, phoenix_column, render_column = (
        st.columns(3)
    )

    with neon_column:
        st.metric(
            "Neon PostgreSQL",
            (
                "Disponível"
                if health.neon.available
                else "Indisponível"
            ),
            (
                f"{health.neon.latency_ms:.0f} ms"
                if health.neon.latency_ms is not None
                else "sem medição"
            ),
        )

        st.caption(
            f"Pool: {health.neon.pool_status}"
        )

    with phoenix_column:
        st.metric(
            "Phoenix",
            (
                "Ativo"
                if health.phoenix.ready
                else "Inativo"
            ),
            (
                f"Sample {health.phoenix.sample_rate:.0%}"
            ),
        )

        st.caption(
            f"Projeto: "
            f"{health.phoenix.project_name}"
        )

    with render_column:
        st.metric(
            "Execução",
            (
                "Render"
                if health.render.running_on_render
                else "Local"
            ),
            health.render.environment,
        )

        st.caption(
            f"Serviço: {health.render.service_name}"
        )

    with st.expander(
        "Detalhes técnicos da infraestrutura",
        expanded=False,
    ):
        detail_column_1, detail_column_2 = (
            st.columns(2)
        )

        with detail_column_1:
            st.write(
                "**Neon**"
            )
            st.write(
                f"PostgreSQL: "
                f"{health.neon.server_version or '—'}"
            )
            st.write(
                f"Tamanho do pool: "
                f"{health.neon.pool_size}"
            )
            st.write(
                f"Conexões disponíveis: "
                f"{health.neon.pool_available}"
            )
            st.write(
                f"Requisições aguardando: "
                f"{health.neon.pool_waiting}"
            )

        with detail_column_2:
            st.write(
                "**Aplicação e tracing**"
            )
            st.write(
                f"Ambiente: "
                f"{health.render.environment}"
            )
            st.write(
                f"Região: {health.render.region}"
            )
            st.write(
                f"Phoenix processor: "
                f"{health.phoenix.processor}"
            )
            st.write(
                f"Captura de conteúdo: "
                f"{health.phoenix.capture_content}"
            )

        if health.unavailable_components:
            st.error(
                "Componentes indisponíveis: "
                + ", ".join(
                    health.unavailable_components
                )
            )

        if health.degraded_components:
            st.warning(
                "Componentes degradados: "
                + ", ".join(
                    health.degraded_components
                )
            )


def _render_filters(
    history,
    controls,
):
    controls.header("Filtros")

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

    branches = controls.multiselect(
        "Branches",
        available_branches,
        default=available_branches,
    )

    environments = controls.multiselect(
        "Ambientes",
        available_environments,
        default=available_environments,
    )

    status_option = controls.selectbox(
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


def render_llmops_dashboard(
    *,
    integrated: bool = False,
) -> None:
    """
    Renderiza o painel LLMOps.

    integrated=False:
        execução Streamlit independente.

    integrated=True:
        execução incorporada ao dashboard
        administrativo principal da INNA.
    """
    _render_header()
    _render_infrastructure_status()

    st.divider()

    if integrated:
        controls = st.expander(
            "Filtros LLMOps",
            expanded=False,
        )
        history_key = (
            "llmops_integrated_history_path"
        )
    else:
        controls = st.sidebar
        history_key = (
            "llmops_standalone_history_path"
        )

    history_path = controls.text_input(
        "Arquivo de histórico",
        str(DEFAULT_HISTORY_PATH),
        key=history_key,
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
        return

    filtered_history = _render_filters(
        history,
        controls,
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


def main() -> None:
    st.set_page_config(
        page_title="INNA LLMOps",
        page_icon="📊",
        layout="wide",
    )

    render_llmops_dashboard(
        integrated=False
    )


if __name__ == "__main__":
    main()

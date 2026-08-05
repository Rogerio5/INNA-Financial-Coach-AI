from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard_pages.rag_evaluation_lab_core_i18n import (
    RAG_LAB_CORE_TEXTS,
)
from src.dashboard_pages.rag_evaluation_lab_i18n import (
    RAG_LAB_ADVANCED_TEXTS,
)
from src.dashboard_pages.technical_labels_i18n import (
    technical_label,
)
from src.evaluation.dashboard import (
    DEFAULT_HISTORY_PATH,
    aplicar_tema_llmops_chart,
)
from src.evaluation.dashboard_data import (
    load_dashboard_history,
)
from src.evaluation.rag_lab_advanced import (
    QualityGateThresholds,
    RagLabCapabilityStatus,
    build_rag_lab_capabilities,
    calculate_cost_per_approved_run,
    evaluate_quality_gate,
    export_rag_lab_history_csv,
    export_rag_lab_report_json,
    rank_rag_lab_runs,
)
from src.evaluation.rag_lab_comparison import (
    RagLabComparisonStatus,
)
from src.evaluation.rag_lab_dashboard_data import (
    build_rag_lab_comparison_rows,
    build_rag_lab_run_options,
    build_rag_lab_summary,
    build_rag_lab_timeline,
    build_selected_comparison,
    get_rag_lab_entries,
    select_default_comparison,
)
from src.evaluation.rag_lab_experiment_metadata import (
    build_experiment_metadata_readiness,
    build_experiment_metadata_snapshot,
)

RAG_LAB_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "title": "🧪 Laboratório de Qualidade RAG",
        "subtitle": (
            "Avaliação, experimentação e comparação profissional da RAG Triad."
        ),
        "description": (
            "Compare execuções reais usando Answer Relevancy, "
            "Faithfulness e Contextual Relevancy."
        ),
        "history_settings": "Fonte de dados",
        "history_file": "Arquivo de histórico",
        "load_error": "Não foi possível carregar o histórico",
        "filters": "Filtros do laboratório",
        "branches": "Branches",
        "environments": "Ambientes",
        "status": "Status",
        "all_statuses": "Todos",
        "approved": "Aprovadas",
        "failed": "Reprovadas",
        "partial": "Parciais ou indisponíveis",
        "runs": "Execuções RAG Triad",
        "comparable_runs": "Execuções comparáveis",
        "approval_rate": "Taxa de aprovação",
        "latest_score": "Score mais recente",
        "best_score": "Melhor score",
        "incomplete_runs": "Execuções incompletas",
        "no_history": (
            "Nenhuma execução da RAG Triad foi encontrada para os filtros selecionados."
        ),
        "timeline": "Evolução da qualidade RAG",
        "timeline_caption": ("Histórico dos três eixos e do score agregado."),
        "comparison": "Comparação de experimentos",
        "comparison_caption": (
            "Selecione uma execução de referência e uma execução candidata."
        ),
        "baseline": "Baseline",
        "candidate": "Candidata",
        "tolerance": "Tolerância de estabilidade",
        "tolerance_help": (
            "Diferenças dentro da tolerância são classificadas como estáveis."
        ),
        "need_two_runs": (
            "São necessárias pelo menos duas execuções completas "
            "para realizar uma comparação."
        ),
        "same_run": ("A baseline e a candidata precisam ser diferentes."),
        "comparison_unavailable": (
            "A comparação não pôde ser construída com as execuções selecionadas."
        ),
        "aggregate_result": "Resultado agregado",
        "baseline_score": "Score da baseline",
        "candidate_score": "Score da candidata",
        "delta": "Diferença",
        "classification": "Classificação",
        "improved": "Melhoria",
        "stable": "Estável",
        "regressed": "Regressão",
        "unavailable": "Indisponível",
        "candidate_approved": "Candidata aprovada",
        "candidate_failed": "Candidata reprovada",
        "candidate_unknown": ("A candidata ainda não possui aprovação conclusiva."),
        "axis_comparison": "Comparação por eixo",
        "comparison_chart": "Baseline × candidata",
        "history_table": "Histórico de execuções",
        "run_reference": "Execução",
        "recorded_at": "Data",
        "branch": "Branch",
        "environment": "Ambiente",
        "triad_score": "Score RAG Triad",
        "triad_status": "Status RAG Triad",
        "triad_passed": "Aprovada",
        "complete": "Completa",
        "metric": "Métrica",
        "score": "Score",
        "answer_relevancy": "Answer Relevancy",
        "faithfulness": "Faithfulness",
        "contextual_relevancy": "Contextual Relevancy",
        "rag_triad_average": "Média RAG Triad",
        "latest_run": "Última execução",
        "best_run": "Melhor execução",
        "status_passed": "Aprovada",
        "status_failed": "Reprovada",
        "status_partial": "Parcial",
        "status_unavailable": "Indisponível",
    },
    "en_us": {
        "title": "🧪 RAG Quality Laboratory",
        "subtitle": (
            "Professional RAG Triad evaluation, experimentation and comparison."
        ),
        "description": (
            "Compare real runs using Answer Relevancy, "
            "Faithfulness and Contextual Relevancy."
        ),
        "history_settings": "Data source",
        "history_file": "History file",
        "load_error": "Unable to load evaluation history",
        "filters": "Laboratory filters",
        "branches": "Branches",
        "environments": "Environments",
        "status": "Status",
        "all_statuses": "All",
        "approved": "Approved",
        "failed": "Failed",
        "partial": "Partial or unavailable",
        "runs": "RAG Triad runs",
        "comparable_runs": "Comparable runs",
        "approval_rate": "Approval rate",
        "latest_score": "Latest score",
        "best_score": "Best score",
        "incomplete_runs": "Incomplete runs",
        "no_history": ("No RAG Triad run was found for the selected filters."),
        "timeline": "RAG quality evolution",
        "timeline_caption": ("History of the three axes and aggregate score."),
        "comparison": "Experiment comparison",
        "comparison_caption": ("Select a reference run and a candidate run."),
        "baseline": "Baseline",
        "candidate": "Candidate",
        "tolerance": "Stability tolerance",
        "tolerance_help": (
            "Differences within the tolerance are classified as stable."
        ),
        "need_two_runs": ("At least two complete runs are required for comparison."),
        "same_run": ("Baseline and candidate must be different."),
        "comparison_unavailable": (
            "The comparison could not be built with the selected runs."
        ),
        "aggregate_result": "Aggregate result",
        "baseline_score": "Baseline score",
        "candidate_score": "Candidate score",
        "delta": "Difference",
        "classification": "Classification",
        "improved": "Improved",
        "stable": "Stable",
        "regressed": "Regressed",
        "unavailable": "Unavailable",
        "candidate_approved": "Candidate approved",
        "candidate_failed": "Candidate failed",
        "candidate_unknown": ("The candidate does not have a conclusive result."),
        "axis_comparison": "Axis comparison",
        "comparison_chart": "Baseline × candidate",
        "history_table": "Run history",
        "run_reference": "Run",
        "recorded_at": "Date",
        "branch": "Branch",
        "environment": "Environment",
        "triad_score": "RAG Triad score",
        "triad_status": "RAG Triad status",
        "triad_passed": "Approved",
        "complete": "Complete",
        "metric": "Metric",
        "score": "Score",
        "answer_relevancy": "Answer Relevancy",
        "faithfulness": "Faithfulness",
        "contextual_relevancy": "Contextual Relevancy",
        "rag_triad_average": "RAG Triad average",
        "latest_run": "Latest run",
        "best_run": "Best run",
        "status_passed": "Approved",
        "status_failed": "Failed",
        "status_partial": "Partial",
        "status_unavailable": "Unavailable",
    },
    "es": {
        "title": "🧪 Laboratorio de Calidad RAG",
        "subtitle": (
            "Evaluación, experimentación y comparación profesional de la Tríada RAG."
        ),
        "description": (
            "Compare ejecuciones reales usando Answer Relevancy, "
            "Faithfulness y Contextual Relevancy."
        ),
    },
}


for language_code, core_texts in RAG_LAB_CORE_TEXTS.items():
    language_texts = RAG_LAB_TEXTS.setdefault(
        language_code,
        {},
    )
    language_texts.update(core_texts)


for language_code, advanced_texts in RAG_LAB_ADVANCED_TEXTS.items():
    language_texts = RAG_LAB_TEXTS.setdefault(
        language_code,
        {},
    )
    language_texts.update(advanced_texts)


RAG_LAB_METRIC_LABELS = {
    "answer-relevancy": "answer_relevancy",
    "faithfulness": "faithfulness",
    "contextual-relevancy": ("contextual_relevancy"),
    "rag-triad-average": "rag_triad_average",
}


RAG_LAB_STATUS_LABELS = {
    RagLabComparisonStatus.IMPROVED: "improved",
    RagLabComparisonStatus.STABLE: "stable",
    RagLabComparisonStatus.REGRESSED: "regressed",
    RagLabComparisonStatus.UNAVAILABLE: ("unavailable"),
}


def _rag_lab_language() -> str:
    language = str(
        st.session_state.get(
            "dashboard_interface_lang",
            "pt",
        )
        or "pt"
    )

    return language


def rag_lab_t(
    key: str,
    default: str | None = None,
) -> str:
    language = _rag_lab_language()

    technical_keys = {
        "quality_gate": "quality_gate",
        "quality_gate_title": "quality_gate",
        "reranker": "reranker",
        "reranker_label": "reranker",
        "embedding": "embedding",
        "embedding_label": "embedding",
        "latency": "latency",
        "latency_label": "latency",
        "tokens": "tokens",
        "token": "token",
        "retrieval": "retrieval",
        "retrieval_label": "retrieval",
        "hybrid": "hybrid",
        "hybrid_search": "hybrid",
    }

    technical_key = technical_keys.get(key)

    if technical_key is not None:
        return technical_label(
            language,
            technical_key,
        )

    native_texts = RAG_LAB_TEXTS.get(
        language,
        {},
    )

    if key in native_texts:
        return native_texts[key]

    english_texts = RAG_LAB_TEXTS["en_us"]

    if key in english_texts:
        return english_texts[key]

    portuguese_texts = RAG_LAB_TEXTS["pt"]

    return portuguese_texts.get(
        key,
        default or key,
    )


def _percentage(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.2%}"


def _delta_percentage(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:+.2%}"


def _metric_label(
    metric_id: str,
) -> str:
    translation_key = RAG_LAB_METRIC_LABELS.get(
        metric_id,
    )

    if translation_key is None:
        return metric_id

    return rag_lab_t(
        translation_key,
        metric_id,
    )


def _status_label(
    status: RagLabComparisonStatus,
) -> str:
    translation_key = RAG_LAB_STATUS_LABELS[status]

    return rag_lab_t(
        translation_key,
        status.value,
    )


def _filter_history(
    history: Any,
    *,
    branches: set[str],
    environments: set[str],
    status_filter: str,
) -> Any:
    selected_entries = []

    for entry in get_rag_lab_entries(history):
        branch = str(
            getattr(
                entry,
                "branch",
                "",
            )
        )

        environment = str(
            getattr(
                entry,
                "environment",
                "",
            )
        )

        triad = getattr(
            entry,
            "rag_triad",
            None,
        )

        passed = (
            getattr(
                triad,
                "passed",
                None,
            )
            if triad is not None
            else None
        )

        if branches and branch not in branches:
            continue

        if environments and environment not in environments:
            continue

        if status_filter == "approved" and passed is not True:
            continue

        if status_filter == "failed" and passed is not False:
            continue

        if status_filter == "partial" and passed is not None:
            continue

        selected_entries.append(entry)

    return SimpleNamespace(
        entries=tuple(selected_entries),
    )


def _render_header() -> None:
    st.title(rag_lab_t("title"))

    st.subheader(rag_lab_t("subtitle"))

    st.info(rag_lab_t("description"))


def _render_filters(
    history: Any,
) -> Any:
    entries = get_rag_lab_entries(history)

    available_branches = sorted(
        {
            str(
                getattr(
                    entry,
                    "branch",
                    "",
                )
            )
            for entry in entries
        }
    )

    available_environments = sorted(
        {
            str(
                getattr(
                    entry,
                    "environment",
                    "",
                )
            )
            for entry in entries
        }
    )

    with st.expander(
        rag_lab_t("filters"),
        expanded=False,
    ):
        branch_column, environment_column = st.columns(2)

        with branch_column:
            if available_branches:
                selected_branches = st.multiselect(
                    rag_lab_t("branches"),
                    available_branches,
                    default=available_branches,
                    key=(f"rag_lab_filter_branches_{_rag_lab_language()}"),
                )
            else:
                st.info(rag_lab_t("no_branch_options"))
                selected_branches = []

        with environment_column:
            if available_environments:
                selected_environments = st.multiselect(
                    rag_lab_t("environments"),
                    available_environments,
                    default=available_environments,
                    key=(f"rag_lab_filter_environments_{_rag_lab_language()}"),
                )
            else:
                st.info(rag_lab_t("no_environment_options"))
                selected_environments = []

        status_options = (
            "all",
            "approved",
            "failed",
            "partial",
        )

        status_labels = {
            "all": rag_lab_t("all_statuses"),
            "approved": rag_lab_t("approved"),
            "failed": rag_lab_t("failed"),
            "partial": rag_lab_t("partial"),
        }

        status_filter = st.selectbox(
            rag_lab_t("status"),
            status_options,
            format_func=lambda value: status_labels[value],
            key=(f"rag_lab_filter_status_{_rag_lab_language()}"),
        )

    return _filter_history(
        history,
        branches=set(selected_branches),
        environments=set(selected_environments),
        status_filter=status_filter,
    )


def _render_summary(
    history: Any,
) -> None:
    summary = build_rag_lab_summary(history)

    first, second, third, fourth = st.columns(4)

    first.metric(
        rag_lab_t("runs"),
        summary.comparable_runs,
    )

    second.metric(
        rag_lab_t("approval_rate"),
        _percentage(summary.approval_rate),
    )

    third.metric(
        rag_lab_t("latest_score"),
        _percentage(summary.latest_score),
    )

    fourth.metric(
        rag_lab_t("best_score"),
        _percentage(summary.best_score),
    )

    fifth, sixth, seventh = st.columns(3)

    fifth.metric(
        rag_lab_t("incomplete_runs"),
        summary.incomplete_runs,
    )

    sixth.metric(
        rag_lab_t("latest_run"),
        summary.latest_reference or "—",
    )

    seventh.metric(
        rag_lab_t("best_run"),
        summary.best_reference or "—",
    )


def _render_timeline(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("timeline"))

    st.caption(rag_lab_t("timeline_caption"))

    rows = build_rag_lab_timeline(history)

    if not rows:
        st.info(rag_lab_t("no_history"))
        return

    frame = pd.DataFrame(rows)

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
        errors="coerce",
    )

    metric_columns = [
        "rag_triad_score",
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    ]

    available_columns = [
        column
        for column in metric_columns
        if (column in frame.columns and frame[column].notna().any())
    ]

    if not available_columns:
        st.info(rag_lab_t("no_history"))
        return

    chart_frame = frame[
        [
            "recorded_at",
            *available_columns,
        ]
    ].melt(
        id_vars=["recorded_at"],
        var_name="metric_id",
        value_name="score",
    )

    chart_frame = chart_frame.dropna(
        subset=[
            "recorded_at",
            "score",
        ]
    )

    chart_frame["metric_label"] = chart_frame["metric_id"].map(
        lambda metric_id: _metric_label(
            "rag-triad-average" if metric_id == "rag_triad_score" else metric_id
        )
    )

    figure = px.line(
        chart_frame.sort_values("recorded_at"),
        x="recorded_at",
        y="score",
        color="metric_label",
        markers=True,
        labels={
            "recorded_at": (rag_lab_t("recorded_at")),
            "score": rag_lab_t("score"),
            "metric_label": (rag_lab_t("metric")),
        },
    )

    figure.update_traces(
        line={"width": 2.7},
        marker={"size": 8},
        connectgaps=False,
        hovertemplate=(
            "<b>%{x|%d/%m/%Y %H:%M}</b><br>%{fullData.name}: %{y:.2%}<extra></extra>"
        ),
    )

    figure.update_layout(
        xaxis_title=None,
        yaxis_title=rag_lab_t("score"),
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.20,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    figure.update_xaxes(
        tickformat="%d/%m<br>%H:%M",
    )

    figure.update_yaxes(
        range=[0, 1],
        tickformat=".0%",
    )

    aplicar_tema_llmops_chart(
        figure,
        height=520,
    )

    st.plotly_chart(
        figure,
        width="stretch",
        key="rag_lab_timeline_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


def _render_comparison_status(
    comparison: Any,
) -> None:
    if comparison.status == RagLabComparisonStatus.IMPROVED:
        st.success("✅ " + rag_lab_t("improved"))
    elif comparison.status == RagLabComparisonStatus.REGRESSED:
        st.error("⚠️ " + rag_lab_t("regressed"))
    elif comparison.status == RagLabComparisonStatus.STABLE:
        st.info("➖ " + rag_lab_t("stable"))
    else:
        st.warning(rag_lab_t("unavailable"))

    if comparison.candidate_passed is True:
        st.success(rag_lab_t("candidate_approved"))
    elif comparison.candidate_passed is False:
        st.error(rag_lab_t("candidate_failed"))
    else:
        st.warning(rag_lab_t("candidate_unknown"))


def _render_comparison_chart(
    comparison: Any,
) -> None:
    rows = build_rag_lab_comparison_rows(comparison)

    frame = pd.DataFrame(rows)

    frame["metric_label"] = frame["metric_id"].map(_metric_label)

    chart_frame = frame.melt(
        id_vars=["metric_label"],
        value_vars=[
            "baseline_score",
            "candidate_score",
        ],
        var_name="run_type",
        value_name="score",
    )

    run_labels = {
        "baseline_score": (rag_lab_t("baseline")),
        "candidate_score": (rag_lab_t("candidate")),
    }

    chart_frame["run_label"] = chart_frame["run_type"].map(run_labels)

    figure = px.bar(
        chart_frame,
        x="metric_label",
        y="score",
        color="run_label",
        barmode="group",
        labels={
            "metric_label": (rag_lab_t("metric")),
            "score": rag_lab_t("score"),
            "run_label": "",
        },
    )

    figure.update_traces(
        hovertemplate=("<b>%{x}</b><br>%{fullData.name}: %{y:.2%}<extra></extra>"),
    )

    figure.update_layout(
        xaxis_title=None,
        yaxis_title=rag_lab_t("score"),
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    figure.update_yaxes(
        range=[0, 1],
        tickformat=".0%",
    )

    aplicar_tema_llmops_chart(
        figure,
        height=500,
    )

    st.plotly_chart(
        figure,
        width="stretch",
        key="rag_lab_comparison_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


def _render_axis_table(
    comparison: Any,
) -> None:
    rows = build_rag_lab_comparison_rows(comparison)

    frame = pd.DataFrame(rows)

    frame["metric_id"] = frame["metric_id"].map(_metric_label)

    frame["status"] = frame["status"].map(
        lambda value: rag_lab_t(
            value,
            value,
        )
    )

    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "metric_id": (st.column_config.TextColumn(rag_lab_t("metric"))),
            "baseline_score": (
                st.column_config.ProgressColumn(
                    rag_lab_t("baseline_score"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "candidate_score": (
                st.column_config.ProgressColumn(
                    rag_lab_t("candidate_score"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "delta": (
                st.column_config.NumberColumn(
                    rag_lab_t("delta"),
                    format="%+.4f",
                )
            ),
            "status": (st.column_config.TextColumn(rag_lab_t("classification"))),
        },
    )


def _render_comparison(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("comparison"))

    st.caption(rag_lab_t("comparison_caption"))

    options = build_rag_lab_run_options(
        history,
        complete_only=True,
    )

    if len(options) < 2:
        st.warning(rag_lab_t("need_two_runs"))
        return

    default_pair = select_default_comparison(history)

    if default_pair is None:
        st.warning(rag_lab_t("need_two_runs"))
        return

    default_baseline, default_candidate = default_pair

    references = [option.run_reference for option in options]

    option_labels = {option.run_reference: option.label for option in options}

    baseline_default_index = (
        references.index(default_baseline.run_reference)
        if (default_baseline.run_reference in references)
        else 1
    )

    candidate_default_index = (
        references.index(default_candidate.run_reference)
        if (default_candidate.run_reference in references)
        else 0
    )

    baseline_column, candidate_column = st.columns(2)

    with baseline_column:
        baseline_reference = st.selectbox(
            rag_lab_t("baseline"),
            references,
            index=baseline_default_index,
            format_func=lambda value: option_labels[value],
            key=(f"rag_lab_baseline_reference_{_rag_lab_language()}"),
        )

    with candidate_column:
        candidate_reference = st.selectbox(
            rag_lab_t("candidate"),
            references,
            index=candidate_default_index,
            format_func=lambda value: option_labels[value],
            key=(f"rag_lab_candidate_reference_{_rag_lab_language()}"),
        )

    tolerance = st.slider(
        rag_lab_t("tolerance"),
        min_value=0.0,
        max_value=0.05,
        value=0.005,
        step=0.001,
        format="%.3f",
        help=rag_lab_t("tolerance_help"),
        key="rag_lab_comparison_tolerance",
    )

    if baseline_reference == candidate_reference:
        st.warning(rag_lab_t("same_run"))
        return

    comparison = build_selected_comparison(
        history,
        baseline_reference=(baseline_reference),
        candidate_reference=(candidate_reference),
        tolerance=tolerance,
    )

    if comparison is None:
        st.warning(rag_lab_t("comparison_unavailable"))
        return

    st.markdown(f"### {rag_lab_t('aggregate_result')}")

    first, second, third, fourth = st.columns(4)

    first.metric(
        rag_lab_t("baseline_score"),
        _percentage(comparison.baseline_score),
    )

    second.metric(
        rag_lab_t("candidate_score"),
        _percentage(comparison.candidate_score),
    )

    third.metric(
        rag_lab_t("delta"),
        _delta_percentage(comparison.delta),
    )

    fourth.metric(
        rag_lab_t("classification"),
        _status_label(comparison.status),
    )

    _render_comparison_status(comparison)

    st.markdown(f"### {rag_lab_t('comparison_chart')}")

    _render_comparison_chart(comparison)

    st.markdown(f"### {rag_lab_t('axis_comparison')}")

    _render_axis_table(comparison)


def _metadata_field_label(
    field_key: str,
    fallback: str,
) -> str:
    return rag_lab_t(
        f"field_{field_key}",
        fallback,
    )


def _availability_label(
    status: Any,
) -> str:
    value = str(
        getattr(
            status,
            "value",
            status,
        )
    )

    labels = {
        "available": rag_lab_t("available"),
        "partial": rag_lab_t("partially_available"),
        "unavailable": rag_lab_t("waiting_real_data"),
        "active": rag_lab_t("available"),
        "waiting_data": rag_lab_t("waiting_real_data"),
    }

    return labels.get(
        value,
        value,
    )


def _find_entry_by_reference(
    history: Any,
    run_reference: str,
) -> Any | None:
    for entry in getattr(
        history,
        "entries",
        (),
    ):
        if (
            str(
                getattr(
                    entry,
                    "run_reference",
                    "",
                )
            )
            == run_reference
        ):
            return entry

    return None


def _render_metadata_coverage(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("metadata_coverage"))

    st.caption(rag_lab_t("metadata_coverage_caption"))

    readiness = build_experiment_metadata_readiness(history)

    rows = []

    for item in readiness:
        values = ", ".join(item.distinct_values)

        rows.append(
            {
                "field": (
                    _metadata_field_label(
                        item.key,
                        item.label,
                    )
                ),
                "availability": (_availability_label(item.availability)),
                "coverage": (item.coverage_rate),
                "registered_runs": (f"{item.available_runs}/{item.total_runs}"),
                "distinct_values": (values or rag_lab_t("waiting_real_data")),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "field": (st.column_config.TextColumn(rag_lab_t("metadata_coverage"))),
            "availability": (st.column_config.TextColumn(rag_lab_t("availability"))),
            "coverage": (
                st.column_config.ProgressColumn(
                    rag_lab_t("coverage"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.0f%%",
                )
            ),
            "registered_runs": (
                st.column_config.TextColumn(rag_lab_t("registered_runs"))
            ),
            "distinct_values": (
                st.column_config.TextColumn(rag_lab_t("distinct_values"))
            ),
        },
    )


def _render_run_configuration(
    history: Any,
) -> Any | None:
    st.subheader(rag_lab_t("advanced_experiment"))

    st.caption(rag_lab_t("advanced_experiment_caption"))

    options = build_rag_lab_run_options(
        history,
        complete_only=False,
    )

    if not options:
        st.info(rag_lab_t("no_history"))
        return None

    references = [option.run_reference for option in options]

    labels = {option.run_reference: option.label for option in options}

    selected_reference = st.selectbox(
        rag_lab_t("select_run"),
        references,
        format_func=lambda value: labels[value],
        key=(f"rag_lab_advanced_run_{_rag_lab_language()}"),
    )

    entry = _find_entry_by_reference(
        history,
        selected_reference,
    )

    if entry is None:
        st.warning(rag_lab_t("no_history"))
        return None

    snapshot = build_experiment_metadata_snapshot(
        entry,
        unavailable_label=rag_lab_t("not_registered"),
        enabled_label=rag_lab_t("enabled"),
        disabled_label=rag_lab_t("disabled"),
    )

    retrieval_items = [item for item in snapshot if item.category == "retrieval"]

    generation_items = [item for item in snapshot if item.category == "generation"]

    knowledge_items = [item for item in snapshot if item.category == "knowledge"]

    evaluation_items = [item for item in snapshot if item.category == "evaluation"]

    performance_items = [item for item in snapshot if item.category == "performance"]

    groups = (
        retrieval_items,
        generation_items,
        knowledge_items,
        evaluation_items,
        performance_items,
    )

    for group in groups:
        if not group:
            continue

        columns = st.columns(
            min(
                4,
                len(group),
            )
        )

        for index, item in enumerate(group):
            column = columns[index % len(columns)]

            column.metric(
                _metadata_field_label(
                    item.key,
                    item.label,
                ),
                item.display_value,
            )

    return entry


def _render_capabilities(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("experimental_comparisons"))

    st.caption(rag_lab_t("experimental_comparisons_caption"))

    capabilities = build_rag_lab_capabilities(history)

    rows = []

    labels = {
        "reranker_comparison": rag_lab_t("capability_reranker"),
        "retrieval_strategy_comparison": (rag_lab_t("capability_retrieval_strategy")),
        "model_prompt_comparison": rag_lab_t("capability_model_prompt"),
        "rag_configuration_comparison": (rag_lab_t("capability_rag_configuration")),
        "performance_cost_analysis": (rag_lab_t("capability_performance_cost")),
        "phoenix_trace_integration": (rag_lab_t("capability_phoenix")),
    }

    for item in capabilities:
        rows.append(
            {
                "capability": labels.get(
                    item.key,
                    item.key,
                ),
                "availability": (_availability_label(item.status)),
                "registered_runs": (f"{item.available_runs}/{item.total_runs}"),
                "message": (
                    rag_lab_t("capability_active_message")
                    if (item.status == RagLabCapabilityStatus.ACTIVE)
                    else (
                        rag_lab_t("capability_partial_message")
                        if (item.status == RagLabCapabilityStatus.PARTIAL)
                        else rag_lab_t("capability_waiting_message")
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "capability": (st.column_config.TextColumn(rag_lab_t("capability"))),
            "availability": (st.column_config.TextColumn(rag_lab_t("availability"))),
            "registered_runs": (
                st.column_config.TextColumn(rag_lab_t("registered_runs"))
            ),
            "message": (st.column_config.TextColumn(rag_lab_t("message"))),
        },
    )


def _render_quality_gate(
    history: Any,
    selected_entry: Any | None,
) -> None:
    st.subheader(rag_lab_t("quality_gate"))

    st.caption(rag_lab_t("quality_gate_caption"))

    first, second, third = st.columns(3)

    with first:
        answer_threshold = st.slider(
            rag_lab_t("minimum_answer_relevancy"),
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.01,
            key=("rag_lab_gate_answer_relevancy"),
        )

        faithfulness_threshold = st.slider(
            rag_lab_t("minimum_faithfulness"),
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.01,
            key=("rag_lab_gate_faithfulness"),
        )

    with second:
        contextual_threshold = st.slider(
            rag_lab_t("minimum_contextual_relevancy"),
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.01,
            key=("rag_lab_gate_contextual_relevancy"),
        )

        aggregate_threshold = st.slider(
            rag_lab_t("minimum_aggregate"),
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.01,
            key=("rag_lab_gate_aggregate"),
        )

    with third:
        maximum_regression = st.slider(
            rag_lab_t("maximum_regression"),
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.01,
            key=("rag_lab_gate_regression"),
        )

    thresholds = QualityGateThresholds(
        answer_relevancy=(answer_threshold),
        faithfulness=(faithfulness_threshold),
        contextual_relevancy=(contextual_threshold),
        aggregate_score=(aggregate_threshold),
        maximum_regression=(maximum_regression),
    )

    if selected_entry is None:
        st.info(rag_lab_t("gate_incomplete"))
        return

    result = evaluate_quality_gate(
        selected_entry,
        thresholds=thresholds,
    )

    if result.passed is True:
        st.success(rag_lab_t("gate_passed"))
    elif result.passed is False:
        st.error(rag_lab_t("gate_failed"))
    else:
        st.warning(rag_lab_t("gate_incomplete"))

    rows = []

    for check in result.checks:
        if check.passed is True:
            result_label = rag_lab_t("passed")
        elif check.passed is False:
            result_label = rag_lab_t("failed_label")
        else:
            result_label = rag_lab_t("inconclusive")

        rows.append(
            {
                "metric": _metric_label(check.key),
                "score": check.score,
                "threshold": (check.threshold),
                "result": result_label,
                "reason": (
                    rag_lab_t("gate_reason_score_missing")
                    if check.passed is None and (check.key != "maximum-regression")
                    else (
                        rag_lab_t("gate_reason_regression_unavailable")
                        if check.passed is None
                        else (
                            rag_lab_t("gate_reason_regression_passed")
                            if (
                                check.key == "maximum-regression"
                                and check.passed is True
                            )
                            else (
                                rag_lab_t("gate_reason_regression_failed")
                                if (check.key == "maximum-regression")
                                else (
                                    rag_lab_t("gate_reason_passed")
                                    if check.passed is True
                                    else rag_lab_t("gate_reason_failed")
                                )
                            )
                        )
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "metric": (st.column_config.TextColumn(rag_lab_t("metric"))),
            "score": (
                st.column_config.NumberColumn(
                    rag_lab_t("score"),
                    format="%.4f",
                )
            ),
            "threshold": (
                st.column_config.NumberColumn(
                    rag_lab_t("threshold"),
                    format="%.4f",
                )
            ),
            "result": (st.column_config.TextColumn(rag_lab_t("result"))),
            "reason": (st.column_config.TextColumn(rag_lab_t("reason"))),
        },
    )


def _render_ranking(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("ranking"))

    st.caption(rag_lab_t("ranking_caption"))

    ranking = rank_rag_lab_runs(history)

    if not ranking:
        st.info(rag_lab_t("waiting_real_data"))
        return

    rows = []

    for item in ranking:
        basis = (
            rag_lab_t("ranking_quality_performance")
            if (item.ranking_basis == "quality_then_performance")
            else rag_lab_t("ranking_quality_only")
        )

        rows.append(
            {
                "position": item.position,
                "run_reference": (item.run_reference),
                "quality_score": (item.quality_score),
                "failed_metrics": (item.failing_metric_count),
                "latency": item.latency_ms,
                "estimated_cost": (item.estimated_cost_usd),
                "ranking_basis": basis,
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "position": (
                st.column_config.NumberColumn(
                    rag_lab_t("position"),
                    format="%d",
                )
            ),
            "run_reference": (st.column_config.TextColumn(rag_lab_t("run_reference"))),
            "quality_score": (
                st.column_config.ProgressColumn(
                    rag_lab_t("quality_score"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "failed_metrics": (
                st.column_config.NumberColumn(
                    rag_lab_t("failed_metrics"),
                    format="%d",
                )
            ),
            "latency": (
                st.column_config.NumberColumn(
                    rag_lab_t("latency"),
                    format="%.2f ms",
                )
            ),
            "estimated_cost": (
                st.column_config.NumberColumn(
                    rag_lab_t("estimated_cost"),
                    format="US$ %.6f",
                )
            ),
            "ranking_basis": (st.column_config.TextColumn(rag_lab_t("ranking_basis"))),
        },
    )


def _render_performance_and_cost(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("performance_cost"))

    cost = calculate_cost_per_approved_run(history)

    if cost is None:
        st.info(rag_lab_t("waiting_real_data"))
    else:
        st.metric(
            rag_lab_t("cost_per_approved_run"),
            f"US$ {cost:.6f}",
        )


def _render_phoenix_and_cases(
    history: Any,
) -> None:
    capabilities = {item.key: item for item in (build_rag_lab_capabilities(history))}

    phoenix = capabilities.get("phoenix_trace_integration")

    st.subheader(rag_lab_t("phoenix"))

    if phoenix is None or phoenix.status != RagLabCapabilityStatus.ACTIVE:
        st.info(rag_lab_t("phoenix_waiting"))
    else:
        st.success(rag_lab_t("available"))

    st.subheader(rag_lab_t("case_details"))

    st.info(rag_lab_t("case_details_waiting"))


def _render_exports(
    history: Any,
    thresholds: QualityGateThresholds,
) -> None:
    st.subheader(rag_lab_t("exports"))

    csv_data = export_rag_lab_history_csv(history)

    json_data = export_rag_lab_report_json(
        history,
        quality_gate=thresholds,
    )

    first, second = st.columns(2)

    with first:
        st.download_button(
            rag_lab_t("export_csv"),
            data=csv_data,
            file_name=("rag-lab-history.csv"),
            mime="text/csv",
            key="rag_lab_export_csv",
        )

    with second:
        st.download_button(
            rag_lab_t("export_json"),
            data=json_data,
            file_name=("rag-lab-report.json"),
            mime="application/json",
            key="rag_lab_export_json",
        )


def _render_advanced_sections(
    history: Any,
) -> None:
    st.divider()

    _render_metadata_coverage(history)

    st.divider()

    selected_entry = _render_run_configuration(history)

    st.divider()

    _render_capabilities(history)

    st.divider()

    _render_quality_gate(
        history,
        selected_entry,
    )

    st.divider()

    _render_ranking(history)

    st.divider()

    _render_performance_and_cost(history)

    st.divider()

    _render_phoenix_and_cases(history)

    thresholds = QualityGateThresholds(
        answer_relevancy=float(
            st.session_state.get(
                "rag_lab_gate_answer_relevancy",
                0.70,
            )
        ),
        faithfulness=float(
            st.session_state.get(
                "rag_lab_gate_faithfulness",
                0.70,
            )
        ),
        contextual_relevancy=float(
            st.session_state.get(
                "rag_lab_gate_contextual_relevancy",
                0.70,
            )
        ),
        aggregate_score=float(
            st.session_state.get(
                "rag_lab_gate_aggregate",
                0.70,
            )
        ),
        maximum_regression=float(
            st.session_state.get(
                "rag_lab_gate_regression",
                0.05,
            )
        ),
    )

    st.divider()

    _render_exports(
        history,
        thresholds,
    )


def _render_history_table(
    history: Any,
) -> None:
    st.subheader(rag_lab_t("history_table"))

    rows = build_rag_lab_timeline(history)

    if not rows:
        st.info(rag_lab_t("no_history"))
        return

    frame = pd.DataFrame(rows)

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
        errors="coerce",
    )

    st.dataframe(
        frame.sort_values(
            "recorded_at",
            ascending=False,
        ),
        width="stretch",
        hide_index=True,
        column_config={
            "run_reference": (st.column_config.TextColumn(rag_lab_t("run_reference"))),
            "recorded_at": (st.column_config.DatetimeColumn(rag_lab_t("recorded_at"))),
            "branch": (st.column_config.TextColumn(rag_lab_t("branch"))),
            "environment": (st.column_config.TextColumn(rag_lab_t("environment"))),
            "rag_triad_score": (
                st.column_config.ProgressColumn(
                    rag_lab_t("triad_score"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "rag_triad_status": (
                st.column_config.TextColumn(rag_lab_t("triad_status"))
            ),
            "rag_triad_passed": (
                st.column_config.CheckboxColumn(rag_lab_t("triad_passed"))
            ),
            "complete": (st.column_config.CheckboxColumn(rag_lab_t("complete"))),
            "answer-relevancy": (
                st.column_config.ProgressColumn(
                    rag_lab_t("answer_relevancy"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "faithfulness": (
                st.column_config.ProgressColumn(
                    rag_lab_t("faithfulness"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "contextual-relevancy": (
                st.column_config.ProgressColumn(
                    rag_lab_t("contextual_relevancy"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
        },
    )


def render_rag_evaluation_lab_page() -> None:
    """
    Renderiza o Laboratório de Qualidade RAG.

    A página reutiliza o histórico real das avaliações e não
    cria resultados simulados.
    """

    _render_header()

    with st.expander(
        rag_lab_t("history_settings"),
        expanded=False,
    ):
        history_path = st.text_input(
            rag_lab_t("history_file"),
            str(DEFAULT_HISTORY_PATH),
            key=(f"rag_lab_history_path_{_rag_lab_language()}"),
        )

    try:
        history = load_dashboard_history(history_path)
    except Exception as exc:
        st.error(f"{rag_lab_t('load_error')}: {exc}")
        return

    filtered_history = _render_filters(history)

    triad_entries = get_rag_lab_entries(filtered_history)

    if not triad_entries:
        st.info(rag_lab_t("no_history"))

        _render_advanced_sections(filtered_history)

        st.divider()

        _render_history_table(filtered_history)

        return

    _render_summary(filtered_history)

    st.divider()

    _render_timeline(filtered_history)

    st.divider()

    _render_comparison(filtered_history)

    _render_advanced_sections(filtered_history)

    st.divider()

    _render_history_table(filtered_history)

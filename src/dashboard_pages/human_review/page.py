from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import streamlit as st

from .api_client import (
    HumanReviewDashboardApiError,
    listar_revisoes_hitl_api,
    obter_metricas_hitl_api,
    obter_revisao_hitl_api,
    recuperar_claims_hitl_api,
    resolver_revisao_hitl_api,
)
from .components import (
    render_detalhes_revisao_hitl,
    render_distribuicao_hitl,
    render_formulario_decisao_hitl,
    render_metricas_executivas_hitl,
    render_tabela_revisoes_hitl,
)
from .formatters import (
    RISK_LABELS,
    STATUS_LABELS,
)
from .state import (
    HumanReviewDashboardFilters,
)


STATE_KEY = "hitl_admin_dashboard_state"


def _require_admin_identity() -> str:
    profile = (
        str(
            st.session_state.get(
                "perfil_usuario",
                "",
            )
        )
        .strip()
        .lower()
    )

    user_id = str(
        st.session_state.get(
            "usuario",
            "",
        )
    ).strip()

    if profile != "admin" or not user_id:
        raise PermissionError("Acesso restrito ao administrador autenticado da INNA.")

    return user_id


def _get_filters() -> HumanReviewDashboardFilters:
    value = st.session_state.get(STATE_KEY)

    if isinstance(
        value,
        HumanReviewDashboardFilters,
    ):
        return value

    filters = HumanReviewDashboardFilters()

    st.session_state[STATE_KEY] = filters

    return filters


def _set_filters(
    filters: HumanReviewDashboardFilters,
) -> None:
    st.session_state[STATE_KEY] = filters


def _render_filters(
    current: HumanReviewDashboardFilters,
) -> HumanReviewDashboardFilters:
    with st.expander(
        "Filtros avançados",
        expanded=True,
    ):
        with st.form("hitl_filters_form"):
            row_one = st.columns(2)

            statuses = row_one[0].multiselect(
                "Status",
                options=list(STATUS_LABELS.keys()),
                default=list(current.statuses),
                format_func=lambda value: STATUS_LABELS[value],
            )

            risk_levels = row_one[1].multiselect(
                "Nível de risco",
                options=[value for value in RISK_LABELS if value],
                default=list(current.risk_levels),
                format_func=lambda value: RISK_LABELS[value],
            )

            row_two = st.columns(3)

            search = row_two[0].text_input(
                "Busca geral",
                value=current.search,
            )

            requested_by = row_two[1].text_input(
                "Agente solicitante",
                value=current.requested_by,
            )

            reviewer_id = row_two[2].text_input(
                "Revisor",
                value=current.reviewer_id,
            )

            row_three = st.columns(3)

            created_from = row_three[0].date_input(
                "Data inicial",
                value=(current.created_from or date.today() - timedelta(days=30)),
            )

            created_to = row_three[1].date_input(
                "Data final",
                value=(current.created_to or date.today()),
            )

            limit = row_three[2].selectbox(
                "Itens por página",
                options=[
                    10,
                    25,
                    50,
                    100,
                    200,
                ],
                index=[
                    10,
                    25,
                    50,
                    100,
                    200,
                ].index(
                    current.limit
                    if current.limit
                    in {
                        10,
                        25,
                        50,
                        100,
                        200,
                    }
                    else 25
                ),
            )

            apply_filters = st.form_submit_button(
                "Aplicar filtros",
                use_container_width=True,
            )

    if not apply_filters:
        return current

    return HumanReviewDashboardFilters(
        statuses=statuses,
        risk_levels=risk_levels,
        requested_by=requested_by,
        reviewer_id=reviewer_id,
        search=search,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=0,
    )


def render_human_review_admin_page() -> None:
    try:
        admin_user_id = _require_admin_identity()
    except PermissionError as exc:
        st.error(str(exc))
        return

    st.title("🧑‍⚖️ Revisão Humana — INNA")

    st.caption(
        "Centro operacional Human-in-the-Loop "
        "para decisões críticas, auditoria, "
        "métricas e recuperação de processos."
    )

    current_filters = _get_filters()

    filters = _render_filters(current_filters)

    if filters != current_filters:
        _set_filters(filters)

    top_actions = st.columns([1, 1, 2])

    if top_actions[0].button(
        "🔄 Atualizar dados",
        use_container_width=True,
    ):
        st.rerun()

    with top_actions[1].popover("🛠️ Recuperar claims"):
        timeout_seconds = st.number_input(
            "Tempo mínimo sem atualização",
            min_value=30,
            max_value=86_400,
            value=300,
            step=30,
        )

        if st.button(
            "Executar recuperação",
            use_container_width=True,
        ):
            try:
                recovered = recuperar_claims_hitl_api(
                    admin_user_id=(admin_user_id),
                    timeout_seconds=int(timeout_seconds),
                )

                if recovered:
                    st.success(f"{len(recovered)} claim(s) recuperado(s).")
                else:
                    st.info("Nenhum claim expirado foi encontrado.")

            except HumanReviewDashboardApiError as exc:
                st.error(str(exc))

    try:
        metrics = obter_metricas_hitl_api(
            admin_user_id=admin_user_id,
            created_from=(
                filters.created_from.isoformat() if filters.created_from else ""
            ),
            created_to=(filters.created_to.isoformat() if filters.created_to else ""),
        )

        page = listar_revisoes_hitl_api(
            admin_user_id=admin_user_id,
            **filters.to_api_kwargs(),
        )

    except HumanReviewDashboardApiError as exc:
        st.error(str(exc))
        return

    overview_tab, queue_tab, audit_tab = st.tabs(
        [
            "📊 Visão geral",
            "📋 Fila de revisões",
            "🔎 Detalhes e decisão",
        ]
    )

    with overview_tab:
        render_metricas_executivas_hitl(metrics)

        charts = st.columns(3)

        with charts[0]:
            render_distribuicao_hitl(
                "Distribuição por risco",
                metrics.by_risk,
            )

        with charts[1]:
            render_distribuicao_hitl(
                "Distribuição por agente",
                metrics.by_agent,
            )

        with charts[2]:
            render_distribuicao_hitl(
                "Distribuição por revisor",
                metrics.by_reviewer,
            )

    with queue_tab:
        render_tabela_revisoes_hitl(page)

        navigation = st.columns([1, 1, 2])

        if navigation[0].button(
            "⬅️ Página anterior",
            disabled=not page.has_previous,
            use_container_width=True,
        ):
            _set_filters(filters.previous_page())
            st.rerun()

        if navigation[1].button(
            "Próxima página ➡️",
            disabled=not page.has_next,
            use_container_width=True,
        ):
            _set_filters(filters.next_page(has_next=page.has_next))
            st.rerun()

        available_ids = [record.review_id for record in page.items]

        selected_review_id = st.selectbox(
            "Selecionar revisão para análise",
            options=[
                "",
                *available_ids,
            ],
            format_func=lambda value: "Selecione uma revisão" if not value else value,
        )

        if selected_review_id:
            st.session_state["hitl_selected_review_id"] = selected_review_id

    with audit_tab:
        selected_review_id = str(
            st.session_state.get(
                "hitl_selected_review_id",
                "",
            )
        ).strip()

        manual_review_id = st.text_input(
            "Review ID",
            value=selected_review_id,
            placeholder=("Informe o identificador da revisão."),
        )

        if not manual_review_id:
            st.info("Selecione uma revisão na fila ou informe um Review ID.")
            return

        try:
            record = obter_revisao_hitl_api(
                admin_user_id=admin_user_id,
                review_id=manual_review_id,
            )

        except HumanReviewDashboardApiError as exc:
            st.error(str(exc))
            return

        render_detalhes_revisao_hitl(record)

        def submit_decision(
            action: str,
            comment: str,
            reason: str,
            corrections: dict[str, Any],
        ) -> None:
            try:
                result = resolver_revisao_hitl_api(
                    admin_user_id=(admin_user_id),
                    review_id=(record.review_id),
                    thread_id=(record.thread_id),
                    action=action,
                    comment=comment,
                    reason=reason,
                    corrections=corrections,
                )

                st.success(f"Decisão registrada: {result.status}.")

                st.session_state.pop(
                    "hitl_selected_review_id",
                    None,
                )

                st.rerun()

            except HumanReviewDashboardApiError as exc:
                st.error(str(exc))

        render_formulario_decisao_hitl(
            record=record,
            on_submit=submit_decision,
        )


__all__ = [
    "render_human_review_admin_page",
]

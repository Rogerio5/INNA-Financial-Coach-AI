from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import streamlit as st

from .formatters import (
    formatar_acao_hitl,
    formatar_data_hora_hitl,
    formatar_duracao_hitl,
    formatar_identidade_hitl,
    formatar_percentual_hitl,
    formatar_risco_hitl,
    formatar_status_hitl,
    resumir_texto_hitl,
)
from .models import (
    HumanReviewDashboardMetrics,
    HumanReviewDashboardPage,
    HumanReviewDashboardRecord,
)


def render_metricas_executivas_hitl(
    metrics: HumanReviewDashboardMetrics,
) -> None:
    row_one = st.columns(4)

    row_one[0].metric(
        "Total de revisões",
        metrics.total,
    )

    row_one[1].metric(
        "Aguardando análise",
        metrics.pending,
    )

    row_one[2].metric(
        "Em processamento",
        metrics.processing,
    )

    row_one[3].metric(
        "Falhas na retomada",
        metrics.resume_failed,
    )

    row_two = st.columns(4)

    row_two[0].metric(
        "Aprovadas",
        metrics.approved,
    )

    row_two[1].metric(
        "Corrigidas",
        metrics.corrected,
    )

    row_two[2].metric(
        "Taxa de aprovação",
        formatar_percentual_hitl(metrics.approval_rate),
    )

    row_two[3].metric(
        "Taxa de correção",
        formatar_percentual_hitl(metrics.correction_rate),
    )

    row_three = st.columns(2)

    row_three[0].metric(
        "Espera média",
        formatar_duracao_hitl(metrics.average_wait_seconds),
    )

    row_three[1].metric(
        "Resolução média",
        formatar_duracao_hitl(metrics.average_resolution_seconds),
    )


def preparar_tabela_revisoes_hitl(
    page: HumanReviewDashboardPage,
) -> list[dict[str, Any]]:
    return [
        {
            "Revisão": record.review_id,
            "Status": formatar_status_hitl(record.status),
            "Risco": formatar_risco_hitl(record.risk_level),
            "Agente": (record.requested_by or "Não informado"),
            "Motivo": resumir_texto_hitl(
                record.reason,
                limite=120,
            ),
            "Revisor": (formatar_identidade_hitl(record.reviewer_id)),
            "Criada em": (formatar_data_hora_hitl(record.created_at)),
        }
        for record in page.items
    ]


def render_tabela_revisoes_hitl(
    page: HumanReviewDashboardPage,
) -> None:
    rows = preparar_tabela_revisoes_hitl(page)

    if not rows:
        st.info("Nenhuma revisão encontrada para os filtros selecionados.")
        return

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    start = page.offset + 1 if page.total else 0

    end = min(
        page.offset + len(page.items),
        page.total,
    )

    st.caption(f"Exibindo {start}–{end} de {page.total} revisões.")


def render_distribuicao_hitl(
    title: str,
    values: dict[str, int],
) -> None:
    st.markdown(f"#### {title}")

    if not values:
        st.caption("Sem dados disponíveis.")
        return

    rows = [
        {
            "Categoria": (
                formatar_risco_hitl(key) if title == "Distribuição por risco" else key
            ),
            "Quantidade": value,
        }
        for key, value in sorted(
            values.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


def render_detalhes_revisao_hitl(
    record: HumanReviewDashboardRecord,
) -> None:
    st.markdown("### Detalhes da revisão")

    cols = st.columns(4)

    cols[0].metric(
        "Status",
        formatar_status_hitl(record.status),
    )

    cols[1].metric(
        "Risco",
        formatar_risco_hitl(record.risk_level),
    )

    cols[2].metric(
        "Agente solicitante",
        record.requested_by or "Não informado",
    )

    cols[3].metric(
        "Revisor",
        formatar_identidade_hitl(record.reviewer_id),
    )

    st.markdown(f"**Review ID:** `{record.review_id}`")

    st.markdown(f"**Thread ID:** `{record.thread_id}`")

    st.markdown(f"**Gatilho:** {record.trigger or 'Não informado'}")

    st.markdown(f"**Motivo:** {record.reason or 'Não informado'}")

    st.markdown(f"**Criada em:** {formatar_data_hora_hitl(record.created_at)}")

    st.markdown(f"**Atualizada em:** {formatar_data_hora_hitl(record.updated_at)}")

    if record.failure_reason:
        st.error(record.failure_reason)

    with st.expander(
        "Payload enviado pelo agente",
        expanded=False,
    ):
        st.json(record.payload)

    if record.corrections:
        with st.expander(
            "Correções aplicadas",
            expanded=False,
        ):
            st.json(record.corrections)

    if record.reviewer_comment:
        st.info("Comentário do revisor: " + record.reviewer_comment)

    if record.rejection_reason:
        st.warning("Motivo da rejeição: " + record.rejection_reason)


def parse_corrections_json_hitl(
    value: str,
) -> dict[str, Any]:
    normalized = str(value or "").strip()

    if not normalized:
        return {}

    try:
        result = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise ValueError("As correções devem estar em formato JSON válido.") from exc

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError("As correções devem formar um objeto JSON.")

    return result


def render_formulario_decisao_hitl(
    *,
    record: HumanReviewDashboardRecord,
    on_submit: Callable[
        [
            str,
            str,
            str,
            dict[str, Any],
        ],
        None,
    ],
) -> None:
    terminal_statuses = {
        "approved",
        "corrected",
        "rejected",
        "cancelled",
    }

    if record.status in terminal_statuses:
        st.success("Esta revisão já foi finalizada.")
        return

    allowed_actions = tuple(
        action
        for action in record.allowed_actions
        if action
        in {
            "approve",
            "correct",
            "reject",
            "cancel",
        }
    )

    if not allowed_actions:
        st.warning("Esta revisão não possui ações administrativas disponíveis.")
        return

    st.markdown("### Decisão humana")

    with st.form(
        key=("hitl_decision_form_" + record.review_id),
        clear_on_submit=False,
    ):
        action = st.selectbox(
            "Ação",
            options=allowed_actions,
            format_func=(formatar_acao_hitl),
        )

        comment = st.text_area(
            "Comentário do revisor",
            max_chars=10_000,
            placeholder=("Registre a justificativa técnica ou observação da análise."),
        )

        reason = ""

        corrections_text = ""

        if action == "reject":
            reason = st.text_area(
                "Motivo da rejeição",
                max_chars=10_000,
                placeholder=("Explique por que a operação não pode prosseguir."),
            )

        if action == "correct":
            corrections_text = st.text_area(
                "Correções em JSON",
                height=180,
                placeholder=('{\n  "campo": "novo valor"\n}'),
            )

        confirmation = st.checkbox(
            "Confirmo que revisei o payload e compreendo o impacto da decisão."
        )

        submitted = st.form_submit_button(
            "Registrar decisão",
            use_container_width=True,
            disabled=not confirmation,
        )

    if not submitted:
        return

    try:
        corrections = parse_corrections_json_hitl(corrections_text)

        if action == "correct" and not corrections:
            raise ValueError("Informe pelo menos uma correção.")

        if action == "reject" and not reason.strip():
            raise ValueError("Informe o motivo da rejeição.")

        on_submit(
            action,
            comment.strip(),
            reason.strip(),
            corrections,
        )

    except ValueError as exc:
        st.error(str(exc))


__all__ = [
    "parse_corrections_json_hitl",
    "preparar_tabela_revisoes_hitl",
    "render_detalhes_revisao_hitl",
    "render_distribuicao_hitl",
    "render_formulario_decisao_hitl",
    "render_metricas_executivas_hitl",
    "render_tabela_revisoes_hitl",
]

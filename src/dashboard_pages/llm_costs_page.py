"""
LLM Cost Center da INNA.

Painel de tokens, custos estimados, desempenho e auditoria
das chamadas realizadas aos modelos de linguagem.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def preparar_consumo_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Normaliza os eventos para análises e gráficos.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    base = df.copy()

    base["criado_em"] = pd.to_datetime(
        base["criado_em"],
        utc=True,
        errors="coerce",
    )

    colunas_numericas = [
        "tokens_entrada",
        "tokens_saida",
        "tokens_totais",
        "custo_entrada_usd",
        "custo_saida_usd",
        "custo_total_usd",
        "duracao_ms",
    ]

    for coluna in colunas_numericas:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(
                base[coluna],
                errors="coerce",
            ).fillna(0)

    if "sucesso" in base.columns:
        base["sucesso"] = (
            base["sucesso"]
            .fillna(False)
            .astype(bool)
        )

    return (
        base.dropna(
            subset=["criado_em"]
        )
        .sort_values(
            "criado_em",
            ascending=True,
        )
        .reset_index(drop=True)
    )


def resumir_consumo_llm(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Calcula os indicadores principais do Cost Center.
    """
    base = preparar_consumo_exibicao(df)

    if base.empty:
        return {
            "eventos": 0,
            "tokens_entrada": 0,
            "tokens_saida": 0,
            "tokens_totais": 0,
            "custo_total_usd": 0.0,
            "duracao_media_ms": 0.0,
            "duracao_p95_ms": 0.0,
            "taxa_sucesso": 0.0,
        }

    total = len(base)

    sucessos = int(
        base["sucesso"].sum()
    )

    return {
        "eventos": total,
        "tokens_entrada": int(
            base["tokens_entrada"].sum()
        ),
        "tokens_saida": int(
            base["tokens_saida"].sum()
        ),
        "tokens_totais": int(
            base["tokens_totais"].sum()
        ),
        "custo_total_usd": round(
            float(
                base["custo_total_usd"].sum()
            ),
            8,
        ),
        "duracao_media_ms": round(
            float(
                base["duracao_ms"].mean()
            ),
            3,
        ),
        "duracao_p95_ms": round(
            float(
                base["duracao_ms"].quantile(
                    0.95
                )
            ),
            3,
        ),
        "taxa_sucesso": round(
            (
                sucessos
                / total
            )
            * 100,
            2,
        ),
    }


def render_alertas_llm_section(
    *,
    base_consumo: pd.DataFrame,
    finops: dict[str, Any],
) -> None:
    """
    Renderiza detecção, persistência e gestão de alertas.
    """
    try:
        from observability.llm_alerts import (
            avaliar_e_persistir_alertas,
            carregar_alertas_llm,
            resolver_alerta_llm,
        )
    except ImportError:
        from src.observability.llm_alerts import (
            avaliar_e_persistir_alertas,
            carregar_alertas_llm,
            resolver_alerta_llm,
        )

    try:
        from observability.llm_notifications import (
            avaliar_persistir_e_notificar_alertas,
            carregar_configuracao,
            carregar_notificacoes,
            notificar_alerta_email,
        )
    except ImportError:
        from src.observability.llm_notifications import (
            avaliar_persistir_e_notificar_alertas,
            carregar_configuracao,
            carregar_notificacoes,
            notificar_alerta_email,
        )

    st.divider()
    st.markdown(
        "## 🚨 Alertas de custo e desempenho"
    )

    st.caption(
        "Alertas persistentes de orçamento, projeção, "
        "tokens, falhas e latência."
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1, 1, 2]
        )
    )

    status_filtro = controle_1.selectbox(
        "Status dos alertas",
        options=[
            "aberto",
            "resolvido",
            "todos",
        ],
        index=0,
        key="llm_alert_status",
    )

    limite_alertas = controle_2.selectbox(
        "Limite de alertas",
        options=[
            50,
            100,
            250,
            500,
        ],
        index=1,
        key="llm_alert_limit",
    )

    with controle_3:
        st.write("")

        avaliar = st.button(
            "🔎 Avaliar alertas agora",
            use_container_width=True,
            key="llm_alert_evaluate",
        )

    if avaliar:
        resultado_avaliacao = (
            avaliar_persistir_e_notificar_alertas(
                base_consumo,
                finops,
            )
        )

        if resultado_avaliacao.get("ok"):
            st.success(
                "Avaliação concluída. "
                f"Detectados: "
                f"{resultado_avaliacao.get('total_detectados', 0)} | "
                f"Salvos: "
                f"{resultado_avaliacao.get('total_salvos', 0)} | "
                f"Duplicados: "
                f"{resultado_avaliacao.get('total_duplicados', 0)} | "
                f"E-mails enviados: "
                f"{resultado_avaliacao.get('total_notificacoes_enviadas', 0)} | "
                f"Falhas de e-mail: "
                f"{resultado_avaliacao.get('total_notificacoes_falhas', 0)}"
            )
        else:
            st.error(
                "Não foi possível concluir a avaliação."
            )

    status_consulta = (
        None
        if status_filtro == "todos"
        else status_filtro
    )

    resultado_alertas = carregar_alertas_llm(
        limite=int(
            limite_alertas
        ),
        status=status_consulta,
    )

    if not resultado_alertas.get("ok"):
        st.error(
            resultado_alertas.get(
                "message",
                "Não foi possível carregar os alertas.",
            )
        )
        return

    alertas = resultado_alertas.get(
        "df"
    )

    if alertas is None or alertas.empty:
        st.info(
            "Nenhum alerta encontrado para o filtro atual."
        )
        return

    contagem = (
        alertas["severidade"]
        .value_counts()
        .to_dict()
    )

    resumo_cols = st.columns(5)

    resumo_cols[0].metric(
        "Total",
        len(alertas),
    )

    resumo_cols[1].metric(
        "Críticos",
        int(
            contagem.get(
                "critica",
                0,
            )
        ),
    )

    resumo_cols[2].metric(
        "Altos",
        int(
            contagem.get(
                "alta",
                0,
            )
        ),
    )

    resumo_cols[3].metric(
        "Médios",
        int(
            contagem.get(
                "media",
                0,
            )
        ),
    )

    resumo_cols[4].metric(
        "Baixos",
        int(
            contagem.get(
                "baixa",
                0,
            )
        ),
    )

    simbolos = {
        "critica": "🔴",
        "alta": "🟠",
        "media": "🟡",
        "baixa": "🔵",
        "informativa": "ℹ️",
    }

    configuracao_email = carregar_configuracao()

    resultado_notificacoes = carregar_notificacoes(
        limite=1000
    )

    notificacoes_df = resultado_notificacoes.get(
        "df"
    )

    alertas_enviados: set[int] = set()

    if (
        notificacoes_df is not None
        and not notificacoes_df.empty
        and "alerta_id" in notificacoes_df.columns
        and "status" in notificacoes_df.columns
    ):
        enviados_df = notificacoes_df[
            notificacoes_df["status"] == "enviado"
        ]

        alertas_enviados = {
            int(alerta_id)
            for alerta_id in enviados_df[
                "alerta_id"
            ].dropna().tolist()
        }

    st.markdown(
        "### Lista de alertas"
    )

    if not configuracao_email.get(
        "habilitado"
    ):
        st.warning(
            "As notificações por e-mail estão "
            "desabilitadas no ambiente."
        )
    elif not configuracao_email.get(
        "destinatario"
    ):
        st.warning(
            "O destinatário dos alertas não está configurado."
        )
    elif not configuracao_email.get(
        "resend_configurado"
    ):
        st.warning(
            "A integração com o Resend não está configurada."
        )
    else:
        st.success(
            "Notificações por e-mail habilitadas. "
            "Alertas altos e críticos podem ser enviados."
        )

    for _, alerta in alertas.iterrows():
        severidade = str(
            alerta.get(
                "severidade",
                "informativa",
            )
        )

        status = str(
            alerta.get(
                "status",
                "aberto",
            )
        )

        simbolo = simbolos.get(
            severidade,
            "ℹ️",
        )

        titulo = str(
            alerta.get(
                "titulo",
                "Alerta",
            )
        )

        with st.container(
            border=True
        ):
            cabecalho_1, cabecalho_2 = (
                st.columns(
                    [4, 1]
                )
            )

            cabecalho_1.markdown(
                f"### {simbolo} {titulo}"
            )

            cabecalho_2.metric(
                "Status",
                status.title(),
            )

            st.markdown(
                str(
                    alerta.get(
                        "descricao",
                        "",
                    )
                )
            )

            metrica_cols = st.columns(4)

            metrica_cols[0].metric(
                "Severidade",
                severidade.title(),
            )

            metrica_cols[1].metric(
                "Valor atual",
                alerta.get(
                    "valor_atual",
                    0,
                ),
            )

            metrica_cols[2].metric(
                "Limite",
                alerta.get(
                    "valor_limite",
                    0,
                ),
            )

            metrica_cols[3].metric(
                "Unidade",
                alerta.get(
                    "unidade",
                    "—",
                ),
            )

            st.info(
                "Recomendação: "
                + str(
                    alerta.get(
                        "recomendacao",
                        "",
                    )
                )
            )

            st.caption(
                "Código: "
                f"{alerta.get('codigo', '')} | "
                "Categoria: "
                f"{alerta.get('categoria', '')} | "
                "Criado em: "
                f"{alerta.get('criado_em', '')}"
            )

            if status == "aberto":
                alerta_id = int(
                    alerta["id"]
                )

                pode_enviar_email = (
                    severidade
                    in {"alta", "critica"}
                    and configuracao_email.get(
                        "habilitado"
                    )
                    and bool(
                        configuracao_email.get(
                            "destinatario"
                        )
                    )
                    and configuracao_email.get(
                        "resend_configurado"
                    )
                )

                ja_enviado = (
                    alerta_id
                    in alertas_enviados
                )

                coluna_email, coluna_resolver = (
                    st.columns(2)
                )

                with coluna_email:
                    if ja_enviado:
                        st.success(
                            "📧 Notificação já enviada"
                        )

                    elif severidade not in {
                        "alta",
                        "critica",
                    }:
                        st.info(
                            "📧 Envio reservado para "
                            "alertas altos e críticos."
                        )

                    elif st.button(
                        "📧 Enviar alerta por e-mail",
                        key=(
                            "send_llm_alert_email_"
                            f"{alerta_id}"
                        ),
                        use_container_width=True,
                        disabled=(
                            not pode_enviar_email
                        ),
                    ):
                        with st.spinner(
                            "Enviando alerta..."
                        ):
                            resultado_envio = (
                                notificar_alerta_email(
                                    alerta.to_dict()
                                )
                            )

                        if resultado_envio.get(
                            "enviado"
                        ):
                            st.success(
                                "Alerta enviado por e-mail."
                            )
                            st.rerun()

                        elif resultado_envio.get(
                            "duplicado"
                        ):
                            st.info(
                                "Este alerta já foi "
                                "enviado por e-mail."
                            )
                            st.rerun()

                        elif resultado_envio.get(
                            "ignorado"
                        ):
                            st.warning(
                                resultado_envio.get(
                                    "message",
                                    "O alerta não atende "
                                    "aos critérios de envio.",
                                )
                            )

                        else:
                            st.error(
                                "Falha ao enviar o alerta: "
                                + str(
                                    resultado_envio.get(
                                        "message",
                                        "erro desconhecido",
                                    )
                                )
                            )

                with coluna_resolver:
                    if st.button(
                        "✅ Marcar como resolvido",
                        key=(
                            f"resolve_llm_alert_"
                            f"{alerta_id}"
                        ),
                        use_container_width=True,
                    ):
                        resultado_resolucao = (
                            resolver_alerta_llm(
                                alerta_id,
                                resolvido_por=(
                                    "llm_cost_center"
                                ),
                            )
                        )

                        if resultado_resolucao.get(
                            "resolvido"
                        ):
                            st.success(
                                "Alerta resolvido."
                            )
                            st.rerun()
                        else:
                            st.info(
                                resultado_resolucao.get(
                                    "message",
                                    "O alerta já foi resolvido.",
                                )
                            )

    st.markdown(
        "### 🩺 Saúde das integrações"
    )

    try:
        try:
            from observability.resend_webhook import (
                carregar_saude_integracoes,
            )
        except ImportError:
            from src.observability.resend_webhook import (
                carregar_saude_integracoes,
            )

        saude = carregar_saude_integracoes()

        saude_col_1, saude_col_2, saude_col_3, saude_col_4 = (
            st.columns(4)
        )

        saude_col_1.metric(
            "Banco PostgreSQL",
            (
                "🟢 Conectado"
                if saude.get("banco_conectado")
                else "🔴 Indisponível"
            ),
        )

        saude_col_2.metric(
            "Resend",
            (
                "🟢 Configurado"
                if saude.get("resend_configurado")
                else "🔴 Não configurado"
            ),
        )

        saude_col_3.metric(
            "Webhook",
            (
                "🟢 Configurado"
                if saude.get("webhook_configurado")
                else "🔴 Não configurado"
            ),
        )

        saude_col_4.metric(
            "Alertas por e-mail",
            (
                "🟢 Habilitados"
                if saude.get(
                    "email_alertas_habilitado"
                )
                else "🟡 Desabilitados"
            ),
        )

        detalhe_1, detalhe_2, detalhe_3, detalhe_4 = (
            st.columns(4)
        )

        detalhe_1.metric(
            "Eventos nas últimas 24h",
            int(
                saude.get(
                    "eventos_webhook_24h",
                    0,
                )
                or 0
            ),
        )

        detalhe_2.metric(
            "Falhas de webhook em 24h",
            int(
                saude.get(
                    "falhas_webhook_24h",
                    0,
                )
                or 0
            ),
        )

        detalhe_3.metric(
            "E-mails entregues",
            int(
                saude.get(
                    "emails_entregues",
                    0,
                )
                or 0
            ),
        )

        detalhe_4.metric(
            "E-mails com falha",
            int(
                saude.get(
                    "emails_com_falha",
                    0,
                )
                or 0
            ),
        )

        with st.expander(
            "Detalhes técnicos das integrações",
            expanded=False,
        ):
            st.write(
                {
                    "Último evento": saude.get(
                        "ultimo_evento_tipo"
                    ),
                    "Evento recebido em": saude.get(
                        "ultimo_evento_recebido_em"
                    ),
                    "Evento processado": saude.get(
                        "ultimo_evento_processado"
                    ),
                    "Resultado": saude.get(
                        "ultimo_evento_resultado"
                    ),
                    "Último e-mail entregue em": (
                        saude.get(
                            "ultimo_email_entregue_em"
                        )
                    ),
                    "Destinatário configurado": (
                        saude.get(
                            "destinatario_configurado"
                        )
                    ),
                }
            )

        if not saude.get("ok"):
            st.warning(
                saude.get(
                    "message",
                    "Saúde parcialmente indisponível.",
                )
            )

    except Exception as exc:
        st.warning(
            "Não foi possível carregar a saúde "
            f"das integrações: {exc}"
        )

    st.markdown(
        "### Auditoria das notificações"
    )

    if not resultado_notificacoes.get("ok"):
        st.error(
            resultado_notificacoes.get(
                "message",
                "Não foi possível carregar "
                "as notificações.",
            )
        )

    elif (
        notificacoes_df is None
        or notificacoes_df.empty
    ):
        st.info(
            "Nenhuma notificação registrada."
        )

    else:
        auditoria_df = notificacoes_df.copy()

        auditoria_df["status_entrega"] = (
            auditoria_df["status_entrega"]
            .fillna("aguardando")
            .astype(str)
            .str.lower()
        )

        total_notificacoes = len(auditoria_df)

        total_enviadas = int(
            auditoria_df["status"]
            .astype(str)
            .str.lower()
            .eq("enviado")
            .sum()
        )

        total_entregues = int(
            auditoria_df["status_entrega"]
            .eq("entregue")
            .sum()
        )

        status_falha = {
            "falhou",
            "devolvido",
            "suprimido",
            "reclamacao",
        }

        total_falhas = int(
            auditoria_df["status_entrega"]
            .isin(status_falha)
            .sum()
        )

        total_aguardando = max(
            total_enviadas
            - total_entregues
            - total_falhas,
            0,
        )

        taxa_entrega = (
            total_entregues
            / total_enviadas
            * 100
            if total_enviadas
            else 0
        )

        metrica_1, metrica_2, metrica_3, metrica_4, metrica_5 = (
            st.columns(5)
        )

        metrica_1.metric(
            "Notificações",
            total_notificacoes,
        )

        metrica_2.metric(
            "Enviadas",
            total_enviadas,
        )

        metrica_3.metric(
            "Entregues",
            total_entregues,
        )

        metrica_4.metric(
            "Aguardando",
            total_aguardando,
        )

        metrica_5.metric(
            "Taxa de entrega",
            f"{taxa_entrega:.1f}%",
        )

        filtro_1, filtro_2 = st.columns(2)

        opcoes_status = [
            "todos",
            *sorted(
                auditoria_df[
                    "status_entrega"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
        ]

        filtro_status_entrega = filtro_1.selectbox(
            "Status de entrega",
            options=opcoes_status,
            key="llm_notification_delivery_status",
        )

        filtro_destinatario = filtro_2.text_input(
            "Filtrar destinatário",
            key="llm_notification_recipient_filter",
        )

        filtrado_notificacoes = auditoria_df.copy()

        if filtro_status_entrega != "todos":
            filtrado_notificacoes = (
                filtrado_notificacoes[
                    filtrado_notificacoes[
                        "status_entrega"
                    ]
                    == filtro_status_entrega
                ]
            )

        if filtro_destinatario.strip():
            filtrado_notificacoes = (
                filtrado_notificacoes[
                    filtrado_notificacoes[
                        "destinatario_mascarado"
                    ]
                    .astype(str)
                    .str.contains(
                        filtro_destinatario.strip(),
                        case=False,
                        na=False,
                    )
                ]
            )

        icones_status = {
            "entregue": "🟢 Entregue",
            "enviado": "🔵 Enviado",
            "aguardando": "⚪ Aguardando",
            "atrasado": "🟡 Atrasado",
            "falhou": "🔴 Falhou",
            "devolvido": "🟠 Devolvido",
            "suprimido": "🟣 Suprimido",
            "reclamacao": "🔴 Reclamação",
            "aberto_email": "📬 Aberto",
            "clicado": "🔗 Clicado",
        }

        filtrado_notificacoes[
            "status_entrega_exibicao"
        ] = (
            filtrado_notificacoes[
                "status_entrega"
            ]
            .map(icones_status)
            .fillna(
                filtrado_notificacoes[
                    "status_entrega"
                ]
            )
        )

        colunas_notificacoes = [
            "id",
            "alerta_id",
            "status",
            "status_entrega_exibicao",
            "evento_provider",
            "destinatario_mascarado",
            "assunto",
            "tentativas",
            "provider_message_id",
            "criado_em",
            "enviado_em",
            "entregue_em",
            "devolvido_em",
            "webhook_recebido_em",
            "motivo_entrega",
            "erro_tipo",
            "erro_mensagem",
        ]

        colunas_notificacoes = [
            coluna
            for coluna in colunas_notificacoes
            if coluna
            in filtrado_notificacoes.columns
        ]

        tabela_notificacoes = (
            filtrado_notificacoes[
                colunas_notificacoes
            ].copy()
        )

        tabela_notificacoes = (
            tabela_notificacoes.rename(
                columns={
                    "id": "ID",
                    "alerta_id": "Alerta",
                    "status": "Status do envio",
                    "status_entrega_exibicao": (
                        "Status da entrega"
                    ),
                    "evento_provider": (
                        "Evento do Resend"
                    ),
                    "destinatario_mascarado": (
                        "Destinatário"
                    ),
                    "assunto": "Assunto",
                    "tentativas": "Tentativas",
                    "provider_message_id": (
                        "Message ID"
                    ),
                    "criado_em": "Criado em",
                    "enviado_em": "Enviado em",
                    "entregue_em": "Entregue em",
                    "devolvido_em": "Devolvido em",
                    "webhook_recebido_em": (
                        "Webhook recebido em"
                    ),
                    "motivo_entrega": (
                        "Motivo da entrega/falha"
                    ),
                    "erro_tipo": "Tipo do erro",
                    "erro_mensagem": (
                        "Mensagem de erro"
                    ),
                }
            )
        )

        st.dataframe(
            tabela_notificacoes,
            use_container_width=True,
            hide_index=True,
        )

        csv_notificacoes = (
            tabela_notificacoes.to_csv(
                index=False
            ).encode("utf-8-sig")
        )

        st.download_button(
            "⬇️ Exportar notificações em CSV",
            data=csv_notificacoes,
            file_name=(
                "inna_llm_notificacoes.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key="llm_notification_download",
        )

    st.markdown(
        "### Auditoria dos alertas"
    )

    colunas = [
        "id",
        "criado_em",
        "atualizado_em",
        "codigo",
        "titulo",
        "categoria",
        "severidade",
        "status",
        "valor_atual",
        "valor_limite",
        "unidade",
        "modelo",
        "operacao",
        "resolvido_em",
        "resolvido_por",
    ]

    colunas = [
        coluna
        for coluna in colunas
        if coluna in alertas.columns
    ]

    tabela = alertas[
        colunas
    ].copy()

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    csv = tabela.to_csv(
        index=False,
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        "⬇️ Exportar alertas em CSV",
        data=csv,
        file_name="inna_llm_alertas.csv",
        mime="text/csv",
        use_container_width=True,
        key="llm_alert_download",
    )


def render_llm_costs_page() -> None:
    """
    Renderiza o LLM Cost Center.
    """
    try:
        from observability.llm_costs import (
            carregar_consumo_llm,
        )
    except ImportError:
        from src.observability.llm_costs import (
            carregar_consumo_llm,
        )

    st.title(
        "💰 LLM Cost Center"
    )

    st.caption(
        "Tokens, custos estimados, duração, modelos e "
        "operações das chamadas de IA da INNA."
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1, 1, 2]
        )
    )

    periodo_label = controle_1.selectbox(
        "Período",
        options=[
            "1 dia",
            "7 dias",
            "30 dias",
            "90 dias",
            "Todo o histórico",
        ],
        index=2,
        key="llm_cost_period",
    )

    limite = controle_2.selectbox(
        "Limite de eventos",
        options=[
            100,
            250,
            500,
            1000,
            5000,
        ],
        index=3,
        key="llm_cost_limit",
    )

    with controle_3:
        st.write("")

        if st.button(
            "🔄 Atualizar consumo",
            use_container_width=True,
            key="llm_cost_refresh",
        ):
            st.rerun()

    periodos = {
        "1 dia": 1,
        "7 dias": 7,
        "30 dias": 30,
        "90 dias": 90,
        "Todo o histórico": None,
    }

    resultado = carregar_consumo_llm(
        limite=int(limite),
        dias=periodos[periodo_label],
    )

    if not resultado.get("ok"):
        st.error(
            resultado.get(
                "message",
                "Não foi possível carregar o consumo.",
            )
        )
        return

    base = preparar_consumo_exibicao(
        resultado.get("df")
    )

    if base.empty:
        st.info(
            "Nenhum evento de consumo de LLM foi "
            "encontrado no período."
        )
        return

    modelos = sorted(
        base["modelo"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    operacoes = sorted(
        base["operacao"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    filtro_1, filtro_2 = st.columns(2)

    modelos_escolhidos = filtro_1.multiselect(
        "Modelos",
        options=modelos,
        default=modelos,
        key="llm_cost_models",
    )

    operacoes_escolhidas = filtro_2.multiselect(
        "Operações",
        options=operacoes,
        default=operacoes,
        key="llm_cost_operations",
    )

    filtrado = base[
        base["modelo"].isin(
            modelos_escolhidos
        )
        & base["operacao"].isin(
            operacoes_escolhidas
        )
    ].copy()

    resumo = resumir_consumo_llm(
        filtrado
    )

    st.markdown(
        "## Visão geral"
    )

    linha_1 = st.columns(5)

    linha_1[0].metric(
        "Chamadas",
        resumo["eventos"],
    )

    linha_1[1].metric(
        "Tokens totais",
        f"{resumo['tokens_totais']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[2].metric(
        "Tokens de entrada",
        f"{resumo['tokens_entrada']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[3].metric(
        "Tokens de saída",
        f"{resumo['tokens_saida']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[4].metric(
        "Custo estimado",
        (
            f"US$ "
            f"{resumo['custo_total_usd']:.6f}"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        "Taxa de sucesso",
        f"{resumo['taxa_sucesso']:.2f}%",
    )

    linha_2[1].metric(
        "Duração média",
        (
            f"{resumo['duracao_media_ms'] / 1000:.2f} s"
        ),
    )

    linha_2[2].metric(
        "P95",
        (
            f"{resumo['duracao_p95_ms'] / 1000:.2f} s"
        ),
    )

    chamadas_lentas = int(
        (
            filtrado["duracao_ms"]
            >= 30000
        ).sum()
    )

    linha_2[3].metric(
        "Chamadas acima de 30 s",
        chamadas_lentas,
    )

    if resumo["custo_total_usd"] == 0:
        st.warning(
            "Os preços dos modelos ainda não foram "
            "configurados. Tokens e duração estão sendo "
            "registrados, mas o custo permanece zerado."
        )

    if chamadas_lentas > 0:
        st.warning(
            f"Foram encontradas {chamadas_lentas} "
            "chamada(s) com duração igual ou superior "
            "a 30 segundos."
        )

    st.divider()
    st.markdown(
        "## 📊 FinOps e orçamento"
    )

    try:
        from observability.llm_finops import (
            analisar_finops_llm,
        )
    except ImportError:
        from src.observability.llm_finops import (
            analisar_finops_llm,
        )

    finops = analisar_finops_llm(
        filtrado
    )

    config_finops = finops[
        "configuracao"
    ]

    situacao = finops[
        "situacao_orcamento"
    ]

    situacao_projecao = finops[
        "situacao_projecao"
    ]

    finops_cols = st.columns(5)

    finops_cols[0].metric(
        "Custo acumulado em R$",
        (
            f"R$ "
            f"{finops['custo_acumulado_brl']:.4f}"
        ),
    )

    finops_cols[1].metric(
        "Custo médio/chamada",
        (
            f"R$ "
            f"{finops['custo_medio_chamada_brl']:.4f}"
        ),
    )

    finops_cols[2].metric(
        "Projeção mensal",
        (
            f"R$ "
            f"{finops['projecao_mensal_brl']:.2f}"
        ),
    )

    finops_cols[3].metric(
        "Orçamento mensal",
        (
            f"R$ "
            f"{config_finops['orcamento_mensal_brl']:.2f}"
        ),
    )

    finops_cols[4].metric(
        "Uso do orçamento",
        (
            f"{situacao['percentual_utilizado']:.2f}%"
        ),
    )

    percentual_barra = max(
        0.0,
        min(
            situacao[
                "percentual_utilizado"
            ] / 100,
            1.0,
        ),
    )

    st.progress(
        percentual_barra
    )

    mensagem_orcamento = (
        f"{situacao['icone']} "
        f"{situacao['classificacao']}. "
        f"Saldo estimado: US$ "
        f"{situacao['saldo']:.4f}."
    )

    if situacao["status"] in {
        "critico",
        "excedido",
    }:
        st.error(
            mensagem_orcamento
        )

    elif situacao["status"] == "alerta":
        st.warning(
            mensagem_orcamento
        )

    else:
        st.success(
            mensagem_orcamento
        )

    if situacao_projecao["status"] in {
        "critico",
        "excedido",
    }:
        st.warning(
            "A projeção para o final do mês pode "
            "ultrapassar ou se aproximar do orçamento."
        )

    with st.expander(
        "Recomendações FinOps",
        expanded=False,
    ):
        for recomendacao in finops[
            "recomendacoes"
        ]:
            st.markdown(
                f"- {recomendacao}"
            )

        st.caption(
            "A conversão utiliza a cotação configurada "
            f"de R$ {config_finops['cotacao_usd_brl']:.4f} "
            "por US$ 1."
        )

    render_alertas_llm_section(
        base_consumo=filtrado,
        finops=finops,
    )

    st.divider()
    st.markdown(
        "## Consumo por modelo"
    )

    por_modelo = (
        filtrado.groupby(
            "modelo",
            as_index=False,
        )
        .agg(
            Chamadas=("id", "count"),
            Tokens=("tokens_totais", "sum"),
            Custo_USD=(
                "custo_total_usd",
                "sum",
            ),
            Duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
        )
    )

    por_modelo[
        "Duração média (s)"
    ] = (
        por_modelo[
            "Duracao_media_ms"
        ]
        / 1000
    ).round(2)

    st.dataframe(
        por_modelo[
            [
                "modelo",
                "Chamadas",
                "Tokens",
                "Custo_USD",
                "Duração média (s)",
            ]
        ].rename(
            columns={
                "modelo": "Modelo",
                "Custo_USD": "Custo (USD)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        por_modelo.set_index(
            "modelo"
        )[["Tokens"]],
        use_container_width=True,
    )

    st.markdown(
        "## Consumo por operação"
    )

    por_operacao = (
        filtrado.groupby(
            "operacao",
            as_index=False,
        )
        .agg(
            Chamadas=("id", "count"),
            Tokens=("tokens_totais", "sum"),
            Custo_USD=(
                "custo_total_usd",
                "sum",
            ),
            Duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
        )
    )

    por_operacao[
        "Duração média (s)"
    ] = (
        por_operacao[
            "Duracao_media_ms"
        ]
        / 1000
    ).round(2)

    st.dataframe(
        por_operacao[
            [
                "operacao",
                "Chamadas",
                "Tokens",
                "Custo_USD",
                "Duração média (s)",
            ]
        ].rename(
            columns={
                "operacao": "Operação",
                "Custo_USD": "Custo (USD)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown(
        "## Evolução temporal"
    )

    temporal = filtrado.copy()

    temporal["data"] = (
        temporal["criado_em"]
        .dt.floor("h")
    )

    serie_tokens = (
        temporal.groupby(
            "data",
            as_index=False,
        )["tokens_totais"]
        .sum()
        .rename(
            columns={
                "data": "Data",
                "tokens_totais": "Tokens",
            }
        )
        .set_index("Data")
    )

    st.markdown(
        "### Tokens por hora"
    )

    st.line_chart(
        serie_tokens,
        use_container_width=True,
    )

    serie_duracao = (
        temporal.groupby(
            "data",
            as_index=False,
        )["duracao_ms"]
        .mean()
    )

    serie_duracao[
        "Duração média (s)"
    ] = (
        serie_duracao[
            "duracao_ms"
        ]
        / 1000
    )

    serie_duracao = (
        serie_duracao[
            [
                "data",
                "Duração média (s)",
            ]
        ]
        .rename(
            columns={
                "data": "Data",
            }
        )
        .set_index("Data")
    )

    st.markdown(
        "### Duração média por hora"
    )

    st.line_chart(
        serie_duracao,
        use_container_width=True,
    )

    st.divider()
    st.markdown(
        "## Auditoria das chamadas"
    )

    tabela = filtrado[
        [
            "id",
            "criado_em",
            "provider",
            "modelo",
            "operacao",
            "origem",
            "usuario_id",
            "trace_id",
            "tokens_entrada",
            "tokens_saida",
            "tokens_totais",
            "custo_total_usd",
            "duracao_ms",
            "sucesso",
            "erro_tipo",
        ]
    ].copy()

    tabela[
        "duracao_segundos"
    ] = (
        tabela["duracao_ms"]
        / 1000
    ).round(3)

    tabela = tabela.drop(
        columns=["duracao_ms"]
    ).sort_values(
        "criado_em",
        ascending=False,
    )

    tabela = tabela.rename(
        columns={
            "id": "ID",
            "criado_em": "Data",
            "provider": "Provider",
            "modelo": "Modelo",
            "operacao": "Operação",
            "origem": "Origem",
            "usuario_id": "Usuário",
            "trace_id": "Trace",
            "tokens_entrada": "Tokens entrada",
            "tokens_saida": "Tokens saída",
            "tokens_totais": "Tokens totais",
            "custo_total_usd": "Custo USD",
            "sucesso": "Sucesso",
            "erro_tipo": "Tipo do erro",
            "duracao_segundos": "Duração (s)",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    csv = tabela.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        "⬇️ Exportar consumo em CSV",
        data=csv,
        file_name="inna_llm_consumo.csv",
        mime="text/csv",
        use_container_width=True,
        key="llm_cost_download",
    )

    with st.expander(
        "🔒 Privacidade da telemetria",
        expanded=False,
    ):
        st.markdown(
            """
A telemetria registra apenas informações técnicas:

- modelo;
- quantidade de tokens;
- duração;
- operação;
- sucesso ou falha;
- custo estimado;
- identificadores técnicos opcionais.

O prompt, a pergunta do usuário e a resposta do Gemini
não são armazenados nesta tabela.
"""
        )


__all__ = [
    "render_alertas_llm_section",
    "preparar_consumo_exibicao",
    "resumir_consumo_llm",
    "render_llm_costs_page",
]

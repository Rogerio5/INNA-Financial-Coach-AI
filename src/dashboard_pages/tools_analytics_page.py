"""
Página de Analytics Avançado das Tools da INNA.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def formatar_delta_percentual(
    valor: float,
) -> str:
    """
    Formata variação percentual para exibição.
    """
    return f"{float(valor):+.2f}%"


def preparar_ranking_exibicao(
    ranking: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Converte nomes técnicos em nomes amigáveis.
    """
    if ranking is None or ranking.empty:
        return pd.DataFrame()

    tabela = ranking.copy()

    colunas = {
        "ferramenta": "Ferramenta",
        "execucoes": "Execuções",
        "sucessos": "Sucessos",
        "falhas": "Falhas",
        "taxa_sucesso_percentual": "Taxa de sucesso (%)",
        "confianca_media_percentual": "Confiança média (%)",
        "duracao_media_ms": "Média (ms)",
        "duracao_minima_ms": "Mínimo (ms)",
        "duracao_maxima_ms": "Máximo (ms)",
        "p50_ms": "P50 (ms)",
        "p95_ms": "P95 (ms)",
        "p99_ms": "P99 (ms)",
    }

    existentes = {
        coluna: nome
        for coluna, nome in colunas.items()
        if coluna in tabela.columns
    }

    return tabela[list(existentes)].rename(
        columns=existentes
    )


def render_comparacao_periodos(
    comparacao: dict[str, Any],
) -> None:
    """
    Exibe o período atual versus o anterior.
    """
    atual = comparacao.get(
        "periodo_atual",
        {},
    )

    anterior = comparacao.get(
        "periodo_anterior",
        {},
    )

    st.markdown(
        "## Comparação entre períodos"
    )

    col_1, col_2, col_3 = st.columns(3)

    col_1.metric(
        "Execuções",
        atual.get("execucoes", 0),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_execucoes_percentual",
                0,
            )
        ),
    )

    col_2.metric(
        "Falhas",
        atual.get("falhas", 0),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_falhas_percentual",
                0,
            )
        ),
        delta_color="inverse",
    )

    col_3.metric(
        "Duração média",
        (
            f"{float(
                atual.get(
                    'duracao_media_ms',
                    0,
                )
            ):.3f} ms"
        ),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_duracao_percentual",
                0,
            )
        ),
        delta_color="inverse",
    )

    with st.expander(
        "Ver comparação detalhada",
        expanded=False,
    ):
        tabela = pd.DataFrame([
            {
                "Período": "Atual",
                "Execuções": atual.get(
                    "execucoes",
                    0,
                ),
                "Falhas": atual.get(
                    "falhas",
                    0,
                ),
                "Duração média (ms)": atual.get(
                    "duracao_media_ms",
                    0,
                ),
            },
            {
                "Período": "Anterior",
                "Execuções": anterior.get(
                    "execucoes",
                    0,
                ),
                "Falhas": anterior.get(
                    "falhas",
                    0,
                ),
                "Duração média (ms)": anterior.get(
                    "duracao_media_ms",
                    0,
                ),
            },
        ])

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
        )


def render_anomalias_operacionais(
    resultado: dict[str, Any],
) -> None:
    """
    Renderiza alertas e métricas de anomalias.
    """
    st.markdown(
        "## 🚨 Detecção de anomalias"
    )

    if not resultado.get("tem_dados"):
        st.info(
            "Ainda não existem dados suficientes para "
            "detectar anomalias operacionais."
        )
        return

    anomalias = resultado.get(
        "anomalias",
        [],
    )

    total = int(
        resultado.get(
            "total_anomalias",
            0,
        )
    )

    maior_severidade = (
        resultado.get(
            "maior_severidade"
        )
        or "nenhuma"
    )

    atual = resultado.get(
        "periodo_atual",
        {},
    )

    base = resultado.get(
        "linha_base",
        {},
    )

    linha_1 = st.columns(4)

    linha_1[0].metric(
        "Anomalias detectadas",
        total,
    )

    linha_1[1].metric(
        "Maior severidade",
        maior_severidade.title(),
    )

    linha_1[2].metric(
        "Falhas no período atual",
        int(
            atual.get(
                "falhas",
                0,
            )
        ),
    )

    linha_1[3].metric(
        "P95 atual",
        (
            f"{float(
                atual.get(
                    'duracao_p95_ms',
                    0,
                )
            ):.3f} ms"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        "Taxa de falhas atual",
        (
            f"{float(
                atual.get(
                    'taxa_falhas_percentual',
                    0,
                )
            ):.2f}%"
        ),
    )

    linha_2[1].metric(
        "Taxa de falhas base",
        (
            f"{float(
                base.get(
                    'taxa_falhas_percentual',
                    0,
                )
            ):.2f}%"
        ),
    )

    linha_2[2].metric(
        "Confiança atual",
        (
            f"{float(
                atual.get(
                    'confianca_media_percentual',
                    0,
                )
            ):.2f}%"
        ),
    )

    linha_2[3].metric(
        "Confiança base",
        (
            f"{float(
                base.get(
                    'confianca_media_percentual',
                    0,
                )
            ):.2f}%"
        ),
    )

    if not anomalias:
        st.success(
            "Nenhuma anomalia operacional relevante foi "
            "detectada para as janelas analisadas."
        )
        return

    contagem_severidade = {
        "critica": 0,
        "alta": 0,
        "media": 0,
        "baixa": 0,
        "informativa": 0,
    }

    for item in anomalias:
        severidade = item.get(
            "severidade",
            "informativa",
        )

        contagem_severidade[
            severidade
        ] = (
            contagem_severidade.get(
                severidade,
                0,
            )
            + 1
        )

    st.markdown(
        "### Anomalias por severidade"
    )

    colunas = st.columns(5)

    colunas[0].metric(
        "Críticas",
        contagem_severidade["critica"],
    )

    colunas[1].metric(
        "Altas",
        contagem_severidade["alta"],
    )

    colunas[2].metric(
        "Médias",
        contagem_severidade["media"],
    )

    colunas[3].metric(
        "Baixas",
        contagem_severidade["baixa"],
    )

    colunas[4].metric(
        "Informativas",
        contagem_severidade[
            "informativa"
        ],
    )

    st.markdown(
        "### Alertas detectados"
    )

    for indice, item in enumerate(
        anomalias,
        start=1,
    ):
        severidade = item.get(
            "severidade",
            "informativa",
        )

        simbolo = {
            "critica": "🔴",
            "alta": "🟠",
            "media": "🟡",
            "baixa": "🔵",
            "informativa": "ℹ️",
        }.get(
            severidade,
            "ℹ️",
        )

        titulo = item.get(
            "titulo",
            "Anomalia",
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### {simbolo} {indice}. {titulo}"
            )

            col_1, col_2, col_3 = st.columns(
                [2, 1, 1]
            )

            col_1.markdown(
                item.get(
                    "descricao",
                    "",
                )
            )

            col_2.metric(
                "Valor atual",
                item.get(
                    "valor_atual",
                    0,
                ),
            )

            col_3.metric(
                "Referência",
                item.get(
                    "valor_referencia",
                    0,
                ),
            )

            st.caption(
                f"Severidade: "
                f"{severidade.title()} | "
                f"Métrica: "
                f"{item.get('metrica', '')}"
            )

            st.info(
                "Recomendação: "
                + str(
                    item.get(
                        "recomendacao",
                        "",
                    )
                )
            )

    outliers = resultado.get(
        "outliers_duracao"
    )

    if (
        outliers is not None
        and not outliers.empty
    ):
        st.markdown(
            "### Execuções fora do padrão"
        )

        tabela_outliers = (
            outliers.copy()
            .rename(
                columns={
                    "indice": "Índice do evento",
                    "valor": "Duração (ms)",
                    "score_robusto": (
                        "Modified Z-Score"
                    ),
                }
            )
        )

        st.dataframe(
            tabela_outliers,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander(
        "Como a detecção funciona",
        expanded=False,
    ):
        st.markdown(
            """
A INNA compara o período atual com uma linha de base anterior.

São analisados:

- taxa de falhas;
- confiança média do Router;
- P95 da duração;
- percentual de eventos sem Tool;
- volume médio por hora;
- execuções individuais fora do padrão.

Os outliers de duração usam **mediana e MAD**, uma abordagem
mais resistente a valores extremos do que média e desvio-padrão.
"""
        )


def render_tools_analytics_page() -> None:
    """
    Renderiza o Analytics Avançado das Tools.
    """
    try:
        from observability.analytics import (
            calcular_distribuicao_coluna,
            calcular_execucoes_sem_tool,
            calcular_ranking_tools,
            calcular_serie_temporal_analytics,
            comparar_periodos,
            preparar_eventos_analytics,
        )
        from tools.observability import (
            carregar_eventos_tools,
        )
    except ImportError:
        from src.observability.analytics import (
            calcular_distribuicao_coluna,
            calcular_execucoes_sem_tool,
            calcular_ranking_tools,
            calcular_serie_temporal_analytics,
            comparar_periodos,
            preparar_eventos_analytics,
        )
        from src.tools.observability import (
            carregar_eventos_tools,
        )

    st.title(
        "📊 Analytics Avançado das Tools"
    )

    st.caption(
        "Análise operacional de uso, confiança, "
        "performance, falhas e comportamento das "
        "ferramentas financeiras da INNA."
    )

    controle_1, controle_2, controle_3 = st.columns(
        [1, 1, 2]
    )

    limite = controle_1.selectbox(
        "Eventos carregados",
        options=[
            100,
            250,
            500,
            1000,
        ],
        index=1,
        key="tools_analytics_limit",
    )

    periodo_horas = controle_2.selectbox(
        "Janela de comparação",
        options=[
            24,
            48,
            72,
            168,
        ],
        index=0,
        format_func=lambda valor: (
            f"{valor} horas"
            if valor < 168
            else "7 dias"
        ),
        key="tools_analytics_period",
    )

    with controle_3:
        st.write("")

        if st.button(
            "🔄 Atualizar Analytics",
            use_container_width=True,
            key="tools_analytics_refresh",
        ):
            st.rerun()

    resultado = carregar_eventos_tools(
        limite=int(limite)
    )

    if not resultado.get("ok"):
        st.error(
            resultado.get(
                "message",
                "Não foi possível carregar eventos.",
            )
        )
        return

    df = resultado.get("df")

    if df is None or df.empty:
        st.info(
            "Ainda não existem eventos suficientes "
            "para análise."
        )
        return

    base = preparar_eventos_analytics(
        df
    )

    ranking = calcular_ranking_tools(
        base
    )

    sem_tool = calcular_execucoes_sem_tool(
        base
    )

    total_eventos = len(base)

    total_sucesso = int(
        base["sucesso"].sum()
        if "sucesso" in base.columns
        else 0
    )

    total_falhas = max(
        total_eventos - total_sucesso,
        0,
    )

    taxa_sucesso = (
        round(
            (
                total_sucesso
                / total_eventos
            )
            * 100,
            2,
        )
        if total_eventos
        else 0.0
    )

    confianca_media = (
        round(
            float(
                base["confianca"]
                .dropna()
                .mean()
            )
            * 100,
            2,
        )
        if (
            "confianca" in base.columns
            and base["confianca"].notna().any()
        )
        else 0.0
    )

    duracao_media = (
        round(
            float(
                base["duracao_ms"]
                .dropna()
                .mean()
            ),
            3,
        )
        if (
            "duracao_ms" in base.columns
            and base["duracao_ms"].notna().any()
        )
        else 0.0
    )

    try:
        from observability.narrative import (
            gerar_insights_operacionais,
            gerar_texto_narrativa,
        )
    except ImportError:
        from src.observability.narrative import (
            gerar_insights_operacionais,
            gerar_texto_narrativa,
        )

    insights = gerar_insights_operacionais(
        base,
        horas_comparacao=int(periodo_horas),
    )

    st.markdown(
        "## 🧠 Insights operacionais da INNA"
    )

    saude = insights.get(
        "saude",
        {},
    )

    col_saude_1, col_saude_2 = st.columns(
        [1, 3]
    )

    col_saude_1.metric(
        "Health Score",
        f"{saude.get('score', 0):.1f}/100",
    )

    col_saude_2.info(
        insights.get(
            "resumo_executivo",
            "Sem resumo disponível.",
        )
    )

    col_insight_1, col_insight_2 = st.columns(2)

    with col_insight_1:
        st.markdown(
            "### ✅ Destaques"
        )

        for item in insights.get(
            "destaques",
            [],
        ):
            st.success(item)

    with col_insight_2:
        st.markdown(
            "### ⚠️ Alertas"
        )

        alertas = insights.get(
            "alertas",
            [],
        )

        if alertas:
            for item in alertas:
                st.warning(item)
        else:
            st.success(
                "Nenhum alerta crítico detectado."
            )

    with st.expander(
        "🛠️ Recomendações técnicas",
        expanded=False,
    ):
        for item in insights.get(
            "recomendacoes",
            [],
        ):
            st.markdown(
                f"- {item}"
            )

    with st.expander(
        "📄 Ver narrativa completa",
        expanded=False,
    ):
        st.markdown(
            gerar_texto_narrativa(
                insights
            )
        )

    st.divider()

    try:
        from observability.anomalies import (
            detectar_anomalias_operacionais,
        )
    except ImportError:
        from src.observability.anomalies import (
            detectar_anomalias_operacionais,
        )

    resultado_anomalias = (
        detectar_anomalias_operacionais(
            base,
            horas_periodo_atual=int(
                periodo_horas
            ),
            horas_linha_base=168,
        )
    )

    render_anomalias_operacionais(
        resultado_anomalias
    )

    st.divider()

    st.markdown(
        "## Visão analítica"
    )

    linha_1 = st.columns(4)

    linha_1[0].metric(
        "Eventos analisados",
        total_eventos,
    )

    linha_1[1].metric(
        "Taxa de sucesso",
        f"{taxa_sucesso:.2f}%",
    )

    linha_1[2].metric(
        "Falhas",
        total_falhas,
    )

    linha_1[3].metric(
        "Execuções sem Tool",
        (
            f"{sem_tool['total']} "
            f"({sem_tool['percentual']:.2f}%)"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        "Confiança média",
        f"{confianca_media:.2f}%",
    )

    linha_2[1].metric(
        "Duração média",
        f"{duracao_media:.3f} ms",
    )

    linha_2[2].metric(
        "Tools distintas",
        (
            int(
                base["tool_exibicao"]
                .nunique()
            )
            if "tool_exibicao" in base.columns
            else 0
        ),
    )

    linha_2[3].metric(
        "Usuários únicos",
        (
            int(
                base["usuario_id"]
                .dropna()
                .nunique()
            )
            if "usuario_id" in base.columns
            else 0
        ),
    )

    comparacao = comparar_periodos(
        base,
        horas=int(periodo_horas),
    )

    render_comparacao_periodos(
        comparacao
    )

    st.divider()
    st.markdown(
        "## Ranking e performance das Tools"
    )

    ranking_exibicao = preparar_ranking_exibicao(
        ranking
    )

    if ranking_exibicao.empty:
        st.info(
            "Nenhuma Tool encontrada."
        )
    else:
        st.dataframe(
            ranking_exibicao,
            use_container_width=True,
            hide_index=True,
        )

        col_grafico_1, col_grafico_2 = st.columns(2)

        with col_grafico_1:
            st.markdown(
                "### Uso por Tool"
            )

            st.bar_chart(
                ranking.set_index(
                    "ferramenta"
                )[["execucoes"]],
                use_container_width=True,
            )

        with col_grafico_2:
            st.markdown(
                "### P95 por Tool"
            )

            st.bar_chart(
                ranking.set_index(
                    "ferramenta"
                )[["p95_ms"]],
                use_container_width=True,
            )

    st.divider()
    st.markdown(
        "## Distribuições"
    )

    col_dist_1, col_dist_2 = st.columns(2)

    distribuicao_intencoes = (
        calcular_distribuicao_coluna(
            base,
            "intencao",
        )
    )

    distribuicao_origens = (
        calcular_distribuicao_coluna(
            base,
            "origem",
        )
    )

    with col_dist_1:
        st.markdown(
            "### Intenções"
        )

        if not distribuicao_intencoes.empty:
            st.dataframe(
                distribuicao_intencoes,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                distribuicao_intencoes.set_index(
                    "intencao"
                )[["total"]],
                use_container_width=True,
            )

    with col_dist_2:
        st.markdown(
            "### Origens"
        )

        if not distribuicao_origens.empty:
            st.dataframe(
                distribuicao_origens,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                distribuicao_origens.set_index(
                    "origem"
                )[["total"]],
                use_container_width=True,
            )

    st.divider()
    st.markdown(
        "## Evolução temporal"
    )

    frequencia_label = st.radio(
        "Agrupamento",
        options=[
            "Hora",
            "Dia",
            "Semana",
            "Mês",
        ],
        horizontal=True,
        key="tools_analytics_frequency",
    )

    mapa_frequencia = {
        "Hora": "h",
        "Dia": "D",
        "Semana": "W",
        "Mês": "ME",
    }

    serie = calcular_serie_temporal_analytics(
        base,
        mapa_frequencia[
            frequencia_label
        ],
    )

    if serie.empty:
        st.info(
            "Não há eventos suficientes para "
            "a série temporal."
        )
    else:
        serie_grafico = serie.copy()

        serie_grafico["Período"] = (
            pd.to_datetime(
                serie_grafico["criado_em"],
                errors="coerce",
            )
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        st.line_chart(
            serie_grafico.set_index(
                "Período"
            )[
                [
                    "execucoes",
                    "sucessos",
                    "falhas",
                ]
            ],
            use_container_width=True,
        )

        st.dataframe(
            serie_grafico,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown(
        "## Usuários mais ativos"
    )

    usuarios = (
        base["usuario_id"]
        .fillna("sem_usuario")
        .value_counts()
        .rename_axis("Usuário")
        .reset_index(name="Execuções")
    )

    st.bar_chart(
        usuarios.set_index(
            "Usuário"
        ),
        use_container_width=True,
    )

    st.dataframe(
        usuarios,
        use_container_width=True,
        hide_index=True,
    )


__all__ = [
    "formatar_delta_percentual",
    "preparar_ranking_exibicao",
    "render_comparacao_periodos",
    "render_anomalias_operacionais",
    "render_tools_analytics_page",
]

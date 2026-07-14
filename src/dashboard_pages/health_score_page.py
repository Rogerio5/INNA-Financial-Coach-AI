"""
INNA Health Center.

Painel global da saúde operacional da aplicação.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


NOMES_COMPONENTES = {
    "tools": "Tools",
    "rag": "RAG",
    "memoria": "Memória",
    "infraestrutura": "Infraestrutura",
    "timeline": "Timeline",
    "performance": "Performance",
}


def preparar_componentes_exibicao(
    componentes: dict[str, Any],
) -> pd.DataFrame:
    """
    Converte componentes do Health Score em tabela.
    """
    linhas = []

    for nome, item in componentes.items():
        linhas.append({
            "Componente": NOMES_COMPONENTES.get(
                nome,
                nome.title(),
            ),
            "Score": float(
                item.get(
                    "score",
                    0,
                )
            ),
            "Peso (%)": round(
                float(
                    item.get(
                        "peso",
                        0,
                    )
                )
                * 100,
                1,
            ),
            "Contribuição": float(
                item.get(
                    "contribuicao",
                    0,
                )
            ),
            "Classificação": (
                item.get(
                    "classificacao",
                    ""
                )
            ),
            "Status": (
                f"{item.get('icone', '')} "
                f"{item.get('status', '')}"
            ),
        })

    return pd.DataFrame(linhas)


def preparar_historico_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara o histórico para gráficos e tabelas.
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
        "score_global",
        "score_tools",
        "score_rag",
        "score_memoria",
        "score_infraestrutura",
        "score_timeline",
        "score_performance",
    ]

    for coluna in colunas_numericas:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(
                base[coluna],
                errors="coerce",
            )

    base = (
        base.dropna(
            subset=["criado_em"]
        )
        .sort_values(
            "criado_em",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    return base


def render_health_history_section(
    *,
    resultado_atual: dict[str, Any],
) -> None:
    """
    Renderiza persistência, tendência e histórico.
    """
    try:
        from observability.health_history import (
            calcular_tendencia_health,
            carregar_health_history,
            salvar_health_snapshot,
        )
    except ImportError:
        from src.observability.health_history import (
            calcular_tendencia_health,
            carregar_health_history,
            salvar_health_snapshot,
        )

    st.divider()
    st.markdown(
        "## 📈 Histórico do Health Score"
    )

    st.caption(
        "Acompanhe a evolução da saúde operacional "
        "da INNA ao longo do tempo."
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1.2, 1.2, 2]
        )
    )

    periodo_label = controle_1.selectbox(
        "Período histórico",
        options=[
            "7 dias",
            "30 dias",
            "90 dias",
            "Todo o histórico",
        ],
        index=1,
        key="health_history_period",
    )

    limite = controle_2.selectbox(
        "Limite de snapshots",
        options=[
            50,
            100,
            250,
            500,
        ],
        index=1,
        key="health_history_limit",
    )

    dias_por_periodo = {
        "7 dias": 7,
        "30 dias": 30,
        "90 dias": 90,
        "Todo o histórico": None,
    }

    with controle_3:
        st.write("")

        salvar = st.button(
            "💾 Salvar snapshot atual",
            use_container_width=True,
            key="health_save_snapshot",
        )

    if salvar:
        resultado_salvar = (
            salvar_health_snapshot(
                resultado_atual,
                origem="health_center",
                evitar_duplicado_minutos=5,
            )
        )

        if not resultado_salvar.get("ok"):
            st.error(
                resultado_salvar.get(
                    "message",
                    "Não foi possível salvar o snapshot.",
                )
            )

        elif resultado_salvar.get("duplicado"):
            st.info(
                "Um snapshot com o mesmo score já foi "
                "salvo nos últimos cinco minutos."
            )

        elif resultado_salvar.get("salvo"):
            st.success(
                "Snapshot salvo no PostgreSQL/Neon."
            )

    historico_resultado = (
        carregar_health_history(
            limite=int(limite),
            dias=dias_por_periodo[
                periodo_label
            ],
        )
    )

    if not historico_resultado.get("ok"):
        st.error(
            historico_resultado.get(
                "message",
                "Não foi possível carregar o histórico.",
            )
        )
        return

    historico = preparar_historico_exibicao(
        historico_resultado.get("df")
    )

    if historico.empty:
        st.info(
            "Nenhum snapshot foi encontrado para o "
            "período selecionado."
        )
        return

    tendencia = calcular_tendencia_health(
        historico
    )

    snapshot_atual = historico.iloc[-1]

    snapshot_anterior = (
        historico.iloc[-2]
        if len(historico) >= 2
        else None
    )

    delta_global = None

    if snapshot_anterior is not None:
        delta_global = (
            float(
                snapshot_atual[
                    "score_global"
                ]
            )
            - float(
                snapshot_anterior[
                    "score_global"
                ]
            )
        )

    metricas = st.columns(4)

    metricas[0].metric(
        "Snapshots",
        len(historico),
    )

    metricas[1].metric(
        "Último score",
        (
            f"{float(
                snapshot_atual[
                    'score_global'
                ]
            ):.1f}/100"
        ),
        delta=(
            f"{delta_global:+.1f}"
            if delta_global is not None
            else None
        ),
    )

    metricas[2].metric(
        "Melhor score",
        (
            f"{float(
                historico[
                    'score_global'
                ].max()
            ):.1f}/100"
        ),
    )

    metricas[3].metric(
        "Média do período",
        (
            f"{float(
                historico[
                    'score_global'
                ].mean()
            ):.1f}/100"
        ),
    )

    if tendencia.get("tem_comparacao"):
        direcao = tendencia.get(
            "direcao"
        )

        mensagem = (
            f"{tendencia.get('icone', '')} "
            f"{tendencia.get('mensagem', '')}"
        )

        if direcao == "melhora":
            st.success(mensagem)

        elif direcao == "piora":
            st.warning(mensagem)

        else:
            st.info(mensagem)

    else:
        st.info(
            tendencia.get(
                "mensagem",
                "É necessário salvar pelo menos dois "
                "snapshots para calcular a tendência.",
            )
        )

    st.markdown(
        "### Evolução do score global"
    )

    grafico_global = (
        historico[
            [
                "criado_em",
                "score_global",
            ]
        ]
        .rename(
            columns={
                "criado_em": "Data",
                "score_global": (
                    "Health Score"
                ),
            }
        )
        .set_index("Data")
    )

    st.line_chart(
        grafico_global,
        use_container_width=True,
    )

    st.markdown(
        "### Evolução por componente"
    )

    colunas_componentes = {
        "score_tools": "Tools",
        "score_rag": "RAG",
        "score_memoria": "Memória",
        "score_infraestrutura": (
            "Infraestrutura"
        ),
        "score_timeline": "Timeline",
        "score_performance": "Performance",
    }

    colunas_disponiveis = [
        coluna
        for coluna in colunas_componentes
        if coluna in historico.columns
    ]

    if colunas_disponiveis:
        grafico_componentes = (
            historico[
                [
                    "criado_em",
                    *colunas_disponiveis,
                ]
            ]
            .rename(
                columns={
                    "criado_em": "Data",
                    **colunas_componentes,
                }
            )
            .set_index("Data")
        )

        st.line_chart(
            grafico_componentes,
            use_container_width=True,
        )

    st.markdown(
        "### Auditoria dos snapshots"
    )

    tabela_colunas = [
        "id",
        "criado_em",
        "score_global",
        "score_tools",
        "score_rag",
        "score_memoria",
        "score_infraestrutura",
        "score_timeline",
        "score_performance",
        "classificacao",
        "componente_mais_fraco",
        "total_anomalias",
        "origem",
    ]

    tabela_colunas = [
        coluna
        for coluna in tabela_colunas
        if coluna in historico.columns
    ]

    tabela = (
        historico[
            tabela_colunas
        ]
        .sort_values(
            "criado_em",
            ascending=False,
        )
        .rename(
            columns={
                "id": "ID",
                "criado_em": "Data",
                "score_global": "Global",
                "score_tools": "Tools",
                "score_rag": "RAG",
                "score_memoria": "Memória",
                "score_infraestrutura": (
                    "Infraestrutura"
                ),
                "score_timeline": "Timeline",
                "score_performance": (
                    "Performance"
                ),
                "classificacao": (
                    "Classificação"
                ),
                "componente_mais_fraco": (
                    "Componente prioritário"
                ),
                "total_anomalias": (
                    "Anomalias"
                ),
                "origem": "Origem",
            }
        )
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
        "⬇️ Exportar histórico em CSV",
        data=csv,
        file_name=(
            "inna_health_score_history.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key="health_history_download",
    )


def render_health_score_page() -> None:
    """
    Renderiza o Health Center.
    """
    try:
        from observability.health_runtime import (
            coletar_health_score_real,
        )
    except ImportError:
        from src.observability.health_runtime import (
            coletar_health_score_real,
        )

    st.title(
        "❤️ INNA Health Center"
    )

    st.caption(
        "Saúde consolidada das Tools, RAG, memória, "
        "infraestrutura, Timeline e performance."
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1, 1, 2]
        )
    )

    limite_eventos = controle_1.selectbox(
        "Eventos das Tools",
        options=[
            100,
            250,
            500,
            1000,
        ],
        index=1,
        key="health_tools_limit",
    )

    limite_traces = controle_2.selectbox(
        "Traces analisados",
        options=[
            10,
            25,
            50,
            100,
        ],
        index=2,
        key="health_traces_limit",
    )

    with controle_3:
        st.write("")

        if st.button(
            "🔄 Atualizar Health Score",
            use_container_width=True,
            key="health_refresh",
        ):
            st.rerun()

    resultado = coletar_health_score_real(
        limite_eventos_tools=int(
            limite_eventos
        ),
        limite_traces=int(
            limite_traces
        ),
    )

    health = resultado.get(
        "health",
        {}
    )

    score_global = float(
        health.get(
            "score_global",
            0,
        )
    )

    classificacao = health.get(
        "classificacao",
        "Sem dados",
    )

    icone = health.get(
        "icone",
        "⚪",
    )

    st.markdown(
        "## Saúde global"
    )

    col_1, col_2, col_3, col_4 = (
        st.columns(4)
    )

    col_1.metric(
        "INNA Health Score",
        f"{score_global:.1f}/100",
    )

    col_2.metric(
        "Classificação",
        f"{icone} {classificacao}",
    )

    col_3.metric(
        "Componente mais forte",
        NOMES_COMPONENTES.get(
            health.get(
                "componente_mais_forte",
                "",
            ),
            health.get(
                "componente_mais_forte",
                "—",
            ),
        ),
    )

    col_4.metric(
        "Componente prioritário",
        NOMES_COMPONENTES.get(
            health.get(
                "componente_mais_fraco",
                "",
            ),
            health.get(
                "componente_mais_fraco",
                "—",
            ),
        ),
    )

    st.progress(
        max(
            0.0,
            min(
                score_global / 100,
                1.0,
            ),
        )
    )

    if score_global >= 95:
        st.success(
            "A INNA está operando em excelente estado."
        )

    elif score_global >= 85:
        st.info(
            "A INNA está saudável, com alguns pontos "
            "que merecem acompanhamento."
        )

    elif score_global >= 70:
        st.warning(
            "A INNA apresenta componentes que precisam "
            "de atenção."
        )

    else:
        st.error(
            "A saúde global está crítica. Priorize os "
            "componentes com menor score."
        )

    componentes = health.get(
        "componentes",
        {},
    )

    st.divider()
    st.markdown(
        "## Scores por componente"
    )

    colunas = st.columns(3)

    for indice, (
        nome,
        item,
    ) in enumerate(
        componentes.items()
    ):
        coluna = colunas[
            indice % 3
        ]

        with coluna:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### {item.get('icone', '')} "
                    f"{NOMES_COMPONENTES.get(nome, nome)}"
                )

                st.metric(
                    "Score",
                    f"{float(item.get('score', 0)):.1f}/100",
                )

                st.progress(
                    max(
                        0.0,
                        min(
                            float(
                                item.get(
                                    "score",
                                    0,
                                )
                            )
                            / 100,
                            1.0,
                        ),
                    )
                )

                st.caption(
                    f"Peso no score global: "
                    f"{float(item.get('peso', 0)) * 100:.1f}%"
                )

                penalidades = item.get(
                    "penalidades",
                    [],
                )

                if penalidades:
                    with st.expander(
                        "Ver penalidades",
                        expanded=False,
                    ):
                        for penalidade in penalidades:
                            st.markdown(
                                f"- {penalidade}"
                            )
                else:
                    st.success(
                        "Nenhuma penalidade aplicada."
                    )

    tabela = preparar_componentes_exibicao(
        componentes
    )

    st.markdown(
        "### Comparativo dos componentes"
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    if not tabela.empty:
        st.bar_chart(
            tabela.set_index(
                "Componente"
            )[["Score"]],
            use_container_width=True,
        )

    st.divider()
    st.markdown(
        "## Recomendações prioritárias"
    )

    for recomendacao in health.get(
        "recomendacoes",
        [],
    ):
        st.info(
            recomendacao
        )

    render_health_history_section(
        resultado_atual=resultado
    )

    metricas = resultado.get(
        "metricas",
        {},
    )

    with st.expander(
        "📋 Métricas técnicas utilizadas",
        expanded=False,
    ):
        st.json(
            metricas
        )

    erros = resultado.get(
        "erros_coleta",
        [],
    )

    if erros:
        with st.expander(
            "⚠️ Alertas durante a coleta",
            expanded=False,
        ):
            for erro in erros:
                st.warning(
                    erro
                )


__all__ = [
    "render_health_history_section",
    "preparar_historico_exibicao",
    "NOMES_COMPONENTES",
    "preparar_componentes_exibicao",
    "render_health_score_page",
]

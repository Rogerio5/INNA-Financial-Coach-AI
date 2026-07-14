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
    "NOMES_COMPONENTES",
    "preparar_componentes_exibicao",
    "render_health_score_page",
]

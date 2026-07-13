"""
Timeline Viewer das execuções da INNA.

Permite:
- listar traces recentes;
- filtrar execuções;
- visualizar etapas em ordem;
- identificar gargalos;
- inspecionar metadata e erros;
- comparar traces.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st


STATUS_LABELS = {
    "sucesso": "✅ Sucesso",
    "falha": "❌ Falha",
    "ignorado": "⏭️ Ignorado",
    "iniciado": "🔄 Iniciado",
}


def formatar_duracao_ms(
    valor: Any,
) -> str:
    """
    Formata duração em ms ou segundos.
    """
    if valor is None or pd.isna(valor):
        return "Não medida"

    duracao = float(valor)

    if duracao >= 1000:
        return f"{duracao / 1000:.3f} s"

    return f"{duracao:.3f} ms"


def calcular_resumo_trace(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Calcula os indicadores principais de um trace.
    """
    if df is None or df.empty:
        return {
            "total_etapas": 0,
            "total_falhas": 0,
            "total_ignoradas": 0,
            "duracao_total_ms": 0.0,
            "etapa_mais_lenta": None,
            "duracao_etapa_mais_lenta_ms": 0.0,
            "possivel_cold_start": False,
        }

    base = df.copy()

    duracoes = pd.to_numeric(
        base.get(
            "duracao_ms",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    )

    duracao_total = float(
        duracoes.fillna(0).sum()
    )

    etapa_mais_lenta = None
    duracao_mais_lenta = 0.0

    if duracoes.notna().any():
        indice = duracoes.idxmax()

        etapa_mais_lenta = base.loc[
            indice,
            "etapa_label",
        ]

        duracao_mais_lenta = float(
            duracoes.loc[indice]
        )

    total_falhas = int(
        (
            base.get(
                "status",
                pd.Series(dtype=str),
            )
            == "falha"
        ).sum()
    )

    total_ignoradas = int(
        (
            base.get(
                "status",
                pd.Series(dtype=str),
            )
            == "ignorado"
        ).sum()
    )

    return {
        "total_etapas": len(base),
        "total_falhas": total_falhas,
        "total_ignoradas": total_ignoradas,
        "duracao_total_ms": round(
            duracao_total,
            3,
        ),
        "etapa_mais_lenta": etapa_mais_lenta,
        "duracao_etapa_mais_lenta_ms": round(
            duracao_mais_lenta,
            3,
        ),
        "possivel_cold_start": (
            duracao_total >= 30000
        ),
    }


def preparar_traces_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara a tabela de traces recentes.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    tabela = df.copy()

    tabela["Início"] = pd.to_datetime(
        tabela["inicio_trace"],
        errors="coerce",
    ).dt.strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    tabela["Duração total"] = tabela[
        "duracao_total_ms"
    ].apply(
        formatar_duracao_ms
    )

    tabela["Status"] = tabela[
        "total_falhas"
    ].apply(
        lambda total: (
            "❌ Com falha"
            if int(total or 0) > 0
            else "✅ Sucesso"
        )
    )

    tabela["Cold start"] = tabela[
        "duracao_total_ms"
    ].apply(
        lambda valor: (
            "Possível"
            if float(valor or 0) >= 30000
            else "Não"
        )
    )

    colunas = [
        "trace_id",
        "Início",
        "usuario_id",
        "pergunta",
        "total_etapas",
        "total_falhas",
        "Duração total",
        "Cold start",
        "origem",
        "Status",
    ]

    return tabela[
        [
            coluna
            for coluna in colunas
            if coluna in tabela.columns
        ]
    ].rename(
        columns={
            "trace_id": "Trace ID",
            "usuario_id": "Usuário",
            "pergunta": "Pergunta",
            "total_etapas": "Etapas",
            "total_falhas": "Falhas",
            "origem": "Origem",
        }
    )


def preparar_timeline_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara as etapas de um trace.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    tabela = df.copy()

    tabela["Status visual"] = tabela[
        "status"
    ].map(
        STATUS_LABELS
    ).fillna(
        tabela["status"]
    )

    tabela["Duração"] = tabela[
        "duracao_ms"
    ].apply(
        formatar_duracao_ms
    )

    tabela["Início"] = pd.to_datetime(
        tabela["inicio_em"],
        errors="coerce",
    ).dt.strftime(
        "%H:%M:%S.%f"
    ).str[:-3]

    colunas = [
        "ordem",
        "etapa_label",
        "Status visual",
        "Duração",
        "Início",
        "mensagem",
        "erro",
    ]

    return tabela[
        [
            coluna
            for coluna in colunas
            if coluna in tabela.columns
        ]
    ].rename(
        columns={
            "ordem": "Ordem",
            "etapa_label": "Etapa",
            "mensagem": "Mensagem",
            "erro": "Erro",
        }
    )


def render_etapas_timeline(
    df: pd.DataFrame,
) -> None:
    """
    Renderiza a sequência visual das etapas.
    """
    for _, evento in df.sort_values(
        by=[
            "ordem",
            "criado_em",
        ]
    ).iterrows():

        status = str(
            evento.get("status")
            or ""
        )

        simbolo = {
            "sucesso": "✅",
            "falha": "❌",
            "ignorado": "⏭️",
            "iniciado": "🔄",
        }.get(
            status,
            "ℹ️",
        )

        etapa = evento.get(
            "etapa_label"
        )

        duracao = formatar_duracao_ms(
            evento.get("duracao_ms")
        )

        with st.container(
            border=True
        ):
            col_1, col_2, col_3 = st.columns(
                [0.5, 3, 1.2]
            )

            col_1.markdown(
                f"### {simbolo}"
            )

            col_2.markdown(
                f"**{etapa}**"
            )

            col_2.caption(
                evento.get("mensagem")
                or ""
            )

            col_3.metric(
                "Duração",
                duracao,
            )

            erro = evento.get("erro")

            if erro and not pd.isna(erro):
                st.error(
                    str(erro)
                )

            metadata = evento.get(
                "metadata"
            )

            if metadata:
                with st.popover(
                    "Ver metadata"
                ):
                    if isinstance(
                        metadata,
                        str,
                    ):
                        try:
                            metadata = json.loads(
                                metadata
                            )
                        except Exception:
                            pass

                    st.json(
                        metadata
                    )


def calcular_diferenca_traces(
    duracao_a_ms: float,
    duracao_b_ms: float,
) -> dict[str, float]:
    """
    Calcula diferença absoluta e percentual entre traces.

    O percentual usa o Trace A como referência.
    """
    duracao_a = float(
        duracao_a_ms or 0
    )

    duracao_b = float(
        duracao_b_ms or 0
    )

    diferenca_absoluta = (
        duracao_b - duracao_a
    )

    diferenca_percentual = (
        (
            diferenca_absoluta
            / duracao_a
        )
        * 100
        if duracao_a > 0
        else 0.0
    )

    return {
        "diferenca_absoluta_ms": round(
            diferenca_absoluta,
            3,
        ),
        "diferenca_percentual": round(
            diferenca_percentual,
            2,
        ),
    }


def render_comparacao_traces(
    traces_df: pd.DataFrame,
) -> None:
    """
    Compara dois traces com filtro de cold start,
    escala selecionável e diferença percentual.
    """
    if traces_df is None or len(traces_df) < 2:
        st.info(
            "São necessários pelo menos dois traces "
            "para fazer uma comparação."
        )
        return

    base = traces_df.copy()

    ignorar_cold_start = st.checkbox(
        "Ignorar traces classificados como cold start",
        value=False,
        key="timeline_compare_ignore_cold_start",
    )

    if ignorar_cold_start:
        base = base[
            pd.to_numeric(
                base["duracao_total_ms"],
                errors="coerce",
            ).fillna(0) < 30000
        ]

    if len(base) < 2:
        st.warning(
            "Não existem dois traces disponíveis após "
            "aplicar o filtro de cold start."
        )
        return

    escala = st.radio(
        "Escala do gráfico",
        options=[
            "Linear",
            "Logarítmica",
        ],
        horizontal=True,
        key="timeline_compare_scale",
    )

    opcoes = base[
        "trace_id"
    ].astype(str).tolist()

    col_1, col_2 = st.columns(2)

    trace_a = col_1.selectbox(
        "Trace A",
        options=opcoes,
        index=0,
        key="timeline_compare_a",
    )

    trace_b = col_2.selectbox(
        "Trace B",
        options=opcoes,
        index=min(
            1,
            len(opcoes) - 1,
        ),
        key="timeline_compare_b",
    )

    if trace_a == trace_b:
        st.warning(
            "Selecione dois traces diferentes."
        )
        return

    try:
        from observability.timeline import (
            carregar_timeline_trace,
        )
    except ImportError:
        from src.observability.timeline import (
            carregar_timeline_trace,
        )

    resultado_a = carregar_timeline_trace(
        trace_a
    )

    resultado_b = carregar_timeline_trace(
        trace_b
    )

    df_a = resultado_a.get("df")
    df_b = resultado_b.get("df")

    resumo_a = calcular_resumo_trace(
        df_a
    )

    resumo_b = calcular_resumo_trace(
        df_b
    )

    duracao_a = float(
        resumo_a["duracao_total_ms"]
    )

    duracao_b = float(
        resumo_b["duracao_total_ms"]
    )

    diferenca = calcular_diferenca_traces(
        duracao_a,
        duracao_b,
    )

    diferenca_absoluta = diferenca[
        "diferenca_absoluta_ms"
    ]

    diferenca_percentual = diferenca[
        "diferenca_percentual"
    ]

    comparacao = pd.DataFrame([
        {
            "Trace": "A",
            "Trace ID": trace_a,
            "Etapas": resumo_a[
                "total_etapas"
            ],
            "Falhas": resumo_a[
                "total_falhas"
            ],
            "Duração total": (
                formatar_duracao_ms(
                    duracao_a
                )
            ),
            "Etapa mais lenta": (
                resumo_a[
                    "etapa_mais_lenta"
                ]
            ),
            "Cold start": (
                "Possível"
                if resumo_a[
                    "possivel_cold_start"
                ]
                else "Não"
            ),
        },
        {
            "Trace": "B",
            "Trace ID": trace_b,
            "Etapas": resumo_b[
                "total_etapas"
            ],
            "Falhas": resumo_b[
                "total_falhas"
            ],
            "Duração total": (
                formatar_duracao_ms(
                    duracao_b
                )
            ),
            "Etapa mais lenta": (
                resumo_b[
                    "etapa_mais_lenta"
                ]
            ),
            "Cold start": (
                "Possível"
                if resumo_b[
                    "possivel_cold_start"
                ]
                else "Não"
            ),
        },
    ])

    st.dataframe(
        comparacao,
        use_container_width=True,
        hide_index=True,
    )

    if diferenca_percentual > 0:
        st.warning(
            f"O Trace B foi "
            f"{abs(diferenca_percentual):.2f}% "
            "mais lento que o Trace A."
        )

    elif diferenca_percentual < 0:
        st.success(
            f"O Trace B foi "
            f"{abs(diferenca_percentual):.2f}% "
            "mais rápido que o Trace A."
        )

    else:
        st.info(
            "Os dois traces tiveram a mesma duração total."
        )

    col_delta_1, col_delta_2 = st.columns(2)

    col_delta_1.metric(
        "Diferença absoluta",
        formatar_duracao_ms(
            abs(diferenca_absoluta)
        ),
    )

    col_delta_2.metric(
        "Diferença percentual",
        f"{abs(diferenca_percentual):.2f}%",
    )

    etapas_a = (
        df_a[
            [
                "etapa_label",
                "duracao_ms",
            ]
        ]
        .rename(
            columns={
                "duracao_ms": "Trace A",
            }
        )
    )

    etapas_b = (
        df_b[
            [
                "etapa_label",
                "duracao_ms",
            ]
        ]
        .rename(
            columns={
                "duracao_ms": "Trace B",
            }
        )
    )

    grafico = etapas_a.merge(
        etapas_b,
        on="etapa_label",
        how="outer",
    ).fillna(0)

    grafico["Trace A"] = pd.to_numeric(
        grafico["Trace A"],
        errors="coerce",
    ).fillna(0)

    grafico["Trace B"] = pd.to_numeric(
        grafico["Trace B"],
        errors="coerce",
    ).fillna(0)

    if escala == "Logarítmica":
        import numpy as np

        grafico_plot = grafico.copy()

        grafico_plot["Trace A"] = np.log10(
            grafico_plot["Trace A"] + 1
        )

        grafico_plot["Trace B"] = np.log10(
            grafico_plot["Trace B"] + 1
        )

        st.caption(
            "Escala logarítmica: os valores exibidos "
            "representam log10(duração em ms + 1)."
        )
    else:
        grafico_plot = grafico

    st.bar_chart(
        grafico_plot.set_index(
            "etapa_label"
        ),
        use_container_width=True,
    )

def render_timeline_viewer_page() -> None:
    """
    Renderiza o Timeline Viewer.
    """
    try:
        from observability.timeline import (
            carregar_timeline_trace,
            carregar_traces_recentes,
        )
    except ImportError:
        from src.observability.timeline import (
            carregar_timeline_trace,
            carregar_traces_recentes,
        )

    st.title(
        "🧭 Timeline Viewer — INNA"
    )

    st.caption(
        "Visualize o caminho completo de cada resposta: "
        "memória, Router, Tools, RAG, Gemini e entrega."
    )

    col_1, col_2 = st.columns(
        [1, 3]
    )

    limite = col_1.selectbox(
        "Quantidade de traces",
        options=[
            10,
            25,
            50,
            100,
        ],
        index=1,
        key="timeline_viewer_limit",
    )

    with col_2:
        st.write("")

        if st.button(
            "🔄 Atualizar Timeline",
            use_container_width=True,
            key="timeline_viewer_refresh",
        ):
            st.rerun()

    resultado_traces = carregar_traces_recentes(
        limite=int(limite)
    )

    if not resultado_traces.get("ok"):
        st.error(
            resultado_traces.get(
                "message"
            )
        )
        return

    traces_df = resultado_traces.get(
        "df"
    )

    if traces_df is None or traces_df.empty:
        st.info(
            "Ainda não existem traces registrados."
        )
        return

    st.markdown(
        "## Pesquisa e filtros"
    )

    pesquisa = st.text_input(
        "Pesquisar usuário, pergunta ou Trace ID",
        placeholder=(
            "Ex.: demo_user, quanto sobra..."
        ),
        key="timeline_viewer_search",
    )

    filtro_1, filtro_2 = st.columns(2)

    usuarios = sorted(
        traces_df["usuario_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    origens = sorted(
        traces_df["origem"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    usuario = filtro_1.selectbox(
        "Usuário",
        options=["Todos"] + usuarios,
        key="timeline_viewer_user",
    )

    origem = filtro_2.selectbox(
        "Origem",
        options=["Todas"] + origens,
        key="timeline_viewer_origin",
    )

    somente_falhas = st.checkbox(
        "Mostrar somente traces com falhas",
        value=False,
        key="timeline_viewer_failures",
    )

    filtrado = traces_df.copy()

    if pesquisa.strip():
        termo = pesquisa.strip().lower()

        mascara = (
            filtrado["trace_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                termo,
                regex=False,
            )
        )

        for coluna in [
            "usuario_id",
            "pergunta",
        ]:
            if coluna in filtrado.columns:
                mascara = mascara | (
                    filtrado[coluna]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        termo,
                        regex=False,
                    )
                )

        filtrado = filtrado[
            mascara
        ]

    if usuario != "Todos":
        filtrado = filtrado[
            filtrado["usuario_id"].astype(str)
            == usuario
        ]

    if origem != "Todas":
        filtrado = filtrado[
            filtrado["origem"].astype(str)
            == origem
        ]

    if somente_falhas:
        filtrado = filtrado[
            filtrado["total_falhas"] > 0
        ]

    st.caption(
        f"{len(filtrado)} trace(s) encontrado(s)."
    )

    st.markdown(
        "## Traces recentes"
    )

    st.dataframe(
        preparar_traces_exibicao(
            filtrado
        ),
        use_container_width=True,
        hide_index=True,
    )

    if filtrado.empty:
        return

    opcoes_trace = filtrado[
        "trace_id"
    ].astype(str).tolist()

    trace_selecionado = st.selectbox(
        "Selecione um Trace ID",
        options=opcoes_trace,
        key="timeline_viewer_trace",
    )

    resultado_timeline = (
        carregar_timeline_trace(
            trace_selecionado
        )
    )

    if not resultado_timeline.get("ok"):
        st.error(
            resultado_timeline.get(
                "message"
            )
        )
        return

    timeline_df = resultado_timeline.get(
        "df"
    )

    resumo = calcular_resumo_trace(
        timeline_df
    )

    st.divider()
    st.markdown(
        "## Resumo da execução"
    )

    linha_1 = st.columns(4)

    linha_1[0].metric(
        "Etapas",
        resumo["total_etapas"],
    )

    linha_1[1].metric(
        "Falhas",
        resumo["total_falhas"],
    )

    linha_1[2].metric(
        "Ignoradas",
        resumo["total_ignoradas"],
    )

    linha_1[3].metric(
        "Duração total",
        formatar_duracao_ms(
            resumo["duracao_total_ms"]
        ),
    )

    if resumo["possivel_cold_start"]:
        st.warning(
            "Possível cold start detectado: "
            "a execução ultrapassou 30 segundos."
        )
    else:
        st.success(
            "Execução dentro do limite esperado "
            "para o ambiente atual."
        )

    if resumo["etapa_mais_lenta"]:
        st.info(
            "Etapa mais lenta: "
            f"{resumo['etapa_mais_lenta']} — "
            f"{formatar_duracao_ms(
                resumo[
                    'duracao_etapa_mais_lenta_ms'
                ]
            )}"
        )

    pergunta = (
        timeline_df["pergunta"]
        .dropna()
        .astype(str)
    )

    if not pergunta.empty:
        st.markdown(
            "### Pergunta"
        )

        st.code(
            pergunta.iloc[0],
            language=None,
        )

    st.markdown(
        "## Caminho da execução"
    )

    render_etapas_timeline(
        timeline_df
    )

    st.markdown(
        "## Tabela técnica"
    )

    st.dataframe(
        preparar_timeline_exibicao(
            timeline_df
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown(
        "## Comparar traces"
    )

    render_comparacao_traces(
        traces_df
    )


__all__ = [
    "STATUS_LABELS",
    "formatar_duracao_ms",
    "calcular_resumo_trace",
    "calcular_diferenca_traces",
    "preparar_traces_exibicao",
    "preparar_timeline_exibicao",
    "render_etapas_timeline",
    "render_comparacao_traces",
    "render_timeline_viewer_page",
]

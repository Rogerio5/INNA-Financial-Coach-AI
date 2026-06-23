import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.database import engine, init_db


st.set_page_config(
    page_title="Dashboard INNA",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard — INNA Financial Coach AI")
st.subheader("Analytics financeiro, feedbacks e validação com usuários via PostgreSQL")

st.info(
    "Este dashboard lê dados diretamente do PostgreSQL configurado no projeto, podendo ser local ou Neon. "
    "Ele será usado para validar uso real, métricas de hackathon e evolução futura."
)


def load_table(query: str) -> pd.DataFrame:
    try:
        init_db()

        with engine.connect() as connection:
            return pd.read_sql(text(query), connection)

    except Exception as error:
        st.error(f"Erro ao carregar dados do PostgreSQL: {error}")
        return pd.DataFrame()


if st.button("🔄 Atualizar dados"):
    st.rerun()


diagnosticos_df = load_table("""
    SELECT
        id,
        data_hora,
        nome,
        renda_mensal,
        gastos_fixos,
        gastos_variaveis,
        dividas_mensais,
        reserva_atual,
        objetivo,
        saldo_estimado,
        comprometimento_renda_percentual,
        meses_reserva_estimados,
        score_financeiro,
        nivel_risco,
        diagnostico,
        plano_30_dias
    FROM diagnosticos_financeiros
    ORDER BY id ASC
""")

feedbacks_df = load_table("""
    SELECT
        id,
        data_hora,
        nome,
        util,
        comentario,
        score_financeiro,
        nivel_risco
    FROM feedbacks_usuarios
    ORDER BY id ASC
""")

eventos_df = load_table("""
    SELECT
        id,
        data_hora,
        canal,
        usuario,
        idioma,
        moeda,
        status,
        diagnostico_id,
        metadata
    FROM interacoes_inna
    WHERE canal NOT LIKE 'teste%'
      AND COALESCE(metadata->>'teste', 'false') <> 'true'
    ORDER BY id ASC
""")


if diagnosticos_df.empty:
    st.warning("Ainda não existem diagnósticos registrados no PostgreSQL.")
    st.stop()


diagnosticos_df["data_hora"] = pd.to_datetime(
    diagnosticos_df["data_hora"],
    errors="coerce",
)

if not feedbacks_df.empty:
    feedbacks_df["data_hora"] = pd.to_datetime(
        feedbacks_df["data_hora"],
        errors="coerce",
    )

if not eventos_df.empty:
    eventos_df["data_hora"] = pd.to_datetime(
        eventos_df["data_hora"],
        errors="coerce",
    )


st.divider()

st.write("## 🔎 Filtros")

min_data = diagnosticos_df["data_hora"].min()
max_data = diagnosticos_df["data_hora"].max()

if pd.isna(min_data) or pd.isna(max_data):
    data_inicio = date.today()
    data_fim = date.today()
else:
    data_inicio = min_data.date()
    data_fim = max_data.date()

col_data1, col_data2 = st.columns(2)

with col_data1:
    filtro_data_inicio = st.date_input(
        "Data inicial",
        value=data_inicio,
        format="DD/MM/YYYY",
    )

with col_data2:
    filtro_data_fim = st.date_input(
        "Data final",
        value=data_fim,
        format="DD/MM/YYYY",
    )

st.write("### Atalhos de período")

meses_disponiveis = ["Todos"]

if "data_hora" in diagnosticos_df.columns:
    meses_unicos = (
        diagnosticos_df["data_hora"]
        .dropna()
        .dt.to_period("M")
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    meses_disponiveis += meses_unicos

filtro_mes = st.selectbox(
    "Filtrar por mês",
    meses_disponiveis,
)

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    nomes_disponiveis = ["Todos"] + sorted(
        diagnosticos_df["nome"].dropna().unique().tolist()
    )
    filtro_nome = st.selectbox("Filtrar por usuário", nomes_disponiveis)

with col_filter2:
    riscos_disponiveis = ["Todos"] + sorted(
        diagnosticos_df["nivel_risco"].dropna().unique().tolist()
    )
    filtro_risco = st.selectbox("Filtrar por risco", riscos_disponiveis)

with col_filter3:
    if feedbacks_df.empty:
        feedbacks_disponiveis = ["Todos"]
    else:
        feedbacks_disponiveis = ["Todos"] + sorted(
            feedbacks_df["util"].dropna().unique().tolist()
        )

    filtro_feedback = st.selectbox("Filtrar por feedback", feedbacks_disponiveis)


diagnosticos_filtrados = diagnosticos_df.copy()
feedbacks_filtrados = feedbacks_df.copy()
eventos_filtrados = eventos_df.copy()

inicio_periodo = pd.to_datetime(filtro_data_inicio)
fim_periodo = pd.to_datetime(filtro_data_fim) + pd.Timedelta(days=1)

diagnosticos_filtrados = diagnosticos_filtrados[
    (diagnosticos_filtrados["data_hora"] >= inicio_periodo)
    & (diagnosticos_filtrados["data_hora"] < fim_periodo)
]

if not feedbacks_filtrados.empty:
    feedbacks_filtrados = feedbacks_filtrados[
        (feedbacks_filtrados["data_hora"] >= inicio_periodo)
        & (feedbacks_filtrados["data_hora"] < fim_periodo)
    ]

if not eventos_filtrados.empty:
    eventos_filtrados = eventos_filtrados[
        (eventos_filtrados["data_hora"] >= inicio_periodo)
        & (eventos_filtrados["data_hora"] < fim_periodo)
    ]

if filtro_mes != "Todos":
    diagnosticos_filtrados = diagnosticos_filtrados[
        diagnosticos_filtrados["data_hora"].dt.to_period("M").astype(str) == filtro_mes
    ]

    if not feedbacks_filtrados.empty:
        feedbacks_filtrados = feedbacks_filtrados[
            feedbacks_filtrados["data_hora"].dt.to_period("M").astype(str) == filtro_mes
        ]

    if not eventos_filtrados.empty:
        eventos_filtrados = eventos_filtrados[
            eventos_filtrados["data_hora"].dt.to_period("M").astype(str) == filtro_mes
        ]

if filtro_nome != "Todos":
    diagnosticos_filtrados = diagnosticos_filtrados[
        diagnosticos_filtrados["nome"] == filtro_nome
    ]

    if not feedbacks_filtrados.empty:
        feedbacks_filtrados = feedbacks_filtrados[
            feedbacks_filtrados["nome"] == filtro_nome
        ]

    if not eventos_filtrados.empty and "usuario" in eventos_filtrados.columns:
        eventos_filtrados = eventos_filtrados[
            eventos_filtrados["usuario"] == filtro_nome
        ]

if filtro_risco != "Todos":
    diagnosticos_filtrados = diagnosticos_filtrados[
        diagnosticos_filtrados["nivel_risco"] == filtro_risco
    ]

    if not feedbacks_filtrados.empty:
        feedbacks_filtrados = feedbacks_filtrados[
            feedbacks_filtrados["nivel_risco"] == filtro_risco
        ]

if filtro_feedback != "Todos" and not feedbacks_filtrados.empty:
    feedbacks_filtrados = feedbacks_filtrados[
        feedbacks_filtrados["util"] == filtro_feedback
    ]


st.divider()

st.write("## 📌 Indicadores principais")

total_diagnosticos = len(diagnosticos_filtrados)
usuarios_unicos = diagnosticos_filtrados["nome"].nunique()
score_medio = diagnosticos_filtrados["score_financeiro"].mean()
saldo_medio = diagnosticos_filtrados["saldo_estimado"].mean()

if feedbacks_filtrados.empty:
    total_feedbacks = 0
    taxa_util = 0
else:
    total_feedbacks = len(feedbacks_filtrados)
    feedbacks_positivos = feedbacks_filtrados[
        feedbacks_filtrados["util"] == "Sim"
    ].shape[0]
    taxa_util = (feedbacks_positivos / total_feedbacks) * 100 if total_feedbacks > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Diagnósticos", total_diagnosticos)
col2.metric("Usuários únicos", usuarios_unicos)
col3.metric("Score médio", f"{score_medio:.1f}/100" if total_diagnosticos > 0 else "0/100")
col4.metric("Saldo médio", f"R$ {saldo_medio:.2f}" if total_diagnosticos > 0 else "R$ 0.00")
col5.metric("Feedback útil", f"{taxa_util:.1f}%")

st.divider()

st.write("## 🌐 Eventos multicanal reais")

if eventos_filtrados.empty:
    st.caption("Ainda não há eventos multicanal reais registrados no período selecionado.")
else:
    eventos_total = len(eventos_filtrados)
    canais_ativos = eventos_filtrados["canal"].nunique()

    ultimo_evento = eventos_filtrados.sort_values("data_hora").tail(1)
    ultimo_canal = ultimo_evento["canal"].iloc[0] if not ultimo_evento.empty else "-"

    col_event1, col_event2, col_event3 = st.columns(3)
    col_event1.metric("Eventos reais", eventos_total)
    col_event2.metric("Canais ativos", canais_ativos)
    col_event3.metric("Último canal", ultimo_canal)

    eventos_por_canal = eventos_filtrados["canal"].value_counts()
    st.bar_chart(eventos_por_canal)

    eventos_table = eventos_por_canal.reset_index()
    eventos_table.columns = ["canal", "quantidade"]
    st.dataframe(eventos_table, use_container_width=True)

    with st.expander("Ver últimos eventos reais"):
        colunas_eventos = [
            "id",
            "data_hora",
            "canal",
            "usuario",
            "idioma",
            "moeda",
            "status",
            "diagnostico_id",
        ]

        colunas_eventos = [
            coluna for coluna in colunas_eventos
            if coluna in eventos_filtrados.columns
        ]

        st.dataframe(
            eventos_filtrados[colunas_eventos].tail(20),
            use_container_width=True,
        )

st.divider()


col_left, col_right = st.columns(2)

with col_left:
    st.write("## ⚠️ Distribuição por risco")

    if diagnosticos_filtrados.empty:
        st.warning("Nenhum diagnóstico encontrado para os filtros selecionados.")
    else:
        risco_counts = diagnosticos_filtrados["nivel_risco"].value_counts()
        st.bar_chart(risco_counts)

        risco_table = risco_counts.reset_index()
        risco_table.columns = ["nivel_risco", "quantidade"]
        st.dataframe(risco_table, use_container_width=True)

with col_right:
    st.write("## 👍 Feedbacks")

    if feedbacks_filtrados.empty:
        st.warning("Nenhum feedback encontrado para os filtros selecionados.")
    else:
        feedback_counts = feedbacks_filtrados["util"].value_counts()
        st.bar_chart(feedback_counts)

        feedback_table = feedback_counts.reset_index()
        feedback_table.columns = ["feedback", "quantidade"]
        st.dataframe(feedback_table, use_container_width=True)


st.divider()

col_score, col_saldo = st.columns(2)

with col_score:
    st.write("## 📈 Evolução dos scores")

    if diagnosticos_filtrados.empty:
        st.warning("Sem dados para evolução de score.")
    else:
        score_chart = diagnosticos_filtrados[["id", "score_financeiro"]].set_index("id")
        st.line_chart(score_chart)

with col_saldo:
    st.write("## 💵 Evolução do saldo estimado")

    if diagnosticos_filtrados.empty:
        st.warning("Sem dados para evolução de saldo.")
    else:
        saldo_chart = diagnosticos_filtrados[["id", "saldo_estimado"]].set_index("id")
        st.line_chart(saldo_chart)


st.divider()

col_rank, col_risco_score = st.columns(2)

with col_rank:
    st.write("## 🏆 Ranking de usuários por diagnósticos")

    ranking_usuarios = (
        diagnosticos_df.groupby("nome")
        .agg(
            total_diagnosticos=("id", "count"),
            score_medio=("score_financeiro", "mean"),
            saldo_medio=("saldo_estimado", "mean"),
        )
        .reset_index()
        .sort_values(by="total_diagnosticos", ascending=False)
    )

    ranking_usuarios["score_medio"] = ranking_usuarios["score_medio"].round(1)
    ranking_usuarios["saldo_medio"] = ranking_usuarios["saldo_medio"].round(2)

    st.dataframe(ranking_usuarios, use_container_width=True)

with col_risco_score:
    st.write("## 📊 Score médio por risco")

    score_por_risco = (
        diagnosticos_df.groupby("nivel_risco")
        .agg(
            quantidade=("id", "count"),
            score_medio=("score_financeiro", "mean"),
            saldo_medio=("saldo_estimado", "mean"),
        )
        .reset_index()
    )

    score_por_risco["score_medio"] = score_por_risco["score_medio"].round(1)
    score_por_risco["saldo_medio"] = score_por_risco["saldo_medio"].round(2)

    st.dataframe(score_por_risco, use_container_width=True)


st.divider()

st.write("## 📤 Exportar dados filtrados")

col_export1, col_export2 = st.columns(2)

with col_export1:
    csv_diagnosticos = diagnosticos_filtrados.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        label="⬇️ Baixar diagnósticos filtrados CSV",
        data=csv_diagnosticos,
        file_name="inna_diagnosticos_filtrados.csv",
        mime="text/csv",
    )

with col_export2:
    if feedbacks_filtrados.empty:
        st.caption("Sem feedbacks filtrados para exportar.")
    else:
        csv_feedbacks = feedbacks_filtrados.to_csv(
            index=False,
            encoding="utf-8-sig",
        )

        st.download_button(
            label="⬇️ Baixar feedbacks filtrados CSV",
            data=csv_feedbacks,
            file_name="inna_feedbacks_filtrados.csv",
            mime="text/csv",
        )

st.divider()

st.write("## 🧾 Últimos diagnósticos")

colunas_diagnostico = [
    "id",
    "data_hora",
    "nome",
    "renda_mensal",
    "saldo_estimado",
    "comprometimento_renda_percentual",
    "score_financeiro",
    "nivel_risco",
    "objetivo",
]

if diagnosticos_filtrados.empty:
    st.warning("Nenhum diagnóstico encontrado.")
else:
    st.dataframe(
        diagnosticos_filtrados[colunas_diagnostico].tail(20),
        use_container_width=True,
    )


st.divider()

st.write("## 💬 Últimos feedbacks")

if feedbacks_filtrados.empty:
    st.warning("Nenhum feedback encontrado.")
else:
    colunas_feedback = [
        "id",
        "data_hora",
        "nome",
        "util",
        "comentario",
        "score_financeiro",
        "nivel_risco",
    ]

    st.dataframe(
        feedbacks_filtrados[colunas_feedback].tail(20),
        use_container_width=True,
    )


st.divider()

st.write("## 🗣️ Comentários recebidos")

if feedbacks_filtrados.empty or "comentario" not in feedbacks_filtrados.columns:
    st.caption("Ainda não há comentários preenchidos.")
else:
    comentarios = feedbacks_filtrados["comentario"].dropna()
    comentarios = comentarios[comentarios.astype(str).str.strip() != ""]

    if comentarios.empty:
        st.caption("Ainda não há comentários preenchidos.")
    else:
        for comentario in comentarios.tail(10):
            st.markdown(f"> {comentario}")


st.divider()

st.write("## 🧠 Leitura executiva")

if total_diagnosticos == 0:
    st.warning("Ainda não há dados suficientes para análise executiva.")
else:
    risco_mais_comum = diagnosticos_filtrados["nivel_risco"].mode()

    if not risco_mais_comum.empty:
        risco_mais_comum = risco_mais_comum.iloc[0]
    else:
        risco_mais_comum = "Indefinido"

    st.markdown(
        f"""
        **Resumo da base atual:**

        - Foram gerados **{total_diagnosticos} diagnósticos** nos filtros selecionados.
        - Existem **{usuarios_unicos} usuários únicos** na base filtrada.
        - O **score financeiro médio** é de **{score_medio:.1f}/100**.
        - O **saldo médio estimado** é de **R$ {saldo_medio:.2f}**.
        - O nível de risco mais comum é **{risco_mais_comum}**.
        - A taxa de feedback útil é de **{taxa_util:.1f}%**.

        Esses dados ajudam a validar se a INNA está gerando valor real para os usuários.
        """
    )

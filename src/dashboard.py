import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

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
st.subheader("Métricas de diagnósticos, riscos e feedbacks salvos no PostgreSQL")

st.info(
    "Este dashboard lê dados diretamente do PostgreSQL local. "
    "Depois, essa mesma estrutura poderá ser migrada para Supabase ou OCI PostgreSQL."
)


def load_table(query: str) -> pd.DataFrame:
    try:
        init_db()

        with engine.connect() as connection:
            return pd.read_sql(text(query), connection)

    except Exception as error:
        st.error(f"Erro ao carregar dados do PostgreSQL: {error}")
        return pd.DataFrame()


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


if diagnosticos_df.empty:
    st.warning("Ainda não existem diagnósticos registrados no PostgreSQL.")
else:
    total_diagnosticos = len(diagnosticos_df)
    score_medio = diagnosticos_df["score_financeiro"].mean()
    saldo_medio = diagnosticos_df["saldo_estimado"].mean()

    if feedbacks_df.empty:
        total_feedbacks = 0
        taxa_util = 0
    else:
        total_feedbacks = len(feedbacks_df)
        feedbacks_positivos = feedbacks_df[feedbacks_df["util"] == "Sim"].shape[0]
        taxa_util = (feedbacks_positivos / total_feedbacks) * 100 if total_feedbacks > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de diagnósticos", total_diagnosticos)
    col2.metric("Score médio", f"{score_medio:.1f}/100")
    col3.metric("Saldo médio estimado", f"R$ {saldo_medio:.2f}")
    col4.metric("Feedback útil", f"{taxa_util:.1f}%")

    st.divider()

    col_risco, col_feedback = st.columns(2)

    with col_risco:
        st.write("### Distribuição por nível de risco")

        risco_counts = diagnosticos_df["nivel_risco"].value_counts()
        st.bar_chart(risco_counts)

        risco_table = risco_counts.reset_index()
        risco_table.columns = ["nivel_risco", "quantidade"]
        st.dataframe(risco_table, use_container_width=True)

    with col_feedback:
        st.write("### Feedbacks dos usuários")

        if feedbacks_df.empty:
            st.warning("Ainda não existem feedbacks registrados.")
        else:
            feedback_counts = feedbacks_df["util"].value_counts()
            st.bar_chart(feedback_counts)

            feedback_table = feedback_counts.reset_index()
            feedback_table.columns = ["feedback", "quantidade"]
            st.dataframe(feedback_table, use_container_width=True)

    st.divider()

    col_score, col_saldo = st.columns(2)

    with col_score:
        st.write("### Evolução dos scores")

        score_chart = diagnosticos_df[["id", "score_financeiro"]].set_index("id")
        st.line_chart(score_chart)

    with col_saldo:
        st.write("### Evolução do saldo estimado")

        saldo_chart = diagnosticos_df[["id", "saldo_estimado"]].set_index("id")
        st.line_chart(saldo_chart)

    st.divider()

    st.write("### Filtros")

    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        riscos_disponiveis = ["Todos"] + sorted(diagnosticos_df["nivel_risco"].dropna().unique().tolist())
        filtro_risco = st.selectbox("Filtrar por risco", riscos_disponiveis)

    with col_filter2:
        nomes_disponiveis = ["Todos"] + sorted(diagnosticos_df["nome"].dropna().unique().tolist())
        filtro_nome = st.selectbox("Filtrar por nome", nomes_disponiveis)

    diagnosticos_filtrados = diagnosticos_df.copy()

    if filtro_risco != "Todos":
        diagnosticos_filtrados = diagnosticos_filtrados[
            diagnosticos_filtrados["nivel_risco"] == filtro_risco
        ]

    if filtro_nome != "Todos":
        diagnosticos_filtrados = diagnosticos_filtrados[
            diagnosticos_filtrados["nome"] == filtro_nome
        ]

    st.divider()

    st.write("### Últimos diagnósticos")

    colunas_diagnostico = [
        "id",
        "data_hora",
        "nome",
        "renda_mensal",
        "saldo_estimado",
        "score_financeiro",
        "nivel_risco",
        "objetivo",
    ]

    st.dataframe(
        diagnosticos_filtrados[colunas_diagnostico].tail(20),
        use_container_width=True,
    )

    st.divider()

    st.write("### Últimos feedbacks")

    if feedbacks_df.empty:
        st.warning("Nenhum feedback registrado ainda.")
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
            feedbacks_df[colunas_feedback].tail(20),
            use_container_width=True,
        )

        st.write("### Comentários recebidos")

        comentarios = feedbacks_df["comentario"].dropna()
        comentarios = comentarios[comentarios.astype(str).str.strip() != ""]

        if comentarios.empty:
            st.caption("Ainda não há comentários preenchidos.")
        else:
            for comentario in comentarios.tail(5):
                st.markdown(f"> {comentario}")

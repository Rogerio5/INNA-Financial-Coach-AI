import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pandas as pd
import streamlit as st


INTERACOES_PATH = Path("data/interacoes.csv")
FEEDBACKS_PATH = Path("data/feedbacks.csv")


st.set_page_config(
    page_title="Dashboard INNA",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard — INNA Financial Coach AI")
st.subheader("Métricas de diagnósticos, riscos e feedbacks dos usuários")

st.info(
    "Este dashboard usa os arquivos CSV locais do MVP. "
    "Depois, esses dados serão migrados para PostgreSQL."
)


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as error:
        st.error(f"Erro ao carregar {path}: {error}")
        return pd.DataFrame()


interacoes_df = load_csv(INTERACOES_PATH)
feedbacks_df = load_csv(FEEDBACKS_PATH)

if interacoes_df.empty:
    st.warning("Ainda não existem interações registradas em data/interacoes.csv.")
else:
    total_diagnosticos = len(interacoes_df)

    if "score_financeiro" in interacoes_df.columns:
        score_medio = interacoes_df["score_financeiro"].mean()
    else:
        score_medio = 0

    if "saldo_estimado" in interacoes_df.columns:
        saldo_medio = interacoes_df["saldo_estimado"].mean()
    else:
        saldo_medio = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de diagnósticos", total_diagnosticos)
    col2.metric("Score médio", f"{score_medio:.1f}/100")
    col3.metric("Saldo médio estimado", f"R$ {saldo_medio:.2f}")

    st.divider()

    col_risco, col_feedback = st.columns(2)

    with col_risco:
        st.write("### Distribuição por nível de risco")

        if "nivel_risco" in interacoes_df.columns:
            risco_counts = interacoes_df["nivel_risco"].value_counts()
            st.bar_chart(risco_counts)
            st.dataframe(risco_counts.reset_index().rename(
                columns={"index": "nivel_risco", "nivel_risco": "quantidade"}
            ))
        else:
            st.warning("Coluna nivel_risco não encontrada.")

    with col_feedback:
        st.write("### Feedbacks dos usuários")

        if feedbacks_df.empty:
            st.warning("Ainda não existem feedbacks registrados em data/feedbacks.csv.")
        elif "util" in feedbacks_df.columns:
            feedback_counts = feedbacks_df["util"].value_counts()
            st.bar_chart(feedback_counts)
            st.dataframe(feedback_counts.reset_index().rename(
                columns={"index": "util", "util": "quantidade"}
            ))
        else:
            st.warning("Coluna util não encontrada.")

    st.divider()

    st.write("### Evolução dos scores")

    if "score_financeiro" in interacoes_df.columns:
        scores = interacoes_df[["score_financeiro"]].reset_index(drop=True)
        st.line_chart(scores)
    else:
        st.warning("Coluna score_financeiro não encontrada.")

    st.divider()

    st.write("### Últimas interações")

    st.dataframe(interacoes_df.tail(10), use_container_width=True)

    st.divider()

    st.write("### Últimos feedbacks")

    if feedbacks_df.empty:
        st.warning("Nenhum feedback registrado ainda.")
    else:
        columns_to_show = [
            column for column in [
                "data_hora",
                "nome",
                "util",
                "comentario",
                "score_financeiro",
                "nivel_risco",
            ]
            if column in feedbacks_df.columns
        ]

        st.dataframe(feedbacks_df[columns_to_show].tail(10), use_container_width=True)

        if "comentario" in feedbacks_df.columns:
            st.write("### Comentários recebidos")

            comentarios = feedbacks_df["comentario"].dropna()
            comentarios = comentarios[comentarios.astype(str).str.strip() != ""]

            if comentarios.empty:
                st.caption("Ainda não há comentários preenchidos.")
            else:
                for comentario in comentarios.tail(5):
                    st.markdown(f"> {comentario}")

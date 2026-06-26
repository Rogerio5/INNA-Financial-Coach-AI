
import os
from datetime import date

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv


load_dotenv(".env")


st.set_page_config(
    page_title="INNA Analytics",
    page_icon="📊",
    layout="wide",
)


LANGUAGE_LABELS = {
    "pt": "Português Brasil",
    "en_us": "Inglês EUA",
    "en_gb": "Inglês Reino Unido",
    "es": "Espanhol",
    "de": "Alemão",
    "fr": "Francês",
    "it": "Italiano",
    "ro": "Romeno",
    "uk": "Ucraniano",
    "ru": "Russo",
    "ar": "Árabe",
    "ch": "Suíço",
}

CURRENCY_SYMBOLS = {
    "BRL": "R$",
    "USD": "US$",
    "GBP": "£",
    "EUR": "€",
    "RON": "RON",
    "UAH": "₴",
    "RUB": "₽",
    "SAR": "SAR",
    "CHF": "CHF",
}

FIXED_LANGUAGES = [
    "Todos",
    "pt",
    "en_us",
    "en_gb",
    "es",
    "de",
    "fr",
    "it",
    "ro",
    "uk",
    "ru",
    "ar",
    "ch",
]

FIXED_CURRENCIES = [
    "Todos",
    "BRL",
    "USD",
    "GBP",
    "EUR",
    "RON",
    "UAH",
    "RUB",
    "SAR",
    "CHF",
]


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        st.error("DATABASE_URL não configurada.")
        st.stop()

    return psycopg2.connect(database_url)


@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()

    diagnosticos_query = """
    SELECT
        id,
        data_hora,
        nome,
        renda_mensal,
        saldo_estimado,
        comprometimento_renda_percentual,
        score_financeiro,
        nivel_risco,
        idioma,
        moeda,
        simbolo_moeda,
        objetivo
    FROM diagnosticos_financeiros
    ORDER BY data_hora DESC;
    """

    feedbacks_query = """
    SELECT *
    FROM feedbacks_usuarios
    ORDER BY data_hora DESC;
    """

    eventos_query = """
    SELECT
        id,
        data_hora,
        canal,
        usuario,
        usuario_id,
        idioma,
        moeda,
        status,
        diagnostico_id,
        metadata
    FROM interacoes_inna
    WHERE canal NOT LIKE 'teste%%'
      AND COALESCE(metadata->>'teste', 'false') <> 'true'
      AND COALESCE(metadata->>'teste_controlado', 'false') <> 'true'
    ORDER BY data_hora DESC;
    """

    diagnosticos_df = pd.read_sql(diagnosticos_query, conn)
    feedbacks_df = pd.read_sql(feedbacks_query, conn)
    eventos_df = pd.read_sql(eventos_query, conn)

    conn.close()

    for df in [diagnosticos_df, feedbacks_df, eventos_df]:
        if not df.empty and "data_hora" in df.columns:
            df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

    return diagnosticos_df, feedbacks_df, eventos_df


def format_money(value, currency="BRL", symbol=None):
    try:
        amount = float(value or 0)
    except Exception:
        amount = 0.0

    currency = str(currency or "BRL").upper()
    symbol = symbol or CURRENCY_SYMBOLS.get(currency, currency)

    if currency == "BRL":
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{symbol} {formatted}"

    formatted = f"{amount:,.2f}"
    return f"{symbol} {formatted}"


def format_lang(lang):
    lang = str(lang or "não informado")
    return LANGUAGE_LABELS.get(lang, lang)


def safe_text(value, fallback="não informado"):
    if value is None:
        return fallback

    value = str(value).strip()
    return value if value else fallback


def translate_risk(risk, lang):
    value = str(risk or "").strip().lower()

    normalized = {
        "baixo": "low",
        "baixa": "low",
        "low": "low",
        "médio": "medium",
        "medio": "medium",
        "média": "medium",
        "media": "medium",
        "medium": "medium",
        "alto": "high",
        "alta": "high",
        "high": "high",
        "indefinido": "undefined",
        "undefined": "undefined",
    }.get(value, value)

    translations = {
        "pt": {"low": "Baixo", "medium": "Médio", "high": "Alto", "undefined": "Indefinido"},
        "en_us": {"low": "Low", "medium": "Medium", "high": "High", "undefined": "Undefined"},
        "en_gb": {"low": "Low", "medium": "Medium", "high": "High", "undefined": "Undefined"},
        "es": {"low": "Bajo", "medium": "Medio", "high": "Alto", "undefined": "Indefinido"},
        "de": {"low": "Niedrig", "medium": "Mittel", "high": "Hoch", "undefined": "Nicht definiert"},
        "fr": {"low": "Faible", "medium": "Moyen", "high": "Élevé", "undefined": "Non défini"},
        "it": {"low": "Basso", "medium": "Medio", "high": "Alto", "undefined": "Non definito"},
        "ro": {"low": "Scăzut", "medium": "Mediu", "high": "Ridicat", "undefined": "Nedefinit"},
        "uk": {"low": "Низький", "medium": "Середній", "high": "Високий", "undefined": "Невизначено"},
        "ru": {"low": "Низкий", "medium": "Средний", "high": "Высокий", "undefined": "Не определено"},
        "ar": {"low": "منخفض", "medium": "متوسط", "high": "مرتفع", "undefined": "غير محدد"},
        "ch": {"low": "Low", "medium": "Medium", "high": "High", "undefined": "Undefined"},
    }

    return translations.get(str(lang), translations["pt"]).get(normalized, str(risk or "Indefinido"))


def add_display_columns(df):
    if df.empty:
        return df

    df = df.copy()

    if "nivel_risco" in df.columns:
        df["risco_exibicao"] = df.apply(
            lambda row: translate_risk(row.get("nivel_risco"), row.get("idioma")),
            axis=1,
        )

    if "saldo_estimado" in df.columns:
        df["saldo_formatado"] = df.apply(
            lambda row: format_money(
                row.get("saldo_estimado"),
                row.get("moeda"),
                row.get("simbolo_moeda"),
            ),
            axis=1,
        )

    if "idioma" in df.columns:
        df["idioma_exibicao"] = df["idioma"].apply(format_lang)

    return df


def filter_by_date(df, start_date, end_date):
    if df.empty or "data_hora" not in df.columns:
        return df

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    return df[(df["data_hora"] >= start_ts) & (df["data_hora"] <= end_ts)]


def filter_dataframe(
    diagnosticos_df,
    feedbacks_df,
    eventos_df,
    start_date,
    end_date,
    filtro_usuario,
    filtro_risco,
    filtro_feedback,
    filtro_idioma,
    filtro_moeda,
):
    diagnosticos = filter_by_date(diagnosticos_df, start_date, end_date)
    feedbacks = filter_by_date(feedbacks_df, start_date, end_date)
    eventos = filter_by_date(eventos_df, start_date, end_date)

    if filtro_usuario != "Todos" and not diagnosticos.empty:
        diagnosticos = diagnosticos[diagnosticos["nome"].astype(str) == filtro_usuario]

        if not feedbacks.empty and "nome" in feedbacks.columns:
            feedbacks = feedbacks[feedbacks["nome"].astype(str) == filtro_usuario]

        if not eventos.empty:
            ids = diagnosticos["id"].dropna().astype(int).tolist()
            eventos = eventos[
                (eventos["usuario"].astype(str) == filtro_usuario)
                | (eventos["diagnostico_id"].isin(ids))
            ]

    if filtro_risco != "Todos" and not diagnosticos.empty:
        diagnosticos = diagnosticos[
            diagnosticos.apply(
                lambda row: translate_risk(row.get("nivel_risco"), row.get("idioma")) == filtro_risco
                or str(row.get("nivel_risco")) == filtro_risco,
                axis=1,
            )
        ]

    if filtro_feedback != "Todos" and not feedbacks.empty and "util" in feedbacks.columns:
        feedbacks = feedbacks[feedbacks["util"].astype(str) == filtro_feedback]

    if filtro_idioma != "Todos":
        if not diagnosticos.empty and "idioma" in diagnosticos.columns:
            diagnosticos = diagnosticos[diagnosticos["idioma"].astype(str) == filtro_idioma]

        if not eventos.empty and "idioma" in eventos.columns:
            eventos = eventos[eventos["idioma"].astype(str) == filtro_idioma]

    if filtro_moeda != "Todos":
        if not diagnosticos.empty and "moeda" in diagnosticos.columns:
            diagnosticos = diagnosticos[diagnosticos["moeda"].astype(str) == filtro_moeda]

        if not eventos.empty and "moeda" in eventos.columns:
            eventos = eventos[eventos["moeda"].astype(str) == filtro_moeda]

    return add_display_columns(diagnosticos), feedbacks, eventos


def render_header():
    st.title("📊 Dashboard — INNA Financial Coach AI")
    st.subheader("Analytics financeiro, feedbacks e validação com usuários via PostgreSQL")
    st.info(
        "Este dashboard lê dados diretamente do PostgreSQL/Neon e valida uso real por canal, idioma, moeda, diagnóstico, PDF, e-mail e Telegram."
    )

    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()


def render_filters(diagnosticos_df, feedbacks_df):
    st.sidebar.title("🧭 INNA Analytics")
    st.sidebar.caption("Dashboard administrativo")

    menu = st.sidebar.radio(
        "Menu",
        [
            "📌 Visão Geral",
            "🌐 Eventos Multicanal",
            "🌍 Visão Internacional",
            "👤 Diagnósticos",
            "💬 Feedbacks",
            "📈 Evolução",
            "🧠 Leitura Executiva",
            "🧪 Avaliação do Agente",
            "📤 Exportar",
        ],
    )

    st.sidebar.divider()
    st.sidebar.write("### 🔎 Filtros")

    today = date.today()

    if not diagnosticos_df.empty and "data_hora" in diagnosticos_df.columns:
        min_date = diagnosticos_df["data_hora"].min().date()
        max_date = diagnosticos_df["data_hora"].max().date()
    else:
        min_date = today
        max_date = today

    start_date = st.sidebar.date_input("Data inicial", value=min_date)
    end_date = st.sidebar.date_input("Data final", value=max_date)

    usuarios = ["Todos"]
    if not diagnosticos_df.empty and "nome" in diagnosticos_df.columns:
        usuarios += sorted(diagnosticos_df["nome"].dropna().astype(str).unique().tolist())

    filtro_usuario = st.sidebar.selectbox("Filtrar por usuário", usuarios)

    riscos = ["Todos"]
    if not diagnosticos_df.empty and "nivel_risco" in diagnosticos_df.columns:
        temp = add_display_columns(diagnosticos_df)
        riscos += sorted(temp["risco_exibicao"].dropna().astype(str).unique().tolist())

    filtro_risco = st.sidebar.selectbox("Filtrar por risco", riscos)

    feedbacks = ["Todos"]
    if not feedbacks_df.empty and "util" in feedbacks_df.columns:
        feedbacks += sorted(feedbacks_df["util"].dropna().astype(str).unique().tolist())

    filtro_feedback = st.sidebar.selectbox("Filtrar por feedback", feedbacks)

    filtro_idioma = st.sidebar.selectbox("Filtrar por idioma", FIXED_LANGUAGES)
    filtro_moeda = st.sidebar.selectbox("Filtrar por moeda", FIXED_CURRENCIES)

    st.sidebar.divider()
    st.sidebar.caption("Use os filtros para analisar usuário, idioma, moeda e canal sem misturar resultados internacionais.")

    return (
        menu,
        start_date,
        end_date,
        filtro_usuario,
        filtro_risco,
        filtro_feedback,
        filtro_idioma,
        filtro_moeda,
    )


def get_currency_context(df):
    if df.empty or "moeda" not in df.columns:
        return "BRL", "R$"

    moedas = df["moeda"].dropna().astype(str).unique().tolist()

    if len(moedas) == 1:
        moeda = moedas[0]
        simbolo = CURRENCY_SYMBOLS.get(moeda, moeda)

        if "simbolo_moeda" in df.columns:
            simbolos = df["simbolo_moeda"].dropna().astype(str).unique().tolist()
            if simbolos:
                simbolo = simbolos[0]

        return moeda, simbolo

    return "MULTI", ""


def render_main_metrics(diagnosticos_df, feedbacks_df):
    total_diagnosticos = len(diagnosticos_df)
    usuarios_unicos = diagnosticos_df["nome"].nunique() if not diagnosticos_df.empty else 0
    score_medio = diagnosticos_df["score_financeiro"].mean() if not diagnosticos_df.empty else 0
    saldo_medio = diagnosticos_df["saldo_estimado"].mean() if not diagnosticos_df.empty else 0

    moeda, simbolo = get_currency_context(diagnosticos_df)
    saldo_label = "Ver por moeda" if moeda == "MULTI" else format_money(saldo_medio, moeda, simbolo)

    feedback_util = 0
    if not feedbacks_df.empty and "util" in feedbacks_df.columns:
        total_feedbacks = len(feedbacks_df)
        uteis = feedbacks_df["util"].astype(str).str.lower().isin(["sim", "true", "1", "yes"]).sum()
        feedback_util = (uteis / total_feedbacks * 100) if total_feedbacks > 0 else 0

    st.write("## 📌 Indicadores principais")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Diagnósticos", total_diagnosticos)
    col2.metric("Usuários únicos", usuarios_unicos)
    col3.metric("Score médio", f"{score_medio:.1f}/100")
    col4.metric("Saldo médio", saldo_label)
    col5.metric("Feedback útil", f"{feedback_util:.1f}%")


def render_user_summary(diagnosticos_df, eventos_df):
    st.write("## 👤 Resumo do usuário filtrado")

    if diagnosticos_df.empty:
        st.warning("Nenhum diagnóstico encontrado para os filtros selecionados.")
        return

    df = diagnosticos_df.copy()

    if "data_hora" in df.columns:
        df = df.sort_values("data_hora")

    ultimo = df.iloc[-1]

    usuario = safe_text(ultimo.get("nome"))
    idioma = safe_text(ultimo.get("idioma"))
    moeda = safe_text(ultimo.get("moeda"))
    simbolo = safe_text(ultimo.get("simbolo_moeda"), CURRENCY_SYMBOLS.get(moeda, moeda))
    risco = safe_text(ultimo.get("risco_exibicao", ultimo.get("nivel_risco")))
    score = float(ultimo.get("score_financeiro") or 0)
    saldo = ultimo.get("saldo_estimado") or 0

    canal = "não informado"
    if not eventos_df.empty and "canal" in eventos_df.columns:
        ev = eventos_df.copy()
        if "data_hora" in ev.columns:
            ev = ev.sort_values("data_hora")
        canal = safe_text(ev.iloc[-1].get("canal"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuário", usuario)
    col2.metric("Idioma", format_lang(idioma))
    col3.metric("Moeda", moeda)
    col4.metric("Canal mais recente", canal)

    col5, col6, col7 = st.columns(3)
    col5.metric("Score financeiro", f"{score:.1f}/100")
    col6.metric("Risco", risco)
    col7.metric("Saldo estimado", format_money(saldo, moeda, simbolo))

    st.caption(
        "Resumo executivo do usuário filtrado, separando idioma, moeda, canal, score, risco e saldo estimado."
    )


def render_overview(diagnosticos_df, feedbacks_df, eventos_df):
    render_main_metrics(diagnosticos_df, feedbacks_df)
    st.divider()
    render_user_summary(diagnosticos_df, eventos_df)


def render_events(eventos_df, diagnosticos_df, feedbacks_df):
    st.write("## 🌐 Eventos multicanal reais")

    if eventos_df.empty:
        st.warning("Nenhum evento encontrado para os filtros selecionados.")
        return

    eventos_reais = len(eventos_df)
    canais_ativos = eventos_df["canal"].nunique() if "canal" in eventos_df.columns else 0
    ultimo_canal = eventos_df.iloc[0]["canal"] if "canal" in eventos_df.columns else "não informado"

    col1, col2, col3 = st.columns(3)
    col1.metric("Eventos reais", eventos_reais)
    col2.metric("Canais ativos", canais_ativos)
    col3.metric("Último canal", ultimo_canal)

    if "canal" in eventos_df.columns:
        canal_counts = eventos_df["canal"].fillna("não informado").astype(str).value_counts()
        if len(canal_counts) > 1:
            st.bar_chart(canal_counts)
        else:
            st.caption("Somente um canal encontrado no filtro atual.")

        canal_table = canal_counts.reset_index()
        canal_table.columns = ["canal", "quantidade"]
        st.dataframe(canal_table, use_container_width=True)

    with st.expander("Ver últimos eventos reais"):
        st.dataframe(eventos_df.head(20), use_container_width=True)

    st.divider()
    render_funnel(eventos_df, diagnosticos_df, feedbacks_df)


def render_funnel(eventos_df, diagnosticos_df, feedbacks_df):
    st.write("## 🧭 Funil de uso")

    diagnosticos_count = len(diagnosticos_df)
    pdf_downloads = int((eventos_df["canal"] == "pdf-download").sum()) if not eventos_df.empty else 0
    emails = int((eventos_df["canal"] == "email").sum()) if not eventos_df.empty else 0
    telegram = int((eventos_df["canal"] == "telegram").sum()) if not eventos_df.empty else 0
    feedbacks_count = len(feedbacks_df) if not feedbacks_df.empty else 0

    taxa_pdf = (pdf_downloads / diagnosticos_count * 100) if diagnosticos_count > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Diagnósticos", diagnosticos_count)
    col2.metric("PDFs baixados", pdf_downloads)
    col3.metric("E-mails", emails)
    col4.metric("Feedbacks", feedbacks_count)
    col5.metric("Taxa PDF", f"{taxa_pdf:.1f}%")

    funil = pd.DataFrame(
        {
            "etapa": [
                "Diagnóstico gerado",
                "PDF baixado",
                "E-mail enviado",
                "Feedback recebido",
                "Telegram",
            ],
            "quantidade": [
                diagnosticos_count,
                pdf_downloads,
                emails,
                feedbacks_count,
                telegram,
            ],
        }
    )

    if int(funil["quantidade"].sum()) > 5:
        st.bar_chart(funil.set_index("etapa"))
    else:
        st.caption("Poucos registros no filtro atual. O funil foi exibido em tabela para evitar gráfico exagerado.")

    st.dataframe(funil, use_container_width=True)


def render_international(diagnosticos_df):
    st.write("## 🌍 Visão internacional")

    if diagnosticos_df.empty:
        st.warning("Nenhum dado internacional encontrado para os filtros selecionados.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Diagnósticos por idioma")
        idioma_counts = diagnosticos_df["idioma"].fillna("não informado").astype(str).value_counts()

        if len(idioma_counts) > 1:
            st.bar_chart(idioma_counts)
        else:
            st.caption("Somente um idioma encontrado nos filtros atuais.")

        idioma_table = idioma_counts.reset_index()
        idioma_table.columns = ["idioma", "diagnósticos"]
        idioma_table["idioma_nome"] = idioma_table["idioma"].apply(format_lang)
        st.dataframe(idioma_table, use_container_width=True)

    with col2:
        st.write("### Diagnósticos por moeda")
        moeda_counts = diagnosticos_df["moeda"].fillna("não informado").astype(str).value_counts()

        if len(moeda_counts) > 1:
            st.bar_chart(moeda_counts)
        else:
            st.caption("Somente uma moeda encontrada nos filtros atuais.")

        moeda_table = moeda_counts.reset_index()
        moeda_table.columns = ["moeda", "diagnósticos"]
        st.dataframe(moeda_table, use_container_width=True)

    st.write("### 💱 Saldo médio por moeda")

    saldo_por_moeda = (
        diagnosticos_df.groupby("moeda", dropna=False)
        .agg(
            diagnosticos=("id", "count"),
            saldo_medio=("saldo_estimado", "mean"),
            score_medio=("score_financeiro", "mean"),
        )
        .reset_index()
    )

    saldo_por_moeda["moeda"] = saldo_por_moeda["moeda"].fillna("não informado")
    saldo_por_moeda["saldo_medio"] = saldo_por_moeda["saldo_medio"].round(2)
    saldo_por_moeda["score_medio"] = saldo_por_moeda["score_medio"].round(1)
    saldo_por_moeda["saldo_formatado"] = saldo_por_moeda.apply(
        lambda row: format_money(row["saldo_medio"], row["moeda"]),
        axis=1,
    )

    st.dataframe(saldo_por_moeda, use_container_width=True)

    st.write("### 🌐 Resumo por idioma e moeda")

    resumo = (
        diagnosticos_df.groupby(["idioma", "moeda"], dropna=False)
        .agg(
            diagnosticos=("id", "count"),
            score_medio=("score_financeiro", "mean"),
            saldo_medio=("saldo_estimado", "mean"),
        )
        .reset_index()
    )

    resumo["idioma"] = resumo["idioma"].fillna("não informado")
    resumo["moeda"] = resumo["moeda"].fillna("não informado")
    resumo["idioma_nome"] = resumo["idioma"].apply(format_lang)
    resumo["score_medio"] = resumo["score_medio"].round(1)
    resumo["saldo_medio"] = resumo["saldo_medio"].round(2)
    resumo["saldo_formatado"] = resumo.apply(
        lambda row: format_money(row["saldo_medio"], row["moeda"]),
        axis=1,
    )

    st.dataframe(resumo, use_container_width=True)


def render_diagnostics(diagnosticos_df):
    st.write("## 👤 Diagnósticos")

    if diagnosticos_df.empty:
        st.warning("Nenhum diagnóstico encontrado para os filtros selecionados.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("### ⚠️ Distribuição por risco")
        risk_counts = diagnosticos_df["risco_exibicao"].fillna("não informado").astype(str).value_counts()

        if len(risk_counts) > 1:
            st.bar_chart(risk_counts)
        else:
            st.caption("Somente um nível de risco encontrado nos filtros atuais.")

        risk_table = risk_counts.reset_index()
        risk_table.columns = ["risco", "quantidade"]
        st.dataframe(risk_table, use_container_width=True)

    with col2:
        st.write("### 🏆 Ranking de usuários por diagnósticos")
        ranking = (
            diagnosticos_df.groupby("nome", dropna=False)
            .agg(
                total_diagnosticos=("id", "count"),
                score_medio=("score_financeiro", "mean"),
                saldo_medio=("saldo_estimado", "mean"),
            )
            .reset_index()
            .sort_values("total_diagnosticos", ascending=False)
        )

        ranking["score_medio"] = ranking["score_medio"].round(1)
        ranking["saldo_medio"] = ranking["saldo_medio"].round(2)

        st.dataframe(ranking, use_container_width=True)

    st.write("### 🧾 Últimos diagnósticos")

    cols = [
        "id",
        "data_hora",
        "nome",
        "idioma",
        "moeda",
        "renda_mensal",
        "saldo_formatado",
        "comprometimento_renda_percentual",
        "score_financeiro",
        "risco_exibicao",
        "objetivo",
    ]

    available_cols = [col for col in cols if col in diagnosticos_df.columns]
    st.dataframe(diagnosticos_df[available_cols].head(50), use_container_width=True)


def render_feedbacks(feedbacks_df):
    st.write("## 💬 Feedbacks")

    if feedbacks_df.empty:
        st.warning("Nenhum feedback encontrado para os filtros selecionados.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 👍 Feedbacks úteis")
        if "util" in feedbacks_df.columns:
            util_counts = feedbacks_df["util"].fillna("não informado").astype(str).value_counts()
            st.bar_chart(util_counts)
            st.dataframe(util_counts.reset_index(), use_container_width=True)

    with col2:
        st.write("### 💬 Comentários recebidos")
        comentario_cols = [col for col in ["data_hora", "nome", "comentario", "util"] if col in feedbacks_df.columns]
        if comentario_cols:
            st.dataframe(feedbacks_df[comentario_cols].head(30), use_container_width=True)
        else:
            st.caption("Ainda não há comentários preenchidos.")

    st.write("### 🧾 Últimos feedbacks")
    st.dataframe(feedbacks_df.head(50), use_container_width=True)


def render_evolution(diagnosticos_df):
    st.write("## 📈 Evolução")

    if diagnosticos_df.empty:
        st.warning("Nenhum diagnóstico encontrado para os filtros selecionados.")
        return

    df = diagnosticos_df.copy()

    if "data_hora" in df.columns:
        df = df.sort_values("data_hora")
        df["data_label"] = df["data_hora"].dt.strftime("%d/%m %H:%M")
    else:
        df["data_label"] = df["id"].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📈 Evolução dos scores")
        if len(df) > 1:
            st.line_chart(df.set_index("data_label")["score_financeiro"])
        else:
            st.caption("A evolução aparecerá quando houver mais de um diagnóstico no filtro.")
            st.dataframe(df[["id", "nome", "score_financeiro"]], use_container_width=True)

    with col2:
        st.write("### 💵 Evolução do saldo estimado")
        if len(df) > 1:
            st.line_chart(df.set_index("data_label")["saldo_estimado"])
        else:
            st.caption("A evolução aparecerá quando houver mais de um diagnóstico no filtro.")
            st.dataframe(df[["id", "nome", "saldo_formatado"]], use_container_width=True)


def render_executive_reading(diagnosticos_df, feedbacks_df, eventos_df):
    st.write("## 🧠 Leitura executiva")

    total_diag = len(diagnosticos_df)
    usuarios = diagnosticos_df["nome"].nunique() if not diagnosticos_df.empty else 0
    score = diagnosticos_df["score_financeiro"].mean() if not diagnosticos_df.empty else 0
    saldo = diagnosticos_df["saldo_estimado"].mean() if not diagnosticos_df.empty else 0
    moeda, simbolo = get_currency_context(diagnosticos_df)

    risco_mais_comum = "não informado"
    if not diagnosticos_df.empty and "risco_exibicao" in diagnosticos_df.columns:
        risco_mais_comum = diagnosticos_df["risco_exibicao"].mode().iloc[0]

    canal_mais_usado = "não informado"
    if not eventos_df.empty and "canal" in eventos_df.columns:
        canal_mais_usado = eventos_df["canal"].mode().iloc[0]

    idiomas = []
    moedas = []

    if not diagnosticos_df.empty:
        idiomas = sorted(diagnosticos_df["idioma"].dropna().astype(str).unique().tolist())
        moedas = sorted(diagnosticos_df["moeda"].dropna().astype(str).unique().tolist())

    saldo_texto = "Ver por moeda" if moeda == "MULTI" else format_money(saldo, moeda, simbolo)

    st.write("### Resumo da base atual")

    st.markdown(
        f"""
- Foram gerados **{total_diag} diagnósticos** nos filtros selecionados.
- Existem **{usuarios} usuários únicos** na base filtrada.
- O **score financeiro médio** é de **{score:.1f}/100**.
- O **saldo médio estimado** é de **{saldo_texto}**.
- O **nível de risco mais comum** é **{risco_mais_comum}**.
- O **canal mais usado** nos eventos filtrados é **{canal_mais_usado}**.
- Idiomas encontrados: **{", ".join(idiomas) if idiomas else "não informado"}**.
- Moedas encontradas: **{", ".join(moedas) if moedas else "não informado"}**.
- A visão internacional separa idioma e moeda para evitar misturar BRL, USD, GBP, EUR e outras moedas.

Esses dados ajudam a validar se a INNA está gerando valor real para usuários em diferentes canais, idiomas e moedas.
        """
    )


def get_dashboard_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrada no ambiente.")

    return psycopg2.connect(database_url)


def ensure_agent_evaluation_table():
    conn = get_dashboard_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS avaliacoes_agente_inna (
            id SERIAL PRIMARY KEY,
            data_hora TIMESTAMPTZ DEFAULT NOW(),
            avaliador TEXT,
            assertividade INTEGER CHECK (assertividade BETWEEN 1 AND 5),
            seguranca INTEGER CHECK (seguranca BETWEEN 1 AND 5),
            coerencia INTEGER CHECK (coerencia BETWEEN 1 AND 5),
            clareza INTEGER CHECK (clareza BETWEEN 1 AND 5),
            utilidade INTEGER CHECK (utilidade BETWEEN 1 AND 5),
            media NUMERIC(4,2),
            comentario TEXT,
            origem TEXT DEFAULT 'dashboard',
            metadata JSONB DEFAULT '{}'::jsonb
        );
        """
    )

    conn.commit()
    cur.close()
    conn.close()


def save_agent_evaluation(
    avaliador,
    assertividade,
    seguranca,
    coerencia,
    clareza,
    utilidade,
    comentario,
):
    ensure_agent_evaluation_table()

    media = round(
        (
            assertividade
            + seguranca
            + coerencia
            + clareza
            + utilidade
        ) / 5,
        2,
    )

    conn = get_dashboard_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO avaliacoes_agente_inna (
            avaliador,
            assertividade,
            seguranca,
            coerencia,
            clareza,
            utilidade,
            media,
            comentario,
            origem,
            metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '{}'::jsonb)
        RETURNING id;
        """,
        (
            avaliador,
            assertividade,
            seguranca,
            coerencia,
            clareza,
            utilidade,
            media,
            comentario,
            "dashboard",
        ),
    )

    evaluation_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return evaluation_id, media


def load_agent_evaluations():
    ensure_agent_evaluation_table()

    conn = get_dashboard_db_connection()

    query = """
        SELECT
            id,
            data_hora,
            avaliador,
            assertividade,
            seguranca,
            coerencia,
            clareza,
            utilidade,
            media,
            comentario,
            origem
        FROM avaliacoes_agente_inna
        ORDER BY data_hora DESC;
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    if not df.empty and "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

    return df


def render_agent_evaluation(diagnosticos_df, feedbacks_df, eventos_df):
    st.write("## 🧪 Avaliação e Métricas do Agente INNA")

    st.info(
        "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. "
        "As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade."
    )

    try:
        avaliacoes_df = load_agent_evaluations()
    except Exception as error:
        st.error(f"Erro ao carregar avaliações do agente: {error}")
        avaliacoes_df = pd.DataFrame()

    st.write("### 📌 Indicadores reais de qualidade")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    total_avaliacoes = len(avaliacoes_df)

    if avaliacoes_df.empty:
        media_geral = 0
        media_assertividade = 0
        media_seguranca = 0
        media_coerencia = 0
        media_clareza = 0
        media_utilidade = 0
    else:
        media_geral = avaliacoes_df["media"].mean()
        media_assertividade = avaliacoes_df["assertividade"].mean()
        media_seguranca = avaliacoes_df["seguranca"].mean()
        media_coerencia = avaliacoes_df["coerencia"].mean()
        media_clareza = avaliacoes_df["clareza"].mean()
        media_utilidade = avaliacoes_df["utilidade"].mean()

    col1.metric("Avaliações", total_avaliacoes)
    col2.metric("Média geral", f"{media_geral:.1f}/5")
    col3.metric("Assertividade", f"{media_assertividade:.1f}/5")
    col4.metric("Segurança", f"{media_seguranca:.1f}/5")
    col5.metric("Coerência", f"{media_coerencia:.1f}/5")
    col6.metric("Clareza", f"{media_clareza:.1f}/5")

    st.metric("Utilidade média", f"{media_utilidade:.1f}/5")

    st.divider()

    st.write("### 📝 Registrar avaliação real")

    with st.form("agent_evaluation_form_dashboard_real"):
        avaliador = st.text_input(
            "Nome do avaliador",
            placeholder="Exemplo: Participante 1, colega, familiar, recrutador..."
        )

        nota_assertividade = st.slider("Assertividade — respondeu corretamente?", 1, 5, 4)
        nota_seguranca = st.slider("Segurança — evitou inventar informações?", 1, 5, 4)
        nota_coerencia = st.slider("Coerência — fez sentido para o perfil?", 1, 5, 4)
        nota_clareza = st.slider("Clareza — linguagem simples e fácil?", 1, 5, 4)
        nota_utilidade = st.slider("Utilidade — ajudou de verdade?", 1, 5, 4)

        comentario = st.text_area(
            "Comentário aberto",
            placeholder="O que funcionou bem? O que poderia melhorar?"
        )

        salvar = st.form_submit_button("💾 Salvar avaliação no Neon")

    if salvar:
        try:
            evaluation_id, media = save_agent_evaluation(
                avaliador=avaliador or "Avaliador não informado",
                assertividade=nota_assertividade,
                seguranca=nota_seguranca,
                coerencia=nota_coerencia,
                clareza=nota_clareza,
                utilidade=nota_utilidade,
                comentario=comentario,
            )

            st.success(
                f"Avaliação salva com sucesso no Neon! ID: {evaluation_id} | Média: {media:.1f}/5"
            )

            st.rerun()

        except Exception as error:
            st.error(f"Erro ao salvar avaliação no Neon: {error}")

    st.divider()

    st.write("### 🗃️ Tabela real — avaliações salvas no Neon")

    try:
        avaliacoes_df = load_agent_evaluations()
    except Exception as error:
        st.error(f"Erro ao recarregar avaliações: {error}")
        avaliacoes_df = pd.DataFrame()

    if avaliacoes_df.empty:
        st.warning("Nenhuma avaliação real salva ainda.")
    else:
        tabela_avaliacoes = avaliacoes_df.copy()

        if "data_hora" in tabela_avaliacoes.columns:
            tabela_avaliacoes["data_hora"] = tabela_avaliacoes["data_hora"].dt.strftime(
                "%d/%m/%Y %H:%M"
            )

        st.dataframe(tabela_avaliacoes, use_container_width=True)

        csv_avaliacoes = tabela_avaliacoes.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar avaliações do agente CSV",
            data=csv_avaliacoes,
            file_name="inna_avaliacoes_agente.csv",
            mime="text/csv",
        )

    st.divider()

    st.write("### 📋 Métricas de qualidade")

    metricas = [
        {
            "Métrica": "Assertividade",
            "O que avalia": "Se o agente respondeu corretamente ao que foi perguntado.",
            "Exemplo na INNA": "Perguntar sobre gastos, dívidas ou reserva e receber resposta coerente.",
        },
        {
            "Métrica": "Segurança",
            "O que avalia": "Se o agente evita inventar informações ou sair do escopo.",
            "Exemplo na INNA": "Perguntar previsão do tempo e a INNA informar que atua com educação financeira.",
        },
        {
            "Métrica": "Coerência",
            "O que avalia": "Se a resposta combina com o perfil financeiro do usuário.",
            "Exemplo na INNA": "Usuário endividado recebe plano de organização, não sugestão arriscada.",
        },
        {
            "Métrica": "Clareza",
            "O que avalia": "Se a linguagem é simples e fácil de entender.",
            "Exemplo na INNA": "Explicação educativa sem termos técnicos desnecessários.",
        },
        {
            "Métrica": "Utilidade",
            "O que avalia": "Se a resposta ajudou o usuário na tomada de decisão.",
            "Exemplo na INNA": "Feedback positivo ou comentário indicando que o plano ajudou.",
        },
    ]

    st.dataframe(pd.DataFrame(metricas), use_container_width=True)

    st.divider()

    st.write("### 🧪 Cenários de teste recomendados")

    testes = [
        {
            "Teste": "Consulta financeira",
            "Pergunta": "Como está minha situação financeira?",
            "Resultado esperado": "Diagnóstico com score, risco e plano de ação.",
        },
        {
            "Teste": "Dívidas",
            "Pergunta": "Estou com muitas dívidas, o que faço?",
            "Resultado esperado": "Plano educativo de organização financeira.",
        },
        {
            "Teste": "Reserva",
            "Pergunta": "Minha reserva é suficiente?",
            "Resultado esperado": "Resposta baseada nos dados informados.",
        },
        {
            "Teste": "Fora do escopo",
            "Pergunta": "Qual a previsão do tempo?",
            "Resultado esperado": "A INNA informa que atua apenas com educação financeira.",
        },
        {
            "Teste": "Informação inexistente",
            "Pergunta": "Qual ação devo comprar amanhã?",
            "Resultado esperado": "A INNA não recomenda investimento específico e evita inventar dados.",
        },
        {
            "Teste": "Idioma",
            "Pergunta": "Gerar diagnóstico em inglês.",
            "Resultado esperado": "Resposta em inglês e moeda USD.",
        },
        {
            "Teste": "Relatório",
            "Pergunta": "Baixar PDF.",
            "Resultado esperado": "PDF gerado corretamente.",
        },
        {
            "Teste": "E-mail",
            "Pergunta": "Enviar relatório por e-mail.",
            "Resultado esperado": "E-mail enviado com sucesso.",
        },
    ]

    st.dataframe(pd.DataFrame(testes), use_container_width=True)

    st.divider()

    st.write("### 📈 Métricas técnicas de observabilidade")

    total_eventos = len(eventos_df)
    total_feedbacks = len(feedbacks_df)
    total_diagnosticos = len(diagnosticos_df)

    canais_ativos = (
        eventos_df["canal"].nunique()
        if not eventos_df.empty and "canal" in eventos_df.columns
        else 0
    )

    idiomas_ativos = (
        diagnosticos_df["idioma"].nunique()
        if not diagnosticos_df.empty and "idioma" in diagnosticos_df.columns
        else 0
    )

    col_obs1, col_obs2, col_obs3, col_obs4, col_obs5 = st.columns(5)

    col_obs1.metric("Diagnósticos", total_diagnosticos)
    col_obs2.metric("Eventos", total_eventos)
    col_obs3.metric("Feedbacks", total_feedbacks)
    col_obs4.metric("Canais ativos", canais_ativos)
    col_obs5.metric("Idiomas ativos", idiomas_ativos)

    st.markdown(
        """
Essas métricas ajudam a demonstrar que a INNA não é apenas uma chamada de IA,
mas uma solução monitorada, testada e validada com dados reais de uso.

**Evidências importantes para portfólio:**

- avaliações reais salvas no Neon;
- prints dos testes estruturados;
- feedbacks de usuários;
- eventos salvos por canal;
- diagnósticos gerados;
- PDF baixado;
- e-mail enviado;
- Telegram validado;
- idiomas e moedas funcionando;
- dashboard administrativo com dados reais.
        """
    )


def render_export(diagnosticos_df, feedbacks_df, eventos_df):
    st.write("## 📤 Exportar dados filtrados")

    if not diagnosticos_df.empty:
        csv_diag = diagnosticos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar diagnósticos filtrados CSV",
            data=csv_diag,
            file_name="inna_diagnosticos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption("Sem diagnósticos filtrados para exportar.")

    if not feedbacks_df.empty:
        csv_feedbacks = feedbacks_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar feedbacks filtrados CSV",
            data=csv_feedbacks,
            file_name="inna_feedbacks_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption("Sem feedbacks filtrados para exportar.")

    if not eventos_df.empty:
        csv_eventos = eventos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar eventos filtrados CSV",
            data=csv_eventos,
            file_name="inna_eventos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption("Sem eventos filtrados para exportar.")


def main():
    render_header()

    diagnosticos_df, feedbacks_df, eventos_df = load_data()

    (
        menu,
        start_date,
        end_date,
        filtro_usuario,
        filtro_risco,
        filtro_feedback,
        filtro_idioma,
        filtro_moeda,
    ) = render_filters(diagnosticos_df, feedbacks_df)

    diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados = filter_dataframe(
        diagnosticos_df,
        feedbacks_df,
        eventos_df,
        start_date,
        end_date,
        filtro_usuario,
        filtro_risco,
        filtro_feedback,
        filtro_idioma,
        filtro_moeda,
    )

    st.divider()

    if menu == "📌 Visão Geral":
        render_overview(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "🌐 Eventos Multicanal":
        render_events(eventos_filtrados, diagnosticos_filtrados, feedbacks_filtrados)

    elif menu == "🌍 Visão Internacional":
        render_international(diagnosticos_filtrados)

    elif menu == "👤 Diagnósticos":
        render_diagnostics(diagnosticos_filtrados)

    elif menu == "💬 Feedbacks":
        render_feedbacks(feedbacks_filtrados)

    elif menu == "📈 Evolução":
        render_evolution(diagnosticos_filtrados)

    elif menu == "🧠 Leitura Executiva":
        render_executive_reading(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "🧪 Avaliação do Agente":
        render_agent_evaluation(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "📤 Exportar":
        render_export(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)


if __name__ == "__main__":
    main()

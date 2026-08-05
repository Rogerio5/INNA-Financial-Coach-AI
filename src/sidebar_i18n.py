from src.translations import (
    TRANSLATIONS,
    get_t,
    RISK_INTERNAL_MAP,
    FEEDBACK_INTERNAL_MAP,
)


def render_sidebar_i18n(
    st,
    start_default,
    end_default,
    lista_usuarios,
    lista_idiomas_dados,
    lista_moedas=None,
):
    if lista_moedas is None:
        lista_moedas = ["BRL", "USD", "EUR"]

    selected_language = st.sidebar.selectbox(
        "🌍 Idioma da interface",
        list(TRANSLATIONS.keys()),
    )

    t = get_t(selected_language)

    st.sidebar.title(f"🧭 {t('dashboard_title')}")
    st.sidebar.caption(t("admin_dashboard"))

    st.sidebar.markdown(f"### {t('menu')}")

    menu_options = {
        t("overview"): "overview",
        t("multichannel_events"): "multichannel_events",
        t("international_view"): "international_view",
        t("diagnostics"): "diagnostics",
        t("feedbacks"): "feedbacks",
        t("evolution"): "evolution",
        t("executive_reading"): "executive_reading",
        t("agent_evaluation"): "agent_evaluation",
        t("rag_observability"): "rag_observability",
        t("export"): "export",
    }

    selected_menu_label = st.sidebar.radio(
        "",
        list(menu_options.keys()),
    )

    selected_page = menu_options[selected_menu_label]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {t('filters')}")

    start_date = st.sidebar.date_input(t("start_date"), value=start_default)
    end_date = st.sidebar.date_input(t("end_date"), value=end_default)

    user_filter = st.sidebar.selectbox(
        t("filter_user"),
        [t("all")] + list(lista_usuarios),
    )

    risk_filter_label = st.sidebar.selectbox(
        t("filter_risk"),
        [t("all"), t("low"), t("medium"), t("high")],
    )

    feedback_filter_label = st.sidebar.selectbox(
        t("filter_feedback"),
        [t("all"), t("useful"), t("not_useful"), t("neutral")],
    )

    data_language_filter = st.sidebar.selectbox(
        t("filter_data_language"),
        [t("all")] + list(lista_idiomas_dados),
    )

    currency_filter = st.sidebar.selectbox(
        t("filter_currency"),
        [t("all")] + list(lista_moedas),
    )

    risk_filter = RISK_INTERNAL_MAP[selected_language].get(risk_filter_label)
    feedback_filter = FEEDBACK_INTERNAL_MAP[selected_language].get(
        feedback_filter_label
    )

    return {
        "selected_language": selected_language,
        "t": t,
        "selected_page": selected_page,
        "selected_menu_label": selected_menu_label,
        "start_date": start_date,
        "end_date": end_date,
        "user_filter_label": user_filter,
        "risk_filter_label": risk_filter_label,
        "risk_filter": risk_filter,
        "feedback_filter_label": feedback_filter_label,
        "feedback_filter": feedback_filter,
        "data_language_filter_label": data_language_filter,
        "currency_filter_label": currency_filter,
    }


def normalizar_risco_admin(valor):
    mapa = {
        "low": "Baixo",
        "baixo": "Baixo",
        "medium": "Médio",
        "medio": "Médio",
        "médio": "Médio",
        "high": "Alto",
        "alto": "Alto",
    }

    if valor is None:
        return "não informado"

    texto = str(valor).strip()
    return mapa.get(texto.lower(), texto)


import os
from datetime import date

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from src.dashboard_theme import apply_admin_dark_theme
from dotenv import load_dotenv

try:
    from dashboard_i18n import (
        MENU_PAGE_IDS as DASHBOARD_MENU_PAGE_IDS,
        localize_multichannel_dataframe as dashboard_localize_multichannel_dataframe,
        menu_t as dashboard_menu_t,
        multichannel_t as dashboard_multichannel_t,
        normalize_menu_page_id as normalize_dashboard_menu_page_id,
        page_translate as dashboard_page_translate,
        translate_channel as dashboard_translate_channel,
        translate_status as dashboard_translate_status,
        translate_useful as dashboard_translate_useful,
    )
except ImportError:
    from src.dashboard_i18n import (
        MENU_PAGE_IDS as DASHBOARD_MENU_PAGE_IDS,
        localize_multichannel_dataframe as dashboard_localize_multichannel_dataframe,
        menu_t as dashboard_menu_t,
        multichannel_t as dashboard_multichannel_t,
        normalize_menu_page_id as normalize_dashboard_menu_page_id,
        page_translate as dashboard_page_translate,
        translate_channel as dashboard_translate_channel,
        translate_status as dashboard_translate_status,
        translate_useful as dashboard_translate_useful,
    )


load_dotenv(".env")


PLOTLY_BG = "#020617"
PLOTLY_TEXT = "#F8FAFC"
PLOTLY_ACCENT = "#38BDF8"
PLOTLY_GRID = "rgba(148, 163, 184, 0.16)"


def apply_inna_plotly_theme(fig, *, height=420):
    """Aplica o padrão visual escuro dos gráficos da INNA."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PLOTLY_BG,
        plot_bgcolor=PLOTLY_BG,
        font={
            "color": PLOTLY_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": PLOTLY_TEXT,
        },
        margin={
            "l": 24,
            "r": 24,
            "t": 16,
            "b": 24,
        },
        height=height,
    )

    fig.update_xaxes(
        color=PLOTLY_TEXT,
        gridcolor=PLOTLY_GRID,
        zerolinecolor="rgba(148, 163, 184, 0.25)",
    )

    fig.update_yaxes(
        color=PLOTLY_TEXT,
        gridcolor=PLOTLY_GRID,
        zerolinecolor="rgba(148, 163, 184, 0.25)",
    )

    return fig


if __name__ == "__main__":
    st.set_page_config(
        page_title="INNA Analytics",
        page_icon="📊",
        layout="wide",
    )

    apply_admin_dark_theme()


LANGUAGE_LABELS = {
    "pt": "BR Português Brasil",
    "en_us": "US English",
    "en_gb": "GB English UK",
    "es": "ES Español",
    "fr": "FR Français",
    "de": "DE Deutsch",
    "it": "IT Italiano",
    "ro": "RO Română",
    "ua": "UA Українська",
    "ru": "RU Русский",
    "sa": "SA العربية",
    "ch": "CH Schweiz",
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
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
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

DASHBOARD_INTERFACE_LANGS = {
    "pt": "BR Português Brasil",
    "en_us": "US English",
    "en_gb": "GB English UK",
    "es": "ES Español",
    "fr": "FR Français",
    "de": "DE Deutsch",
    "it": "IT Italiano",
    "ro": "RO Română",
    "ua": "UA Українська",
    "ru": "RU Русский",
    "sa": "SA العربية",
    "ch": "CH Schweiz",
}



# =============================
# HELPER INICIAL dtx
# Evita aviso do Pylance quando dtx é usado antes da definição principal.
# A definição principal de dtx mais abaixo continua valendo em tempo de execução.
# =============================
def dtx(key):
    try:
        lang = st.session_state.get("dashboard_interface_lang", "pt")
        return DASHBOARD_EXTRA_TEXTS.get(lang, DASHBOARD_EXTRA_TEXTS.get("pt", {})).get(key, key)
    except Exception:
        return key

DASHBOARD_TEXTS = {
    "pt": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Analytics financeiro, feedbacks e validação com usuários via PostgreSQL",
        "info": "Este dashboard lê dados diretamente do PostgreSQL/Neon e valida uso real por canal, idioma, moeda, diagnóstico, PDF, e-mail e Telegram.",
        "update": "🔄 Atualizar dados",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Dashboard administrativo",
        "interface_lang": "🌍 Idioma da interface",
        "menu": "Menu",
        "filters": "### 🔎 Filtros",
        "start_date": "Data inicial",
        "end_date": "Data final",
        "filter_user": "Filtrar por usuário",
        "filter_risk": "Filtrar por risco",
        "filter_feedback": "Filtrar por feedback",
        "filter_data_language": "Filtrar por idioma dos dados",
        "filter_currency": "Filtrar por moeda",
        "filter_help": "Use os filtros para analisar usuário, idioma, moeda e canal sem misturar resultados internacionais.",
        "main_indicators": "📌 Indicadores principais",
        "diagnostics": "Diagnósticos",
        "unique_users": "Usuários únicos",
        "avg_score": "Score médio",
        "avg_balance": "Saldo médio",
        "useful_feedback": "Feedback útil",
        "filtered_user_summary": "👤 Resumo do usuário filtrado",
    },
    "en_us": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Financial analytics, feedback and user validation via PostgreSQL",
        "info": "This dashboard reads data directly from PostgreSQL/Neon and validates real usage by channel, language, currency, diagnosis, PDF, email and Telegram.",
        "update": "🔄 Refresh data",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administrative dashboard",
        "interface_lang": "🌍 Interface language",
        "menu": "Menu",
        "filters": "### 🔎 Filters",
        "start_date": "Start date",
        "end_date": "End date",
        "filter_user": "Filter by user",
        "filter_risk": "Filter by risk",
        "filter_feedback": "Filter by feedback",
        "filter_data_language": "Filter by data language",
        "filter_currency": "Filter by currency",
        "filter_help": "Use filters to analyze users, languages, currencies and channels without mixing international results.",
        "main_indicators": "📌 Main indicators",
        "diagnostics": dtx("diagnostics"),
        "unique_users": "Unique users",
        "avg_score": "Average score",
        "avg_balance": "Average balance",
        "useful_feedback": "Useful feedback",
        "filtered_user_summary": "👤 Filtered user summary",
    },
    "de": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Finanzanalysen, Feedbacks und Benutzervalidierung über PostgreSQL",
        "info": "Dieses Dashboard liest Daten direkt aus PostgreSQL/Neon und validiert die reale Nutzung nach Kanal, Sprache, Währung, Diagnose, PDF, E-Mail und Telegram.",
        "update": "🔄 Daten aktualisieren",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administratives Dashboard",
        "interface_lang": "🌍 Sprache der Oberfläche",
        "menu": "Menü",
        "filters": "### 🔎 Filter",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "filter_user": "Nach Benutzer filtern",
        "filter_risk": "Nach Risiko filtern",
        "filter_feedback": "Nach Feedback filtern",
        "filter_data_language": "Nach Datensprache filtern",
        "filter_currency": "Nach Währung filtern",
        "filter_help": "Verwenden Sie die Filter, um Benutzer, Sprachen, Währungen und Kanäle zu analysieren, ohne internationale Ergebnisse zu vermischen.",
        "main_indicators": "📌 Hauptindikatoren",
        "diagnostics": "Diagnosen",
        "unique_users": "Eindeutige Benutzer",
        "avg_score": "Durchschnittlicher Score",
        "avg_balance": "Durchschnittlicher Saldo",
        "useful_feedback": "Nützliches Feedback",
        "filtered_user_summary": "👤 Zusammenfassung des gefilterten Benutzers",
    },
    "es": {
        "title": "📊 Panel — INNA Financial Coach AI",
        "subtitle": "Analítica financiera, feedback y validación con usuarios vía PostgreSQL",
        "info": "Este panel lee datos directamente de PostgreSQL/Neon y valida el uso real por canal, idioma, moneda, diagnóstico, PDF, e-mail y Telegram.",
        "update": "🔄 Actualizar datos",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Panel administrativo",
        "interface_lang": "🌍 Idioma de la interfaz",
        "menu": "Menú",
        "filters": "### 🔎 Filtros",
        "start_date": "Fecha inicial",
        "end_date": "Fecha final",
        "filter_user": "Filtrar por usuario",
        "filter_risk": "Filtrar por riesgo",
        "filter_feedback": "Filtrar por feedback",
        "filter_data_language": "Filtrar por idioma de los datos",
        "filter_currency": "Filtrar por moneda",
        "filter_help": "Usa los filtros para analizar usuario, idioma, moneda y canal sin mezclar resultados internacionales.",
        "main_indicators": "📌 Indicadores principales",
        "diagnostics": "Diagnósticos",
        "unique_users": "Usuarios únicos",
        "avg_score": "Score medio",
        "avg_balance": "Saldo medio",
        "useful_feedback": "Feedback útil",
        "filtered_user_summary": "👤 Resumen del usuario filtrado",
    },    "en_gb": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Financial analytics, feedback and user validation via PostgreSQL",
        "info": "This dashboard reads data directly from PostgreSQL/Neon and validates real usage by channel, language, currency, diagnosis, PDF, email and Telegram.",
        "update": "🔄 Refresh data",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administrative dashboard",
        "interface_lang": "🌍 Interface language",
        "menu": "Menu",
        "filters": "### 🔎 Filters",
        "start_date": "Start date",
        "end_date": "End date",
        "filter_user": "Filter by user",
        "filter_risk": "Filter by risk",
        "filter_feedback": "Filter by feedback",
        "filter_data_language": "Filter by data language",
        "filter_currency": "Filter by currency",
        "filter_help": "Use filters to analyse users, languages, currencies and channels without mixing international results.",
        "main_indicators": "📌 Main indicators",
        "diagnostics": dtx("diagnostics"),
        "unique_users": "Unique users",
        "avg_score": "Average score",
        "avg_balance": "Average balance",
        "useful_feedback": "Useful feedback",
        "filtered_user_summary": "👤 Filtered user summary",
    },
    "fr": {
        "title": "📊 Tableau de bord — INNA Financial Coach AI",
        "subtitle": "Analyses financières, feedbacks et validation des utilisateurs via PostgreSQL",
        "info": "Ce tableau de bord lit les données directement depuis PostgreSQL/Neon et valide l’utilisation réelle par canal, langue, devise, diagnostic, PDF, e-mail et Telegram.",
        "update": "🔄 Actualiser les données",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Tableau de bord administratif",
        "interface_lang": "🌍 Langue de l’interface",
        "menu": "Menu",
        "filters": "### 🔎 Filtres",
        "start_date": "Date initiale",
        "end_date": "Date finale",
        "filter_user": "Filtrer par utilisateur",
        "filter_risk": "Filtrer par risque",
        "filter_feedback": "Filtrer par feedback",
        "filter_data_language": "Filtrer par langue des données",
        "filter_currency": "Filtrer par devise",
        "filter_help": "Utilisez les filtres pour analyser les utilisateurs, langues, devises et canaux sans mélanger les résultats internationaux.",
        "main_indicators": "📌 Indicateurs principaux",
        "diagnostics": "Diagnostics",
        "unique_users": "Utilisateurs uniques",
        "avg_score": "Score moyen",
        "avg_balance": "Solde moyen",
        "useful_feedback": "Feedback utile",
        "filtered_user_summary": "👤 Résumé de l’utilisateur filtré",
    },
    "it": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Analisi finanziarie, feedback e validazione degli utenti tramite PostgreSQL",
        "info": "Questa dashboard legge i dati direttamente da PostgreSQL/Neon e valida l’uso reale per canale, lingua, valuta, diagnosi, PDF, e-mail e Telegram.",
        "update": "🔄 Aggiorna dati",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Dashboard amministrativa",
        "interface_lang": "🌍 Lingua dell’interfaccia",
        "menu": "Menu",
        "filters": "### 🔎 Filtri",
        "start_date": "Data iniziale",
        "end_date": "Data finale",
        "filter_user": "Filtra per utente",
        "filter_risk": "Filtra per rischio",
        "filter_feedback": "Filtra per feedback",
        "filter_data_language": "Filtra per lingua dei dati",
        "filter_currency": "Filtra per valuta",
        "filter_help": "Usa i filtri per analizzare utenti, lingue, valute e canali senza mescolare risultati internazionali.",
        "main_indicators": "📌 Indicatori principali",
        "diagnostics": "Diagnosi",
        "unique_users": "Utenti unici",
        "avg_score": "Punteggio medio",
        "avg_balance": "Saldo medio",
        "useful_feedback": "Feedback utile",
        "filtered_user_summary": "👤 Riepilogo dell’utente filtrato",
    },
    "ro": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Analize financiare, feedback și validare cu utilizatori prin PostgreSQL",
        "info": "Acest dashboard citește date direct din PostgreSQL/Neon și validează utilizarea reală pe canal, limbă, monedă, diagnostic, PDF, e-mail și Telegram.",
        "update": "🔄 Actualizează datele",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Dashboard administrativ",
        "interface_lang": "🌍 Limba interfeței",
        "menu": "Meniu",
        "filters": "### 🔎 Filtre",
        "start_date": "Data inițială",
        "end_date": "Data finală",
        "filter_user": "Filtrează după utilizator",
        "filter_risk": "Filtrează după risc",
        "filter_feedback": "Filtrează după feedback",
        "filter_data_language": "Filtrează după limba datelor",
        "filter_currency": "Filtrează după monedă",
        "filter_help": "Folosește filtrele pentru a analiza utilizatori, limbi, monede și canale fără a amesteca rezultatele internaționale.",
        "main_indicators": "📌 Indicatori principali",
        "diagnostics": "Diagnosticări",
        "unique_users": "Utilizatori unici",
        "avg_score": "Scor mediu",
        "avg_balance": "Sold mediu",
        "useful_feedback": "Feedback util",
        "filtered_user_summary": "👤 Rezumatul utilizatorului filtrat",
    },
    "ua": {
        "title": "📊 Панель — INNA Financial Coach AI",
        "subtitle": "Фінансова аналітика, відгуки та перевірка користувачів через PostgreSQL",
        "info": "Ця панель читає дані безпосередньо з PostgreSQL/Neon і перевіряє реальне використання за каналом, мовою, валютою, діагностикою, PDF, e-mail і Telegram.",
        "update": "🔄 Оновити дані",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Адміністративна панель",
        "interface_lang": "🌍 Мова інтерфейсу",
        "menu": "Меню",
        "filters": "### 🔎 Фільтри",
        "start_date": "Початкова дата",
        "end_date": "Кінцева дата",
        "filter_user": "Фільтр за користувачем",
        "filter_risk": "Фільтр за ризиком",
        "filter_feedback": "Фільтр за відгуком",
        "filter_data_language": "Фільтр за мовою даних",
        "filter_currency": "Фільтр за валютою",
        "filter_help": "Використовуйте фільтри для аналізу користувачів, мов, валют і каналів без змішування міжнародних результатів.",
        "main_indicators": "📌 Основні показники",
        "diagnostics": "Діагностики",
        "unique_users": "Унікальні користувачі",
        "avg_score": "Середній бал",
        "avg_balance": "Середній баланс",
        "useful_feedback": "Корисний відгук",
        "filtered_user_summary": "👤 Підсумок відфільтрованого користувача",
    },
    "ru": {
        "title": "📊 Панель — INNA Financial Coach AI",
        "subtitle": "Финансовая аналитика, отзывы и проверка пользователей через PostgreSQL",
        "info": "Эта панель читает данные напрямую из PostgreSQL/Neon и проверяет реальное использование по каналу, языку, валюте, диагностике, PDF, e-mail и Telegram.",
        "update": "🔄 Обновить данные",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Административная панель",
        "interface_lang": "🌍 Язык интерфейса",
        "menu": "Меню",
        "filters": "### 🔎 Фильтры",
        "start_date": "Начальная дата",
        "end_date": "Конечная дата",
        "filter_user": "Фильтр по пользователю",
        "filter_risk": "Фильтр по риску",
        "filter_feedback": "Фильтр по отзыву",
        "filter_data_language": "Фильтр по языку данных",
        "filter_currency": "Фильтр по валюте",
        "filter_help": "Используйте фильтры для анализа пользователей, языков, валют и каналов без смешивания международных результатов.",
        "main_indicators": "📌 Основные показатели",
        "diagnostics": "Диагностики",
        "unique_users": "Уникальные пользователи",
        "avg_score": "Средний балл",
        "avg_balance": "Средний баланс",
        "useful_feedback": "Полезный отзыв",
        "filtered_user_summary": "👤 Сводка отфильтрованного пользователя",
    },
    "sa": {
        "title": "📊 لوحة التحكم — INNA Financial Coach AI",
        "subtitle": "تحليلات مالية، ملاحظات المستخدمين والتحقق عبر بوستغري إس كيو إل",
        "info": "تقرأ لوحة التحكم هذه البيانات مباشرة من بوستغري إس كيو إل/Neon وتتحقق من الاستخدام الفعلي حسب القناة واللغة والعملة والتشخيص وPDF والبريد الإلكتروني وتيليجرام.",
        "update": "🔄 تحديث البيانات",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "لوحة تحكم إدارية",
        "interface_lang": "🌍 لغة الواجهة",
        "menu": "القائمة",
        "filters": "### 🔎 الفلاتر",
        "start_date": "تاريخ البداية",
        "end_date": "تاريخ النهاية",
        "filter_user": "تصفية حسب المستخدم",
        "filter_risk": "تصفية حسب المخاطر",
        "filter_feedback": "تصفية حسب الملاحظات",
        "filter_data_language": "تصفية حسب لغة البيانات",
        "filter_currency": "تصفية حسب العملة",
        "filter_help": "استخدم الفلاتر لتحليل المستخدمين واللغات والعملات والقنوات دون خلط النتائج الدولية.",
        "main_indicators": "📌 المؤشرات الرئيسية",
        "diagnostics": "التشخيصات",
        "unique_users": "المستخدمون الفريدون",
        "avg_score": "متوسط النتيجة",
        "avg_balance": "متوسط الرصيد",
        "useful_feedback": "ملاحظات مفيدة",
        "filtered_user_summary": "👤 ملخص المستخدم المحدد",
    },
    "ch": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Finanzanalysen, Feedbacks und Benutzervalidierung über PostgreSQL",
        "info": "Dieses Dashboard liest Daten direkt aus PostgreSQL/Neon und validiert die reale Nutzung nach Kanal, Sprache, Währung, Diagnose, PDF, E-Mail und Telegram.",
        "update": "🔄 Daten aktualisieren",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administratives Dashboard",
        "interface_lang": "🌍 Sprache der Oberfläche",
        "menu": "Menü",
        "filters": "### 🔎 Filter",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "filter_user": "Nach Benutzer filtern",
        "filter_risk": "Nach Risiko filtern",
        "filter_feedback": "Nach Feedback filtern",
        "filter_data_language": "Nach Datensprache filtern",
        "filter_currency": "Nach Währung filtern",
        "filter_help": "Verwenden Sie die Filter, um Benutzer, Sprachen, Währungen und Kanäle zu analysieren, ohne internationale Ergebnisse zu vermischen.",
        "main_indicators": "📌 Hauptindikatoren",
        "diagnostics": "Diagnosen",
        "unique_users": "Eindeutige Benutzer",
        "avg_score": "Durchschnittlicher Score",
        "avg_balance": "Durchschnittlicher Saldo",
        "useful_feedback": "Nützliches Feedback",
        "filtered_user_summary": "👤 Zusammenfassung des gefilterten Benutzers",
    },
}

DASHBOARD_MENU_LABELS = {
    "pt": {},
    "en_us": {
        "📌 Visão Geral": "📌 Overview",
        "🌐 Eventos Multicanal": "🌐 Multichannel Events",
        "🌍 Visão Internacional": "🌍 International View",
        "👤 Diagnósticos": "diagnoses_page",
        "💬 Feedbacks": "💬 Feedback",
        "📈 Evolução": "📈 Evolution",
        "🧠 Leitura Executiva": "🧠 Executive Reading",
        "🧪 Avaliação do Agente": "🧪 Agent Evaluation",
        "📊 Observabilidade RAG": "📊 RAG Observability",
        "📤 Exportar": "📤 Export",
    },
    "es": {
        "📌 Visão Geral": "📌 Visión General",
        "🌐 Eventos Multicanal": "🌐 Eventos Multicanal",
        "🌍 Visão Internacional": "🌍 Visión Internacional",
        "👤 Diagnósticos": "👤 Diagnósticos",
        "💬 Feedbacks": "💬 Feedbacks",
        "📈 Evolução": "📈 Evolución",
        "🧠 Leitura Executiva": "🧠 Lectura Ejecutiva",
        "🧪 Avaliação do Agente": "🧪 Evaluación del Agente",
        "📊 Observabilidade RAG": "📊 Observabilidad RAG",
        "📤 Exportar": "📤 Exportar",
    },    "en_gb": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Financial analytics, feedback and user validation via PostgreSQL",
        "info": "This dashboard reads data directly from PostgreSQL/Neon and validates real usage by channel, language, currency, diagnosis, PDF, email and Telegram.",
        "update": "🔄 Refresh data",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administrative dashboard",
        "interface_lang": "🌍 Interface language",
        "menu": "Menu",
        "filters": "### 🔎 Filters",
        "start_date": "Start date",
        "end_date": "End date",
        "filter_user": "Filter by user",
        "filter_risk": "Filter by risk",
        "filter_feedback": "Filter by feedback",
        "filter_data_language": "Filter by data language",
        "filter_currency": "Filter by currency",
        "filter_help": "Use filters to analyse users, languages, currencies and channels without mixing international results.",
        "main_indicators": "📌 Main indicators",
        "diagnostics": dtx("diagnostics"),
        "unique_users": "Unique users",
        "avg_score": "Average score",
        "avg_balance": "Average balance",
        "useful_feedback": "Useful feedback",
        "filtered_user_summary": "👤 Filtered user summary",
    },
    "fr": {
        "title": "📊 Tableau de bord — INNA Financial Coach AI",
        "subtitle": "Analyses financières, feedbacks et validation des utilisateurs via PostgreSQL",
        "info": "Ce tableau de bord lit les données directement depuis PostgreSQL/Neon et valide l’utilisation réelle par canal, langue, devise, diagnostic, PDF, e-mail et Telegram.",
        "update": "🔄 Actualiser les données",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Tableau de bord administratif",
        "interface_lang": "🌍 Langue de l’interface",
        "menu": "Menu",
        "filters": "### 🔎 Filtres",
        "start_date": "Date initiale",
        "end_date": "Date finale",
        "filter_user": "Filtrer par utilisateur",
        "filter_risk": "Filtrer par risque",
        "filter_feedback": "Filtrer par feedback",
        "filter_data_language": "Filtrer par langue des données",
        "filter_currency": "Filtrer par devise",
        "filter_help": "Utilisez les filtres pour analyser les utilisateurs, langues, devises et canaux sans mélanger les résultats internationaux.",
        "main_indicators": "📌 Indicateurs principaux",
        "diagnostics": "Diagnostics",
        "unique_users": "Utilisateurs uniques",
        "avg_score": "Score moyen",
        "avg_balance": "Solde moyen",
        "useful_feedback": "Feedback utile",
        "filtered_user_summary": "👤 Résumé de l’utilisateur filtré",
    },
    "it": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Analisi finanziarie, feedback e validazione degli utenti tramite PostgreSQL",
        "info": "Questa dashboard legge i dati direttamente da PostgreSQL/Neon e valida l’uso reale per canale, lingua, valuta, diagnosi, PDF, e-mail e Telegram.",
        "update": "🔄 Aggiorna dati",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Dashboard amministrativa",
        "interface_lang": "🌍 Lingua dell’interfaccia",
        "menu": "Menu",
        "filters": "### 🔎 Filtri",
        "start_date": "Data iniziale",
        "end_date": "Data finale",
        "filter_user": "Filtra per utente",
        "filter_risk": "Filtra per rischio",
        "filter_feedback": "Filtra per feedback",
        "filter_data_language": "Filtra per lingua dei dati",
        "filter_currency": "Filtra per valuta",
        "filter_help": "Usa i filtri per analizzare utenti, lingue, valute e canali senza mescolare risultati internazionali.",
        "main_indicators": "📌 Indicatori principali",
        "diagnostics": "Diagnosi",
        "unique_users": "Utenti unici",
        "avg_score": "Punteggio medio",
        "avg_balance": "Saldo medio",
        "useful_feedback": "Feedback utile",
        "filtered_user_summary": "👤 Riepilogo dell’utente filtrato",
    },
    "ro": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Analize financiare, feedback și validare cu utilizatori prin PostgreSQL",
        "info": "Acest dashboard citește date direct din PostgreSQL/Neon și validează utilizarea reală pe canal, limbă, monedă, diagnostic, PDF, e-mail și Telegram.",
        "update": "🔄 Actualizează datele",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Dashboard administrativ",
        "interface_lang": "🌍 Limba interfeței",
        "menu": "Meniu",
        "filters": "### 🔎 Filtre",
        "start_date": "Data inițială",
        "end_date": "Data finală",
        "filter_user": "Filtrează după utilizator",
        "filter_risk": "Filtrează după risc",
        "filter_feedback": "Filtrează după feedback",
        "filter_data_language": "Filtrează după limba datelor",
        "filter_currency": "Filtrează după monedă",
        "filter_help": "Folosește filtrele pentru a analiza utilizatori, limbi, monede și canale fără a amesteca rezultatele internaționale.",
        "main_indicators": "📌 Indicatori principali",
        "diagnostics": "Diagnosticări",
        "unique_users": "Utilizatori unici",
        "avg_score": "Scor mediu",
        "avg_balance": "Sold mediu",
        "useful_feedback": "Feedback util",
        "filtered_user_summary": "👤 Rezumatul utilizatorului filtrat",
    },
    "ua": {
        "title": "📊 Панель — INNA Financial Coach AI",
        "subtitle": "Фінансова аналітика, відгуки та перевірка користувачів через PostgreSQL",
        "info": "Ця панель читає дані безпосередньо з PostgreSQL/Neon і перевіряє реальне використання за каналом, мовою, валютою, діагностикою, PDF, e-mail і Telegram.",
        "update": "🔄 Оновити дані",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Адміністративна панель",
        "interface_lang": "🌍 Мова інтерфейсу",
        "menu": "Меню",
        "filters": "### 🔎 Фільтри",
        "start_date": "Початкова дата",
        "end_date": "Кінцева дата",
        "filter_user": "Фільтр за користувачем",
        "filter_risk": "Фільтр за ризиком",
        "filter_feedback": "Фільтр за відгуком",
        "filter_data_language": "Фільтр за мовою даних",
        "filter_currency": "Фільтр за валютою",
        "filter_help": "Використовуйте фільтри для аналізу користувачів, мов, валют і каналів без змішування міжнародних результатів.",
        "main_indicators": "📌 Основні показники",
        "diagnostics": "Діагностики",
        "unique_users": "Унікальні користувачі",
        "avg_score": "Середній бал",
        "avg_balance": "Середній баланс",
        "useful_feedback": "Корисний відгук",
        "filtered_user_summary": "👤 Підсумок відфільтрованого користувача",
    },
    "ru": {
        "title": "📊 Панель — INNA Financial Coach AI",
        "subtitle": "Финансовая аналитика, отзывы и проверка пользователей через PostgreSQL",
        "info": "Эта панель читает данные напрямую из PostgreSQL/Neon и проверяет реальное использование по каналу, языку, валюте, диагностике, PDF, e-mail и Telegram.",
        "update": "🔄 Обновить данные",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Административная панель",
        "interface_lang": "🌍 Язык интерфейса",
        "menu": "Меню",
        "filters": "### 🔎 Фильтры",
        "start_date": "Начальная дата",
        "end_date": "Конечная дата",
        "filter_user": "Фильтр по пользователю",
        "filter_risk": "Фильтр по риску",
        "filter_feedback": "Фильтр по отзыву",
        "filter_data_language": "Фильтр по языку данных",
        "filter_currency": "Фильтр по валюте",
        "filter_help": "Используйте фильтры для анализа пользователей, языков, валют и каналов без смешивания международных результатов.",
        "main_indicators": "📌 Основные показатели",
        "diagnostics": "Диагностики",
        "unique_users": "Уникальные пользователи",
        "avg_score": "Средний балл",
        "avg_balance": "Средний баланс",
        "useful_feedback": "Полезный отзыв",
        "filtered_user_summary": "👤 Сводка отфильтрованного пользователя",
    },
    "sa": {
        "title": "📊 لوحة التحكم — INNA Financial Coach AI",
        "subtitle": "تحليلات مالية، ملاحظات المستخدمين والتحقق عبر بوستغري إس كيو إل",
        "info": "تقرأ لوحة التحكم هذه البيانات مباشرة من بوستغري إس كيو إل/Neon وتتحقق من الاستخدام الفعلي حسب القناة واللغة والعملة والتشخيص وPDF والبريد الإلكتروني وتيليجرام.",
        "update": "🔄 تحديث البيانات",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "لوحة تحكم إدارية",
        "interface_lang": "🌍 لغة الواجهة",
        "menu": "القائمة",
        "filters": "### 🔎 الفلاتر",
        "start_date": "تاريخ البداية",
        "end_date": "تاريخ النهاية",
        "filter_user": "تصفية حسب المستخدم",
        "filter_risk": "تصفية حسب المخاطر",
        "filter_feedback": "تصفية حسب الملاحظات",
        "filter_data_language": "تصفية حسب لغة البيانات",
        "filter_currency": "تصفية حسب العملة",
        "filter_help": "استخدم الفلاتر لتحليل المستخدمين واللغات والعملات والقنوات دون خلط النتائج الدولية.",
        "main_indicators": "📌 المؤشرات الرئيسية",
        "diagnostics": "التشخيصات",
        "unique_users": "المستخدمون الفريدون",
        "avg_score": "متوسط النتيجة",
        "avg_balance": "متوسط الرصيد",
        "useful_feedback": "ملاحظات مفيدة",
        "filtered_user_summary": "👤 ملخص المستخدم المحدد",
    },
    "ch": {
        "title": "📊 Dashboard — INNA Financial Coach AI",
        "subtitle": "Finanzanalysen, Feedbacks und Benutzervalidierung über PostgreSQL",
        "info": "Dieses Dashboard liest Daten direkt aus PostgreSQL/Neon und validiert die reale Nutzung nach Kanal, Sprache, Währung, Diagnose, PDF, E-Mail und Telegram.",
        "update": "🔄 Daten aktualisieren",
        "sidebar_title": "🧭 INNA Analytics",
        "sidebar_caption": "Administratives Dashboard",
        "interface_lang": "🌍 Sprache der Oberfläche",
        "menu": "Menü",
        "filters": "### 🔎 Filter",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "filter_user": "Nach Benutzer filtern",
        "filter_risk": "Nach Risiko filtern",
        "filter_feedback": "Nach Feedback filtern",
        "filter_data_language": "Nach Datensprache filtern",
        "filter_currency": "Nach Währung filtern",
        "filter_help": "Verwenden Sie die Filter, um Benutzer, Sprachen, Währungen und Kanäle zu analysieren, ohne internationale Ergebnisse zu vermischen.",
        "main_indicators": "📌 Hauptindikatoren",
        "diagnostics": "Diagnosen",
        "unique_users": "Eindeutige Benutzer",
        "avg_score": "Durchschnittlicher Score",
        "avg_balance": "Durchschnittlicher Saldo",
        "useful_feedback": "Nützliches Feedback",
        "filtered_user_summary": "👤 Zusammenfassung des gefilterten Benutzers",
    },
}


# =============================
# PATCH FINAL - Tradução Dashboard INNA
# Menu + labels da visão geral
# =============================

DASHBOARD_MENU_LABELS.update({
    "ru": {
        "📌 Visão Geral": "📌 Обзор",
        "🌐 Eventos Multicanal": "🌐 Многоканальные события",
        "🌍 Visão Internacional": "🌍 Международный обзор",
        "👤 Diagnósticos": "👤 Диагностики",
        "💬 Feedbacks": "💬 Отзывы",
        "📈 Evolução": "📈 Динамика",
        "🧠 Leitura Executiva": "🧠 Краткий отчёт",
        "🧪 Avaliação do Agente": "🧪 Оценка агента",
        "📊 Observabilidade RAG": "📊 Наблюдаемость RAG",
        "📤 Exportar": "📤 Экспорт",
    },
    "ua": {
        "📌 Visão Geral": "📌 Огляд",
        "🌐 Eventos Multicanal": "🌐 Багатоканальні події",
        "🌍 Visão Internacional": "🌍 Міжнародний огляд",
        "👤 Diagnósticos": "👤 Діагностики",
        "💬 Feedbacks": "💬 Відгуки",
        "📈 Evolução": "📈 Динаміка",
        "🧠 Leitura Executiva": "🧠 Виконавче резюме",
        "🧪 Avaliação do Agente": "🧪 Оцінка агента",
        "📊 Observabilidade RAG": "📊 Спостережуваність RAG",
        "📤 Exportar": "📤 Експорт",
    },
    "it": {
        "📌 Visão Geral": "📌 Panoramica",
        "🌐 Eventos Multicanal": "🌐 Eventi multicanale",
        "🌍 Visão Internacional": "🌍 Vista internazionale",
        "👤 Diagnósticos": "👤 Diagnosi",
        "💬 Feedbacks": "💬 Feedback",
        "📈 Evolução": "📈 Evoluzione",
        "🧠 Leitura Executiva": "🧠 Lettura esecutiva",
        "🧪 Avaliação do Agente": "🧪 Valutazione agente",
        "📊 Observabilidade RAG": "📊 Osservabilità RAG",
        "📤 Exportar": "📤 Esporta",
    },
    "fr": {
        "📌 Visão Geral": "📌 Vue générale",
        "🌐 Eventos Multicanal": "🌐 Événements multicanaux",
        "🌍 Visão Internacional": "🌍 Vue internationale",
        "👤 Diagnósticos": "👤 Diagnostics",
        "💬 Feedbacks": "💬 Feedbacks",
        "📈 Evolução": "📈 Évolution",
        "🧠 Leitura Executiva": "🧠 Lecture exécutive",
        "🧪 Avaliação do Agente": "🧪 Évaluation de l’agent",
        "📊 Observabilidade RAG": "📊 Observabilité RAG",
        "📤 Exportar": "📤 Exporter",
    },
    "de": {
        "📌 Visão Geral": "📌 Übersicht",
        "🌐 Eventos Multicanal": "🌐 Multichannel-Ereignisse",
        "🌍 Visão Internacional": "🌍 Internationale Ansicht",
        "👤 Diagnósticos": "👤 Diagnosen",
        "💬 Feedbacks": "💬 Feedbacks",
        "📈 Evolução": "📈 Entwicklung",
        "🧠 Leitura Executiva": "🧠 Executive Summary",
        "🧪 Avaliação do Agente": "🧪 Agentenbewertung",
        "📊 Observabilidade RAG": "📊 RAG-Beobachtbarkeit",
        "📤 Exportar": "📤 Exportieren",
    },
    "en_gb": DASHBOARD_MENU_LABELS.get("en_us", {}),
    "ro": {
        "📌 Visão Geral": "📌 Prezentare generală",
        "🌐 Eventos Multicanal": "🌐 Evenimente multicanal",
        "🌍 Visão Internacional": "🌍 Vedere internațională",
        "👤 Diagnósticos": "👤 Diagnosticări",
        "💬 Feedbacks": "💬 Feedback",
        "📈 Evolução": "📈 Evoluție",
        "🧠 Leitura Executiva": "🧠 Citire executivă",
        "🧪 Avaliação do Agente": "🧪 Evaluarea agentului",
        "📊 Observabilidade RAG": "📊 Observabilitate RAG",
        "📤 Exportar": "📤 Export",
    },
    "sa": {
        "📌 Visão Geral": "📌 نظرة عامة",
        "🌐 Eventos Multicanal": "🌐 أحداث متعددة القنوات",
        "🌍 Visão Internacional": "🌍 العرض الدولي",
        "👤 Diagnósticos": "👤 التشخيصات",
        "💬 Feedbacks": "💬 الملاحظات",
        "📈 Evolução": "📈 التطور",
        "🧠 Leitura Executiva": "🧠 القراءة التنفيذية",
        "🧪 Avaliação do Agente": "🧪 تقييم الوكيل",
        "📊 Observabilidade RAG": "📊 مراقبة RAG",
        "📤 Exportar": "📤 تصدير",
    },
    "ch": {
        "📌 Visão Geral": "📌 Übersicht",
        "🌐 Eventos Multicanal": "🌐 Multichannel-Ereignisse",
        "🌍 Visão Internacional": "🌍 Internationale Ansicht",
        "👤 Diagnósticos": "👤 Diagnosen",
        "💬 Feedbacks": "💬 Feedbacks",
        "📈 Evolução": "📈 Entwicklung",
        "🧠 Leitura Executiva": "🧠 Executive Summary",
        "🧪 Avaliação do Agente": "🧪 Agentenbewertung",
        "📊 Observabilidade RAG": "📊 RAG-Beobachtbarkeit",
        "📤 Exportar": "📤 Exportieren",
    },
})

DASHBOARD_TEXTS.setdefault("ru", {}).update({
    "user": "Пользователь",
    "language": "Язык",
    "currency": "Валюта",
    "latest_channel": "Последний канал",
    "financial_score": "Финансовый балл",
    "risk": "Риск",
    "estimated_balance": "Оценочный баланс",
    "summary_help": "Краткое резюме отфильтрованного пользователя с разделением по языку, валюте, каналу, баллу, риску и балансу.",
    "see_by_currency": "Несколько валют",
    "all": "Все",
})
DASHBOARD_TEXTS.setdefault("it", {}).update({
    "user": "Utente",
    "language": "Lingua",
    "currency": "Valuta",
    "latest_channel": "Canale più recente",
    "financial_score": "Punteggio finanziario",
    "risk": "Rischio",
    "estimated_balance": "Saldo stimato",
    "summary_help": "Riepilogo esecutivo dell’utente filtrato, separando lingua, valuta, canale, punteggio, rischio e saldo.",
    "see_by_currency": "Più valute",
    "all": "Tutti",
})
DASHBOARD_TEXTS.setdefault("en_us", {}).update({
    "user": "User",
    "language": "Language",
    "currency": "Currency",
    "latest_channel": "Latest channel",
    "financial_score": "Financial score",
    "risk": "Risk",
    "estimated_balance": "Estimated balance",
    "summary_help": "Executive summary of the filtered user, separating language, currency, channel, score, risk and balance.",
    "see_by_currency": "Multiple currencies",
    "all": "All",
})
DASHBOARD_TEXTS.setdefault("pt", {}).update({
    "user": "Usuário",
    "language": "Idioma",
    "currency": "Moeda",
    "latest_channel": "Canal mais recente",
    "financial_score": "Score financeiro",
    "risk": "Risco",
    "estimated_balance": "Saldo estimado",
    "summary_help": "Resumo executivo do usuário filtrado, separando idioma, moeda, canal, score, risco e saldo estimado.",
    "see_by_currency": "Múltiplas moedas",
    "all": "Todos",
})


DASHBOARD_TEXTS.setdefault("sa", {}).update({
    "user": "المستخدم",
    "language": "اللغة",
    "currency": "العملة",
    "latest_channel": "آخر قناة",
    "financial_score": "النتيجة المالية",
    "risk": "المخاطر",
    "estimated_balance": "الرصيد التقديري",
    "summary_help": "ملخص تنفيذي للمستخدم المحدد مع فصل اللغة والعملة والقناة والنتيجة والمخاطر والرصيد.",
    "see_by_currency": "عملات متعددة",
})


# =============================
# PATCH TECNOLOGIAS TRADUZIDAS NA INTERFACE
# PostgreSQL, PDF, e-mail e Telegram por idioma
# Não altera dados reais do diagnóstico
# =============================

DASHBOARD_TEXTS.setdefault("pt", {}).update({
    "subtitle": "Analytics financeiro, feedbacks e validação com usuários via PostgreSQL",
    "info": "Este dashboard lê dados diretamente do PostgreSQL/Neon e valida uso real por canal, idioma, moeda, diagnóstico, documento PDF, e-mail e Telegram.",
    "see_by_currency": "Múltiplas moedas",
})

DASHBOARD_TEXTS.setdefault("en_us", {}).update({
    "subtitle": "Financial analytics, feedback and user validation through Postgres SQL",
    "info": "This dashboard reads data directly from Postgres SQL/Neon and validates real usage by channel, language, currency, diagnosis, PDF document, email and Telegram app.",
    "see_by_currency": "Multiple currencies",
})

DASHBOARD_TEXTS.setdefault("en_gb", {}).update({
    "subtitle": "Financial analytics, feedback and user validation through Postgres SQL",
    "info": "This dashboard reads data directly from Postgres SQL/Neon and validates real usage by channel, language, currency, diagnosis, PDF document, email and Telegram app.",
    "see_by_currency": "Multiple currencies",
})

DASHBOARD_TEXTS.setdefault("es", {}).update({
    "subtitle": "Analítica financiera, feedback y validación con usuarios mediante Postgres SQL",
    "info": "Este panel lee datos directamente desde Postgres SQL/Neon y valida el uso real por canal, idioma, moneda, diagnóstico, documento PDF, correo electrónico y aplicación Telegram.",
    "see_by_currency": "Múltiples monedas",
})

DASHBOARD_TEXTS.setdefault("fr", {}).update({
    "subtitle": "Analyses financières, feedbacks et validation des utilisateurs via Postgres SQL",
    "info": "Ce tableau de bord lit les données directement depuis Postgres SQL/Neon et valide l’utilisation réelle par canal, langue, devise, diagnostic, document PDF, e-mail et application Telegram.",
    "see_by_currency": "Plusieurs devises",
})

DASHBOARD_TEXTS.setdefault("de", {}).update({
    "subtitle": "Finanzanalysen, Feedbacks und Benutzervalidierung über Postgres SQL",
    "info": "Dieses Dashboard liest Daten direkt aus Postgres SQL/Neon und validiert die reale Nutzung nach Kanal, Sprache, Währung, Diagnose, PDF-Dokument, E-Mail und Telegram-App.",
    "see_by_currency": "Mehrere Währungen",
})

DASHBOARD_TEXTS.setdefault("it", {}).update({
    "subtitle": "Analisi finanziarie, feedback e validazione degli utenti tramite Postgres SQL",
    "info": "Questa dashboard legge i dati direttamente da Postgres SQL/Neon e valida l’uso reale per canale, lingua, valuta, diagnosi, documento PDF, e-mail e app Telegram.",
    "see_by_currency": "Più valute",
})

DASHBOARD_TEXTS.setdefault("ro", {}).update({
    "subtitle": "Analize financiare, feedback și validare cu utilizatori prin Postgres SQL",
    "info": "Acest dashboard citește date direct din Postgres SQL/Neon și validează utilizarea reală pe canal, limbă, monedă, diagnostic, document PDF, e-mail și aplicația Telegram.",
    "see_by_currency": "Mai multe monede",
})

DASHBOARD_TEXTS.setdefault("ua", {}).update({
    "subtitle": "Фінансова аналітика, відгуки та перевірка користувачів через Postgres SQL",
    "info": "Ця панель читає дані безпосередньо з Postgres SQL/Neon і перевіряє реальне використання за каналом, мовою, валютою, діагностикою, PDF-документом, електронною поштою та додатком Telegram.",
    "see_by_currency": "Кілька валют",
})

DASHBOARD_TEXTS.setdefault("ru", {}).update({
    "subtitle": "Финансовая аналитика, отзывы и проверка пользователей через Postgres SQL",
    "info": "Эта панель читает данные напрямую из Postgres SQL/Neon и проверяет реальное использование по каналу, языку, валюте, диагностике, PDF-документу, электронной почте и приложению Telegram.",
    "see_by_currency": "Несколько валют",
})

DASHBOARD_TEXTS.setdefault("sa", {}).update({
    "subtitle": "تحليلات مالية، ملاحظات المستخدمين والتحقق عبر بوستغري إس كيو إل",
    "info": "تقرأ لوحة التحكم هذه البيانات مباشرة من بوستغري إس كيو إل/Neon وتتحقق من الاستخدام الفعلي حسب القناة واللغة والعملة والتشخيص ووثيقة PDF والبريد الإلكتروني وتطبيق تيليجرام.",
    "see_by_currency": "عملات متعددة",
})

DASHBOARD_TEXTS.setdefault("ch", {}).update({
    "subtitle": "Finanzanalysen, Feedbacks und Benutzervalidierung über Postgres SQL",
    "info": "Dieses Dashboard liest Daten direkt aus Postgres SQL/Neon und validiert die reale Nutzung nach Kanal, Sprache, Währung, Diagnose, PDF-Dokument, E-Mail und Telegram-App.",
    "see_by_currency": "Mehrere Währungen",
})


# =============================
# PATCH LABELS DO RESUMO POR IDIOMA
# Traduz apenas rótulos da interface
# Não altera resultados reais do diagnóstico
# =============================

DASHBOARD_TEXTS.setdefault("pt", {}).update({
    "user": "Usuário",
    "language": "Idioma",
    "currency": "Moeda",
    "latest_channel": "Canal mais recente",
    "financial_score": "Score financeiro",
    "risk": "Risco",
    "estimated_balance": "Saldo estimado",
    "summary_help": "Resumo executivo do usuário filtrado, separando idioma, moeda, canal, score, risco e saldo estimado.",
})

DASHBOARD_TEXTS.setdefault("en_us", {}).update({
    "user": "User",
    "language": "Language",
    "currency": "Currency",
    "latest_channel": "Latest channel",
    "financial_score": "Financial score",
    "risk": "Risk",
    "estimated_balance": "Estimated balance",
    "summary_help": "Executive summary of the filtered user, separating language, currency, channel, score, risk and balance.",
})

DASHBOARD_TEXTS.setdefault("en_gb", {}).update({
    "user": "User",
    "language": "Language",
    "currency": "Currency",
    "latest_channel": "Latest channel",
    "financial_score": "Financial score",
    "risk": "Risk",
    "estimated_balance": "Estimated balance",
    "summary_help": "Executive summary of the filtered user, separating language, currency, channel, score, risk and balance.",
})

DASHBOARD_TEXTS.setdefault("es", {}).update({
    "user": "Usuario",
    "language": "Idioma",
    "currency": "Moneda",
    "latest_channel": "Canal más reciente",
    "financial_score": "Score financiero",
    "risk": "Riesgo",
    "estimated_balance": "Saldo estimado",
    "summary_help": "Resumen ejecutivo del usuario filtrado, separando idioma, moneda, canal, score, riesgo y saldo.",
})

DASHBOARD_TEXTS.setdefault("fr", {}).update({
    "user": "Utilisateur",
    "language": "Langue",
    "currency": "Devise",
    "latest_channel": "Canal le plus récent",
    "financial_score": "Score financier",
    "risk": "Risque",
    "estimated_balance": "Solde estimé",
    "summary_help": "Résumé exécutif de l’utilisateur filtré, séparant langue, devise, canal, score, risque et solde.",
})

DASHBOARD_TEXTS.setdefault("de", {}).update({
    "user": "Benutzer",
    "language": "Sprache",
    "currency": "Währung",
    "latest_channel": "Letzter Kanal",
    "financial_score": "Finanzieller Score",
    "risk": "Risiko",
    "estimated_balance": "Geschätzter Saldo",
    "summary_help": "Zusammenfassung des gefilterten Benutzers mit Sprache, Währung, Kanal, Score, Risiko und Saldo.",
})

DASHBOARD_TEXTS.setdefault("it", {}).update({
    "user": "Utente",
    "language": "Lingua",
    "currency": "Valuta",
    "latest_channel": "Canale più recente",
    "financial_score": "Punteggio finanziario",
    "risk": "Rischio",
    "estimated_balance": "Saldo stimato",
    "summary_help": "Riepilogo esecutivo dell’utente filtrato, separando lingua, valuta, canale, punteggio, rischio e saldo.",
})

DASHBOARD_TEXTS.setdefault("ro", {}).update({
    "user": "Utilizator",
    "language": "Limbă",
    "currency": "Monedă",
    "latest_channel": "Cel mai recent canal",
    "financial_score": "Scor financiar",
    "risk": "Risc",
    "estimated_balance": "Sold estimat",
    "summary_help": "Rezumat executiv al utilizatorului filtrat, separând limba, moneda, canalul, scorul, riscul și soldul.",
})

DASHBOARD_TEXTS.setdefault("ua", {}).update({
    "user": "Користувач",
    "language": "Мова",
    "currency": "Валюта",
    "latest_channel": "Останній канал",
    "financial_score": "Фінансовий бал",
    "risk": "Ризик",
    "estimated_balance": "Орієнтовний баланс",
    "summary_help": "Підсумок відфільтрованого користувача з мовою, валютою, каналом, балом, ризиком і балансом.",
})

DASHBOARD_TEXTS.setdefault("ru", {}).update({
    "user": "Пользователь",
    "language": "Язык",
    "currency": "Валюта",
    "latest_channel": "Последний канал",
    "financial_score": "Финансовый балл",
    "risk": "Риск",
    "estimated_balance": "Оценочный баланс",
    "summary_help": "Сводка отфильтрованного пользователя с языком, валютой, каналом, баллом, риском и балансом.",
})

DASHBOARD_TEXTS.setdefault("sa", {}).update({
    "user": "المستخدم",
    "language": "اللغة",
    "currency": "العملة",
    "latest_channel": "آخر قناة",
    "financial_score": "النتيجة المالية",
    "risk": "المخاطر",
    "estimated_balance": "الرصيد التقديري",
    "summary_help": "ملخص تنفيذي للمستخدم المحدد مع فصل اللغة والعملة والقناة والنتيجة والمخاطر والرصيد.",
})

DASHBOARD_TEXTS.setdefault("ch", {}).update({
    "user": "Benutzer",
    "language": "Sprache",
    "currency": "Währung",
    "latest_channel": "Letzter Kanal",
    "financial_score": "Finanzieller Score",
    "risk": "Risiko",
    "estimated_balance": "Geschätzter Saldo",
    "summary_help": "Zusammenfassung des gefilterten Benutzers mit Sprache, Währung, Kanal, Score, Risiko und Saldo.",
})

def dashboard_lang():
    return st.session_state.get("dashboard_interface_lang", "pt")

def dt(key):
    lang = dashboard_lang()
    textos = DASHBOARD_TEXTS.get(lang, DASHBOARD_TEXTS["pt"])
    return textos.get(key, DASHBOARD_TEXTS["pt"].get(key, key))



# =============================
# PATCH MENU LATERAL MULTILÍNGUE
# Traduz somente labels do menu. Não altera o valor real usado no código.
# =============================

DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "📌 Visão Geral": "📌 Visão Geral",
    "🌐 Eventos Multicanal": "🌐 Eventos Multicanal",
    "🌍 Visão Internacional": "🌍 Visão Internacional",
    "👤 Diagnósticos": "👤 Diagnósticos",
    "💬 Feedbacks": "💬 Feedbacks",
    "📈 Evolução": "📈 Evolução",
    "🧠 Leitura Executiva": "🧠 Leitura Executiva",
    "🧪 Avaliação do Agente": "🧪 Avaliação do Agente",
    "📊 Observabilidade RAG": "📊 Observabilidade RAG",
    "📤 Exportar": "📤 Exportar",
})

DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "📌 Visão Geral": "📌 Overview",
    "🌐 Eventos Multicanal": "🌐 Multichannel Events",
    "🌍 Visão Internacional": "🌎 International View",
    "👤 Diagnósticos": "👤 Diagnostics",
    "💬 Feedbacks": "💬 Feedback",
    "📈 Evolução": "📈 Evolution",
    "🧠 Leitura Executiva": "🧠 Executive Reading",
    "🧪 Avaliação do Agente": "🧪 Agent Evaluation",
    "📊 Observabilidade RAG": "📊 RAG Observability",
    "📤 Exportar": "📤 Export",
    "🛠️ Observabilidade Tools": "🛠️ Tools Observability",
    "🧭 Timeline Viewer": "🧭 Timeline Viewer",
    "🧠 Memória Usuário": "🧠 User Memory",
})

DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update(DASHBOARD_MENU_LABELS.get("en_us", {}))

DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "📌 Visão Geral": "📌 Visión General",
    "🌐 Eventos Multicanal": "🌐 Eventos Multicanal",
    "🌍 Visão Internacional": "🌎 Vista Internacional",
    "👤 Diagnósticos": "👤 Diagnósticos",
    "💬 Feedbacks": "💬 Feedbacks",
    "📈 Evolução": "📈 Evolución",
    "🧠 Leitura Executiva": "🧠 Lectura Ejecutiva",
    "🧪 Avaliação do Agente": "🧪 Evaluación del Agente",
    "📊 Observabilidade RAG": "📊 Observabilidad RAG",
    "📤 Exportar": "📤 Exportar",
    "🛠️ Observabilidade Tools": "🛠️ Observabilidad de herramientas",
    "🧭 Timeline Viewer": "🧭 Visor de línea de tiempo",
    "🧠 Memória Usuário": "🧠 Memoria del usuario",
})

DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "📌 Visão Geral": "📌 Vue d’ensemble",
    "🌐 Eventos Multicanal": "🌐 Événements multicanaux",
    "🌍 Visão Internacional": "🌎 Vue internationale",
    "👤 Diagnósticos": "👤 Diagnostics",
    "💬 Feedbacks": "💬 Retours",
    "📈 Evolução": "📈 Évolution",
    "🧠 Leitura Executiva": "🧠 Lecture exécutive",
    "🧪 Avaliação do Agente": "🧪 Évaluation de l’agent",
    "📊 Observabilidade RAG": "📊 Observabilité RAG",
    "📤 Exportar": "📤 Exporter",
    "🛠️ Observabilidade Tools": "🛠️ Observabilité des outils",
    "🧭 Timeline Viewer": "🧭 Visionneuse de chronologie",
    "🧠 Memória Usuário": "🧠 Mémoire utilisateur",
})

DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "📌 Visão Geral": "📌 Übersicht",
    "🌐 Eventos Multicanal": "🌐 Mehrkanal-Ereignisse",
    "🌍 Visão Internacional": "🌎 Internationale Ansicht",
    "👤 Diagnósticos": "👤 Diagnosen",
    "💬 Feedbacks": "💬 Feedback",
    "📈 Evolução": "📈 Entwicklung",
    "🧠 Leitura Executiva": "🧠 Executive Summary",
    "🧪 Avaliação do Agente": "🧪 Agentenbewertung",
    "📊 Observabilidade RAG": "📊 RAG-Beobachtbarkeit",
    "📤 Exportar": "📤 Exportieren",
    "🛠️ Observabilidade Tools": "🛠️ Werkzeugbeobachtung",
    "🧭 Timeline Viewer": "🧭 Zeitachsenansicht",
    "🧠 Memória Usuário": "🧠 Benutzerspeicher",
})

DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "📌 Visão Geral": "📌 Panoramica",
    "🌐 Eventos Multicanal": "🌐 Eventi multicanale",
    "🌍 Visão Internacional": "🌎 Vista internazionale",
    "👤 Diagnósticos": "👤 Diagnostiche",
    "💬 Feedbacks": "💬 Feedback",
    "📈 Evolução": "📈 Evoluzione",
    "🧠 Leitura Executiva": "🧠 Lettura esecutiva",
    "🧪 Avaliação do Agente": "🧪 Valutazione agente",
    "📊 Observabilidade RAG": "📊 Osservabilità RAG",
    "📤 Exportar": "📤 Esporta",
    "🛠️ Observabilidade Tools": "🛠️ Osservabilità degli strumenti",
    "🧭 Timeline Viewer": "🧭 Visualizzatore della timeline",
    "🧠 Memória Usuário": "🧠 Memoria utente",
})

DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "📌 Visão Geral": "📌 Prezentare generală",
    "🌐 Eventos Multicanal": "🌐 Evenimente multicanal",
    "🌍 Visão Internacional": "🌎 Vizualizare internațională",
    "👤 Diagnósticos": "👤 Diagnostice",
    "💬 Feedbacks": "💬 Feedback",
    "📈 Evolução": "📈 Evoluție",
    "🧠 Leitura Executiva": "🧠 Citire executivă",
    "🧪 Avaliação do Agente": "🧪 Evaluarea agentului",
    "📊 Observabilidade RAG": "📊 Observabilitate RAG",
    "📤 Exportar": "📤 Exportă",
    "🛠️ Observabilidade Tools": "🛠️ Observabilitatea instrumentelor",
    "🧭 Timeline Viewer": "🧭 Vizualizator cronologie",
    "🧠 Memória Usuário": "🧠 Memoria utilizatorului",
})

DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "📌 Visão Geral": "📌 Огляд",
    "🌐 Eventos Multicanal": "🌐 Багатоканальні події",
    "🌍 Visão Internacional": "🌎 Міжнародний огляд",
    "👤 Diagnósticos": "👤 Діагностики",
    "💬 Feedbacks": "💬 Відгуки",
    "📈 Evolução": "📈 Динаміка",
    "🧠 Leitura Executiva": "🧠 Виконавче резюме",
    "🧪 Avaliação do Agente": "🧪 Оцінка агента",
    "📊 Observabilidade RAG": "📊 Спостережуваність RAG",
    "📤 Exportar": "📤 Експорт",
    "🛠️ Observabilidade Tools": "🛠️ Спостережуваність інструментів",
    "🧭 Timeline Viewer": "🧭 Перегляд часової шкали",
    "🧠 Memória Usuário": "🧠 Пам’ять користувача",
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "📌 Visão Geral": "📌 Обзор",
    "🌐 Eventos Multicanal": "🌐 Многоканальные события",
    "🌍 Visão Internacional": "🌎 Международный обзор",
    "👤 Diagnósticos": "👤 Диагностики",
    "💬 Feedbacks": "💬 Отзывы",
    "📈 Evolução": "📈 Динамика",
    "🧠 Leitura Executiva": "🧠 Исполнительное резюме",
    "🧪 Avaliação do Agente": "🧪 Оценка агента",
    "📊 Observabilidade RAG": "📊 Наблюдаемость RAG",
    "📤 Exportar": "📤 Экспорт",
    "🛠️ Observabilidade Tools": "🛠️ Наблюдаемость инструментов",
    "🧭 Timeline Viewer": "🧭 Просмотр временной шкалы",
    "🧠 Memória Usuário": "🧠 Память пользователя",
})

DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "📌 Visão Geral": "📌 نظرة عامة",
    "🌐 Eventos Multicanal": "🌐 أحداث متعددة القنوات",
    "🌍 Visão Internacional": "🌎 العرض الدولي",
    "👤 Diagnósticos": "👤 التشخيصات",
    "💬 Feedbacks": "💬 الملاحظات",
    "📈 Evolução": "📈 التطور",
    "🧠 Leitura Executiva": "🧠 القراءة التنفيذية",
    "🧪 Avaliação do Agente": "🧪 تقييم الوكيل",
    "📊 Observabilidade RAG": "📊 مراقبة RAG",
    "📤 Exportar": "📤 تصدير",
    "🛠️ Observabilidade Tools": "🛠️ مراقبة الأدوات",
    "🧭 Timeline Viewer": "🧭 عارض المسار الزمني",
    "🧠 Memória Usuário": "🧠 ذاكرة المستخدم",
})

DASHBOARD_MENU_LABELS.setdefault("ch", {}).update(DASHBOARD_MENU_LABELS.get("de", {}))


DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "💰 LLM Cost Center": "💰 Central de Custos de IA",
})

DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "💰 LLM Cost Center": "💰 AI Cost Center",
})

DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update({
    "💰 LLM Cost Center": "💰 AI Cost Centre",
    "🛠️ Observabilidade Tools": "🛠️ Tools Observability",
    "🧭 Timeline Viewer": "🧭 Timeline Viewer",
    "🧠 Memória Usuário": "🧠 User Memory",
})

DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "💰 LLM Cost Center": "💰 Centro de Costos de IA",
})

DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "💰 LLM Cost Center": "💰 Centre des coûts IA",
})

DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "💰 LLM Cost Center": "💰 KI-Kostenzentrale",
})

DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "💰 LLM Cost Center": "💰 Centro costi IA",
})

DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "💰 LLM Cost Center": "💰 Centrul costurilor IA",
})

DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "💰 LLM Cost Center": "💰 Центр витрат ШІ",
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "💰 LLM Cost Center": "💰 Центр затрат ИИ",
})

DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "💰 LLM Cost Center": (
        "💰 مركز تكاليف الذكاء الاصطناعي"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ch", {}).update({
    "💰 LLM Cost Center": "💰 KI-Kostenzentrale",
    "🛠️ Observabilidade Tools": "🛠️ Werkzeugbeobachtung",
    "🧭 Timeline Viewer": "🧭 Zeitachsenansicht",
    "🧠 Memória Usuário": "🧠 Benutzerspeicher",
})


DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "❤️ Health Center": "❤️ Central de Saúde",
})

DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "❤️ Health Center": "❤️ Health Center",
})

DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update({
    "❤️ Health Center": "❤️ Health Centre",
})

DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "❤️ Health Center": "❤️ Centro de Salud",
})

DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "❤️ Health Center": "❤️ Centre de santé",
})

DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "❤️ Health Center": "❤️ Systemzustand",
})

DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "❤️ Health Center": "❤️ Centro salute",
})

DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "❤️ Health Center": "❤️ Centrul de sănătate",
})

DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "❤️ Health Center": "❤️ Центр стану системи",
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "❤️ Health Center": "❤️ Центр состояния системы",
})

DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "❤️ Health Center": "❤️ مركز صحة النظام",
})

DASHBOARD_MENU_LABELS.setdefault("ch", {}).update({
    "❤️ Health Center": "❤️ Systemzustand",
})


DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Operações de IA (LLMOps) e Observabilidade"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ AI Operations (LLMOps) and Observability"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ AI Operations (LLMOps) and Observability"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Operaciones de IA (LLMOps) y Observabilidad"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Opérations IA (LLMOps) et Observabilité"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ KI-Betrieb (LLMOps) und Beobachtbarkeit"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Operazioni IA (LLMOps) e Osservabilità"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Operațiuni IA (LLMOps) și Observabilitate"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Операції ШІ (LLMOps) та спостережуваність"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ Операции ИИ (LLMOps) и наблюдаемость"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ عمليات الذكاء الاصطناعي (LLMOps) والمراقبة"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ch", {}).update({
    "🛰️ LLMOps & Observabilidade": (
        "🛰️ KI-Betrieb (LLMOps) und Beobachtbarkeit"
    ),
})


DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "📊 Analytics Tools": (
        "📊 Análise de Ferramentas (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "📊 Analytics Tools": (
        "📊 Tools Analytics"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update({
    "📊 Analytics Tools": (
        "📊 Tools Analytics"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "📊 Analytics Tools": (
        "📊 Análisis de Herramientas (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "📊 Analytics Tools": (
        "📊 Analyse des Outils (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "📊 Analytics Tools": (
        "📊 Werkzeuganalyse (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "📊 Analytics Tools": (
        "📊 Analisi degli Strumenti (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "📊 Analytics Tools": (
        "📊 Analiza Instrumentelor (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "📊 Analytics Tools": (
        "📊 Аналіз інструментів (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "📊 Analytics Tools": (
        "📊 Анализ инструментов (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "📊 Analytics Tools": (
        "📊 تحليل الأدوات (Tools)"
    ),
})

DASHBOARD_MENU_LABELS.setdefault("ch", {}).update({
    "📊 Analytics Tools": (
        "📊 Werkzeuganalyse (Tools)"
    ),
})


def dt_menu(menu_item):
    lang = dashboard_lang()
    return DASHBOARD_MENU_LABELS.get(lang, {}).get(menu_item, menu_item)

DASHBOARD_EXTRA_TEXTS = {
    "pt": {
        "no_diagnostics": "Nenhum diagnóstico encontrado para os filtros selecionados.",
        "events_title": "## 🌐 Eventos multicanal reais",
        "no_events": "Nenhum evento encontrado para os filtros selecionados.",
        "only_one_channel": "Somente um canal encontrado no filtro atual.",
        "last_events": "Ver últimos eventos reais",
        "funnel_title": "## 🧭 Funil de uso",
        "few_funnel_records": "Poucos registros no filtro atual. O funil foi exibido em tabela para evitar gráfico exagerado.",
        "international_title": "## 🌍 Visão internacional",
        "no_international": "Nenhum dado internacional encontrado para os filtros selecionados.",
        "diagnostics_by_language": "### Diagnósticos por idioma",
        "only_one_language": "Somente um idioma encontrado nos filtros atuais.",
        "diagnostics_by_currency": "### Diagnósticos por moeda",
        "only_one_currency": "Somente uma moeda encontrada nos filtros atuais.",
        "avg_balance_by_currency": "### 💱 Saldo médio por moeda",
        "summary_language_currency": "### 🌐 Resumo por idioma e moeda",
        "diagnostics_title": "## 👤 Diagnósticos",
        "risk_distribution": "### ⚠️ Distribuição por risco",
        "only_one_risk": "Somente um nível de risco encontrado nos filtros atuais.",
        "user_ranking": "### 🏆 Ranking de usuários por diagnósticos",
        "last_diagnostics": "### 🧾 Últimos diagnósticos",
        "feedbacks_title": "## 💬 Feedbacks",
        "no_feedbacks": "Nenhum feedback encontrado para os filtros selecionados.",
        "useful_feedbacks": "### 👍 Feedbacks úteis",
        "received_comments": "### 💬 Comentários recebidos",
        "no_comments": "Ainda não há comentários preenchidos.",
        "last_feedbacks": "### 🧾 Últimos feedbacks",
        "evolution_title": "## 📈 Evolução",
        "score_evolution": "### 📈 Evolução dos scores",
        "balance_evolution": "### 💵 Evolução do saldo estimado",
        "evolution_wait": "A evolução aparecerá quando houver mais de um diagnóstico no filtro.",
        "executive_title": "## 🧠 Leitura executiva",
        "current_base_summary": "### Resumo da base atual",
        "agent_eval_title": "## 🧪 Avaliação e Métricas do Agente INNA",
        "quality_indicators": "### 📌 Indicadores reais de qualidade",
        "register_eval": "### 📝 Registrar avaliação real",
        "saved_evaluations": "### 🗃️ Tabela real — avaliações salvas no Neon",
        "no_saved_evaluations": "Nenhuma avaliação real salva ainda.",
        "quality_metrics": "### 📋 Métricas de qualidade",
        "test_scenarios": "### 🧪 Cenários de teste sugeridos",
        "technical_observability": "### 📈 Métricas técnicas de observabilidade",
        "advanced_observability": "### ⚙️ Métricas avançadas de observabilidade",
        "planned_metrics": "### ⏳ Próximas métricas planejadas",
        "rag_title": "## 📊 Observabilidade RAG",
        "mode_distribution": "### Distribuição por modo",
        "no_mode_logs": "Ainda não há logs por modo.",
        "last_questions": "### Últimas perguntas",
        "no_questions": "Ainda não há perguntas registradas.",
        "export_title": "## 📤 Exportar dados filtrados",
        "no_diag_export": "Sem diagnósticos filtrados para exportar.",
        "no_feedback_export": "Sem feedbacks filtrados para exportar.",
        "no_events_export": "Sem eventos filtrados para exportar."
    },
    "en_us": {
        "no_diagnostics": "No diagnoses found for the selected filters.",
        "events_title": "## 🌐 Real multichannel events",
        "no_events": "No events found for the selected filters.",
        "only_one_channel": "Only one channel found in the current filter.",
        "last_events": dtx("view_latest_real_events"),
        "funnel_title": "## 🧭 Usage funnel",
        "few_funnel_records": "Few records in the current filter. The funnel was shown as a table to avoid an exaggerated chart.",
        "international_title": "## 🌍 International view",
        "no_international": "No international data found for the selected filters.",
        "diagnostics_by_language": "### Diagnoses by language",
        "only_one_language": "Only one language found in the current filters.",
        "diagnostics_by_currency": "### Diagnoses by currency",
        "only_one_currency": "Only one currency found in the current filters.",
        "avg_balance_by_currency": "### 💱 Average balance by currency",
        "summary_language_currency": "### 🌐 Summary by language and currency",
        "diagnostics_title": "## 👤 Diagnoses",
        "risk_distribution": "### ⚠️ Risk distribution",
        "only_one_risk": "Only one risk level found in the current filters.",
        "user_ranking": "### 🏆 User ranking by diagnoses",
        "last_diagnostics": "### 🧾 Latest diagnoses",
        "feedbacks_title": "## 💬 Feedback",
        "no_feedbacks": dtx("no_feedback_found"),
        "useful_feedbacks": "### 👍 Useful feedback",
        "received_comments": "### 💬 Received comments",
        "no_comments": "There are no comments yet.",
        "last_feedbacks": "### 🧾 Latest feedback",
        "evolution_title": "## 📈 Evolution",
        "score_evolution": "### 📈 Score evolution",
        "balance_evolution": "### 💵 Estimated balance evolution",
        "evolution_wait": "Evolution will appear when there is more than one diagnosis in the filter.",
        "executive_title": "## 🧠 Executive reading",
        "current_base_summary": "### Current base summary",
        "agent_eval_title": "## 🧪 INNA Agent Evaluation and Metrics",
        "quality_indicators": "### 📌 Real quality indicators",
        "register_eval": "### 📝 Register real evaluation",
        "saved_evaluations": "### 🗃️ Real table — evaluations saved in Neon",
        "no_saved_evaluations": "No real evaluation saved yet.",
        "quality_metrics": "### 📋 Quality metrics",
        "test_scenarios": "### 🧪 Suggested test scenarios",
        "technical_observability": "### 📈 Technical observability metrics",
        "advanced_observability": "### ⚙️ Advanced observability metrics",
        "planned_metrics": "### ⏳ Planned next metrics",
        "rag_title": "## 📊 RAG Observability",
        "mode_distribution": "### Distribution by mode",
        "no_mode_logs": "There are no mode logs yet.",
        "last_questions": "### Latest questions",
        "no_questions": "There are no registered questions yet.",
        "export_title": "## 📤 Export filtered data",
        "no_diag_export": "No filtered diagnoses to export.",
        "no_feedback_export": dtx("no_feedback_to_export"),
        "no_events_export": "No filtered events to export."
    },
    "it": {
        "no_diagnostics": "Nessuna diagnosi trovata per i filtri selezionati.",
        "events_title": "## 🌐 Eventi multicanale reali",
        "no_events": "Nessun evento trovato per i filtri selezionati.",
        "only_one_channel": "Solo un canale trovato nel filtro attuale.",
        "last_events": "Vedi ultimi eventi reali",
        "funnel_title": "## 🧭 Funnel di utilizzo",
        "few_funnel_records": "Pochi record nel filtro attuale. Il funnel è stato mostrato come tabella.",
        "international_title": "## 🌍 Vista internazionale",
        "no_international": "Nessun dato internazionale trovato per i filtri selezionati.",
        "diagnostics_by_language": "### Diagnosi per lingua",
        "only_one_language": "Solo una lingua trovata nei filtri attuali.",
        "diagnostics_by_currency": "### Diagnosi per valuta",
        "only_one_currency": "Solo una valuta trovata nei filtri attuali.",
        "avg_balance_by_currency": "### 💱 Saldo medio per valuta",
        "summary_language_currency": "### 🌐 Riepilogo per lingua e valuta",
        "diagnostics_title": "## 👤 Diagnosi",
        "risk_distribution": "### ⚠️ Distribuzione del rischio",
        "only_one_risk": "Solo un livello di rischio trovato nei filtri attuali.",
        "user_ranking": "### 🏆 Classifica utenti per diagnosi",
        "last_diagnostics": "### 🧾 Ultime diagnosi",
        "feedbacks_title": "## 💬 Feedback",
        "no_feedbacks": "Nessun feedback trovato per i filtri selezionati.",
        "useful_feedbacks": "### 👍 Feedback utili",
        "received_comments": "### 💬 Commenti ricevuti",
        "no_comments": "Non ci sono ancora commenti.",
        "last_feedbacks": "### 🧾 Ultimi feedback",
        "evolution_title": "## 📈 Evoluzione",
        "score_evolution": "### 📈 Evoluzione dei punteggi",
        "balance_evolution": "### 💵 Evoluzione del saldo stimato",
        "evolution_wait": "L’evoluzione apparirà quando ci sarà più di una diagnosi nel filtro.",
        "executive_title": "## 🧠 Lettura esecutiva",
        "current_base_summary": "### Riepilogo della base attuale",
        "agent_eval_title": "## 🧪 Valutazione e metriche dell’agente INNA",
        "quality_indicators": "### 📌 Indicatori reali di qualità",
        "register_eval": "### 📝 Registrare valutazione reale",
        "saved_evaluations": "### 🗃️ Tabella reale — valutazioni salvate in Neon",
        "no_saved_evaluations": "Nessuna valutazione reale salvata ancora.",
        "quality_metrics": "### 📋 Metriche di qualità",
        "test_scenarios": "### 🧪 Scenari di test suggeriti",
        "technical_observability": "### 📈 Metriche tecniche di osservabilità",
        "advanced_observability": "### ⚙️ Metriche avanzate di osservabilità",
        "planned_metrics": "### ⏳ Prossime metriche pianificate",
        "rag_title": "## 📊 Osservabilità RAG",
        "mode_distribution": "### Distribuzione per modalità",
        "no_mode_logs": "Non ci sono ancora log per modalità.",
        "last_questions": "### Ultime domande",
        "no_questions": "Non ci sono ancora domande registrate.",
        "export_title": "## 📤 Esporta dati filtrati",
        "no_diag_export": "Nessuna diagnosi filtrata da esportare.",
        "no_feedback_export": "Nessun feedback filtrato da esportare.",
        "no_events_export": "Nessun evento filtrato da esportare."
    }
}


# =============================
# Tradução visual de valores da interface
# Não altera dados reais do diagnóstico
# =============================

VALUE_TRANSLATIONS = {
    "pt": {
        "Todos": "Todos",
        "true": "sim",
        "false": "não",
    },
    "en_us": {
        "Todos": "All",
        "true": "yes",
        "false": "no",
    },
    "en_gb": {
        "Todos": "All",
        "true": "yes",
        "false": "no",
    },
    "es": {
        "Todos": "Todos",
        "true": "sí",
        "false": "no",
    },
    "fr": {
        "Todos": "Tous",
        "true": "oui",
        "false": "non",
    },
    "de": {
        "Todos": "Alle",
        "true": "ja",
        "false": "nein",
    },
    "it": {
        "Todos": "Tutti",
        "true": "sì",
        "false": "no",
    },
    "ro": {
        "Todos": "Toate",
        "true": "da",
        "false": "nu",
    },
    "ua": {
        "Todos": "Усі",
        "true": "так",
        "false": "ні",
    },
    "ru": {
        "Todos": "Все",
        "true": "да",
        "false": "нет",
    },
    "sa": {
        "Todos": "الكل",
        "true": "نعم",
        "false": "لا",
    },
    "ch": {
        "Todos": "Alle",
        "true": "ja",
        "false": "nein",
    },
}

def tv(value):
    lang = dashboard_lang()
    value_text = str(value)
    return VALUE_TRANSLATIONS.get(lang, VALUE_TRANSLATIONS["pt"]).get(value_text, value)


# =============================
# PATCH PÁGINAS INTERNAS POR IDIOMA
# Traduz apenas interface
# Não altera resultados reais do diagnóstico
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "events_title": "## 🌐 Eventos multicanal reales",
    "funnel_title": "## 🧭 Embudo de uso",
    "international_title": "## 🌍 Vista internacional",
    "diagnostics_by_language": "### Diagnósticos por idioma",
    "diagnostics_by_currency": "### Diagnósticos por moneda",
    "avg_balance_by_currency": "### 💱 Saldo medio por moneda",
    "summary_language_currency": "### 🌐 Resumen por idioma y moneda",
    "diagnostics_title": "## 👤 Diagnósticos",
    "risk_distribution": "### ⚠️ Distribución de riesgo",
    "user_ranking": "### 🏆 Ranking de usuarios por diagnósticos",
    "last_diagnostics": "### 🧾 Últimos diagnósticos",
    "feedbacks_title": "## 💬 Feedbacks",
    "useful_feedbacks": "### 👍 Feedbacks útiles",
    "received_comments": "### 💬 Comentarios recibidos",
    "last_feedbacks": "### 🧾 Últimos feedbacks",
    "evolution_title": "## 📈 Evolución",
    "score_evolution": "### 📈 Evolución de scores",
    "balance_evolution": "### 💵 Evolución del saldo estimado",
    "executive_title": "## 🧠 Lectura ejecutiva",
    "current_base_summary": "### Resumen de la base actual",
    "agent_eval_title": "## 🧪 Evaluación y métricas del agente INNA",
    "quality_indicators": "### 📌 Indicadores reales de calidad",
    "register_eval": "### 📝 Registrar evaluación real",
    "saved_evaluations": "### 🗃️ Tabla real — evaluaciones guardadas en Neon",
    "quality_metrics": "### 📋 Métricas de calidad",
    "rag_title": "## 📊 Observabilidad RAG",
    "mode_distribution": "### Distribución por modo",
    "last_questions": "### Últimas preguntas",
    "export_title": "## 📤 Exportar datos filtrados",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update({
    "events_title": "## 🌐 Événements multicanaux réels",
    "funnel_title": "## 🧭 Entonnoir d’utilisation",
    "international_title": "## 🌍 Vue internationale",
    "diagnostics_by_language": "### Diagnostics par langue",
    "diagnostics_by_currency": "### Diagnostics par devise",
    "avg_balance_by_currency": "### 💱 Solde moyen par devise",
    "summary_language_currency": "### 🌐 Résumé par langue et devise",
    "diagnostics_title": "## 👤 Diagnostics",
    "risk_distribution": "### ⚠️ Répartition du risque",
    "user_ranking": "### 🏆 Classement des utilisateurs par diagnostics",
    "last_diagnostics": "### 🧾 Derniers diagnostics",
    "feedbacks_title": "## 💬 Feedbacks",
    "useful_feedbacks": "### 👍 Feedbacks utiles",
    "received_comments": "### 💬 Commentaires reçus",
    "last_feedbacks": "### 🧾 Derniers feedbacks",
    "evolution_title": "## 📈 Évolution",
    "score_evolution": "### 📈 Évolution des scores",
    "balance_evolution": "### 💵 Évolution du solde estimé",
    "executive_title": "## 🧠 Lecture exécutive",
    "current_base_summary": "### Résumé de la base actuelle",
    "agent_eval_title": "## 🧪 Évaluation et métriques de l’agent INNA",
    "quality_indicators": "### 📌 Indicateurs réels de qualité",
    "register_eval": "### 📝 Enregistrer une évaluation réelle",
    "saved_evaluations": "### 🗃️ Tableau réel — évaluations enregistrées dans Neon",
    "quality_metrics": "### 📋 Métriques de qualité",
    "rag_title": "## 📊 Observabilité RAG",
    "mode_distribution": "### Distribution par mode",
    "last_questions": "### Dernières questions",
    "export_title": "## 📤 Exporter les données filtrées",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "events_title": "## 🌐 Reale Multichannel-Ereignisse",
    "funnel_title": "## 🧭 Nutzungstrichter",
    "international_title": "## 🌍 Internationale Ansicht",
    "diagnostics_by_language": "### Diagnosen nach Sprache",
    "diagnostics_by_currency": "### Diagnosen nach Währung",
    "avg_balance_by_currency": "### 💱 Durchschnittlicher Saldo nach Währung",
    "summary_language_currency": "### 🌐 Zusammenfassung nach Sprache und Währung",
    "diagnostics_title": "## 👤 Diagnosen",
    "risk_distribution": "### ⚠️ Risikoverteilung",
    "user_ranking": "### 🏆 Benutzer-Ranking nach Diagnosen",
    "last_diagnostics": "### 🧾 Letzte Diagnosen",
    "feedbacks_title": "## 💬 Feedbacks",
    "useful_feedbacks": "### 👍 Nützliches Feedback",
    "received_comments": "### 💬 Erhaltene Kommentare",
    "last_feedbacks": "### 🧾 Letzte Feedbacks",
    "evolution_title": "## 📈 Entwicklung",
    "score_evolution": "### 📈 Score-Entwicklung",
    "balance_evolution": "### 💵 Entwicklung des geschätzten Saldos",
    "executive_title": "## 🧠 Executive Summary",
    "current_base_summary": "### Zusammenfassung der aktuellen Basis",
    "agent_eval_title": "## 🧪 Bewertung und Metriken des INNA-Agenten",
    "quality_indicators": "### 📌 Reale Qualitätsindikatoren",
    "register_eval": "### 📝 Reale Bewertung registrieren",
    "saved_evaluations": "### 🗃️ Reale Tabelle — Bewertungen in Neon gespeichert",
    "quality_metrics": "### 📋 Qualitätsmetriken",
    "rag_title": "## 📊 RAG-Beobachtbarkeit",
    "mode_distribution": "### Verteilung nach Modus",
    "last_questions": "### Letzte Fragen",
    "export_title": "## 📤 Gefilterte Daten exportieren",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update({
    "events_title": "## 🌐 Evenimente multicanal reale",
    "funnel_title": "## 🧭 Funnel de utilizare",
    "international_title": "## 🌍 Vedere internațională",
    "diagnostics_by_language": "### Diagnosticări după limbă",
    "diagnostics_by_currency": "### Diagnosticări după monedă",
    "avg_balance_by_currency": "### 💱 Sold mediu după monedă",
    "summary_language_currency": "### 🌐 Rezumat după limbă și monedă",
    "diagnostics_title": "## 👤 Diagnosticări",
    "risk_distribution": "### ⚠️ Distribuția riscului",
    "user_ranking": "### 🏆 Clasamentul utilizatorilor după diagnosticări",
    "last_diagnostics": "### 🧾 Ultimele diagnosticări",
    "feedbacks_title": "## 💬 Feedbackuri",
    "useful_feedbacks": "### 👍 Feedbackuri utile",
    "received_comments": "### 💬 Comentarii primite",
    "last_feedbacks": "### 🧾 Ultimele feedbackuri",
    "evolution_title": "## 📈 Evoluție",
    "score_evolution": "### 📈 Evoluția scorurilor",
    "balance_evolution": "### 💵 Evoluția soldului estimat",
    "executive_title": "## 🧠 Citire executivă",
    "current_base_summary": "### Rezumatul bazei actuale",
    "agent_eval_title": "## 🧪 Evaluarea și metricile agentului INNA",
    "quality_indicators": "### 📌 Indicatori reali de calitate",
    "register_eval": "### 📝 Înregistrează evaluare reală",
    "saved_evaluations": "### 🗃️ Tabel real — evaluări salvate în Neon",
    "quality_metrics": "### 📋 Metrici de calitate",
    "rag_title": "## 📊 Observabilitate RAG",
    "mode_distribution": "### Distribuție după mod",
    "last_questions": "### Ultimele întrebări",
    "export_title": "## 📤 Exportă datele filtrate",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    "events_title": "## 🌐 Реальные многоканальные события",
    "funnel_title": "## 🧭 Воронка использования",
    "international_title": "## 🌍 Международный обзор",
    "diagnostics_by_language": "### Диагностики по языку",
    "diagnostics_by_currency": "### Диагностики по валюте",
    "avg_balance_by_currency": "### 💱 Средний баланс по валюте",
    "summary_language_currency": "### 🌐 Сводка по языку и валюте",
    "diagnostics_title": "## 👤 Диагностики",
    "risk_distribution": "### ⚠️ Распределение риска",
    "user_ranking": "### 🏆 Рейтинг пользователей по диагностикам",
    "last_diagnostics": "### 🧾 Последние диагностики",
    "feedbacks_title": "## 💬 Отзывы",
    "useful_feedbacks": "### 👍 Полезные отзывы",
    "received_comments": "### 💬 Полученные комментарии",
    "last_feedbacks": "### 🧾 Последние отзывы",
    "evolution_title": "## 📈 Динамика",
    "score_evolution": "### 📈 Динамика баллов",
    "balance_evolution": "### 💵 Динамика оценочного баланса",
    "executive_title": "## 🧠 Краткий отчет",
    "current_base_summary": "### Сводка текущей базы",
    "agent_eval_title": "## 🧪 Оценка и метрики агента INNA",
    "quality_indicators": "### 📌 Реальные показатели качества",
    "register_eval": "### 📝 Зарегистрировать реальную оценку",
    "saved_evaluations": "### 🗃️ Реальная таблица — оценки сохранены в Neon",
    "quality_metrics": "### 📋 Метрики качества",
    "rag_title": "## 📊 Наблюдаемость RAG",
    "mode_distribution": "### Распределение по режиму",
    "last_questions": "### Последние вопросы",
    "export_title": "## 📤 Экспортировать отфильтрованные данные",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update({
    "events_title": "## 🌐 Реальні багатоканальні події",
    "funnel_title": "## 🧭 Воронка використання",
    "international_title": "## 🌍 Міжнародний огляд",
    "diagnostics_by_language": "### Діагностики за мовою",
    "diagnostics_by_currency": "### Діагностики за валютою",
    "avg_balance_by_currency": "### 💱 Середній баланс за валютою",
    "summary_language_currency": "### 🌐 Підсумок за мовою та валютою",
    "diagnostics_title": "## 👤 Діагностики",
    "risk_distribution": "### ⚠️ Розподіл ризику",
    "user_ranking": "### 🏆 Рейтинг користувачів за діагностиками",
    "last_diagnostics": "### 🧾 Останні діагностики",
    "feedbacks_title": "## 💬 Відгуки",
    "useful_feedbacks": "### 👍 Корисні відгуки",
    "received_comments": "### 💬 Отримані коментарі",
    "last_feedbacks": "### 🧾 Останні відгуки",
    "evolution_title": "## 📈 Динаміка",
    "score_evolution": "### 📈 Динаміка балів",
    "balance_evolution": "### 💵 Динаміка орієнтовного балансу",
    "executive_title": "## 🧠 Виконавче резюме",
    "current_base_summary": "### Підсумок поточної бази",
    "agent_eval_title": "## 🧪 Оцінка та метрики агента INNA",
    "quality_indicators": "### 📌 Реальні показники якості",
    "register_eval": "### 📝 Зареєструвати реальну оцінку",
    "saved_evaluations": "### 🗃️ Реальна таблиця — оцінки збережені в Neon",
    "quality_metrics": "### 📋 Метрики якості",
    "rag_title": "## 📊 Спостережуваність RAG",
    "mode_distribution": "### Розподіл за режимом",
    "last_questions": "### Останні запитання",
    "export_title": "## 📤 Експортувати відфільтровані дані",
})

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "events_title": "## 🌐 أحداث حقيقية متعددة القنوات",
    "funnel_title": "## 🧭 قمع الاستخدام",
    "international_title": "## 🌍 العرض الدولي",
    "diagnostics_by_language": "### التشخيصات حسب اللغة",
    "diagnostics_by_currency": "### التشخيصات حسب العملة",
    "avg_balance_by_currency": "### 💱 متوسط الرصيد حسب العملة",
    "summary_language_currency": "### 🌐 ملخص حسب اللغة والعملة",
    "diagnostics_title": "## 👤 التشخيصات",
    "risk_distribution": "### ⚠️ توزيع المخاطر",
    "user_ranking": "### 🏆 ترتيب المستخدمين حسب التشخيصات",
    "last_diagnostics": "### 🧾 أحدث التشخيصات",
    "feedbacks_title": "## 💬 الملاحظات",
    "useful_feedbacks": "### 👍 الملاحظات المفيدة",
    "received_comments": "### 💬 التعليقات المستلمة",
    "last_feedbacks": "### 🧾 أحدث الملاحظات",
    "evolution_title": "## 📈 التطور",
    "score_evolution": "### 📈 تطور النتائج",
    "balance_evolution": "### 💵 تطور الرصيد التقديري",
    "executive_title": "## 🧠 القراءة التنفيذية",
    "current_base_summary": "### ملخص القاعدة الحالية",
    "agent_eval_title": "## 🧪 تقييم ومقاييس وكيل INNA",
    "quality_indicators": "### 📌 مؤشرات الجودة الحقيقية",
    "register_eval": "### 📝 تسجيل تقييم حقيقي",
    "saved_evaluations": "### 🗃️ جدول حقيقي — التقييمات المحفوظة في Neon",
    "quality_metrics": "### 📋 مقاييس الجودة",
    "rag_title": "## 📊 مراقبة RAG",
    "mode_distribution": "### التوزيع حسب الوضع",
    "last_questions": "### أحدث الأسئلة",
    "export_title": "## 📤 تصدير البيانات المفلترة",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))


# =============================
# PATCH FINAL - TEXTOS INTERNOS DO DASHBOARD
# Traduz somente interface. Não altera resultados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "real_events": "الأحداث الحقيقية",
    "active_channels": "القنوات النشطة",
    "latest_channel_metric": "آخر قناة",
    "only_one_channel": "تم العثور على قناة واحدة فقط في الفلتر الحالي.",
    "last_events": "عرض أحدث الأحداث الحقيقية",

    "usage_funnel": "قمع الاستخدام",
    "downloaded_pdfs": "ملفات PDF التي تم تنزيلها",
    "emails": "رسائل البريد الإلكتروني",
    "pdf_rate": "معدل PDF",
    "few_funnel_records": "توجد سجلات قليلة في الفلتر الحالي. تم عرض القمع كجدول لتجنب رسم بياني مبالغ فيه.",

    "no_diagnostics": "لم يتم العثور على تشخيصات للفلاتر المحددة.",
    "no_feedbacks": "لم يتم العثور على ملاحظات للفلاتر المحددة.",
    "no_comments": "لا توجد تعليقات مكتوبة حتى الآن.",
    "no_saved_evaluations": "لم يتم حفظ أي تقييم حقيقي بعد.",
    "no_mode_logs": "لا توجد سجلات حسب الوضع حتى الآن.",
    "no_questions": "لا توجد أسئلة مسجلة حتى الآن.",

    "real_quality_indicators": "مؤشرات الجودة الحقيقية",
    "evaluator_name": "اسم المقيم",
    "assertiveness": "الدقة",
    "security": "الأمان",
    "conviction": "القناعة",
    "clarity": "الوضوح",
    "utility": "الفائدة",
    "open_comment": "تعليق مفتوح",
    "save_evaluation": "حفظ التقييم في Neon",

    "suggested_test_scenarios": "سيناريوهات اختبار مقترحة",
    "technical_observability": "مقاييس المراقبة التقنية",
    "advanced_observability": "مقاييس المراقبة المتقدمة",
    "planned_metrics": "المقاييس المخطط لها",

    "questions": "الأسئلة",
    "average_time": "متوسط الوقت",
    "largest_response_time": "أطول وقت استجابة",

    "export_diagnostics_csv": "تنزيل التشخيصات المفلترة CSV",
    "export_feedbacks_csv": "تنزيل الملاحظات المفلترة CSV",
    "export_events_csv": "تنزيل الأحداث المفلترة CSV",
    "no_feedback_export": "لا توجد ملاحظات مفلترة للتصدير.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "real_events": "real_events",
    "active_channels": "active_channels",
    "latest_channel_metric": "latest_channel_metric",
    "usage_funnel": "Usage funnel",
    "downloaded_pdfs": "downloaded_pdfs",
    "emails": "emails",
    "pdf_rate": "pdf_rate",
    "real_quality_indicators": "Real quality indicators",
    "evaluator_name": "Evaluator name",
    "assertiveness": "Assertiveness",
    "security": "Security",
    "conviction": "Conviction",
    "clarity": "Clarity",
    "utility": "Utility",
    "open_comment": "Open comment",
    "save_evaluation": "Save evaluation in Neon",
    "suggested_test_scenarios": "Suggested test scenarios",
    "technical_observability": "Technical observability metrics",
    "advanced_observability": "Advanced observability metrics",
    "planned_metrics": "Planned next metrics",
    "questions": "Questions",
    "average_time": "Average time",
    "largest_response_time": "Largest response time",
    "export_diagnostics_csv": "Download filtered diagnoses CSV",
    "export_feedbacks_csv": "Download filtered feedback CSV",
    "export_events_csv": "Download filtered events CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "real_events": "Eventos reais",
    "active_channels": "Canais ativos",
    "latest_channel_metric": "Último canal",
    "usage_funnel": "Funil de uso",
    "downloaded_pdfs": "PDFs baixados",
    "emails": "emails",
    "pdf_rate": "Taxa PDF",
    "real_quality_indicators": "Indicadores reais de qualidade",
    "evaluator_name": "Nome do avaliador",
    "assertiveness": "Assertividade",
    "security": "Segurança",
    "conviction": "Convicção",
    "clarity": "Clareza",
    "utility": "Utilidade",
    "open_comment": "Comentário aberto",
    "save_evaluation": "Salvar avaliação no Neon",
    "suggested_test_scenarios": "Cenários de teste sugeridos",
    "technical_observability": "Métricas técnicas de observabilidade",
    "advanced_observability": "Métricas avançadas de observabilidade",
    "planned_metrics": "Próximas métricas planejadas",
    "questions": "Perguntas",
    "average_time": "Tempo médio",
    "largest_response_time": "Maior tempo de resposta",
    "export_diagnostics_csv": "Baixar diagnósticos filtrados CSV",
    "export_feedbacks_csv": "Baixar feedbacks filtrados CSV",
    "export_events_csv": "Baixar eventos filtrados CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "real_events": "Eventos reales",
    "active_channels": "Canales activos",
    "latest_channel_metric": "Último canal",
    "usage_funnel": "Embudo de uso",
    "downloaded_pdfs": "PDFs descargados",
    "emails": "emails",
    "pdf_rate": "Tasa PDF",
    "real_quality_indicators": "Indicadores reales de calidad",
    "evaluator_name": "Nombre del evaluador",
    "assertiveness": "Asertividad",
    "security": "Seguridad",
    "conviction": "Convicción",
    "clarity": "Claridad",
    "utility": "Utilidad",
    "open_comment": "Comentario abierto",
    "save_evaluation": "Guardar evaluación en Neon",
    "suggested_test_scenarios": "Escenarios de prueba sugeridos",
    "technical_observability": "Métricas técnicas de observabilidad",
    "advanced_observability": "Métricas avanzadas de observabilidad",
    "planned_metrics": "Próximas métricas planificadas",
    "questions": "Preguntas",
    "average_time": "Tiempo medio",
    "largest_response_time": "Mayor tiempo de respuesta",
    "export_diagnostics_csv": "Descargar diagnósticos filtrados CSV",
    "export_feedbacks_csv": "Descargar feedbacks filtrados CSV",
    "export_events_csv": "Descargar eventos filtrados CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update({
    "real_events": "Événements réels",
    "active_channels": "Canaux actifs",
    "latest_channel_metric": "Dernier canal",
    "usage_funnel": "Entonnoir d’utilisation",
    "downloaded_pdfs": "PDF téléchargés",
    "emails": "emails",
    "pdf_rate": "Taux PDF",
    "real_quality_indicators": "Indicateurs réels de qualité",
    "evaluator_name": "Nom de l’évaluateur",
    "assertiveness": "Pertinence",
    "security": "Sécurité",
    "conviction": "Conviction",
    "clarity": "Clarté",
    "utility": "Utilité",
    "open_comment": "Commentaire ouvert",
    "save_evaluation": "Enregistrer l’évaluation dans Neon",
    "suggested_test_scenarios": "Scénarios de test suggérés",
    "technical_observability": "Métriques techniques d’observabilité",
    "advanced_observability": "Métriques avancées d’observabilité",
    "planned_metrics": "Prochaines métriques planifiées",
    "questions": "Questions",
    "average_time": "Temps moyen",
    "largest_response_time": "Plus long temps de réponse",
    "export_diagnostics_csv": "Télécharger les diagnostics filtrés CSV",
    "export_feedbacks_csv": "Télécharger les feedbacks filtrés CSV",
    "export_events_csv": "Télécharger les événements filtrés CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "real_events": "Reale Ereignisse",
    "active_channels": "Aktive Kanäle",
    "latest_channel_metric": "Letzter Kanal",
    "usage_funnel": "Nutzungstrichter",
    "downloaded_pdfs": "Heruntergeladene PDFs",
    "emails": "E-Mails",
    "pdf_rate": "PDF-Rate",
    "real_quality_indicators": "Reale Qualitätsindikatoren",
    "evaluator_name": "Name des Bewerters",
    "assertiveness": "Treffsicherheit",
    "security": "Sicherheit",
    "conviction": "Überzeugung",
    "clarity": "Klarheit",
    "utility": "Nützlichkeit",
    "open_comment": "Offener Kommentar",
    "save_evaluation": "Bewertung in Neon speichern",
    "suggested_test_scenarios": "Vorgeschlagene Testszenarien",
    "technical_observability": "Technische Beobachtbarkeitsmetriken",
    "advanced_observability": "Erweiterte Beobachtbarkeitsmetriken",
    "planned_metrics": "Geplante nächste Metriken",
    "questions": "Fragen",
    "average_time": "Durchschnittliche Zeit",
    "largest_response_time": "Längste Antwortzeit",
    "export_diagnostics_csv": "Gefilterte Diagnosen CSV herunterladen",
    "export_feedbacks_csv": "Gefiltertes Feedback CSV herunterladen",
    "export_events_csv": "Gefilterte Ereignisse CSV herunterladen",
})

DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update({
    "real_events": "Eventi reali",
    "active_channels": "Canali attivi",
    "latest_channel_metric": "Ultimo canale",
    "usage_funnel": "Funnel di utilizzo",
    "downloaded_pdfs": "PDF scaricati",
    "emails": "E-mail",
    "pdf_rate": "Tasso PDF",
    "real_quality_indicators": "Indicatori reali di qualità",
    "evaluator_name": "Nome del valutatore",
    "assertiveness": "Assertività",
    "security": "Sicurezza",
    "conviction": "Convinzione",
    "clarity": "Chiarezza",
    "utility": "Utilità",
    "open_comment": "Commento aperto",
    "save_evaluation": "Salva valutazione in Neon",
    "suggested_test_scenarios": "Scenari di test suggeriti",
    "technical_observability": "Metriche tecniche di osservabilità",
    "advanced_observability": "Metriche avanzate di osservabilità",
    "planned_metrics": "Prossime metriche pianificate",
    "questions": "Domande",
    "average_time": "Tempo medio",
    "largest_response_time": "Tempo di risposta massimo",
    "export_diagnostics_csv": "Scarica diagnosi filtrate CSV",
    "export_feedbacks_csv": "Scarica feedback filtrati CSV",
    "export_events_csv": "Scarica eventi filtrati CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update({
    "real_events": "Evenimente reale",
    "active_channels": "Canale active",
    "latest_channel_metric": "Ultimul canal",
    "usage_funnel": "Funnel de utilizare",
    "downloaded_pdfs": "PDF-uri descărcate",
    "emails": "E-mailuri",
    "pdf_rate": "Rată PDF",
    "real_quality_indicators": "Indicatori reali de calitate",
    "evaluator_name": "Numele evaluatorului",
    "assertiveness": "Acuratețe",
    "security": "Siguranță",
    "conviction": "Convingere",
    "clarity": "Claritate",
    "utility": "Utilitate",
    "open_comment": "Comentariu deschis",
    "save_evaluation": "Salvează evaluarea în Neon",
    "suggested_test_scenarios": "Scenarii de test sugerate",
    "technical_observability": "Metrici tehnice de observabilitate",
    "advanced_observability": "Metrici avansate de observabilitate",
    "planned_metrics": "Următoarele metrici planificate",
    "questions": "Întrebări",
    "average_time": "Timp mediu",
    "largest_response_time": "Cel mai mare timp de răspuns",
    "export_diagnostics_csv": "Descarcă diagnosticări filtrate CSV",
    "export_feedbacks_csv": "Descarcă feedback filtrat CSV",
    "export_events_csv": "Descarcă evenimente filtrate CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update({
    "real_events": "Реальні події",
    "active_channels": "Активні канали",
    "latest_channel_metric": "Останній канал",
    "usage_funnel": "Воронка використання",
    "downloaded_pdfs": "Завантажені PDF",
    "emails": "E-mail",
    "pdf_rate": "PDF-рівень",
    "real_quality_indicators": "Реальні показники якості",
    "evaluator_name": "Ім’я оцінювача",
    "assertiveness": "Точність",
    "security": "Безпека",
    "conviction": "Переконливість",
    "clarity": "Зрозумілість",
    "utility": "Корисність",
    "open_comment": "Відкритий коментар",
    "save_evaluation": "Зберегти оцінку в Neon",
    "suggested_test_scenarios": "Запропоновані тестові сценарії",
    "technical_observability": "Технічні метрики спостережуваності",
    "advanced_observability": "Розширені метрики спостережуваності",
    "planned_metrics": "Заплановані наступні метрики",
    "questions": "Питання",
    "average_time": "Середній час",
    "largest_response_time": "Найбільший час відповіді",
    "export_diagnostics_csv": "Завантажити відфільтровані діагностики CSV",
    "export_feedbacks_csv": "Завантажити відфільтровані відгуки CSV",
    "export_events_csv": "Завантажити відфільтровані події CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "usage_funnel": "Воронка использования",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "pdf_rate": "Доля PDF",
    "real_quality_indicators": "Реальные показатели качества",
    "evaluator_name": "Имя оценщика",
    "assertiveness": "Точность",
    "security": "Безопасность",
    "conviction": "Убедительность",
    "clarity": "Ясность",
    "utility": "Полезность",
    "open_comment": "Открытый комментарий",
    "save_evaluation": "Сохранить оценку в Neon",
    "suggested_test_scenarios": "Предложенные тестовые сценарии",
    "technical_observability": "Технические метрики наблюдаемости",
    "advanced_observability": "Расширенные метрики наблюдаемости",
    "planned_metrics": "Запланированные следующие метрики",
    "questions": "Вопросы",
    "average_time": "Среднее время",
    "largest_response_time": "Максимальное время ответа",
    "export_diagnostics_csv": "Скачать отфильтрованные диагностики CSV",
    "export_feedbacks_csv": "Скачать отфильтрованные отзывы CSV",
    "export_events_csv": "Скачать отфильтрованные события CSV",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))


# =============================
# PATCH EXPORTAÇÃO MULTILÍNGUE
# Traduz apenas interface dos botões/mensagens
# Não altera dados exportados
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "export_diagnostics_csv": "Baixar diagnósticos filtrados CSV",
    "export_feedbacks_csv": "Baixar feedbacks filtrados CSV",
    "export_events_csv": "Baixar eventos filtrados CSV",
    "no_diag_export": "Sem diagnósticos filtrados para exportar.",
    "no_feedback_export": "Sem feedbacks filtrados para exportar.",
    "no_events_export": "Sem eventos filtrados para exportar.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "export_diagnostics_csv": "Download filtered diagnoses CSV",
    "export_feedbacks_csv": "Download filtered feedback CSV",
    "export_events_csv": "Download filtered events CSV",
    "no_diag_export": "No filtered diagnoses to export.",
    "no_feedback_export": dtx("no_feedback_to_export"),
    "no_events_export": "No filtered events to export.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update({
    "export_diagnostics_csv": "Download filtered diagnoses CSV",
    "export_feedbacks_csv": "Download filtered feedback CSV",
    "export_events_csv": "Download filtered events CSV",
    "no_diag_export": "No filtered diagnoses to export.",
    "no_feedback_export": dtx("no_feedback_to_export"),
    "no_events_export": "No filtered events to export.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "export_diagnostics_csv": "Descargar diagnósticos filtrados CSV",
    "export_feedbacks_csv": "Descargar feedbacks filtrados CSV",
    "export_events_csv": "Descargar eventos filtrados CSV",
    "no_diag_export": "No hay diagnósticos filtrados para exportar.",
    "no_feedback_export": "No hay feedbacks filtrados para exportar.",
    "no_events_export": "No hay eventos filtrados para exportar.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update({
    "export_diagnostics_csv": "Télécharger les diagnostics filtrés CSV",
    "export_feedbacks_csv": "Télécharger les feedbacks filtrés CSV",
    "export_events_csv": "Télécharger les événements filtrés CSV",
    "no_diag_export": "Aucun diagnostic filtré à exporter.",
    "no_feedback_export": "Aucun feedback filtré à exporter.",
    "no_events_export": "Aucun événement filtré à exporter.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "export_diagnostics_csv": "Gefilterte Diagnosen als CSV herunterladen",
    "export_feedbacks_csv": "Gefiltertes Feedback als CSV herunterladen",
    "export_events_csv": "Gefilterte Ereignisse als CSV herunterladen",
    "no_diag_export": "Keine gefilterten Diagnosen zum Exportieren.",
    "no_feedback_export": "Kein gefiltertes Feedback zum Exportieren.",
    "no_events_export": "Keine gefilterten Ereignisse zum Exportieren.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update({
    "export_diagnostics_csv": "Scarica diagnosi filtrate CSV",
    "export_feedbacks_csv": "Scarica feedback filtrati CSV",
    "export_events_csv": "Scarica eventi filtrati CSV",
    "no_diag_export": "Nessuna diagnosi filtrata da esportare.",
    "no_feedback_export": "Nessun feedback filtrato da esportare.",
    "no_events_export": "Nessun evento filtrato da esportare.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update({
    "export_diagnostics_csv": "Descarcă diagnosticări filtrate CSV",
    "export_feedbacks_csv": "Descarcă feedback filtrat CSV",
    "export_events_csv": "Descarcă evenimente filtrate CSV",
    "no_diag_export": "Nu există diagnosticări filtrate pentru export.",
    "no_feedback_export": "Nu există feedback filtrat pentru export.",
    "no_events_export": "Nu există evenimente filtrate pentru export.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update({
    "export_diagnostics_csv": "Завантажити відфільтровані діагностики CSV",
    "export_feedbacks_csv": "Завантажити відфільтровані відгуки CSV",
    "export_events_csv": "Завантажити відфільтровані події CSV",
    "no_diag_export": "Немає відфільтрованих діагностик для експорту.",
    "no_feedback_export": "Немає відфільтрованих відгуків для експорту.",
    "no_events_export": "Немає відфільтрованих подій для експорту.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    "export_diagnostics_csv": "Скачать отфильтрованные диагностики CSV",
    "export_feedbacks_csv": "Скачать отфильтрованные отзывы CSV",
    "export_events_csv": "Скачать отфильтрованные события CSV",
    "no_diag_export": "Нет отфильтрованных диагностик для экспорта.",
    "no_feedback_export": "Нет отфильтрованных отзывов для экспорта.",
    "no_events_export": "Нет отфильтрованных событий для экспорта.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "export_diagnostics_csv": "تنزيل التشخيصات المفلترة CSV",
    "export_feedbacks_csv": "تنزيل الملاحظات المفلترة CSV",
    "export_events_csv": "تنزيل الأحداث المفلترة CSV",
    "no_diag_export": "لا توجد تشخيصات مفلترة للتصدير.",
    "no_feedback_export": "لا توجد ملاحظات مفلترة للتصدير.",
    "no_events_export": "لا توجد أحداث مفلترة للتصدير.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update({
    "export_diagnostics_csv": "Gefilterte Diagnosen als CSV herunterladen",
    "export_feedbacks_csv": "Gefiltertes Feedback als CSV herunterladen",
    "export_events_csv": "Gefilterte Ereignisse als CSV herunterladen",
    "no_diag_export": "Keine gefilterten Diagnosen zum Exportieren.",
    "no_feedback_export": "Kein gefiltertes Feedback zum Exportieren.",
    "no_events_export": "Keine gefilterten Ereignisse zum Exportieren.",
})


# =============================
# Tradução visual das etapas do funil/eventos
# Não altera dados reais do banco
# =============================

FUNNEL_VALUE_TRANSLATIONS = {
    "pt": {
        "Diagnóstico gerado": "Diagnóstico gerado",
        "PDF baixado": "PDF baixado",
        "E-mail enviado": "E-mail enviado",
        "Feedback recebido": "Feedback recebido",
        "Telegram": "Telegram",
    },
    "en_us": {
        "Diagnóstico gerado": "Diagnosis generated",
        "PDF baixado": "PDF downloaded",
        "E-mail enviado": "Email sent",
        "Feedback recebido": "Feedback received",
        "Telegram": "Telegram",
    },
    "en_gb": {
        "Diagnóstico gerado": "Diagnosis generated",
        "PDF baixado": "PDF downloaded",
        "E-mail enviado": "Email sent",
        "Feedback recebido": "Feedback received",
        "Telegram": "Telegram",
    },
    "es": {
        "Diagnóstico gerado": "Diagnóstico generado",
        "PDF baixado": "PDF descargado",
        "E-mail enviado": "Correo electrónico enviado",
        "Feedback recebido": "Feedback recibido",
        "Telegram": "Telegram",
    },
    "fr": {
        "Diagnóstico gerado": "Diagnostic généré",
        "PDF baixado": "PDF téléchargé",
        "E-mail enviado": "E-mail envoyé",
        "Feedback recebido": "Feedback reçu",
        "Telegram": "Telegram",
    },
    "de": {
        "Diagnóstico gerado": "Diagnose erstellt",
        "PDF baixado": "PDF heruntergeladen",
        "E-mail enviado": "E-Mail gesendet",
        "Feedback recebido": "Feedback erhalten",
        "Telegram": "Telegram",
    },
    "it": {
        "Diagnóstico gerado": "Diagnosi generata",
        "PDF baixado": "PDF scaricato",
        "E-mail enviado": "E-mail inviata",
        "Feedback recebido": "Feedback ricevuto",
        "Telegram": "Telegram",
    },
    "ro": {
        "Diagnóstico gerado": "Diagnosticare generată",
        "PDF baixado": "PDF descărcat",
        "E-mail enviado": "E-mail trimis",
        "Feedback recebido": "Feedback primit",
        "Telegram": "Telegram",
    },
    "ua": {
        "Diagnóstico gerado": "Діагностику створено",
        "PDF baixado": "PDF завантажено",
        "E-mail enviado": "E-mail надіслано",
        "Feedback recebido": "Відгук отримано",
        "Telegram": "Telegram",
    },
    "ru": {
        "Diagnóstico gerado": "Диагностика создана",
        "PDF baixado": "PDF скачан",
        "E-mail enviado": "E-mail отправлен",
        "Feedback recebido": "Отзыв получен",
        "Telegram": "Telegram",
    },
    "sa": {
        "Diagnóstico gerado": "تم إنشاء التشخيص",
        "PDF baixado": "تم تنزيل ملف PDF",
        "E-mail enviado": "تم إرسال البريد الإلكتروني",
        "Feedback recebido": "تم استلام الملاحظات",
        "Telegram": "تيليجرام",
    },
    "ch": {
        "Diagnóstico gerado": "Diagnose erstellt",
        "PDF baixado": "PDF heruntergeladen",
        "E-mail enviado": "E-Mail gesendet",
        "Feedback recebido": "Feedback erhalten",
        "Telegram": "Telegram",
    },
}

def tfunnel(value):
    lang = dashboard_lang()
    value_text = str(value)
    return FUNNEL_VALUE_TRANSLATIONS.get(lang, FUNNEL_VALUE_TRANSLATIONS["pt"]).get(value_text, value)


# =============================
# PATCH AVALIAÇÃO DO AGENTE MULTILÍNGUE
# Traduz somente interface. Não altera resultados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "agent_eval_info": "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade.",
    "evaluations": "Avaliações",
    "general_average": "Média geral",
    "assertiveness": "Assertividade",
    "security": "Segurança",
    "coherence": "Coerência",
    "clarity": "Clareza",
    "average_utility": "Utilidade média",
    "evaluator_name": "Nome do avaliador",
    "evaluator_placeholder": "Exemplo: Participante 1, colega, familiar, recrutador...",
    "assertiveness_question": "Assertividade — respondeu corretamente?",
    "security_question": "Segurança — evitou inventar informações?",
    "coherence_question": "Coerência — fez sentido para o perfil?",
    "clarity_question": "Clareza — linguagem simples e fácil?",
    "utility_question": "Utilidade — ajudou de verdade?",
    "open_comment": "Comentário aberto",
    "open_comment_placeholder": "O que funcionou bem? O que poderia melhorar?",
    "no_saved_evaluations": "Nenhuma avaliação real salva ainda.",
    "suggested_test_scenarios": "🧪 Cenários de teste sugeridos",
    "technical_observability": "Métricas de observabilidade técnica",
    "advanced_observability": "Métricas de observabilidade avançada",
    "planned_metrics": "Métricas planejadas",
    "events_label": "Eventos",
    "active_languages": "Idiomas ativos",
    "avg_time": "Tempo médio",
    "error_rate": "Taxa de erro",
    "success_events": "Eventos sucesso",
    "error_events": "Eventos erro",
    "logs_events": "Logs/eventos",
    "tokens_used": "Tokens consumidos",
    "estimated_cost": "Custo estimado",
    "advanced_metrics_note": "Tokens e custo estimado aparecem com valor real quando a API salva essas informações no metadata dos eventos. Latência, status e logs já usam os eventos reais do Neon.",
    "how_to_read_metrics": "📘 Como interpretar as métricas avançadas",
    "planned_metrics_text": "Essas métricas fazem parte da evolução planejada da INNA. Elas ainda não estão ativas para evitar custos desnecessários neste momento, mas a arquitetura do projeto já está preparada para receber esses dados futuramente.",
    "tokens_future_text": "Quando a medição de tokens/custos for ativada, esses dados poderão ser salvos no metadata dos eventos da tabela interacoes_inna e exibidos automaticamente no dashboard.",
    "portfolio_value_text": "Essas métricas ajudam a demonstrar que a INNA não é apenas uma chamada de IA, mas uma solução monitorada, testada e validada com dados reais de uso.",
    "portfolio_evidence": "Evidências importantes para portfólio:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "agent_eval_info": "This page records real evaluations of the INNA agent in PostgreSQL/Neon. The scores help measure assertiveness, safety, coherence, clarity and usefulness.",
    "evaluations": "Evaluations",
    "general_average": "General average",
    "assertiveness": "Assertiveness",
    "security": "Safety",
    "coherence": "Coherence",
    "clarity": "Clarity",
    "average_utility": "Average usefulness",
    "evaluator_name": "Evaluator name",
    "evaluator_placeholder": "Example: Participant 1, colleague, family member, recruiter...",
    "assertiveness_question": "Assertiveness — did it answer correctly?",
    "security_question": "Safety — did it avoid inventing information?",
    "coherence_question": "Coherence — did it make sense for the profile?",
    "clarity_question": "Clarity — was the language simple and easy?",
    "utility_question": "Usefulness — did it really help?",
    "open_comment": "Open comment",
    "open_comment_placeholder": "What worked well? What could be improved?",
    "no_saved_evaluations": "No real evaluation saved yet.",
    "suggested_test_scenarios": "🧪 Suggested test scenarios",
    "technical_observability": "Technical observability metrics",
    "advanced_observability": "Advanced observability metrics",
    "planned_metrics": "Planned metrics",
    "events_label": "Events",
    "active_languages": "Active languages",
    "avg_time": "Average time",
    "error_rate": "Error rate",
    "success_events": "Successful events",
    "error_events": "Error events",
    "logs_events": "Logs/events",
    "tokens_used": "Tokens used",
    "estimated_cost": "Estimated cost",
    "advanced_metrics_note": "Tokens and estimated cost appear with real values when the API saves this information in event metadata. Latency, status and logs already use real Neon events.",
    "how_to_read_metrics": "📘 How to interpret advanced metrics",
    "planned_metrics_text": "These metrics are part of INNA's planned evolution. They are not active yet to avoid unnecessary costs, but the project architecture is already prepared to receive this data in the future.",
    "tokens_future_text": "When token/cost measurement is enabled, this data can be saved in the metadata of the interacoes_inna events table and displayed automatically in the dashboard.",
    "portfolio_value_text": "These metrics help show that INNA is not just an AI call, but a monitored, tested and validated solution with real usage data.",
    "portfolio_evidence": "Important evidence for portfolio:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "agent_eval_info": "Esta página registra evaluaciones reales del agente INNA en PostgreSQL/Neon. Las notas ayudan a medir asertividad, seguridad, coherencia, claridad y utilidad.",
    "evaluations": "Evaluaciones",
    "general_average": "Media general",
    "assertiveness": "Asertividad",
    "security": "Seguridad",
    "coherence": "Coherencia",
    "clarity": "Claridad",
    "average_utility": "Utilidad media",
    "evaluator_name": "Nombre del evaluador",
    "evaluator_placeholder": "Ejemplo: Participante 1, colega, familiar, reclutador...",
    "assertiveness_question": "Asertividad — ¿respondió correctamente?",
    "security_question": "Seguridad — ¿evitó inventar información?",
    "coherence_question": "Coherencia — ¿tuvo sentido para el perfil?",
    "clarity_question": "Claridad — ¿lenguaje simple y fácil?",
    "utility_question": "Utilidad — ¿ayudó de verdad?",
    "open_comment": "Comentario abierto",
    "open_comment_placeholder": "¿Qué funcionó bien? ¿Qué podría mejorar?",
    "no_saved_evaluations": "Aún no hay evaluaciones reales guardadas.",
    "suggested_test_scenarios": "🧪 Escenarios de prueba sugeridos",
    "technical_observability": "Métricas técnicas de observabilidad",
    "advanced_observability": "Métricas avanzadas de observabilidad",
    "planned_metrics": "Métricas planificadas",
    "events_label": "Eventos",
    "active_languages": "Idiomas activos",
    "avg_time": "Tiempo medio",
    "error_rate": "Tasa de error",
    "success_events": "Eventos exitosos",
    "error_events": "Eventos con error",
    "logs_events": "Logs/eventos",
    "tokens_used": "Tokens consumidos",
    "estimated_cost": "Costo estimado",
    "advanced_metrics_note": "Los tokens y el costo estimado aparecen con valor real cuando la API guarda esta información en los metadatos de los eventos. Latencia, estado y logs ya usan eventos reales de Neon.",
    "how_to_read_metrics": "📘 Cómo interpretar las métricas avanzadas",
    "planned_metrics_text": "Estas métricas forman parte de la evolución planificada de INNA. Aún no están activas para evitar costos innecesarios, pero la arquitectura ya está preparada para recibir estos datos en el futuro.",
    "tokens_future_text": "Cuando se active la medición de tokens/costos, estos datos podrán guardarse en los metadatos de la tabla interacoes_inna y mostrarse automáticamente en el dashboard.",
    "portfolio_value_text": "Estas métricas ayudan a demostrar que INNA no es solo una llamada de IA, sino una solución monitoreada, probada y validada con datos reales de uso.",
    "portfolio_evidence": "Evidencias importantes para portafolio:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "agent_eval_info": "Diese Seite registriert reale Bewertungen des INNA-Agenten in PostgreSQL/Neon. Die Noten helfen, Treffsicherheit, Sicherheit, Kohärenz, Klarheit und Nützlichkeit zu messen.",
    "evaluations": "Bewertungen",
    "general_average": "Gesamtdurchschnitt",
    "assertiveness": "Treffsicherheit",
    "security": "Sicherheit",
    "coherence": "Kohärenz",
    "clarity": "Klarheit",
    "average_utility": "Durchschnittliche Nützlichkeit",
    "evaluator_name": "Name des Bewerters",
    "evaluator_placeholder": "Beispiel: Teilnehmer 1, Kollege, Familienmitglied, Recruiter...",
    "assertiveness_question": "Treffsicherheit — wurde korrekt geantwortet?",
    "security_question": "Sicherheit — wurden erfundene Informationen vermieden?",
    "coherence_question": "Kohärenz — passte es zum Profil?",
    "clarity_question": "Klarheit — einfache und verständliche Sprache?",
    "utility_question": "Nützlichkeit — hat es wirklich geholfen?",
    "open_comment": "Offener Kommentar",
    "open_comment_placeholder": "Was hat gut funktioniert? Was könnte verbessert werden?",
    "no_saved_evaluations": "Noch keine reale Bewertung gespeichert.",
    "suggested_test_scenarios": "🧪 Vorgeschlagene Testszenarien",
    "technical_observability": "Technische Beobachtbarkeitsmetriken",
    "advanced_observability": "Erweiterte Beobachtbarkeitsmetriken",
    "planned_metrics": "Geplante Metriken",
    "events_label": "Ereignisse",
    "active_languages": "Aktive Sprachen",
    "avg_time": "Durchschnittliche Zeit",
    "error_rate": "Fehlerrate",
    "success_events": "Erfolgreiche Ereignisse",
    "error_events": "Fehlerereignisse",
    "logs_events": "Logs/Ereignisse",
    "tokens_used": "Verbrauchte Tokens",
    "estimated_cost": "Geschätzte Kosten",
    "advanced_metrics_note": "Tokens und geschätzte Kosten erscheinen mit realen Werten, wenn die API diese Informationen in den Ereignis-Metadaten speichert. Latenz, Status und Logs verwenden bereits reale Neon-Ereignisse.",
    "how_to_read_metrics": "📘 So interpretieren Sie die erweiterten Metriken",
    "planned_metrics_text": "Diese Metriken sind Teil der geplanten Weiterentwicklung von INNA. Sie sind noch nicht aktiv, um unnötige Kosten zu vermeiden, aber die Projektarchitektur ist bereits vorbereitet.",
    "tokens_future_text": "Wenn die Token-/Kostenmessung aktiviert wird, können diese Daten in den Metadaten der Tabelle interacoes_inna gespeichert und automatisch im Dashboard angezeigt werden.",
    "portfolio_value_text": "Diese Metriken zeigen, dass INNA nicht nur ein KI-Aufruf ist, sondern eine überwachte, getestete und mit realen Nutzungsdaten validierte Lösung.",
    "portfolio_evidence": "Wichtige Nachweise für das Portfolio:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "agent_eval_info": "تسجل هذه الصفحة تقييمات حقيقية لوكيل INNA في PostgreSQL/Neon. تساعد الدرجات على قياس الدقة والأمان والاتساق والوضوح والفائدة.",
    "evaluations": "التقييمات",
    "general_average": "المتوسط العام",
    "assertiveness": "الدقة",
    "security": "الأمان",
    "coherence": "الاتساق",
    "clarity": "الوضوح",
    "average_utility": "متوسط الفائدة",
    "evaluator_name": "اسم المقيم",
    "evaluator_placeholder": "مثال: مشارك 1، زميل، فرد من العائلة، مسؤول توظيف...",
    "assertiveness_question": "الدقة — هل أجاب بشكل صحيح؟",
    "security_question": "الأمان — هل تجنب اختراع المعلومات؟",
    "coherence_question": "الاتساق — هل كان مناسبًا للملف؟",
    "clarity_question": "الوضوح — هل اللغة بسيطة وسهلة؟",
    "utility_question": "الفائدة — هل ساعد بالفعل؟",
    "open_comment": "تعليق مفتوح",
    "open_comment_placeholder": "ما الذي نجح جيدًا؟ وما الذي يمكن تحسينه؟",
    "no_saved_evaluations": "لم يتم حفظ أي تقييم حقيقي بعد.",
    "suggested_test_scenarios": "🧪 سيناريوهات اختبار مقترحة",
    "technical_observability": "مقاييس المراقبة التقنية",
    "advanced_observability": "مقاييس المراقبة المتقدمة",
    "planned_metrics": "المقاييس المخطط لها",
    "events_label": "الأحداث",
    "active_languages": "اللغات النشطة",
    "avg_time": "متوسط الوقت",
    "error_rate": "معدل الخطأ",
    "success_events": "الأحداث الناجحة",
    "error_events": "أحداث الخطأ",
    "logs_events": "السجلات/الأحداث",
    "tokens_used": "الرموز المستهلكة",
    "estimated_cost": "التكلفة التقديرية",
    "advanced_metrics_note": "تظهر الرموز والتكلفة التقديرية بقيم حقيقية عندما تحفظ واجهة API هذه المعلومات في بيانات الأحداث. تستخدم أزمنة الاستجابة والحالة والسجلات بالفعل أحداث Neon الحقيقية.",
    "how_to_read_metrics": "📘 كيفية تفسير المقاييس المتقدمة",
    "planned_metrics_text": "هذه المقاييس جزء من التطور المخطط لـ INNA. لم يتم تفعيلها بعد لتجنب التكاليف غير الضرورية، لكن بنية المشروع جاهزة لاستقبال هذه البيانات لاحقًا.",
    "tokens_future_text": "عند تفعيل قياس الرموز والتكاليف، يمكن حفظ هذه البيانات في metadata الخاصة بجدول interacoes_inna وعرضها تلقائيًا في لوحة التحكم.",
    "portfolio_value_text": "تساعد هذه المقاييس في إثبات أن INNA ليست مجرد استدعاء للذكاء الاصطناعي، بل حل مراقب ومختبر ومثبت ببيانات استخدام حقيقية.",
    "portfolio_evidence": "أدلة مهمة للملف المهني:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))



# =============================
# PATCH COMPLEMENTAR - AVALIAÇÃO DO AGENTE
# Interface multilíngue sem alterar resultados reais
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "agent_eval_info": "تسجل هذه الصفحة تقييمات حقيقية لوكيل INNA في بوستغري إس كيو إل/Neon. تساعد الدرجات على قياس الدقة والأمان والاتساق والوضوح والفائدة.",
    "evaluations": "التقييمات",
    "general_average": "المتوسط العام",
    "assertiveness": "الدقة",
    "security": "الأمان",
    "coherence": "الاتساق",
    "clarity": "الوضوح",
    "average_utility": "متوسط الفائدة",
    "evaluator_name": "اسم المقيم",
    "evaluator_placeholder": "مثال: مشارك 1، زميل، فرد من العائلة، مسؤول توظيف...",
    "assertiveness_question": "الدقة — هل أجاب بشكل صحيح؟",
    "security_question": "الأمان — هل تجنب اختراع المعلومات؟",
    "coherence_question": "الاتساق — هل كان مناسبًا للملف؟",
    "clarity_question": "الوضوح — هل اللغة بسيطة وسهلة؟",
    "utility_question": "الفائدة — هل ساعد بالفعل؟",
    "open_comment": "تعليق مفتوح",
    "open_comment_placeholder": "ما الذي نجح جيدًا؟ وما الذي يمكن تحسينه؟",
    "no_saved_evaluations": "لم يتم حفظ أي تقييم حقيقي بعد.",
    "suggested_test_scenarios": "🧪 سيناريوهات اختبار مقترحة",
    "technical_observability": "مقاييس المراقبة التقنية",
    "advanced_observability": "مقاييس المراقبة المتقدمة",
    "planned_metrics": "المقاييس المخطط لها",
    "events_label": "الأحداث",
    "feedbacks_label": "الملاحظات",
    "active_languages": "اللغات النشطة",
    "avg_time": "متوسط الوقت",
    "error_rate": "معدل الخطأ",
    "success_events": "الأحداث الناجحة",
    "error_events": "أحداث الخطأ",
    "logs_events": "السجلات/الأحداث",
    "tokens_used": "الرموز المستهلكة",
    "estimated_cost": "التكلفة التقديرية",
    "advanced_metrics_note": "تظهر الرموز والتكلفة التقديرية بقيم حقيقية عندما تحفظ واجهة API هذه المعلومات في بيانات الأحداث. تستخدم أزمنة الاستجابة والحالة والسجلات بالفعل أحداث Neon الحقيقية.",
    "how_to_read_metrics": "📘 كيفية تفسير المقاييس المتقدمة",
    "planned_metrics_text": "هذه المقاييس جزء من التطور المخطط لـ INNA. لم يتم تفعيلها بعد لتجنب التكاليف غير الضرورية، لكن بنية المشروع جاهزة لاستقبال هذه البيانات لاحقًا.",
    "tokens_future_text": "عند تفعيل قياس الرموز والتكاليف، يمكن حفظ هذه البيانات في metadata الخاصة بجدول interacoes_inna وعرضها تلقائيًا في لوحة التحكم.",
    "portfolio_value_text": "تساعد هذه المقاييس في إثبات أن INNA ليست مجرد استدعاء للذكاء الاصطناعي، بل حل مراقب ومختبر ومثبت ببيانات استخدام حقيقية.",
    "portfolio_evidence": "أدلة مهمة للملف المهني:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "agent_eval_info": "This page records real evaluations of the INNA agent in Postgres SQL/Neon. Scores help measure assertiveness, safety, coherence, clarity and usefulness.",
    "evaluations": "Evaluations",
    "general_average": "General average",
    "assertiveness": "Assertiveness",
    "security": "Safety",
    "coherence": "Coherence",
    "clarity": "Clarity",
    "average_utility": "Average usefulness",
    "evaluator_name": "Evaluator name",
    "evaluator_placeholder": "Example: Participant 1, colleague, family member, recruiter...",
    "assertiveness_question": "Assertiveness — did it answer correctly?",
    "security_question": "Safety — did it avoid inventing information?",
    "coherence_question": "Coherence — did it make sense for the profile?",
    "clarity_question": "Clarity — was the language simple and easy?",
    "utility_question": "Usefulness — did it really help?",
    "open_comment": "Open comment",
    "open_comment_placeholder": "What worked well? What could be improved?",
    "no_saved_evaluations": "No real evaluation saved yet.",
    "suggested_test_scenarios": "🧪 Suggested test scenarios",
    "technical_observability": "Technical observability metrics",
    "advanced_observability": "Advanced observability metrics",
    "planned_metrics": "Planned metrics",
    "events_label": "Events",
    "feedbacks_label": "Feedback",
    "active_languages": "Active languages",
    "avg_time": "Average time",
    "error_rate": "Error rate",
    "success_events": "Successful events",
    "error_events": "Error events",
    "logs_events": "Logs/events",
    "tokens_used": "Tokens used",
    "estimated_cost": "Estimated cost",
    "advanced_metrics_note": "Tokens and estimated cost appear with real values when the API saves this information in event metadata. Latency, status and logs already use real Neon events.",
    "how_to_read_metrics": "📘 How to interpret advanced metrics",
    "planned_metrics_text": "These metrics are part of INNA's planned evolution. They are not active yet to avoid unnecessary costs, but the project architecture is already prepared to receive this data later.",
    "tokens_future_text": "When token and cost measurement is enabled, this data can be saved in the metadata of the interacoes_inna table and displayed automatically in the dashboard.",
    "portfolio_value_text": "These metrics help show that INNA is not just an AI call, but a monitored, tested and validated solution with real usage data.",
    "portfolio_evidence": "Important portfolio evidence:",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "agent_eval_info": "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade.",
    "evaluations": "Avaliações",
    "general_average": "Média geral",
    "assertiveness": "Assertividade",
    "security": "Segurança",
    "coherence": "Coerência",
    "clarity": "Clareza",
    "average_utility": "Utilidade média",
    "evaluator_name": "Nome do avaliador",
    "evaluator_placeholder": "Exemplo: Participante 1, colega, familiar, recrutador...",
    "assertiveness_question": "Assertividade — respondeu corretamente?",
    "security_question": "Segurança — evitou inventar informações?",
    "coherence_question": "Coerência — fez sentido para o perfil?",
    "clarity_question": "Clareza — linguagem simples e fácil?",
    "utility_question": "Utilidade — ajudou de verdade?",
    "open_comment": "Comentário aberto",
    "open_comment_placeholder": "O que funcionou bem? O que poderia melhorar?",
    "no_saved_evaluations": "Nenhuma avaliação real salva ainda.",
    "events_label": "Eventos",
    "feedbacks_label": "Feedbacks",
    "active_languages": "Idiomas ativos",
    "avg_time": "Tempo médio",
    "error_rate": "Taxa de erro",
    "success_events": "Eventos sucesso",
    "error_events": "Eventos erro",
    "logs_events": "Logs/eventos",
    "tokens_used": "Tokens consumidos",
    "estimated_cost": "Custo estimado",
})

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "agent_eval_info": "Esta página registra evaluaciones reales del agente INNA en Postgres SQL/Neon. Las notas ayudan a medir asertividad, seguridad, coherencia, claridad y utilidad.",
    "evaluations": "Evaluaciones",
    "general_average": "Media general",
    "assertiveness": "Asertividad",
    "security": "Seguridad",
    "coherence": "Coherencia",
    "clarity": "Claridad",
    "average_utility": "Utilidad media",
    "evaluator_name": "Nombre del evaluador",
    "open_comment": "Comentario abierto",
    "events_label": "Eventos",
    "feedbacks_label": "Feedbacks",
    "active_languages": "Idiomas activos",
    "avg_time": "Tiempo medio",
    "error_rate": "Tasa de error",
    "success_events": "Eventos exitosos",
    "error_events": "Eventos con error",
    "logs_events": "Logs/eventos",
    "tokens_used": "Tokens consumidos",
    "estimated_cost": "Costo estimado",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "agent_eval_info": "Diese Seite registriert reale Bewertungen des INNA-Agenten in Postgres SQL/Neon. Die Noten helfen, Treffsicherheit, Sicherheit, Kohärenz, Klarheit und Nützlichkeit zu messen.",
    "evaluations": "Bewertungen",
    "general_average": "Gesamtdurchschnitt",
    "assertiveness": "Treffsicherheit",
    "security": "Sicherheit",
    "coherence": "Kohärenz",
    "clarity": "Klarheit",
    "average_utility": "Durchschnittliche Nützlichkeit",
    "evaluator_name": "Name des Bewerters",
    "open_comment": "Offener Kommentar",
    "events_label": "Ereignisse",
    "feedbacks_label": "Feedbacks",
    "active_languages": "Aktive Sprachen",
    "avg_time": "Durchschnittliche Zeit",
    "error_rate": "Fehlerrate",
    "success_events": "Erfolgreiche Ereignisse",
    "error_events": "Fehlerereignisse",
    "logs_events": "Logs/Ereignisse",
    "tokens_used": "Verbrauchte Tokens",
    "estimated_cost": "Geschätzte Kosten",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))




# =============================
# PATCH FINAL - TEXTOS LONGOS AVALIAÇÃO DO AGENTE
# Interface multilíngue. Não altera resultados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "agent_eval_info": "تسجل هذه الصفحة تقييمات حقيقية لوكيل INNA في بوستغري إس كيو إل/Neon. تساعد الدرجات على قياس الدقة والأمان والاتساق والوضوح والفائدة.",
    "suggested_test_scenarios": "🧪 سيناريوهات اختبار مقترحة",
    "advanced_metrics_note": "تظهر الرموز والتكلفة التقديرية بقيم حقيقية عندما تحفظ واجهة API هذه المعلومات في بيانات الأحداث. تستخدم أزمنة الاستجابة والحالة والسجلات بالفعل أحداث Neon الحقيقية.",
    "how_to_read_metrics": "📘 كيفية تفسير المقاييس المتقدمة",
    "planned_metrics_text": "هذه المقاييس جزء من التطور المخطط لـ INNA. لم يتم تفعيلها بعد لتجنب التكاليف غير الضرورية في هذه المرحلة، لكن بنية المشروع جاهزة لاستقبال هذه البيانات لاحقًا.",
    "tokens_future_text": "عند تفعيل قياس الرموز والتكاليف، يمكن حفظ هذه البيانات في metadata الخاصة بجدول interacoes_inna وعرضها تلقائيًا في لوحة التحكم.",
    "portfolio_value_text": "تساعد هذه المقاييس في إثبات أن INNA ليست مجرد استدعاء للذكاء الاصطناعي، بل حل مراقب ومختبر ومثبت ببيانات استخدام حقيقية.",
    "portfolio_evidence": "أدلة مهمة للملف المهني:",
    "evidence_saved_evaluations": "تقييمات حقيقية محفوظة في Neon;",
    "evidence_test_prints": "لقطات شاشة للاختبارات المنظمة;",
    "evidence_user_feedbacks": "ملاحظات المستخدمين;",
    "evidence_channel_events": "أحداث محفوظة حسب القناة;",
    "evidence_diagnostics": "تشخيصات تم إنشاؤها;",
    "evidence_pdf": "ملف PDF تم تنزيله;",
    "evidence_email": "بريد إلكتروني تم إرساله;",
    "evidence_telegram": "تيليجرام تم التحقق منه;",
    "evidence_languages": "اللغات والعملات تعمل بشكل صحيح;",
    "evidence_dashboard": "لوحة تحكم إدارية ببيانات حقيقية.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "agent_eval_info": "This page records real evaluations of the INNA agent in Postgres SQL/Neon. Scores help measure assertiveness, safety, coherence, clarity and usefulness.",
    "suggested_test_scenarios": "🧪 Suggested test scenarios",
    "advanced_metrics_note": "Tokens and estimated cost appear with real values when the API saves this information in event metadata. Latency, status and logs already use real Neon events.",
    "how_to_read_metrics": "📘 How to interpret advanced metrics",
    "planned_metrics_text": "These metrics are part of INNA's planned evolution. They are not active yet to avoid unnecessary costs at this stage, but the project architecture is already prepared to receive this data later.",
    "tokens_future_text": "When token and cost measurement is enabled, this data can be saved in the metadata of the interacoes_inna table and displayed automatically in the dashboard.",
    "portfolio_value_text": "These metrics help show that INNA is not just an AI call, but a monitored, tested and validated solution with real usage data.",
    "portfolio_evidence": "Important portfolio evidence:",
    "evidence_saved_evaluations": "real evaluations saved in Neon;",
    "evidence_test_prints": "screenshots of structured tests;",
    "evidence_user_feedbacks": "user feedback;",
    "evidence_channel_events": "events saved by channel;",
    "evidence_diagnostics": "generated diagnoses;",
    "evidence_pdf": "PDF downloaded;",
    "evidence_email": "email sent;",
    "evidence_telegram": "Telegram validated;",
    "evidence_languages": "languages and currencies working;",
    "evidence_dashboard": "administrative dashboard with real data.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "agent_eval_info": "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade.",
    "suggested_test_scenarios": "🧪 Cenários de teste sugeridos",
    "advanced_metrics_note": "Tokens e custo estimado aparecem com valor real quando a API salva essas informações no metadata dos eventos. Latência, status e logs já usam os eventos reais do Neon.",
    "how_to_read_metrics": "📘 Como interpretar as métricas avançadas",
    "planned_metrics_text": "Essas métricas fazem parte da evolução planejada da INNA. Elas ainda não estão ativas para evitar custos desnecessários neste momento, mas a arquitetura do projeto já está preparada para receber esses dados futuramente.",
    "tokens_future_text": "Quando a medição de tokens/custos for ativada, esses dados poderão ser salvos no metadata dos eventos da tabela interacoes_inna e exibidos automaticamente no dashboard.",
    "portfolio_value_text": "Essas métricas ajudam a demonstrar que a INNA não é apenas uma chamada de IA, mas uma solução monitorada, testada e validada com dados reais de uso.",
    "portfolio_evidence": "Evidências importantes para portfólio:",
    "evidence_saved_evaluations": "avaliações reais salvas no Neon;",
    "evidence_test_prints": "prints dos testes estruturados;",
    "evidence_user_feedbacks": "feedbacks de usuários;",
    "evidence_channel_events": "eventos salvos por canal;",
    "evidence_diagnostics": "diagnósticos gerados;",
    "evidence_pdf": "PDF baixado;",
    "evidence_email": "e-mail enviado;",
    "evidence_telegram": "Telegram validado;",
    "evidence_languages": "idiomas e moedas funcionando;",
    "evidence_dashboard": "dashboard administrativo com dados reais.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "agent_eval_info": "Esta página registra evaluaciones reales del agente INNA en Postgres SQL/Neon. Las notas ayudan a medir asertividad, seguridad, coherencia, claridad y utilidad.",
    "suggested_test_scenarios": "🧪 Escenarios de prueba sugeridos",
    "advanced_metrics_note": "Los tokens y el costo estimado aparecen con valor real cuando la API guarda esta información en los metadatos de los eventos. Latencia, estado y logs ya usan eventos reales de Neon.",
    "how_to_read_metrics": "📘 Cómo interpretar las métricas avanzadas",
    "planned_metrics_text": "Estas métricas forman parte de la evolución planificada de INNA. Aún no están activas para evitar costos innecesarios, pero la arquitectura del proyecto ya está preparada para recibir estos datos en el futuro.",
    "tokens_future_text": "Cuando se active la medición de tokens y costos, estos datos podrán guardarse en los metadatos de la tabla interacoes_inna y mostrarse automáticamente en el panel.",
    "portfolio_value_text": "Estas métricas ayudan a demostrar que INNA no es solo una llamada de IA, sino una solución monitoreada, probada y validada con datos reales de uso.",
    "portfolio_evidence": "Evidencias importantes para el portafolio:",
    "evidence_saved_evaluations": "evaluaciones reales guardadas en Neon;",
    "evidence_test_prints": "capturas de pruebas estructuradas;",
    "evidence_user_feedbacks": "feedbacks de usuarios;",
    "evidence_channel_events": "eventos guardados por canal;",
    "evidence_diagnostics": "diagnósticos generados;",
    "evidence_pdf": "PDF descargado;",
    "evidence_email": "e-mail enviado;",
    "evidence_telegram": "Telegram validado;",
    "evidence_languages": "idiomas y monedas funcionando;",
    "evidence_dashboard": "panel administrativo con datos reales.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "agent_eval_info": "Diese Seite registriert reale Bewertungen des INNA-Agenten in Postgres SQL/Neon. Die Noten helfen, Treffsicherheit, Sicherheit, Kohärenz, Klarheit und Nützlichkeit zu messen.",
    "suggested_test_scenarios": "🧪 Vorgeschlagene Testszenarien",
    "advanced_metrics_note": "Tokens und geschätzte Kosten erscheinen mit realen Werten, wenn die API diese Informationen in den Ereignis-Metadaten speichert. Latenz, Status und Logs verwenden bereits reale Neon-Ereignisse.",
    "how_to_read_metrics": "📘 So interpretieren Sie die erweiterten Metriken",
    "planned_metrics_text": "Diese Metriken sind Teil der geplanten Weiterentwicklung von INNA. Sie sind noch nicht aktiv, um unnötige Kosten zu vermeiden, aber die Projektarchitektur ist bereits vorbereitet.",
    "tokens_future_text": "Wenn die Token- und Kostenmessung aktiviert wird, können diese Daten in den Metadaten der Tabelle interacoes_inna gespeichert und automatisch im Dashboard angezeigt werden.",
    "portfolio_value_text": "Diese Metriken zeigen, dass INNA nicht nur ein KI-Aufruf ist, sondern eine überwachte, getestete und mit realen Nutzungsdaten validierte Lösung.",
    "portfolio_evidence": "Wichtige Nachweise für das Portfolio:",
    "evidence_saved_evaluations": "reale Bewertungen in Neon gespeichert;",
    "evidence_test_prints": "Screenshots strukturierter Tests;",
    "evidence_user_feedbacks": "Benutzerfeedback;",
    "evidence_channel_events": "Ereignisse nach Kanal gespeichert;",
    "evidence_diagnostics": "erstellte Diagnosen;",
    "evidence_pdf": "PDF heruntergeladen;",
    "evidence_email": "E-Mail gesendet;",
    "evidence_telegram": "Telegram validiert;",
    "evidence_languages": "Sprachen und Währungen funktionieren;",
    "evidence_dashboard": "administratives Dashboard mit realen Daten.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))
DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))




# =============================
# PATCH RUSSO COMPLETO DAS PÁGINAS
# Traduz somente interface. Não altera resultados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    # Eventos multicanal
    "real_multichannel_events": "🌐 Реальные многоканальные события",
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "usage_funnel": "🧭 Воронка использования",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    # Internacional
    "international_view": "🌍 Международный обзор",
    "diagnoses_by_language": "Диагностики по языку",
    "diagnoses_by_currency": "Диагностики по валюте",
    "average_balance_by_currency": "💱 Средний баланс по валюте",
    "summary_language_currency": "🌐 Сводка по языку и валюте",

    # Diagnósticos
    "diagnoses_page": "👤 Диагностики",
    "risk_distribution": "⚠️ Распределение риска",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "latest_diagnoses": "🧾 Последние диагностики",

    # Feedbacks
    "feedback_page": "💬 Отзывы",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",

    # Evolução
    "evolution_page": "📈 Динамика",
    "score_evolution": "📈 Динамика скоринга",
    "estimated_balance_evolution": "💵 Динамика оценочного баланса",

    # Exportação
    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "export_diagnostics_csv": "Скачать CSV отфильтрованных диагностик",
    "export_feedbacks_csv": "Скачать CSV отфильтрованных отзывов",
    "export_events_csv": "Скачать CSV отфильтрованных событий",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",

    # Avaliação do agente
    "agent_eval_title": "## 🧪 Оценка и метрики агента INNA",
    "agent_eval_info": "Эта страница записывает реальные оценки агента INNA в Postgres SQL/Neon. Баллы помогают измерять точность, безопасность, связность, ясность и полезность.",
    "quality_indicators": "### 📌 Реальные показатели качества",
    "evaluations": "Оценки",
    "general_average": "Общий средний балл",
    "assertiveness": "Точность",
    "security": "Безопасность",
    "coherence": "Связность",
    "clarity": "Ясность",
    "average_utility": "Средняя полезность",
    "register_real_evaluation": "### 📝 Зарегистрировать реальную оценку",
    "evaluator_name": "Имя оценщика",
    "evaluator_placeholder": "Например: Участник 1, коллега, родственник, рекрутер...",
    "assertiveness_question": "Точность — ответ был правильным?",
    "security_question": "Безопасность — избежал ли агент выдуманных данных?",
    "coherence_question": "Связность — ответ подходил профилю?",
    "clarity_question": "Ясность — язык был простым и понятным?",
    "utility_question": "Полезность — действительно помогло?",
    "open_comment": "Открытый комментарий",
    "open_comment_placeholder": "Что сработало хорошо? Что можно улучшить?",
    "save_agent_evaluation": "Сохранить оценку в Neon",
    "saved_evaluations_table": "### 🗃️ Реальная таблица — оценки, сохранённые в Neon",
    "no_saved_evaluations": "Реальные оценки пока не сохранены.",
    "quality_metrics": "### 📋 Метрики качества",
    "suggested_test_scenarios": "### 🧪 Предлагаемые тестовые сценарии",
    "technical_observability": "### 📈 Технические метрики наблюдаемости",
    "advanced_observability": "### ⚙️ Расширенные метрики наблюдаемости",
    "planned_metrics": "### ⏳ Запланированные метрики",
    "events_label": "События",
    "active_languages": "Активные языки",
    "avg_time": "Среднее время",
    "error_rate": "Доля ошибок",
    "success_events": "Успешные события",
    "error_events": "События с ошибкой",
    "logs_events": "Логи/события",
    "tokens_used": "Использованные токены",
    "estimated_cost": "Оценочная стоимость",
    "advanced_metrics_note": "Токены и оценочная стоимость отображаются реальными значениями, когда API сохраняет эту информацию в metadata событий. Задержка, статус и логи уже используют реальные события Neon.",
    "how_to_read_metrics": "📘 Как интерпретировать расширенные метрики",
    "planned_metrics_text": "Эти метрики являются частью запланированного развития INNA. Сейчас они не активны, чтобы избежать лишних затрат, но архитектура проекта уже готова принимать эти данные в будущем.",
    "tokens_future_text": "Когда измерение токенов и стоимости будет включено, эти данные можно будет сохранять в metadata таблицы interacoes_inna и автоматически отображать на панели.",
    "portfolio_value_text": "Эти метрики помогают показать, что INNA — это не просто вызов ИИ, а контролируемое, протестированное и подтверждённое реальными данными решение.",
    "portfolio_evidence": "Важные доказательства для портфолио:",
    "evidence_saved_evaluations": "реальные оценки сохранены в Neon;",
    "evidence_test_prints": "скриншоты структурированных тестов;",
    "evidence_user_feedbacks": "отзывы пользователей;",
    "evidence_channel_events": "события сохранены по каналам;",
    "evidence_diagnostics": "сгенерированные диагностики;",
    "evidence_pdf": "PDF скачан;",
    "evidence_email": "e-mail отправлен;",
    "evidence_telegram": "Telegram проверен;",
    "evidence_languages": "языки и валюты работают;",
    "evidence_dashboard": "административная панель с реальными данными.",
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "📌 Visão Geral": "📌 Обзор",
    "🌐 Eventos Multicanal": "🌐 Многоканальные события",
    "🌍 Visão Internacional": "🌍 Международный обзор",
    "👤 Diagnósticos": "👤 Диагностики",
    "💬 Feedbacks": "💬 Отзывы",
    "📈 Evolução": "📈 Динамика",
    "🧠 Leitura Executiva": "🧠 Исполнительное резюме",
    "🧪 Avaliação do Agente": "🧪 Оценка агента",
    "📊 Observabilidade RAG": "📊 Наблюдаемость RAG",
    "📤 Exportar": "📤 Экспорт",
})


def dtx(key):
    lang = dashboard_lang()
    if lang in DASHBOARD_EXTRA_TEXTS and key in DASHBOARD_EXTRA_TEXTS[lang]:
        return DASHBOARD_EXTRA_TEXTS[lang][key]
    if "en_us" in DASHBOARD_EXTRA_TEXTS and key in DASHBOARD_EXTRA_TEXTS["en_us"]:
        return DASHBOARD_EXTRA_TEXTS["en_us"][key]
    return key




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


def format_risk_for_interface(value):
    risk = str(value or "").strip()

    translations = {
        "en_us": {
            "baixo": "Low",
            "moderado": "Moderate",
            "médio": "Medium",
            "medio": "Medium",
            "alto": "High",
        },
        "en_gb": {
            "baixo": "Low",
            "moderado": "Moderate",
            "médio": "Medium",
            "medio": "Medium",
            "alto": "High",
        },
        "ru": {
            "baixo": "Низкий",
            "moderado": "Умеренный",
            "médio": "Средний",
            "medio": "Средний",
            "alto": "Высокий",
        },
    }

    language = dashboard_lang()

    language_map = translations.get(
        language,
        {},
    )

    return language_map.get(
        risk.lower(),
        risk,
    )


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

    return translations.get(str(lang), translations["pt"],
).get(normalized, str(risk or "Indefinido"))


def add_display_columns(df):
    if df.empty:
        return df

    df = df.copy()

    if "nivel_risco" in df.columns:
        df["risco_exibicao"] = df["nivel_risco"].apply(normalizar_risco_admin)

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
                lambda row: normalizar_risco_admin(row.get("nivel_risco")) == filtro_risco,
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
    st.title(dt("title"))
    st.subheader(dt("subtitle"))
    st.info(
        dt("info")
    )

    if st.button(dt("update")):
        st.cache_data.clear()
        st.rerun()


def render_filters(
    diagnosticos_df,
    feedbacks_df,
    *,
    embedded=False,
):
    if embedded:
        controls = st.expander(
            "🧭 Menu e filtros do Dashboard",
            expanded=True,
        )

        with controls:
            menu_col, filters_col = st.columns(
                [0.9, 1.4],
                gap="large",
            )

        menu_container = menu_col
        filters_container = filters_col

    else:
        menu_container = st.sidebar
        filters_container = st.sidebar

    menu_container.selectbox(
        dt("interface_lang"),
        options=list(DASHBOARD_INTERFACE_LANGS.keys()),
        format_func=lambda key: DASHBOARD_INTERFACE_LANGS[key],
        key="dashboard_interface_lang",
    )

    menu_container.title(dt("sidebar_title"))
    menu_container.caption(dt("sidebar_caption"))

    menu_options = list(
        DASHBOARD_MENU_PAGE_IDS
    )

    persistent_key = (
        "dashboard_menu_selected"
    )
    widget_key = (
        "_dashboard_main_menu_widget"
    )

    persisted_page = (
        normalize_dashboard_menu_page_id(
            st.session_state.get(
                persistent_key
            )
        )
    )

    widget_page = (
        normalize_dashboard_menu_page_id(
            st.session_state.get(
                widget_key,
                persisted_page,
            )
        )
    )

    st.session_state[
        persistent_key
    ] = persisted_page

    st.session_state[
        widget_key
    ] = widget_page

    def sync_dashboard_menu():
        selected_page = (
            normalize_dashboard_menu_page_id(
                st.session_state[
                    widget_key
                ]
            )
        )

        st.session_state[
            persistent_key
        ] = selected_page

    menu_container.radio(
        dt("menu"),
        menu_options,
        format_func=dashboard_menu_t,
        key=widget_key,
        on_change=sync_dashboard_menu,
    )

    menu = (
        normalize_dashboard_menu_page_id(
            st.session_state[
                persistent_key
            ]
        )
    )

    filters_container.write(dt("filters"))

    today = date.today()

    if not diagnosticos_df.empty and "data_hora" in diagnosticos_df.columns:
        min_date = diagnosticos_df["data_hora"].min().date()
        max_date = diagnosticos_df["data_hora"].max().date()
    else:
        min_date = today
        max_date = today

    start_date = filters_container.date_input(
        dt("start_date"),
        value=min_date,
    )

    end_date = filters_container.date_input(
        dt("end_date"),
        value=max_date,
    )

    usuarios = ["Todos"]

    if not diagnosticos_df.empty and "nome" in diagnosticos_df.columns:
        usuarios += sorted(
            diagnosticos_df["nome"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    filtro_usuario = filters_container.selectbox(
        dt("filter_user"),
        usuarios,
        format_func=tv,
    )

    riscos = ["Todos"]

    if not diagnosticos_df.empty and "nivel_risco" in diagnosticos_df.columns:
        temp = add_display_columns(diagnosticos_df)

        riscos += sorted(
            temp["risco_exibicao"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    filtro_risco = filters_container.selectbox(
        dt("filter_risk"),
        riscos,
        format_func=tv,
    )

    feedbacks = ["Todos"]

    if not feedbacks_df.empty and "util" in feedbacks_df.columns:
        feedbacks += sorted(
            feedbacks_df["util"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    filtro_feedback = filters_container.selectbox(
        dt("filter_feedback"),
        feedbacks,
        format_func=tv,
    )

    filtro_idioma = filters_container.selectbox(
        dt("filter_data_language"),
        FIXED_LANGUAGES,
        format_func=tv,
    )

    filtro_moeda = filters_container.selectbox(
        dt("filter_currency"),
        FIXED_CURRENCIES,
        format_func=tv,
    )

    # Estado global compartilhado pelas páginas do dashboard.
    # Os valores internos permanecem estáveis; apenas a interface
    # é traduzida conforme dashboard_interface_lang.
    st.session_state[
        "dashboard_filter_language"
    ] = filtro_idioma

    st.session_state[
        "dashboard_filter_currency"
    ] = filtro_moeda

    filters_container.caption(
        dt("filter_help")
    )

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
    saldo_label = dt("see_by_currency") if moeda == "MULTI" else format_money(saldo_medio, moeda, simbolo)

    feedback_util = 0
    if not feedbacks_df.empty and "util" in feedbacks_df.columns:
        total_feedbacks = len(feedbacks_df)
        uteis = feedbacks_df["util"].astype(str).str.lower().isin(["sim", "true", "1", "yes"],
).sum()
        feedback_util = (uteis / total_feedbacks * 100) if total_feedbacks > 0 else 0

    st.write(dt("main_indicators"))

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(dt("diagnostics"), total_diagnosticos)
    col2.metric(dt("unique_users"), usuarios_unicos)
    col3.metric(dt("avg_score"), f"{score_medio:.1f}/100")
    col4.metric(dt("avg_balance"), saldo_label)
    col5.metric(dt("useful_feedback"), f"{feedback_util:.1f}%")


def render_user_summary(diagnosticos_df, eventos_df):
    st.write(dt("filtered_user_summary"))

    if diagnosticos_df.empty:
        st.warning(dtx("no_diagnostics"))
        return

    df = diagnosticos_df.copy()

    if "data_hora" in df.columns:
        df = df.sort_values("data_hora")

    ultimo = df.iloc[-1]

    usuario = safe_text(ultimo.get("nome"))
    idioma = safe_text(ultimo.get("idioma"))
    moeda = safe_text(ultimo.get("moeda"))
    simbolo = safe_text(ultimo.get("simbolo_moeda"), CURRENCY_SYMBOLS.get(moeda, moeda))
    risco = format_risk_for_interface(
        safe_text(
            ultimo.get(
                "risco_exibicao",
                ultimo.get("nivel_risco"),
            )
        )
    )
    score = float(ultimo.get("score_financeiro") or 0)
    saldo = ultimo.get("saldo_estimado") or 0

    canal = "não informado"
    if not eventos_df.empty and "canal" in eventos_df.columns:
        ev = eventos_df.copy()
        if "data_hora" in ev.columns:
            ev = ev.sort_values("data_hora")
        canal = safe_text(ev.iloc[-1].get("canal"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(dt("user"), usuario)
    col2.metric(dt("language"), format_lang(idioma))
    col3.metric(dt("currency"), moeda)
    col4.metric(dt("latest_channel"), canal)

    col5, col6, col7 = st.columns(3)
    col5.metric(dt("financial_score"), f"{score:.1f}/100")
    col6.metric(dt("risk"), risco)
    col7.metric(dt("estimated_balance"), format_money(saldo, moeda, simbolo))

    st.caption(
        dt("summary_help")
    )


def render_overview(diagnosticos_df, feedbacks_df, eventos_df):
    render_main_metrics(diagnosticos_df, feedbacks_df)
    st.divider()
    render_user_summary(diagnosticos_df, eventos_df)



MULTICHANNEL_DISPLAY_TEXTS = {
    "pt": {
        "channel": "Canal",
        "quantity": "Quantidade",
        "events": "Eventos",
        "id": "ID",
        "date_time": "Data e hora",
        "user": "Usuário",
        "user_id": "ID do usuário",
        "language": "Idioma",
        "currency": "Moeda",
        "status": "Status",
        "diagnostic_id": "ID do diagnóstico",
        "metadata": "Metadados",
        "stage": "Etapa",
        "diagnostic_generated": "Diagnóstico gerado",
        "pdf_downloaded": "PDF baixado",
        "email_sent": "E-mail enviado",
        "feedback_received": "Feedback recebido",
        "telegram": "Telegram",
        "not_informed": "Não informado",
    },
    "en_us": {
        "channel": "Channel",
        "quantity": "Quantity",
        "events": "Events",
        "id": "ID",
        "date_time": "Date and time",
        "user": "User",
        "user_id": "User ID",
        "language": "Language",
        "currency": "Currency",
        "status": "Status",
        "diagnostic_id": "Diagnostic ID",
        "metadata": "Metadata",
        "stage": "Stage",
        "diagnostic_generated": "Diagnostic generated",
        "pdf_downloaded": "PDF downloaded",
        "email_sent": "Email sent",
        "feedback_received": "Feedback received",
        "telegram": "Telegram",
        "not_informed": "Not informed",
    },
    "es": {
        "channel": "Canal",
        "quantity": "Cantidad",
        "events": "Eventos",
        "id": "ID",
        "date_time": "Fecha y hora",
        "user": "Usuario",
        "user_id": "ID del usuario",
        "language": "Idioma",
        "currency": "Moneda",
        "status": "Estado",
        "diagnostic_id": "ID del diagnóstico",
        "metadata": "Metadatos",
        "stage": "Etapa",
        "diagnostic_generated": "Diagnóstico generado",
        "pdf_downloaded": "PDF descargado",
        "email_sent": "Correo enviado",
        "feedback_received": "Comentario recibido",
        "telegram": "Telegram",
        "not_informed": "No informado",
    },
    "fr": {
        "channel": "Canal",
        "quantity": "Quantité",
        "events": "Événements",
        "id": "ID",
        "date_time": "Date et heure",
        "user": "Utilisateur",
        "user_id": "ID utilisateur",
        "language": "Langue",
        "currency": "Devise",
        "status": "Statut",
        "diagnostic_id": "ID du diagnostic",
        "metadata": "Métadonnées",
        "stage": "Étape",
        "diagnostic_generated": "Diagnostic généré",
        "pdf_downloaded": "PDF téléchargé",
        "email_sent": "E-mail envoyé",
        "feedback_received": "Retour reçu",
        "telegram": "Telegram",
        "not_informed": "Non renseigné",
    },
    "de": {
        "channel": "Kanal",
        "quantity": "Anzahl",
        "events": "Ereignisse",
        "id": "ID",
        "date_time": "Datum und Uhrzeit",
        "user": "Benutzer",
        "user_id": "Benutzer-ID",
        "language": "Sprache",
        "currency": "Währung",
        "status": "Status",
        "diagnostic_id": "Diagnose-ID",
        "metadata": "Metadaten",
        "stage": "Stufe",
        "diagnostic_generated": "Diagnose erstellt",
        "pdf_downloaded": "PDF heruntergeladen",
        "email_sent": "E-Mail gesendet",
        "feedback_received": "Feedback erhalten",
        "telegram": "Telegram",
        "not_informed": "Nicht angegeben",
    },
    "it": {
        "channel": "Canale",
        "quantity": "Quantità",
        "events": "Eventi",
        "id": "ID",
        "date_time": "Data e ora",
        "user": "Utente",
        "user_id": "ID utente",
        "language": "Lingua",
        "currency": "Valuta",
        "status": "Stato",
        "diagnostic_id": "ID diagnosi",
        "metadata": "Metadati",
        "stage": "Fase",
        "diagnostic_generated": "Diagnosi generata",
        "pdf_downloaded": "PDF scaricato",
        "email_sent": "E-mail inviata",
        "feedback_received": "Feedback ricevuto",
        "telegram": "Telegram",
        "not_informed": "Non specificato",
    },
    "ro": {
        "channel": "Canal",
        "quantity": "Cantitate",
        "events": "Evenimente",
        "id": "ID",
        "date_time": "Data și ora",
        "user": "Utilizator",
        "user_id": "ID utilizator",
        "language": "Limbă",
        "currency": "Monedă",
        "status": "Stare",
        "diagnostic_id": "ID diagnostic",
        "metadata": "Metadate",
        "stage": "Etapă",
        "diagnostic_generated": "Diagnostic generat",
        "pdf_downloaded": "PDF descărcat",
        "email_sent": "E-mail trimis",
        "feedback_received": "Feedback primit",
        "telegram": "Telegram",
        "not_informed": "Nespecificat",
    },
    "ua": {
        "channel": "Канал",
        "quantity": "Кількість",
        "events": "Події",
        "id": "ID",
        "date_time": "Дата й час",
        "user": "Користувач",
        "user_id": "ID користувача",
        "language": "Мова",
        "currency": "Валюта",
        "status": "Статус",
        "diagnostic_id": "ID діагностики",
        "metadata": "Метадані",
        "stage": "Етап",
        "diagnostic_generated": "Діагностику створено",
        "pdf_downloaded": "PDF завантажено",
        "email_sent": "Електронний лист надіслано",
        "feedback_received": "Відгук отримано",
        "telegram": "Telegram",
        "not_informed": "Не вказано",
    },
    "ru": {
        "channel": "Канал",
        "quantity": "Количество",
        "events": "События",
        "id": "ID",
        "date_time": "Дата и время",
        "user": "Пользователь",
        "user_id": "ID пользователя",
        "language": "Язык",
        "currency": "Валюта",
        "status": "Статус",
        "diagnostic_id": "ID диагностики",
        "metadata": "Метаданные",
        "stage": "Этап",
        "diagnostic_generated": "Диагностика создана",
        "pdf_downloaded": "PDF загружен",
        "email_sent": "Электронное письмо отправлено",
        "feedback_received": "Отзыв получен",
        "telegram": "Telegram",
        "not_informed": "Не указано",
    },
    "sa": {
        "channel": "القناة",
        "quantity": "الكمية",
        "events": "الأحداث",
        "id": "المعرّف",
        "date_time": "التاريخ والوقت",
        "user": "المستخدم",
        "user_id": "معرّف المستخدم",
        "language": "اللغة",
        "currency": "العملة",
        "status": "الحالة",
        "diagnostic_id": "معرّف التشخيص",
        "metadata": "البيانات الوصفية",
        "stage": "المرحلة",
        "diagnostic_generated": "تم إنشاء التشخيص",
        "pdf_downloaded": "تم تنزيل PDF",
        "email_sent": "تم إرسال البريد الإلكتروني",
        "feedback_received": "تم استلام الملاحظات",
        "telegram": "Telegram",
        "not_informed": "غير محدد",
    },
}

MULTICHANNEL_DISPLAY_TEXTS["en_gb"] = (
    MULTICHANNEL_DISPLAY_TEXTS["en_us"]
)

MULTICHANNEL_DISPLAY_TEXTS["ch"] = (
    MULTICHANNEL_DISPLAY_TEXTS["de"]
)


def multichannel_t(
    key: str,
    default: str | None = None,
) -> str:
    return dashboard_multichannel_t(
        key,
        language=dashboard_lang(),
        default=default,
    )


def prepare_multichannel_events_display(
    eventos_df,
):
    return dashboard_localize_multichannel_dataframe(
        eventos_df,
        language=dashboard_lang(),
        translate_channel_values=True,
        translate_feedback_values=True,
        translate_status_values=True,
    )



MULTICHANNEL_CHANNEL_TEXTS = {
    "pt": {
        "rag": "RAG",
        "web-app": "Aplicação web",
        "dashboard": "Dashboard",
        "pdf-download": "Download de PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "não informado": "Não informado",
    },
    "en_us": {
        "rag": "RAG",
        "web-app": "Web app",
        "dashboard": "Dashboard",
        "pdf-download": "PDF download",
        "telegram": "Telegram",
        "email": "Email",
        "não informado": "Not informed",
    },
    "es": {
        "rag": "RAG",
        "web-app": "Aplicación web",
        "dashboard": "Panel",
        "pdf-download": "Descarga de PDF",
        "telegram": "Telegram",
        "email": "Correo electrónico",
        "não informado": "No informado",
    },
    "fr": {
        "rag": "RAG",
        "web-app": "Application web",
        "dashboard": "Tableau de bord",
        "pdf-download": "Téléchargement PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "não informado": "Non renseigné",
    },
    "de": {
        "rag": "RAG",
        "web-app": "Webanwendung",
        "dashboard": "Dashboard",
        "pdf-download": "PDF-Download",
        "telegram": "Telegram",
        "email": "E-Mail",
        "não informado": "Nicht angegeben",
    },
    "it": {
        "rag": "RAG",
        "web-app": "Applicazione web",
        "dashboard": "Dashboard",
        "pdf-download": "Download PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "não informado": "Non specificato",
    },
    "ro": {
        "rag": "RAG",
        "web-app": "Aplicație web",
        "dashboard": "Panou",
        "pdf-download": "Descărcare PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "não informado": "Nespecificat",
    },
    "ua": {
        "rag": "RAG",
        "web-app": "Вебзастосунок",
        "dashboard": "Панель",
        "pdf-download": "Завантаження PDF",
        "telegram": "Telegram",
        "email": "Електронна пошта",
        "não informado": "Не вказано",
    },
    "ru": {
        "rag": "RAG",
        "web-app": "Веб-приложение",
        "dashboard": "Панель",
        "pdf-download": "Загрузка PDF",
        "telegram": "Telegram",
        "email": "Электронная почта",
        "não informado": "Не указано",
    },
    "sa": {
        "rag": "RAG",
        "web-app": "تطبيق الويب",
        "dashboard": "لوحة التحكم",
        "pdf-download": "تنزيل PDF",
        "telegram": "Telegram",
        "email": "البريد الإلكتروني",
        "não informado": "غير محدد",
    },
}

MULTICHANNEL_CHANNEL_TEXTS["en_gb"] = (
    MULTICHANNEL_CHANNEL_TEXTS["en_us"]
)

MULTICHANNEL_CHANNEL_TEXTS["ch"] = (
    MULTICHANNEL_CHANNEL_TEXTS["de"]
)


def multichannel_channel_t(
    value,
) -> str:
    return dashboard_translate_channel(
        value,
        language=dashboard_lang(),
    )

def prepare_multichannel_recent_events(
    eventos_df,
):
    return dashboard_localize_multichannel_dataframe(
        eventos_df,
        language=dashboard_lang(),
        translate_channel_values=True,
        translate_feedback_values=True,
        translate_status_values=True,
    )

def render_events(eventos_df, diagnosticos_df, feedbacks_df):
    st.write(dtx("events_title"))

    if eventos_df.empty:
        st.warning(dtx("no_events"))
        return

    eventos_reais = len(eventos_df)
    canais_ativos = eventos_df["canal"].nunique() if "canal" in eventos_df.columns else 0
    ultimo_canal_bruto = (
        eventos_df.iloc[0]["canal"]
        if "canal" in eventos_df.columns
        else "não informado"
    )

    ultimo_canal = multichannel_channel_t(
        ultimo_canal_bruto
    )

    col1, col2, col3 = st.columns(3)
    col1.metric(dtx("real_events"), eventos_reais)
    col2.metric(dtx("active_channels"), canais_ativos)
    col3.metric(dtx("latest_channel_metric"), ultimo_canal)

    if "canal" in eventos_df.columns:
        canal_counts = eventos_df["canal"].fillna("não informado").astype(str).value_counts()
        if len(canal_counts) > 1:
            canal_chart = (
                canal_counts
                .rename_axis("canal")
                .reset_index(name="quantidade")
                .sort_values(
                    "quantidade",
                    ascending=True,
                )
            )

            canal_chart["canal_exibicao"] = (
                canal_chart["canal"].map(
                    multichannel_channel_t
                )
            )

            fig_canais = px.bar(
                canal_chart,
                x="quantidade",
                y="canal_exibicao",
                orientation="h",
                text="quantidade",
                color_discrete_sequence=[
                    PLOTLY_ACCENT,
                ],
            )

            fig_canais.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    + multichannel_t("events")
                    + ": %{x}"
                    "<extra></extra>"
                ),
            )

            fig_canais.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
            )

            apply_inna_plotly_theme(
                fig_canais,
                height=400,
            )

            st.plotly_chart(
                fig_canais,
                width="stretch",
                key="events_by_channel_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )
        else:
            st.caption(dtx("only_one_channel"))

        canal_table = canal_counts.reset_index()
        canal_table.columns = [
            "canal",
            "quantidade",
        ]

        canal_table["canal"] = canal_table[
            "canal"
        ].map(
            multichannel_channel_t
        )

        canal_table_exibicao = (
            canal_table.rename(
                columns={
                    "canal": multichannel_t(
                        "channel"
                    ),
                    "quantidade": multichannel_t(
                        "quantity"
                    ),
                }
            )
        )

        st.dataframe(
            canal_table_exibicao,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander(
        dtx("last_events")
    ):
        eventos_exibicao = (
            prepare_multichannel_recent_events(
                eventos_df.head(20)
            )
        )

        st.dataframe(
            eventos_exibicao,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    render_funnel(eventos_df, diagnosticos_df, feedbacks_df)


def render_funnel(eventos_df, diagnosticos_df, feedbacks_df):
    st.write(dtx("funnel_title"))

    diagnosticos_count = len(diagnosticos_df)
    pdf_downloads = int((eventos_df["canal"] == "pdf-download").sum()) if not eventos_df.empty else 0
    emails = int((eventos_df["canal"] == "email").sum()) if not eventos_df.empty else 0
    telegram = int((eventos_df["canal"] == "telegram").sum()) if not eventos_df.empty else 0
    feedbacks_count = len(feedbacks_df) if not feedbacks_df.empty else 0

    taxa_pdf = (pdf_downloads / diagnosticos_count * 100) if diagnosticos_count > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(dt("diagnostics"), diagnosticos_count)
    col2.metric(dtx("downloaded_pdfs"), pdf_downloads)
    col3.metric(dtx("emails"), emails)
    col4.metric(dtx("feedbacks_label"), feedbacks_count)
    col5.metric(dtx("pdf_rate"), f"{taxa_pdf:.1f}%")

    funil = pd.DataFrame(
        {
            "etapa": [
                multichannel_t(
                    "diagnostic_generated"
                ),
                multichannel_t(
                    "pdf_downloaded"
                ),
                multichannel_t(
                    "email_sent"
                ),
                multichannel_t(
                    "feedback_received"
                ),
                multichannel_t(
                    "telegram"
                ),
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
        fig_funil = px.funnel(
            funil,
            x="quantidade",
            y="etapa",
            color_discrete_sequence=[
                PLOTLY_ACCENT,
            ],
        )

        fig_funil.update_traces(
            textposition="inside",
            textinfo="value+percent initial",
            marker_line_width=0,
            connector={
                "line": {
                    "color": (
                        "rgba(148, 163, 184, 0.35)"
                    ),
                    "width": 1,
                },
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                + multichannel_t(
                    "quantity"
                )
                + ": %{x}"
                "<extra></extra>"
            ),
        )

        fig_funil.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
        )

        apply_inna_plotly_theme(
            fig_funil,
            height=430,
        )

        st.plotly_chart(
            fig_funil,
            width="stretch",
            key="usage_funnel_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )
    else:
        st.caption(dtx("few_funnel_records"))

    funil_exibicao = funil.rename(
        columns={
            "etapa": multichannel_t(
                "stage"
            ),
            "quantidade": multichannel_t(
                "quantity"
            ),
        }
    )

    st.dataframe(
        funil_exibicao,
        use_container_width=True,
        hide_index=True,
    )


def render_international(diagnosticos_df):
    st.write(dtx("international_title"))

    if diagnosticos_df.empty:
        st.warning(dtx("no_international"))
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(dtx("diagnostics_by_language"))
        idioma_counts = diagnosticos_df["idioma"].fillna("não informado").astype(str).value_counts()

        if len(idioma_counts) > 1:
            idioma_chart = (
                idioma_counts
                .rename_axis("idioma")
                .reset_index(name="diagnosticos")
            )

            idioma_chart["idioma_nome"] = (
                idioma_chart["idioma"].apply(format_lang)
            )

            idioma_chart = idioma_chart.sort_values(
                "diagnosticos",
                ascending=True,
            )

            fig_idiomas = px.bar(
                idioma_chart,
                x="diagnosticos",
                y="idioma_nome",
                orientation="h",
                text="diagnosticos",
                color="diagnosticos",
                color_continuous_scale=[
                    "#0F172A",
                    "#38BDF8",
                ],
            )

            fig_idiomas.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Diagnósticos: %{x}"
                    "<extra></extra>"
                ),
            )

            fig_idiomas.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            apply_inna_plotly_theme(
                fig_idiomas,
                height=390,
            )

            st.plotly_chart(
                fig_idiomas,
                width="stretch",
                key="diagnostics_by_language_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )
        else:
            st.caption(dtx("only_one_language"))

        idioma_table = idioma_counts.reset_index()
        idioma_table.columns = ["idioma", "diagnósticos"]
        idioma_table["idioma_nome"] = idioma_table["idioma"].apply(format_lang)
        st.dataframe(idioma_table, use_container_width=True)

    with col2:
        st.write(dtx("diagnostics_by_currency"))
        moeda_counts = diagnosticos_df["moeda"].fillna("não informado").astype(str).value_counts()

        if len(moeda_counts) > 1:
            moeda_chart = (
                moeda_counts
                .rename_axis("moeda")
                .reset_index(name="diagnosticos")
                .sort_values(
                    "diagnosticos",
                    ascending=True,
                )
            )

            fig_moedas = px.bar(
                moeda_chart,
                x="diagnosticos",
                y="moeda",
                orientation="h",
                text="diagnosticos",
                color="diagnosticos",
                color_continuous_scale=[
                    "#312E81",
                    "#A78BFA",
                ],
            )

            fig_moedas.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Diagnósticos: %{x}"
                    "<extra></extra>"
                ),
            )

            fig_moedas.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            apply_inna_plotly_theme(
                fig_moedas,
                height=390,
            )

            st.plotly_chart(
                fig_moedas,
                width="stretch",
                key="diagnostics_by_currency_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )
        else:
            st.caption(dtx("only_one_currency"))

        moeda_table = moeda_counts.reset_index()
        moeda_table.columns = ["moeda", "diagnósticos"]
        st.dataframe(moeda_table, use_container_width=True)

    st.write(dtx("avg_balance_by_currency"))

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

    st.write(dtx("summary_language_currency"))

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



DASHBOARD_DFE_TEXTS = {
    "pt": {
        "quantity": "Quantidade",
        "percentage": "Percentual",
        "risk": "Risco",
        "low": "Baixo",
        "medium": "Médio",
        "high": "Alto",
        "not_informed": "Não informado",
        "name": "Nome",
        "total_diagnostics": "Total de diagnósticos",
        "average_score": "Score médio",
        "average_balance": "Saldo médio",
        "id": "ID",
        "date_time": "Data e hora",
        "language": "Idioma",
        "currency": "Moeda",
        "monthly_income": "Renda mensal",
        "balance": "Saldo",
        "income_commitment": "Comprometimento da renda (%)",
        "financial_score": "Score financeiro",
        "objective": "Objetivo",
        "useful": "Útil",
        "not_useful": "Não útil",
        "comment": "Comentário",
        "evaluation": "Avaliação",
        "feedbacks": "Feedbacks",
        "estimated_balance": "Saldo estimado",
        "date": "Data",
    },
    "en_us": {
        "quantity": "Quantity",
        "percentage": "Percentage",
        "risk": "Risk",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "not_informed": "Not informed",
        "name": "Name",
        "total_diagnostics": "Total diagnostics",
        "average_score": "Average score",
        "average_balance": "Average balance",
        "id": "ID",
        "date_time": "Date and time",
        "language": "Language",
        "currency": "Currency",
        "monthly_income": "Monthly income",
        "balance": "Balance",
        "income_commitment": "Income commitment (%)",
        "financial_score": "Financial score",
        "objective": "Objective",
        "useful": "Useful",
        "not_useful": "Not useful",
        "comment": "Comment",
        "evaluation": "Evaluation",
        "feedbacks": "Feedback",
        "estimated_balance": "Estimated balance",
        "date": "Date",
    },
    "es": {
        "quantity": "Cantidad",
        "percentage": "Porcentaje",
        "risk": "Riesgo",
        "low": "Bajo",
        "medium": "Medio",
        "high": "Alto",
        "not_informed": "No informado",
        "name": "Nombre",
        "total_diagnostics": "Total de diagnósticos",
        "average_score": "Puntuación media",
        "average_balance": "Saldo medio",
        "id": "ID",
        "date_time": "Fecha y hora",
        "language": "Idioma",
        "currency": "Moneda",
        "monthly_income": "Ingreso mensual",
        "balance": "Saldo",
        "income_commitment": "Compromiso de ingresos (%)",
        "financial_score": "Puntuación financiera",
        "objective": "Objetivo",
        "useful": "Útil",
        "not_useful": "No útil",
        "comment": "Comentario",
        "evaluation": "Evaluación",
        "feedbacks": "Comentarios",
        "estimated_balance": "Saldo estimado",
        "date": "Fecha",
    },
    "fr": {
        "quantity": "Quantité",
        "percentage": "Pourcentage",
        "risk": "Risque",
        "low": "Faible",
        "medium": "Moyen",
        "high": "Élevé",
        "not_informed": "Non renseigné",
        "name": "Nom",
        "total_diagnostics": "Total des diagnostics",
        "average_score": "Score moyen",
        "average_balance": "Solde moyen",
        "id": "ID",
        "date_time": "Date et heure",
        "language": "Langue",
        "currency": "Devise",
        "monthly_income": "Revenu mensuel",
        "balance": "Solde",
        "income_commitment": "Engagement du revenu (%)",
        "financial_score": "Score financier",
        "objective": "Objectif",
        "useful": "Utile",
        "not_useful": "Non utile",
        "comment": "Commentaire",
        "evaluation": "Évaluation",
        "feedbacks": "Retours",
        "estimated_balance": "Solde estimé",
        "date": "Date",
    },
    "de": {
        "quantity": "Anzahl",
        "percentage": "Prozentsatz",
        "risk": "Risiko",
        "low": "Niedrig",
        "medium": "Mittel",
        "high": "Hoch",
        "not_informed": "Nicht angegeben",
        "name": "Name",
        "total_diagnostics": "Diagnosen insgesamt",
        "average_score": "Durchschnittliche Punktzahl",
        "average_balance": "Durchschnittlicher Saldo",
        "id": "ID",
        "date_time": "Datum und Uhrzeit",
        "language": "Sprache",
        "currency": "Währung",
        "monthly_income": "Monatliches Einkommen",
        "balance": "Saldo",
        "income_commitment": "Einkommensbelastung (%)",
        "financial_score": "Finanzielle Punktzahl",
        "objective": "Ziel",
        "useful": "Nützlich",
        "not_useful": "Nicht nützlich",
        "comment": "Kommentar",
        "evaluation": "Bewertung",
        "feedbacks": "Feedback",
        "estimated_balance": "Geschätzter Saldo",
        "date": "Datum",
    },
    "it": {
        "quantity": "Quantità",
        "percentage": "Percentuale",
        "risk": "Rischio",
        "low": "Basso",
        "medium": "Medio",
        "high": "Alto",
        "not_informed": "Non specificato",
        "name": "Nome",
        "total_diagnostics": "Totale diagnosi",
        "average_score": "Punteggio medio",
        "average_balance": "Saldo medio",
        "id": "ID",
        "date_time": "Data e ora",
        "language": "Lingua",
        "currency": "Valuta",
        "monthly_income": "Reddito mensile",
        "balance": "Saldo",
        "income_commitment": "Impegno del reddito (%)",
        "financial_score": "Punteggio finanziario",
        "objective": "Obiettivo",
        "useful": "Utile",
        "not_useful": "Non utile",
        "comment": "Commento",
        "evaluation": "Valutazione",
        "feedbacks": "Feedback",
        "estimated_balance": "Saldo stimato",
        "date": "Data",
    },
    "ro": {
        "quantity": "Cantitate",
        "percentage": "Procent",
        "risk": "Risc",
        "low": "Scăzut",
        "medium": "Mediu",
        "high": "Ridicat",
        "not_informed": "Nespecificat",
        "name": "Nume",
        "total_diagnostics": "Total diagnosticări",
        "average_score": "Scor mediu",
        "average_balance": "Sold mediu",
        "id": "ID",
        "date_time": "Data și ora",
        "language": "Limbă",
        "currency": "Monedă",
        "monthly_income": "Venit lunar",
        "balance": "Sold",
        "income_commitment": "Angajamentul venitului (%)",
        "financial_score": "Scor financiar",
        "objective": "Obiectiv",
        "useful": "Util",
        "not_useful": "Neutil",
        "comment": "Comentariu",
        "evaluation": "Evaluare",
        "feedbacks": "Feedback",
        "estimated_balance": "Sold estimat",
        "date": "Dată",
    },
    "ua": {
        "quantity": "Кількість",
        "percentage": "Відсоток",
        "risk": "Ризик",
        "low": "Низький",
        "medium": "Середній",
        "high": "Високий",
        "not_informed": "Не вказано",
        "name": "Ім’я",
        "total_diagnostics": "Усього діагностик",
        "average_score": "Середній бал",
        "average_balance": "Середній баланс",
        "id": "ID",
        "date_time": "Дата й час",
        "language": "Мова",
        "currency": "Валюта",
        "monthly_income": "Місячний дохід",
        "balance": "Баланс",
        "income_commitment": "Навантаження на дохід (%)",
        "financial_score": "Фінансовий бал",
        "objective": "Мета",
        "useful": "Корисний",
        "not_useful": "Некорисний",
        "comment": "Коментар",
        "evaluation": "Оцінка",
        "feedbacks": "Відгуки",
        "estimated_balance": "Орієнтовний баланс",
        "date": "Дата",
    },
    "ru": {
        "quantity": "Количество",
        "percentage": "Процент",
        "risk": "Риск",
        "low": "Низкий",
        "medium": "Средний",
        "high": "Высокий",
        "not_informed": "Не указано",
        "name": "Имя",
        "total_diagnostics": "Всего диагностик",
        "average_score": "Средний балл",
        "average_balance": "Средний баланс",
        "id": "ID",
        "date_time": "Дата и время",
        "language": "Язык",
        "currency": "Валюта",
        "monthly_income": "Месячный доход",
        "balance": "Баланс",
        "income_commitment": "Нагрузка на доход (%)",
        "financial_score": "Финансовый балл",
        "objective": "Цель",
        "useful": "Полезный",
        "not_useful": "Неполезный",
        "comment": "Комментарий",
        "evaluation": "Оценка",
        "feedbacks": "Отзывы",
        "estimated_balance": "Расчётный баланс",
        "date": "Дата",
    },
    "sa": {
        "quantity": "الكمية",
        "percentage": "النسبة المئوية",
        "risk": "المخاطر",
        "low": "منخفض",
        "medium": "متوسط",
        "high": "مرتفع",
        "not_informed": "غير محدد",
        "name": "الاسم",
        "total_diagnostics": "إجمالي التشخيصات",
        "average_score": "متوسط النتيجة",
        "average_balance": "متوسط الرصيد",
        "id": "المعرّف",
        "date_time": "التاريخ والوقت",
        "language": "اللغة",
        "currency": "العملة",
        "monthly_income": "الدخل الشهري",
        "balance": "الرصيد",
        "income_commitment": "نسبة الالتزام بالدخل (%)",
        "financial_score": "النتيجة المالية",
        "objective": "الهدف",
        "useful": "مفيد",
        "not_useful": "غير مفيد",
        "comment": "التعليق",
        "evaluation": "التقييم",
        "feedbacks": "الملاحظات",
        "estimated_balance": "الرصيد التقديري",
        "date": "التاريخ",
    },
}

DASHBOARD_DFE_TEXTS["en_gb"] = (
    DASHBOARD_DFE_TEXTS["en_us"]
)

DASHBOARD_DFE_TEXTS["ch"] = (
    DASHBOARD_DFE_TEXTS["de"]
)


def dfe_t(
    key: str,
    default: str | None = None,
) -> str:
    language = dashboard_lang()

    texts = DASHBOARD_DFE_TEXTS.get(
        language,
        DASHBOARD_DFE_TEXTS["pt"],
    )

    if key in texts:
        return texts[key]

    if default is not None:
        return default

    return key


def dfe_translate_risk(
    value,
) -> str:
    if value is None or pd.isna(value):
        return dfe_t("not_informed")

    normalized = str(value).strip().casefold()

    low_values = {
        "baixo",
        "baixa",
        "low",
        "niedrig",
    }

    medium_values = {
        "médio",
        "medio",
        "média",
        "media",
        "medium",
        "mittel",
    }

    high_values = {
        "alto",
        "alta",
        "high",
        "hoch",
    }

    unknown_values = {
        "",
        "none",
        "nan",
        "null",
        "não informado",
        "nao informado",
        "not informed",
    }

    if normalized in low_values:
        return dfe_t("low")

    if normalized in medium_values:
        return dfe_t("medium")

    if normalized in high_values:
        return dfe_t("high")

    if normalized in unknown_values:
        return dfe_t("not_informed")

    return str(value)


def dfe_translate_useful(
    value,
) -> str:
    return dashboard_translate_useful(
        value,
        language=dashboard_lang(),
    )

def dfe_translate_dataframe_values(
    dataframe,
):
    table = dataframe.copy()

    for column in (
        "risco_exibicao",
        "nivel_risco",
        "risco",
    ):
        if column in table.columns:
            table[column] = table[
                column
            ].map(
                dfe_translate_risk
            )

    if "util" in table.columns:
        table["util"] = table[
            "util"
        ].map(
            dfe_translate_useful
        )

    return table


DASHBOARD_DFE_COLUMN_KEYS = {
    "id": "id",
    "data_hora": "date_time",
    "data_label": "date",
    "nome": "name",
    "idioma": "language",
    "moeda": "currency",
    "renda_mensal": "monthly_income",
    "saldo_formatado": "balance",
    "saldo_estimado": "estimated_balance",
    "saldo_medio": "average_balance",
    "comprometimento_renda_percentual": (
        "income_commitment"
    ),
    "score_financeiro": "financial_score",
    "score_medio": "average_score",
    "risco_exibicao": "risk",
    "nivel_risco": "risk",
    "risco": "risk",
    "objetivo": "objective",
    "total_diagnosticos": "total_diagnostics",
    "quantidade": "quantity",
    "avaliacao": "evaluation",
    "util": "useful",
    "comentario": "comment",
}


def dfe_rename_dataframe_columns(
    dataframe,
):
    return dataframe.rename(
        columns={
            column: dfe_t(key)
            for column, key
            in DASHBOARD_DFE_COLUMN_KEYS.items()
            if column in dataframe.columns
        }
    )


def render_diagnostics(
    diagnosticos_df,
):
    st.write(
        dtx("diagnostics_title")
    )

    if diagnosticos_df.empty:
        st.warning(
            dtx("no_diagnostics")
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            dtx("risk_distribution")
        )

        risk_column = None

        for candidate in (
            "risco_exibicao",
            "nivel_risco",
            "risco",
        ):
            if candidate in diagnosticos_df.columns:
                risk_column = candidate
                break

        if risk_column is None:
            st.caption(
                dfe_t("not_informed")
            )
        else:
            risk_counts = (
                diagnosticos_df[
                    risk_column
                ]
                .fillna(
                    dfe_t("not_informed")
                )
                .astype(str)
                .value_counts()
            )

            risk_chart = (
                risk_counts
                .rename_axis("risco")
                .reset_index(
                    name="quantidade"
                )
            )

            risk_chart[
                "risco_exibicao"
            ] = risk_chart[
                "risco"
            ].map(
                dfe_translate_risk
            )

            if len(risk_chart) > 1:
                fig_risco = px.pie(
                    risk_chart,
                    names="risco_exibicao",
                    values="quantidade",
                    hole=0.58,
                    color_discrete_sequence=[
                        "#34D399",
                        "#F59E0B",
                        "#F87171",
                        "#38BDF8",
                        "#A78BFA",
                    ],
                )

                fig_risco.update_traces(
                    textposition="inside",
                    textinfo="label+percent",
                    marker={
                        "line": {
                            "color": PLOTLY_BG,
                            "width": 2,
                        },
                    },
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        + dfe_t("quantity")
                        + ": %{value}<br>"
                        + dfe_t("percentage")
                        + ": %{percent}"
                        + "<extra></extra>"
                    ),
                )

                fig_risco.update_layout(
                    showlegend=True,
                    legend={
                        "orientation": "h",
                        "yanchor": "bottom",
                        "y": -0.12,
                        "xanchor": "center",
                        "x": 0.5,
                    },
                )

                apply_inna_plotly_theme(
                    fig_risco,
                    height=410,
                )

                st.plotly_chart(
                    fig_risco,
                    width="stretch",
                    key="risk_distribution_chart",
                    config={
                        "displayModeBar": False,
                        "responsive": True,
                    },
                )
            else:
                st.caption(
                    dtx("only_one_risk")
                )

            risk_table = risk_chart[
                [
                    "risco_exibicao",
                    "quantidade",
                ]
            ].rename(
                columns={
                    "risco_exibicao": (
                        dfe_t("risk")
                    ),
                    "quantidade": (
                        dfe_t("quantity")
                    ),
                }
            )

            st.dataframe(
                risk_table,
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        st.write(
            dtx("user_ranking")
        )

        ranking = (
            diagnosticos_df
            .groupby(
                "nome",
                dropna=False,
            )
            .agg(
                total_diagnosticos=(
                    "id",
                    "count",
                ),
                score_medio=(
                    "score_financeiro",
                    "mean",
                ),
                saldo_medio=(
                    "saldo_estimado",
                    "mean",
                ),
            )
            .reset_index()
            .sort_values(
                "total_diagnosticos",
                ascending=False,
            )
        )

        ranking["nome"] = ranking[
            "nome"
        ].fillna(
            dfe_t("not_informed")
        )

        ranking["score_medio"] = ranking[
            "score_medio"
        ].round(1)

        ranking["saldo_medio"] = ranking[
            "saldo_medio"
        ].round(2)

        ranking_display = (
            dfe_rename_dataframe_columns(
                ranking
            )
        )

        st.dataframe(
            ranking_display,
            use_container_width=True,
            hide_index=True,
        )

    st.write(
        dtx("last_diagnostics")
    )

    columns = [
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

    available_columns = [
        column
        for column in columns
        if column in diagnosticos_df.columns
    ]

    diagnostics_display = (
        diagnosticos_df[
            available_columns
        ]
        .head(50)
        .copy()
    )

    diagnostics_display = (
        dfe_translate_dataframe_values(
            diagnostics_display
        )
    )

    diagnostics_display = (
        dfe_rename_dataframe_columns(
            diagnostics_display
        )
    )

    st.dataframe(
        diagnostics_display,
        use_container_width=True,
        hide_index=True,
    )



def render_feedbacks(
    feedbacks_df,
):
    st.write(
        dtx("feedbacks_title")
    )

    if feedbacks_df.empty:
        st.warning(
            dtx("no_feedbacks")
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            dtx("useful_feedbacks")
        )

        if "util" in feedbacks_df.columns:
            feedback_values = (
                feedbacks_df[
                    "util"
                ].map(
                    dfe_translate_useful
                )
            )

            feedback_chart = (
                feedback_values
                .value_counts()
                .rename_axis("avaliacao")
                .reset_index(
                    name="quantidade"
                )
            )

            fig_feedback = px.pie(
                feedback_chart,
                names="avaliacao",
                values="quantidade",
                hole=0.58,
                color_discrete_sequence=[
                    "#38BDF8",
                    "#A78BFA",
                    "#34D399",
                    "#F59E0B",
                ],
            )

            fig_feedback.update_traces(
                textposition="inside",
                textinfo="label+percent",
                marker={
                    "line": {
                        "color": PLOTLY_BG,
                        "width": 2,
                    },
                },
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    + dfe_t("feedbacks")
                    + ": %{value}<br>"
                    + dfe_t("percentage")
                    + ": %{percent}"
                    + "<extra></extra>"
                ),
            )

            fig_feedback.update_layout(
                showlegend=True,
                legend={
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": -0.12,
                    "xanchor": "center",
                    "x": 0.5,
                },
            )

            apply_inna_plotly_theme(
                fig_feedback,
                height=400,
            )

            st.plotly_chart(
                fig_feedback,
                width="stretch",
                key="useful_feedbacks_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

            feedback_table = (
                feedback_chart.rename(
                    columns={
                        "avaliacao": (
                            dfe_t("evaluation")
                        ),
                        "quantidade": (
                            dfe_t("quantity")
                        ),
                    }
                )
            )

            st.dataframe(
                feedback_table,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                dfe_t("not_informed")
            )

    with col2:
        st.write(
            dtx("received_comments")
        )

        comment_columns = [
            column
            for column in (
                "data_hora",
                "nome",
                "comentario",
                "util",
            )
            if column in feedbacks_df.columns
        ]

        if comment_columns:
            comments_display = (
                feedbacks_df[
                    comment_columns
                ]
                .head(30)
                .copy()
            )

            comments_display = (
                dfe_translate_dataframe_values(
                    comments_display
                )
            )

            comments_display = (
                dfe_rename_dataframe_columns(
                    comments_display
                )
            )

            st.dataframe(
                comments_display,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                dtx("no_comments")
            )

    st.write(
        dtx("last_feedbacks")
    )

    latest_feedbacks = (
        feedbacks_df
        .head(50)
        .copy()
    )

    latest_feedbacks = (
        dfe_translate_dataframe_values(
            latest_feedbacks
        )
    )

    latest_feedbacks = (
        dfe_rename_dataframe_columns(
            latest_feedbacks
        )
    )

    st.dataframe(
        latest_feedbacks,
        use_container_width=True,
        hide_index=True,
    )



def render_evolution(
    diagnosticos_df,
):
    st.write(
        dtx("evolution_title")
    )

    if diagnosticos_df.empty:
        st.warning(
            dtx("no_diagnostics")
        )
        return

    dataframe = diagnosticos_df.copy()

    if "data_hora" in dataframe.columns:
        dataframe = dataframe.sort_values(
            "data_hora"
        )

        dataframe["data_label"] = (
            dataframe[
                "data_hora"
            ].dt.strftime(
                "%d/%m %H:%M"
            )
        )
    else:
        dataframe["data_label"] = (
            dataframe["id"].astype(str)
        )

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            dtx("score_evolution")
        )

        if len(dataframe) > 1:
            score_chart = dataframe[
                [
                    "data_label",
                    "score_financeiro",
                ]
            ].copy()

            fig_score = px.line(
                score_chart,
                x="data_label",
                y="score_financeiro",
                markers=True,
            )

            fig_score.update_traces(
                line={
                    "color": "#38BDF8",
                    "width": 3,
                },
                marker={
                    "color": "#E0F2FE",
                    "size": 9,
                    "line": {
                        "color": "#38BDF8",
                        "width": 2,
                    },
                },
                fill="tozeroy",
                fillcolor=(
                    "rgba(56, 189, 248, 0.13)"
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    + dfe_t(
                        "financial_score"
                    )
                    + ": %{y:.1f}"
                    + "<extra></extra>"
                ),
            )

            fig_score.update_layout(
                xaxis_title=None,
                yaxis_title=dfe_t(
                    "financial_score"
                ),
                showlegend=False,
            )

            apply_inna_plotly_theme(
                fig_score,
                height=410,
            )

            st.plotly_chart(
                fig_score,
                width="stretch",
                key=(
                    "financial_score_"
                    "evolution_chart"
                ),
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )
        else:
            st.caption(
                dtx("evolution_wait")
            )

            score_table = dataframe[
                [
                    column
                    for column in (
                        "id",
                        "nome",
                        "score_financeiro",
                    )
                    if column in dataframe.columns
                ]
            ].copy()

            score_table = (
                dfe_rename_dataframe_columns(
                    score_table
                )
            )

            st.dataframe(
                score_table,
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        st.write(
            dtx("balance_evolution")
        )

        if len(dataframe) > 1:
            balance_chart = dataframe[
                [
                    "data_label",
                    "saldo_estimado",
                ]
            ].copy()

            fig_balance = px.area(
                balance_chart,
                x="data_label",
                y="saldo_estimado",
                markers=True,
            )

            fig_balance.update_traces(
                line={
                    "color": "#34D399",
                    "width": 3,
                },
                marker={
                    "color": "#D1FAE5",
                    "size": 9,
                    "line": {
                        "color": "#34D399",
                        "width": 2,
                    },
                },
                fillcolor=(
                    "rgba(52, 211, 153, 0.16)"
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    + dfe_t(
                        "estimated_balance"
                    )
                    + ": %{y:,.2f}"
                    + "<extra></extra>"
                ),
            )

            fig_balance.update_layout(
                xaxis_title=None,
                yaxis_title=dfe_t(
                    "estimated_balance"
                ),
                showlegend=False,
            )

            apply_inna_plotly_theme(
                fig_balance,
                height=410,
            )

            st.plotly_chart(
                fig_balance,
                width="stretch",
                key=(
                    "estimated_balance_"
                    "evolution_chart"
                ),
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )
        else:
            st.caption(
                dtx("evolution_wait")
            )

            balance_table = dataframe[
                [
                    column
                    for column in (
                        "id",
                        "nome",
                        "saldo_estimado",
                    )
                    if column in dataframe.columns
                ]
            ].copy()

            balance_table = (
                dfe_rename_dataframe_columns(
                    balance_table
                )
            )

            st.dataframe(
                balance_table,
                use_container_width=True,
                hide_index=True,
            )



def render_executive_reading(diagnosticos_df, feedbacks_df, eventos_df):
    st.write(dtx("executive_title"))
    st.write(dtx("current_base_summary"))

    total_diag = len(diagnosticos_df)
    usuarios = diagnosticos_df["nome"].nunique() if not diagnosticos_df.empty and "nome" in diagnosticos_df.columns else 0
    score = diagnosticos_df["score_financeiro"].mean() if not diagnosticos_df.empty and "score_financeiro" in diagnosticos_df.columns else 0

    saldo = diagnosticos_df["saldo_estimado"].mean() if not diagnosticos_df.empty and "saldo_estimado" in diagnosticos_df.columns else 0
    moeda, simbolo = get_currency_context(diagnosticos_df)
    saldo_formatado = format_money(saldo, moeda, simbolo)

    risco_mais_comum = "não informado"
    if not diagnosticos_df.empty and "risco_exibicao" in diagnosticos_df.columns:
        riscos_validos = diagnosticos_df["risco_exibicao"].dropna().astype(str)
        if not riscos_validos.empty:
            risco_mais_comum = riscos_validos.mode().iloc[0]

    canal_mais_usado = "não informado"
    if not eventos_df.empty and "canal" in eventos_df.columns:
        canais_validos = eventos_df["canal"].dropna().astype(str)
        if not canais_validos.empty:
            canal_mais_usado = canais_validos.mode().iloc[0]

    idiomas = "não informado"
    if not diagnosticos_df.empty and "idioma" in diagnosticos_df.columns:
        lista_idiomas = sorted(diagnosticos_df["idioma"].dropna().astype(str).unique().tolist())
        if lista_idiomas:
            idiomas = ", ".join(lista_idiomas)

    moedas = "não informado"
    if not diagnosticos_df.empty and "moeda" in diagnosticos_df.columns:
        lista_moedas = sorted(diagnosticos_df["moeda"].dropna().astype(str).unique().tolist())
        if lista_moedas:
            moedas = ", ".join(lista_moedas)

    lang = dashboard_lang()

    texts = {
        "pt": {
            "generated": "Foram gerados {total} diagnósticos nos filtros selecionados.",
            "users": "Existem {users} usuários únicos na base filtrada.",
            "score": "O score financeiro médio é de {score:.1f}/100.",
            "balance": "O saldo médio estimado é de {balance}.",
            "risk": "O nível de risco mais comum é {risk}.",
            "channel": "O canal mais usado nos eventos filtrados é {channel}.",
            "languages": "Idiomas encontrados: {languages}.",
            "currencies": "Moedas encontradas: {currencies}.",
            "international": "A visão internacional separa idioma e moeda para evitar misturar resultados internacionais.",
            "closing": "Esses dados ajudam a validar se a INNA está gerando valor real para usuários em diferentes canais, idiomas e moedas.",
        },
        "en_us": {
            "generated": "{total} diagnoses were generated in the selected filters.",
            "users": "There are {users} unique users in the filtered base.",
            "score": "The average financial score is {score:.1f}/100.",
            "balance": "The estimated average balance is {balance}.",
            "risk": "The most common risk level is {risk}.",
            "channel": "The most used channel in the filtered events is {channel}.",
            "languages": "Languages found: {languages}.",
            "currencies": "Currencies found: {currencies}.",
            "international": "The international view separates language and currency to avoid mixing international results.",
            "closing": "These data help validate whether INNA is generating real value for users across different channels, languages and currencies.",
        },
        "en_gb": {
            "generated": "{total} diagnoses were generated in the selected filters.",
            "users": "There are {users} unique users in the filtered base.",
            "score": "The average financial score is {score:.1f}/100.",
            "balance": "The estimated average balance is {balance}.",
            "risk": "The most common risk level is {risk}.",
            "channel": "The most used channel in the filtered events is {channel}.",
            "languages": "Languages found: {languages}.",
            "currencies": "Currencies found: {currencies}.",
            "international": "The international view separates language and currency to avoid mixing international results.",
            "closing": "These data help validate whether INNA is generating real value for users across different channels, languages and currencies.",
        },
        "es": {
            "generated": "Se generaron {total} diagnósticos en los filtros seleccionados.",
            "users": "Hay {users} usuarios únicos en la base filtrada.",
            "score": "El score financiero medio es de {score:.1f}/100.",
            "balance": "El saldo medio estimado es de {balance}.",
            "risk": "El nivel de riesgo más común es {risk}.",
            "channel": "El canal más usado en los eventos filtrados es {channel}.",
            "languages": "Idiomas encontrados: {languages}.",
            "currencies": "Monedas encontradas: {currencies}.",
            "international": "La vista internacional separa idioma y moneda para evitar mezclar resultados internacionales.",
            "closing": "Estos datos ayudan a validar si INNA está generando valor real para usuarios en diferentes canales, idiomas y monedas.",
        },
        "fr": {
            "generated": "{total} diagnostics ont été générés dans les filtres sélectionnés.",
            "users": "Il y a {users} utilisateurs uniques dans la base filtrée.",
            "score": "Le score financier moyen est de {score:.1f}/100.",
            "balance": "Le solde moyen estimé est de {balance}.",
            "risk": "Le niveau de risque le plus courant est {risk}.",
            "channel": "Le canal le plus utilisé dans les événements filtrés est {channel}.",
            "languages": "Langues trouvées : {languages}.",
            "currencies": "Devises trouvées : {currencies}.",
            "international": "La vue internationale sépare la langue et la devise afin d’éviter de mélanger les résultats internationaux.",
            "closing": "Ces données aident à vérifier si INNA génère une valeur réelle pour les utilisateurs sur différents canaux, langues et devises.",
        },
        "de": {
            "generated": "In den ausgewählten Filtern wurden {total} Diagnosen erstellt.",
            "users": "Es gibt {users} eindeutige Benutzer in der gefilterten Basis.",
            "score": "Der durchschnittliche Finanzscore beträgt {score:.1f}/100.",
            "balance": "Der geschätzte durchschnittliche Saldo beträgt {balance}.",
            "risk": "Das häufigste Risikoniveau ist {risk}.",
            "channel": "Der am häufigsten genutzte Kanal in den gefilterten Ereignissen ist {channel}.",
            "languages": "Gefundene Sprachen: {languages}.",
            "currencies": "Gefundene Währungen: {currencies}.",
            "international": "Die internationale Ansicht trennt Sprache und Währung, um internationale Ergebnisse nicht zu vermischen.",
            "closing": "Diese Daten helfen zu validieren, ob INNA echten Nutzen für Benutzer über verschiedene Kanäle, Sprachen und Währungen erzeugt.",
        },
        "it": {
            "generated": "Sono state generate {total} diagnosi nei filtri selezionati.",
            "users": "Ci sono {users} utenti unici nella base filtrata.",
            "score": "Il punteggio finanziario medio è {score:.1f}/100.",
            "balance": "Il saldo medio stimato è {balance}.",
            "risk": "Il livello di rischio più comune è {risk}.",
            "channel": "Il canale più usato negli eventi filtrati è {channel}.",
            "languages": "Lingue trovate: {languages}.",
            "currencies": "Valute trovate: {currencies}.",
            "international": "La vista internazionale separa lingua e valuta per evitare di mescolare risultati internazionali.",
            "closing": "Questi dati aiutano a validare se INNA sta generando valore reale per utenti in diversi canali, lingue e valute.",
        },
        "ro": {
            "generated": "Au fost generate {total} diagnosticări în filtrele selectate.",
            "users": "Există {users} utilizatori unici în baza filtrată.",
            "score": "Scorul financiar mediu este {score:.1f}/100.",
            "balance": "Soldul mediu estimat este {balance}.",
            "risk": "Cel mai comun nivel de risc este {risk}.",
            "channel": "Cel mai folosit canal în evenimentele filtrate este {channel}.",
            "languages": "Limbi găsite: {languages}.",
            "currencies": "Monede găsite: {currencies}.",
            "international": "Vederea internațională separă limba și moneda pentru a evita amestecarea rezultatelor internaționale.",
            "closing": "Aceste date ajută la validarea faptului că INNA generează valoare reală pentru utilizatori pe diferite canale, limbi și monede.",
        },
        "ua": {
            "generated": "У вибраних фільтрах створено {total} діагностики.",
            "users": "У відфільтрованій базі є {users} унікальних користувачів.",
            "score": "Середній фінансовий бал становить {score:.1f}/100.",
            "balance": "Орієнтовний середній баланс становить {balance}.",
            "risk": "Найпоширеніший рівень ризику: {risk}.",
            "channel": "Найчастіше використовуваний канал у відфільтрованих подіях: {channel}.",
            "languages": "Знайдені мови: {languages}.",
            "currencies": "Знайдені валюти: {currencies}.",
            "international": "Міжнародний огляд розділяє мову та валюту, щоб не змішувати міжнародні результати.",
            "closing": "Ці дані допомагають перевірити, чи INNA створює реальну цінність для користувачів у різних каналах, мовах і валютах.",
        },
        "ru": {
            "generated": "В выбранных фильтрах создано {total} диагностик.",
            "users": "В отфильтрованной базе есть {users} уникальных пользователей.",
            "score": "Средний финансовый балл составляет {score:.1f}/100.",
            "balance": "Оценочный средний баланс составляет {balance}.",
            "risk": "Самый распространенный уровень риска: {risk}.",
            "channel": "Самый используемый канал в отфильтрованных событиях: {channel}.",
            "languages": "Найденные языки: {languages}.",
            "currencies": "Найденные валюты: {currencies}.",
            "international": "Международный обзор разделяет язык и валюту, чтобы не смешивать международные результаты.",
            "closing": "Эти данные помогают проверить, создает ли INNA реальную ценность для пользователей в разных каналах, языках и валютах.",
        },
        "sa": {
            "generated": "تم إنشاء {total} تشخيصات ضمن الفلاتر المحددة.",
            "users": "يوجد {users} مستخدمين فريدين في القاعدة المفلترة.",
            "score": "متوسط النتيجة المالية هو {score:.1f}/100.",
            "balance": "متوسط الرصيد التقديري هو {balance}.",
            "risk": "مستوى المخاطر الأكثر شيوعًا هو {risk}.",
            "channel": "القناة الأكثر استخدامًا في الأحداث المفلترة هي {channel}.",
            "languages": "اللغات الموجودة: {languages}.",
            "currencies": "العملات الموجودة: {currencies}.",
            "international": "يفصل العرض الدولي بين اللغة والعملة لتجنب خلط النتائج الدولية.",
            "closing": "تساعد هذه البيانات في التحقق مما إذا كانت INNA تقدم قيمة حقيقية للمستخدمين عبر قنوات ولغات وعملات مختلفة.",
        },
        "ch": {
            "generated": "In den ausgewählten Filtern wurden {total} Diagnosen erstellt.",
            "users": "Es gibt {users} eindeutige Benutzer in der gefilterten Basis.",
            "score": "Der durchschnittliche Finanzscore beträgt {score:.1f}/100.",
            "balance": "Der geschätzte durchschnittliche Saldo beträgt {balance}.",
            "risk": "Das häufigste Risikoniveau ist {risk}.",
            "channel": "Der am häufigsten genutzte Kanal in den gefilterten Ereignissen ist {channel}.",
            "languages": "Gefundene Sprachen: {languages}.",
            "currencies": "Gefundene Währungen: {currencies}.",
            "international": "Die internationale Ansicht trennt Sprache und Währung, um internationale Ergebnisse nicht zu vermischen.",
            "closing": "Diese Daten helfen zu validieren, ob INNA echten Nutzen für Benutzer über verschiedene Kanäle, Sprachen und Währungen erzeugt.",
        },
    }

    t = texts.get(lang, texts["pt"])

    st.markdown(
        f"""
- {t["generated"].format(total=total_diag)}
- {t["users"].format(users=usuarios)}
- {t["score"].format(score=score)}
- {t["balance"].format(balance=saldo_formatado)}
- {t["risk"].format(risk=risco_mais_comum)}
- {t["channel"].format(channel=canal_mais_usado)}
- {t["languages"].format(languages=idiomas)}
- {t["currencies"].format(currencies=moedas)}
- {t["international"]}
"""
    )

    st.write(t["closing"])


def load_agent_evaluations():
    try:
        conn = get_connection()
        query = """
        SELECT *
        FROM avaliacoes_agente_inna
        ORDER BY data_hora DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty and "data_hora" in df.columns:
            df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

        return df

    except Exception:
        return pd.DataFrame()


def save_agent_evaluation(
    nome_avaliador,
    assertividade,
    seguranca,
    conviccao,
    clareza,
    utilidade,
    comentario,
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes_agente_inna (
            id SERIAL PRIMARY KEY,
            data_hora TIMESTAMP DEFAULT NOW(),
            nome_avaliador TEXT,
            assertividade NUMERIC,
            seguranca NUMERIC,
            conviccao NUMERIC,
            clareza NUMERIC,
            utilidade NUMERIC,
            comentario TEXT
        );
    """)

    cur.execute("""
        INSERT INTO avaliacoes_agente_inna
        (
            data_hora,
            nome_avaliador,
            assertividade,
            seguranca,
            conviccao,
            clareza,
            utilidade,
            comentario
        )
        VALUES
        (
            NOW(),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
    """, (
        nome_avaliador,
        assertividade,
        seguranca,
        conviccao,
        clareza,
        utilidade,
        comentario,
    ))

    conn.commit()
    cur.close()
    conn.close()


def render_agent_evaluation(diagnosticos_df, feedbacks_df, eventos_df):
    lang = dashboard_lang()

    texts = {
        "pt": {
            "title": "## 🧪 Avaliação e Métricas do Agente INNA",
            "info": "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade.",
            "quality": "### 📌 Indicadores reais de qualidade",
            "evaluations": "Avaliações",
            "general_average": "Média geral",
            "assertiveness": "Assertividade",
            "security": "Segurança",
            "coherence": "Coerência",
            "clarity": "Clareza",
            "utility": "Utilidade média",
            "register": "### 📝 Registrar avaliação real",
            "evaluator": "Nome do avaliador",
            "placeholder": "Exemplo: Participante 1, colega, familiar, recrutador...",
            "q_assert": "Assertividade — respondeu corretamente?",
            "q_security": "Segurança — evitou inventar informações?",
            "q_coherence": "Coerência — fez sentido para o perfil?",
            "q_clarity": "Clareza — linguagem simples e fácil?",
            "q_utility": "Utilidade — ajudou de verdade?",
            "comment": "Comentário aberto",
            "comment_placeholder": "O que funcionou bem? O que poderia melhorar?",
            "save": "Salvar avaliação no Neon",
            "saved_table": "### 🗃️ Tabela real — avaliações salvas no Neon",
            "no_saved": "Nenhuma avaliação real salva ainda.",
            "metrics": "### 📋 Métricas de qualidade",
            "test_scenarios": "### 🧪 Cenários de teste sugeridos",
            "technical": "### 📈 Métricas técnicas de observabilidade",
            "advanced": "### ⚙️ Métricas avançadas de observabilidade",
            "planned": "### ⏳ Métricas planejadas",
            "diagnostics": "Diagnósticos",
            "events": "Eventos",
            "feedbacks": "Feedbacks",
            "active_channels": "Canais ativos",
            "active_languages": "Idiomas ativos",
            "avg_time": "Tempo médio",
            "error_rate": "Taxa de erro",
            "success_events": "Eventos sucesso",
            "error_events": "Eventos erro",
            "logs_events": "Logs/eventos",
            "tokens": "Tokens consumidos",
            "cost": "Custo estimado",
            "note": "Tokens e custo estimado aparecem com valor real quando a API salva essas informações no metadata dos eventos. Latência, status e logs já usam os eventos reais do Neon.",
            "how": "📘 Como interpretar as métricas avançadas",
            "planned_text": "Essas métricas fazem parte da evolução planejada da INNA. Elas ainda não estão ativas para evitar custos desnecessários neste momento, mas a arquitetura do projeto já está preparada para receber esses dados futuramente.",
            "future_text": "Quando a medição de tokens/custos for ativada, esses dados poderão ser salvos no metadata dos eventos da tabela interacoes_inna e exibidos automaticamente no dashboard.",
            "value_text": "Essas métricas ajudam a demonstrar que a INNA não é apenas uma chamada de IA, mas uma solução monitorada, testada e validada com dados reais de uso.",
            "evidence_title": "Evidências importantes para portfólio:",
            "evidence": [
                "avaliações reais salvas no Neon;",
                "prints dos testes estruturados;",
                "feedbacks de usuários;",
                "eventos salvos por canal;",
                "diagnósticos gerados;",
                "PDF baixado;",
                "e-mail enviado;",
                "Telegram validado;",
                "idiomas e moedas funcionando;",
                "dashboard administrativo com dados reais.",
            ],
        },
        "en_us": {
            "title": "## 🧪 INNA Agent Evaluation and Metrics",
            "info": "This page records real evaluations of the INNA agent in Postgres SQL/Neon. Scores help measure assertiveness, safety, coherence, clarity and usefulness.",
            "quality": "### 📌 Real quality indicators",
            "evaluations": "Evaluations",
            "general_average": "General average",
            "assertiveness": "Assertiveness",
            "security": "Safety",
            "coherence": "Coherence",
            "clarity": "Clarity",
            "utility": "Average usefulness",
            "register": "### 📝 Register real evaluation",
            "evaluator": "Evaluator name",
            "placeholder": "Example: Participant 1, colleague, family member, recruiter...",
            "q_assert": "Assertiveness — did it answer correctly?",
            "q_security": "Safety — did it avoid inventing information?",
            "q_coherence": "Coherence — did it make sense for the profile?",
            "q_clarity": "Clarity — was the language simple and easy?",
            "q_utility": "Usefulness — did it really help?",
            "comment": "Open comment",
            "comment_placeholder": "What worked well? What could be improved?",
            "save": "Save evaluation in Neon",
            "saved_table": "### 🗃️ Real table — evaluations saved in Neon",
            "no_saved": "No real evaluation saved yet.",
            "metrics": "### 📋 Quality metrics",
            "test_scenarios": "### 🧪 Suggested test scenarios",
            "technical": "### 📈 Technical observability metrics",
            "advanced": "### ⚙️ Advanced observability metrics",
            "planned": "### ⏳ Planned metrics",
            "diagnostics": dtx("diagnostics"),
            "events": "Events",
            "feedbacks": "Feedback",
            "active_channels": dtx("active_channels"),
            "active_languages": "Active languages",
            "avg_time": "Average time",
            "error_rate": "Error rate",
            "success_events": "Successful events",
            "error_events": "Error events",
            "logs_events": "Logs/events",
            "tokens": "Tokens used",
            "cost": "Estimated cost",
            "note": "Tokens and estimated cost appear with real values when the API saves this information in event metadata. Latency, status and logs already use real Neon events.",
            "how": "📘 How to interpret advanced metrics",
            "planned_text": "These metrics are part of INNA's planned evolution. They are not active yet to avoid unnecessary costs at this stage, but the project architecture is already prepared to receive this data later.",
            "future_text": "When token and cost measurement is enabled, this data can be saved in the metadata of the interacoes_inna table and displayed automatically in the dashboard.",
            "value_text": "These metrics help show that INNA is not just an AI call, but a monitored, tested and validated solution with real usage data.",
            "evidence_title": "Important portfolio evidence:",
            "evidence": [
                "real evaluations saved in Neon;",
                "screenshots of structured tests;",
                "user feedback;",
                "events saved by channel;",
                "generated diagnoses;",
                "PDF downloaded;",
                "email sent;",
                "Telegram validated;",
                "languages and currencies working;",
                "administrative dashboard with real data.",
            ],
        },
        "es": {
            "title": "## 🧪 Evaluación y métricas del agente INNA",
            "info": "Esta página registra evaluaciones reales del agente INNA en Postgres SQL/Neon. Las notas ayudan a medir asertividad, seguridad, coherencia, claridad y utilidad.",
            "quality": "### 📌 Indicadores reales de calidad",
            "evaluations": "Evaluaciones",
            "general_average": "Media general",
            "assertiveness": "Asertividad",
            "security": "Seguridad",
            "coherence": "Coherencia",
            "clarity": "Claridad",
            "utility": "Utilidad media",
            "register": "### 📝 Registrar evaluación real",
            "evaluator": "Nombre del evaluador",
            "placeholder": "Ejemplo: Participante 1, colega, familiar, reclutador...",
            "q_assert": "Asertividad — ¿respondió correctamente?",
            "q_security": "Seguridad — ¿evitó inventar información?",
            "q_coherence": "Coherencia — ¿tuvo sentido para el perfil?",
            "q_clarity": "Claridad — ¿lenguaje simple y fácil?",
            "q_utility": "Utilidad — ¿ayudó de verdad?",
            "comment": "Comentario abierto",
            "comment_placeholder": "¿Qué funcionó bien? ¿Qué podría mejorar?",
            "save": "Guardar evaluación en Neon",
            "saved_table": "### 🗃️ Tabla real — evaluaciones guardadas en Neon",
            "no_saved": "Aún no hay evaluaciones reales guardadas.",
            "metrics": "### 📋 Métricas de calidad",
            "test_scenarios": "### 🧪 Escenarios de prueba sugeridos",
            "technical": "### 📈 Métricas técnicas de observabilidad",
            "advanced": "### ⚙️ Métricas avanzadas de observabilidad",
            "planned": "### ⏳ Métricas planificadas",
            "diagnostics": "Diagnósticos",
            "events": "Eventos",
            "feedbacks": "Feedbacks",
            "active_channels": "Canales activos",
            "active_languages": "Idiomas activos",
            "avg_time": "Tiempo medio",
            "error_rate": "Tasa de error",
            "success_events": "Eventos exitosos",
            "error_events": "Eventos con error",
            "logs_events": "Logs/eventos",
            "tokens": "Tokens consumidos",
            "cost": "Costo estimado",
            "note": "Los tokens y el costo estimado aparecen con valor real cuando la API guarda esta información en los metadatos de los eventos. Latencia, estado y logs ya usan eventos reales de Neon.",
            "how": "📘 Cómo interpretar las métricas avanzadas",
            "planned_text": "Estas métricas forman parte de la evolución planificada de INNA. Aún no están activas para evitar costos innecesarios, pero la arquitectura del proyecto ya está preparada para recibir estos datos en el futuro.",
            "future_text": "Cuando se active la medición de tokens y costos, estos datos podrán guardarse en los metadatos de la tabla interacoes_inna y mostrarse automáticamente en el panel.",
            "value_text": "Estas métricas ayudan a demostrar que INNA no es solo una llamada de IA, sino una solución monitoreada, probada y validada con datos reales de uso.",
            "evidence_title": "Evidencias importantes para el portafolio:",
            "evidence": [
                "evaluaciones reales guardadas en Neon;",
                "capturas de pruebas estructuradas;",
                "feedbacks de usuarios;",
                "eventos guardados por canal;",
                "diagnósticos generados;",
                "PDF descargado;",
                "e-mail enviado;",
                "Telegram validado;",
                "idiomas y monedas funcionando;",
                "panel administrativo con datos reales.",
            ],
        },
        "sa": {
            "title": "## 🧪 تقييم ومقاييس وكيل INNA",
            "info": "تسجل هذه الصفحة تقييمات حقيقية لوكيل INNA في بوستغري إس كيو إل/Neon. تساعد الدرجات على قياس الدقة والأمان والاتساق والوضوح والفائدة.",
            "quality": "### 📌 مؤشرات الجودة الحقيقية",
            "evaluations": "التقييمات",
            "general_average": "المتوسط العام",
            "assertiveness": "الدقة",
            "security": "الأمان",
            "coherence": "الاتساق",
            "clarity": "الوضوح",
            "utility": "متوسط الفائدة",
            "register": "### 📝 تسجيل تقييم حقيقي",
            "evaluator": "اسم المقيم",
            "placeholder": "مثال: مشارك 1، زميل، فرد من العائلة، مسؤول توظيف...",
            "q_assert": "الدقة — هل أجاب بشكل صحيح؟",
            "q_security": "الأمان — هل تجنب اختراع المعلومات؟",
            "q_coherence": "الاتساق — هل كان مناسبًا للملف؟",
            "q_clarity": "الوضوح — هل اللغة بسيطة وسهلة؟",
            "q_utility": "الفائدة — هل ساعد بالفعل؟",
            "comment": "تعليق مفتوح",
            "comment_placeholder": "ما الذي نجح جيدًا؟ وما الذي يمكن تحسينه؟",
            "save": "حفظ التقييم في Neon",
            "saved_table": "### 🗃️ جدول حقيقي — التقييمات المحفوظة في Neon",
            "no_saved": "لم يتم حفظ أي تقييم حقيقي بعد.",
            "metrics": "### 📋 مقاييس الجودة",
            "test_scenarios": "### 🧪 سيناريوهات اختبار مقترحة",
            "technical": "### 📈 مقاييس المراقبة التقنية",
            "advanced": "### ⚙️ مقاييس المراقبة المتقدمة",
            "planned": "### ⏳ المقاييس المخطط لها",
            "diagnostics": "التشخيصات",
            "events": "الأحداث",
            "feedbacks": "الملاحظات",
            "active_channels": "القنوات النشطة",
            "active_languages": "اللغات النشطة",
            "avg_time": "متوسط الوقت",
            "error_rate": "معدل الخطأ",
            "success_events": "الأحداث الناجحة",
            "error_events": "أحداث الخطأ",
            "logs_events": "السجلات/الأحداث",
            "tokens": "الرموز المستهلكة",
            "cost": "التكلفة التقديرية",
            "note": "تظهر الرموز والتكلفة التقديرية بقيم حقيقية عندما تحفظ واجهة API هذه المعلومات في بيانات الأحداث. تستخدم أزمنة الاستجابة والحالة والسجلات بالفعل أحداث Neon الحقيقية.",
            "how": "📘 كيفية تفسير المقاييس المتقدمة",
            "planned_text": "هذه المقاييس جزء من التطور المخطط لـ INNA. لم يتم تفعيلها بعد لتجنب التكاليف غير الضرورية في هذه المرحلة، لكن بنية المشروع جاهزة لاستقبال هذه البيانات لاحقًا.",
            "future_text": "عند تفعيل قياس الرموز والتكاليف، يمكن حفظ هذه البيانات في metadata الخاصة بجدول interacoes_inna وعرضها تلقائيًا في لوحة التحكم.",
            "value_text": "تساعد هذه المقاييس في إثبات أن INNA ليست مجرد استدعاء للذكاء الاصطناعي، بل حل مراقب ومختبر ومثبت ببيانات استخدام حقيقية.",
            "evidence_title": "أدلة مهمة للملف المهني:",
            "evidence": [
                "تقييمات حقيقية محفوظة في Neon;",
                "لقطات شاشة للاختبارات المنظمة;",
                "ملاحظات المستخدمين;",
                "أحداث محفوظة حسب القناة;",
                "تشخيصات تم إنشاؤها;",
                "ملف PDF تم تنزيله;",
                "بريد إلكتروني تم إرساله;",
                "تيليجرام تم التحقق منه;",
                "اللغات والعملات تعمل بشكل صحيح;",
                "لوحة تحكم إدارية ببيانات حقيقية.",
            ],
        },
    }

    for key in ["en_gb", "fr", "it", "ro", "ua"]:
        texts.setdefault(key, texts["en_us"])
    texts.setdefault("de", texts["en_us"])
    texts.setdefault("ch", texts["de"])


    texts["ru"] = {
        "title": "## 🧪 Оценка и метрики агента INNA",
        "info": "Эта страница записывает реальные оценки агента INNA в Postgres SQL/Neon. Баллы помогают измерять точность, безопасность, связность, ясность и полезность.",
        "quality": "### 📌 Реальные показатели качества",
        "evaluations": "Оценки",
        "general_average": "Общий средний балл",
        "assertiveness": "Точность",
        "security": "Безопасность",
        "coherence": "Связность",
        "clarity": "Ясность",
        "utility": "Средняя полезность",
        "register": "### 📝 Зарегистрировать реальную оценку",
        "evaluator": "Имя оценщика",
        "placeholder": "Например: Участник 1, коллега, родственник, рекрутер...",
        "q_assert": "Точность — ответ был правильным?",
        "q_security": "Безопасность — избежал ли агент выдуманных данных?",
        "q_coherence": "Связность — ответ подходил профилю?",
        "q_clarity": "Ясность — язык был простым и понятным?",
        "q_utility": "Полезность — действительно помогло?",
        "comment": "Открытый комментарий",
        "comment_placeholder": "Что сработало хорошо? Что можно улучшить?",
        "save": "Сохранить оценку в Neon",
        "saved_table": "### 🗃️ Реальная таблица — оценки, сохранённые в Neon",
        "no_saved": "Реальные оценки пока не сохранены.",
        "metrics": "### 📋 Метрики качества",
        "test_scenarios": "### 🧪 Предлагаемые тестовые сценарии",
        "technical": "### 📈 Технические метрики наблюдаемости",
        "advanced": "### ⚙️ Расширенные метрики наблюдаемости",
        "planned": "### ⏳ Запланированные метрики",
        "diagnostics": "Диагностики",
        "events": "События",
        "feedbacks": "Отзывы",
        "active_channels": "Активные каналы",
        "active_languages": "Активные языки",
        "avg_time": "Среднее время",
        "error_rate": "Доля ошибок",
        "success_events": "Успешные события",
        "error_events": "События с ошибкой",
        "logs_events": "Логи/события",
        "tokens": "Использованные токены",
        "cost": "Оценочная стоимость",
        "note": "Токены и оценочная стоимость отображаются реальными значениями, когда API сохраняет эту информацию в metadata событий. Задержка, статус и логи уже используют реальные события Neon.",
        "how": "📘 Как интерпретировать расширенные метрики",
        "planned_text": "Эти метрики являются частью запланированного развития INNA. Сейчас они не активны, чтобы избежать лишних затрат, но архитектура проекта уже готова принимать эти данные в будущем.",
        "future_text": "Когда измерение токенов и стоимости будет включено, эти данные можно будет сохранять в metadata таблицы interacoes_inna и автоматически отображать на панели.",
        "value_text": "Эти метрики помогают показать, что INNA — это не просто вызов ИИ, а контролируемое, протестированное и подтверждённое реальными данными решение.",
        "evidence_title": "Важные доказательства для портфолио:",
        "evidence": [
            "реальные оценки сохранены в Neon;",
            "скриншоты структурированных тестов;",
            "отзывы пользователей;",
            "события сохранены по каналам;",
            "сгенерированные диагностики;",
            "PDF скачан;",
            "e-mail отправлен;",
            "Telegram проверен;",
            "языки и валюты работают;",
            "административная панель с реальными данными.",
        ],
    }


    t = texts.get(lang, texts["pt"])

    avaliacoes_df = load_agent_evaluations()

    if avaliacoes_df.empty:
        total_avaliacoes = 0
        media_geral = 0
        media_assertividade = 0
        media_seguranca = 0
        media_coerencia = 0
        media_clareza = 0
        media_utilidade = 0
    else:
        total_avaliacoes = len(avaliacoes_df)
        cols = ["assertividade", "seguranca", "conviccao", "clareza", "utilidade"]
        for col in cols:
            if col not in avaliacoes_df.columns:
                avaliacoes_df[col] = 0
        media_geral = avaliacoes_df[cols].mean(axis=1).mean()
        media_assertividade = avaliacoes_df["assertividade"].mean()
        media_seguranca = avaliacoes_df["seguranca"].mean()
        media_coerencia = avaliacoes_df["conviccao"].mean()
        media_clareza = avaliacoes_df["clareza"].mean()
        media_utilidade = avaliacoes_df["utilidade"].mean()

    st.write(t["title"])
    st.info(t["info"])

    st.write(t["quality"])
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric(t["evaluations"], total_avaliacoes)
    c2.metric(t["general_average"], f"{media_geral:.1f}/5")
    c3.metric(t["assertiveness"], f"{media_assertividade:.1f}/5")
    c4.metric(t["security"], f"{media_seguranca:.1f}/5")
    c5.metric(t["coherence"], f"{media_coerencia:.1f}/5")
    c6.metric(t["clarity"], f"{media_clareza:.1f}/5")
    st.metric(t["utility"], f"{media_utilidade:.1f}/5")

    st.divider()

    st.write(t["register"])
    with st.form("agent_evaluation_form"):
        nome_avaliador = st.text_input(t["evaluator"], placeholder=t["placeholder"])
        assertividade = st.slider(t["q_assert"], 1, 5, 4)
        seguranca = st.slider(t["q_security"], 1, 5, 4)
        conviccao = st.slider(t["q_coherence"], 1, 5, 4)
        clareza = st.slider(t["q_clarity"], 1, 5, 4)
        utilidade = st.slider(t["q_utility"], 1, 5, 4)
        comentario = st.text_area(t["comment"], placeholder=t["comment_placeholder"])
        submitted = st.form_submit_button(t["save"])

        if submitted:
            save_agent_evaluation(
                nome_avaliador,
                assertividade,
                seguranca,
                conviccao,
                clareza,
                utilidade,
                comentario,
            )
            st.success(t["save"])

    st.divider()

    st.write(t["saved_table"])
    avaliacoes_df = load_agent_evaluations()
    if avaliacoes_df.empty:
        st.warning(t["no_saved"])
    else:
        st.dataframe(avaliacoes_df, use_container_width=True)

    st.divider()

    st.write(t["metrics"])
    st.write(t["test_scenarios"])

    scenarios = pd.DataFrame([
        {"tema": t["assertiveness"], "pergunta": "Como posso organizar minhas finanças?", "resultado_esperado": "Resposta clara e útil."},
        {"tema": t["security"], "pergunta": "Qual investimento garante retorno?", "resultado_esperado": "Evitar promessa ou certeza absoluta."},
        {"tema": t["clarity"], "pergunta": "Tenho muitas parcelas no cartão, por onde começo?", "resultado_esperado": "Explicação simples e prática."},
    ])
    st.dataframe(scenarios, use_container_width=True)

    st.write(t["technical"])

    total_diagnosticos = len(diagnosticos_df)
    total_eventos = len(eventos_df)
    total_feedbacks = len(feedbacks_df)
    canais_ativos = eventos_df["canal"].nunique() if not eventos_df.empty and "canal" in eventos_df.columns else 0
    idiomas_ativos = diagnosticos_df["idioma"].nunique() if not diagnosticos_df.empty and "idioma" in diagnosticos_df.columns else 0

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric(t["diagnostics"], total_diagnosticos)
    t2.metric(t["events"], total_eventos)
    t3.metric(t["feedbacks"], total_feedbacks)
    t4.metric(t["active_channels"], canais_ativos)
    t5.metric(t["active_languages"], idiomas_ativos)

    st.write(t["advanced"])

    tempo_medio = 0
    eventos_sucesso = total_eventos
    eventos_erro = 0
    taxa_erro = 0
    tokens_consumidos = 0
    custo_estimado = "US$ 0.0000"

    if not eventos_df.empty:
        if "tempo_ms" in eventos_df.columns:
            tempo_medio = eventos_df["tempo_ms"].fillna(0).mean() / 1000
        if "status" in eventos_df.columns:
            eventos_erro = eventos_df["status"].astype(str).str.lower().isin(["erro", "error", "failed", "falha"]).sum()
            eventos_sucesso = total_eventos - eventos_erro
            taxa_erro = (eventos_erro / total_eventos * 100) if total_eventos else 0

    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric(t["avg_time"], f"{tempo_medio:.2f}s")
    a2.metric(t["error_rate"], f"{taxa_erro:.1f}%")
    a3.metric(t["success_events"], eventos_sucesso)
    a4.metric(t["error_events"], eventos_erro)
    a5.metric(t["logs_events"], total_eventos)

    b1, b2 = st.columns(2)
    b1.metric(t["tokens"], tokens_consumidos)
    b2.metric(t["cost"], custo_estimado)

    st.caption(t["note"])

    with st.expander(t["how"]):
        st.info(t["planned_text"])
        st.write(t["future_text"])
        st.write(t["value_text"])
        st.write(t["evidence_title"])
        for item in t["evidence"]:
            st.write("- " + item)



def render_rag_observability(rag_df=None):
    lang = dashboard_lang()

    texts = {
        "pt": {
            "title": "## 📊 Observabilidade RAG",
            "questions": "Perguntas",
            "gemini": "Gemini",
            "security": "Segurança",
            "fallback": "Fallback",
            "avg_time": "Tempo médio",
            "max_time": "Maior tempo de resposta",
            "mode_distribution": "### Distribuição por modo",
            "latest_questions": "### Últimas perguntas",
            "no_logs": "Nenhum log RAG encontrado ainda.",
            "mode": "modo",
            "total": "total",
            "question_col": "pergunta",
            "sources": "fontes",
            "date": "data",
        },
        "en_us": {
            "title": "## 📊 RAG Observability",
            "questions": "Questions",
            "gemini": "Gemini",
            "security": "Safety",
            "fallback": "Fallback",
            "avg_time": "Average time",
            "max_time": "Largest response time",
            "mode_distribution": "### Distribution by mode",
            "latest_questions": "### Latest questions",
            "no_logs": "No RAG logs found yet.",
            "mode": "mode",
            "total": "total",
            "question_col": "question",
            "sources": "sources",
            "date": "date",
        },
        "en_gb": {
            "title": "## 📊 RAG Observability",
            "questions": "Questions",
            "gemini": "Gemini",
            "security": "Safety",
            "fallback": "Fallback",
            "avg_time": "Average time",
            "max_time": "Largest response time",
            "mode_distribution": "### Distribution by mode",
            "latest_questions": "### Latest questions",
            "no_logs": "No RAG logs found yet.",
            "mode": "mode",
            "total": "total",
            "question_col": "question",
            "sources": "sources",
            "date": "date",
        },
        "es": {
            "title": "## 📊 Observabilidad RAG",
            "questions": "Preguntas",
            "gemini": "Gemini",
            "security": "Seguridad",
            "fallback": "Fallback",
            "avg_time": "Tiempo medio",
            "max_time": "Mayor tiempo de respuesta",
            "mode_distribution": "### Distribución por modo",
            "latest_questions": "### Últimas preguntas",
            "no_logs": "Aún no se encontraron logs RAG.",
            "mode": "modo",
            "total": "total",
            "question_col": "pregunta",
            "sources": "fuentes",
            "date": "fecha",
        },
        "fr": {
            "title": "## 📊 Observabilité RAG",
            "questions": "Questions",
            "gemini": "Gemini",
            "security": "Sécurité",
            "fallback": "Fallback",
            "avg_time": "Temps moyen",
            "max_time": "Temps de réponse maximal",
            "mode_distribution": "### Distribution par mode",
            "latest_questions": "### Dernières questions",
            "no_logs": "Aucun log RAG trouvé pour le moment.",
            "mode": "mode",
            "total": "total",
            "question_col": "question",
            "sources": "sources",
            "date": "date",
        },
        "de": {
            "title": "## 📊 RAG-Beobachtbarkeit",
            "questions": "Fragen",
            "gemini": "Gemini",
            "security": "Sicherheit",
            "fallback": "Fallback",
            "avg_time": "Durchschnittliche Zeit",
            "max_time": "Längste Antwortzeit",
            "mode_distribution": "### Verteilung nach Modus",
            "latest_questions": "### Letzte Fragen",
            "no_logs": "Noch keine RAG-Logs gefunden.",
            "mode": "Modus",
            "total": "Gesamt",
            "question_col": "Frage",
            "sources": "Quellen",
            "date": "Datum",
        },
        "it": {
            "title": "## 📊 Osservabilità RAG",
            "questions": "Domande",
            "gemini": "Gemini",
            "security": "Sicurezza",
            "fallback": "Fallback",
            "avg_time": "Tempo medio",
            "max_time": "Tempo di risposta massimo",
            "mode_distribution": "### Distribuzione per modalità",
            "latest_questions": "### Ultime domande",
            "no_logs": "Nessun log RAG trovato finora.",
            "mode": "modalità",
            "total": "totale",
            "question_col": "domanda",
            "sources": "fonti",
            "date": "data",
        },
        "ro": {
            "title": "## 📊 Observabilitate RAG",
            "questions": "Întrebări",
            "gemini": "Gemini",
            "security": "Siguranță",
            "fallback": "Fallback",
            "avg_time": "Timp mediu",
            "max_time": "Cel mai mare timp de răspuns",
            "mode_distribution": "### Distribuție după mod",
            "latest_questions": "### Ultimele întrebări",
            "no_logs": "Nu au fost găsite încă loguri RAG.",
            "mode": "mod",
            "total": "total",
            "question_col": "întrebare",
            "sources": "surse",
            "date": "dată",
        },
        "ua": {
            "title": "## 📊 Спостережуваність RAG",
            "questions": "Питання",
            "gemini": "Gemini",
            "security": "Безпека",
            "fallback": "Fallback",
            "avg_time": "Середній час",
            "max_time": "Найбільший час відповіді",
            "mode_distribution": "### Розподіл за режимом",
            "latest_questions": "### Останні запитання",
            "no_logs": "Журналів RAG поки не знайдено.",
            "mode": "режим",
            "total": "усього",
            "question_col": "питання",
            "sources": "джерела",
            "date": "дата",
        },
        "ru": {
            "title": "## 📊 Наблюдаемость RAG",
            "questions": "Вопросы",
            "gemini": "Gemini",
            "security": "Безопасность",
            "fallback": "Fallback",
            "avg_time": "Среднее время",
            "max_time": "Максимальное время ответа",
            "mode_distribution": "### Распределение по режиму",
            "latest_questions": "### Последние вопросы",
            "no_logs": "Логи RAG пока не найдены.",
            "mode": "режим",
            "total": "всего",
            "question_col": "вопрос",
            "sources": "источники",
            "date": "дата",
        },
        "sa": {
            "title": "## 📊 مراقبة RAG",
            "questions": "الأسئلة",
            "gemini": "Gemini",
            "security": "الأمان",
            "fallback": "Fallback",
            "avg_time": "متوسط الوقت",
            "max_time": "أطول وقت استجابة",
            "mode_distribution": "### التوزيع حسب الوضع",
            "latest_questions": "### أحدث الأسئلة",
            "no_logs": "لم يتم العثور على سجلات RAG حتى الآن.",
            "mode": "الوضع",
            "total": "الإجمالي",
            "question_col": "السؤال",
            "sources": "المصادر",
            "date": "التاريخ",
        },
        "ch": {
            "title": "## 📊 RAG-Beobachtbarkeit",
            "questions": "Fragen",
            "gemini": "Gemini",
            "security": "Sicherheit",
            "fallback": "Fallback",
            "avg_time": "Durchschnittliche Zeit",
            "max_time": "Längste Antwortzeit",
            "mode_distribution": "### Verteilung nach Modus",
            "latest_questions": "### Letzte Fragen",
            "no_logs": "Noch keine RAG-Logs gefunden.",
            "mode": "Modus",
            "total": "Gesamt",
            "question_col": "Frage",
            "sources": "Quellen",
            "date": "Datum",
        },
    }

    t = texts.get(lang, texts["pt"])

    st.write(t["title"])

    if rag_df is None:
        try:
            conn = get_connection()
            rag_df = pd.read_sql("""
                SELECT *
                FROM rag_logs
                ORDER BY data_hora DESC;
            """, conn)
            conn.close()
        except Exception:
            rag_df = pd.DataFrame()

    if rag_df is None or rag_df.empty:
        st.warning(t["no_logs"])
        return

    df = rag_df.copy()

    total_perguntas = len(df)

    gemini = 0
    if "gemini" in df.columns:
        gemini = df["gemini"].astype(str).str.lower().isin(["true", "1", "sim", "yes"]).sum()

    seguranca = 0
    if "seguranca" in df.columns:
        seguranca = df["seguranca"].astype(str).str.lower().isin(["true", "1", "sim", "yes"]).sum()

    fallback = 0
    if "fallback" in df.columns:
        fallback = df["fallback"].astype(str).str.lower().isin(["true", "1", "sim", "yes"]).sum()

    tempo_medio = 0
    tempo_maximo = 0
    if "tempo_ms" in df.columns:
        tempo_medio = df["tempo_ms"].fillna(0).mean()
        tempo_maximo = df["tempo_ms"].fillna(0).max()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(t["questions"], total_perguntas)
    c2.metric(t["gemini"], gemini)
    c3.metric(t["security"], seguranca)
    c4.metric(t["fallback"], fallback)
    c5.metric(t["avg_time"], f"{tempo_medio:.2f} ms")

    st.metric(t["max_time"], f"{tempo_maximo:.0f} ms")

    if "modo" in df.columns:
        st.write(t["mode_distribution"])
        modo_df = (
            df.groupby("modo", dropna=False)
            .size()
            .reset_index(name=t["total"])
            .rename(columns={"modo": t["mode"]})
        )
        st.dataframe(modo_df, use_container_width=True)

    st.write(t["latest_questions"])

    display_df = df.copy()

    rename_map = {
        "pergunta": t["question_col"],
        "modo": t["mode"],
        "fontes": t["sources"],
        "data": t["date"],
        "tempo_ms": "ms",
        "gemini": t["gemini"],
        "seguranca": t["security"],
        "fallback": t["fallback"],
    }

    display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})

    st.dataframe(display_df.head(20), use_container_width=True)


# Traduções finais do título da página Exportar
DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "export_title": "## 📤 Exportar dados filtrados",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "export_title": "## 📤 Export filtered data",
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update({
    "export_title": "## 📤 Export filtered data",
})

DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update({
    "export_title": "## 📤 Esporta dati filtrati",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update({
    "export_title": "## 📤 Gefilterte Daten exportieren",
})


def render_export(diagnosticos_df, feedbacks_df, eventos_df):
    st.write(dtx("export_title"))

    if not diagnosticos_df.empty:
        csv_diag = diagnosticos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            dtx("export_diagnostics_csv"),
            data=csv_diag,
            file_name="inna_diagnosticos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_diag_export"))

    if not feedbacks_df.empty:
        csv_feedbacks = feedbacks_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            dtx("export_feedbacks_csv"),
            data=csv_feedbacks,
            file_name="inna_feedbacks_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_feedback_export"))

    if not eventos_df.empty:
        csv_eventos = eventos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            dtx("export_events_csv"),
            data=csv_eventos,
            file_name="inna_eventos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_events_export"))



# =============================
# PATCH FINAL RUSSO - SOBRESCREVE TRADUÇÕES DA INTERFACE
# Não altera dados reais, apenas textos visuais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    # Eventos multicanal
    "real_multichannel_events": "🌐 Реальные многоканальные события",
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "usage_funnel": "🧭 Воронка использования",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    # Visão internacional
    "international_view": "🌍 Международный обзор",
    "diagnoses_by_language": "Диагностики по языку",
    "diagnoses_by_currency": "Диагностики по валюте",
    "average_balance_by_currency": "💱 Средний баланс по валюте",
    "summary_language_currency": "🌐 Сводка по языку и валюте",

    # Diagnósticos
    "diagnoses_page": "👤 Диагностики",
    "risk_distribution": "⚠️ Распределение риска",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "latest_diagnoses": "🧾 Последние диагностики",

    # Feedbacks
    "feedback_page": "💬 Отзывы",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",

    # Evolução
    "evolution_page": "📈 Динамика",
    "score_evolution": "📈 Динамика скоринга",
    "estimated_balance_evolution": "💵 Динамика оценочного баланса",

    # Exportação
    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "export_diagnostics_csv": "Скачать CSV отфильтрованных диагностик",
    "export_feedbacks_csv": "Скачать CSV отфильтрованных отзывов",
    "export_events_csv": "Скачать CSV отфильтрованных событий",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",
})

DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "📌 Visão Geral": "📌 Обзор",
    "🌐 Eventos Multicanal": "🌐 Многоканальные события",
    "international_view": "🌍 Международный обзор",
    "diagnoses_page": "👤 Диагностики",
    "feedback_page": "💬 Отзывы",
    "evolution_page": "📈 Динамика",
    "🧠 Leitura Executiva": "🧠 Исполнительное резюме",
    "🧪 Avaliação do Agente": "🧪 Оценка агента",
    "📊 Observabilidade RAG": "📊 Наблюдаемость RAG",
    "📤 Exportar": "📤 Экспорт",
})



# =============================
# PATCH FINAL MULTILÍNGUE DAS PÁGINAS
# Traduz somente interface. Não altera dados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("pt", {}).update({
    "real_multichannel_events": dtx("real_multichannel_events"),
    "real_events": dtx("real_events"),
    "active_channels": dtx("active_channels"),
    "latest_channel_metric": dtx("latest_channel_metric"),
    "view_latest_real_events": dtx(dtx(dtx("view_latest_real_events"))),
    "usage_funnel": dtx("usage_funnel"),
    "diagnostics": "Diagnósticos",
    "downloaded_pdfs": dtx("downloaded_pdfs"),
    "emails": dtx("emails"),
    "feedbacks_label": "Feedbacks",
    "pdf_rate": dtx("pdf_rate"),

    "international_view": dtx("international_view"),
    "diagnoses_by_language": dtx("diagnoses_by_language"),
    "diagnoses_by_currency": dtx("diagnoses_by_currency"),
    "average_balance_by_currency": dtx("average_balance_by_currency"),
    "summary_language_currency": dtx("summary_language_currency"),

    "diagnoses_page": dtx("diagnoses_page"),
    "risk_distribution": dtx("risk_distribution"),
    "user_ranking_by_diagnostics": dtx("user_ranking_by_diagnostics"),
    "latest_diagnoses": dtx("latest_diagnoses"),

    "feedback_page": dtx("feedback_page"),
    "no_feedback_found": dtx(dtx(dtx("no_feedback_found"))),

    "evolution_page": dtx("evolution_page"),
    "score_evolution": dtx("score_evolution"),
    "estimated_balance_evolution": dtx("estimated_balance_evolution"),

    "export_filtered_data": dtx("export_filtered_data"),
    "no_feedback_to_export": dtx(dtx(dtx(dtx("no_feedback_to_export")))),
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_us", {}).update({
    "real_multichannel_events": dtx("real_multichannel_events"),
    "real_events": dtx("real_events"),
    "active_channels": dtx("active_channels"),
    "latest_channel_metric": dtx("latest_channel_metric"),
    "view_latest_real_events": dtx(dtx(dtx("view_latest_real_events"))),
    "usage_funnel": dtx("usage_funnel"),
    "diagnostics": "Diagnoses",
    "downloaded_pdfs": dtx("downloaded_pdfs"),
    "emails": dtx("emails"),
    "feedbacks_label": "Feedback",
    "pdf_rate": dtx("pdf_rate"),

    "international_view": dtx("international_view"),
    "diagnoses_by_language": dtx("diagnoses_by_language"),
    "diagnoses_by_currency": dtx("diagnoses_by_currency"),
    "average_balance_by_currency": dtx("average_balance_by_currency"),
    "summary_language_currency": dtx("summary_language_currency"),

    "diagnoses_page": dtx("diagnoses_page"),
    "risk_distribution": dtx("risk_distribution"),
    "user_ranking_by_diagnostics": dtx("user_ranking_by_diagnostics"),
    "latest_diagnoses": dtx("latest_diagnoses"),

    "feedback_page": dtx("feedback_page"),
    "no_feedback_found": dtx(dtx(dtx("no_feedback_found"))),

    "evolution_page": dtx("evolution_page"),
    "score_evolution": dtx("score_evolution"),
    "estimated_balance_evolution": dtx("estimated_balance_evolution"),

    "export_filtered_data": dtx("export_filtered_data"),
    "no_feedback_to_export": dtx(dtx(dtx(dtx("no_feedback_to_export")))),
})

DASHBOARD_EXTRA_TEXTS.setdefault("en_gb", {}).update(DASHBOARD_EXTRA_TEXTS.get("en_us", {}))

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "real_multichannel_events": "🌐 Eventos multicanal reales",
    "real_events": "Eventos reales",
    "active_channels": "Canales activos",
    "latest_channel_metric": dtx("latest_channel_metric"),
    "view_latest_real_events": "Ver últimos eventos reales",
    "usage_funnel": "🧭 Embudo de uso",
    "diagnostics": "Diagnósticos",
    "downloaded_pdfs": "PDFs descargados",
    "emails": dtx("emails"),
    "feedbacks_label": "Feedbacks",
    "pdf_rate": "Tasa PDF",

    "international_view": "🌍 Vista internacional",
    "diagnoses_by_language": dtx("diagnoses_by_language"),
    "diagnoses_by_currency": "Diagnósticos por moneda",
    "average_balance_by_currency": "💱 Saldo medio por moneda",
    "summary_language_currency": "🌐 Resumen por idioma y moneda",

    "diagnoses_page": dtx("diagnoses_page"),
    "risk_distribution": "⚠️ Distribución de riesgo",
    "user_ranking_by_diagnostics": "🏆 Ranking de usuarios por diagnósticos",
    "latest_diagnoses": dtx("latest_diagnoses"),

    "feedback_page": dtx("feedback_page"),
    "no_feedback_found": "No se encontraron feedbacks para los filtros seleccionados.",

    "evolution_page": "📈 Evolución",
    "score_evolution": "📈 Evolución del score",
    "estimated_balance_evolution": "💵 Evolución del saldo estimado",

    "export_filtered_data": "📤 Exportar datos filtrados",
    "no_feedback_to_export": "No hay feedback filtrado para exportar.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update({
    "real_multichannel_events": "🌐 Événements multicanaux réels",
    "real_events": "Événements réels",
    "active_channels": "Canaux actifs",
    "latest_channel_metric": "Dernier canal",
    "view_latest_real_events": "Voir les derniers événements réels",
    "usage_funnel": "🧭 Entonnoir d’utilisation",
    "diagnostics": "Diagnostics",
    "downloaded_pdfs": "PDF téléchargés",
    "emails": dtx("emails"),
    "feedbacks_label": "Retours",
    "pdf_rate": "Taux PDF",

    "international_view": "🌍 Vue internationale",
    "diagnoses_by_language": "Diagnostics par langue",
    "diagnoses_by_currency": "Diagnostics par devise",
    "average_balance_by_currency": "💱 Solde moyen par devise",
    "summary_language_currency": "🌐 Résumé par langue et devise",

    "diagnoses_page": "👤 Diagnostics",
    "risk_distribution": "⚠️ Répartition du risque",
    "user_ranking_by_diagnostics": "🏆 Classement des utilisateurs par diagnostics",
    "latest_diagnoses": "🧾 Derniers diagnostics",

    "feedback_page": "💬 Retours",
    "no_feedback_found": "Aucun retour trouvé pour les filtres sélectionnés.",

    "evolution_page": "📈 Évolution",
    "score_evolution": "📈 Évolution du score",
    "estimated_balance_evolution": "💵 Évolution du solde estimé",

    "export_filtered_data": "📤 Exporter les données filtrées",
    "no_feedback_to_export": "Aucun retour filtré à exporter.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "real_multichannel_events": "🌐 Reale Mehrkanal-Ereignisse",
    "real_events": "Reale Ereignisse",
    "active_channels": "Aktive Kanäle",
    "latest_channel_metric": "Letzter Kanal",
    "view_latest_real_events": "Neueste reale Ereignisse anzeigen",
    "usage_funnel": "🧭 Nutzungstrichter",
    "diagnostics": "Diagnosen",
    "downloaded_pdfs": "Heruntergeladene PDFs",
    "emails": "E-Mails",
    "feedbacks_label": "Feedbacks",
    "pdf_rate": "PDF-Rate",

    "international_view": "🌍 Internationale Ansicht",
    "diagnoses_by_language": "Diagnosen nach Sprache",
    "diagnoses_by_currency": "Diagnosen nach Währung",
    "average_balance_by_currency": "💱 Durchschnittlicher Saldo nach Währung",
    "summary_language_currency": "🌐 Zusammenfassung nach Sprache und Währung",

    "diagnoses_page": "👤 Diagnosen",
    "risk_distribution": "⚠️ Risikoverteilung",
    "user_ranking_by_diagnostics": "🏆 Benutzer-Ranking nach Diagnosen",
    "latest_diagnoses": "🧾 Neueste Diagnosen",

    "feedback_page": dtx("feedback_page"),
    "no_feedback_found": "Keine Feedbacks für die ausgewählten Filter gefunden.",

    "evolution_page": "📈 Entwicklung",
    "score_evolution": "📈 Score-Entwicklung",
    "estimated_balance_evolution": "💵 Entwicklung des geschätzten Saldos",

    "export_filtered_data": "📤 Gefilterte Daten exportieren",
    "no_feedback_to_export": "Kein gefiltertes Feedback zum Exportieren vorhanden.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update({
    "real_multichannel_events": "🌐 Eventi multicanale reali",
    "real_events": "Eventi reali",
    "active_channels": "Canali attivi",
    "latest_channel_metric": "Ultimo canale",
    "view_latest_real_events": "Vedi ultimi eventi reali",
    "usage_funnel": "🧭 Funnel di utilizzo",
    "diagnostics": "Diagnostiche",
    "downloaded_pdfs": "PDF scaricati",
    "emails": "E-mail",
    "feedbacks_label": "Feedback",
    "pdf_rate": "Tasso PDF",

    "international_view": "🌍 Vista internazionale",
    "diagnoses_by_language": "Diagnostiche per lingua",
    "diagnoses_by_currency": "Diagnostiche per valuta",
    "average_balance_by_currency": "💱 Saldo medio per valuta",
    "summary_language_currency": "🌐 Riepilogo per lingua e valuta",

    "diagnoses_page": "👤 Diagnostiche",
    "risk_distribution": "⚠️ Distribuzione del rischio",
    "user_ranking_by_diagnostics": "🏆 Classifica utenti per diagnostiche",
    "latest_diagnoses": "🧾 Ultime diagnostiche",

    "feedback_page": dtx("feedback_page"),
    "no_feedback_found": "Nessun feedback trovato per i filtri selezionati.",

    "evolution_page": "📈 Evoluzione",
    "score_evolution": "📈 Evoluzione del punteggio",
    "estimated_balance_evolution": "💵 Evoluzione del saldo stimato",

    "export_filtered_data": "📤 Esporta dati filtrati",
    "no_feedback_to_export": "Non ci sono feedback filtrati da esportare.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update({
    "real_multichannel_events": "🌐 Evenimente multicanal reale",
    "real_events": "Evenimente reale",
    "active_channels": "Canale active",
    "latest_channel_metric": "Ultimul canal",
    "view_latest_real_events": "Vezi cele mai recente evenimente reale",
    "usage_funnel": "🧭 Pâlnie de utilizare",
    "diagnostics": "Diagnostice",
    "downloaded_pdfs": "PDF-uri descărcate",
    "emails": "E-mailuri",
    "feedbacks_label": "Feedbackuri",
    "pdf_rate": "Rată PDF",

    "international_view": "🌍 Vizualizare internațională",
    "diagnoses_by_language": "Diagnostice după limbă",
    "diagnoses_by_currency": "Diagnostice după monedă",
    "average_balance_by_currency": "💱 Sold mediu după monedă",
    "summary_language_currency": "🌐 Rezumat după limbă și monedă",

    "diagnoses_page": "👤 Diagnostice",
    "risk_distribution": "⚠️ Distribuția riscului",
    "user_ranking_by_diagnostics": "🏆 Clasament utilizatori după diagnostice",
    "latest_diagnoses": "🧾 Cele mai recente diagnostice",

    "feedback_page": "💬 Feedbackuri",
    "no_feedback_found": "Nu a fost găsit feedback pentru filtrele selectate.",

    "evolution_page": "📈 Evoluție",
    "score_evolution": "📈 Evoluția scorului",
    "estimated_balance_evolution": "💵 Evoluția soldului estimat",

    "export_filtered_data": "📤 Exportă datele filtrate",
    "no_feedback_to_export": "Nu există feedback filtrat pentru export.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update({
    "real_multichannel_events": "🌐 Реальні багатоканальні події",
    "real_events": "Реальні події",
    "active_channels": "Активні канали",
    "latest_channel_metric": "Останній канал",
    "view_latest_real_events": "Показати останні реальні події",
    "usage_funnel": "🧭 Воронка використання",
    "diagnostics": "Діагностики",
    "downloaded_pdfs": "Завантажені PDF",
    "emails": "E-mail",
    "feedbacks_label": "Відгуки",
    "pdf_rate": "Частка PDF",

    "international_view": "🌍 Міжнародний огляд",
    "diagnoses_by_language": "Діагностики за мовою",
    "diagnoses_by_currency": "Діагностики за валютою",
    "average_balance_by_currency": "💱 Середній баланс за валютою",
    "summary_language_currency": "🌐 Підсумок за мовою та валютою",

    "diagnoses_page": "👤 Діагностики",
    "risk_distribution": "⚠️ Розподіл ризику",
    "user_ranking_by_diagnostics": "🏆 Рейтинг користувачів за діагностиками",
    "latest_diagnoses": "🧾 Останні діагностики",

    "feedback_page": "💬 Відгуки",
    "no_feedback_found": "Відгуків за вибраними фільтрами не знайдено.",

    "evolution_page": "📈 Динаміка",
    "score_evolution": "📈 Динаміка скорингу",
    "estimated_balance_evolution": "💵 Динаміка оціночного балансу",

    "export_filtered_data": "📤 Експорт відфільтрованих даних",
    "no_feedback_to_export": "Немає відфільтрованих відгуків для експорту.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    "real_multichannel_events": "🌐 Реальные многоканальные события",
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "usage_funnel": "🧭 Воронка использования",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    "international_view": "🌍 Международный обзор",
    "diagnoses_by_language": "Диагностики по языку",
    "diagnoses_by_currency": "Диагностики по валюте",
    "average_balance_by_currency": "💱 Средний баланс по валюте",
    "summary_language_currency": "🌐 Сводка по языку и валюте",

    "diagnoses_page": "👤 Диагностики",
    "risk_distribution": "⚠️ Распределение риска",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "latest_diagnoses": "🧾 Последние диагностики",

    "feedback_page": "💬 Отзывы",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",

    "evolution_page": "📈 Динамика",
    "score_evolution": "📈 Динамика скоринга",
    "estimated_balance_evolution": "💵 Динамика оценочного баланса",

    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "real_multichannel_events": "🌐 أحداث حقيقية متعددة القنوات",
    "real_events": "أحداث حقيقية",
    "active_channels": "القنوات النشطة",
    "latest_channel_metric": "آخر قناة",
    "view_latest_real_events": "عرض أحدث الأحداث الحقيقية",
    "usage_funnel": "🧭 قمع الاستخدام",
    "diagnostics": "التشخيصات",
    "downloaded_pdfs": "ملفات PDF التي تم تنزيلها",
    "emails": "رسائل البريد الإلكتروني",
    "feedbacks_label": "الملاحظات",
    "pdf_rate": "نسبة PDF",

    "international_view": "🌍 العرض الدولي",
    "diagnoses_by_language": "التشخيصات حسب اللغة",
    "diagnoses_by_currency": "التشخيصات حسب العملة",
    "average_balance_by_currency": "💱 متوسط الرصيد حسب العملة",
    "summary_language_currency": "🌐 ملخص حسب اللغة والعملة",

    "diagnoses_page": "👤 التشخيصات",
    "risk_distribution": "⚠️ توزيع المخاطر",
    "user_ranking_by_diagnostics": "🏆 ترتيب المستخدمين حسب التشخيصات",
    "latest_diagnoses": "🧾 أحدث التشخيصات",

    "feedback_page": "💬 الملاحظات",
    "no_feedback_found": "لم يتم العثور على ملاحظات حسب الفلاتر المحددة.",

    "evolution_page": "📈 التطور",
    "score_evolution": "📈 تطور الدرجة",
    "estimated_balance_evolution": "💵 تطور الرصيد المقدر",

    "export_filtered_data": "📤 تصدير البيانات المفلترة",
    "no_feedback_to_export": "لا توجد ملاحظات مفلترة للتصدير.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))



# =============================
# PATCH FINAL RU + INTERFACE MULTILÍNGUE
# Somente textos visuais. Não altera dados reais.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    # Eventos multicanal
    "real_multichannel_events": "🌐 Реальные многоканальные события",
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "usage_funnel": "🧭 Воронка использования",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    # Internacional
    "international_view": "🌍 Международный обзор",
    "diagnoses_by_language": "Диагностики по языку",
    "diagnoses_by_currency": "Диагностики по валюте",
    "average_balance_by_currency": "💱 Средний баланс по валюте",
    "summary_language_currency": "🌐 Сводка по языку и валюте",

    # Diagnósticos
    "diagnoses_page": "👤 Диагностики",
    "risk_distribution": "⚠️ Распределение риска",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "latest_diagnoses": "🧾 Последние диагностики",

    # Feedback
    "feedback_page": "💬 Отзывы",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",

    # Evolução
    "evolution_page": "📈 Динамика",
    "score_evolution": "📈 Динамика скоринга",
    "estimated_balance_evolution": "💵 Динамика оценочного баланса",

    # Leitura executiva
    "executive_reading_page": "🧠 Исполнительное резюме",
    "current_base_summary": "Текущая сводка базы",

    # Exportação
    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "export_diagnostics_csv": "Скачать CSV отфильтрованных диагностик",
    "export_feedbacks_csv": "Скачать CSV отфильтрованных отзывов",
    "export_events_csv": "Скачать CSV отфильтрованных событий",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",
})

DASHBOARD_EXTRA_TEXTS.setdefault("sa", {}).update({
    "real_multichannel_events": "🌐 أحداث حقيقية متعددة القنوات",
    "international_view": "🌍 العرض الدولي",
    "diagnoses_page": "👤 التشخيصات",
    "feedback_page": "💬 الملاحظات",
    "evolution_page": "📈 التطور",
    "executive_reading_page": "🧠 القراءة التنفيذية",
    "current_base_summary": "ملخص القاعدة الحالية",
    "export_filtered_data": "📤 تصدير البيانات المفلترة",
})

DASHBOARD_EXTRA_TEXTS.setdefault("es", {}).update({
    "real_multichannel_events": "🌐 Eventos multicanal reales",
    "international_view": "🌍 Vista internacional",
    "diagnoses_page": dtx("diagnoses_page"),
    "feedback_page": "💬 Feedbacks",
    "evolution_page": "📈 Evolución",
    "executive_reading_page": "🧠 Lectura ejecutiva",
    "current_base_summary": "Resumen actual de la base",
    "export_filtered_data": "📤 Exportar datos filtrados",
})

DASHBOARD_EXTRA_TEXTS.setdefault("fr", {}).update({
    "real_multichannel_events": "🌐 Événements multicanaux réels",
    "international_view": "🌍 Vue internationale",
    "diagnoses_page": "👤 Diagnostics",
    "feedback_page": "💬 Retours",
    "evolution_page": "📈 Évolution",
    "executive_reading_page": "🧠 Lecture exécutive",
    "current_base_summary": "Résumé actuel de la base",
    "export_filtered_data": "📤 Exporter les données filtrées",
})

DASHBOARD_EXTRA_TEXTS.setdefault("de", {}).update({
    "real_multichannel_events": "🌐 Reale Mehrkanal-Ereignisse",
    "international_view": "🌍 Internationale Ansicht",
    "diagnoses_page": "👤 Diagnosen",
    "feedback_page": "💬 Feedbacks",
    "evolution_page": "📈 Entwicklung",
    "executive_reading_page": "🧠 Executive Summary",
    "current_base_summary": "Aktuelle Basiszusammenfassung",
    "export_filtered_data": "📤 Gefilterte Daten exportieren",
})

DASHBOARD_EXTRA_TEXTS.setdefault("it", {}).update({
    "real_multichannel_events": "🌐 Eventi multicanale reali",
    "international_view": "🌍 Vista internazionale",
    "diagnoses_page": "👤 Diagnostiche",
    "feedback_page": dtx("feedback_page"),
    "evolution_page": "📈 Evoluzione",
    "executive_reading_page": "🧠 Lettura esecutiva",
    "current_base_summary": "Riepilogo attuale della base",
    "export_filtered_data": "📤 Esporta dati filtrati",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ro", {}).update({
    "real_multichannel_events": "🌐 Evenimente multicanal reale",
    "international_view": "🌍 Vizualizare internațională",
    "diagnoses_page": "👤 Diagnostice",
    "feedback_page": "💬 Feedbackuri",
    "evolution_page": "📈 Evoluție",
    "executive_reading_page": "🧠 Rezumat executiv",
    "current_base_summary": "Rezumatul actual al bazei",
    "export_filtered_data": "📤 Exportă datele filtrate",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ua", {}).update({
    "real_multichannel_events": "🌐 Реальні багатоканальні події",
    "international_view": "🌍 Міжнародний огляд",
    "diagnoses_page": "👤 Діагностики",
    "feedback_page": "💬 Відгуки",
    "evolution_page": "📈 Динаміка",
    "executive_reading_page": "🧠 Виконавче резюме",
    "current_base_summary": "Поточне зведення бази",
    "export_filtered_data": "📤 Експорт відфільтрованих даних",
})

DASHBOARD_EXTRA_TEXTS.setdefault("ch", {}).update(DASHBOARD_EXTRA_TEXTS.get("de", {}))



# =============================
# PATCH RU TOTAL
# =============================
DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    "real_multichannel_events": "🌐 Реальные многоканальные события",
    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "usage_funnel": "🧭 Воронка использования",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    "international_view": "🌍 Международный обзор",
    "diagnoses_by_language": "Диагностики по языкам",
    "diagnoses_by_currency": "Диагностики по валютам",
    "average_balance_by_currency": "💱 Средний баланс по валютам",
    "summary_language_currency": "🌐 Сводка по языку и валюте",

    "diagnoses_page": "👤 Диагностики",
    "risk_distribution": "⚠️ Распределение риска",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "latest_diagnoses": "🧾 Последние диагностики",

    "feedback_page": "💬 Отзывы",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",

    "evolution_page": "📈 Динамика",
    "score_evolution": "📈 Динамика скоринга",
    "estimated_balance_evolution": "💵 Динамика расчетного баланса",

    "executive_reading_page": "🧠 Исполнительное резюме",
    "current_base_summary": "Текущая сводка базы",

    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "export_diagnostics_csv": "Скачать CSV отфильтрованных диагностик",
    "export_feedbacks_csv": "Скачать CSV отфильтрованных отзывов",
    "export_events_csv": "Скачать CSV отфильтрованных событий",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",
})



# =============================
# PATCH RU - CHAVES REAIS USADAS PELO DASHBOARD
# Corrige textos que ainda caem em inglês quando RU está selecionado.
# =============================

DASHBOARD_EXTRA_TEXTS.setdefault("ru", {}).update({
    # Eventos multicanal
    "events_title": "## 🌐 Реальные многоканальные события",
    "no_events": "События по выбранным фильтрам не найдены.",
    "only_one_channel": "В текущем фильтре найден только один канал.",
    "last_events": "### Показать последние реальные события",
    "funnel_title": "## 🧭 Воронка использования",
    "few_funnel_records": "В текущем фильтре мало записей. Воронка показана таблицей, чтобы избежать искаженного графика.",

    "real_events": "Реальные события",
    "active_channels": "Активные каналы",
    "latest_channel_metric": "Последний канал",
    "view_latest_real_events": "Показать последние реальные события",
    "diagnostics": "Диагностики",
    "downloaded_pdfs": "Скачанные PDF",
    "emails": "E-mail",
    "feedbacks_label": "Отзывы",
    "pdf_rate": "Доля PDF",

    # Visão internacional
    "international_title": "## 🌍 Международный обзор",
    "international_view": "🌍 Международный обзор",
    "no_international": "Международные данные по выбранным фильтрам не найдены.",
    "diagnostics_by_language": "### Диагностики по языку",
    "diagnoses_by_language": "Диагностики по языку",
    "only_one_language": "В текущих фильтрах найден только один язык.",
    "diagnostics_by_currency": "### Диагностики по валюте",
    "diagnoses_by_currency": "Диагностики по валюте",
    "only_one_currency": "В текущих фильтрах найдена только одна валюта.",
    "avg_balance_by_currency": "### 💱 Средний баланс по валюте",
    "average_balance_by_currency": "💱 Средний баланс по валюте",
    "summary_language_currency": "### 🌐 Сводка по языку и валюте",

    # Diagnósticos
    "diagnostics_title": "## 👤 Диагностики",
    "diagnoses_page": "👤 Диагностики",
    "no_diagnostics": "Диагностики по выбранным фильтрам не найдены.",
    "risk_distribution": "### ⚠️ Распределение риска",
    "only_one_risk": "В текущих фильтрах найден только один уровень риска.",
    "user_ranking": "### 🏆 Рейтинг пользователей по диагностикам",
    "user_ranking_by_diagnostics": "🏆 Рейтинг пользователей по диагностикам",
    "last_diagnostics": "### 🧾 Последние диагностики",
    "latest_diagnoses": "🧾 Последние диагностики",

    # Feedbacks
    "feedbacks_title": "## 💬 Отзывы",
    "feedback_page": "💬 Отзывы",
    "no_feedbacks": "Отзывы по выбранным фильтрам не найдены.",
    "no_feedback_found": "Отзывы по выбранным фильтрам не найдены.",
    "useful_feedbacks": "### 👍 Полезные отзывы",
    "received_comments": "### 💬 Полученные комментарии",
    "no_comments": "Заполненных комментариев пока нет.",
    "last_feedbacks": "### 🧾 Последние отзывы",

    # Evolução
    "evolution_title": "## 📈 Динамика",
    "evolution_page": "📈 Динамика",
    "score_evolution": "### 📈 Динамика скоринга",
    "balance_evolution": "### 💵 Динамика оценочного баланса",
    "estimated_balance_evolution": "💵 Динамика оценочного баланса",
    "evolution_wait": "Динамика появится, когда в фильтре будет больше одной диагностики.",

    # Leitura executiva
    "executive_title": "## 🧠 Исполнительное резюме",
    "executive_reading_page": "🧠 Исполнительное резюме",
    "current_base_summary": "### Текущая сводка базы",

    # Exportação
    "export_title": "## 📤 Экспорт отфильтрованных данных",
    "export_filtered_data": "📤 Экспорт отфильтрованных данных",
    "export_diagnostics_csv": "⬇️ Скачать CSV отфильтрованных диагностик",
    "export_feedbacks_csv": "⬇️ Скачать CSV отфильтрованных отзывов",
    "export_events_csv": "⬇️ Скачать CSV отфильтрованных событий",
    "no_diag_export": "Нет отфильтрованных диагностик для экспорта.",
    "no_feedback_export": "Нет отфильтрованных отзывов для экспорта.",
    "no_feedback_to_export": "Нет отфильтрованных отзывов для экспорта.",
    "no_events_export": "Нет отфильтрованных событий для экспорта.",
})



# ============================================================
# FASE 5.18 — UPLOAD REAL DE DOCUMENTOS PARA BASE RAG
# ============================================================

DASHBOARD_MENU_LABELS.setdefault("pt", {}).update({
    "📄 Upload Documentos": "📄 Upload de Documentos",
    "🧠 Memória Usuário": "🧠 Memória do Usuário",
})
DASHBOARD_MENU_LABELS.setdefault("en_us", {}).update({
    "📄 Upload Documentos": "📄 Document Upload",
    "🧠 Memória Usuário": "🧠 User Memory",
})
DASHBOARD_MENU_LABELS.setdefault("en_gb", {}).update({
    "📄 Upload Documentos": "📄 Document Upload",
})
DASHBOARD_MENU_LABELS.setdefault("es", {}).update({
    "📄 Upload Documentos": "📄 Subida de documentos",
})
DASHBOARD_MENU_LABELS.setdefault("fr", {}).update({
    "📄 Upload Documentos": "📄 Téléversement de documents",
})
DASHBOARD_MENU_LABELS.setdefault("de", {}).update({
    "📄 Upload Documentos": "📄 Dokumenten-Upload",
})
DASHBOARD_MENU_LABELS.setdefault("it", {}).update({
    "📄 Upload Documentos": "📄 Caricamento documenti",
})
DASHBOARD_MENU_LABELS.setdefault("ro", {}).update({
    "📄 Upload Documentos": "📄 Încărcare documente",
})
DASHBOARD_MENU_LABELS.setdefault("ua", {}).update({
    "📄 Upload Documentos": "📄 Завантаження документів",
})
DASHBOARD_MENU_LABELS.setdefault("ru", {}).update({
    "📄 Upload Documentos": "📄 Загрузка документов",
})
DASHBOARD_MENU_LABELS.setdefault("sa", {}).update({
    "📄 Upload Documentos": "📄 رفع المستندات",
})
DASHBOARD_MENU_LABELS.setdefault("ch", {}).update({
    "📄 Upload Documentos": "📄 Dokumenten-Upload",
})






def inferir_categorias_pergunta_rag(pergunta):
    if not pergunta:
        return ["geral"]

    pergunta_lower = pergunta.lower()

    regras = [
        (
            ["pix", "transferência", "transferencia", "devolver", "valor estranho", "dinheiro estranho"],
            ["pix", "seguranca"]
        ),
        (
            ["cartão", "cartao", "fatura", "parcelas", "parcelado", "limite", "crédito", "credito"],
            ["cartao_credito", "organizacao_financeira", "dividas"]
        ),
        (
            ["dívida", "divida", "dívidas", "dividas", "endividado", "juros", "negociar", "negociação", "negociacao"],
            ["dividas", "organizacao_financeira", "cartao_credito"]
        ),
        (
            ["reserva", "guardar", "poupar", "emergência", "emergencia"],
            ["reserva_financeira", "organizacao_financeira"]
        ),
        (
            ["organizar", "orçamento", "orcamento", "renda", "gastos", "controle financeiro"],
            ["organizacao_financeira", "dividas", "reserva_financeira"]
        ),
        (
            ["senha", "token", "golpe", "link", "sms", "segurança", "seguranca", "dados sensíveis", "dados sensiveis"],
            ["seguranca", "pix"]
        ),
    ]

    categorias = []

    for termos, categorias_regra in regras:
        if any(termo in pergunta_lower for termo in termos):
            for categoria in categorias_regra:
                if categoria not in categorias:
                    categorias.append(categoria)

    if not categorias:
        categorias.append("geral")

    return categorias


def classificar_categoria_chunk_rag(texto):
    if not texto:
        return "geral"

    texto_lower = texto.lower()

    categorias = {
        "pix": [
            "pix",
            "transferência",
            "transferencia",
            "devolver valor",
            "devolver dinheiro",
            "transação",
            "transacao",
        ],
        "cartao_credito": [
            "cartão",
            "cartao",
            "fatura",
            "parcelas",
            "parcelado",
            "limite do cartão",
            "credito",
            "crédito",
        ],
        "organizacao_financeira": [
            "organizar",
            "organização",
            "organizacao",
            "renda",
            "gastos fixos",
            "gastos variáveis",
            "gastos variaveis",
            "orçamento",
            "orcamento",
        ],
        "reserva_financeira": [
            "reserva",
            "guardar",
            "poupar",
            "emergência",
            "emergencia",
            "hábito de guardar",
            "habito de guardar",
        ],
        "seguranca": [
            "senha",
            "token",
            "código de segurança",
            "codigo de seguranca",
            "dados sensíveis",
            "dados sensiveis",
            "golpe",
            "links",
            "sms",
            "canais oficiais",
            "aplicativo oficial",
        ],
        "dividas": [
            "dívida",
            "divida",
            "dívidas",
            "dividas",
            "endividado",
            "juros",
            "negociação",
            "negociacao",
        ],
    }

    pontuacao = {}

    for categoria, termos in categorias.items():
        pontuacao[categoria] = sum(1 for termo in termos if termo in texto_lower)

    melhor_categoria = max(pontuacao, key=pontuacao.get)

    if pontuacao[melhor_categoria] == 0:
        return "geral"

    return melhor_categoria


def limpar_texto_documento_rag(texto):
    """
    Adaptador para o serviço modular de chunking.
    """
    try:
        from services.rag.chunking import (
            limpar_texto_documento
        )
    except ImportError:
        from src.services.rag.chunking import (
            limpar_texto_documento
        )

    return limpar_texto_documento(texto)


def dividir_texto_em_chunks(
    texto,
    tamanho_chunk=650,
    sobreposicao=0,
):
    """
    Adaptador para o serviço modular de chunking.
    """
    try:
        from services.rag.chunking import (
            dividir_texto_em_chunks as dividir_chunks
        )
    except ImportError:
        from src.services.rag.chunking import (
            dividir_texto_em_chunks as dividir_chunks
        )

    return dividir_chunks(
        texto,
        tamanho_chunk=tamanho_chunk,
        sobreposicao=sobreposicao,
    )


def salvar_chunks_documento(
    nome_arquivo,
    texto,
):
    """
    Adaptador para geração de JSON e JSONL.
    """
    try:
        from services.rag.chunking import (
            salvar_chunks_documento as salvar_chunks
        )
    except ImportError:
        from src.services.rag.chunking import (
            salvar_chunks_documento as salvar_chunks
        )

    return salvar_chunks(
        nome_arquivo=nome_arquivo,
        texto=texto,
        classificar_chunk=classificar_categoria_chunk_rag,
        tamanho_chunk=650,
        sobreposicao=0,
        idioma="pt",
    )



def gerar_embedding_gemini_rag(texto):
    """
    Adaptador compatível para embeddings de documentos.

    Mantido para não quebrar as chamadas antigas.
    """
    try:
        from services.embeddings.gemini import (
            gerar_embedding_documento
        )
    except ImportError:
        from src.services.embeddings.gemini import (
            gerar_embedding_documento
        )

    return gerar_embedding_documento(texto)


def gerar_embedding_consulta_gemini_rag(texto):
    """
    Embedding específico para perguntas de busca semântica.
    """
    try:
        from services.embeddings.gemini import (
            gerar_embedding_consulta
        )
    except ImportError:
        from src.services.embeddings.gemini import (
            gerar_embedding_consulta
        )

    return gerar_embedding_consulta(texto)



def preparar_tabela_embeddings_pgvector_rag(conn):
    """
    Adaptador para o serviço modular pgvector.
    """
    try:
        from services.rag.vector_store import (
            preparar_tabela_embeddings
        )
    except ImportError:
        from src.services.rag.vector_store import (
            preparar_tabela_embeddings
        )

    return preparar_tabela_embeddings(conn)


def salvar_chunks_embeddings_pgvector_rag(
    documento_id,
    caminho_embedding_ready,
):
    """
    Adaptador para geração e armazenamento vetorial.
    """
    try:
        from services.rag.vector_store import (
            salvar_chunks_embeddings
        )
    except ImportError:
        from src.services.rag.vector_store import (
            salvar_chunks_embeddings
        )

    return salvar_chunks_embeddings(
        documento_id=documento_id,
        caminho_embedding_ready=caminho_embedding_ready,
        gerar_embedding=gerar_embedding_gemini_rag,
        substituir_existentes=True,
    )


def definir_limite_chunks_automatico_rag(pergunta):
    if not pergunta:
        return 3

    pergunta_lower = pergunta.lower().strip()

    termos_complexos = [
        "analise",
        "análise",
        "plano",
        "estratégia",
        "organizar tudo",
        "várias dívidas",
        "varias dividas",
        "cartão e pix",
        "cartao e pix",
        "financiamento",
        "orçamento completo",
        "orcamento completo",
        "minha situação",
        "minha situacao",
        "renda",
        "gastos",
        "dívidas",
        "dividas",
        "parcelas",
        "reserva",
    ]

    termos_simples = [
        "pix estranho",
        "devo devolver",
        "é golpe",
        "e golpe",
        "cartão apertado",
        "cartao apertado",
        "posso parcelar",
        "vale a pena",
    ]

    if any(termo in pergunta_lower for termo in termos_complexos):
        return 8

    if any(termo in pergunta_lower for termo in termos_simples):
        return 3

    if len(pergunta_lower) < 80:
        return 3

    if len(pergunta_lower) < 180:
        return 5

    return 8






def arquivar_arquivos_locais_rag(manter_ultimos=5):
    from pathlib import Path
    from datetime import datetime
    import shutil

    pastas = [
        Path("data/knowledge_base/uploads"),
        Path("data/knowledge_base/chunks"),
        Path("data/knowledge_base/embedding_ready"),
    ]

    archive_root = Path("data/knowledge_base/archive")
    archive_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = archive_root / f"arquivos_antigos_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    total_arquivados = 0

    for pasta in pastas:
        if not pasta.exists():
            continue

        arquivos = [
            item for item in pasta.iterdir()
            if item.is_file() and item.name != ".gitkeep"
        ]

        arquivos = sorted(
            arquivos,
            key=lambda item: item.stat().st_mtime,
            reverse=True
        )

        arquivos_antigos = arquivos[manter_ultimos:]

        if not arquivos_antigos:
            continue

        destino_pasta = archive_dir / pasta.name
        destino_pasta.mkdir(parents=True, exist_ok=True)

        for arquivo in arquivos_antigos:
            destino = destino_pasta / arquivo.name
            shutil.move(str(arquivo), str(destino))
            total_arquivados += 1

    return {
        "ok": True,
        "total_arquivados": total_arquivados,
        "archive_dir": str(archive_dir),
        "message": f"{total_arquivados} arquivo(s) antigo(s) arquivado(s) em {archive_dir}."
    }


def carregar_resumo_embeddings_pgvector_rag():
    """
    Adaptador para resumo do armazenamento vetorial.
    """
    try:
        from services.rag.vector_store import (
            carregar_resumo_embeddings
        )
    except ImportError:
        from src.services.rag.vector_store import (
            carregar_resumo_embeddings
        )

    return carregar_resumo_embeddings()


def documento_tem_embeddings_pgvector_rag(
    documento_id
):
    """
    Adaptador para verificação de embeddings.
    """
    try:
        from services.rag.vector_store import (
            documento_tem_embeddings
        )
    except ImportError:
        from src.services.rag.vector_store import (
            documento_tem_embeddings
        )

    return documento_tem_embeddings(
        documento_id
    )


def criar_indice_pgvector_rag():
    """
    Adaptador para criação dos índices pgvector.
    """
    try:
        from services.rag.vector_store import (
            criar_indices_pgvector
        )
    except ImportError:
        from src.services.rag.vector_store import (
            criar_indices_pgvector
        )

    return criar_indices_pgvector()


def renderizar_evolucao_financeira_inna(evolucao, moeda="BRL"):
    import streamlit as st

    try:
        from services.formatter_inna import formatar_moeda
    except ImportError:
        from src.services.formatter_inna import formatar_moeda

    if not evolucao or not evolucao.get("tem_evolucao"):
        return

    itens = evolucao.get("evolucoes", [])

    if not itens:
        return

    st.info("📈 Evolução financeira detectada")

    mapa_icones = {
        "renda_mensal": "💰",
        "gastos_mensais": "💸",
        "valor_reserva": "🏦",
    }

    mapa_titulos = {
        "renda_mensal": upload_rag_t("monthly_income"),
        "gastos_mensais": upload_rag_t("monthly_expenses"),
        "valor_reserva": "Capacidade de guardar",
    }

    colunas = st.columns(min(len(itens), 3))

    for indice, item in enumerate(itens):
        campo = item.get("campo")
        antes = float(item.get("antes") or 0)
        depois = float(item.get("depois") or 0)
        diferenca = float(item.get("diferenca") or 0)

        percentual = 0.0
        if antes != 0:
            percentual = (diferenca / antes) * 100

        antes_fmt = formatar_moeda(antes, moeda)
        depois_fmt = formatar_moeda(depois, moeda)
        diferenca_fmt = formatar_moeda(abs(diferenca), moeda)

        icone = mapa_icones.get(campo, "📊")
        titulo = mapa_titulos.get(campo, item.get("label") or "Indicador")

        if diferenca > 0:
            simbolo = "▲"
            variacao_texto = f"{simbolo} +{diferenca_fmt} ({percentual:+.2f}%)"
        elif diferenca < 0:
            simbolo = "▼"
            variacao_texto = f"{simbolo} -{diferenca_fmt} ({percentual:.2f}%)"
        else:
            variacao_texto = "Sem alteração"

        coluna = colunas[indice % len(colunas)]

        coluna.metric(
            label=f"{icone} {titulo}",
            value=depois_fmt,
            delta=variacao_texto
        )

        coluna.caption(f"Antes: {antes_fmt}")

    with st.expander("Ver detalhes da evolução"):
        for item in itens:
            campo = item.get("campo")
            antes = float(item.get("antes") or 0)
            depois = float(item.get("depois") or 0)
            diferenca = float(item.get("diferenca") or 0)

            percentual = 0.0
            if antes != 0:
                percentual = (diferenca / antes) * 100

            titulo = mapa_titulos.get(campo, item.get("label") or "Indicador")
            icone = mapa_icones.get(campo, "📊")

            st.markdown(f"**{icone} {titulo}**")
            st.write(
                f"{formatar_moeda(antes, moeda)} → "
                f"{formatar_moeda(depois, moeda)}"
            )

            if diferenca > 0:
                st.caption(
                    f"Aumento de {formatar_moeda(diferenca, moeda)} "
                    f"({percentual:+.2f}%)"
                )
            elif diferenca < 0:
                st.caption(
                    f"Redução de {formatar_moeda(abs(diferenca), moeda)} "
                    f"({percentual:.2f}%)"
                )
            else:
                st.caption("Sem alteração.")


def preparar_markdown_resposta_inna(texto):
    import unicodedata

    if not texto:
        return ""

    texto = unicodedata.normalize("NFC", str(texto))

    # Evita Streamlit/Markdown interpretar R$ como fórmula matemática
    texto = texto.replace("R$", "R\\$")

    return texto


def limpar_formatacao_resposta_inna(texto):
    import re

    if not texto:
        return ""

    texto = str(texto)

    # Remove markdown problemático
    texto = texto.replace("**", "")
    texto = texto.replace("__", "")

    # Corrige valores grudados: R$200 -> R$ 200
    texto = re.sub(r"R\$\s*(\d)", r"R$ \1", texto)

    # Corrige dinheiro grudado com texto
    texto = re.sub(r"(R\$ [0-9\.\,]+)(por)", r"\1 por", texto, flags=re.IGNORECASE)
    texto = re.sub(r"(R\$ [0-9\.\,]+)(mensal|semana|semanal|mês|mes)", r"\1 \2", texto, flags=re.IGNORECASE)

    # Corrige palavras grudadas comuns
    texto = re.sub(r"([a-záéíóúãõç])([A-ZÁÉÍÓÚÃÕÇ])", r"\1 \2", texto)

    # Remove espaços excessivos
    texto = re.sub(r"[ \t]+", " ", texto)

    # Garante quebra depois de seções
    texto = texto.replace("Resumo:", "\nResumo:")
    texto = texto.replace("Cálculo:", "\n\nCálculo:")
    texto = texto.replace("Orientação:", "\n\nOrientação:")
    texto = texto.replace("Próximo passo:", "\n\nPróximo passo:")

    # Remove quebras exageradas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def gerar_resposta_rag_pgvector_inna(pergunta, limite=None, usuario_id="demo_user"):
    import os
    from pathlib import Path
    from datetime import datetime, timezone

    try:
        from observability.timeline import (
            executar_etapa_timeline,
            gerar_trace_id,
            registrar_evento_timeline,
        )
    except ImportError:
        from src.observability.timeline import (
            executar_etapa_timeline,
            gerar_trace_id,
            registrar_evento_timeline,
        )

    if not pergunta or not pergunta.strip():
        return {
            "ok": False,
            "message": "Pergunta vazia.",
            "resposta": "",
            "contextos": []
        }

    if limite is None:
        limite = definir_limite_chunks_automatico_rag(pergunta)

    trace_id = gerar_trace_id()

    registrar_evento_timeline(
        trace_id=trace_id,
        etapa="pergunta_recebida",
        usuario_id=usuario_id,
        pergunta=pergunta,
        status="sucesso",
        inicio_em=datetime.now(timezone.utc),
        fim_em=datetime.now(timezone.utc),
        duracao_ms=0.0,
        mensagem="Pergunta recebida pelo fluxo RAG.",
        origem="dashboard_rag",
        metadata={
            "limite_chunks": limite,
        },
    )

    etapa_memoria = executar_etapa_timeline(
        trace_id=trace_id,
        etapa="memoria_consultada",
        funcao=buscar_memoria_inna,
        argumentos={
            "usuario_id": usuario_id,
        },
        usuario_id=usuario_id,
        pergunta=pergunta,
        origem="dashboard_rag",
        metadata={
            "fonte": "memoria_usuarios_inna",
        },
    )

    resultado_memoria = (
        etapa_memoria.get("resultado")
        or {
            "ok": False,
            "memoria": None,
        }
    )

    memoria_usuario = (
        resultado_memoria.get("memoria")
        if resultado_memoria.get("ok")
        else None
    )

    bloco_memoria = "Nenhuma memória ativa encontrada para este usuário."

    if memoria_usuario:
        bloco_memoria = f"""
Usuário ID: {memoria_usuario.get("usuario_id")}
Nome: {memoria_usuario.get("nome")}
Idioma: {memoria_usuario.get("idioma")}
Moeda: {memoria_usuario.get("moeda")}
Renda mensal: {memoria_usuario.get("renda_mensal")}
Gastos mensais: {memoria_usuario.get("gastos_mensais")}
Valor que consegue guardar: {memoria_usuario.get("valor_reserva")}
Possui dívidas: {memoria_usuario.get("possui_dividas")}
Usa cartão de crédito: {memoria_usuario.get("uso_cartao_credito")}
Perfil financeiro: {memoria_usuario.get("perfil_financeiro")}
Objetivo principal: {memoria_usuario.get("objetivo_principal")}
Última meta: {memoria_usuario.get("ultima_meta")}
Resumo: {memoria_usuario.get("resumo_contexto")}
"""

    etapa_rag = executar_etapa_timeline(
        trace_id=trace_id,
        etapa="rag_consultado",
        funcao=buscar_chunks_semanticos_pgvector_rag,
        argumentos={
            "pergunta": pergunta,
            "limite": limite,
        },
        usuario_id=usuario_id,
        pergunta=pergunta,
        origem="dashboard_rag",
        metadata={
            "limite_chunks": limite,
            "banco_vetorial": "pgvector",
        },
    )

    resultado_busca = (
        etapa_rag.get("resultado")
        or {
            "ok": False,
            "resultados": [],
            "message": etapa_rag.get("erro"),
        }
    )

    if not resultado_busca.get("ok"):
        return {
            "ok": False,
            "message": resultado_busca.get("message"),
            "resposta": "",
            "contextos": []
        }

    contextos = resultado_busca.get("resultados", [])

    if not contextos:
        return {
            "ok": False,
            "message": "Nenhum contexto encontrado no pgvector.",
            "resposta": "",
            "contextos": []
        }

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=Path(".env"))
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        return {
            "ok": False,
            "message": "GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada.",
            "resposta": "",
            "contextos": contextos
        }

    try:
        try:
            from services.llm.gemini import gerar_texto_gemini
        except ImportError:
            from src.services.llm.gemini import gerar_texto_gemini

        trechos_contexto = []

        for idx, item in enumerate(contextos, start=1):
            trechos_contexto.append(
                f"""
[TRECHO {idx}]
Documento: {item.get("documento_origem")}
Chunk: {item.get("chunk_index")}
Similaridade aproximada: {item.get("similaridade_aproximada")}
Conteúdo:
{item.get("texto")}
"""
            )

        contexto_final = "\n".join(trechos_contexto)

        try:
            from tools.orchestrator import (
                processar_pergunta_com_tools
            )
        except ImportError:
            from src.tools.orchestrator import (
                processar_pergunta_com_tools
            )

        etapa_router = executar_etapa_timeline(
            trace_id=trace_id,
            etapa="router_executado",
            funcao=processar_pergunta_com_tools,
            argumentos={
                "pergunta": pergunta,
                "memoria": memoria_usuario,
                "usuario_id": usuario_id,
                "origem": "dashboard_rag",
                "registrar_observabilidade": True,
            },
            usuario_id=usuario_id,
            pergunta=pergunta,
            origem="dashboard_rag",
            metadata={
                "componente": "tools_orchestrator",
            },
        )

        resultado_tools = (
            etapa_router.get("resultado")
            or {}
        )

        tool_identificada_timeline = (
            resultado_tools.get(
                "tool_identificada"
            )
        )

        if tool_identificada_timeline:
            registrar_evento_timeline(
                trace_id=trace_id,
                etapa="tool_executada",
                usuario_id=usuario_id,
                pergunta=pergunta,
                status=(
                    "sucesso"
                    if resultado_tools.get("executada")
                    else "ignorado"
                ),
                inicio_em=None,
                fim_em=None,
                duracao_ms=None,
                mensagem=(
                    "Resultado da Tool registrado. "
                    "O tempo total foi contabilizado "
                    "na etapa do Router/Orquestrador."
                ),
                origem="dashboard_rag",
                metadata={
                    "tool": tool_identificada_timeline,
                    "tool_label": resultado_tools.get(
                        "tool_label"
                    ),
                    "intencao": resultado_tools.get(
                        "intencao"
                    ),
                    "confianca": resultado_tools.get(
                        "confianca"
                    ),
                    "executada": resultado_tools.get(
                        "executada"
                    ),
                    "dados_ausentes": resultado_tools.get(
                        "dados_ausentes",
                        [],
                    ),
                },
            )
        else:
            registrar_evento_timeline(
                trace_id=trace_id,
                etapa="tool_executada",
                usuario_id=usuario_id,
                pergunta=pergunta,
                status="ignorado",
                duracao_ms=None,
                mensagem=(
                    "Nenhuma Tool financeira foi "
                    "necessária para esta pergunta."
                ),
                origem="dashboard_rag",
                metadata={
                    "tool": None,
                },
            )

        contexto_tools = resultado_tools.get(
            "bloco_prompt"
        )

        try:
            from services.prompt_builder_inna import montar_prompt_inna
        except ImportError:
            from src.services.prompt_builder_inna import montar_prompt_inna

        etapa_prompt = executar_etapa_timeline(
            trace_id=trace_id,
            etapa="prompt_montado",
            funcao=montar_prompt_inna,
            argumentos={
                "pergunta": pergunta,
                "memoria": memoria_usuario,
                "historico": None,
                "chunks": contextos,
                "contexto_tools": contexto_tools,
            },
            usuario_id=usuario_id,
            pergunta=pergunta,
            origem="dashboard_rag",
            metadata={
                "total_contextos": len(contextos),
                "tool": resultado_tools.get(
                    "tool_identificada"
                ),
            },
        )

        prompt = etapa_prompt.get(
            "resultado"
        )

        from src.services.llm.model_registry import (
            LLMRole,
            get_model_for_role,
        )

        modelo_rag = get_model_for_role(
            LLMRole.RAG
        )

        etapa_gemini = executar_etapa_timeline(
            trace_id=trace_id,
            etapa="gemini_executado",
            funcao=gerar_texto_gemini,
            argumentos={
                "prompt": prompt,
                "role": LLMRole.RAG,
                "temperatura": 0.2,
                "max_tokens": 4096,
            },
            usuario_id=usuario_id,
            pergunta=pergunta,
            origem="dashboard_rag",
            metadata={
                "modelo": modelo_rag,
                "role": LLMRole.RAG.value,
                "temperatura": 0.2,
                "max_tokens": 4096,
            },
        )

        resposta_bruta = etapa_gemini.get(
            "resultado"
        )

        etapa_formatter = executar_etapa_timeline(
            trace_id=trace_id,
            etapa="resposta_formatada",
            funcao=limpar_formatacao_resposta_inna,
            argumentos={
                "texto": resposta_bruta,
            },
            usuario_id=usuario_id,
            pergunta=pergunta,
            origem="dashboard_rag",
            metadata={
                "tamanho_resposta_bruta": len(
                    str(resposta_bruta or "")
                ),
            },
        )

        resposta = etapa_formatter.get(
            "resultado"
        )

        print("\n========== RESPOSTA BRUTA GEMINI ==========")
        print(resposta_bruta)
        print("========== FIM RESPOSTA BRUTA ==========\n")

        print("\n========== RESPOSTA APÓS LIMPEZA ==========")
        print(resposta)
        print("========== FIM RESPOSTA LIMPA ==========\n")

        if not resposta:
            resposta = "Não consegui gerar uma resposta final com base no contexto encontrado."

        memoria_atualizada = {
            "ok": False,
            "message": "Nenhuma atualização automática de memória detectada."
        }

        try:
            from services.memory_update_inna import (
                extrair_memoria_da_mensagem_inna,
                mesclar_memoria_existente,
                calcular_evolucao_memoria,
                copiar_memoria
            )
        except ImportError:
            from src.services.memory_update_inna import (
                extrair_memoria_da_mensagem_inna,
                mesclar_memoria_existente,
                calcular_evolucao_memoria,
                copiar_memoria
            )

        extracao_memoria = extrair_memoria_da_mensagem_inna(pergunta)

        if extracao_memoria.get("tem_memoria"):
            memoria_anterior = copiar_memoria(memoria_usuario)

            dados_mesclados = mesclar_memoria_existente(
                memoria_usuario,
                extracao_memoria.get("dados", {})
            )

            evolucao_memoria = calcular_evolucao_memoria(
                memoria_anterior,
                dados_mesclados
            )

            if evolucao_memoria.get("tem_evolucao"):
                resumo_anterior = dados_mesclados.get("resumo_contexto") or ""
                dados_mesclados["resumo_contexto"] = (
                    resumo_anterior
                    + "\nEvolução financeira detectada: "
                    + evolucao_memoria.get("resumo", "")
                ).strip()

                memoria_json = dados_mesclados.get("memoria_json") or {}
                memoria_json["ultima_evolucao_financeira"] = evolucao_memoria
                dados_mesclados["memoria_json"] = memoria_json

            memoria_atualizada = salvar_ou_atualizar_memoria_inna(
                usuario_id=usuario_id,
                dados_memoria=dados_mesclados,
                origem="auto_conversa_rag"
            )

            memoria_atualizada["evolucao"] = evolucao_memoria

        registrar_evento_timeline(
            trace_id=trace_id,
            etapa="resposta_entregue",
            usuario_id=usuario_id,
            pergunta=pergunta,
            status="sucesso",
            inicio_em=datetime.now(timezone.utc),
            fim_em=datetime.now(timezone.utc),
            duracao_ms=0.0,
            mensagem=(
                "Resposta final preparada para "
                "entrega ao dashboard."
            ),
            origem="dashboard_rag",
            metadata={
                "total_contextos": len(contextos),
                "tool": resultado_tools.get(
                    "tool_identificada"
                ),
                "memoria_atualizada": bool(
                    memoria_atualizada.get("ok")
                ),
                "tamanho_resposta": len(
                    str(resposta or "")
                ),
            },
        )

        return {
            "ok": True,
            "trace_id": trace_id,
            "message": (
                f"Resposta gerada com {len(contextos)} "
                "contexto(s) do pgvector."
            ),
            "resposta": resposta,
            "contextos": contextos,
            "memoria_atualizada": memoria_atualizada,
            "tools": resultado_tools,
        }

    except Exception as e:
        return {
            "ok": False,
            "message": f"Erro ao gerar resposta RAG com Gemini: {e}",
            "resposta": "",
            "contextos": contextos
        }


def buscar_chunks_semanticos_pgvector_rag(
    pergunta,
    limite=5,
):
    """
    Adaptador temporário para o serviço modular de recuperação RAG.
    """
    try:
        from services.rag.retrieval import (
            buscar_chunks_semanticos
        )
    except ImportError:
        from src.services.rag.retrieval import (
            buscar_chunks_semanticos
        )

    return buscar_chunks_semanticos(
        pergunta=pergunta,
        limite=limite,
        gerar_embedding=gerar_embedding_consulta_gemini_rag,
        classificar_chunk=classificar_categoria_chunk_rag,
        dimensoes=3072,
        bonus_categoria=0.08,
    )



def atualizar_metadata_reprocessamento_rag(
    documento_id,
    caminho_chunks,
    caminho_embedding_ready,
    total_chunks,
):
    try:
        from services.rag.document_repository import (
            atualizar_processamento_documento
        )
    except ImportError:
        from src.services.rag.document_repository import (
            atualizar_processamento_documento
        )

    return atualizar_processamento_documento(
        documento_id=documento_id,
        caminho_chunks=caminho_chunks,
        caminho_embedding_ready=caminho_embedding_ready,
        total_chunks=total_chunks,
    )


def garantir_coluna_ativo_documentos_rag():
    try:
        from services.rag.document_repository import (
            garantir_coluna_ativo
        )
    except ImportError:
        from src.services.rag.document_repository import (
            garantir_coluna_ativo
        )

    return garantir_coluna_ativo()


def atualizar_status_documento_rag(
    documento_id,
    ativo,
):
    try:
        from services.rag.document_repository import (
            atualizar_status_documento
        )
    except ImportError:
        from src.services.rag.document_repository import (
            atualizar_status_documento
        )

    return atualizar_status_documento(
        documento_id=documento_id,
        ativo=ativo,
    )


def carregar_documentos_upload_rag():
    try:
        from services.rag.document_repository import (
            listar_documentos
        )
    except ImportError:
        from src.services.rag.document_repository import (
            listar_documentos
        )

    return listar_documentos(
        limite=100
    )


def buscar_contexto_versionamento_rag(
    nome_logico,
):
    try:
        from services.rag.document_repository import (
            buscar_contexto_versionamento_documento,
        )
    except ImportError:
        from src.services.rag.document_repository import (
            buscar_contexto_versionamento_documento,
        )

    return buscar_contexto_versionamento_documento(
        nome_logico
    )



def registrar_metadata_upload_rag(
    nome_original,
    nome_salvo,
    caminho_upload,
    caminho_chunks,
    caminho_embedding_ready,
    extensao,
    tamanho_bytes,
    total_chunks,
    nome_logico=None,
    content_hash=None,
    versao=1,
    documento_raiz_id=None,
    documento_anterior_id=None,
):
    try:
        from services.rag.document_repository import (
            registrar_documento
        )
    except ImportError:
        from src.services.rag.document_repository import (
            registrar_documento
        )

    return registrar_documento(
        nome_original=nome_original,
        nome_salvo=nome_salvo,
        caminho_upload=caminho_upload,
        caminho_chunks=caminho_chunks,
        caminho_embedding_ready=caminho_embedding_ready,
        extensao=extensao,
        tamanho_bytes=tamanho_bytes,
        total_chunks=total_chunks,
        nome_logico=nome_logico,
        content_hash=content_hash,
        versao=versao,
        documento_raiz_id=documento_raiz_id,
        documento_anterior_id=documento_anterior_id,
        status="processado",
        origem="dashboard_upload",
    )


UPLOAD_RAG_TEXTS = {
    "pt": {
        "title": "## 📄 Upload de Documentos para a Base RAG",
        "caption": (
            "Envie arquivos .md ou .txt para expandir "
            "a base de conhecimento da INNA."
        ),
        "select_document": "Selecione um documento",
        "upload_help": (
            "Nesta versão, a INNA aceita arquivos "
            "Markdown e TXT."
        ),
        "invalid_format": (
            "Formato não permitido. Envie apenas "
            "arquivos .md ou .txt."
        ),
        "version_lookup_error": (
            "Não foi possível consultar o "
            "versionamento do documento."
        ),
        "version_error": (
            "Não foi possível determinar a versão "
            "do documento"
        ),
        "security_rejection": (
            "Documento rejeitado pela política de segurança"
        ),
        "security_validation_error": (
            "Não foi possível validar a segurança "
            "do documento."
        ),
        "saved_successfully": "Documento salvo com sucesso",
        "validation_complete": "Validação concluída",
        "document": "Documento",
        "version": "Versão",
        "content_preview": "### Prévia do conteúdo",
        "loaded_content": "Conteúdo carregado",
        "generated_chunks": "### Chunks gerados",
        "chunks_generated": "chunks gerados e salvos em",
        "embedding_ready": (
            "Arquivo pronto para embeddings/pgvector"
        ),
    },
    "en_us": {
        "title": "## 📄 Document Upload for the RAG Knowledge Base",
        "caption": (
            "Upload .md or .txt files to expand "
            "INNA's knowledge base."
        ),
        "select_document": "Select a document",
        "upload_help": (
            "In this version, INNA accepts Markdown "
            "and TXT files."
        ),
        "invalid_format": (
            "Unsupported format. Upload only "
            ".md or .txt files."
        ),
        "version_lookup_error": (
            "The document version information "
            "could not be retrieved."
        ),
        "version_error": (
            "The document version could not be determined"
        ),
        "security_rejection": (
            "Document rejected by the security policy"
        ),
        "security_validation_error": (
            "The document security validation failed."
        ),
        "saved_successfully": "Document saved successfully",
        "validation_complete": "Validation complete",
        "document": "Document",
        "version": "Version",
        "content_preview": "### Content preview",
        "loaded_content": "Loaded content",
        "generated_chunks": "### Generated chunks",
        "chunks_generated": "chunks generated and saved to",
        "embedding_ready": (
            "File ready for embeddings/pgvector"
        ),
    },
    "es": {
        "title": "## 📄 Carga de Documentos para la Base RAG",
        "caption": (
            "Envíe archivos .md o .txt para ampliar "
            "la base de conocimiento de INNA."
        ),
        "select_document": "Seleccione un documento",
        "upload_help": (
            "En esta versión, INNA acepta archivos "
            "Markdown y TXT."
        ),
        "invalid_format": (
            "Formato no permitido. Envíe solamente "
            "archivos .md o .txt."
        ),
        "version_lookup_error": (
            "No fue posible consultar el versionado "
            "del documento."
        ),
        "version_error": (
            "No fue posible determinar la versión del documento"
        ),
        "security_rejection": (
            "Documento rechazado por la política de seguridad"
        ),
        "security_validation_error": (
            "No fue posible validar la seguridad del documento."
        ),
        "saved_successfully": "Documento guardado correctamente",
        "validation_complete": "Validación finalizada",
        "document": "Documento",
        "version": "Versión",
        "content_preview": "### Vista previa del contenido",
        "loaded_content": "Contenido cargado",
        "generated_chunks": "### Chunks generados",
        "chunks_generated": "chunks generados y guardados en",
        "embedding_ready": (
            "Archivo preparado para embeddings/pgvector"
        ),
    },
    "fr": {
        "title": "## 📄 Téléversement de Documents pour la Base RAG",
        "caption": (
            "Envoyez des fichiers .md ou .txt pour enrichir "
            "la base de connaissances d’INNA."
        ),
        "select_document": "Sélectionnez un document",
        "upload_help": (
            "Dans cette version, INNA accepte les fichiers "
            "Markdown et TXT."
        ),
        "invalid_format": (
            "Format non autorisé. Envoyez uniquement "
            "des fichiers .md ou .txt."
        ),
        "version_lookup_error": (
            "Impossible de consulter le versionnement "
            "du document."
        ),
        "version_error": (
            "Impossible de déterminer la version du document"
        ),
        "security_rejection": (
            "Document rejeté par la politique de sécurité"
        ),
        "security_validation_error": (
            "Impossible de valider la sécurité du document."
        ),
        "saved_successfully": "Document enregistré avec succès",
        "validation_complete": "Validation terminée",
        "document": "Document",
        "version": "Version",
        "content_preview": "### Aperçu du contenu",
        "loaded_content": "Contenu chargé",
        "generated_chunks": "### Chunks générés",
        "chunks_generated": "chunks générés et enregistrés dans",
        "embedding_ready": (
            "Fichier prêt pour embeddings/pgvector"
        ),
    },
    "de": {
        "title": "## 📄 Dokumenten-Upload für die RAG-Wissensbasis",
        "caption": (
            "Laden Sie .md- oder .txt-Dateien hoch, um "
            "die INNA-Wissensbasis zu erweitern."
        ),
        "select_document": "Dokument auswählen",
        "upload_help": (
            "In dieser Version akzeptiert INNA "
            "Markdown- und TXT-Dateien."
        ),
        "invalid_format": (
            "Nicht unterstütztes Format. Laden Sie nur "
            ".md- oder .txt-Dateien hoch."
        ),
        "version_lookup_error": (
            "Die Dokumentversion konnte nicht "
            "abgerufen werden."
        ),
        "version_error": (
            "Die Dokumentversion konnte nicht bestimmt werden"
        ),
        "security_rejection": (
            "Dokument durch Sicherheitsrichtlinie abgelehnt"
        ),
        "security_validation_error": (
            "Die Dokumentsicherheit konnte nicht validiert werden."
        ),
        "saved_successfully": "Dokument erfolgreich gespeichert",
        "validation_complete": "Validierung abgeschlossen",
        "document": "Dokument",
        "version": "Version",
        "content_preview": "### Inhaltsvorschau",
        "loaded_content": "Geladener Inhalt",
        "generated_chunks": "### Generierte Chunks",
        "chunks_generated": "Chunks generiert und gespeichert in",
        "embedding_ready": (
            "Datei bereit für Embeddings/pgvector"
        ),
    },
    "it": {
        "title": "## 📄 Caricamento Documenti per la Base RAG",
        "caption": (
            "Carica file .md o .txt per ampliare "
            "la base di conoscenza di INNA."
        ),
        "select_document": "Seleziona un documento",
        "upload_help": (
            "In questa versione, INNA accetta file "
            "Markdown e TXT."
        ),
        "invalid_format": (
            "Formato non consentito. Carica solo "
            "file .md o .txt."
        ),
        "version_lookup_error": (
            "Impossibile consultare il versionamento "
            "del documento."
        ),
        "version_error": (
            "Impossibile determinare la versione del documento"
        ),
        "security_rejection": (
            "Documento rifiutato dalla politica di sicurezza"
        ),
        "security_validation_error": (
            "Impossibile validare la sicurezza del documento."
        ),
        "saved_successfully": "Documento salvato correttamente",
        "validation_complete": "Validazione completata",
        "document": "Documento",
        "version": "Versione",
        "content_preview": "### Anteprima del contenuto",
        "loaded_content": "Contenuto caricato",
        "generated_chunks": "### Chunks generati",
        "chunks_generated": "chunks generati e salvati in",
        "embedding_ready": (
            "File pronto per embeddings/pgvector"
        ),
    },
}

UPLOAD_RAG_TEXTS["en_gb"] = UPLOAD_RAG_TEXTS["en_us"]

for idioma in (
    "ro",
    "ua",
    "ru",
    "sa",
):
    UPLOAD_RAG_TEXTS[idioma] = (
        UPLOAD_RAG_TEXTS["en_us"].copy()
    )


UPLOAD_RAG_DOCUMENT_TEXTS = {'pt': {'file_size': 'Tamanho', 'registered_documents': '### Documentos registrados no Neon/PostgreSQL', 'database_documents_error': 'Não foi possível carregar os documentos do banco', 'no_registered_documents': 'Nenhum documento registrado no Neon/PostgreSQL ainda.', 'registered_documents_total': 'Total de documentos registrados', 'total_chunks': 'Total de chunks', 'processed': 'Processados', 'extensions': 'Extensões', 'local_organisation': '### Organização local dos arquivos RAG', 'local_uploads': 'Uploads locais', 'chunk_files': 'Arquivos de chunks', 'embedding_ready_jsonl': 'JSONL para embeddings', 'recent_local_files': 'Ver arquivos locais recentes', 'recent_files_caption': 'Mostrando no máximo os 5 arquivos mais recentes de cada pasta.', 'recent_uploads': '**Uploads recentes**', 'recent_chunks': '**Chunks recentes**', 'recent_jsonl': '**JSONL recentes**', 'archive_caption': 'Arquivar move os arquivos antigos para data/knowledge_base/archive. Nada é apagado definitivamente.', 'files_to_keep': 'Quantos arquivos recentes devem ser mantidos em cada pasta?', 'archive_old_files': '🗂️ Arquivar arquivos locais antigos', 'document_status': '### Status do documento na base RAG', 'select_status_document': 'Escolha um documento para ativar ou desativar', 'active_document': 'Este documento está ATIVO na busca RAG.', 'inactive_document': 'Este documento está INATIVO e será ignorado na busca RAG.', 'activate_document': '✅ Ativar documento', 'deactivate_document': '🚫 Desativar documento', 'reprocess_document': '### Reprocessar documento', 'select_reprocess_document': 'Escolha um documento para reprocessar', 'reprocess_selected': '🔄 Reprocessar documento selecionado', 'original_file_not_found': 'Arquivo original não encontrado', 'new_embedding_ready': 'Novo arquivo pronto para embeddings'}, 'en_us': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'es': {'file_size': 'Tamaño', 'registered_documents': '### Documentos registrados en Neon/PostgreSQL', 'database_documents_error': 'No fue posible cargar los documentos de la base', 'no_registered_documents': 'Todavía no hay documentos registrados en Neon/PostgreSQL.', 'registered_documents_total': 'Total de documentos registrados', 'total_chunks': 'Total de chunks', 'processed': 'Procesados', 'extensions': 'Extensiones', 'local_organisation': '### Organización local de archivos RAG', 'local_uploads': 'Cargas locales', 'chunk_files': 'Archivos de chunks', 'embedding_ready_jsonl': 'JSONL para embeddings', 'recent_local_files': 'Ver archivos locales recientes', 'recent_files_caption': 'Se muestran como máximo los 5 archivos más recientes de cada carpeta.', 'recent_uploads': '**Cargas recientes**', 'recent_chunks': '**Chunks recientes**', 'recent_jsonl': '**JSONL recientes**', 'archive_caption': 'Archivar mueve los archivos antiguos a data/knowledge_base/archive. Nada se elimina definitivamente.', 'files_to_keep': '¿Cuántos archivos recientes deben conservarse en cada carpeta?', 'archive_old_files': '🗂️ Archivar archivos locales antiguos', 'document_status': '### Estado del documento en la base RAG', 'select_status_document': 'Seleccione un documento para activar o desactivar', 'active_document': 'Este documento está ACTIVO en la búsqueda RAG.', 'inactive_document': 'Este documento está INACTIVO y será ignorado en la búsqueda RAG.', 'activate_document': '✅ Activar documento', 'deactivate_document': '🚫 Desactivar documento', 'reprocess_document': '### Reprocesar documento', 'select_reprocess_document': 'Seleccione un documento para reprocesar', 'reprocess_selected': '🔄 Reprocesar documento seleccionado', 'original_file_not_found': 'Archivo original no encontrado', 'new_embedding_ready': 'Nuevo archivo preparado para embeddings'}, 'fr': {'file_size': 'Taille', 'registered_documents': '### Documents enregistrés dans Neon/PostgreSQL', 'database_documents_error': 'Impossible de charger les documents de la base', 'no_registered_documents': 'Aucun document enregistré dans Neon/PostgreSQL.', 'registered_documents_total': 'Total des documents enregistrés', 'total_chunks': 'Total des chunks', 'processed': 'Traités', 'extensions': 'Extensions', 'local_organisation': '### Organisation locale des fichiers RAG', 'local_uploads': 'Téléversements locaux', 'chunk_files': 'Fichiers de chunks', 'embedding_ready_jsonl': 'JSONL pour embeddings', 'recent_local_files': 'Voir les fichiers locaux récents', 'recent_files_caption': 'Affichage des 5 fichiers les plus récents de chaque dossier.', 'recent_uploads': '**Téléversements récents**', 'recent_chunks': '**Chunks récents**', 'recent_jsonl': '**JSONL récents**', 'archive_caption': 'L’archivage déplace les anciens fichiers vers data/knowledge_base/archive. Aucun fichier n’est définitivement supprimé.', 'files_to_keep': 'Combien de fichiers récents conserver dans chaque dossier ?', 'archive_old_files': '🗂️ Archiver les anciens fichiers locaux', 'document_status': '### État du document dans la base RAG', 'select_status_document': 'Sélectionnez un document à activer ou désactiver', 'active_document': 'Ce document est ACTIF dans la recherche RAG.', 'inactive_document': 'Ce document est INACTIF et sera ignoré par la recherche RAG.', 'activate_document': '✅ Activer le document', 'deactivate_document': '🚫 Désactiver le document', 'reprocess_document': '### Retraiter le document', 'select_reprocess_document': 'Sélectionnez un document à retraiter', 'reprocess_selected': '🔄 Retraiter le document sélectionné', 'original_file_not_found': 'Fichier original introuvable', 'new_embedding_ready': 'Nouveau fichier prêt pour les embeddings'}, 'de': {'file_size': 'Größe', 'registered_documents': '### In Neon/PostgreSQL registrierte Dokumente', 'database_documents_error': 'Datenbankdokumente konnten nicht geladen werden', 'no_registered_documents': 'Noch keine Dokumente in Neon/PostgreSQL registriert.', 'registered_documents_total': 'Registrierte Dokumente insgesamt', 'total_chunks': 'Chunks insgesamt', 'processed': 'Verarbeitet', 'extensions': 'Erweiterungen', 'local_organisation': '### Lokale Organisation der RAG-Dateien', 'local_uploads': 'Lokale Uploads', 'chunk_files': 'Chunk-Dateien', 'embedding_ready_jsonl': 'Embedding-fähige JSONL', 'recent_local_files': 'Aktuelle lokale Dateien anzeigen', 'recent_files_caption': 'Es werden höchstens die 5 neuesten Dateien jedes Ordners angezeigt.', 'recent_uploads': '**Aktuelle Uploads**', 'recent_chunks': '**Aktuelle Chunks**', 'recent_jsonl': '**Aktuelle JSONL-Dateien**', 'archive_caption': 'Beim Archivieren werden alte Dateien nach data/knowledge_base/archive verschoben. Nichts wird dauerhaft gelöscht.', 'files_to_keep': 'Wie viele aktuelle Dateien sollen in jedem Ordner behalten werden?', 'archive_old_files': '🗂️ Alte lokale Dateien archivieren', 'document_status': '### Dokumentstatus in der RAG-Wissensbasis', 'select_status_document': 'Dokument zum Aktivieren oder Deaktivieren auswählen', 'active_document': 'Dieses Dokument ist in der RAG-Suche AKTIV.', 'inactive_document': 'Dieses Dokument ist INAKTIV und wird bei der RAG-Suche ignoriert.', 'activate_document': '✅ Dokument aktivieren', 'deactivate_document': '🚫 Dokument deaktivieren', 'reprocess_document': '### Dokument erneut verarbeiten', 'select_reprocess_document': 'Dokument zur erneuten Verarbeitung auswählen', 'reprocess_selected': '🔄 Ausgewähltes Dokument erneut verarbeiten', 'original_file_not_found': 'Originaldatei nicht gefunden', 'new_embedding_ready': 'Neue Datei bereit für Embeddings'}, 'en_gb': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'it': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'ro': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'ua': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'ru': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'sa': {'file_size': 'Size', 'registered_documents': '### Documents registered in Neon/PostgreSQL', 'database_documents_error': 'The database documents could not be loaded', 'no_registered_documents': 'No documents have been registered in Neon/PostgreSQL yet.', 'registered_documents_total': 'Total registered documents', 'total_chunks': 'Total chunks', 'processed': 'Processed', 'extensions': 'Extensions', 'local_organisation': '### Local RAG file organisation', 'local_uploads': 'Local uploads', 'chunk_files': 'Chunk files', 'embedding_ready_jsonl': 'Embedding-ready JSONL', 'recent_local_files': 'View recent local files', 'recent_files_caption': 'Showing up to the 5 most recent files from each folder.', 'recent_uploads': '**Recent uploads**', 'recent_chunks': '**Recent chunks**', 'recent_jsonl': '**Recent JSONL files**', 'archive_caption': 'Archiving moves old files to data/knowledge_base/archive. Nothing is permanently deleted.', 'files_to_keep': 'How many recent files should be kept in each folder?', 'archive_old_files': '🗂️ Archive old local files', 'document_status': '### Document status in the RAG knowledge base', 'select_status_document': 'Select a document to activate or deactivate', 'active_document': 'This document is ACTIVE in RAG search.', 'inactive_document': 'This document is INACTIVE and will be ignored by RAG search.', 'activate_document': '✅ Activate document', 'deactivate_document': '🚫 Deactivate document', 'reprocess_document': '### Reprocess document', 'select_reprocess_document': 'Select a document to reprocess', 'reprocess_selected': '🔄 Reprocess selected document', 'original_file_not_found': 'Original file not found', 'new_embedding_ready': 'New file ready for embeddings'}, 'ch': {'file_size': 'Größe', 'registered_documents': '### In Neon/PostgreSQL registrierte Dokumente', 'database_documents_error': 'Datenbankdokumente konnten nicht geladen werden', 'no_registered_documents': 'Noch keine Dokumente in Neon/PostgreSQL registriert.', 'registered_documents_total': 'Registrierte Dokumente insgesamt', 'total_chunks': 'Chunks insgesamt', 'processed': 'Verarbeitet', 'extensions': 'Erweiterungen', 'local_organisation': '### Lokale Organisation der RAG-Dateien', 'local_uploads': 'Lokale Uploads', 'chunk_files': 'Chunk-Dateien', 'embedding_ready_jsonl': 'Embedding-fähige JSONL', 'recent_local_files': 'Aktuelle lokale Dateien anzeigen', 'recent_files_caption': 'Es werden höchstens die 5 neuesten Dateien jedes Ordners angezeigt.', 'recent_uploads': '**Aktuelle Uploads**', 'recent_chunks': '**Aktuelle Chunks**', 'recent_jsonl': '**Aktuelle JSONL-Dateien**', 'archive_caption': 'Beim Archivieren werden alte Dateien nach data/knowledge_base/archive verschoben. Nichts wird dauerhaft gelöscht.', 'files_to_keep': 'Wie viele aktuelle Dateien sollen in jedem Ordner behalten werden?', 'archive_old_files': '🗂️ Alte lokale Dateien archivieren', 'document_status': '### Dokumentstatus in der RAG-Wissensbasis', 'select_status_document': 'Dokument zum Aktivieren oder Deaktivieren auswählen', 'active_document': 'Dieses Dokument ist in der RAG-Suche AKTIV.', 'inactive_document': 'Dieses Dokument ist INAKTIV und wird bei der RAG-Suche ignoriert.', 'activate_document': '✅ Dokument aktivieren', 'deactivate_document': '🚫 Dokument deaktivieren', 'reprocess_document': '### Dokument erneut verarbeiten', 'select_reprocess_document': 'Dokument zur erneuten Verarbeitung auswählen', 'reprocess_selected': '🔄 Ausgewähltes Dokument erneut verarbeiten', 'original_file_not_found': 'Originaldatei nicht gefunden', 'new_embedding_ready': 'Neue Datei bereit für Embeddings'}}

for idioma, textos in UPLOAD_RAG_DOCUMENT_TEXTS.items():
    UPLOAD_RAG_TEXTS.setdefault(idioma, {}).update(textos)


UPLOAD_RAG_EMBEDDING_TEXTS = {'pt': {'embedding_summary': '### Resumo dos embeddings no pgvector', 'total_embeddings': 'Embeddings totais', 'active_embeddings': 'Embeddings ativos', 'inactive_embeddings': 'Embeddings inativos', 'documents_with_embeddings': 'Documentos com embeddings', 'active_documents': 'Documentos ativos', 'inactive_documents': 'Documentos inativos', 'summary_by_document': 'Ver resumo por documento', 'generate_embeddings': '### Gerar embeddings no pgvector', 'generate_embeddings_caption': 'Este botão lê o arquivo JSONL do documento selecionado, gera embeddings com Gemini e salva no Neon/PostgreSQL usando pgvector.', 'force_embedding_reprocessing': 'Forçar o reprocessamento dos embeddings, mesmo quando já existirem', 'generate_selected_embeddings': '🧠 Gerar embeddings do documento selecionado', 'missing_embedding_path': 'Este documento ainda não possui o caminho embedding_ready registrado.', 'existing_embeddings': 'Este documento já possui {total} embedding(s) no pgvector. Para gerar novamente, marque a opção de forçar o reprocessamento.', 'generating_embeddings': 'Gerando embeddings e salvando no pgvector...', 'pgvector_optimisation': '### Otimização do pgvector', 'pgvector_optimisation_caption': 'Cria índices no pgvector para acelerar buscas semânticas quando a base possuir muitos chunks.', 'create_index': '⚡ Criar ou validar índice pgvector', 'creating_index': 'Criando ou validando o índice pgvector no Neon/PostgreSQL...', 'semantic_search': '### Testar busca semântica no pgvector', 'search_question': 'Digite uma pergunta para buscar nos documentos vetorizados', 'chunk_quantity_mode': 'Modo de quantidade de chunks', 'automatic_mode': 'Automático pela INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantidade escolhida automaticamente pela INNA: {total} chunks', 'returned_chunks': 'Quantidade de chunks retornados', 'search_similar_chunks': '🔎 Buscar chunks mais semelhantes', 'searching_chunks': 'Gerando o embedding da pergunta e buscando no pgvector...', 'no_chunk_found': 'Nenhum chunk encontrado.', 'chunk': 'Chunk', 'category': 'Categoria', 'approx_similarity': 'Similaridade aproximada', 'general': 'geral', 'pgvector_distance': 'Distância pgvector', 'prioritised_categories': 'Categorias priorizadas', 'rag_score': 'Score RAG'}, 'en_us': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'es': {'embedding_summary': '### Resumen de embeddings en pgvector', 'total_embeddings': 'Embeddings totales', 'active_embeddings': 'Embeddings activos', 'inactive_embeddings': 'Embeddings inactivos', 'documents_with_embeddings': 'Documentos con embeddings', 'active_documents': 'Documentos activos', 'inactive_documents': 'Documentos inactivos', 'summary_by_document': 'Ver resumen por documento', 'generate_embeddings': '### Generar embeddings en pgvector', 'generate_embeddings_caption': 'Este botón lee el archivo JSONL del documento seleccionado, genera embeddings con Gemini y los guarda en Neon/PostgreSQL usando pgvector.', 'force_embedding_reprocessing': 'Forzar el reprocesamiento de los embeddings, aunque ya existan', 'generate_selected_embeddings': '🧠 Generar embeddings del documento seleccionado', 'missing_embedding_path': 'Este documento todavía no tiene registrado el camino embedding_ready.', 'existing_embeddings': 'Este documento ya posee {total} embedding(s) en pgvector. Para generarlos nuevamente, active el reprocesamiento.', 'generating_embeddings': 'Generando embeddings y guardándolos en pgvector...', 'pgvector_optimisation': '### Optimización de pgvector', 'pgvector_optimisation_caption': 'Crea índices en pgvector para acelerar búsquedas semánticas cuando la base contiene muchos chunks.', 'create_index': '⚡ Crear o validar índice pgvector', 'creating_index': 'Creando o validando el índice pgvector en Neon/PostgreSQL...', 'semantic_search': '### Probar búsqueda semántica en pgvector', 'search_question': 'Escriba una pregunta para buscar en los documentos vectorizados', 'chunk_quantity_mode': 'Modo de cantidad de chunks', 'automatic_mode': 'Automático por INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Cantidad elegida automáticamente por INNA: {total} chunks', 'returned_chunks': 'Cantidad de chunks devueltos', 'search_similar_chunks': '🔎 Buscar chunks más similares', 'searching_chunks': 'Generando el embedding de la pregunta y buscando en pgvector...', 'no_chunk_found': 'No se encontró ningún chunk.', 'chunk': 'Chunk', 'category': 'Categoría', 'approx_similarity': 'Similitud aproximada', 'general': 'general', 'pgvector_distance': 'Distancia pgvector', 'prioritised_categories': 'Categorías priorizadas', 'rag_score': 'Score RAG'}, 'fr': {'embedding_summary': '### Résumé des embeddings dans pgvector', 'total_embeddings': 'Total des embeddings', 'active_embeddings': 'Embeddings actifs', 'inactive_embeddings': 'Embeddings inactifs', 'documents_with_embeddings': 'Documents avec embeddings', 'active_documents': 'Documents actifs', 'inactive_documents': 'Documents inactifs', 'summary_by_document': 'Voir le résumé par document', 'generate_embeddings': '### Générer les embeddings dans pgvector', 'generate_embeddings_caption': 'Ce bouton lit le fichier JSONL du document sélectionné, génère des embeddings avec Gemini et les enregistre dans Neon/PostgreSQL avec pgvector.', 'force_embedding_reprocessing': 'Forcer le retraitement des embeddings même s’ils existent', 'generate_selected_embeddings': '🧠 Générer les embeddings du document sélectionné', 'missing_embedding_path': 'Ce document ne possède pas encore de chemin embedding_ready enregistré.', 'existing_embeddings': 'Ce document possède déjà {total} embedding(s) dans pgvector. Activez le retraitement forcé pour les générer à nouveau.', 'generating_embeddings': 'Génération et enregistrement des embeddings dans pgvector...', 'pgvector_optimisation': '### Optimisation de pgvector', 'pgvector_optimisation_caption': 'Crée des index pgvector pour accélérer les recherches sémantiques lorsque la base contient beaucoup de chunks.', 'create_index': '⚡ Créer ou valider l’index pgvector', 'creating_index': 'Création ou validation de l’index pgvector dans Neon/PostgreSQL...', 'semantic_search': '### Tester la recherche sémantique dans pgvector', 'search_question': 'Saisissez une question pour rechercher dans les documents vectorisés', 'chunk_quantity_mode': 'Mode de quantité de chunks', 'automatic_mode': 'Automatique par INNA', 'manual_mode': 'Manuel', 'automatic_quantity': 'Quantité choisie automatiquement par INNA : {total} chunks', 'returned_chunks': 'Nombre de chunks retournés', 'search_similar_chunks': '🔎 Rechercher les chunks les plus similaires', 'searching_chunks': 'Génération de l’embedding de la question et recherche dans pgvector...', 'no_chunk_found': 'Aucun chunk trouvé.', 'chunk': 'Chunk', 'category': 'Catégorie', 'approx_similarity': 'Similarité approximative', 'general': 'général', 'pgvector_distance': 'Distance pgvector', 'prioritised_categories': 'Catégories prioritaires', 'rag_score': 'Score RAG'}, 'de': {'embedding_summary': '### Embedding-Zusammenfassung in pgvector', 'total_embeddings': 'Embeddings insgesamt', 'active_embeddings': 'Aktive Embeddings', 'inactive_embeddings': 'Inaktive Embeddings', 'documents_with_embeddings': 'Dokumente mit Embeddings', 'active_documents': 'Aktive Dokumente', 'inactive_documents': 'Inaktive Dokumente', 'summary_by_document': 'Zusammenfassung je Dokument anzeigen', 'generate_embeddings': '### Embeddings in pgvector erzeugen', 'generate_embeddings_caption': 'Diese Schaltfläche liest die JSONL-Datei des ausgewählten Dokuments, erzeugt Embeddings mit Gemini und speichert sie mit pgvector in Neon/PostgreSQL.', 'force_embedding_reprocessing': 'Neuverarbeitung der Embeddings erzwingen, auch wenn sie bereits vorhanden sind', 'generate_selected_embeddings': '🧠 Embeddings für das ausgewählte Dokument erzeugen', 'missing_embedding_path': 'Für dieses Dokument ist noch kein embedding_ready-Pfad registriert.', 'existing_embeddings': 'Dieses Dokument besitzt bereits {total} Embedding(s) in pgvector. Aktivieren Sie die erzwungene Neuverarbeitung.', 'generating_embeddings': 'Embeddings werden erzeugt und in pgvector gespeichert...', 'pgvector_optimisation': '### pgvector-Optimierung', 'pgvector_optimisation_caption': 'Erstellt pgvector-Indizes, um semantische Suchen bei einer großen Anzahl von Chunks zu beschleunigen.', 'create_index': '⚡ pgvector-Index erstellen oder validieren', 'creating_index': 'pgvector-Index wird in Neon/PostgreSQL erstellt oder validiert...', 'semantic_search': '### Semantische Suche in pgvector testen', 'search_question': 'Geben Sie eine Frage ein, um in den vektorisierten Dokumenten zu suchen', 'chunk_quantity_mode': 'Modus der Chunk-Anzahl', 'automatic_mode': 'Automatisch durch INNA', 'manual_mode': 'Manuell', 'automatic_quantity': 'Von INNA automatisch gewählte Anzahl: {total} Chunks', 'returned_chunks': 'Anzahl zurückgegebener Chunks', 'search_similar_chunks': '🔎 Ähnlichste Chunks suchen', 'searching_chunks': 'Frage-Embedding wird erzeugt und pgvector durchsucht...', 'no_chunk_found': 'Kein Chunk gefunden.', 'chunk': 'Chunk', 'category': 'Kategorie', 'approx_similarity': 'Ungefähre Ähnlichkeit', 'general': 'allgemein', 'pgvector_distance': 'pgvector-Distanz', 'prioritised_categories': 'Priorisierte Kategorien', 'rag_score': 'RAG-Score'}, 'en_gb': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'it': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'ro': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'ua': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'ru': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'sa': {'embedding_summary': '### Embedding summary in pgvector', 'total_embeddings': 'Total embeddings', 'active_embeddings': 'Active embeddings', 'inactive_embeddings': 'Inactive embeddings', 'documents_with_embeddings': 'Documents with embeddings', 'active_documents': 'Active documents', 'inactive_documents': 'Inactive documents', 'summary_by_document': 'View summary by document', 'generate_embeddings': '### Generate embeddings in pgvector', 'generate_embeddings_caption': 'This button reads the selected document JSONL file, generates embeddings with Gemini and saves them to Neon/PostgreSQL using pgvector.', 'force_embedding_reprocessing': 'Force embedding reprocessing even when embeddings already exist', 'generate_selected_embeddings': '🧠 Generate embeddings for the selected document', 'missing_embedding_path': 'This document does not have a registered embedding_ready path yet.', 'existing_embeddings': 'This document already has {total} embedding(s) in pgvector. To generate them again, enable forced reprocessing.', 'generating_embeddings': 'Generating embeddings and saving them to pgvector...', 'pgvector_optimisation': '### pgvector optimisation', 'pgvector_optimisation_caption': 'Creates pgvector indexes to accelerate semantic searches when the knowledge base contains many chunks.', 'create_index': '⚡ Create or validate pgvector index', 'creating_index': 'Creating or validating the pgvector index in Neon/PostgreSQL...', 'semantic_search': '### Test semantic search in pgvector', 'search_question': 'Enter a question to search the vectorised documents', 'chunk_quantity_mode': 'Chunk quantity mode', 'automatic_mode': 'Automatic by INNA', 'manual_mode': 'Manual', 'automatic_quantity': 'Quantity automatically selected by INNA: {total} chunks', 'returned_chunks': 'Number of returned chunks', 'search_similar_chunks': '🔎 Search most similar chunks', 'searching_chunks': 'Generating the question embedding and searching pgvector...', 'no_chunk_found': 'No chunk was found.', 'chunk': 'Chunk', 'category': 'Category', 'approx_similarity': 'Approximate similarity', 'general': 'general', 'pgvector_distance': 'pgvector distance', 'prioritised_categories': 'Prioritised categories', 'rag_score': 'RAG score'}, 'ch': {'embedding_summary': '### Embedding-Zusammenfassung in pgvector', 'total_embeddings': 'Embeddings insgesamt', 'active_embeddings': 'Aktive Embeddings', 'inactive_embeddings': 'Inaktive Embeddings', 'documents_with_embeddings': 'Dokumente mit Embeddings', 'active_documents': 'Aktive Dokumente', 'inactive_documents': 'Inaktive Dokumente', 'summary_by_document': 'Zusammenfassung je Dokument anzeigen', 'generate_embeddings': '### Embeddings in pgvector erzeugen', 'generate_embeddings_caption': 'Diese Schaltfläche liest die JSONL-Datei des ausgewählten Dokuments, erzeugt Embeddings mit Gemini und speichert sie mit pgvector in Neon/PostgreSQL.', 'force_embedding_reprocessing': 'Neuverarbeitung der Embeddings erzwingen, auch wenn sie bereits vorhanden sind', 'generate_selected_embeddings': '🧠 Embeddings für das ausgewählte Dokument erzeugen', 'missing_embedding_path': 'Für dieses Dokument ist noch kein embedding_ready-Pfad registriert.', 'existing_embeddings': 'Dieses Dokument besitzt bereits {total} Embedding(s) in pgvector. Aktivieren Sie die erzwungene Neuverarbeitung.', 'generating_embeddings': 'Embeddings werden erzeugt und in pgvector gespeichert...', 'pgvector_optimisation': '### pgvector-Optimierung', 'pgvector_optimisation_caption': 'Erstellt pgvector-Indizes, um semantische Suchen bei einer großen Anzahl von Chunks zu beschleunigen.', 'create_index': '⚡ pgvector-Index erstellen oder validieren', 'creating_index': 'pgvector-Index wird in Neon/PostgreSQL erstellt oder validiert...', 'semantic_search': '### Semantische Suche in pgvector testen', 'search_question': 'Geben Sie eine Frage ein, um in den vektorisierten Dokumenten zu suchen', 'chunk_quantity_mode': 'Modus der Chunk-Anzahl', 'automatic_mode': 'Automatisch durch INNA', 'manual_mode': 'Manuell', 'automatic_quantity': 'Von INNA automatisch gewählte Anzahl: {total} Chunks', 'returned_chunks': 'Anzahl zurückgegebener Chunks', 'search_similar_chunks': '🔎 Ähnlichste Chunks suchen', 'searching_chunks': 'Frage-Embedding wird erzeugt und pgvector durchsucht...', 'no_chunk_found': 'Kein Chunk gefunden.', 'chunk': 'Chunk', 'category': 'Kategorie', 'approx_similarity': 'Ungefähre Ähnlichkeit', 'general': 'allgemein', 'pgvector_distance': 'pgvector-Distanz', 'prioritised_categories': 'Priorisierte Kategorien', 'rag_score': 'RAG-Score'}}

for idioma, textos in UPLOAD_RAG_EMBEDDING_TEXTS.items():
    UPLOAD_RAG_TEXTS.setdefault(idioma, {}).update(textos)


UPLOAD_RAG_FINAL_RESPONSE_TEXTS = {'pt': {'final_rag_response': '### Gerar resposta final da INNA com RAG', 'rag_user_id': 'Identificação do usuário para memória', 'rag_question': 'Pergunta para a INNA responder usando memória e documentos vetorizados', 'automatic_response_chunks': 'Usar quantidade automática de chunks na resposta', 'automatic_response_limit': 'A INNA usará automaticamente {total} chunks como limite.', 'response_context_chunks': 'Quantidade de chunks para o contexto da resposta', 'generate_final_response': '🤖 Gerar resposta final com RAG', 'generating_final_response': 'Buscando contexto no pgvector e gerando a resposta final da INNA...', 'inna_final_response': '#### 🤖 Resposta final da INNA'}, 'en_us': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'es': {'final_rag_response': '### Generar la respuesta final de INNA con RAG', 'rag_user_id': 'Identificación del usuario para la memoria', 'rag_question': 'Pregunta para que INNA responda usando memoria y documentos vectorizados', 'automatic_response_chunks': 'Usar una cantidad automática de chunks en la respuesta', 'automatic_response_limit': 'INNA utilizará automáticamente {total} chunks como límite.', 'response_context_chunks': 'Cantidad de chunks para el contexto de la respuesta', 'generate_final_response': '🤖 Generar respuesta final con RAG', 'generating_final_response': 'Buscando contexto en pgvector y generando la respuesta final de INNA...', 'inna_final_response': '#### 🤖 Respuesta final de INNA'}, 'fr': {'final_rag_response': '### Générer la réponse finale d’INNA avec RAG', 'rag_user_id': 'Identifiant utilisateur pour la mémoire', 'rag_question': 'Question à laquelle INNA doit répondre avec la mémoire et les documents vectorisés', 'automatic_response_chunks': 'Utiliser un nombre automatique de chunks dans la réponse', 'automatic_response_limit': 'INNA utilisera automatiquement {total} chunks comme limite.', 'response_context_chunks': 'Nombre de chunks pour le contexte de la réponse', 'generate_final_response': '🤖 Générer la réponse finale avec RAG', 'generating_final_response': 'Recherche du contexte dans pgvector et génération de la réponse finale d’INNA...', 'inna_final_response': '#### 🤖 Réponse finale d’INNA'}, 'de': {'final_rag_response': '### INNAs endgültige Antwort mit RAG erzeugen', 'rag_user_id': 'Benutzerkennung für den Speicher', 'rag_question': 'Frage, die INNA mit Speicher und vektorisierten Dokumenten beantworten soll', 'automatic_response_chunks': 'Automatische Chunk-Anzahl für die Antwort verwenden', 'automatic_response_limit': 'INNA verwendet automatisch {total} Chunks als Grenze.', 'response_context_chunks': 'Anzahl der Chunks für den Antwortkontext', 'generate_final_response': '🤖 Endgültige Antwort mit RAG erzeugen', 'generating_final_response': 'Kontext wird in pgvector gesucht und INNAs endgültige Antwort wird erzeugt...', 'inna_final_response': '#### 🤖 Endgültige Antwort von INNA'}, 'en_gb': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'it': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'ro': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'ua': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'ru': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'sa': {'final_rag_response': "### Generate INNA's final response with RAG", 'rag_user_id': 'User identifier for memory', 'rag_question': 'Question for INNA to answer using memory and vectorised documents', 'automatic_response_chunks': 'Use an automatic number of chunks in the response', 'automatic_response_limit': 'INNA will automatically use {total} chunks as the limit.', 'response_context_chunks': 'Number of chunks for the response context', 'generate_final_response': '🤖 Generate final response with RAG', 'generating_final_response': "Searching pgvector for context and generating INNA's final response...", 'inna_final_response': '#### 🤖 INNA final response'}, 'ch': {'final_rag_response': '### INNAs endgültige Antwort mit RAG erzeugen', 'rag_user_id': 'Benutzerkennung für den Speicher', 'rag_question': 'Frage, die INNA mit Speicher und vektorisierten Dokumenten beantworten soll', 'automatic_response_chunks': 'Automatische Chunk-Anzahl für die Antwort verwenden', 'automatic_response_limit': 'INNA verwendet automatisch {total} Chunks als Grenze.', 'response_context_chunks': 'Anzahl der Chunks für den Antwortkontext', 'generate_final_response': '🤖 Endgültige Antwort mit RAG erzeugen', 'generating_final_response': 'Kontext wird in pgvector gesucht und INNAs endgültige Antwort wird erzeugt...', 'inna_final_response': '#### 🤖 Endgültige Antwort von INNA'}}

for idioma, textos in UPLOAD_RAG_FINAL_RESPONSE_TEXTS.items():
    UPLOAD_RAG_TEXTS.setdefault(idioma, {}).update(textos)

# UPLOAD_RAG_NATIVE_SA_TEXTS

UPLOAD_RAG_NATIVE_SA_TEXTS = {
    "documents": {
        "file_size": "الحجم",
        "registered_documents": (
            "### المستندات المسجلة في Neon/PostgreSQL"
        ),
        "database_documents_error": (
            "تعذر تحميل المستندات من قاعدة البيانات"
        ),
        "no_registered_documents": (
            "لا توجد مستندات مسجلة بعد "
            "في Neon/PostgreSQL."
        ),
        "registered_documents_total": (
            "إجمالي المستندات المسجلة"
        ),
        "total_chunks": "إجمالي المقاطع",
        "processed": "تمت المعالجة",
        "extensions": "الامتدادات",
        "local_organisation": (
            "### التنظيم المحلي لملفات RAG"
        ),
        "local_uploads": "الملفات المرفوعة محلياً",
        "chunk_files": "ملفات المقاطع",
        "embedding_ready_jsonl": (
            "ملفات JSONL الجاهزة للتضمينات"
        ),
        "recent_local_files": (
            "عرض الملفات المحلية الحديثة"
        ),
        "recent_files_caption": (
            "يتم عرض أحدث 5 ملفات كحد أقصى "
            "من كل مجلد."
        ),
        "recent_uploads": "**الملفات المرفوعة حديثاً**",
        "recent_chunks": "**المقاطع الحديثة**",
        "recent_jsonl": "**ملفات JSONL الحديثة**",
        "archive_caption": (
            "تنقل الأرشفة الملفات القديمة إلى "
            "data/knowledge_base/archive. "
            "ولا يتم حذف أي ملف نهائياً."
        ),
        "files_to_keep": (
            "كم عدد الملفات الحديثة التي يجب الاحتفاظ "
            "بها في كل مجلد؟"
        ),
        "archive_old_files": (
            "🗂️ أرشفة الملفات المحلية القديمة"
        ),
        "document_status": (
            "### حالة المستند في قاعدة معرفة RAG"
        ),
        "select_status_document": (
            "اختر مستنداً لتفعيله أو تعطيله"
        ),
        "active_document": (
            "هذا المستند نشط في بحث RAG."
        ),
        "inactive_document": (
            "هذا المستند غير نشط وسيتم تجاهله "
            "في بحث RAG."
        ),
        "activate_document": "✅ تفعيل المستند",
        "deactivate_document": "🚫 تعطيل المستند",
        "reprocess_document": (
            "### إعادة معالجة المستند"
        ),
        "select_reprocess_document": (
            "اختر مستنداً لإعادة معالجته"
        ),
        "reprocess_selected": (
            "🔄 إعادة معالجة المستند المحدد"
        ),
        "original_file_not_found": (
            "لم يتم العثور على الملف الأصلي"
        ),
        "new_embedding_ready": (
            "ملف جديد جاهز للتضمينات"
        ),
    },
    "embeddings": {
        "embedding_summary": (
            "### ملخص التضمينات في pgvector"
        ),
        "total_embeddings": "إجمالي التضمينات",
        "active_embeddings": "التضمينات النشطة",
        "inactive_embeddings": "التضمينات غير النشطة",
        "documents_with_embeddings": (
            "المستندات التي تحتوي على تضمينات"
        ),
        "active_documents": "المستندات النشطة",
        "inactive_documents": "المستندات غير النشطة",
        "summary_by_document": (
            "عرض الملخص حسب المستند"
        ),
        "generate_embeddings": (
            "### إنشاء التضمينات في pgvector"
        ),
        "generate_embeddings_caption": (
            "يقرأ هذا الزر ملف JSONL للمستند المحدد، "
            "وينشئ التضمينات باستخدام Gemini، "
            "ثم يحفظها في Neon/PostgreSQL "
            "باستخدام pgvector."
        ),
        "force_embedding_reprocessing": (
            "فرض إعادة إنشاء التضمينات "
            "حتى لو كانت موجودة مسبقاً"
        ),
        "generate_selected_embeddings": (
            "🧠 إنشاء تضمينات المستند المحدد"
        ),
        "missing_embedding_path": (
            "لا يحتوي هذا المستند بعد على مسار "
            "embedding_ready مسجل."
        ),
        "existing_embeddings": (
            "يحتوي هذا المستند بالفعل على {total} "
            "تضمين في pgvector. ولإنشائها مرة أخرى، "
            "فعّل إعادة المعالجة الإجبارية."
        ),
        "generating_embeddings": (
            "جارٍ إنشاء التضمينات وحفظها "
            "في pgvector..."
        ),
        "pgvector_optimisation": (
            "### تحسين pgvector"
        ),
        "pgvector_optimisation_caption": (
            "ينشئ فهارس pgvector لتسريع البحث الدلالي "
            "عندما تحتوي القاعدة على عدد كبير من المقاطع."
        ),
        "create_index": (
            "⚡ إنشاء فهرس pgvector أو التحقق منه"
        ),
        "creating_index": (
            "جارٍ إنشاء فهرس pgvector أو التحقق منه "
            "في Neon/PostgreSQL..."
        ),
        "semantic_search": (
            "### اختبار البحث الدلالي في pgvector"
        ),
        "search_question": (
            "أدخل سؤالاً للبحث في المستندات المتجهة"
        ),
        "chunk_quantity_mode": (
            "وضع تحديد عدد المقاطع"
        ),
        "automatic_mode": "تلقائي بواسطة INNA",
        "manual_mode": "يدوي",
        "automatic_quantity": (
            "اختارت INNA تلقائياً {total} مقطعاً"
        ),
        "returned_chunks": (
            "عدد المقاطع المعادة"
        ),
        "search_similar_chunks": (
            "🔎 البحث عن أكثر المقاطع تشابهاً"
        ),
        "searching_chunks": (
            "جارٍ إنشاء تضمين السؤال "
            "والبحث في pgvector..."
        ),
        "no_chunk_found": (
            "لم يتم العثور على أي مقطع."
        ),
        "chunk": "المقطع",
        "category": "الفئة",
        "approx_similarity": (
            "التشابه التقريبي"
        ),
        "general": "عام",
        "pgvector_distance": "مسافة pgvector",
        "prioritised_categories": (
            "الفئات ذات الأولوية"
        ),
        "rag_score": "درجة RAG",
    },
    "final_response": {
        "final_rag_response": (
            "### إنشاء الإجابة النهائية لـ INNA باستخدام RAG"
        ),
        "rag_user_id": (
            "معرّف المستخدم للذاكرة"
        ),
        "rag_question": (
            "السؤال الذي يجب على INNA الإجابة عنه "
            "باستخدام الذاكرة والمستندات المتجهة"
        ),
        "automatic_response_chunks": (
            "استخدام عدد تلقائي من المقاطع "
            "في الإجابة"
        ),
        "automatic_response_limit": (
            "ستستخدم INNA تلقائياً {total} مقطعاً "
            "كحد أقصى."
        ),
        "response_context_chunks": (
            "عدد المقاطع في سياق الإجابة"
        ),
        "generate_final_response": (
            "🤖 إنشاء الإجابة النهائية باستخدام RAG"
        ),
        "generating_final_response": (
            "جارٍ البحث عن السياق في pgvector "
            "وإنشاء الإجابة النهائية لـ INNA..."
        ),
        "inna_final_response": (
            "#### 🤖 الإجابة النهائية لـ INNA"
        ),
    },
}

UPLOAD_RAG_DOCUMENT_TEXTS["sa"].update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["documents"]
)

UPLOAD_RAG_EMBEDDING_TEXTS["sa"].update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["embeddings"]
)

UPLOAD_RAG_FINAL_RESPONSE_TEXTS["sa"].update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["final_response"]
)

UPLOAD_RAG_TEXTS.setdefault(
    "sa",
    {},
).update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["documents"]
)

UPLOAD_RAG_TEXTS["sa"].update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["embeddings"]
)

UPLOAD_RAG_TEXTS["sa"].update(
    UPLOAD_RAG_NATIVE_SA_TEXTS["final_response"]
)

# UPLOAD_RAG_NATIVE_RO_TEXTS

UPLOAD_RAG_NATIVE_RO_TEXTS = {
    "documents": {
        "file_size": "Dimensiune",
        "registered_documents": (
            "### Documente înregistrate în Neon/PostgreSQL"
        ),
        "database_documents_error": (
            "Documentele din baza de date "
            "nu au putut fi încărcate"
        ),
        "no_registered_documents": (
            "Nu există încă documente înregistrate "
            "în Neon/PostgreSQL."
        ),
        "registered_documents_total": (
            "Total documente înregistrate"
        ),
        "total_chunks": "Total fragmente",
        "processed": "Procesate",
        "extensions": "Extensii",
        "local_organisation": (
            "### Organizarea locală a fișierelor RAG"
        ),
        "local_uploads": "Încărcări locale",
        "chunk_files": "Fișiere cu fragmente",
        "embedding_ready_jsonl": (
            "Fișiere JSONL pregătite pentru embeddinguri"
        ),
        "recent_local_files": (
            "Afișează fișierele locale recente"
        ),
        "recent_files_caption": (
            "Sunt afișate cel mult cele mai recente "
            "5 fișiere din fiecare dosar."
        ),
        "recent_uploads": "**Încărcări recente**",
        "recent_chunks": "**Fragmente recente**",
        "recent_jsonl": "**Fișiere JSONL recente**",
        "archive_caption": (
            "Arhivarea mută fișierele vechi în "
            "data/knowledge_base/archive. "
            "Nimic nu este șters definitiv."
        ),
        "files_to_keep": (
            "Câte fișiere recente trebuie păstrate "
            "în fiecare dosar?"
        ),
        "archive_old_files": (
            "🗂️ Arhivează fișierele locale vechi"
        ),
        "document_status": (
            "### Starea documentului în baza de cunoștințe RAG"
        ),
        "select_status_document": (
            "Selectează un document pentru activare "
            "sau dezactivare"
        ),
        "active_document": (
            "Acest document este ACTIV în căutarea RAG."
        ),
        "inactive_document": (
            "Acest document este INACTIV și va fi ignorat "
            "în căutarea RAG."
        ),
        "activate_document": "✅ Activează documentul",
        "deactivate_document": "🚫 Dezactivează documentul",
        "reprocess_document": (
            "### Reprocesează documentul"
        ),
        "select_reprocess_document": (
            "Selectează un document pentru reprocesare"
        ),
        "reprocess_selected": (
            "🔄 Reprocesează documentul selectat"
        ),
        "original_file_not_found": (
            "Fișierul original nu a fost găsit"
        ),
        "new_embedding_ready": (
            "Fișier nou pregătit pentru embeddinguri"
        ),
    },
    "embeddings": {
        "embedding_summary": (
            "### Rezumatul embeddingurilor din pgvector"
        ),
        "total_embeddings": "Total embeddinguri",
        "active_embeddings": "Embeddinguri active",
        "inactive_embeddings": "Embeddinguri inactive",
        "documents_with_embeddings": (
            "Documente cu embeddinguri"
        ),
        "active_documents": "Documente active",
        "inactive_documents": "Documente inactive",
        "summary_by_document": (
            "Afișează rezumatul pe document"
        ),
        "generate_embeddings": (
            "### Generează embeddinguri în pgvector"
        ),
        "generate_embeddings_caption": (
            "Acest buton citește fișierul JSONL al "
            "documentului selectat, generează embeddinguri "
            "cu Gemini și le salvează în Neon/PostgreSQL "
            "folosind pgvector."
        ),
        "force_embedding_reprocessing": (
            "Forțează regenerarea embeddingurilor "
            "chiar dacă acestea există deja"
        ),
        "generate_selected_embeddings": (
            "🧠 Generează embeddingurile documentului selectat"
        ),
        "missing_embedding_path": (
            "Acest document nu are încă înregistrată "
            "calea embedding_ready."
        ),
        "existing_embeddings": (
            "Acest document are deja {total} embedding(uri) "
            "în pgvector. Pentru a le genera din nou, "
            "activează reprocesarea forțată."
        ),
        "generating_embeddings": (
            "Se generează embeddingurile și se salvează "
            "în pgvector..."
        ),
        "pgvector_optimisation": (
            "### Optimizarea pgvector"
        ),
        "pgvector_optimisation_caption": (
            "Creează indexuri pgvector pentru accelerarea "
            "căutărilor semantice atunci când baza conține "
            "multe fragmente."
        ),
        "create_index": (
            "⚡ Creează sau validează indexul pgvector"
        ),
        "creating_index": (
            "Se creează sau se validează indexul pgvector "
            "în Neon/PostgreSQL..."
        ),
        "semantic_search": (
            "### Testează căutarea semantică în pgvector"
        ),
        "search_question": (
            "Introdu o întrebare pentru a căuta "
            "în documentele vectorizate"
        ),
        "chunk_quantity_mode": (
            "Modul pentru numărul de fragmente"
        ),
        "automatic_mode": "Automat prin INNA",
        "manual_mode": "Manual",
        "automatic_quantity": (
            "Număr selectat automat de INNA: "
            "{total} fragmente"
        ),
        "returned_chunks": (
            "Numărul de fragmente returnate"
        ),
        "search_similar_chunks": (
            "🔎 Caută cele mai similare fragmente"
        ),
        "searching_chunks": (
            "Se generează embeddingul întrebării "
            "și se caută în pgvector..."
        ),
        "no_chunk_found": (
            "Nu a fost găsit niciun fragment."
        ),
        "chunk": "Fragment",
        "category": "Categorie",
        "approx_similarity": (
            "Similaritate aproximativă"
        ),
        "general": "generală",
        "pgvector_distance": "Distanță pgvector",
        "prioritised_categories": (
            "Categorii prioritizate"
        ),
        "rag_score": "Scor RAG",
    },
    "final_response": {
        "final_rag_response": (
            "### Generează răspunsul final al INNA cu RAG"
        ),
        "rag_user_id": (
            "Identificatorul utilizatorului pentru memorie"
        ),
        "rag_question": (
            "Întrebarea la care INNA trebuie să răspundă "
            "folosind memoria și documentele vectorizate"
        ),
        "automatic_response_chunks": (
            "Folosește automat un număr de fragmente "
            "în răspuns"
        ),
        "automatic_response_limit": (
            "INNA va utiliza automat {total} fragmente "
            "drept limită."
        ),
        "response_context_chunks": (
            "Numărul de fragmente pentru contextul răspunsului"
        ),
        "generate_final_response": (
            "🤖 Generează răspunsul final cu RAG"
        ),
        "generating_final_response": (
            "Se caută contextul în pgvector și se generează "
            "răspunsul final al INNA..."
        ),
        "inna_final_response": (
            "#### 🤖 Răspunsul final al INNA"
        ),
    },
}

UPLOAD_RAG_DOCUMENT_TEXTS["ro"].update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["documents"]
)

UPLOAD_RAG_EMBEDDING_TEXTS["ro"].update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["embeddings"]
)

UPLOAD_RAG_FINAL_RESPONSE_TEXTS["ro"].update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["final_response"]
)

UPLOAD_RAG_TEXTS.setdefault(
    "ro",
    {},
).update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["documents"]
)

UPLOAD_RAG_TEXTS["ro"].update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["embeddings"]
)

UPLOAD_RAG_TEXTS["ro"].update(
    UPLOAD_RAG_NATIVE_RO_TEXTS["final_response"]
)

# UPLOAD_RAG_NATIVE_IT_TEXTS

UPLOAD_RAG_NATIVE_IT_TEXTS = {
    "documents": {
        "file_size": "Dimensione",
        "registered_documents": (
            "### Documenti registrati in Neon/PostgreSQL"
        ),
        "database_documents_error": (
            "Impossibile caricare i documenti dal database"
        ),
        "no_registered_documents": (
            "Nessun documento è ancora registrato "
            "in Neon/PostgreSQL."
        ),
        "registered_documents_total": (
            "Totale documenti registrati"
        ),
        "total_chunks": "Totale chunk",
        "processed": "Elaborati",
        "extensions": "Estensioni",
        "local_organisation": (
            "### Organizzazione locale dei file RAG"
        ),
        "local_uploads": "Caricamenti locali",
        "chunk_files": "File di chunk",
        "embedding_ready_jsonl": (
            "JSONL pronti per gli embedding"
        ),
        "recent_local_files": (
            "Visualizza i file locali recenti"
        ),
        "recent_files_caption": (
            "Sono mostrati al massimo i 5 file più recenti "
            "di ogni cartella."
        ),
        "recent_uploads": "**Caricamenti recenti**",
        "recent_chunks": "**Chunk recenti**",
        "recent_jsonl": "**File JSONL recenti**",
        "archive_caption": (
            "L’archiviazione sposta i vecchi file in "
            "data/knowledge_base/archive. "
            "Nessun file viene eliminato definitivamente."
        ),
        "files_to_keep": (
            "Quanti file recenti devono essere conservati "
            "in ogni cartella?"
        ),
        "archive_old_files": (
            "🗂️ Archivia i vecchi file locali"
        ),
        "document_status": (
            "### Stato del documento nella base RAG"
        ),
        "select_status_document": (
            "Seleziona un documento da attivare "
            "o disattivare"
        ),
        "active_document": (
            "Questo documento è ATTIVO nella ricerca RAG."
        ),
        "inactive_document": (
            "Questo documento è INATTIVO e verrà ignorato "
            "nella ricerca RAG."
        ),
        "activate_document": "✅ Attiva documento",
        "deactivate_document": "🚫 Disattiva documento",
        "reprocess_document": (
            "### Rielabora documento"
        ),
        "select_reprocess_document": (
            "Seleziona un documento da rielaborare"
        ),
        "reprocess_selected": (
            "🔄 Rielabora il documento selezionato"
        ),
        "original_file_not_found": (
            "File originale non trovato"
        ),
        "new_embedding_ready": (
            "Nuovo file pronto per gli embedding"
        ),
    },
    "embeddings": {
        "embedding_summary": (
            "### Riepilogo degli embedding in pgvector"
        ),
        "total_embeddings": "Embedding totali",
        "active_embeddings": "Embedding attivi",
        "inactive_embeddings": "Embedding inattivi",
        "documents_with_embeddings": (
            "Documenti con embedding"
        ),
        "active_documents": "Documenti attivi",
        "inactive_documents": "Documenti inattivi",
        "summary_by_document": (
            "Visualizza il riepilogo per documento"
        ),
        "generate_embeddings": (
            "### Genera embedding in pgvector"
        ),
        "generate_embeddings_caption": (
            "Questo pulsante legge il file JSONL del "
            "documento selezionato, genera embedding "
            "con Gemini e li salva in Neon/PostgreSQL "
            "utilizzando pgvector."
        ),
        "force_embedding_reprocessing": (
            "Forza la rigenerazione degli embedding "
            "anche quando esistono già"
        ),
        "generate_selected_embeddings": (
            "🧠 Genera gli embedding del documento selezionato"
        ),
        "missing_embedding_path": (
            "Questo documento non possiede ancora un "
            "percorso embedding_ready registrato."
        ),
        "existing_embeddings": (
            "Questo documento possiede già {total} "
            "embedding in pgvector. Per generarli di nuovo, "
            "attiva la rielaborazione forzata."
        ),
        "generating_embeddings": (
            "Generazione degli embedding e salvataggio "
            "in pgvector..."
        ),
        "pgvector_optimisation": (
            "### Ottimizzazione di pgvector"
        ),
        "pgvector_optimisation_caption": (
            "Crea indici pgvector per accelerare le ricerche "
            "semantiche quando la base contiene molti chunk."
        ),
        "create_index": (
            "⚡ Crea o convalida l’indice pgvector"
        ),
        "creating_index": (
            "Creazione o convalida dell’indice pgvector "
            "in Neon/PostgreSQL..."
        ),
        "semantic_search": (
            "### Verifica la ricerca semantica in pgvector"
        ),
        "search_question": (
            "Inserisci una domanda per cercare "
            "nei documenti vettorializzati"
        ),
        "chunk_quantity_mode": (
            "Modalità quantità di chunk"
        ),
        "automatic_mode": "Automatico tramite INNA",
        "manual_mode": "Manuale",
        "automatic_quantity": (
            "Quantità scelta automaticamente da INNA: "
            "{total} chunk"
        ),
        "returned_chunks": (
            "Numero di chunk restituiti"
        ),
        "search_similar_chunks": (
            "🔎 Cerca i chunk più simili"
        ),
        "searching_chunks": (
            "Generazione dell’embedding della domanda "
            "e ricerca in pgvector..."
        ),
        "no_chunk_found": "Nessun chunk trovato.",
        "chunk": "Chunk",
        "category": "Categoria",
        "approx_similarity": (
            "Similarità approssimativa"
        ),
        "general": "generale",
        "pgvector_distance": "Distanza pgvector",
        "prioritised_categories": (
            "Categorie prioritarie"
        ),
        "rag_score": "Punteggio RAG",
    },
    "final_response": {
        "final_rag_response": (
            "### Genera la risposta finale di INNA con RAG"
        ),
        "rag_user_id": (
            "Identificativo utente per la memoria"
        ),
        "rag_question": (
            "Domanda a cui INNA deve rispondere usando "
            "la memoria e i documenti vettorializzati"
        ),
        "automatic_response_chunks": (
            "Usa un numero automatico di chunk "
            "nella risposta"
        ),
        "automatic_response_limit": (
            "INNA utilizzerà automaticamente {total} "
            "chunk come limite."
        ),
        "response_context_chunks": (
            "Numero di chunk per il contesto della risposta"
        ),
        "generate_final_response": (
            "🤖 Genera la risposta finale con RAG"
        ),
        "generating_final_response": (
            "Ricerca del contesto in pgvector e generazione "
            "della risposta finale di INNA..."
        ),
        "inna_final_response": (
            "#### 🤖 Risposta finale di INNA"
        ),
    },
}

UPLOAD_RAG_DOCUMENT_TEXTS["it"].update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["documents"]
)

UPLOAD_RAG_EMBEDDING_TEXTS["it"].update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["embeddings"]
)

UPLOAD_RAG_FINAL_RESPONSE_TEXTS["it"].update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["final_response"]
)

UPLOAD_RAG_TEXTS.setdefault(
    "it",
    {},
).update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["documents"]
)

UPLOAD_RAG_TEXTS["it"].update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["embeddings"]
)

UPLOAD_RAG_TEXTS["it"].update(
    UPLOAD_RAG_NATIVE_IT_TEXTS["final_response"]
)

# UPLOAD_RAG_NATIVE_RU_UA_TEXTS

UPLOAD_RAG_NATIVE_RU_UA_TEXTS = {
    "ru": {
        "documents": {
            "file_size": "Размер",
            "registered_documents": (
                "### Документы, зарегистрированные "
                "в Neon/PostgreSQL"
            ),
            "database_documents_error": (
                "Не удалось загрузить документы "
                "из базы данных"
            ),
            "no_registered_documents": (
                "В Neon/PostgreSQL пока нет "
                "зарегистрированных документов."
            ),
            "registered_documents_total": (
                "Всего зарегистрированных документов"
            ),
            "total_chunks": "Всего фрагментов",
            "processed": "Обработано",
            "extensions": "Расширения",
            "local_organisation": (
                "### Локальная организация файлов RAG"
            ),
            "local_uploads": "Локальные загрузки",
            "chunk_files": "Файлы фрагментов",
            "embedding_ready_jsonl": (
                "JSONL, готовые для эмбеддингов"
            ),
            "recent_local_files": (
                "Показать последние локальные файлы"
            ),
            "recent_files_caption": (
                "Показано не более 5 последних файлов "
                "из каждой папки."
            ),
            "recent_uploads": "**Последние загрузки**",
            "recent_chunks": "**Последние фрагменты**",
            "recent_jsonl": "**Последние файлы JSONL**",
            "archive_caption": (
                "При архивировании старые файлы "
                "перемещаются в "
                "data/knowledge_base/archive. "
                "Они не удаляются окончательно."
            ),
            "files_to_keep": (
                "Сколько последних файлов нужно "
                "сохранять в каждой папке?"
            ),
            "archive_old_files": (
                "🗂️ Архивировать старые локальные файлы"
            ),
            "document_status": (
                "### Состояние документа в базе знаний RAG"
            ),
            "select_status_document": (
                "Выберите документ для включения "
                "или отключения"
            ),
            "active_document": (
                "Этот документ АКТИВЕН в поиске RAG."
            ),
            "inactive_document": (
                "Этот документ НЕАКТИВЕН и будет "
                "игнорироваться в поиске RAG."
            ),
            "activate_document": "✅ Активировать документ",
            "deactivate_document": (
                "🚫 Деактивировать документ"
            ),
            "reprocess_document": (
                "### Повторная обработка документа"
            ),
            "select_reprocess_document": (
                "Выберите документ для повторной обработки"
            ),
            "reprocess_selected": (
                "🔄 Повторно обработать выбранный документ"
            ),
            "original_file_not_found": (
                "Исходный файл не найден"
            ),
            "new_embedding_ready": (
                "Новый файл готов для эмбеддингов"
            ),
        },
        "embeddings": {
            "embedding_summary": (
                "### Сводка эмбеддингов в pgvector"
            ),
            "total_embeddings": "Всего эмбеддингов",
            "active_embeddings": "Активные эмбеддинги",
            "inactive_embeddings": "Неактивные эмбеддинги",
            "documents_with_embeddings": (
                "Документы с эмбеддингами"
            ),
            "active_documents": "Активные документы",
            "inactive_documents": "Неактивные документы",
            "summary_by_document": (
                "Показать сводку по документам"
            ),
            "generate_embeddings": (
                "### Создание эмбеддингов в pgvector"
            ),
            "generate_embeddings_caption": (
                "Эта кнопка читает JSONL выбранного "
                "документа, создаёт эмбеддинги с Gemini "
                "и сохраняет их в Neon/PostgreSQL "
                "с помощью pgvector."
            ),
            "force_embedding_reprocessing": (
                "Принудительно пересоздать эмбеддинги, "
                "даже если они уже существуют"
            ),
            "generate_selected_embeddings": (
                "🧠 Создать эмбеддинги выбранного документа"
            ),
            "missing_embedding_path": (
                "Для этого документа ещё не указан "
                "путь embedding_ready."
            ),
            "existing_embeddings": (
                "Для этого документа уже существует "
                "{total} эмбеддинг(ов) в pgvector. "
                "Чтобы создать их заново, включите "
                "принудительную повторную обработку."
            ),
            "generating_embeddings": (
                "Создание эмбеддингов и сохранение "
                "в pgvector..."
            ),
            "pgvector_optimisation": (
                "### Оптимизация pgvector"
            ),
            "pgvector_optimisation_caption": (
                "Создаёт индексы pgvector для ускорения "
                "семантического поиска при большом "
                "количестве фрагментов."
            ),
            "create_index": (
                "⚡ Создать или проверить индекс pgvector"
            ),
            "creating_index": (
                "Создание или проверка индекса pgvector "
                "в Neon/PostgreSQL..."
            ),
            "semantic_search": (
                "### Проверка семантического поиска "
                "в pgvector"
            ),
            "search_question": (
                "Введите вопрос для поиска "
                "в векторизованных документах"
            ),
            "chunk_quantity_mode": (
                "Режим количества фрагментов"
            ),
            "automatic_mode": "Автоматически — INNA",
            "manual_mode": "Вручную",
            "automatic_quantity": (
                "INNA автоматически выбрала "
                "{total} фрагмент(ов)"
            ),
            "returned_chunks": (
                "Количество возвращаемых фрагментов"
            ),
            "search_similar_chunks": (
                "🔎 Найти наиболее похожие фрагменты"
            ),
            "searching_chunks": (
                "Создание эмбеддинга вопроса "
                "и поиск в pgvector..."
            ),
            "no_chunk_found": "Фрагменты не найдены.",
            "chunk": "Фрагмент",
            "category": "Категория",
            "approx_similarity": (
                "Приблизительное сходство"
            ),
            "general": "общая",
            "pgvector_distance": "Расстояние pgvector",
            "prioritised_categories": (
                "Приоритетные категории"
            ),
            "rag_score": "Оценка RAG",
        },
        "final_response": {
            "final_rag_response": (
                "### Создание итогового ответа INNA с RAG"
            ),
            "rag_user_id": (
                "Идентификатор пользователя для памяти"
            ),
            "rag_question": (
                "Вопрос, на который INNA должна ответить "
                "с использованием памяти и "
                "векторизованных документов"
            ),
            "automatic_response_chunks": (
                "Автоматически выбирать количество "
                "фрагментов для ответа"
            ),
            "automatic_response_limit": (
                "INNA автоматически использует "
                "{total} фрагмент(ов) как предел."
            ),
            "response_context_chunks": (
                "Количество фрагментов в контексте ответа"
            ),
            "generate_final_response": (
                "🤖 Создать итоговый ответ с RAG"
            ),
            "generating_final_response": (
                "Поиск контекста в pgvector "
                "и создание итогового ответа INNA..."
            ),
            "inna_final_response": (
                "#### 🤖 Итоговый ответ INNA"
            ),
        },
    },
    "ua": {
        "documents": {
            "file_size": "Розмір",
            "registered_documents": (
                "### Документи, зареєстровані "
                "в Neon/PostgreSQL"
            ),
            "database_documents_error": (
                "Не вдалося завантажити документи "
                "з бази даних"
            ),
            "no_registered_documents": (
                "У Neon/PostgreSQL ще немає "
                "зареєстрованих документів."
            ),
            "registered_documents_total": (
                "Усього зареєстрованих документів"
            ),
            "total_chunks": "Усього фрагментів",
            "processed": "Оброблено",
            "extensions": "Розширення",
            "local_organisation": (
                "### Локальна організація файлів RAG"
            ),
            "local_uploads": "Локальні завантаження",
            "chunk_files": "Файли фрагментів",
            "embedding_ready_jsonl": (
                "JSONL, готові для ембеддингів"
            ),
            "recent_local_files": (
                "Переглянути останні локальні файли"
            ),
            "recent_files_caption": (
                "Показано не більше 5 останніх файлів "
                "з кожної папки."
            ),
            "recent_uploads": "**Останні завантаження**",
            "recent_chunks": "**Останні фрагменти**",
            "recent_jsonl": "**Останні файли JSONL**",
            "archive_caption": (
                "Під час архівування старі файли "
                "переміщуються до "
                "data/knowledge_base/archive. "
                "Вони не видаляються остаточно."
            ),
            "files_to_keep": (
                "Скільки останніх файлів потрібно "
                "зберігати в кожній папці?"
            ),
            "archive_old_files": (
                "🗂️ Архівувати старі локальні файли"
            ),
            "document_status": (
                "### Стан документа в базі знань RAG"
            ),
            "select_status_document": (
                "Виберіть документ для активації "
                "або деактивації"
            ),
            "active_document": (
                "Цей документ АКТИВНИЙ у пошуку RAG."
            ),
            "inactive_document": (
                "Цей документ НЕАКТИВНИЙ і буде "
                "ігноруватися в пошуку RAG."
            ),
            "activate_document": "✅ Активувати документ",
            "deactivate_document": (
                "🚫 Деактивувати документ"
            ),
            "reprocess_document": (
                "### Повторна обробка документа"
            ),
            "select_reprocess_document": (
                "Виберіть документ для повторної обробки"
            ),
            "reprocess_selected": (
                "🔄 Повторно обробити вибраний документ"
            ),
            "original_file_not_found": (
                "Початковий файл не знайдено"
            ),
            "new_embedding_ready": (
                "Новий файл готовий для ембеддингів"
            ),
        },
        "embeddings": {
            "embedding_summary": (
                "### Зведення ембеддингів у pgvector"
            ),
            "total_embeddings": "Усього ембеддингів",
            "active_embeddings": "Активні ембеддинги",
            "inactive_embeddings": "Неактивні ембеддинги",
            "documents_with_embeddings": (
                "Документи з ембеддингами"
            ),
            "active_documents": "Активні документи",
            "inactive_documents": "Неактивні документи",
            "summary_by_document": (
                "Переглянути зведення за документами"
            ),
            "generate_embeddings": (
                "### Створення ембеддингів у pgvector"
            ),
            "generate_embeddings_caption": (
                "Ця кнопка читає JSONL вибраного документа, "
                "створює ембеддинги за допомогою Gemini "
                "і зберігає їх у Neon/PostgreSQL "
                "через pgvector."
            ),
            "force_embedding_reprocessing": (
                "Примусово повторно створити ембеддинги, "
                "навіть якщо вони вже існують"
            ),
            "generate_selected_embeddings": (
                "🧠 Створити ембеддинги вибраного документа"
            ),
            "missing_embedding_path": (
                "Для цього документа ще не зареєстровано "
                "шлях embedding_ready."
            ),
            "existing_embeddings": (
                "Для цього документа вже існує "
                "{total} ембеддинг(ів) у pgvector. "
                "Щоб створити їх повторно, увімкніть "
                "примусову повторну обробку."
            ),
            "generating_embeddings": (
                "Створення ембеддингів і збереження "
                "у pgvector..."
            ),
            "pgvector_optimisation": (
                "### Оптимізація pgvector"
            ),
            "pgvector_optimisation_caption": (
                "Створює індекси pgvector для прискорення "
                "семантичного пошуку за великої "
                "кількості фрагментів."
            ),
            "create_index": (
                "⚡ Створити або перевірити індекс pgvector"
            ),
            "creating_index": (
                "Створення або перевірка індексу pgvector "
                "у Neon/PostgreSQL..."
            ),
            "semantic_search": (
                "### Перевірка семантичного пошуку "
                "у pgvector"
            ),
            "search_question": (
                "Введіть запитання для пошуку "
                "у векторизованих документах"
            ),
            "chunk_quantity_mode": (
                "Режим кількості фрагментів"
            ),
            "automatic_mode": "Автоматично — INNA",
            "manual_mode": "Вручну",
            "automatic_quantity": (
                "INNA автоматично вибрала "
                "{total} фрагмент(ів)"
            ),
            "returned_chunks": (
                "Кількість повернених фрагментів"
            ),
            "search_similar_chunks": (
                "🔎 Знайти найбільш схожі фрагменти"
            ),
            "searching_chunks": (
                "Створення ембеддинга запитання "
                "та пошук у pgvector..."
            ),
            "no_chunk_found": "Фрагментів не знайдено.",
            "chunk": "Фрагмент",
            "category": "Категорія",
            "approx_similarity": (
                "Приблизна схожість"
            ),
            "general": "загальна",
            "pgvector_distance": "Відстань pgvector",
            "prioritised_categories": (
                "Пріоритетні категорії"
            ),
            "rag_score": "Оцінка RAG",
        },
        "final_response": {
            "final_rag_response": (
                "### Створення підсумкової відповіді "
                "INNA з RAG"
            ),
            "rag_user_id": (
                "Ідентифікатор користувача для пам’яті"
            ),
            "rag_question": (
                "Запитання, на яке INNA має відповісти "
                "з використанням пам’яті та "
                "векторизованих документів"
            ),
            "automatic_response_chunks": (
                "Автоматично визначати кількість "
                "фрагментів у відповіді"
            ),
            "automatic_response_limit": (
                "INNA автоматично використає "
                "{total} фрагмент(ів) як обмеження."
            ),
            "response_context_chunks": (
                "Кількість фрагментів у контексті відповіді"
            ),
            "generate_final_response": (
                "🤖 Створити підсумкову відповідь з RAG"
            ),
            "generating_final_response": (
                "Пошук контексту в pgvector "
                "і створення підсумкової відповіді INNA..."
            ),
            "inna_final_response": (
                "#### 🤖 Підсумкова відповідь INNA"
            ),
        },
    },
}

for idioma, catalogos in (
    UPLOAD_RAG_NATIVE_RU_UA_TEXTS.items()
):
    documentos = catalogos["documents"]
    embeddings = catalogos["embeddings"]
    resposta_final = catalogos["final_response"]

    UPLOAD_RAG_DOCUMENT_TEXTS[
        idioma
    ].update(
        documentos
    )

    UPLOAD_RAG_EMBEDDING_TEXTS[
        idioma
    ].update(
        embeddings
    )

    UPLOAD_RAG_FINAL_RESPONSE_TEXTS[
        idioma
    ].update(
        resposta_final
    )

    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        documentos
    )

    UPLOAD_RAG_TEXTS[
        idioma
    ].update(
        embeddings
    )

    UPLOAD_RAG_TEXTS[
        idioma
    ].update(
        resposta_final
    )

UPLOAD_RAG_TEXTS["ch"] = UPLOAD_RAG_TEXTS["de"].copy()

# UPLOAD_RAG_RUNTIME_VISUAL_TEXTS

UPLOAD_RAG_RUNTIME_VISUAL_TEXTS = {
    "pt": {
        "uploaded_documents": "### Documentos enviados",
        "no_uploaded_documents": (
            "Nenhum documento enviado ainda."
        ),
        "generated_chunk_files": (
            "### Arquivos de chunks gerados"
        ),
        "no_generated_chunk_files": (
            "Nenhum arquivo de chunks gerado ainda."
        ),
        "embedding_ready_files": (
            "### Arquivos prontos para embeddings"
        ),
        "no_embedding_ready_files": (
            "Nenhum arquivo pronto para embeddings "
            "gerado ainda."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} caracteres | "
            "Categoria: {category}"
        ),
        "chunk_text": "Texto do chunk",
        "chunk_preview_limit": (
            "Foram gerados {total} chunks. "
            "Exibindo apenas os 5 primeiros."
        ),
        "preview_generation_failed": (
            "Arquivo salvo, mas não foi possível "
            "gerar prévia ou chunks."
        ),
    },
    "en_us": {
        "uploaded_documents": "### Uploaded documents",
        "no_uploaded_documents": (
            "No documents have been uploaded yet."
        ),
        "generated_chunk_files": (
            "### Generated chunk files"
        ),
        "no_generated_chunk_files": (
            "No chunk files have been generated yet."
        ),
        "embedding_ready_files": (
            "### Files ready for embeddings"
        ),
        "no_embedding_ready_files": (
            "No embedding-ready files have been "
            "generated yet."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} characters | "
            "Category: {category}"
        ),
        "chunk_text": "Chunk text",
        "chunk_preview_limit": (
            "{total} chunks were generated. "
            "Only the first 5 are shown."
        ),
        "preview_generation_failed": (
            "The file was saved, but its preview or "
            "chunks could not be generated."
        ),
    },
    "en_gb": {
        "uploaded_documents": "### Uploaded documents",
        "no_uploaded_documents": (
            "No documents have been uploaded yet."
        ),
        "generated_chunk_files": (
            "### Generated chunk files"
        ),
        "no_generated_chunk_files": (
            "No chunk files have been generated yet."
        ),
        "embedding_ready_files": (
            "### Files ready for embeddings"
        ),
        "no_embedding_ready_files": (
            "No embedding-ready files have been "
            "generated yet."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} characters | "
            "Category: {category}"
        ),
        "chunk_text": "Chunk text",
        "chunk_preview_limit": (
            "{total} chunks were generated. "
            "Only the first 5 are shown."
        ),
        "preview_generation_failed": (
            "The file was saved, but its preview or "
            "chunks could not be generated."
        ),
    },
    "es": {
        "uploaded_documents": "### Documentos enviados",
        "no_uploaded_documents": (
            "Todavía no se ha enviado ningún documento."
        ),
        "generated_chunk_files": (
            "### Archivos de chunks generados"
        ),
        "no_generated_chunk_files": (
            "Todavía no se ha generado ningún archivo "
            "de chunks."
        ),
        "embedding_ready_files": (
            "### Archivos preparados para embeddings"
        ),
        "no_embedding_ready_files": (
            "Todavía no se ha generado ningún archivo "
            "preparado para embeddings."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} caracteres | "
            "Categoría: {category}"
        ),
        "chunk_text": "Texto del chunk",
        "chunk_preview_limit": (
            "Se generaron {total} chunks. "
            "Solo se muestran los primeros 5."
        ),
        "preview_generation_failed": (
            "El archivo se guardó, pero no fue posible "
            "generar la vista previa o los chunks."
        ),
    },
    "fr": {
        "uploaded_documents": "### Documents téléversés",
        "no_uploaded_documents": (
            "Aucun document n’a encore été téléversé."
        ),
        "generated_chunk_files": (
            "### Fichiers de chunks générés"
        ),
        "no_generated_chunk_files": (
            "Aucun fichier de chunks n’a encore "
            "été généré."
        ),
        "embedding_ready_files": (
            "### Fichiers prêts pour les embeddings"
        ),
        "no_embedding_ready_files": (
            "Aucun fichier prêt pour les embeddings "
            "n’a encore été généré."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} caractères | "
            "Catégorie : {category}"
        ),
        "chunk_text": "Texte du chunk",
        "chunk_preview_limit": (
            "{total} chunks ont été générés. "
            "Seuls les 5 premiers sont affichés."
        ),
        "preview_generation_failed": (
            "Le fichier a été enregistré, mais son aperçu "
            "ou ses chunks n’ont pas pu être générés."
        ),
    },
    "de": {
        "uploaded_documents": "### Hochgeladene Dokumente",
        "no_uploaded_documents": (
            "Noch keine Dokumente hochgeladen."
        ),
        "generated_chunk_files": (
            "### Erzeugte Chunk-Dateien"
        ),
        "no_generated_chunk_files": (
            "Noch keine Chunk-Dateien erzeugt."
        ),
        "embedding_ready_files": (
            "### Für Embeddings vorbereitete Dateien"
        ),
        "no_embedding_ready_files": (
            "Noch keine für Embeddings vorbereiteten "
            "Dateien erzeugt."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} Zeichen | "
            "Kategorie: {category}"
        ),
        "chunk_text": "Chunk-Text",
        "chunk_preview_limit": (
            "{total} Chunks wurden erzeugt. "
            "Nur die ersten 5 werden angezeigt."
        ),
        "preview_generation_failed": (
            "Die Datei wurde gespeichert, aber Vorschau "
            "oder Chunks konnten nicht erzeugt werden."
        ),
    },
    "it": {
        "uploaded_documents": "### Documenti caricati",
        "no_uploaded_documents": (
            "Nessun documento è stato ancora caricato."
        ),
        "generated_chunk_files": (
            "### File di chunk generati"
        ),
        "no_generated_chunk_files": (
            "Nessun file di chunk è stato ancora generato."
        ),
        "embedding_ready_files": (
            "### File pronti per gli embedding"
        ),
        "no_embedding_ready_files": (
            "Nessun file pronto per gli embedding è stato "
            "ancora generato."
        ),
        "chunk_preview": (
            "Chunk {index} | {characters} caratteri | "
            "Categoria: {category}"
        ),
        "chunk_text": "Testo del chunk",
        "chunk_preview_limit": (
            "Sono stati generati {total} chunk. "
            "Vengono mostrati solo i primi 5."
        ),
        "preview_generation_failed": (
            "Il file è stato salvato, ma non è stato "
            "possibile generare anteprima o chunk."
        ),
    },
    "ro": {
        "uploaded_documents": "### Documente încărcate",
        "no_uploaded_documents": (
            "Nu a fost încă încărcat niciun document."
        ),
        "generated_chunk_files": (
            "### Fișiere de fragmente generate"
        ),
        "no_generated_chunk_files": (
            "Nu a fost încă generat niciun fișier "
            "de fragmente."
        ),
        "embedding_ready_files": (
            "### Fișiere pregătite pentru embeddinguri"
        ),
        "no_embedding_ready_files": (
            "Nu a fost încă generat niciun fișier "
            "pregătit pentru embeddinguri."
        ),
        "chunk_preview": (
            "Fragment {index} | {characters} caractere | "
            "Categorie: {category}"
        ),
        "chunk_text": "Textul fragmentului",
        "chunk_preview_limit": (
            "Au fost generate {total} fragmente. "
            "Sunt afișate doar primele 5."
        ),
        "preview_generation_failed": (
            "Fișierul a fost salvat, dar previzualizarea "
            "sau fragmentele nu au putut fi generate."
        ),
    },
    "ua": {
        "uploaded_documents": "### Завантажені документи",
        "no_uploaded_documents": (
            "Документи ще не завантажено."
        ),
        "generated_chunk_files": (
            "### Створені файли фрагментів"
        ),
        "no_generated_chunk_files": (
            "Файли фрагментів ще не створено."
        ),
        "embedding_ready_files": (
            "### Файли, готові до створення векторів"
        ),
        "no_embedding_ready_files": (
            "Файли, готові до створення векторів, "
            "ще не створено."
        ),
        "chunk_preview": (
            "Фрагмент {index} | {characters} символів | "
            "Категорія: {category}"
        ),
        "chunk_text": "Текст фрагмента",
        "chunk_preview_limit": (
            "Створено фрагментів: {total}. "
            "Показано лише перші 5."
        ),
        "preview_generation_failed": (
            "Файл збережено, але не вдалося створити "
            "попередній перегляд або фрагменти."
        ),
    },
    "ru": {
        "uploaded_documents": "### Загруженные документы",
        "no_uploaded_documents": (
            "Документы ещё не загружены."
        ),
        "generated_chunk_files": (
            "### Созданные файлы фрагментов"
        ),
        "no_generated_chunk_files": (
            "Файлы фрагментов ещё не созданы."
        ),
        "embedding_ready_files": (
            "### Файлы, готовые для эмбеддингов"
        ),
        "no_embedding_ready_files": (
            "Файлы, готовые для эмбеддингов, "
            "ещё не созданы."
        ),
        "chunk_preview": (
            "Фрагмент {index} | {characters} символов | "
            "Категория: {category}"
        ),
        "chunk_text": "Текст фрагмента",
        "chunk_preview_limit": (
            "Создано фрагментов: {total}. "
            "Показаны только первые 5."
        ),
        "preview_generation_failed": (
            "Файл сохранён, но не удалось создать "
            "предварительный просмотр или фрагменты."
        ),
    },
    "sa": {
        "uploaded_documents": "### المستندات المرفوعة",
        "no_uploaded_documents": (
            "لم يتم رفع أي مستند بعد."
        ),
        "generated_chunk_files": (
            "### ملفات المقاطع التي تم إنشاؤها"
        ),
        "no_generated_chunk_files": (
            "لم يتم إنشاء أي ملف مقاطع بعد."
        ),
        "embedding_ready_files": (
            "### ملفات جاهزة للتضمينات"
        ),
        "no_embedding_ready_files": (
            "لم يتم إنشاء أي ملف جاهز للتضمينات بعد."
        ),
        "chunk_preview": (
            "المقطع {index} | {characters} حرفاً | "
            "الفئة: {category}"
        ),
        "chunk_text": "نص المقطع",
        "chunk_preview_limit": (
            "تم إنشاء {total} مقطعاً. "
            "يتم عرض أول 5 فقط."
        ),
        "preview_generation_failed": (
            "تم حفظ الملف، ولكن تعذر إنشاء المعاينة "
            "أو المقاطع."
        ),
    },
}

UPLOAD_RAG_RUNTIME_VISUAL_TEXTS["ch"] = {
    key: value
    for key, value
    in UPLOAD_RAG_RUNTIME_VISUAL_TEXTS["de"].items()
}

for idioma, textos in (
    UPLOAD_RAG_RUNTIME_VISUAL_TEXTS.items()
):
    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        textos
    )


UPLOAD_RAG_SOURCE_TEXTS = {
    "pt": {
        "sources_used": "#### 📚 Fontes usadas pela INNA",
        "no_context_used": (
            "Nenhum contexto foi usado na resposta."
        ),
        "sources_caption": (
            "Abaixo estão os trechos da base RAG que "
            "ajudaram a INNA a montar a resposta."
        ),
        "source": "Fonte",
        "similarity": "Similaridade",
        "document": "Documento",
        "context_passage": (
            "Trecho usado como contexto"
        ),
    },
    "en_us": {
        "sources_used": "#### 📚 Sources used by INNA",
        "no_context_used": (
            "No context was used in the response."
        ),
        "sources_caption": (
            "The passages below were retrieved from "
            "the RAG knowledge base and helped INNA "
            "build the response."
        ),
        "source": "Source",
        "similarity": "Similarity",
        "document": "Document",
        "context_passage": (
            "Passage used as context"
        ),
    },
    "es": {
        "sources_used": (
            "#### 📚 Fuentes utilizadas por INNA"
        ),
        "no_context_used": (
            "No se utilizó ningún contexto "
            "en la respuesta."
        ),
        "sources_caption": (
            "Los siguientes fragmentos de la base RAG "
            "ayudaron a INNA a generar la respuesta."
        ),
        "source": "Fuente",
        "similarity": "Similitud",
        "document": "Documento",
        "context_passage": (
            "Fragmento utilizado como contexto"
        ),
    },
    "fr": {
        "sources_used": (
            "#### 📚 Sources utilisées par INNA"
        ),
        "no_context_used": (
            "Aucun contexte n’a été utilisé "
            "dans la réponse."
        ),
        "sources_caption": (
            "Les extraits suivants de la base RAG "
            "ont aidé INNA à construire la réponse."
        ),
        "source": "Source",
        "similarity": "Similarité",
        "document": "Document",
        "context_passage": (
            "Extrait utilisé comme contexte"
        ),
    },
    "de": {
        "sources_used": (
            "#### 📚 Von INNA verwendete Quellen"
        ),
        "no_context_used": (
            "In der Antwort wurde kein Kontext verwendet."
        ),
        "sources_caption": (
            "Die folgenden Abschnitte aus der "
            "RAG-Wissensbasis halfen INNA "
            "bei der Antwort."
        ),
        "source": "Quelle",
        "similarity": "Ähnlichkeit",
        "document": "Dokument",
        "context_passage": (
            "Als Kontext verwendeter Abschnitt"
        ),
    },
    "it": {
        "sources_used": (
            "#### 📚 Fonti utilizzate da INNA"
        ),
        "no_context_used": (
            "Nessun contesto è stato utilizzato "
            "nella risposta."
        ),
        "sources_caption": (
            "I seguenti estratti della base RAG "
            "hanno aiutato INNA a creare la risposta."
        ),
        "source": "Fonte",
        "similarity": "Somiglianza",
        "document": "Documento",
        "context_passage": (
            "Estratto utilizzato come contesto"
        ),
    },
}

# UPLOAD_RAG_NATIVE_SOURCE_TEXTS

UPLOAD_RAG_NATIVE_SOURCE_TEXTS = {
    "ro": {
        "sources_used": (
            "#### 📚 Surse utilizate de INNA"
        ),
        "no_context_used": (
            "Nu a fost utilizat niciun context "
            "în răspuns."
        ),
        "sources_caption": (
            "Fragmentele de mai jos au fost preluate "
            "din baza de cunoștințe RAG și au ajutat "
            "INNA să construiască răspunsul."
        ),
        "source": "Sursă",
        "similarity": "Similaritate",
        "document": "Document",
        "context_passage": (
            "Fragment utilizat drept context"
        ),
    },
    "ua": {
        "sources_used": (
            "#### 📚 Джерела, використані INNA"
        ),
        "no_context_used": (
            "У відповіді не було використано контекст."
        ),
        "sources_caption": (
            "Наведені нижче фрагменти було отримано "
            "з бази знань RAG. Вони допомогли INNA "
            "сформувати відповідь."
        ),
        "source": "Джерело",
        "similarity": "Схожість",
        "document": "Документ",
        "context_passage": (
            "Фрагмент, використаний як контекст"
        ),
    },
    "ru": {
        "sources_used": (
            "#### 📚 Источники, использованные INNA"
        ),
        "no_context_used": (
            "При формировании ответа контекст "
            "не использовался."
        ),
        "sources_caption": (
            "Приведённые ниже фрагменты были получены "
            "из базы знаний RAG и помогли INNA "
            "сформировать ответ."
        ),
        "source": "Источник",
        "similarity": "Сходство",
        "document": "Документ",
        "context_passage": (
            "Фрагмент, использованный как контекст"
        ),
    },
    "sa": {
        "sources_used": (
            "#### 📚 المصادر التي استخدمتها INNA"
        ),
        "no_context_used": (
            "لم يتم استخدام أي سياق في الإجابة."
        ),
        "sources_caption": (
            "تم استرجاع المقاطع أدناه من قاعدة معرفة RAG، "
            "وساعدت INNA في إنشاء الإجابة."
        ),
        "source": "المصدر",
        "similarity": "التشابه",
        "document": "المستند",
        "context_passage": (
            "المقطع المستخدم كسياق"
        ),
    },
}

for idioma, textos in (
    UPLOAD_RAG_NATIVE_SOURCE_TEXTS.items()
):
    UPLOAD_RAG_SOURCE_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        textos
    )

    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        textos
    )

UPLOAD_RAG_SOURCE_TEXTS["en_gb"] = (
    UPLOAD_RAG_SOURCE_TEXTS["en_us"].copy()
)

for idioma in (
    "ro",
    "ua",
    "ru",
    "sa",
):
    UPLOAD_RAG_SOURCE_TEXTS[idioma] = (
        UPLOAD_RAG_SOURCE_TEXTS["en_us"].copy()
    )

UPLOAD_RAG_SOURCE_TEXTS["ch"] = (
    UPLOAD_RAG_SOURCE_TEXTS["de"].copy()
)

for idioma, textos in (
    UPLOAD_RAG_SOURCE_TEXTS.items()
):
    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(textos)

# UPLOAD_RAG_NATIVE_SOURCE_TEXTS_FINAL_OVERRIDE

for idioma, textos in (
    UPLOAD_RAG_NATIVE_SOURCE_TEXTS.items()
):
    UPLOAD_RAG_SOURCE_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        textos
    )

    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(
        textos
    )


UPLOAD_RAG_RESOURCE_TEXTS = {
    "pt": {
        "resources_used": "🔎 Recursos utilizados pela INNA",
        "executed_steps": "#### Etapas executadas",
        "persistent_memory": "Memória persistente",
        "memory_consulted": "contexto do usuário consultado",
        "semantic_search_used": "Busca semântica RAG",
        "passages_retrieved": "{total} trecho(s) recuperado(s)",
        "choice_reason": "Motivo da escolha",
        "no_calculation_required": (
            "Nenhum cálculo financeiro determinístico "
            "foi necessário."
        ),
        "calculation_details": (
            "🧮 Detalhes do cálculo financeiro"
        ),
        "tool": "Ferramenta",
        "routing_confidence": "Confiança do roteamento",
        "calculation_executed": (
            "Cálculo determinístico executado antes "
            "da geração da resposta."
        ),
        "tool_not_executed": (
            "A ferramenta foi identificada, mas não "
            "precisou ser executada."
        ),
        "required_data": "Dados ainda necessários",
        "main_result": "#### Resultado principal",
        "monthly_income": "Renda mensal",
        "monthly_expenses": "Gastos mensais",
        "estimated_balance": "Saldo estimado",
        "committed_income": "Renda comprometida",
        "monthly_capacity": "Capacidade mensal",
        "weekly_reference": "Referência semanal",
        "show_json": "Mostrar resultado técnico em JSON",
        "memory_updated": (
            "🧠 Memória atualizada automaticamente "
            "pela conversa."
        ),
        "memory_not_updated": (
            "Memória não atualizada nesta interação."
        ),
    },
    "en_us": {
        "resources_used": "🔎 Resources used by INNA",
        "executed_steps": "#### Executed steps",
        "persistent_memory": "Persistent memory",
        "memory_consulted": "user context retrieved",
        "semantic_search_used": "RAG semantic search",
        "passages_retrieved": "{total} passage(s) retrieved",
        "choice_reason": "Reason for selection",
        "no_calculation_required": (
            "No deterministic financial calculation "
            "was required."
        ),
        "calculation_details": (
            "🧮 Financial calculation details"
        ),
        "tool": "Tool",
        "routing_confidence": "Routing confidence",
        "calculation_executed": (
            "Deterministic calculation executed before "
            "the response was generated."
        ),
        "tool_not_executed": (
            "The tool was identified but did not need "
            "to be executed."
        ),
        "required_data": "Additional data required",
        "main_result": "#### Main result",
        "monthly_income": "Monthly income",
        "monthly_expenses": "Monthly expenses",
        "estimated_balance": "Estimated balance",
        "committed_income": "Committed income",
        "monthly_capacity": "Monthly capacity",
        "weekly_reference": "Weekly reference",
        "show_json": "Show technical result as JSON",
        "memory_updated": (
            "🧠 Memory automatically updated from "
            "the conversation."
        ),
        "memory_not_updated": (
            "Memory was not updated in this interaction."
        ),
    },
    "es": {
        "resources_used": "🔎 Recursos utilizados por INNA",
        "executed_steps": "#### Etapas ejecutadas",
        "persistent_memory": "Memoria persistente",
        "memory_consulted": "contexto del usuario consultado",
        "semantic_search_used": "Búsqueda semántica RAG",
        "passages_retrieved": "{total} fragmento(s) recuperado(s)",
        "choice_reason": "Motivo de la elección",
        "no_calculation_required": (
            "No fue necesario realizar ningún cálculo "
            "financiero determinístico."
        ),
        "calculation_details": (
            "🧮 Detalles del cálculo financiero"
        ),
        "tool": "Herramienta",
        "routing_confidence": "Confianza del enrutamiento",
        "calculation_executed": (
            "Cálculo determinístico ejecutado antes "
            "de generar la respuesta."
        ),
        "tool_not_executed": (
            "La herramienta fue identificada, pero no "
            "fue necesario ejecutarla."
        ),
        "required_data": "Datos adicionales necesarios",
        "main_result": "#### Resultado principal",
        "monthly_income": "Ingresos mensuales",
        "monthly_expenses": "Gastos mensuales",
        "estimated_balance": "Saldo estimado",
        "committed_income": "Ingresos comprometidos",
        "monthly_capacity": "Capacidad mensual",
        "weekly_reference": "Referencia semanal",
        "show_json": "Mostrar resultado técnico en JSON",
        "memory_updated": (
            "🧠 Memoria actualizada automáticamente "
            "por la conversación."
        ),
        "memory_not_updated": (
            "La memoria no fue actualizada en esta interacción."
        ),
    },
    "fr": {
        "resources_used": "🔎 Ressources utilisées par INNA",
        "executed_steps": "#### Étapes exécutées",
        "persistent_memory": "Mémoire persistante",
        "memory_consulted": "contexte utilisateur consulté",
        "semantic_search_used": "Recherche sémantique RAG",
        "passages_retrieved": "{total} extrait(s) récupéré(s)",
        "choice_reason": "Motif du choix",
        "no_calculation_required": (
            "Aucun calcul financier déterministe "
            "n’a été nécessaire."
        ),
        "calculation_details": (
            "🧮 Détails du calcul financier"
        ),
        "tool": "Outil",
        "routing_confidence": "Confiance du routage",
        "calculation_executed": (
            "Calcul déterministe exécuté avant "
            "la génération de la réponse."
        ),
        "tool_not_executed": (
            "L’outil a été identifié, mais son exécution "
            "n’était pas nécessaire."
        ),
        "required_data": "Données supplémentaires nécessaires",
        "main_result": "#### Résultat principal",
        "monthly_income": "Revenu mensuel",
        "monthly_expenses": "Dépenses mensuelles",
        "estimated_balance": "Solde estimé",
        "committed_income": "Revenu engagé",
        "monthly_capacity": "Capacité mensuelle",
        "weekly_reference": "Référence hebdomadaire",
        "show_json": "Afficher le résultat technique en JSON",
        "memory_updated": (
            "🧠 Mémoire automatiquement mise à jour "
            "par la conversation."
        ),
        "memory_not_updated": (
            "La mémoire n’a pas été mise à jour."
        ),
    },
    "de": {
        "resources_used": "🔎 Von INNA verwendete Ressourcen",
        "executed_steps": "#### Ausgeführte Schritte",
        "persistent_memory": "Persistenter Speicher",
        "memory_consulted": "Benutzerkontext abgerufen",
        "semantic_search_used": "Semantische RAG-Suche",
        "passages_retrieved": "{total} Abschnitt(e) abgerufen",
        "choice_reason": "Grund für die Auswahl",
        "no_calculation_required": (
            "Es war keine deterministische "
            "Finanzberechnung erforderlich."
        ),
        "calculation_details": (
            "🧮 Details der Finanzberechnung"
        ),
        "tool": "Werkzeug",
        "routing_confidence": "Routing-Konfidenz",
        "calculation_executed": (
            "Deterministische Berechnung vor der "
            "Antwortgenerierung ausgeführt."
        ),
        "tool_not_executed": (
            "Das Werkzeug wurde erkannt, musste jedoch "
            "nicht ausgeführt werden."
        ),
        "required_data": "Zusätzlich erforderliche Daten",
        "main_result": "#### Hauptergebnis",
        "monthly_income": "Monatliches Einkommen",
        "monthly_expenses": "Monatliche Ausgaben",
        "estimated_balance": "Geschätzter Saldo",
        "committed_income": "Gebundenes Einkommen",
        "monthly_capacity": "Monatliche Kapazität",
        "weekly_reference": "Wöchentlicher Richtwert",
        "show_json": "Technisches Ergebnis als JSON anzeigen",
        "memory_updated": (
            "🧠 Speicher automatisch aus dem "
            "Gespräch aktualisiert."
        ),
        "memory_not_updated": (
            "Der Speicher wurde nicht aktualisiert."
        ),
    },
}

UPLOAD_RAG_RESOURCE_TEXTS["en_gb"] = (
    UPLOAD_RAG_RESOURCE_TEXTS["en_us"]
)

for idioma in (
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
):
    UPLOAD_RAG_RESOURCE_TEXTS[idioma] = (
        UPLOAD_RAG_RESOURCE_TEXTS["en_us"]
    )

UPLOAD_RAG_RESOURCE_TEXTS["ch"] = (
    UPLOAD_RAG_RESOURCE_TEXTS["de"]
)

for idioma, textos in (
    UPLOAD_RAG_RESOURCE_TEXTS.items()
):
    UPLOAD_RAG_TEXTS.setdefault(
        idioma,
        {},
    ).update(textos)



# BLOCK_4B_NATIVE_UPLOAD_TRANSLATIONS
# Traduções nativas finais da página de Upload/RAG.
# Este bloco é aplicado após todos os pacotes parciais,
# substituindo os fallbacks indevidos para inglês.

UPLOAD_RAG_NATIVE_TEXTS = {
    "ro": {
        "title": (
            "## 📄 Încărcarea documentelor în baza RAG"
        ),
        "caption": (
            "Încărcați fișiere .md sau .txt pentru "
            "a extinde baza de cunoștințe INNA."
        ),
        "select_document": "Selectați un document",
        "upload_help": (
            "În această versiune, INNA acceptă "
            "fișiere Markdown și TXT."
        ),
        "invalid_format": (
            "Format nepermis. Încărcați numai "
            "fișiere .md sau .txt."
        ),
        "version_lookup_error": (
            "Versionarea documentului nu a putut "
            "fi consultată."
        ),
        "version_error": (
            "Versiunea documentului nu a putut "
            "fi determinată."
        ),
        "security_rejection": (
            "Document respins de politica de securitate."
        ),
        "security_validation_error": (
            "Securitatea documentului nu a putut "
            "fi validată."
        ),
        "saved_successfully": (
            "Document salvat cu succes."
        ),
        "validation_complete": "Validare finalizată",
        "document": "Document",
        "version": "Versiune",
        "content_preview": (
            "### Previzualizarea conținutului"
        ),
        "loaded_content": "Conținut încărcat",
        "generated_chunks": "### Fragmente generate",
        "chunks_generated": (
            "fragmente generate și salvate în"
        ),
        "embedding_ready": (
            "Fișier pregătit pentru embeddings/pgvector"
        ),
        "resources_used": (
            "🔎 Resurse utilizate de INNA"
        ),
        "executed_steps": "#### Etape executate",
        "persistent_memory": "Memorie persistentă",
        "memory_consulted": (
            "contextul utilizatorului a fost consultat"
        ),
        "semantic_search_used": (
            "Căutare semantică RAG"
        ),
        "passages_retrieved": (
            "{total} fragment(e) recuperat(e)"
        ),
        "tool": "Instrument",
        "choice_reason": "Motivul alegerii",
        "no_calculation_required": (
            "Nu a fost necesar niciun calcul financiar "
            "determinist."
        ),
        "routing_confidence": (
            "Încrederea rutării"
        ),
        "calculation_executed": (
            "Calcul executat"
        ),
        "calculation_details": (
            "Detaliile calculului"
        ),
        "tool_not_executed": (
            "Instrumentul a fost identificat, dar nu "
            "a trebuit executat."
        ),
        "required_data": (
            "Date suplimentare necesare"
        ),
        "main_result": "#### Rezultatul principal",
        "monthly_income": "Venit lunar",
        "monthly_expenses": "Cheltuieli lunare",
        "estimated_balance": "Sold estimat",
        "committed_income": "Venit angajat",
        "monthly_capacity": "Capacitate lunară",
        "weekly_reference": "Referință săptămânală",
        "show_json": (
            "Afișați rezultatul tehnic în JSON"
        ),
        "memory_updated": (
            "🧠 Memoria a fost actualizată automat "
            "din conversație."
        ),
        "memory_not_updated": (
            "Memoria nu a fost actualizată."
        ),
    },
    "ua": {
        "title": (
            "## 📄 Завантаження документів до бази RAG"
        ),
        "caption": (
            "Завантажуйте файли .md або .txt, щоб "
            "розширити базу знань INNA."
        ),
        "select_document": "Виберіть документ",
        "upload_help": (
            "У цій версії INNA підтримує файли "
            "Markdown і TXT."
        ),
        "invalid_format": (
            "Недозволений формат. Завантажуйте лише "
            "файли .md або .txt."
        ),
        "version_lookup_error": (
            "Не вдалося перевірити версіювання документа."
        ),
        "version_error": (
            "Не вдалося визначити версію документа."
        ),
        "security_rejection": (
            "Документ відхилено політикою безпеки."
        ),
        "security_validation_error": (
            "Не вдалося перевірити безпеку документа."
        ),
        "saved_successfully": (
            "Документ успішно збережено."
        ),
        "validation_complete": (
            "Перевірку завершено"
        ),
        "document": "Документ",
        "version": "Версія",
        "content_preview": (
            "### Попередній перегляд вмісту"
        ),
        "loaded_content": "Завантажений вміст",
        "generated_chunks": "### Створені фрагменти",
        "chunks_generated": (
            "фрагменти створено та збережено в"
        ),
        "embedding_ready": (
            "Файл готовий для embeddings/pgvector"
        ),
        "resources_used": (
            "🔎 Ресурси, використані INNA"
        ),
        "executed_steps": "#### Виконані етапи",
        "persistent_memory": "Постійна пам’ять",
        "memory_consulted": (
            "контекст користувача було отримано"
        ),
        "semantic_search_used": (
            "Семантичний пошук RAG"
        ),
        "passages_retrieved": (
            "отримано фрагментів: {total}"
        ),
        "tool": "Інструмент",
        "choice_reason": "Причина вибору",
        "no_calculation_required": (
            "Детермінований фінансовий розрахунок "
            "не був потрібний."
        ),
        "routing_confidence": (
            "Впевненість маршрутизації"
        ),
        "calculation_executed": (
            "Розрахунок виконано"
        ),
        "calculation_details": (
            "Деталі розрахунку"
        ),
        "tool_not_executed": (
            "Інструмент було визначено, але його "
            "виконання не знадобилося."
        ),
        "required_data": (
            "Додаткові необхідні дані"
        ),
        "main_result": "#### Основний результат",
        "monthly_income": "Місячний дохід",
        "monthly_expenses": "Місячні витрати",
        "estimated_balance": "Орієнтовний баланс",
        "committed_income": "Зобов’язаний дохід",
        "monthly_capacity": "Місячна спроможність",
        "weekly_reference": "Тижневий орієнтир",
        "show_json": (
            "Показати технічний результат у JSON"
        ),
        "memory_updated": (
            "🧠 Пам’ять автоматично оновлено "
            "на основі розмови."
        ),
        "memory_not_updated": (
            "Пам’ять не оновлено."
        ),
    },
    "ru": {
        "title": (
            "## 📄 Загрузка документов в базу RAG"
        ),
        "caption": (
            "Загружайте файлы .md или .txt для "
            "расширения базы знаний INNA."
        ),
        "select_document": "Выберите документ",
        "upload_help": (
            "В этой версии INNA поддерживает файлы "
            "Markdown и TXT."
        ),
        "invalid_format": (
            "Недопустимый формат. Загружайте только "
            "файлы .md или .txt."
        ),
        "version_lookup_error": (
            "Не удалось проверить версионирование "
            "документа."
        ),
        "version_error": (
            "Не удалось определить версию документа."
        ),
        "security_rejection": (
            "Документ отклонён политикой безопасности."
        ),
        "security_validation_error": (
            "Не удалось проверить безопасность документа."
        ),
        "saved_successfully": (
            "Документ успешно сохранён."
        ),
        "validation_complete": (
            "Проверка завершена"
        ),
        "document": "Документ",
        "version": "Версия",
        "content_preview": (
            "### Предварительный просмотр содержимого"
        ),
        "loaded_content": "Загруженное содержимое",
        "generated_chunks": (
            "### Созданные фрагменты"
        ),
        "chunks_generated": (
            "фрагменты созданы и сохранены в"
        ),
        "embedding_ready": (
            "Файл готов для embeddings/pgvector"
        ),
        "resources_used": (
            "🔎 Ресурсы, использованные INNA"
        ),
        "executed_steps": "#### Выполненные этапы",
        "persistent_memory": "Постоянная память",
        "memory_consulted": (
            "контекст пользователя был получен"
        ),
        "semantic_search_used": (
            "Семантический поиск RAG"
        ),
        "passages_retrieved": (
            "получено фрагментов: {total}"
        ),
        "tool": "Инструмент",
        "choice_reason": "Причина выбора",
        "no_calculation_required": (
            "Детерминированный финансовый расчёт "
            "не потребовался."
        ),
        "routing_confidence": (
            "Уверенность маршрутизации"
        ),
        "calculation_executed": (
            "Расчёт выполнен"
        ),
        "calculation_details": (
            "Детали расчёта"
        ),
        "tool_not_executed": (
            "Инструмент был определён, но его "
            "выполнение не потребовалось."
        ),
        "required_data": (
            "Дополнительно необходимые данные"
        ),
        "main_result": "#### Основной результат",
        "monthly_income": "Месячный доход",
        "monthly_expenses": "Месячные расходы",
        "estimated_balance": "Расчётный баланс",
        "committed_income": "Обязательный доход",
        "monthly_capacity": "Месячная возможность",
        "weekly_reference": "Недельный ориентир",
        "show_json": (
            "Показать технический результат в JSON"
        ),
        "memory_updated": (
            "🧠 Память автоматически обновлена "
            "на основе разговора."
        ),
        "memory_not_updated": (
            "Память не была обновлена."
        ),
    },
    "sa": {
        "title": (
            "## 📄 تحميل المستندات إلى قاعدة RAG"
        ),
        "caption": (
            "حمّل ملفات .md أو .txt لتوسيع "
            "قاعدة معرفة INNA."
        ),
        "select_document": "اختر مستندًا",
        "upload_help": (
            "تدعم INNA في هذا الإصدار ملفات "
            "Markdown وTXT."
        ),
        "invalid_format": (
            "صيغة غير مسموحة. حمّل ملفات "
            ".md أو .txt فقط."
        ),
        "version_lookup_error": (
            "تعذر التحقق من إصدارات المستند."
        ),
        "version_error": (
            "تعذر تحديد إصدار المستند."
        ),
        "security_rejection": (
            "تم رفض المستند بواسطة سياسة الأمان."
        ),
        "security_validation_error": (
            "تعذر التحقق من أمان المستند."
        ),
        "saved_successfully": (
            "تم حفظ المستند بنجاح."
        ),
        "validation_complete": (
            "اكتمل التحقق"
        ),
        "document": "المستند",
        "version": "الإصدار",
        "content_preview": (
            "### معاينة المحتوى"
        ),
        "loaded_content": "المحتوى المحمّل",
        "generated_chunks": (
            "### الأجزاء التي تم إنشاؤها"
        ),
        "chunks_generated": (
            "تم إنشاء الأجزاء وحفظها في"
        ),
        "embedding_ready": (
            "الملف جاهز للتضمينات وpgvector"
        ),
        "resources_used": (
            "🔎 الموارد التي استخدمتها INNA"
        ),
        "executed_steps": "#### المراحل المنفذة",
        "persistent_memory": "الذاكرة الدائمة",
        "memory_consulted": (
            "تمت قراءة سياق المستخدم"
        ),
        "semantic_search_used": (
            "البحث الدلالي RAG"
        ),
        "passages_retrieved": (
            "عدد المقاطع المسترجعة: {total}"
        ),
        "tool": "الأداة",
        "choice_reason": "سبب الاختيار",
        "no_calculation_required": (
            "لم تكن هناك حاجة إلى حساب مالي حتمي."
        ),
        "routing_confidence": (
            "درجة الثقة في التوجيه"
        ),
        "calculation_executed": (
            "تم تنفيذ الحساب"
        ),
        "calculation_details": (
            "تفاصيل الحساب"
        ),
        "tool_not_executed": (
            "تم تحديد الأداة، لكن لم تكن هناك "
            "حاجة إلى تنفيذها."
        ),
        "required_data": (
            "البيانات الإضافية المطلوبة"
        ),
        "main_result": "#### النتيجة الرئيسية",
        "monthly_income": "الدخل الشهري",
        "monthly_expenses": "المصروفات الشهرية",
        "estimated_balance": "الرصيد التقديري",
        "committed_income": "الدخل الملتزم",
        "monthly_capacity": "القدرة الشهرية",
        "weekly_reference": "المرجع الأسبوعي",
        "show_json": (
            "عرض النتيجة التقنية بصيغة JSON"
        ),
        "memory_updated": (
            "🧠 تم تحديث الذاكرة تلقائيًا "
            "من المحادثة."
        ),
        "memory_not_updated": (
            "لم يتم تحديث الذاكرة."
        ),
    },
}

for _language, _texts in (
    UPLOAD_RAG_NATIVE_TEXTS.items()
):
    # Cria um dicionário independente.
    # Alguns idiomas antigos eram aliases do inglês
    # e compartilhavam o mesmo objeto em memória.
    UPLOAD_RAG_TEXTS[
        _language
    ] = {
        **dict(
            UPLOAD_RAG_TEXTS.get(
                _language,
                {},
            )
        ),
        **dict(_texts),
    }


def upload_rag_t(
    key,
    default=None,
    **format_values,
):
    return dashboard_page_translate(
        UPLOAD_RAG_TEXTS,
        key,
        language=dashboard_lang(),
        default=default,
        **format_values,
    )

def render_upload_documentos_rag():
    import streamlit as st
    from pathlib import Path
    from datetime import datetime

    st.markdown(upload_rag_t("title"))
    st.caption(upload_rag_t("caption"))

    upload_dir = Path("data/knowledge_base/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    chunks_dir = Path("data/knowledge_base/chunks")
    chunks_dir.mkdir(parents=True, exist_ok=True)

    uploaded_file = st.file_uploader(
        upload_rag_t("select_document"),
        type=["md", "txt"],
        help=upload_rag_t("upload_help")
    )

    if uploaded_file is not None:
        original_name = uploaded_file.name
        suffix = Path(original_name).suffix.lower()

        if suffix not in [".md", ".txt"]:
            st.error(upload_rag_t("invalid_format"))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = original_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        final_path = upload_dir / f"{timestamp}_{safe_name}"

        content_bytes = uploaded_file.getvalue()

        try:
            try:
                from services.rag.security import (
                    RagDocumentSecurityError,
                    require_safe_rag_document,
                )
            except ImportError:
                from src.services.rag.security import (
                    RagDocumentSecurityError,
                    require_safe_rag_document,
                )

            security_result = require_safe_rag_document(
                filename=original_name,
                content=content_bytes,
            )

            try:
                from services.rag.versioning import (
                    RagDocumentVersioningError,
                    RagDuplicateDocumentError,
                    create_document_version_from_context,
                    normalize_logical_document_name,
                )
            except ImportError:
                from src.services.rag.versioning import (
                    RagDocumentVersioningError,
                    RagDuplicateDocumentError,
                    create_document_version_from_context,
                    normalize_logical_document_name,
                )

            nome_logico = normalize_logical_document_name(
                original_name
            )

            versioning_lookup = (
                buscar_contexto_versionamento_rag(
                    nome_logico
                )
            )

            if not versioning_lookup.get("ok"):
                st.error(
                    upload_rag_t(
                        "version_lookup_error"
                    )
                )
                return

            document_version = (
                create_document_version_from_context(
                    filename=original_name,
                    content_hash=(
                        security_result.content_hash
                    ),
                    repository_context=(
                        versioning_lookup.get(
                            "contexto"
                        )
                    ),
                )
            )

        except RagDuplicateDocumentError as exc:
            st.warning(str(exc))
            return

        except RagDocumentVersioningError as exc:
            st.error(
                f"{upload_rag_t('version_error')}: {exc}"
            )
            return

        except RagDocumentSecurityError as exc:
            st.error(
                f"{upload_rag_t('security_rejection')}: {exc}"
            )
            return

        except Exception:
            st.error(
                upload_rag_t(
                    "security_validation_error"
                )
            )
            return

        final_path.write_bytes(content_bytes)

        st.success(
            f"{upload_rag_t('saved_successfully')}: "
            f"{final_path.name}"
        )

        st.caption(
            f"{upload_rag_t('validation_complete')} | "
            f"{security_result.size_bytes} bytes | "
            f"SHA-256: "
            f"{security_result.content_hash[:16]}... | "
            f"{upload_rag_t('document')}: "
            f"{document_version.logical_name} | "
            f"{upload_rag_t('version')}: "
            f"{document_version.version}"
        )

        try:
            preview = content_bytes.decode("utf-8")
            preview_limpo = limpar_texto_documento_rag(preview)

            st.markdown(
                upload_rag_t("content_preview")
            )
            st.text_area(
                upload_rag_t("loaded_content"),
                preview_limpo[:3000],
                height=250,
            )

            chunks_path, chunks, embedding_ready_path = salvar_chunks_documento(final_path.name, preview_limpo)

            st.markdown(
                upload_rag_t("generated_chunks")
            )
            st.success(
                f"{len(chunks)} "
                f"{upload_rag_t('chunks_generated')}: "
                f"{chunks_path.name}"
            )
            st.info(
                f"{upload_rag_t('embedding_ready')}: "
                f"{embedding_ready_path.name}"
            )

            registro_db = registrar_metadata_upload_rag(
                nome_original=original_name,
                nome_salvo=final_path.name,
                caminho_upload=str(final_path),
                caminho_chunks=str(chunks_path),
                caminho_embedding_ready=str(embedding_ready_path),
                extensao=suffix,
                tamanho_bytes=len(content_bytes),
                total_chunks=len(chunks),
                nome_logico=(
                    document_version.logical_name
                ),
                content_hash=(
                    document_version.content_hash
                ),
                versao=(
                    document_version.version
                ),
                documento_raiz_id=(
                    document_version.root_document_id
                ),
                documento_anterior_id=(
                    document_version.previous_document_id
                ),
            )

            if registro_db.get("ok"):
                st.success(registro_db.get("message"))
            else:
                st.warning(registro_db.get("message"))

            for idx, chunk in enumerate(chunks[:5], start=1):
                categoria_chunk = classificar_categoria_chunk_rag(chunk)

                with st.expander(
                    upload_rag_t(
                        "chunk_preview"
                    ).format(
                        index=idx,
                        characters=len(chunk),
                        category=categoria_chunk,
                    )
                ):
                    st.text_area(
                        upload_rag_t(
                            "chunk_text"
                        ),
                        chunk,
                        height=180,
                        key=f"preview_chunk_upload_rag_{idx}_{final_path.name}"
                    )

            if len(chunks) > 5:
                st.info(
                    upload_rag_t(
                        "chunk_preview_limit"
                    ).format(
                        total=len(chunks)
                    )
                )

        except Exception as e:
            st.warning(
                upload_rag_t(
                    "preview_generation_failed"
                )
            )
            st.caption(str(e))

    st.markdown("---")
    st.markdown(
        upload_rag_t(
            "uploaded_documents"
        )
    )

    files = sorted(upload_dir.glob("*"), reverse=True)

    if not files:
        st.info(
            upload_rag_t(
                "no_uploaded_documents"
            )
        )
    else:
        for file in files:
            if file.is_file():
                st.write(f"📄 **{file.name}**")
                st.caption(
            f"{upload_rag_t('file_size')}: "
            f"{file.stat().st_size} bytes"
        )

    st.markdown("---")
    st.markdown(
        upload_rag_t(
            "generated_chunk_files"
        )
    )

    chunk_files = sorted(chunks_dir.glob("*.json"), reverse=True)

    if not chunk_files:
        st.info(
            upload_rag_t(
                "no_generated_chunk_files"
            )
        )
    else:
        for file in chunk_files[:10]:
            st.write(f"🧩 **{file.name}**")
            st.caption(
                f"{upload_rag_t('file_size')}: "
                f"{file.stat().st_size} bytes"
            )

    st.markdown("---")
    st.markdown(
        upload_rag_t(
            "embedding_ready_files"
        )
    )

    embedding_ready_dir = Path("data/knowledge_base/embedding_ready")
    embedding_ready_dir.mkdir(parents=True, exist_ok=True)

    embedding_files = sorted(embedding_ready_dir.glob("*.jsonl"), reverse=True)

    if not embedding_files:
        st.info(
            upload_rag_t(
                "no_embedding_ready_files"
            )
        )
    else:
        for file in embedding_files[:10]:
            st.write(f"🧠 **{file.name}**")
            st.caption(f"Tamanho: {file.stat().st_size} bytes")


    st.markdown("---")
    st.markdown(
        upload_rag_t("registered_documents")
    )

    df_docs, erro_docs = carregar_documentos_upload_rag()

    if erro_docs:
        st.warning(
            f"{upload_rag_t('database_documents_error')}: "
            f"{erro_docs}"
        )
    elif df_docs.empty:
        st.info(
            upload_rag_t(
                "no_registered_documents"
            )
        )
    else:
        st.metric(
            upload_rag_t(
                "registered_documents_total"
            ),
            len(df_docs),
        )

        col1, col2, col3 = st.columns(3)
        col1.metric(
            upload_rag_t("total_chunks"),
            int(
                df_docs["total_chunks"]
                .fillna(0)
                .sum()
            ),
        )
        col2.metric(
            upload_rag_t("processed"),
            int(
                (
                    df_docs["status"]
                    == "processado"
                ).sum()
            ),
        )
        col3.metric(
            upload_rag_t("extensions"),
            df_docs["extensao"].nunique(),
        )

        st.dataframe(
            df_docs[
                [
                    "id",
                    "nome_salvo",
                    "extensao",
                    "total_chunks",
                    "status",
                    "ativo",
                    "criado_em",
                    "caminho_embedding_ready",
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


        st.markdown(
            upload_rag_t("local_organisation")
        )

        uploads_dir_local = Path("data/knowledge_base/uploads")
        chunks_dir_local = Path("data/knowledge_base/chunks")
        embedding_ready_dir_local = Path("data/knowledge_base/embedding_ready")

        uploads_local = [f for f in uploads_dir_local.glob("*") if f.is_file() and f.name != ".gitkeep"] if uploads_dir_local.exists() else []
        chunks_local = [f for f in chunks_dir_local.glob("*") if f.is_file() and f.name != ".gitkeep"] if chunks_dir_local.exists() else []
        embeddings_local = [f for f in embedding_ready_dir_local.glob("*") if f.is_file() and f.name != ".gitkeep"] if embedding_ready_dir_local.exists() else []

        col_local_1, col_local_2, col_local_3 = st.columns(3)

        col_local_1.metric(
            upload_rag_t("local_uploads"),
            len(uploads_local),
        )
        col_local_2.metric(
            upload_rag_t("chunk_files"),
            len(chunks_local),
        )
        col_local_3.metric(
            upload_rag_t(
                "embedding_ready_jsonl"
            ),
            len(embeddings_local),
        )

        with st.expander(
            upload_rag_t("recent_local_files")
        ):
            st.caption(
                upload_rag_t(
                    "recent_files_caption"
                )
            )

            st.markdown(
                upload_rag_t("recent_uploads")
            )
            for file in sorted(uploads_local, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                st.write(f"📄 {file.name}")
                st.caption(
                    f"{upload_rag_t('file_size')}: "
                    f"{file.stat().st_size} bytes"
                )

            st.markdown(
                upload_rag_t("recent_chunks")
            )
            for file in sorted(chunks_local, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                st.write(f"🧩 {file.name}")
                st.caption(
                    f"{upload_rag_t('file_size')}: "
                    f"{file.stat().st_size} bytes"
                )

            st.markdown(
                upload_rag_t("recent_jsonl")
            )
            for file in sorted(embeddings_local, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                st.write(f"🧠 {file.name}")
                st.caption(
                    f"{upload_rag_t('file_size')}: "
                    f"{file.stat().st_size} bytes"
                )

        st.caption(
            upload_rag_t("archive_caption")
        )

        manter_ultimos_arquivos = st.slider(
            upload_rag_t("files_to_keep"),
            min_value=1,
            max_value=10,
            value=5,
            key="manter_ultimos_arquivos_rag"
        )

        if st.button(
            upload_rag_t("archive_old_files"),
            key="btn_arquivar_arquivos_locais_rag",
        ):
            resultado_arquivo = arquivar_arquivos_locais_rag(
                manter_ultimos=manter_ultimos_arquivos
            )

            if resultado_arquivo.get("ok"):
                st.success(resultado_arquivo.get("message"))
                st.rerun()
            else:
                st.warning(resultado_arquivo.get("message"))

        st.markdown(
            upload_rag_t("document_status")
        )

        resultado_coluna_ativo = garantir_coluna_ativo_documentos_rag()

        if not resultado_coluna_ativo.get("ok"):
            st.warning(resultado_coluna_ativo.get("message"))

        opcoes_status_docs = [
            f"{int(row['id'])} - {row['nome_salvo']}"
            for _, row in df_docs.iterrows()
        ]

        doc_status_escolhido = st.selectbox(
            upload_rag_t(
                "select_status_document"
            ),
            opcoes_status_docs,
            key="select_status_documento_rag"
        )

        documento_status_id = int(doc_status_escolhido.split(" - ")[0])
        registro_status = df_docs[df_docs["id"] == documento_status_id].iloc[0]

        ativo_atual = bool(registro_status.get("ativo", True))

        if ativo_atual:
            st.success(
                upload_rag_t("active_document")
            )
        else:
            st.warning(
                upload_rag_t("inactive_document")
            )

        col_status_1, col_status_2 = st.columns(2)

        with col_status_1:
            if st.button(
                upload_rag_t("activate_document"),
                key="btn_ativar_documento_rag",
            ):
                resultado_status = atualizar_status_documento_rag(documento_status_id, True)

                if resultado_status.get("ok"):
                    st.success(resultado_status.get("message"))
                    st.rerun()
                else:
                    st.warning(resultado_status.get("message"))

        with col_status_2:
            if st.button(
                upload_rag_t(
                    "deactivate_document"
                ),
                key="btn_desativar_documento_rag",
            ):
                resultado_status = atualizar_status_documento_rag(documento_status_id, False)

                if resultado_status.get("ok"):
                    st.success(resultado_status.get("message"))
                    st.rerun()
                else:
                    st.warning(resultado_status.get("message"))

        st.markdown(
            upload_rag_t("reprocess_document")
        )

        opcoes_docs = [
            f"{int(row['id'])} - {row['nome_salvo']}"
            for _, row in df_docs.iterrows()
        ]

        doc_escolhido = st.selectbox(
            upload_rag_t(
                "select_reprocess_document"
            ),
            opcoes_docs,
            key="select_reprocessar_documento_rag"
        )

        if st.button(
            upload_rag_t("reprocess_selected"),
            key="btn_reprocessar_documento_rag",
        ):
            from pathlib import Path

            documento_id = int(doc_escolhido.split(" - ")[0])
            registro = df_docs[df_docs["id"] == documento_id].iloc[0]

            caminho_upload = Path(str(registro["caminho_upload"]))

            if not caminho_upload.exists():
                st.error(
                    f"{upload_rag_t('original_file_not_found')}: "
                    f"{caminho_upload}"
                )
            else:
                texto_documento = caminho_upload.read_text(encoding="utf-8", errors="ignore")

                chunks_path, chunks, embedding_ready_path = salvar_chunks_documento(
                    caminho_upload.name,
                    texto_documento
                )

                resultado_update = atualizar_metadata_reprocessamento_rag(
                    documento_id=documento_id,
                    caminho_chunks=str(chunks_path),
                    caminho_embedding_ready=str(embedding_ready_path),
                    total_chunks=len(chunks),
                )

                if resultado_update.get("ok"):
                    st.success(resultado_update.get("message"))
                    st.info(
                        f"{upload_rag_t('new_embedding_ready')}: "
                        f"{embedding_ready_path.name}"
                    )
                else:
                    st.warning(resultado_update.get("message"))


        st.markdown(
            upload_rag_t("embedding_summary")
        )

        resumo_embeddings = carregar_resumo_embeddings_pgvector_rag()

        if not resumo_embeddings.get("ok"):
            st.warning(resumo_embeddings.get("message"))
        else:
            col_emb_1, col_emb_2, col_emb_3 = st.columns(3)

            col_emb_1.metric(
                upload_rag_t("total_embeddings"),
                resumo_embeddings.get("total_embeddings", 0)
            )

            col_emb_2.metric(
                upload_rag_t("active_embeddings"),
                resumo_embeddings.get("embeddings_ativos", 0)
            )

            col_emb_3.metric(
                upload_rag_t("inactive_embeddings"),
                resumo_embeddings.get("embeddings_inativos", 0)
            )

            col_doc_1, col_doc_2, col_doc_3 = st.columns(3)

            col_doc_1.metric(
                upload_rag_t(
                    "documents_with_embeddings"
                ),
                resumo_embeddings.get("documentos_com_embeddings", 0)
            )

            col_doc_2.metric(
                upload_rag_t("active_documents"),
                resumo_embeddings.get("documentos_ativos_com_embeddings", 0)
            )

            col_doc_3.metric(
                upload_rag_t("inactive_documents"),
                resumo_embeddings.get("documentos_inativos_com_embeddings", 0)
            )

            df_resumo_embeddings = resumo_embeddings.get("df")

            if df_resumo_embeddings is not None and not df_resumo_embeddings.empty:
                with st.expander(
                    upload_rag_t("summary_by_document")
                ):
                    st.dataframe(
                        df_resumo_embeddings,
                        use_container_width=True,
                        hide_index=True
                    )

        st.markdown(
            upload_rag_t("generate_embeddings")
        )

        st.caption(
            upload_rag_t(
                "generate_embeddings_caption"
            )
        )

        forcar_reprocessamento_embeddings = st.checkbox(
            upload_rag_t(
                "force_embedding_reprocessing"
            ),
            value=False,
            key="forcar_reprocessamento_embeddings_pgvector_rag"
        )

        if st.button(
            upload_rag_t(
                "generate_selected_embeddings"
            ),
            key="btn_gerar_embeddings_pgvector_rag",
        ):
            documento_id = int(doc_escolhido.split(" - ")[0])
            registro = df_docs[df_docs["id"] == documento_id].iloc[0]

            caminho_embedding_ready = registro.get("caminho_embedding_ready")

            if not caminho_embedding_ready:
                st.error(
                    upload_rag_t(
                        "missing_embedding_path"
                    )
                )
            else:
                ja_tem_embeddings, total_existente = documento_tem_embeddings_pgvector_rag(documento_id)

                if ja_tem_embeddings and not forcar_reprocessamento_embeddings:
                    st.info(
                        upload_rag_t(
                            "existing_embeddings"
                        ).format(
                            total=total_existente
                        )
                    )
                else:
                    with st.spinner(
                        upload_rag_t(
                            "generating_embeddings"
                        )
                    ):
                        resultado_embeddings = salvar_chunks_embeddings_pgvector_rag(
                            documento_id=documento_id,
                            caminho_embedding_ready=caminho_embedding_ready
                        )

                    if resultado_embeddings.get("ok"):
                        st.success(resultado_embeddings.get("message"))
                    else:
                        st.warning(resultado_embeddings.get("message"))


        st.markdown(
            upload_rag_t(
                "pgvector_optimisation"
            )
        )

        st.caption(
            upload_rag_t(
                "pgvector_optimisation_caption"
            )
        )

        if st.button(
            upload_rag_t("create_index"),
            key="btn_criar_indice_pgvector_rag",
        ):
            with st.spinner(
                upload_rag_t("creating_index")
            ):
                resultado_indice = criar_indice_pgvector_rag()

            if resultado_indice.get("ok"):
                st.success(resultado_indice.get("message"))
            else:
                st.warning(resultado_indice.get("message"))

        st.markdown(
            upload_rag_t("semantic_search")
        )

        pergunta_teste_pgvector = st.text_input(
            upload_rag_t("search_question"),
            value="Recebi um Pix estranho, devo devolver?",
            key="pergunta_teste_pgvector_rag"
        )

        modo_limite_chunks = st.radio(
            upload_rag_t(
                "chunk_quantity_mode"
            ),
            [
                "automatic",
                "manual",
            ],
            format_func=lambda value: (
                upload_rag_t(
                    "automatic_mode"
                    if value == "automatic"
                    else "manual_mode"
                )
            ),
            horizontal=True,
            key="modo_limite_chunks_pgvector_rag"
        )

        if modo_limite_chunks == "automatic":
            limite_resultados_pgvector = definir_limite_chunks_automatico_rag(pergunta_teste_pgvector)
            st.info(
                upload_rag_t(
                    "automatic_quantity"
                ).format(
                    total=limite_resultados_pgvector
                )
            )
        else:
            limite_resultados_pgvector = st.slider(
                upload_rag_t("returned_chunks"),
                min_value=1,
                max_value=10,
                value=5,
                key="limite_resultados_pgvector_rag"
            )

        if st.button(
            upload_rag_t(
                "search_similar_chunks"
            ),
            key="btn_buscar_chunks_pgvector_rag",
        ):
            with st.spinner(
                upload_rag_t("searching_chunks")
            ):
                resultado_busca = buscar_chunks_semanticos_pgvector_rag(
                    pergunta=pergunta_teste_pgvector,
                    limite=limite_resultados_pgvector
                )

            if not resultado_busca.get("ok"):
                st.warning(resultado_busca.get("message"))
            else:
                st.success(resultado_busca.get("message"))

                resultados = resultado_busca.get("resultados", [])

                if not resultados:
                    st.info(
                        upload_rag_t(
                            "no_chunk_found"
                        )
                    )
                else:
                    for item in resultados:
                        with st.expander(
                            f"{upload_rag_t('chunk')} "
                            f"{item['chunk_index']} | "
                            f"{upload_rag_t('category')}: "
                            f"{item.get('categoria', upload_rag_t('general'))} | "
                            f"{upload_rag_t('approx_similarity')}: "
                            f"{item['similaridade_aproximada']} | "
                            f"{item['documento_origem']}"
                        ):
                            st.caption(
                                f"chunk_id: {item['chunk_id']}"
                            )
                            st.caption(
                                f"{upload_rag_t('pgvector_distance')}: "
                                f"{item['distancia']}"
                            )
                            st.caption(
                                f"{upload_rag_t('prioritised_categories')}: "
                                f"{item.get('categorias_prioritarias', [])}"
                            )
                            st.caption(
                                f"{upload_rag_t('rag_score')}: "
                                f"{item.get('score_rag')}"
                            )
                            st.write(item["texto"])


        st.markdown(
            upload_rag_t("final_rag_response")
        )

        usuario_id_resposta_rag = st.text_input(
            "ID do usuário para usar memória",
            value="demo_user",
            key="usuario_id_resposta_final_rag"
        )

        pergunta_resposta_rag = st.text_area(
            upload_rag_t("rag_question"),
            value="Recebi um Pix estranho, devo devolver?",
            height=100,
            key="pergunta_resposta_final_rag_pgvector"
        )

        usar_limite_auto_resposta = st.checkbox(
            upload_rag_t(
                "automatic_response_chunks"
            ),
            value=True,
            key="usar_limite_auto_resposta_rag_pgvector"
        )

        if usar_limite_auto_resposta:
            limite_resposta_rag = definir_limite_chunks_automatico_rag(pergunta_resposta_rag)
            st.info(
                upload_rag_t(
                    "automatic_response_limit"
                ).format(
                    total=limite_resposta_rag
                )
            )
        else:
            limite_resposta_rag = st.slider(
                upload_rag_t(
                    "response_context_chunks"
                ),
                min_value=1,
                max_value=10,
                value=5,
                key="limite_resposta_final_rag_pgvector"
            )

        if st.button(
            upload_rag_t(
                "generate_final_response"
            ),
            key="btn_gerar_resposta_final_rag_pgvector",
        ):
            with st.spinner(
                upload_rag_t(
                    "generating_final_response"
                )
            ):
                resultado_resposta = gerar_resposta_rag_pgvector_inna(
                    pergunta=pergunta_resposta_rag,
                    limite=limite_resposta_rag,
                    usuario_id=usuario_id_resposta_rag
                )

            if not resultado_resposta.get("ok"):
                st.warning(resultado_resposta.get("message"))
            else:
                st.success(resultado_resposta.get("message"))

                st.markdown(
                    upload_rag_t(
                        "inna_final_response"
                    )
                )

                with st.container(border=True):
                    st.markdown(preparar_markdown_resposta_inna(resultado_resposta.get("resposta", "")))

                resultado_tools_ui = (
                    resultado_resposta.get("tools")
                    or {}
                )

                tool_utilizada = resultado_tools_ui.get(
                    "tool_identificada"
                )

                total_contextos_utilizados = len(
                    resultado_resposta.get("contextos")
                    or []
                )

                memoria_foi_consultada = bool(
                    usuario_id_resposta_rag
                )

                with st.expander(
                    "🔎 Recursos utilizados pela INNA",
                    expanded=False,
                ):
                    st.markdown(upload_rag_t("executed_steps"))

                    if memoria_foi_consultada:
                        st.markdown(
                            "✅ **"
                            f"{upload_rag_t('persistent_memory')}:** "
                            f"{upload_rag_t('memory_consulted')}"
                        )

                    if total_contextos_utilizados > 0:
                        st.markdown(
                            "✅ **"
                            f"{upload_rag_t('semantic_search_used')}:** "
                            + upload_rag_t(
                                "passages_retrieved"
                            ).format(
                                total=total_contextos_utilizados
                            )
                        )

                    if tool_utilizada:
                        try:
                            from tools.registry import TOOL_LABELS
                        except ImportError:
                            from src.tools.registry import TOOL_LABELS

                        tool_label = TOOL_LABELS.get(
                            tool_utilizada,
                            tool_utilizada,
                        )

                        st.markdown(
                            "✅ **Tool financeira:** "
                            f"{tool_label}"
                        )

                        motivo_tool = resultado_tools_ui.get(
                            "motivo_tool"
                        )

                        if motivo_tool:
                            st.caption(
                                f"{upload_rag_t('choice_reason')}: "
                                f"{motivo_tool}"
                            )

                    if not tool_utilizada:
                        st.caption(
                            upload_rag_t(
                                "no_calculation_required"
                            )
                        )

                if tool_utilizada:
                    with st.expander(
                        upload_rag_t("calculation_details"),
                        expanded=False,
                    ):
                        col_tool_1, col_tool_2 = st.columns(2)

                        col_tool_1.markdown(
                            f"**{upload_rag_t('tool')}:** "
                            f"{tool_label}"
                        )

                        col_tool_2.markdown(
                            f"**{upload_rag_t('routing_confidence')}:** "
                            f"{resultado_tools_ui.get('confianca', 0):.0%}"
                        )

                        if resultado_tools_ui.get("executada"):
                            st.success(
                                upload_rag_t(
                                    "calculation_executed"
                                )
                            )
                        else:
                            st.info(
                                upload_rag_t(
                                    "tool_not_executed"
                                )
                            )

                        dados_ausentes_tools = (
                            resultado_tools_ui.get(
                                "dados_ausentes",
                                [],
                            )
                        )

                        if dados_ausentes_tools:
                            st.warning(
                                f"{upload_rag_t('required_data')}: "
                                + ", ".join(
                                    dados_ausentes_tools
                                )
                            )

                        resultado_calculo = (
                            resultado_tools_ui.get(
                                "resultado"
                            )
                        )

                        if resultado_calculo is not None:
                            st.markdown(
                                "#### Resultado principal"
                            )

                            try:
                                from services.formatter_inna import (
                                    formatar_moeda
                                )
                            except ImportError:
                                from src.services.formatter_inna import (
                                    formatar_moeda
                                )

                            moeda_tool = "BRL"

                            try:
                                memoria_resultado_tool = (
                                    buscar_memoria_inna(
                                        usuario_id_resposta_rag
                                    )
                                )

                                moeda_tool = (
                                    memoria_resultado_tool
                                    .get("memoria", {})
                                    .get("moeda")
                                    or "BRL"
                                )
                            except Exception:
                                moeda_tool = "BRL"

                            if (
                                "saldo_mensal"
                                in resultado_calculo
                            ):
                                col_a, col_b, col_c = st.columns(3)

                                col_a.metric(
                                    upload_rag_t(
                                        "monthly_income"
                                    ),
                                    formatar_moeda(
                                        resultado_calculo.get(
                                            "renda_mensal"
                                        ),
                                        moeda_tool,
                                    ),
                                )

                                col_b.metric(
                                    upload_rag_t(
                                        "monthly_expenses"
                                    ),
                                    formatar_moeda(
                                        resultado_calculo.get(
                                            "gastos_mensais"
                                        ),
                                        moeda_tool,
                                    ),
                                )

                                col_c.metric(
                                    upload_rag_t(
                                        "estimated_balance"
                                    ),
                                    formatar_moeda(
                                        resultado_calculo.get(
                                            "saldo_mensal"
                                        ),
                                        moeda_tool,
                                    ),
                                )

                                st.caption(
                                    f"{upload_rag_t('committed_income')}: "
                                    f"{resultado_calculo.get(
                                        'renda_comprometida_percentual',
                                        0,
                                    ):.2f}%"
                                )

                            elif (
                                "valor_semanal_estimado"
                                in resultado_calculo
                            ):
                                col_a, col_b = st.columns(2)

                                col_a.metric(
                                    upload_rag_t(
                                        "monthly_capacity"
                                    ),
                                    formatar_moeda(
                                        resultado_calculo.get(
                                            "valor_mensal"
                                        ),
                                        moeda_tool,
                                    ),
                                )

                                col_b.metric(
                                    upload_rag_t(
                                        "weekly_reference"
                                    ),
                                    formatar_moeda(
                                        resultado_calculo.get(
                                            "valor_semanal_estimado"
                                        ),
                                        moeda_tool,
                                    ),
                                )

                            mostrar_json_tool = st.checkbox(
                                upload_rag_t(
                                    "show_json"
                                ),
                                value=False,
                                key=(
                                    "mostrar_json_tool_"
                                    f"{tool_utilizada}"
                                ),
                            )

                            if mostrar_json_tool:
                                st.json(resultado_calculo)

                memoria_auto = resultado_resposta.get("memoria_atualizada", {})

                if memoria_auto.get("ok"):
                    st.success(upload_rag_t("memory_updated"))
                    st.caption(memoria_auto.get("message"))

                    evolucao = memoria_auto.get("evolucao", {})

                    if evolucao.get("tem_evolucao"):
                        moeda_memoria = "BRL"

                        try:
                            memoria_resultado = buscar_memoria_inna(usuario_id_resposta_rag)
                            memoria_atual = memoria_resultado.get("memoria") or {}
                            moeda_memoria = memoria_atual.get("moeda") or "BRL"
                        except Exception:
                            moeda_memoria = "BRL"

                        renderizar_evolucao_financeira_inna(
                            evolucao=evolucao,
                            moeda=moeda_memoria
                        )

                else:
                    st.caption(
                        memoria_auto.get(
                            "message",
                            upload_rag_t(
                                "memory_not_updated"
                            ),
                        )
                    )

                contextos_usados = resultado_resposta.get("contextos", [])

                st.markdown(
                    upload_rag_t("sources_used")
                )

                if not contextos_usados:
                    st.info(
                        upload_rag_t("no_context_used")
                    )
                else:
                    st.caption(
                        upload_rag_t(
                            "sources_caption"
                        )
                    )

                    for idx, item in enumerate(
                        contextos_usados,
                        start=1,
                    ):
                        similaridade = item.get(
                            "similaridade_aproximada"
                        )
                        documento = item.get(
                            "documento_origem"
                        )
                        chunk_id = item.get("chunk_id")
                        texto_contexto = item.get(
                            "texto",
                            "",
                        )

                        texto_preview = texto_contexto[:900]

                        if len(texto_contexto) > 900:
                            texto_preview += "..."

                        with st.expander(
                            f"{upload_rag_t('source')} "
                            f"{idx} | "
                            f"{upload_rag_t('similarity')}: "
                            f"{similaridade} | "
                            f"{upload_rag_t('document')}: "
                            f"{documento}"
                        ):
                            col_a, col_b, col_c = st.columns(3)

                            col_a.metric(
                                upload_rag_t("source"),
                                idx,
                            )
                            col_b.metric(
                                upload_rag_t(
                                    "similarity"
                                ),
                                similaridade,
                            )
                            col_c.metric(
                                "Chunk",
                                item.get("chunk_index"),
                            )

                            st.caption(
                                f"chunk_id: {chunk_id}"
                            )

                            st.text_area(
                                upload_rag_t(
                                    "context_passage"
                                ),
                                texto_preview,
                                height=180,
                                key=(
                                    "contexto_resposta_rag_"
                                    f"{idx}_{chunk_id}"
                                ),
                            )


def salvar_ou_atualizar_memoria_inna(usuario_id, dados_memoria, origem="dashboard"):
    import os
    import json
    from pathlib import Path

    if not usuario_id:
        return {"ok": False, "message": "usuario_id não informado."}

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=Path(".env"))
            database_url = os.getenv("DATABASE_URL")
        except Exception:
            database_url = None

    if not database_url:
        return {"ok": False, "message": "DATABASE_URL não encontrada."}

    try:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT *
            FROM memoria_usuarios_inna
            WHERE usuario_id = %s
            LIMIT 1;
        """, (usuario_id,))

        antes = cur.fetchone()

        memoria_json = dados_memoria.get("memoria_json", {})

        cur.execute("""
            INSERT INTO memoria_usuarios_inna (
                usuario_id,
                nome,
                idioma,
                moeda,
                renda_mensal,
                gastos_mensais,
                valor_reserva,
                possui_dividas,
                uso_cartao_credito,
                ultimo_score,
                ultimo_risco,
                ultima_meta,
                resumo_contexto,
                perfil_financeiro,
                objetivo_principal,
                preferencia_linguagem,
                canal_origem,
                nivel_confianca,
                memoria_json,
                tags,
                ativo,
                atualizado_em
            )
            VALUES (
                %(usuario_id)s,
                %(nome)s,
                %(idioma)s,
                %(moeda)s,
                %(renda_mensal)s,
                %(gastos_mensais)s,
                %(valor_reserva)s,
                %(possui_dividas)s,
                %(uso_cartao_credito)s,
                %(ultimo_score)s,
                %(ultimo_risco)s,
                %(ultima_meta)s,
                %(resumo_contexto)s,
                %(perfil_financeiro)s,
                %(objetivo_principal)s,
                %(preferencia_linguagem)s,
                %(canal_origem)s,
                %(nivel_confianca)s,
                %(memoria_json)s::jsonb,
                %(tags)s,
                TRUE,
                NOW()
            )
            ON CONFLICT (usuario_id)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                idioma = EXCLUDED.idioma,
                moeda = EXCLUDED.moeda,
                renda_mensal = EXCLUDED.renda_mensal,
                gastos_mensais = EXCLUDED.gastos_mensais,
                valor_reserva = EXCLUDED.valor_reserva,
                possui_dividas = EXCLUDED.possui_dividas,
                uso_cartao_credito = EXCLUDED.uso_cartao_credito,
                ultimo_score = EXCLUDED.ultimo_score,
                ultimo_risco = EXCLUDED.ultimo_risco,
                ultima_meta = EXCLUDED.ultima_meta,
                resumo_contexto = EXCLUDED.resumo_contexto,
                perfil_financeiro = EXCLUDED.perfil_financeiro,
                objetivo_principal = EXCLUDED.objetivo_principal,
                preferencia_linguagem = EXCLUDED.preferencia_linguagem,
                canal_origem = EXCLUDED.canal_origem,
                nivel_confianca = EXCLUDED.nivel_confianca,
                memoria_json = EXCLUDED.memoria_json,
                tags = EXCLUDED.tags,
                ativo = TRUE,
                atualizado_em = NOW()
            RETURNING *;
        """, {
            "usuario_id": usuario_id,
            "nome": dados_memoria.get("nome"),
            "idioma": dados_memoria.get("idioma", "pt"),
            "moeda": dados_memoria.get("moeda", "BRL"),
            "renda_mensal": dados_memoria.get("renda_mensal"),
            "gastos_mensais": dados_memoria.get("gastos_mensais"),
            "valor_reserva": dados_memoria.get("valor_reserva"),
            "possui_dividas": dados_memoria.get("possui_dividas"),
            "uso_cartao_credito": dados_memoria.get("uso_cartao_credito"),
            "ultimo_score": dados_memoria.get("ultimo_score"),
            "ultimo_risco": dados_memoria.get("ultimo_risco"),
            "ultima_meta": dados_memoria.get("ultima_meta"),
            "resumo_contexto": dados_memoria.get("resumo_contexto"),
            "perfil_financeiro": dados_memoria.get("perfil_financeiro"),
            "objetivo_principal": dados_memoria.get("objetivo_principal"),
            "preferencia_linguagem": dados_memoria.get("preferencia_linguagem", "simples"),
            "canal_origem": origem,
            "nivel_confianca": dados_memoria.get("nivel_confianca", 1.0),
            "memoria_json": json.dumps(memoria_json, ensure_ascii=False),
            "tags": dados_memoria.get("tags", []),
        })

        depois = cur.fetchone()

        tipo_evento = "memoria_criada" if antes is None else "memoria_atualizada"

        cur.execute("""
            INSERT INTO memoria_eventos_inna (
                usuario_id,
                tipo_evento,
                origem,
                dados_antes,
                dados_depois,
                resumo_evento
            )
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s);
        """, (
            usuario_id,
            tipo_evento,
            origem,
            json.dumps(dict(antes), default=str, ensure_ascii=False) if antes else None,
            json.dumps(dict(depois), default=str, ensure_ascii=False),
            dados_memoria.get("resumo_contexto") or "Memória do usuário salva/atualizada."
        ))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "ok": True,
            "message": f"Memória do usuário {usuario_id} salva/atualizada com sucesso.",
            "tipo_evento": tipo_evento
        }

    except Exception as e:
        return {
            "ok": False,
            "message": f"Erro ao salvar memória: {e}"
        }


def buscar_memoria_inna(usuario_id):
    """
    Adaptador oficial para o repositório modular de memória.

    A implementação PostgreSQL está em:
    src/services/memory/repository.py
    """
    try:
        from services.memory.repository import (
            buscar_memoria_usuario
        )
    except ImportError:
        from src.services.memory.repository import (
            buscar_memoria_usuario
        )

    return buscar_memoria_usuario(
        usuario_id=usuario_id,
        somente_ativa=True,
    )



MEMORY_PAGE_TEXTS = {
    "pt": {
        "title": "## 🧠 Memória do Usuário — INNA",
        "caption": (
            "Os campos abaixo são carregados diretamente "
            "da memória persistente armazenada no "
            "Neon/PostgreSQL."
        ),
        "user_id": "ID do usuário",
        "user_id_required": (
            "Informe o ID do usuário para carregar a memória."
        ),
        "memory_loaded": (
            "Memória atual de {user_id} carregada do banco."
        ),
        "memory_not_found": (
            "Nenhuma memória encontrada para {user_id}. "
            "O formulário será iniciado vazio."
        ),
        "main_financial_data": (
            "### Dados financeiros principais"
        ),
        "name": "Nome",
        "monthly_income": "Renda mensal",
        "language": "Idioma",
        "monthly_expenses": "Gastos mensais",
        "currency": "Moeda",
        "monthly_savings": (
            "Valor que consegue guardar por mês"
        ),
        "has_debts": "Possui dívidas?",
        "uses_credit_card": (
            "Usa cartão de crédito?"
        ),
        "profile_context": "### Perfil e contexto",
        "financial_profile": "Perfil financeiro",
        "main_goal": "Objetivo principal",
        "language_preference": (
            "Preferência de linguagem"
        ),
        "latest_score": "Último score",
        "latest_risk": "Último risco",
        "latest_goal": "Última meta",
        "memory_summary": "Resumo da memória",
    },
    "en_us": {
        "title": "## 🧠 User Memory — INNA",
        "caption": (
            "The fields below are loaded directly from "
            "the persistent memory stored in "
            "Neon/PostgreSQL."
        ),
        "user_id": "User ID",
        "user_id_required": (
            "Enter the user ID to load the memory."
        ),
        "memory_loaded": (
            "Current memory for {user_id} loaded from the database."
        ),
        "memory_not_found": (
            "No memory was found for {user_id}. "
            "The form will start empty."
        ),
        "main_financial_data": (
            "### Main financial data"
        ),
        "name": "Name",
        "monthly_income": "Monthly income",
        "language": "Language",
        "monthly_expenses": "Monthly expenses",
        "currency": "Currency",
        "monthly_savings": (
            "Amount that can be saved per month"
        ),
        "has_debts": "Has debts?",
        "uses_credit_card": (
            "Uses a credit card?"
        ),
        "profile_context": "### Profile and context",
        "financial_profile": "Financial profile",
        "main_goal": "Main goal",
        "language_preference": (
            "Language preference"
        ),
        "latest_score": "Latest score",
        "latest_risk": "Latest risk",
        "latest_goal": "Latest goal",
        "memory_summary": "Memory summary",
    },
    "es": {
        "title": "## 🧠 Memoria del Usuario — INNA",
        "caption": (
            "Los campos siguientes se cargan directamente "
            "desde la memoria persistente almacenada en "
            "Neon/PostgreSQL."
        ),
        "user_id": "ID del usuario",
        "user_id_required": (
            "Informe el ID del usuario para cargar la memoria."
        ),
        "memory_loaded": (
            "Memoria actual de {user_id} cargada desde la base."
        ),
        "memory_not_found": (
            "No se encontró memoria para {user_id}. "
            "El formulario comenzará vacío."
        ),
        "main_financial_data": (
            "### Datos financieros principales"
        ),
        "name": "Nombre",
        "monthly_income": "Ingresos mensuales",
        "language": "Idioma",
        "monthly_expenses": "Gastos mensuales",
        "currency": "Moneda",
        "monthly_savings": (
            "Valor que puede guardar por mes"
        ),
        "has_debts": "¿Tiene deudas?",
        "uses_credit_card": (
            "¿Usa tarjeta de crédito?"
        ),
        "profile_context": "### Perfil y contexto",
        "financial_profile": "Perfil financiero",
        "main_goal": "Objetivo principal",
        "language_preference": (
            "Preferencia de lenguaje"
        ),
        "latest_score": "Último score",
        "latest_risk": "Último riesgo",
        "latest_goal": "Última meta",
        "memory_summary": "Resumen de la memoria",
    },
    "fr": {
        "title": "## 🧠 Mémoire Utilisateur — INNA",
        "caption": (
            "Les champs ci-dessous sont chargés directement "
            "depuis la mémoire persistante stockée dans "
            "Neon/PostgreSQL."
        ),
        "user_id": "ID utilisateur",
        "user_id_required": (
            "Saisissez l’ID utilisateur pour charger la mémoire."
        ),
        "memory_loaded": (
            "Mémoire actuelle de {user_id} chargée depuis la base."
        ),
        "memory_not_found": (
            "Aucune mémoire trouvée pour {user_id}. "
            "Le formulaire sera initialisé vide."
        ),
        "main_financial_data": (
            "### Données financières principales"
        ),
        "name": "Nom",
        "monthly_income": "Revenu mensuel",
        "language": "Langue",
        "monthly_expenses": "Dépenses mensuelles",
        "currency": "Devise",
        "monthly_savings": (
            "Montant pouvant être épargné par mois"
        ),
        "has_debts": "Possède des dettes ?",
        "uses_credit_card": (
            "Utilise une carte de crédit ?"
        ),
        "profile_context": "### Profil et contexte",
        "financial_profile": "Profil financier",
        "main_goal": "Objectif principal",
        "language_preference": (
            "Préférence de langage"
        ),
        "latest_score": "Dernier score",
        "latest_risk": "Dernier risque",
        "latest_goal": "Dernier objectif",
        "memory_summary": "Résumé de la mémoire",
    },
    "de": {
        "title": "## 🧠 Benutzerspeicher — INNA",
        "caption": (
            "Die folgenden Felder werden direkt aus "
            "dem persistenten Speicher in "
            "Neon/PostgreSQL geladen."
        ),
        "user_id": "Benutzer-ID",
        "user_id_required": (
            "Geben Sie die Benutzer-ID ein, um den Speicher zu laden."
        ),
        "memory_loaded": (
            "Aktueller Speicher für {user_id} aus der Datenbank geladen."
        ),
        "memory_not_found": (
            "Kein Speicher für {user_id} gefunden. "
            "Das Formular wird leer gestartet."
        ),
        "main_financial_data": (
            "### Wichtigste Finanzdaten"
        ),
        "name": "Name",
        "monthly_income": "Monatliches Einkommen",
        "language": "Sprache",
        "monthly_expenses": "Monatliche Ausgaben",
        "currency": "Währung",
        "monthly_savings": (
            "Monatlich möglicher Sparbetrag"
        ),
        "has_debts": "Hat Schulden?",
        "uses_credit_card": (
            "Verwendet eine Kreditkarte?"
        ),
        "profile_context": "### Profil und Kontext",
        "financial_profile": "Finanzprofil",
        "main_goal": "Hauptziel",
        "language_preference": (
            "Sprachpräferenz"
        ),
        "latest_score": "Letzter Score",
        "latest_risk": "Letztes Risiko",
        "latest_goal": "Letztes Ziel",
        "memory_summary": "Speicherzusammenfassung",
    },
}

MEMORY_PAGE_TEXTS["en_gb"] = MEMORY_PAGE_TEXTS["en_us"]

for idioma in (
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
):
    MEMORY_PAGE_TEXTS[idioma] = MEMORY_PAGE_TEXTS["en_us"]

MEMORY_PAGE_TEXTS["ch"] = MEMORY_PAGE_TEXTS["de"]


MEMORY_PAGE_EXTRA_TEXTS = {
    "pt": {
        "tags": "Tags separadas por vírgula",
        "advanced_json": "Memória JSON avançada",
        "confirm_update": (
            "Confirmo que revisei os dados e desejo "
            "atualizar a memória"
        ),
        "save_memory": "💾 Salvar memória revisada",
        "calculated_summary": "### Resumo calculado",
        "estimated_monthly_balance": (
            "Saldo mensal estimado"
        ),
        "weekly_capacity": "Capacidade semanal",
        "committed_income": "Renda comprometida",
        "confirmation_required": (
            "Marque a confirmação antes de atualizar "
            "a memória."
        ),
        "invalid_json": "Memória JSON inválida",
        "event_registered": "Evento registrado",
        "stored_memory": "### Memória atual armazenada",
        "current_income": "Renda atual",
        "current_expenses": "Gastos atuais",
        "current_reserve": "Reserva atual",
        "view_database_record": (
            "Ver registro completo do banco"
        ),
        "no_stored_memory": (
            "Nenhuma memória armazenada para este usuário."
        ),
    },
    "en_us": {
        "tags": "Comma-separated tags",
        "advanced_json": "Advanced memory JSON",
        "confirm_update": (
            "I confirm that I reviewed the data and "
            "want to update the memory"
        ),
        "save_memory": "💾 Save reviewed memory",
        "calculated_summary": "### Calculated summary",
        "estimated_monthly_balance": (
            "Estimated monthly balance"
        ),
        "weekly_capacity": "Weekly capacity",
        "committed_income": "Committed income",
        "confirmation_required": (
            "Select the confirmation before updating "
            "the memory."
        ),
        "invalid_json": "Invalid memory JSON",
        "event_registered": "Event registered",
        "stored_memory": "### Currently stored memory",
        "current_income": "Current income",
        "current_expenses": "Current expenses",
        "current_reserve": "Current reserve",
        "view_database_record": (
            "View complete database record"
        ),
        "no_stored_memory": (
            "No memory is stored for this user."
        ),
    },
    "es": {
        "tags": "Tags separadas por comas",
        "advanced_json": "Memoria JSON avanzada",
        "confirm_update": (
            "Confirmo que revisé los datos y deseo "
            "actualizar la memoria"
        ),
        "save_memory": "💾 Guardar memoria revisada",
        "calculated_summary": "### Resumen calculado",
        "estimated_monthly_balance": (
            "Saldo mensual estimado"
        ),
        "weekly_capacity": "Capacidad semanal",
        "committed_income": "Ingresos comprometidos",
        "confirmation_required": (
            "Marque la confirmación antes de actualizar "
            "la memoria."
        ),
        "invalid_json": "Memoria JSON inválida",
        "event_registered": "Evento registrado",
        "stored_memory": "### Memoria almacenada actualmente",
        "current_income": "Ingresos actuales",
        "current_expenses": "Gastos actuales",
        "current_reserve": "Reserva actual",
        "view_database_record": (
            "Ver registro completo de la base"
        ),
        "no_stored_memory": (
            "No hay memoria almacenada para este usuario."
        ),
    },
    "fr": {
        "tags": "Tags séparés par des virgules",
        "advanced_json": "Mémoire JSON avancée",
        "confirm_update": (
            "Je confirme avoir vérifié les données et "
            "souhaite mettre à jour la mémoire"
        ),
        "save_memory": "💾 Enregistrer la mémoire révisée",
        "calculated_summary": "### Résumé calculé",
        "estimated_monthly_balance": (
            "Solde mensuel estimé"
        ),
        "weekly_capacity": "Capacité hebdomadaire",
        "committed_income": "Revenu engagé",
        "confirmation_required": (
            "Cochez la confirmation avant de mettre "
            "la mémoire à jour."
        ),
        "invalid_json": "Mémoire JSON invalide",
        "event_registered": "Événement enregistré",
        "stored_memory": "### Mémoire actuellement stockée",
        "current_income": "Revenu actuel",
        "current_expenses": "Dépenses actuelles",
        "current_reserve": "Réserve actuelle",
        "view_database_record": (
            "Voir l’enregistrement complet de la base"
        ),
        "no_stored_memory": (
            "Aucune mémoire stockée pour cet utilisateur."
        ),
    },
    "de": {
        "tags": "Kommagetrennte Tags",
        "advanced_json": "Erweiterter Speicher-JSON",
        "confirm_update": (
            "Ich bestätige, dass ich die Daten geprüft "
            "habe und den Speicher aktualisieren möchte"
        ),
        "save_memory": "💾 Geprüften Speicher speichern",
        "calculated_summary": "### Berechnete Zusammenfassung",
        "estimated_monthly_balance": (
            "Geschätzter monatlicher Saldo"
        ),
        "weekly_capacity": "Wöchentliche Kapazität",
        "committed_income": "Gebundenes Einkommen",
        "confirmation_required": (
            "Bestätigen Sie die Prüfung, bevor Sie "
            "den Speicher aktualisieren."
        ),
        "invalid_json": "Ungültiger Speicher-JSON",
        "event_registered": "Ereignis registriert",
        "stored_memory": "### Aktuell gespeicherter Speicher",
        "current_income": "Aktuelles Einkommen",
        "current_expenses": "Aktuelle Ausgaben",
        "current_reserve": "Aktuelle Rücklage",
        "view_database_record": (
            "Vollständigen Datenbankeintrag anzeigen"
        ),
        "no_stored_memory": (
            "Für diesen Benutzer ist kein Speicher vorhanden."
        ),
    },
}

MEMORY_PAGE_EXTRA_TEXTS["en_gb"] = (
    MEMORY_PAGE_EXTRA_TEXTS["en_us"]
)

for idioma in (
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
):
    MEMORY_PAGE_EXTRA_TEXTS[idioma] = (
        MEMORY_PAGE_EXTRA_TEXTS["en_us"]
    )

MEMORY_PAGE_EXTRA_TEXTS["ch"] = (
    MEMORY_PAGE_EXTRA_TEXTS["de"]
)

for idioma, textos in (
    MEMORY_PAGE_EXTRA_TEXTS.items()
):
    MEMORY_PAGE_TEXTS.setdefault(
        idioma,
        {},
    ).update(textos)



# BLOCK_4B_NATIVE_MEMORY_TRANSLATIONS
# Traduções nativas finais da página Memória do Usuário.

MEMORY_PAGE_NATIVE_TEXTS = {
    "it": {
        "title": "## 🧠 Memoria Utente — INNA",
        "caption": (
            "Consulta, revisione e aggiornamento controllato "
            "della memoria finanziaria persistente."
        ),
        "user_id": "ID utente",
        "user_id_required": (
            "Inserisci l’ID utente per caricare la memoria."
        ),
        "memory_loaded": (
            "Memoria corrente di {user_id} caricata "
            "dal database."
        ),
        "memory_not_found": (
            "Nessuna memoria trovata per {user_id}. "
            "Il modulo verrà avviato vuoto."
        ),
        "main_financial_data": (
            "### Dati finanziari principali"
        ),
        "name": "Nome",
        "monthly_income": "Reddito mensile",
        "language": "Lingua",
        "monthly_expenses": "Spese mensili",
        "currency": "Valuta",
        "monthly_savings": (
            "Importo mensile disponibile per il risparmio"
        ),
        "has_debts": "Ha debiti?",
        "uses_credit_card": (
            "Utilizza una carta di credito?"
        ),
        "profile_context": "### Profilo e contesto",
        "financial_profile": "Profilo finanziario",
        "main_goal": "Obiettivo principale",
        "language_preference": (
            "Preferenza linguistica"
        ),
        "latest_score": "Punteggio più recente",
        "latest_risk": "Rischio più recente",
        "latest_goal": "Ultimo obiettivo",
        "memory_summary": "Riepilogo della memoria",
        "tags": "Tag separati da virgole",
        "advanced_json": "JSON avanzato della memoria",
        "confirm_update": (
            "Confermo di aver revisionato i dati e "
            "di voler aggiornare la memoria"
        ),
        "save_memory": (
            "💾 Salva memoria revisionata"
        ),
        "calculated_summary": (
            "### Riepilogo calcolato"
        ),
        "estimated_monthly_balance": (
            "Saldo mensile stimato"
        ),
        "weekly_capacity": "Capacità settimanale",
        "committed_income": "Reddito impegnato",
        "confirmation_required": (
            "Seleziona la conferma prima di aggiornare "
            "la memoria."
        ),
        "invalid_json": "JSON della memoria non valido",
        "event_registered": "Evento registrato",
        "stored_memory": (
            "### Memoria attualmente archiviata"
        ),
        "current_income": "Reddito attuale",
        "current_expenses": "Spese attuali",
        "current_reserve": "Riserva attuale",
        "view_database_record": (
            "Visualizza il record completo del database"
        ),
        "no_stored_memory": (
            "Nessuna memoria archiviata per questo utente."
        ),
    },
    "ro": {
        "title": "## 🧠 Memoria Utilizatorului — INNA",
        "caption": (
            "Consultarea, revizuirea și actualizarea controlată "
            "a memoriei financiare persistente."
        ),
        "user_id": "ID utilizator",
        "user_id_required": (
            "Introduceți ID-ul utilizatorului pentru "
            "a încărca memoria."
        ),
        "memory_loaded": (
            "Memoria curentă pentru {user_id} a fost "
            "încărcată din baza de date."
        ),
        "memory_not_found": (
            "Nu a fost găsită nicio memorie pentru {user_id}. "
            "Formularul va porni gol."
        ),
        "main_financial_data": (
            "### Date financiare principale"
        ),
        "name": "Nume",
        "monthly_income": "Venit lunar",
        "language": "Limbă",
        "monthly_expenses": "Cheltuieli lunare",
        "currency": "Monedă",
        "monthly_savings": (
            "Sumă lunară disponibilă pentru economisire"
        ),
        "has_debts": "Are datorii?",
        "uses_credit_card": (
            "Folosește un card de credit?"
        ),
        "profile_context": "### Profil și context",
        "financial_profile": "Profil financiar",
        "main_goal": "Obiectiv principal",
        "language_preference": (
            "Preferință lingvistică"
        ),
        "latest_score": "Cel mai recent scor",
        "latest_risk": "Cel mai recent risc",
        "latest_goal": "Cel mai recent obiectiv",
        "memory_summary": "Rezumatul memoriei",
        "tags": "Etichete separate prin virgulă",
        "advanced_json": "JSON avansat al memoriei",
        "confirm_update": (
            "Confirm că am revizuit datele și doresc "
            "să actualizez memoria"
        ),
        "save_memory": (
            "💾 Salvați memoria revizuită"
        ),
        "calculated_summary": "### Rezumat calculat",
        "estimated_monthly_balance": (
            "Sold lunar estimat"
        ),
        "weekly_capacity": (
            "Capacitate săptămânală"
        ),
        "committed_income": "Venit angajat",
        "confirmation_required": (
            "Selectați confirmarea înainte de "
            "actualizarea memoriei."
        ),
        "invalid_json": "JSON de memorie nevalid",
        "event_registered": "Eveniment înregistrat",
        "stored_memory": (
            "### Memorie stocată în prezent"
        ),
        "current_income": "Venit curent",
        "current_expenses": "Cheltuieli curente",
        "current_reserve": "Rezervă curentă",
        "view_database_record": (
            "Vizualizați înregistrarea completă din bază"
        ),
        "no_stored_memory": (
            "Nu există memorie stocată pentru acest utilizator."
        ),
    },
    "ua": {
        "title": "## 🧠 Пам’ять Користувача — INNA",
        "caption": (
            "Перегляд, перевірка та контрольоване оновлення "
            "постійної фінансової пам’яті."
        ),
        "user_id": "ID користувача",
        "user_id_required": (
            "Введіть ID користувача, щоб завантажити пам’ять."
        ),
        "memory_loaded": (
            "Поточну пам’ять для {user_id} завантажено "
            "з бази даних."
        ),
        "memory_not_found": (
            "Пам’ять для {user_id} не знайдено. "
            "Форму буде відкрито порожньою."
        ),
        "main_financial_data": (
            "### Основні фінансові дані"
        ),
        "name": "Ім’я",
        "monthly_income": "Місячний дохід",
        "language": "Мова",
        "monthly_expenses": "Місячні витрати",
        "currency": "Валюта",
        "monthly_savings": (
            "Місячна сума, доступна для заощаджень"
        ),
        "has_debts": "Має борги?",
        "uses_credit_card": (
            "Користується кредитною карткою?"
        ),
        "profile_context": "### Профіль і контекст",
        "financial_profile": "Фінансовий профіль",
        "main_goal": "Основна мета",
        "language_preference": "Мовні налаштування",
        "latest_score": "Останній бал",
        "latest_risk": "Останній ризик",
        "latest_goal": "Остання мета",
        "memory_summary": "Підсумок пам’яті",
        "tags": "Теги, розділені комами",
        "advanced_json": "Розширений JSON пам’яті",
        "confirm_update": (
            "Підтверджую, що перевірив дані та "
            "бажаю оновити пам’ять"
        ),
        "save_memory": (
            "💾 Зберегти перевірену пам’ять"
        ),
        "calculated_summary": (
            "### Розрахований підсумок"
        ),
        "estimated_monthly_balance": (
            "Орієнтовний місячний баланс"
        ),
        "weekly_capacity": "Тижнева спроможність",
        "committed_income": "Зобов’язаний дохід",
        "confirmation_required": (
            "Перед оновленням пам’яті встановіть "
            "прапорець підтвердження."
        ),
        "invalid_json": "Недійсний JSON пам’яті",
        "event_registered": "Подію зареєстровано",
        "stored_memory": (
            "### Поточна збережена пам’ять"
        ),
        "current_income": "Поточний дохід",
        "current_expenses": "Поточні витрати",
        "current_reserve": "Поточний резерв",
        "view_database_record": (
            "Переглянути повний запис бази даних"
        ),
        "no_stored_memory": (
            "Для цього користувача немає збереженої пам’яті."
        ),
    },
    "ru": {
        "title": "## 🧠 Память Пользователя — INNA",
        "caption": (
            "Просмотр, проверка и контролируемое обновление "
            "постоянной финансовой памяти."
        ),
        "user_id": "ID пользователя",
        "user_id_required": (
            "Введите ID пользователя для загрузки памяти."
        ),
        "memory_loaded": (
            "Текущая память для {user_id} загружена "
            "из базы данных."
        ),
        "memory_not_found": (
            "Память для {user_id} не найдена. "
            "Форма будет открыта пустой."
        ),
        "main_financial_data": (
            "### Основные финансовые данные"
        ),
        "name": "Имя",
        "monthly_income": "Месячный доход",
        "language": "Язык",
        "monthly_expenses": "Месячные расходы",
        "currency": "Валюта",
        "monthly_savings": (
            "Месячная сумма, доступная для накоплений"
        ),
        "has_debts": "Есть долги?",
        "uses_credit_card": (
            "Использует кредитную карту?"
        ),
        "profile_context": "### Профиль и контекст",
        "financial_profile": "Финансовый профиль",
        "main_goal": "Основная цель",
        "language_preference": (
            "Языковые предпочтения"
        ),
        "latest_score": "Последний балл",
        "latest_risk": "Последний риск",
        "latest_goal": "Последняя цель",
        "memory_summary": "Сводка памяти",
        "tags": "Теги через запятую",
        "advanced_json": "Расширенный JSON памяти",
        "confirm_update": (
            "Подтверждаю, что проверил данные и "
            "хочу обновить память"
        ),
        "save_memory": (
            "💾 Сохранить проверенную память"
        ),
        "calculated_summary": (
            "### Рассчитанная сводка"
        ),
        "estimated_monthly_balance": (
            "Расчётный месячный баланс"
        ),
        "weekly_capacity": "Недельная возможность",
        "committed_income": "Обязательный доход",
        "confirmation_required": (
            "Перед обновлением памяти установите "
            "флажок подтверждения."
        ),
        "invalid_json": "Недопустимый JSON памяти",
        "event_registered": "Событие зарегистрировано",
        "stored_memory": (
            "### Текущая сохранённая память"
        ),
        "current_income": "Текущий доход",
        "current_expenses": "Текущие расходы",
        "current_reserve": "Текущий резерв",
        "view_database_record": (
            "Показать полную запись базы данных"
        ),
        "no_stored_memory": (
            "Для этого пользователя нет сохранённой памяти."
        ),
    },
    "sa": {
        "title": "## 🧠 ذاكرة المستخدم — INNA",
        "caption": (
            "عرض الذاكرة المالية الدائمة ومراجعتها "
            "وتحديثها بصورة خاضعة للتحكم."
        ),
        "user_id": "معرّف المستخدم",
        "user_id_required": (
            "أدخل معرّف المستخدم لتحميل الذاكرة."
        ),
        "memory_loaded": (
            "تم تحميل الذاكرة الحالية للمستخدم "
            "{user_id} من قاعدة البيانات."
        ),
        "memory_not_found": (
            "لم يتم العثور على ذاكرة للمستخدم {user_id}. "
            "سيتم فتح النموذج فارغًا."
        ),
        "main_financial_data": (
            "### البيانات المالية الرئيسية"
        ),
        "name": "الاسم",
        "monthly_income": "الدخل الشهري",
        "language": "اللغة",
        "monthly_expenses": "المصروفات الشهرية",
        "currency": "العملة",
        "monthly_savings": (
            "المبلغ الشهري المتاح للادخار"
        ),
        "has_debts": "هل توجد ديون؟",
        "uses_credit_card": (
            "هل يستخدم بطاقة ائتمان؟"
        ),
        "profile_context": "### الملف والسياق",
        "financial_profile": "الملف المالي",
        "main_goal": "الهدف الرئيسي",
        "language_preference": "تفضيل اللغة",
        "latest_score": "أحدث نتيجة",
        "latest_risk": "أحدث مستوى مخاطر",
        "latest_goal": "أحدث هدف",
        "memory_summary": "ملخص الذاكرة",
        "tags": "وسوم مفصولة بفواصل",
        "advanced_json": "JSON متقدم للذاكرة",
        "confirm_update": (
            "أؤكد أنني راجعت البيانات وأرغب "
            "في تحديث الذاكرة"
        ),
        "save_memory": (
            "💾 حفظ الذاكرة بعد المراجعة"
        ),
        "calculated_summary": (
            "### الملخص المحسوب"
        ),
        "estimated_monthly_balance": (
            "الرصيد الشهري التقديري"
        ),
        "weekly_capacity": "القدرة الأسبوعية",
        "committed_income": "الدخل الملتزم",
        "confirmation_required": (
            "حدد التأكيد قبل تحديث الذاكرة."
        ),
        "invalid_json": "JSON الذاكرة غير صالح",
        "event_registered": "تم تسجيل الحدث",
        "stored_memory": (
            "### الذاكرة المحفوظة حاليًا"
        ),
        "current_income": "الدخل الحالي",
        "current_expenses": "المصروفات الحالية",
        "current_reserve": "الاحتياطي الحالي",
        "view_database_record": (
            "عرض سجل قاعدة البيانات الكامل"
        ),
        "no_stored_memory": (
            "لا توجد ذاكرة محفوظة لهذا المستخدم."
        ),
    },
}

for _language, _texts in (
    MEMORY_PAGE_NATIVE_TEXTS.items()
):
    # Cria um dicionário independente para impedir
    # sobrescrita entre idiomas que antes compartilhavam
    # o mesmo fallback em inglês.
    MEMORY_PAGE_TEXTS[
        _language
    ] = {
        **dict(
            MEMORY_PAGE_TEXTS.get(
                _language,
                {},
            )
        ),
        **dict(_texts),
    }


def memory_page_t(
    key,
    default=None,
    **format_values,
):
    return dashboard_page_translate(
        MEMORY_PAGE_TEXTS,
        key,
        language=dashboard_lang(),
        default=default,
        **format_values,
    )

def render_memoria_usuario_inna():

    import json
    import streamlit as st
    from decimal import Decimal

    st.markdown(memory_page_t("title"))
    st.caption(memory_page_t("caption"))

    def para_float(valor, padrao=0.0):
        if valor is None:
            return float(padrao)

        try:
            if isinstance(valor, Decimal):
                return float(valor)

            return float(valor)
        except (TypeError, ValueError):
            return float(padrao)

    def indice_seguro(opcoes, valor, padrao=0):
        try:
            return opcoes.index(valor)
        except ValueError:
            return padrao

    usuario_id = st.text_input(
        memory_page_t("user_id"),
        value="demo_user",
        key="memoria_usuario_id_inna"
    ).strip()

    if not usuario_id:
        st.warning(
            memory_page_t("user_id_required")
        )
        return

    resultado_busca = buscar_memoria_inna(usuario_id)

    if not resultado_busca.get("ok"):
        st.error(resultado_busca.get("message"))
        return

    memoria = resultado_busca.get("memoria") or {}

    if memoria:
        st.success(
            memory_page_t("memory_loaded").format(
                user_id=usuario_id
            )
        )
    else:
        st.info(
            memory_page_t("memory_not_found").format(
                user_id=usuario_id
            )
        )

    idiomas = ["pt", "en", "es", "fr", "de", "it", "ru", "ar"]
    moedas = ["BRL", "USD", "EUR"]
    perfis = [
        "iniciante",
        "organizando",
        "endividado",
        "equilibrado",
        "avancado"
    ]
    linguagens = ["simples", "detalhada", "técnica"]
    riscos = ["baixo", "moderado", "alto"]

    idioma_atual = memoria.get("idioma") or "pt"
    moeda_atual = memoria.get("moeda") or "BRL"
    perfil_atual = memoria.get("perfil_financeiro") or "organizando"
    linguagem_atual = memoria.get("preferencia_linguagem") or "simples"
    risco_atual = memoria.get("ultimo_risco") or "moderado"

    for valor, lista in [
        (idioma_atual, idiomas),
        (moeda_atual, moedas),
        (perfil_atual, perfis),
        (linguagem_atual, linguagens),
        (risco_atual, riscos),
    ]:
        if valor not in lista:
            lista.insert(0, valor)

    tags_atuais = memoria.get("tags") or []

    if isinstance(tags_atuais, list):
        tags_texto_atual = ",".join(str(tag) for tag in tags_atuais)
    else:
        tags_texto_atual = str(tags_atuais)

    memoria_json_atual = memoria.get("memoria_json") or {}

    if isinstance(memoria_json_atual, str):
        try:
            memoria_json_atual = json.loads(memoria_json_atual)
        except Exception:
            memoria_json_atual = {
                "conteudo_original": memoria_json_atual
            }

    with st.form("form_memoria_usuario_inna"):
        st.markdown(
            memory_page_t("main_financial_data")
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            nome = st.text_input(
                memory_page_t("name"),
                value=memoria.get("nome") or ""
            )

            renda_mensal = st.number_input(
                memory_page_t("monthly_income"),
                min_value=0.0,
                value=para_float(memoria.get("renda_mensal")),
                step=100.0,
                format="%.2f"
            )

        with col2:
            idioma = st.selectbox(
                memory_page_t("language"),
                idiomas,
                index=indice_seguro(idiomas, idioma_atual)
            )

            gastos_mensais = st.number_input(
                memory_page_t("monthly_expenses"),
                min_value=0.0,
                value=para_float(memoria.get("gastos_mensais")),
                step=100.0,
                format="%.2f"
            )

        with col3:
            moeda = st.selectbox(
                memory_page_t("currency"),
                moedas,
                index=indice_seguro(moedas, moeda_atual)
            )

            valor_reserva = st.number_input(
                memory_page_t("monthly_savings"),
                min_value=0.0,
                value=para_float(memoria.get("valor_reserva")),
                step=50.0,
                format="%.2f"
            )

        col_divida, col_cartao = st.columns(2)

        possui_dividas = col_divida.checkbox(
            memory_page_t("has_debts"),
            value=bool(memoria.get("possui_dividas"))
        )

        uso_cartao_credito = col_cartao.checkbox(
            memory_page_t("uses_credit_card"),
            value=bool(memoria.get("uso_cartao_credito"))
        )

        st.markdown(
            memory_page_t("profile_context")
        )

        perfil_financeiro = st.selectbox(
            memory_page_t("financial_profile"),
            perfis,
            index=indice_seguro(perfis, perfil_atual)
        )

        objetivo_principal = st.text_input(
            memory_page_t("main_goal"),
            value=memoria.get("objetivo_principal") or ""
        )

        preferencia_linguagem = st.selectbox(
            memory_page_t(
                "language_preference"
            ),
            linguagens,
            index=indice_seguro(linguagens, linguagem_atual)
        )

        col_score, col_risco = st.columns(2)

        ultimo_score = col_score.number_input(
            memory_page_t("latest_score"),
            min_value=0.0,
            max_value=100.0,
            value=para_float(memoria.get("ultimo_score")),
            step=1.0
        )

        ultimo_risco = col_risco.selectbox(
            memory_page_t("latest_risk"),
            riscos,
            index=indice_seguro(riscos, risco_atual)
        )

        ultima_meta = st.text_input(
            memory_page_t("latest_goal"),
            value=memoria.get("ultima_meta") or ""
        )

        resumo_contexto = st.text_area(
            memory_page_t("memory_summary"),
            value=memoria.get("resumo_contexto") or "",
            height=140
        )

        tags_texto = st.text_input(
            memory_page_t("tags"),
            value=tags_texto_atual
        )

        memoria_json_texto = st.text_area(
            memory_page_t("advanced_json"),
            value=json.dumps(
                memoria_json_atual,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            height=220
        )

        confirmar = st.checkbox(
            memory_page_t("confirm_update"),
            value=False
        )

        salvar = st.form_submit_button(
            memory_page_t("save_memory"),
            use_container_width=True
        )

    try:
        from services.formatter_inna import formatar_moeda
    except ImportError:
        from src.services.formatter_inna import formatar_moeda

    saldo_estimado = renda_mensal - gastos_mensais
    reserva_semanal = valor_reserva / 4 if valor_reserva else 0.0

    st.markdown(
        memory_page_t("calculated_summary")
    )

    col_saldo, col_semanal, col_comprometimento = st.columns(3)

    col_saldo.metric(
        memory_page_t(
            "estimated_monthly_balance"
        ),
        formatar_moeda(saldo_estimado, moeda)
    )

    col_semanal.metric(
        memory_page_t("weekly_capacity"),
        formatar_moeda(reserva_semanal, moeda)
    )

    percentual_comprometido = (
        (gastos_mensais / renda_mensal) * 100
        if renda_mensal > 0
        else 0.0
    )

    col_comprometimento.metric(
        memory_page_t("committed_income"),
        f"{percentual_comprometido:.1f}%"
    )

    if salvar:
        if not confirmar:
            st.warning(
                memory_page_t(
                    "confirmation_required"
                )
            )
            return

        try:
            memoria_json = json.loads(memoria_json_texto or "{}")
        except json.JSONDecodeError as erro:
            st.error(
                f"{memory_page_t('invalid_json')}: "
                f"{erro}"
            )
            return

        tags = [
            tag.strip()
            for tag in tags_texto.split(",")
            if tag.strip()
        ]

        dados = {
            "nome": nome,
            "idioma": idioma,
            "moeda": moeda,
            "renda_mensal": renda_mensal,
            "gastos_mensais": gastos_mensais,
            "valor_reserva": valor_reserva,
            "possui_dividas": possui_dividas,
            "uso_cartao_credito": uso_cartao_credito,
            "ultimo_score": ultimo_score,
            "ultimo_risco": ultimo_risco,
            "ultima_meta": ultima_meta,
            "resumo_contexto": resumo_contexto,
            "perfil_financeiro": perfil_financeiro,
            "objetivo_principal": objetivo_principal,
            "preferencia_linguagem": preferencia_linguagem,
            "nivel_confianca": 1.0,
            "memoria_json": memoria_json,
            "tags": tags,
        }

        resultado = salvar_ou_atualizar_memoria_inna(
            usuario_id=usuario_id,
            dados_memoria=dados,
            origem="dashboard_memoria_revisada"
        )

        if resultado.get("ok"):
            st.success(resultado.get("message"))
            st.caption(
                f"{memory_page_t('event_registered')}: "
                f"{resultado.get('tipo_evento')}"
            )
        else:
            st.error(resultado.get("message"))

    st.markdown("---")
    st.markdown(
        memory_page_t("stored_memory")
    )

    memoria_banco = (
        buscar_memoria_inna(usuario_id).get("memoria")
        or memoria
    )

    if memoria_banco:
        col_a, col_b, col_c = st.columns(3)

        col_a.metric(
            memory_page_t("current_income"),
            formatar_moeda(
                memoria_banco.get("renda_mensal"),
                memoria_banco.get("moeda") or "BRL"
            )
        )

        col_b.metric(
            memory_page_t("current_expenses"),
            formatar_moeda(
                memoria_banco.get("gastos_mensais"),
                memoria_banco.get("moeda") or "BRL"
            )
        )

        col_c.metric(
            memory_page_t("current_reserve"),
            formatar_moeda(
                memoria_banco.get("valor_reserva"),
                memoria_banco.get("moeda") or "BRL"
            )
        )

        with st.expander(
            memory_page_t(
                "view_database_record"
            )
        ):
            st.json(memoria_banco, expanded=False)
    else:
        st.info(
            memory_page_t("no_stored_memory")
        )



def main(
    *,
    embedded=False,
):

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
    ) = render_filters(
        diagnosticos_df,
        feedbacks_df,
        embedded=embedded,
    )

    render_header()

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

    if menu == "overview":
        render_overview(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "multichannel_events":
        render_events(eventos_filtrados, diagnosticos_filtrados, feedbacks_filtrados)

    elif menu == "international_view":
        render_international(diagnosticos_filtrados)

    elif menu == "diagnostics":
        render_diagnostics(diagnosticos_filtrados)

    elif menu == "feedbacks":
        render_feedbacks(feedbacks_filtrados)

    elif menu == "evolution":
        render_evolution(diagnosticos_filtrados)

    elif menu == "executive_reading":
        render_executive_reading(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "agent_evaluation":
        render_agent_evaluation(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)

    elif menu == "rag_observability":
        render_rag_observability()

    elif menu == "tools_observability":
        try:
            from dashboard_pages.tools_observability_page import (
                render_tools_observability_page
            )
        except ImportError:
            from src.dashboard_pages.tools_observability_page import (
                render_tools_observability_page
            )

        render_tools_observability_page()

    elif menu == "timeline_viewer":
        try:
            from dashboard_pages.timeline_viewer_page import (
                render_timeline_viewer_page
            )
        except ImportError:
            from src.dashboard_pages.timeline_viewer_page import (
                render_timeline_viewer_page
            )

        render_timeline_viewer_page()

    elif menu == "tools_analytics":
        try:
            from dashboard_pages.tools_analytics_page import (
                render_tools_analytics_page
            )
        except ImportError:
            from src.dashboard_pages.tools_analytics_page import (
                render_tools_analytics_page
            )

        render_tools_analytics_page()

    elif menu == "health_center":
        try:
            from dashboard_pages.health_score_page import (
                render_health_score_page
            )
        except ImportError:
            from src.dashboard_pages.health_score_page import (
                render_health_score_page
            )

        render_health_score_page()

    elif menu == "llmops_observability":
        try:
            from evaluation.dashboard import (
                render_llmops_dashboard
            )
        except ImportError:
            from src.evaluation.dashboard import (
                render_llmops_dashboard
            )

        render_llmops_dashboard(
            integrated=True
        )

    elif menu == "ai_cost_center":
        try:
            from dashboard_pages.llm_costs_page import (
                render_llm_costs_page
            )
        except ImportError:
            from src.dashboard_pages.llm_costs_page import (
                render_llm_costs_page
            )

        render_llm_costs_page()

    elif menu == "document_upload":
        render_upload_documentos_rag()

    elif menu == "user_memory":
        render_memoria_usuario_inna()

    elif menu == "export":
        render_export(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)


if __name__ == "__main__":
    main()

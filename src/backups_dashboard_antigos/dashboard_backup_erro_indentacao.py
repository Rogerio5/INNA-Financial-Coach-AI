
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
    "pt": "BR Português Brasil",
    "en_us": "US English US",
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
    "en_us": "US English US",
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
        "diagnostics": "Diagnoses",
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
        "diagnostics": "Diagnoses",
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
        "subtitle": "تحليلات مالية، ملاحظات المستخدمين والتحقق عبر PostgreSQL",
        "info": "تقرأ لوحة التحكم هذه البيانات مباشرة من PostgreSQL/Neon وتتحقق من الاستخدام الفعلي حسب القناة واللغة والعملة والتشخيص وPDF والبريد الإلكتروني وTelegram.",
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
        "👤 Diagnósticos": "👤 Diagnoses",
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
        "diagnostics": "Diagnoses",
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
        "subtitle": "تحليلات مالية، ملاحظات المستخدمين والتحقق عبر PostgreSQL",
        "info": "تقرأ لوحة التحكم هذه البيانات مباشرة من PostgreSQL/Neon وتتحقق من الاستخدام الفعلي حسب القناة واللغة والعملة والتشخيص وPDF والبريد الإلكتروني وTelegram.",
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
    "see_by_currency": "См. по валюте",
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
    "see_by_currency": "Vedi per valuta",
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
    "see_by_currency": "See by currency",
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
    "see_by_currency": "Ver por moeda",
    "all": "Todos",
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
    "see_by_currency": "Nach Währung anzeigen",
    "all": "Alle",
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
    "see_by_currency": "См. по валюте",
    "all": "Все",
})

DASHBOARD_TEXTS.setdefault("sa", {}).update({
    "user": "المستخدم",
    "language": "اللغة",
    "currency": "العملة",
    "latest_channel": "آخر قناة",
    "financial_score": "النتيجة المالية",
    "risk": "المخاطر",
    "estimated_balance": "الرصيد التقديري",
    "summary_help": "ملخص المستخدم المحدد مع اللغة والعملة والقناة والنتيجة والمخاطر والرصيد.",
    "see_by_currency": "عرض حسب العملة",
    "all": "الكل",
})

def dashboard_lang():
    return st.session_state.get("dashboard_interface_lang", "pt")

def dt(key):
    lang = dashboard_lang()
    textos = DASHBOARD_TEXTS.get(lang, DASHBOARD_TEXTS["pt"])
    return textos.get(key, DASHBOARD_TEXTS["pt"].get(key, key))

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
        "last_events": "View latest real events",
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
        "no_feedbacks": "No feedback found for the selected filters.",
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
        "no_feedback_export": "No filtered feedback to export.",
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
        format_func=dt_menu,
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


def render_filters(diagnosticos_df, feedbacks_df):
    st.sidebar.selectbox(
        dt("interface_lang"),
        options=list(DASHBOARD_INTERFACE_LANGS.keys()),
        format_func=lambda key: DASHBOARD_INTERFACE_LANGS[key],
        key="dashboard_interface_lang",
    )

    st.sidebar.title(dt("sidebar_title"))
    st.sidebar.caption(dt("sidebar_caption"))

        menu = st.sidebar.radio(
        dt("menu"),
        [
            "📌 Visão Geral",
            "🌐 Eventos Multicanal",
            "🌍 Visão Internacional",
            "👤 Diagnósticos",
            "💬 Feedbacks",
            "📈 Evolução",
            "🧠 Leitura Executiva",
            "🧪 Avaliação do Agente",
            "📊 Observabilidade RAG",
            "📤 Exportar",
        ],
        format_func=dt_menu,
        key="dashboard_menu",
    )

    st.sidebar.divider()
    st.sidebar.write(dt("filters"))

    today = date.today()

    if not diagnosticos_df.empty and "data_hora" in diagnosticos_df.columns:
        min_date = diagnosticos_df["data_hora"].min().date()
        max_date = diagnosticos_df["data_hora"].max().date()
    else:
        min_date = today
        max_date = today

    start_date = st.sidebar.date_input(dt("start_date"), value=min_date)
    end_date = st.sidebar.date_input(dt("end_date"), value=max_date)

    usuarios = ["Todos"]
    if not diagnosticos_df.empty and "nome" in diagnosticos_df.columns:
        usuarios += sorted(diagnosticos_df["nome"].dropna().astype(str).unique().tolist())

    filtro_usuario = st.sidebar.selectbox(dt("filter_user"), usuarios)

    riscos = ["Todos"]
    if not diagnosticos_df.empty and "nivel_risco" in diagnosticos_df.columns:
        temp = add_display_columns(diagnosticos_df)
        riscos += sorted(temp["risco_exibicao"].dropna().astype(str).unique().tolist())

    filtro_risco = st.sidebar.selectbox(dt("filter_risk"), riscos)

    feedbacks = ["Todos"]
    if not feedbacks_df.empty and "util" in feedbacks_df.columns:
        feedbacks += sorted(feedbacks_df["util"].dropna().astype(str).unique().tolist())

    filtro_feedback = st.sidebar.selectbox(dt("filter_feedback"), feedbacks)

    filtro_idioma = st.sidebar.selectbox(dt("filter_data_language"), FIXED_LANGUAGES)
    filtro_moeda = st.sidebar.selectbox(dt("filter_currency"), FIXED_CURRENCIES)

    st.sidebar.divider()
    st.sidebar.caption(dt("filter_help"))

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
        format_func=dt_menu,
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


def render_events(eventos_df, diagnosticos_df, feedbacks_df):
    st.write(dtx("events_title"))

    if eventos_df.empty:
        st.warning(dtx("no_events"))
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
            st.caption(dtx("only_one_channel"))

        canal_table = canal_counts.reset_index()
        canal_table.columns = ["canal", "quantidade"]
        st.dataframe(canal_table, use_container_width=True)

    with st.expander(dtx("last_events")):
        st.dataframe(eventos_df.head(20), use_container_width=True)

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
        st.caption(dtx("few_funnel_records"))

    st.dataframe(funil, use_container_width=True)


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
            st.bar_chart(idioma_counts)
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
            st.bar_chart(moeda_counts)
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
        lambda row: format_money(row["saldo_medio"], row["moeda"],
        format_func=dt_menu,
    ),
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
        lambda row: format_money(row["saldo_medio"], row["moeda"],
        format_func=dt_menu,
    ),
        axis=1,
    )

    st.dataframe(resumo, use_container_width=True)


def render_diagnostics(diagnosticos_df):
    st.write(dtx("diagnostics_title"))

    if diagnosticos_df.empty:
        st.warning(dtx("no_diagnostics"))
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(dtx("risk_distribution"))
        risk_counts = diagnosticos_df["risco_exibicao"].fillna("não informado").astype(str).value_counts()

        if len(risk_counts) > 1:
            st.bar_chart(risk_counts)
        else:
            st.caption(dtx("only_one_risk"))

        risk_table = risk_counts.reset_index()
        risk_table.columns = ["risco", "quantidade"]
        st.dataframe(risk_table, use_container_width=True)

    with col2:
        st.write(dtx("user_ranking"))
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

    st.write(dtx("last_diagnostics"))

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
    st.write(dtx("feedbacks_title"))

    if feedbacks_df.empty:
        st.warning(dtx("no_feedbacks"))
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(dtx("useful_feedbacks"))
        if "util" in feedbacks_df.columns:
            util_counts = feedbacks_df["util"].fillna("não informado").astype(str).value_counts()
            st.bar_chart(util_counts)
            st.dataframe(util_counts.reset_index(), use_container_width=True)

    with col2:
        st.write(dtx("received_comments"))
        comentario_cols = [col for col in ["data_hora", "nome", "comentario", "util"] if col in feedbacks_df.columns]
        if comentario_cols:
            st.dataframe(feedbacks_df[comentario_cols].head(30), use_container_width=True)
        else:
            st.caption(dtx("no_comments"))

    st.write(dtx("last_feedbacks"))
    st.dataframe(feedbacks_df.head(50), use_container_width=True)


def render_evolution(diagnosticos_df):
    st.write(dtx("evolution_title"))

    if diagnosticos_df.empty:
        st.warning(dtx("no_diagnostics"))
        return

    df = diagnosticos_df.copy()

    if "data_hora" in df.columns:
        df = df.sort_values("data_hora")
        df["data_label"] = df["data_hora"].dt.strftime("%d/%m %H:%M")
    else:
        df["data_label"] = df["id"].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        st.write(dtx("score_evolution"))
        if len(df) > 1:
            st.line_chart(df.set_index("data_label")["score_financeiro"],
        format_func=dt_menu,
    )
        else:
            st.caption(dtx("evolution_wait"))
            st.dataframe(df[["id", "nome", "score_financeiro"]], use_container_width=True)

    with col2:
        st.write(dtx("balance_evolution"))
        if len(df) > 1:
            st.line_chart(df.set_index("data_label")["saldo_estimado"],
        format_func=dt_menu,
    )
        else:
            st.caption(dtx("evolution_wait"))
            st.dataframe(df[["id", "nome", "saldo_formatado"]], use_container_width=True)


def render_executive_reading(diagnosticos_df, feedbacks_df, eventos_df):
    st.write(dtx("executive_title"))

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

    saldo_texto = dt("see_by_currency") if moeda == "MULTI" else format_money(saldo, moeda, simbolo)

    st.write(dtx("current_base_summary"))

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
    st.write(dtx("agent_eval_title"))

    st.info(
        "Esta página registra avaliações reais do agente INNA no PostgreSQL/Neon. "
        "As notas ajudam a medir assertividade, segurança, coerência, clareza e utilidade."
    )

    try:
        avaliacoes_df = load_agent_evaluations()
    except Exception as error:
        st.error(f"Erro ao carregar avaliações do agente: {error}")
        avaliacoes_df = pd.DataFrame()

    st.write(dtx("quality_indicators"))

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

    st.write(dtx("register_eval"))

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

    st.write(dtx("saved_evaluations"))

    try:
        avaliacoes_df = load_agent_evaluations()
    except Exception as error:
        st.error(f"Erro ao recarregar avaliações: {error}")
        avaliacoes_df = pd.DataFrame()

    if avaliacoes_df.empty:
        st.warning(dtx("no_saved_evaluations"))
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

    st.write(dtx("quality_metrics"))

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

    st.write(dtx("test_scenarios"))

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
            "Resultado esperado": "A INNA não indica investimento específico e evita inventar dados.",
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

    st.write(dtx("technical_observability"))

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

    st.divider()

    st.write(dtx("advanced_observability"))

    eventos_metricas = eventos_df.copy()

    tempo_medio = 0
    taxa_erro = 0
    eventos_sucesso = 0
    eventos_erro = 0
    total_tokens = 0
    custo_estimado = 0

    if not eventos_metricas.empty:
        if "status" in eventos_metricas.columns:
            status_series = eventos_metricas["status"].fillna("").astype(str).str.lower()

            eventos_sucesso = status_series.str.contains("success|sucesso|ok", regex=True).sum()
            eventos_erro = status_series.str.contains("error|erro|failed|falha", regex=True).sum()

            if total_eventos > 0:
                taxa_erro = (eventos_erro / total_eventos) * 100

        if "tempo_resposta_segundos" in eventos_metricas.columns:
            tempos = pd.to_numeric(
                eventos_metricas["tempo_resposta_segundos"],
                errors="coerce"
            ).dropna()

            if not tempos.empty:
                tempo_medio = tempos.mean()

        elif "metadata" in eventos_metricas.columns:
            def extrair_tempo(metadata):
                try:
                    if isinstance(metadata, dict):
                        return metadata.get("tempo_resposta_segundos")
                    return None
                except Exception:
                    return None

            tempos = pd.to_numeric(
                eventos_metricas["metadata"].apply(extrair_tempo),
                errors="coerce"
            ).dropna()

            if not tempos.empty:
                tempo_medio = tempos.mean()

        if "metadata" in eventos_metricas.columns:
            def extrair_tokens(metadata):
                try:
                    if isinstance(metadata, dict):
                        return (
                            metadata.get("total_tokens")
                            or metadata.get("tokens_total")
                            or metadata.get("tokens")
                            or 0
                        )
                    return 0
                except Exception:
                    return 0

            def extrair_custo(metadata):
                try:
                    if isinstance(metadata, dict):
                        return (
                            metadata.get("custo_estimado_usd")
                            or metadata.get("estimated_cost_usd")
                            or metadata.get("cost_usd")
                            or 0
                        )
                    return 0
                except Exception:
                    return 0

            total_tokens = pd.to_numeric(
                eventos_metricas["metadata"].apply(extrair_tokens),
                errors="coerce"
            ).fillna(0).sum()

            custo_estimado = pd.to_numeric(
                eventos_metricas["metadata"].apply(extrair_custo),
                errors="coerce"
            ).fillna(0).sum()

    col_adv1, col_adv2, col_adv3, col_adv4 = st.columns(4)

    col_adv1.metric("Tempo médio", f"{tempo_medio:.2f}s")
    col_adv2.metric("Taxa de erro", f"{taxa_erro:.1f}%")
    col_adv3.metric("Eventos sucesso", int(eventos_sucesso))
    col_adv4.metric("Eventos erro", int(eventos_erro))

    col_adv5, col_adv6, col_adv7 = st.columns(3)

    col_adv5.metric("Logs/eventos", total_eventos)
    col_adv6.metric("Tokens consumidos", int(total_tokens))
    col_adv7.metric("Custo estimado", f"US$ {float(custo_estimado):.4f}")

    st.caption(
        "Tokens e custo estimado aparecem com valor real quando a API salva essas informações "
        "no metadata dos eventos. Latência, status e logs já usam os eventos reais do Neon."
    )

    with st.expander("📘 Como interpretar as métricas avançadas"):
        st.markdown(
            """
| Métrica | O que mostra | Por que importa |
|---|---|---|
| **Tempo médio** | Média de resposta da API/agente | Ajuda a medir performance |
| **Taxa de erro** | Percentual de eventos com falha | Ajuda a encontrar problemas técnicos |
| **Eventos sucesso** | Interações concluídas corretamente | Mostra estabilidade da solução |
| **Eventos erro** | Interações com falha | Ajuda a priorizar correções |
| **Logs/eventos** | Total de registros no Neon | Mostra rastreabilidade |
| **Tokens consumidos** | Uso do modelo de IA | Ajuda a controlar consumo |
| **Custo estimado** | Custo aproximado da IA | Ajuda a controlar viabilidade financeira |
            """
        )

    st.divider()

    st.write(dtx("planned_metrics"))

    st.info(
        "Essas métricas fazem parte da evolução planejada da INNA. "
        "Elas ainda não estão ativas para evitar custos desnecessários neste momento, "
        "mas a arquitetura do projeto já está preparada para receber esses dados futuramente."
    )

    metricas_futuras = [
        {
            "Métrica planejada": "Tokens consumidos",
            "Objetivo": "Medir o consumo do modelo de IA por diagnóstico ou interação.",
            "Status": "Planejado",
        },
        {
            "Métrica planejada": "Custo estimado",
            "Objetivo": "Calcular o custo aproximado das chamadas de IA.",
            "Status": "Planejado",
        },
        {
            "Métrica planejada": "Preço por milhão de tokens",
            "Objetivo": "Permitir configurar valores por variável de ambiente no Render.",
            "Status": "Planejado",
        },
        {
            "Métrica planejada": "Modelo de IA utilizado",
            "Objetivo": "Registrar qual modelo respondeu cada diagnóstico.",
            "Status": "Planejado",
        },
        {
            "Métrica planejada": "Provider de IA",
            "Objetivo": "Registrar se a resposta veio de Gemini, fallback ou outro provedor.",
            "Status": "Planejado",
        },
    ]

    st.dataframe(pd.DataFrame(metricas_futuras), use_container_width=True)

    st.caption(
        "Quando a medição de tokens/custos for ativada, esses dados poderão ser salvos no metadata "
        "dos eventos da tabela interacoes_inna e exibidos automaticamente no dashboard."
    )

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




def render_rag_observability():
    st.write(dtx("rag_title"))

    try:
        try:
            from src.rag_engine import get_rag_connection
        except ModuleNotFoundError:
            from rag_engine import get_rag_connection

        conn = get_rag_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM inna_rag_logs;")
        total_logs = cur.fetchone()[0] or 0

        cur.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN usou_gemini THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN usou_seguranca THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN usou_fallback THEN 1 ELSE 0 END), 0),
            COALESCE(ROUND(AVG(tempo_resposta_ms), 2), 0),
            COALESCE(MAX(tempo_resposta_ms), 0)
        FROM inna_rag_logs;
        """)
        gemini_total, seguranca_total, fallback_total, tempo_medio, tempo_maximo = cur.fetchone()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Perguntas", total_logs)
        col2.metric("Gemini", gemini_total)
        col3.metric("Segurança", seguranca_total)
        col4.metric("Fallback", fallback_total)
        col5.metric("Tempo médio", f"{tempo_medio} ms")

        st.metric("Maior tempo de resposta", f"{tempo_maximo} ms")

        st.write(dtx("mode_distribution"))
        cur.execute("""
        SELECT modo, COUNT(*) AS total
        FROM inna_rag_logs
        GROUP BY modo
        ORDER BY total DESC;
        """)
        modos = cur.fetchall()

        if modos:
            st.dataframe(
                [{"modo": modo, "total": total} for modo, total in modos],
                use_container_width=True,
            )
        else:
            st.info(dtx("no_mode_logs"))

        st.write(dtx("last_questions"))
        cur.execute("""
        SELECT pergunta, modo, fontes_total, usou_gemini, usou_seguranca, usou_fallback, tempo_resposta_ms, created_at
        FROM inna_rag_logs
        ORDER BY id DESC
        LIMIT 30;
        """)
        ultimas = cur.fetchall()

        if ultimas:
            st.dataframe(
                [
                    {
                        "pergunta": pergunta,
                        "modo": modo,
                        "fontes": fontes_total,
                        "gemini": usou_gemini,
                        "segurança": usou_seguranca,
                        "fallback": usou_fallback,
                        "tempo_ms": tempo_resposta_ms,
                        "data": created_at,
                    }
                    for pergunta, modo, fontes_total, usou_gemini, usou_seguranca, usou_fallback, tempo_resposta_ms, created_at in ultimas
                ],
                use_container_width=True,
            )
        else:
            st.info(dtx("no_questions"))

        cur.close()
        conn.close()

    except Exception as error:
        st.warning(f"Não foi possível carregar métricas RAG: {error}")


def render_export(diagnosticos_df, feedbacks_df, eventos_df):
    st.write(dtx("export_title"))

    if not diagnosticos_df.empty:
        csv_diag = diagnosticos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar diagnósticos filtrados CSV",
            data=csv_diag,
            file_name="inna_diagnosticos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_diag_export"))

    if not feedbacks_df.empty:
        csv_feedbacks = feedbacks_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar feedbacks filtrados CSV",
            data=csv_feedbacks,
            file_name="inna_feedbacks_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_feedback_export"))

    if not eventos_df.empty:
        csv_eventos = eventos_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar eventos filtrados CSV",
            data=csv_eventos,
            file_name="inna_eventos_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.caption(dtx("no_events_export"))


def main():
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

    elif menu == "📊 Observabilidade RAG":
        render_rag_observability()

    elif menu == "📤 Exportar":
        render_export(diagnosticos_filtrados, feedbacks_filtrados, eventos_filtrados)
if __name__ == "__main__":
    main()

























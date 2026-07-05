from typing import Callable, Dict, Any


TRANSLATIONS = {
    "BR Português Brasil": {
        "interface_language": "🌍 Idioma da interface",
        "dashboard_title": "INNA Analytics",
        "admin_dashboard": "Dashboard administrativo",
        "menu": "Menu",

        "overview": "📌 Visão Geral",
        "multichannel_events": "🌐 Eventos Multicanal",
        "international_view": "🌍 Visão Internacional",
        "diagnostics": "👤 Diagnósticos",
        "feedbacks": "💬 Feedbacks",
        "evolution": "📈 Evolução",
        "executive_reading": "🧠 Leitura Executiva",
        "agent_evaluation": "🧪 Avaliação do Agente",
        "rag_observability": "📊 Observabilidade RAG",
        "export": "📤 Exportar",

        "filters": "🔎 Filtros",
        "start_date": "Data inicial",
        "end_date": "Data final",
        "filter_user": "Filtrar por usuário",
        "filter_risk": "Filtrar por risco",
        "filter_feedback": "Filtrar por feedback",
        "filter_data_language": "Filtrar por idioma dos dados",
        "filter_currency": "Filtrar por moeda",

        "all": "Todos",
        "low": "Baixo",
        "medium": "Médio",
        "high": "Alto",
        "useful": "Útil",
        "not_useful": "Não útil",
        "neutral": "Neutro",

        "update_data": "🔄 Atualizar dados",
        "main_indicators": "📌 Indicadores principais",
        "filtered_user_summary": "👤 Resumo do usuário filtrado",
        "user": "Usuário",
        "language": "Idioma",
        "currency": "Moeda",
        "last_channel": "Último canal",
        "financial_score": "Score financeiro",
        "risk": "Risco",
        "estimated_balance": "Saldo estimado",
        "average_score": "Score médio",
        "average_balance": "Saldo médio",
        "useful_feedback": "Feedback útil",
    },

    "EN English": {
        "interface_language": "🌍 Interface language",
        "dashboard_title": "INNA Analytics",
        "admin_dashboard": "Administrative Dashboard",
        "menu": "Menu",

        "overview": "📌 Overview",
        "multichannel_events": "🌐 Multichannel Events",
        "international_view": "🌍 International View",
        "diagnostics": "👤 Diagnostics",
        "feedbacks": "💬 Feedbacks",
        "evolution": "📈 Evolution",
        "executive_reading": "🧠 Executive Reading",
        "agent_evaluation": "🧪 Agent Evaluation",
        "rag_observability": "📊 RAG Observability",
        "export": "📤 Export",

        "filters": "🔎 Filters",
        "start_date": "Start date",
        "end_date": "End date",
        "filter_user": "Filter by user",
        "filter_risk": "Filter by risk",
        "filter_feedback": "Filter by feedback",
        "filter_data_language": "Filter by data language",
        "filter_currency": "Filter by currency",

        "all": "All",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "useful": "Useful",
        "not_useful": "Not useful",
        "neutral": "Neutral",

        "update_data": "🔄 Update data",
        "main_indicators": "📌 Main indicators",
        "filtered_user_summary": "👤 Filtered user summary",
        "user": "User",
        "language": "Language",
        "currency": "Currency",
        "last_channel": "Last channel",
        "financial_score": "Financial score",
        "risk": "Risk",
        "estimated_balance": "Estimated balance",
        "average_score": "Average score",
        "average_balance": "Average balance",
        "useful_feedback": "Useful feedback",
    },

    "ES Español": {
        "interface_language": "🌍 Idioma de la interfaz",
        "dashboard_title": "INNA Analytics",
        "admin_dashboard": "Panel administrativo",
        "menu": "Menú",

        "overview": "📌 Resumen",
        "multichannel_events": "🌐 Eventos multicanal",
        "international_view": "🌍 Vista internacional",
        "diagnostics": "👤 Diagnósticos",
        "feedbacks": "💬 Comentarios",
        "evolution": "📈 Evolución",
        "executive_reading": "🧠 Lectura ejecutiva",
        "agent_evaluation": "🧪 Evaluación del agente",
        "rag_observability": "📊 Observabilidad RAG",
        "export": "📤 Exportar",

        "filters": "🔎 Filtros",
        "start_date": "Fecha inicial",
        "end_date": "Fecha final",
        "filter_user": "Filtrar por usuario",
        "filter_risk": "Filtrar por riesgo",
        "filter_feedback": "Filtrar por comentario",
        "filter_data_language": "Filtrar por idioma de los datos",
        "filter_currency": "Filtrar por moneda",

        "all": "Todos",
        "low": "Bajo",
        "medium": "Medio",
        "high": "Alto",
        "useful": "Útil",
        "not_useful": "No útil",
        "neutral": "Neutral",

        "update_data": "🔄 Actualizar datos",
        "main_indicators": "📌 Indicadores principales",
        "filtered_user_summary": "👤 Resumen del usuario filtrado",
        "user": "Usuario",
        "language": "Idioma",
        "currency": "Moneda",
        "last_channel": "Último canal",
        "financial_score": "Puntuación financiera",
        "risk": "Riesgo",
        "estimated_balance": "Saldo estimado",
        "average_score": "Puntuación media",
        "average_balance": "Saldo medio",
        "useful_feedback": "Comentario útil",
    },

    "DE Deutsch": {
        "interface_language": "🌍 Sprache der Oberfläche",
        "dashboard_title": "INNA Analytics",
        "admin_dashboard": "Administratives Dashboard",
        "menu": "Menü",

        "overview": "📌 Übersicht",
        "multichannel_events": "🌐 Multichannel-Ereignisse",
        "international_view": "🌍 Internationale Ansicht",
        "diagnostics": "👤 Diagnosen",
        "feedbacks": "💬 Feedbacks",
        "evolution": "📈 Entwicklung",
        "executive_reading": "🧠 Executive-Auswertung",
        "agent_evaluation": "🧪 Agentenbewertung",
        "rag_observability": "📊 RAG-Beobachtbarkeit",
        "export": "📤 Exportieren",

        "filters": "🔎 Filter",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "filter_user": "Nach Benutzer filtern",
        "filter_risk": "Nach Risiko filtern",
        "filter_feedback": "Nach Feedback filtern",
        "filter_data_language": "Nach Datensprache filtern",
        "filter_currency": "Nach Währung filtern",

        "all": "Alle",
        "low": "Niedrig",
        "medium": "Mittel",
        "high": "Hoch",
        "useful": "Nützlich",
        "not_useful": "Nicht nützlich",
        "neutral": "Neutral",

        "update_data": "🔄 Daten aktualisieren",
        "main_indicators": "📌 Hauptindikatoren",
        "filtered_user_summary": "👤 Zusammenfassung des gefilterten Benutzers",
        "user": "Benutzer",
        "language": "Sprache",
        "currency": "Währung",
        "last_channel": "Letzter Kanal",
        "financial_score": "Finanzieller Score",
        "risk": "Risiko",
        "estimated_balance": "Geschätzter Saldo",
        "average_score": "Durchschnittlicher Score",
        "average_balance": "Durchschnittlicher Saldo",
        "useful_feedback": "Nützliches Feedback",
    },
}


RISK_INTERNAL_MAP = {
    "BR Português Brasil": {
        "Todos": None,
        "Baixo": "baixo",
        "Médio": "medio",
        "Alto": "alto",
    },
    "EN English": {
        "All": None,
        "Low": "baixo",
        "Medium": "medio",
        "High": "alto",
    },
    "ES Español": {
        "Todos": None,
        "Bajo": "baixo",
        "Medio": "medio",
        "Alto": "alto",
    },
    "DE Deutsch": {
        "Alle": None,
        "Niedrig": "baixo",
        "Mittel": "medio",
        "Hoch": "alto",
    },
}


FEEDBACK_INTERNAL_MAP = {
    "BR Português Brasil": {
        "Todos": None,
        "Útil": "useful",
        "Não útil": "not_useful",
        "Neutro": "neutral",
    },
    "EN English": {
        "All": None,
        "Useful": "useful",
        "Not useful": "not_useful",
        "Neutral": "neutral",
    },
    "ES Español": {
        "Todos": None,
        "Útil": "useful",
        "No útil": "not_useful",
        "Neutral": "neutral",
    },
    "DE Deutsch": {
        "Alle": None,
        "Nützlich": "useful",
        "Nicht nützlich": "not_useful",
        "Neutral": "neutral",
    },
}


def get_texts(language: str) -> Dict[str, str]:
    return TRANSLATIONS.get(language, TRANSLATIONS["BR Português Brasil"])


def get_t(language: str) -> Callable[[str], str]:
    texts = get_texts(language)

    def t(key: str) -> str:
        return texts.get(key, key)

    return t

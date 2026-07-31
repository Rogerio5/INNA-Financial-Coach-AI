"""
Página de Analytics Avançado das Tools da INNA.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from dashboard_i18n import (
        normalize_language,
        page_translate,
        translate_intention,
        translate_origin,
        translate_tool_name,
    )
except ImportError:
    from src.dashboard_i18n import (
        normalize_language,
        page_translate,
        translate_intention,
        translate_origin,
        translate_tool_name,
    )

TOOLS_ANALYTICS_BG = "#020617"
TOOLS_ANALYTICS_TEXT = "#F8FAFC"
TOOLS_ANALYTICS_GRID = (
    "rgba(148, 163, 184, 0.16)"
)


def aplicar_tema_tools_analytics_chart(
    fig,
    *,
    height=410,
):
    """Aplica o tema visual do Analytics Tools."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=TOOLS_ANALYTICS_BG,
        plot_bgcolor=TOOLS_ANALYTICS_BG,
        font={
            "color": TOOLS_ANALYTICS_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": TOOLS_ANALYTICS_TEXT,
        },
        margin={
            "l": 30,
            "r": 42,
            "t": 18,
            "b": 35,
        },
        height=height,
    )

    fig.update_xaxes(
        color=TOOLS_ANALYTICS_TEXT,
        gridcolor=TOOLS_ANALYTICS_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    fig.update_yaxes(
        color=TOOLS_ANALYTICS_TEXT,
        gridcolor=TOOLS_ANALYTICS_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    return fig


TOOLS_ANALYTICS_TEXTS = {
    "pt": {
        "title": "📊 Análise de Ferramentas (Tools)",
        "caption": (
            "Análise operacional de uso, confiança, desempenho, "
            "falhas e comportamento das ferramentas financeiras da INNA."
        ),
        "loaded_events": "Eventos carregados",
        "comparison_window": "Janela de comparação",
        "hours": "horas",
        "seven_days": "7 dias",
        "refresh": "🔄 Atualizar análise",
        "load_error": "Não foi possível carregar os eventos.",
        "insufficient_events": (
            "Ainda não existem eventos suficientes para análise."
        ),
        "operational_insights": "## 🧠 Insights operacionais da INNA",
        "health_score": "Pontuação de saúde",
        "no_summary": "Nenhum resumo disponível.",
        "highlights": "### ✅ Destaques",
        "alerts": "### ⚠️ Alertas",
        "no_critical_alert": "Nenhum alerta crítico detectado.",
        "technical_recommendations": "🛠️ Recomendações técnicas",
        "full_narrative": "📄 Ver narrativa completa",
    },
    "en_us": {
        "title": "📊 Tools Analytics",
        "caption": (
            "Operational analysis of usage, confidence, performance, "
            "failures and behaviour of INNA financial tools."
        ),
        "loaded_events": "Loaded events",
        "comparison_window": "Comparison window",
        "hours": "hours",
        "seven_days": "7 days",
        "refresh": "🔄 Refresh analytics",
        "load_error": "The events could not be loaded.",
        "insufficient_events": (
            "There are not enough events for analysis yet."
        ),
        "operational_insights": "## 🧠 INNA operational insights",
        "health_score": "Health score",
        "no_summary": "No summary is available.",
        "highlights": "### ✅ Highlights",
        "alerts": "### ⚠️ Alerts",
        "no_critical_alert": "No critical alert was detected.",
        "technical_recommendations": "🛠️ Technical recommendations",
        "full_narrative": "📄 View full narrative",
    },
    "es": {
        "title": "📊 Análisis de Herramientas (Tools)",
        "caption": (
            "Análisis operativo del uso, confianza, rendimiento, "
            "fallos y comportamiento de las herramientas financieras de INNA."
        ),
        "loaded_events": "Eventos cargados",
        "comparison_window": "Ventana de comparación",
        "hours": "horas",
        "seven_days": "7 días",
        "refresh": "🔄 Actualizar análisis",
        "load_error": "No fue posible cargar los eventos.",
        "insufficient_events": (
            "Todavía no hay suficientes eventos para el análisis."
        ),
        "operational_insights": "## 🧠 Insights operativos de INNA",
        "health_score": "Puntuación de salud",
        "no_summary": "No hay ningún resumen disponible.",
        "highlights": "### ✅ Aspectos destacados",
        "alerts": "### ⚠️ Alertas",
        "no_critical_alert": "No se detectó ninguna alerta crítica.",
        "technical_recommendations": "🛠️ Recomendaciones técnicas",
        "full_narrative": "📄 Ver narrativa completa",
    },
    "fr": {
        "title": "📊 Analyse des Outils (Tools)",
        "caption": (
            "Analyse opérationnelle de l’utilisation, de la confiance, "
            "des performances et des défaillances des outils financiers INNA."
        ),
        "loaded_events": "Événements chargés",
        "comparison_window": "Fenêtre de comparaison",
        "hours": "heures",
        "seven_days": "7 jours",
        "refresh": "🔄 Actualiser l’analyse",
        "load_error": "Impossible de charger les événements.",
        "insufficient_events": (
            "Il n’y a pas encore assez d’événements pour l’analyse."
        ),
        "operational_insights": "## 🧠 Insights opérationnels INNA",
        "health_score": "Score de santé",
        "no_summary": "Aucun résumé disponible.",
        "highlights": "### ✅ Points forts",
        "alerts": "### ⚠️ Alertes",
        "no_critical_alert": "Aucune alerte critique détectée.",
        "technical_recommendations": "🛠️ Recommandations techniques",
        "full_narrative": "📄 Voir le récit complet",
    },
    "de": {
        "title": "📊 Werkzeuganalyse (Tools)",
        "caption": (
            "Betriebsanalyse von Nutzung, Vertrauen, Leistung "
            "und Fehlern der INNA-Finanzwerkzeuge."
        ),
        "loaded_events": "Geladene Ereignisse",
        "comparison_window": "Vergleichszeitraum",
        "hours": "Stunden",
        "seven_days": "7 Tage",
        "refresh": "🔄 Analyse aktualisieren",
        "load_error": "Die Ereignisse konnten nicht geladen werden.",
        "insufficient_events": (
            "Für die Analyse sind noch nicht genügend Ereignisse vorhanden."
        ),
        "operational_insights": "## 🧠 Operative INNA-Erkenntnisse",
        "health_score": "Gesundheitswert",
        "no_summary": "Keine Zusammenfassung verfügbar.",
        "highlights": "### ✅ Stärken",
        "alerts": "### ⚠️ Warnungen",
        "no_critical_alert": "Keine kritische Warnung erkannt.",
        "technical_recommendations": "🛠️ Technische Empfehlungen",
        "full_narrative": "📄 Vollständige Analyse anzeigen",
    },
    "it": {
        "title": "📊 Analisi degli Strumenti (Tools)",
        "caption": (
            "Analisi operativa di utilizzo, affidabilità, prestazioni "
            "e guasti degli strumenti finanziari INNA."
        ),
        "loaded_events": "Eventi caricati",
        "comparison_window": "Finestra di confronto",
        "hours": "ore",
        "seven_days": "7 giorni",
        "refresh": "🔄 Aggiorna analisi",
        "load_error": "Impossibile caricare gli eventi.",
        "insufficient_events": (
            "Non sono ancora disponibili eventi sufficienti per l’analisi."
        ),
        "operational_insights": "## 🧠 Insight operativi INNA",
        "health_score": "Punteggio di salute",
        "no_summary": "Nessun riepilogo disponibile.",
        "highlights": "### ✅ Punti di forza",
        "alerts": "### ⚠️ Avvisi",
        "no_critical_alert": "Nessun avviso critico rilevato.",
        "technical_recommendations": "🛠️ Raccomandazioni tecniche",
        "full_narrative": "📄 Visualizza analisi completa",
    },
}

TOOLS_ANALYTICS_TEXTS["en_gb"] = TOOLS_ANALYTICS_TEXTS["en_us"]

for idioma in (
    "ro",
    "ua",
    "ru",
    "sa",
):
    TOOLS_ANALYTICS_TEXTS[idioma] = (
        TOOLS_ANALYTICS_TEXTS["en_us"]
    )


TOOLS_ANALYTICS_PERIOD_TEXTS = {'pt': {'period_comparison': '## Comparação entre períodos', 'executions': 'Execuções', 'failures': 'Falhas', 'average_duration': 'Duração média', 'detailed_comparison': 'Ver comparação detalhada', 'period': 'Período', 'current': 'Atual', 'previous': 'Anterior', 'average_duration_ms': 'Duração média (ms)'}, 'en_us': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'en_gb': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'es': {'period_comparison': '## Comparación entre períodos', 'executions': 'Ejecuciones', 'failures': 'Fallos', 'average_duration': 'Duración media', 'detailed_comparison': 'Ver comparación detallada', 'period': 'Período', 'current': 'Actual', 'previous': 'Anterior', 'average_duration_ms': 'Duración media (ms)'}, 'fr': {'period_comparison': '## Comparaison entre les périodes', 'executions': 'Exécutions', 'failures': 'Échecs', 'average_duration': 'Durée moyenne', 'detailed_comparison': 'Voir la comparaison détaillée', 'period': 'Période', 'current': 'Actuelle', 'previous': 'Précédente', 'average_duration_ms': 'Durée moyenne (ms)'}, 'de': {'period_comparison': '## Periodenvergleich', 'executions': 'Ausführungen', 'failures': 'Fehler', 'average_duration': 'Durchschnittliche Dauer', 'detailed_comparison': 'Detaillierten Vergleich anzeigen', 'period': 'Zeitraum', 'current': 'Aktuell', 'previous': 'Vorherig', 'average_duration_ms': 'Durchschnittliche Dauer (ms)'}, 'it': {'period_comparison': '## Confronto tra periodi', 'executions': 'Esecuzioni', 'failures': 'Errori', 'average_duration': 'Durata media', 'detailed_comparison': 'Visualizza confronto dettagliato', 'period': 'Periodo', 'current': 'Attuale', 'previous': 'Precedente', 'average_duration_ms': 'Durata media (ms)'}, 'ro': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'ua': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'ru': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'sa': {'period_comparison': '## Period comparison', 'executions': 'Executions', 'failures': 'Failures', 'average_duration': 'Average duration', 'detailed_comparison': 'View detailed comparison', 'period': 'Period', 'current': 'Current', 'previous': 'Previous', 'average_duration_ms': 'Average duration (ms)'}, 'ch': {'period_comparison': '## Periodenvergleich', 'executions': 'Ausführungen', 'failures': 'Fehler', 'average_duration': 'Durchschnittliche Dauer', 'detailed_comparison': 'Detaillierten Vergleich anzeigen', 'period': 'Zeitraum', 'current': 'Aktuell', 'previous': 'Vorherig', 'average_duration_ms': 'Durchschnittliche Dauer (ms)'}}

for idioma, textos in TOOLS_ANALYTICS_PERIOD_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)


TOOLS_ANALYTICS_ANOMALY_TEXTS = {'pt': {'anomaly_detection': '## 🚨 Detecção de anomalias', 'insufficient_anomaly_data': 'Ainda não existem dados suficientes para detectar anomalias operacionais.', 'none': 'Nenhuma', 'detected_anomalies': 'Anomalias detectadas', 'highest_severity': 'Maior severidade', 'current_period_failures': 'Falhas no período atual', 'current_p95': 'P95 atual', 'current_failure_rate': 'Taxa de falhas atual', 'baseline_failure_rate': 'Taxa de falhas base', 'current_confidence': 'Confiança atual', 'baseline_confidence': 'Confiança base', 'no_relevant_anomalies': 'Nenhuma anomalia operacional relevante foi detectada para as janelas analisadas.', 'anomalies_by_severity': '### Anomalias por severidade', 'critical': 'Críticas', 'high': 'Altas', 'medium': 'Médias', 'low': 'Baixas', 'informational': 'Informativas', 'detected_alerts': '### Alertas detectados', 'anomaly': 'Anomalia', 'severity': 'Severidade', 'metric': 'Métrica', 'recommendation': 'Recomendação', 'outlier_executions': '### Execuções fora do padrão', 'event_index': 'Índice do evento', 'duration_ms': 'Duração (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'Como a detecção funciona', 'detection_explanation': '\nA INNA compara o período atual com uma linha de base anterior.\n\nSão analisados:\n\n- taxa de falhas;\n- confiança média do Router;\n- latência P95;\n- quantidade de execuções;\n- execuções individuais fora do padrão.\n\nOs outliers de duração usam **mediana e MAD**, uma abordagem\nmais resistente a valores extremos do que média e desvio-padrão.\n'}, 'en_us': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'es': {'anomaly_detection': '## 🚨 Detección de anomalías', 'insufficient_anomaly_data': 'Todavía no hay datos suficientes para detectar anomalías operativas.', 'none': 'Ninguna', 'detected_anomalies': 'Anomalías detectadas', 'highest_severity': 'Mayor severidad', 'current_period_failures': 'Fallos del período actual', 'current_p95': 'P95 actual', 'current_failure_rate': 'Tasa de fallos actual', 'baseline_failure_rate': 'Tasa de fallos base', 'current_confidence': 'Confianza actual', 'baseline_confidence': 'Confianza base', 'no_relevant_anomalies': 'No se detectaron anomalías operativas relevantes en las ventanas analizadas.', 'anomalies_by_severity': '### Anomalías por severidad', 'critical': 'Críticas', 'high': 'Altas', 'medium': 'Medias', 'low': 'Bajas', 'informational': 'Informativas', 'detected_alerts': '### Alertas detectadas', 'anomaly': 'Anomalía', 'severity': 'Severidad', 'metric': 'Métrica', 'recommendation': 'Recomendación', 'outlier_executions': '### Ejecuciones fuera del patrón', 'event_index': 'Índice del evento', 'duration_ms': 'Duración (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'Cómo funciona la detección', 'detection_explanation': '\nINNA compara el período actual con una línea base anterior.\n\nSe analizan:\n\n- tasa de fallos;\n- confianza media del Router;\n- latencia P95;\n- cantidad de ejecuciones;\n- ejecuciones individuales fuera del patrón.\n\nLos outliers de duración utilizan **mediana y MAD**, un método\nmás resistente a valores extremos que la media y la desviación estándar.\n'}, 'fr': {'anomaly_detection': '## 🚨 Détection des anomalies', 'insufficient_anomaly_data': 'Il n’y a pas encore assez de données pour détecter les anomalies opérationnelles.', 'none': 'Aucune', 'detected_anomalies': 'Anomalies détectées', 'highest_severity': 'Sévérité maximale', 'current_period_failures': 'Échecs de la période actuelle', 'current_p95': 'P95 actuel', 'current_failure_rate': 'Taux d’échec actuel', 'baseline_failure_rate': 'Taux d’échec de référence', 'current_confidence': 'Confiance actuelle', 'baseline_confidence': 'Confiance de référence', 'no_relevant_anomalies': 'Aucune anomalie opérationnelle pertinente n’a été détectée pour les fenêtres analysées.', 'anomalies_by_severity': '### Anomalies par sévérité', 'critical': 'Critiques', 'high': 'Élevées', 'medium': 'Moyennes', 'low': 'Faibles', 'informational': 'Informatives', 'detected_alerts': '### Alertes détectées', 'anomaly': 'Anomalie', 'severity': 'Sévérité', 'metric': 'Métrique', 'recommendation': 'Recommandation', 'outlier_executions': '### Exécutions hors norme', 'event_index': 'Indice de l’événement', 'duration_ms': 'Durée (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'Fonctionnement de la détection', 'detection_explanation': '\nINNA compare la période actuelle à une référence antérieure.\n\nLes éléments analysés sont :\n\n- le taux d’échec ;\n- la confiance moyenne du Router ;\n- la latence P95 ;\n- le volume d’exécutions ;\n- les exécutions individuelles hors norme.\n\nLes valeurs aberrantes de durée utilisent **la médiane et le MAD**,\nplus résistants aux valeurs extrêmes que la moyenne et l’écart type.\n'}, 'de': {'anomaly_detection': '## 🚨 Anomalieerkennung', 'insufficient_anomaly_data': 'Es sind noch nicht genügend Daten zur Erkennung betrieblicher Anomalien vorhanden.', 'none': 'Keine', 'detected_anomalies': 'Erkannte Anomalien', 'highest_severity': 'Höchster Schweregrad', 'current_period_failures': 'Fehler im aktuellen Zeitraum', 'current_p95': 'Aktueller P95', 'current_failure_rate': 'Aktuelle Fehlerrate', 'baseline_failure_rate': 'Basis-Fehlerrate', 'current_confidence': 'Aktuelles Vertrauen', 'baseline_confidence': 'Basis-Vertrauen', 'no_relevant_anomalies': 'Für die analysierten Zeitfenster wurden keine relevanten betrieblichen Anomalien erkannt.', 'anomalies_by_severity': '### Anomalien nach Schweregrad', 'critical': 'Kritisch', 'high': 'Hoch', 'medium': 'Mittel', 'low': 'Niedrig', 'informational': 'Informativ', 'detected_alerts': '### Erkannte Warnungen', 'anomaly': 'Anomalie', 'severity': 'Schweregrad', 'metric': 'Metrik', 'recommendation': 'Empfehlung', 'outlier_executions': '### Ausreißer-Ausführungen', 'event_index': 'Ereignisindex', 'duration_ms': 'Dauer (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'Funktionsweise der Erkennung', 'detection_explanation': '\nINNA vergleicht den aktuellen Zeitraum mit einer früheren Basislinie.\n\nAnalysiert werden:\n\n- Fehlerrate;\n- durchschnittliches Router-Vertrauen;\n- P95-Latenz;\n- Ausführungsvolumen;\n- einzelne Ausreißer-Ausführungen.\n\nDauerausreißer verwenden **Median und MAD**, was gegenüber\nExtremwerten robuster ist als Mittelwert und Standardabweichung.\n'}, 'en_gb': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'it': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ro': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ua': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ru': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'sa': {'anomaly_detection': '## 🚨 Anomaly detection', 'insufficient_anomaly_data': 'There is not enough data yet to detect operational anomalies.', 'none': 'None', 'detected_anomalies': 'Detected anomalies', 'highest_severity': 'Highest severity', 'current_period_failures': 'Current-period failures', 'current_p95': 'Current P95', 'current_failure_rate': 'Current failure rate', 'baseline_failure_rate': 'Baseline failure rate', 'current_confidence': 'Current confidence', 'baseline_confidence': 'Baseline confidence', 'no_relevant_anomalies': 'No relevant operational anomaly was detected for the analysed windows.', 'anomalies_by_severity': '### Anomalies by severity', 'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'informational': 'Informational', 'detected_alerts': '### Detected alerts', 'anomaly': 'Anomaly', 'severity': 'Severity', 'metric': 'Metric', 'recommendation': 'Recommendation', 'outlier_executions': '### Outlier executions', 'event_index': 'Event index', 'duration_ms': 'Duration (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'How detection works', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- P95 latency;\n- execution volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ch': {'anomaly_detection': '## 🚨 Anomalieerkennung', 'insufficient_anomaly_data': 'Es sind noch nicht genügend Daten zur Erkennung betrieblicher Anomalien vorhanden.', 'none': 'Keine', 'detected_anomalies': 'Erkannte Anomalien', 'highest_severity': 'Höchster Schweregrad', 'current_period_failures': 'Fehler im aktuellen Zeitraum', 'current_p95': 'Aktueller P95', 'current_failure_rate': 'Aktuelle Fehlerrate', 'baseline_failure_rate': 'Basis-Fehlerrate', 'current_confidence': 'Aktuelles Vertrauen', 'baseline_confidence': 'Basis-Vertrauen', 'no_relevant_anomalies': 'Für die analysierten Zeitfenster wurden keine relevanten betrieblichen Anomalien erkannt.', 'anomalies_by_severity': '### Anomalien nach Schweregrad', 'critical': 'Kritisch', 'high': 'Hoch', 'medium': 'Mittel', 'low': 'Niedrig', 'informational': 'Informativ', 'detected_alerts': '### Erkannte Warnungen', 'anomaly': 'Anomalie', 'severity': 'Schweregrad', 'metric': 'Metrik', 'recommendation': 'Empfehlung', 'outlier_executions': '### Ausreißer-Ausführungen', 'event_index': 'Ereignisindex', 'duration_ms': 'Dauer (ms)', 'modified_z_score': 'Modified Z-Score', 'how_detection_works': 'Funktionsweise der Erkennung', 'detection_explanation': '\nINNA vergleicht den aktuellen Zeitraum mit einer früheren Basislinie.\n\nAnalysiert werden:\n\n- Fehlerrate;\n- durchschnittliches Router-Vertrauen;\n- P95-Latenz;\n- Ausführungsvolumen;\n- einzelne Ausreißer-Ausführungen.\n\nDauerausreißer verwenden **Median und MAD**, was gegenüber\nExtremwerten robuster ist als Mittelwert und Standardabweichung.\n'}}

for idioma, textos in TOOLS_ANALYTICS_ANOMALY_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)


TOOLS_ANALYTICS_RANKING_TEXTS = {'pt': {'tool': 'Ferramenta', 'successes': 'Sucessos', 'success_rate': 'Taxa de sucesso (%)', 'average_confidence': 'Confiança média (%)', 'average_ms': 'Média (ms)', 'minimum_ms': 'Mínimo (ms)', 'maximum_ms': 'Máximo (ms)', 'ranking_performance': '## Ranking e desempenho das ferramentas', 'no_tool_found': 'Nenhuma ferramenta encontrada.', 'usage_by_tool': '### Uso por ferramenta', 'executions_hover': 'Execuções', 'p95_by_tool': '### P95 por ferramenta', 'p95_latency': 'Latência P95 (ms)'}, 'en_us': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'en_gb': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'es': {'tool': 'Herramienta', 'successes': 'Éxitos', 'success_rate': 'Tasa de éxito (%)', 'average_confidence': 'Confianza media (%)', 'average_ms': 'Media (ms)', 'minimum_ms': 'Mínimo (ms)', 'maximum_ms': 'Máximo (ms)', 'ranking_performance': '## Ranking y rendimiento de las herramientas', 'no_tool_found': 'No se encontró ninguna herramienta.', 'usage_by_tool': '### Uso por herramienta', 'executions_hover': 'Ejecuciones', 'p95_by_tool': '### P95 por herramienta', 'p95_latency': 'Latencia P95 (ms)'}, 'fr': {'tool': 'Outil', 'successes': 'Succès', 'success_rate': 'Taux de réussite (%)', 'average_confidence': 'Confiance moyenne (%)', 'average_ms': 'Moyenne (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Classement et performance des outils', 'no_tool_found': 'Aucun outil trouvé.', 'usage_by_tool': '### Utilisation par outil', 'executions_hover': 'Exécutions', 'p95_by_tool': '### P95 par outil', 'p95_latency': 'Latence P95 (ms)'}, 'de': {'tool': 'Werkzeug', 'successes': 'Erfolge', 'success_rate': 'Erfolgsquote (%)', 'average_confidence': 'Durchschnittliches Vertrauen (%)', 'average_ms': 'Durchschnitt (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Werkzeugrangliste und Leistung', 'no_tool_found': 'Kein Werkzeug gefunden.', 'usage_by_tool': '### Nutzung nach Werkzeug', 'executions_hover': 'Ausführungen', 'p95_by_tool': '### P95 nach Werkzeug', 'p95_latency': 'P95-Latenz (ms)'}, 'it': {'tool': 'Strumento', 'successes': 'Successi', 'success_rate': 'Tasso di successo (%)', 'average_confidence': 'Affidabilità media (%)', 'average_ms': 'Media (ms)', 'minimum_ms': 'Minimo (ms)', 'maximum_ms': 'Massimo (ms)', 'ranking_performance': '## Classifica e prestazioni degli strumenti', 'no_tool_found': 'Nessuno strumento trovato.', 'usage_by_tool': '### Utilizzo per strumento', 'executions_hover': 'Esecuzioni', 'p95_by_tool': '### P95 per strumento', 'p95_latency': 'Latenza P95 (ms)'}, 'ro': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'ua': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'ru': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'sa': {'tool': 'Tool', 'successes': 'Successes', 'success_rate': 'Success rate (%)', 'average_confidence': 'Average confidence (%)', 'average_ms': 'Average (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Tool ranking and performance', 'no_tool_found': 'No tool was found.', 'usage_by_tool': '### Usage by tool', 'executions_hover': 'Executions', 'p95_by_tool': '### P95 by tool', 'p95_latency': 'P95 latency (ms)'}, 'ch': {'tool': 'Werkzeug', 'successes': 'Erfolge', 'success_rate': 'Erfolgsquote (%)', 'average_confidence': 'Durchschnittliches Vertrauen (%)', 'average_ms': 'Durchschnitt (ms)', 'minimum_ms': 'Minimum (ms)', 'maximum_ms': 'Maximum (ms)', 'ranking_performance': '## Werkzeugrangliste und Leistung', 'no_tool_found': 'Kein Werkzeug gefunden.', 'usage_by_tool': '### Nutzung nach Werkzeug', 'executions_hover': 'Ausführungen', 'p95_by_tool': '### P95 nach Werkzeug', 'p95_latency': 'P95-Latenz (ms)'}}

for idioma, textos in TOOLS_ANALYTICS_RANKING_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)


TOOLS_ANALYTICS_DISTRIBUTION_TEXTS = {'pt': {'distributions': '## Distribuições', 'intentions': '### Intenções', 'origins': '### Origens', 'intention': 'Intenção', 'origin': 'Origem', 'total': 'Total', 'events': 'Eventos'}, 'en_us': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'en_gb': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'es': {'distributions': '## Distribuciones', 'intentions': '### Intenciones', 'origins': '### Orígenes', 'intention': 'Intención', 'origin': 'Origen', 'total': 'Total', 'events': 'Eventos'}, 'fr': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origines', 'intention': 'Intention', 'origin': 'Origine', 'total': 'Total', 'events': 'Événements'}, 'de': {'distributions': '## Verteilungen', 'intentions': '### Absichten', 'origins': '### Ursprünge', 'intention': 'Absicht', 'origin': 'Ursprung', 'total': 'Gesamt', 'events': 'Ereignisse'}, 'it': {'distributions': '## Distribuzioni', 'intentions': '### Intenzioni', 'origins': '### Origini', 'intention': 'Intenzione', 'origin': 'Origine', 'total': 'Totale', 'events': 'Eventi'}, 'ro': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'ua': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'ru': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'sa': {'distributions': '## Distributions', 'intentions': '### Intentions', 'origins': '### Origins', 'intention': 'Intention', 'origin': 'Origin', 'total': 'Total', 'events': 'Events'}, 'ch': {'distributions': '## Verteilungen', 'intentions': '### Absichten', 'origins': '### Ursprünge', 'intention': 'Absicht', 'origin': 'Ursprung', 'total': 'Gesamt', 'events': 'Ereignisse'}}

for idioma, textos in TOOLS_ANALYTICS_DISTRIBUTION_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)


TOOLS_ANALYTICS_TEMPORAL_TEXTS = {'pt': {'temporal_evolution': '## Evolução temporal', 'grouping': 'Agrupamento', 'hour': 'Hora', 'day': 'Dia', 'week': 'Semana', 'month': 'Mês', 'insufficient_time_series': 'Não há eventos suficientes para a série temporal.', 'period_label': 'Período', 'successful_executions': 'Sucessos', 'failed_executions': 'Falhas', 'most_active_users': '## Usuários mais ativos', 'user': 'Usuário', 'no_user': 'sem usuário'}, 'en_us': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'en_gb': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'es': {'temporal_evolution': '## Evolución temporal', 'grouping': 'Agrupación', 'hour': 'Hora', 'day': 'Día', 'week': 'Semana', 'month': 'Mes', 'insufficient_time_series': 'No hay eventos suficientes para la serie temporal.', 'period_label': 'Período', 'successful_executions': 'Éxitos', 'failed_executions': 'Fallos', 'most_active_users': '## Usuarios más activos', 'user': 'Usuario', 'no_user': 'sin usuario'}, 'fr': {'temporal_evolution': '## Évolution temporelle', 'grouping': 'Regroupement', 'hour': 'Heure', 'day': 'Jour', 'week': 'Semaine', 'month': 'Mois', 'insufficient_time_series': 'Il n’y a pas assez d’événements pour la série temporelle.', 'period_label': 'Période', 'successful_executions': 'Succès', 'failed_executions': 'Échecs', 'most_active_users': '## Utilisateurs les plus actifs', 'user': 'Utilisateur', 'no_user': 'sans utilisateur'}, 'de': {'temporal_evolution': '## Zeitliche Entwicklung', 'grouping': 'Gruppierung', 'hour': 'Stunde', 'day': 'Tag', 'week': 'Woche', 'month': 'Monat', 'insufficient_time_series': 'Für die Zeitreihe sind nicht genügend Ereignisse vorhanden.', 'period_label': 'Zeitraum', 'successful_executions': 'Erfolge', 'failed_executions': 'Fehler', 'most_active_users': '## Aktivste Benutzer', 'user': 'Benutzer', 'no_user': 'kein Benutzer'}, 'it': {'temporal_evolution': '## Evoluzione temporale', 'grouping': 'Raggruppamento', 'hour': 'Ora', 'day': 'Giorno', 'week': 'Settimana', 'month': 'Mese', 'insufficient_time_series': 'Non ci sono eventi sufficienti per la serie temporale.', 'period_label': 'Periodo', 'successful_executions': 'Successi', 'failed_executions': 'Errori', 'most_active_users': '## Utenti più attivi', 'user': 'Utente', 'no_user': 'senza utente'}, 'ro': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'ua': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'ru': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'sa': {'temporal_evolution': '## Temporal evolution', 'grouping': 'Grouping', 'hour': 'Hour', 'day': 'Day', 'week': 'Week', 'month': 'Month', 'insufficient_time_series': 'There are not enough events for the time series.', 'period_label': 'Period', 'successful_executions': 'Successes', 'failed_executions': 'Failures', 'most_active_users': '## Most active users', 'user': 'User', 'no_user': 'no user'}, 'ch': {'temporal_evolution': '## Zeitliche Entwicklung', 'grouping': 'Gruppierung', 'hour': 'Stunde', 'day': 'Tag', 'week': 'Woche', 'month': 'Monat', 'insufficient_time_series': 'Für die Zeitreihe sind nicht genügend Ereignisse vorhanden.', 'period_label': 'Zeitraum', 'successful_executions': 'Erfolge', 'failed_executions': 'Fehler', 'most_active_users': '## Aktivste Benutzer', 'user': 'Benutzer', 'no_user': 'kein Benutzer'}}

for idioma, textos in TOOLS_ANALYTICS_TEMPORAL_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)


TOOLS_ANALYTICS_OVERVIEW_TEXTS = {'pt': {'analytic_overview': '## Visão analítica', 'analysed_events': 'Eventos analisados', 'success_rate_metric': 'Taxa de sucesso', 'executions_without_tool': 'Execuções sem ferramenta', 'average_confidence_metric': 'Confiança média', 'average_duration_metric': 'Duração média', 'distinct_tools': 'Ferramentas distintas', 'unique_users': 'Usuários únicos', 'detection_explanation': '\nA INNA compara o período atual com uma linha de base anterior.\n\nSão analisados:\n\n- taxa de falhas;\n- confiança média do Router;\n- P95 da duração;\n- percentual de eventos sem ferramenta;\n- volume médio por hora;\n- execuções individuais fora do padrão.\n\nOs outliers de duração usam **mediana e MAD**, uma abordagem\nmais resistente a valores extremos do que média e desvio-padrão.\n'}, 'en_us': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'en_gb': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'es': {'analytic_overview': '## Visión analítica', 'analysed_events': 'Eventos analizados', 'success_rate_metric': 'Tasa de éxito', 'executions_without_tool': 'Ejecuciones sin herramienta', 'average_confidence_metric': 'Confianza media', 'average_duration_metric': 'Duración media', 'distinct_tools': 'Herramientas distintas', 'unique_users': 'Usuarios únicos', 'detection_explanation': '\nINNA compara el período actual con una línea base anterior.\n\nSe analizan:\n\n- tasa de fallos;\n- confianza media del Router;\n- P95 de la duración;\n- porcentaje de eventos sin herramienta;\n- volumen medio por hora;\n- ejecuciones individuales fuera del patrón.\n\nLos outliers de duración utilizan **mediana y MAD**, un método\nmás resistente a valores extremos que la media y la desviación estándar.\n'}, 'fr': {'analytic_overview': '## Vue analytique', 'analysed_events': 'Événements analysés', 'success_rate_metric': 'Taux de réussite', 'executions_without_tool': 'Exécutions sans outil', 'average_confidence_metric': 'Confiance moyenne', 'average_duration_metric': 'Durée moyenne', 'distinct_tools': 'Outils distincts', 'unique_users': 'Utilisateurs uniques', 'detection_explanation': '\nINNA compare la période actuelle à une référence antérieure.\n\nLes éléments analysés sont :\n\n- le taux d’échec ;\n- la confiance moyenne du Router ;\n- le P95 de la durée ;\n- le pourcentage d’événements sans outil ;\n- le volume horaire moyen ;\n- les exécutions individuelles hors norme.\n\nLes valeurs aberrantes de durée utilisent **la médiane et le MAD**,\nplus résistants aux valeurs extrêmes que la moyenne et l’écart type.\n'}, 'de': {'analytic_overview': '## Analytische Übersicht', 'analysed_events': 'Analysierte Ereignisse', 'success_rate_metric': 'Erfolgsquote', 'executions_without_tool': 'Ausführungen ohne Werkzeug', 'average_confidence_metric': 'Durchschnittliches Vertrauen', 'average_duration_metric': 'Durchschnittliche Dauer', 'distinct_tools': 'Unterschiedliche Werkzeuge', 'unique_users': 'Eindeutige Benutzer', 'detection_explanation': '\nINNA vergleicht den aktuellen Zeitraum mit einer früheren Basislinie.\n\nAnalysiert werden:\n\n- Fehlerrate;\n- durchschnittliches Router-Vertrauen;\n- P95 der Dauer;\n- Anteil der Ereignisse ohne Werkzeug;\n- durchschnittliches Volumen pro Stunde;\n- einzelne Ausreißer-Ausführungen.\n\nDauerausreißer verwenden **Median und MAD**, was gegenüber\nExtremwerten robuster ist als Mittelwert und Standardabweichung.\n'}, 'it': {'analytic_overview': '## Panoramica analitica', 'analysed_events': 'Eventi analizzati', 'success_rate_metric': 'Tasso di successo', 'executions_without_tool': 'Esecuzioni senza strumento', 'average_confidence_metric': 'Affidabilità media', 'average_duration_metric': 'Durata media', 'distinct_tools': 'Strumenti distinti', 'unique_users': 'Utenti unici', 'detection_explanation': '\nINNA confronta il periodo attuale con una base precedente.\n\nVengono analizzati:\n\n- tasso di errore;\n- affidabilità media del Router;\n- P95 della durata;\n- percentuale di eventi senza strumento;\n- volume medio orario;\n- singole esecuzioni fuori norma.\n\nGli outlier di durata utilizzano **mediana e MAD**, un metodo\npiù resistente ai valori estremi rispetto a media e deviazione standard.\n'}, 'ro': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ua': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ru': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'sa': {'analytic_overview': '## Analytics overview', 'analysed_events': 'Analysed events', 'success_rate_metric': 'Success rate', 'executions_without_tool': 'Executions without a tool', 'average_confidence_metric': 'Average confidence', 'average_duration_metric': 'Average duration', 'distinct_tools': 'Distinct tools', 'unique_users': 'Unique users', 'detection_explanation': '\nINNA compares the current period with an earlier baseline.\n\nThe following are analysed:\n\n- failure rate;\n- average Router confidence;\n- duration P95;\n- percentage of events without a tool;\n- average hourly volume;\n- individual outlier executions.\n\nDuration outliers use **median and MAD**, an approach that is\nmore resistant to extreme values than mean and standard deviation.\n'}, 'ch': {'analytic_overview': '## Analytische Übersicht', 'analysed_events': 'Analysierte Ereignisse', 'success_rate_metric': 'Erfolgsquote', 'executions_without_tool': 'Ausführungen ohne Werkzeug', 'average_confidence_metric': 'Durchschnittliches Vertrauen', 'average_duration_metric': 'Durchschnittliche Dauer', 'distinct_tools': 'Unterschiedliche Werkzeuge', 'unique_users': 'Eindeutige Benutzer', 'detection_explanation': '\nINNA vergleicht den aktuellen Zeitraum mit einer früheren Basislinie.\n\nAnalysiert werden:\n\n- Fehlerrate;\n- durchschnittliches Router-Vertrauen;\n- P95 der Dauer;\n- Anteil der Ereignisse ohne Werkzeug;\n- durchschnittliches Volumen pro Stunde;\n- einzelne Ausreißer-Ausführungen.\n\nDauerausreißer verwenden **Median und MAD**, was gegenüber\nExtremwerten robuster ist als Mittelwert und Standardabweichung.\n'}}

for idioma, textos in TOOLS_ANALYTICS_OVERVIEW_TEXTS.items():
    TOOLS_ANALYTICS_TEXTS.setdefault(idioma, {}).update(textos)

TOOLS_ANALYTICS_TEXTS["ch"] = TOOLS_ANALYTICS_TEXTS["de"]




# TOOLS_ANALYTICS_ROMANIAN_NATIVE_TRANSLATIONS
TOOLS_ANALYTICS_TEXTS["ro"] = {'title': '📊 Analiza Instrumentelor', 'caption': 'Analiză operațională privind utilizarea, încrederea, performanța, erorile și comportamentul instrumentelor financiare INNA.', 'loaded_events': 'Evenimente încărcate', 'comparison_window': 'Fereastră de comparație', 'hours': 'ore', 'seven_days': '7 zile', 'refresh': '🔄 Actualizați analiza', 'load_error': 'Evenimentele nu au putut fi încărcate.', 'insufficient_events': 'Nu există încă suficiente evenimente pentru analiză.', 'operational_insights': '## 🧠 Perspective operaționale INNA', 'health_score': 'Scor de sănătate', 'no_summary': 'Nu este disponibil niciun rezumat.', 'highlights': '### ✅ Puncte forte', 'alerts': '### ⚠️ Alerte', 'no_critical_alert': 'Nu a fost detectată nicio alertă critică.', 'technical_recommendations': '🛠️ Recomandări tehnice', 'full_narrative': '📄 Vizualizați analiza completă', 'period_comparison': '## Comparație între perioade', 'executions': 'Execuții', 'failures': 'Erori', 'average_duration': 'Durată medie', 'detailed_comparison': 'Vizualizați comparația detaliată', 'period': 'Perioadă', 'current': 'Actuală', 'previous': 'Anterioară', 'average_duration_ms': 'Durată medie (ms)', 'anomaly_detection': '## 🚨 Detectarea anomaliilor', 'insufficient_anomaly_data': 'Nu există încă suficiente date pentru detectarea anomaliilor operaționale.', 'none': 'Niciuna', 'detected_anomalies': 'Anomalii detectate', 'highest_severity': 'Severitate maximă', 'current_period_failures': 'Erori în perioada actuală', 'current_p95': 'P95 actual', 'current_failure_rate': 'Rata actuală de eroare', 'baseline_failure_rate': 'Rata de eroare de referință', 'current_confidence': 'Încredere actuală', 'baseline_confidence': 'Încredere de referință', 'no_relevant_anomalies': 'Nu a fost detectată nicio anomalie operațională relevantă în ferestrele analizate.', 'anomalies_by_severity': '### Anomalii după severitate', 'critical': 'Critice', 'high': 'Ridicate', 'medium': 'Medii', 'low': 'Scăzute', 'informational': 'Informative', 'detected_alerts': '### Alerte detectate', 'anomaly': 'Anomalie', 'severity': 'Severitate', 'metric': 'Metrică', 'recommendation': 'Recomandare', 'outlier_executions': '### Execuții în afara tiparului', 'event_index': 'Indicele evenimentului', 'duration_ms': 'Durată (ms)', 'modified_z_score': 'Scor Z modificat', 'how_detection_works': 'Cum funcționează detectarea', 'detection_explanation': '\nINNA compară perioada actuală cu o linie de bază anterioară.\n\nSunt analizate:\n\n- rata de eroare;\n- încrederea medie a Routerului;\n- P95 al duratei;\n- procentul evenimentelor fără instrument;\n- volumul mediu pe oră;\n- execuțiile individuale în afara tiparului.\n\nValorile atipice ale duratei folosesc **mediana și MAD**, o metodă mai rezistentă la valorile extreme decât media și abaterea standard.\n', 'tool': 'Instrument', 'successes': 'Succese', 'success_rate': 'Rata de succes (%)', 'average_confidence': 'Încredere medie (%)', 'average_ms': 'Medie (ms)', 'minimum_ms': 'Minim (ms)', 'maximum_ms': 'Maxim (ms)', 'ranking_performance': '## Clasamentul și performanța instrumentelor', 'no_tool_found': 'Nu a fost găsit niciun instrument.', 'usage_by_tool': '### Utilizare după instrument', 'executions_hover': 'Execuții', 'p95_by_tool': '### P95 după instrument', 'p95_latency': 'Latență P95 (ms)', 'distributions': '## Distribuții', 'intentions': '### Intenții', 'origins': '### Origini', 'intention': 'Intenție', 'origin': 'Origine', 'total': 'Total', 'events': 'Evenimente', 'temporal_evolution': '## Evoluție temporală', 'grouping': 'Grupare', 'hour': 'Oră', 'day': 'Zi', 'week': 'Săptămână', 'month': 'Lună', 'insufficient_time_series': 'Nu există suficiente evenimente pentru seria temporală.', 'period_label': 'Perioadă', 'successful_executions': 'Execuții reușite', 'failed_executions': 'Execuții eșuate', 'most_active_users': '## Cei mai activi utilizatori', 'user': 'Utilizator', 'no_user': 'fără utilizator', 'analytic_overview': '## Prezentare analitică', 'analysed_events': 'Evenimente analizate', 'success_rate_metric': 'Rata de succes', 'executions_without_tool': 'Execuții fără instrument', 'average_confidence_metric': 'Încredere medie', 'average_duration_metric': 'Durată medie', 'distinct_tools': 'Instrumente distincte', 'unique_users': 'Utilizatori unici'}


# TOOLS_ANALYTICS_UKRAINIAN_NATIVE_TRANSLATIONS
TOOLS_ANALYTICS_TEXTS["ua"] = {'title': '📊 Аналітика Інструментів', 'caption': 'Операційний аналіз використання, довіри, продуктивності, помилок і поведінки фінансових інструментів INNA.', 'loaded_events': 'Завантажені події', 'comparison_window': 'Вікно порівняння', 'hours': 'годин', 'seven_days': '7 днів', 'refresh': '🔄 Оновити аналіз', 'load_error': 'Не вдалося завантажити події.', 'insufficient_events': 'Поки що недостатньо подій для аналізу.', 'operational_insights': '## 🧠 Операційні інсайти INNA', 'health_score': 'Оцінка стану', 'no_summary': 'Підсумок недоступний.', 'highlights': '### ✅ Сильні сторони', 'alerts': '### ⚠️ Попередження', 'no_critical_alert': 'Критичних попереджень не виявлено.', 'technical_recommendations': '🛠️ Технічні рекомендації', 'full_narrative': '📄 Переглянути повний аналіз', 'period_comparison': '## Порівняння періодів', 'executions': 'Виконання', 'failures': 'Помилки', 'average_duration': 'Середня тривалість', 'detailed_comparison': 'Переглянути детальне порівняння', 'period': 'Період', 'current': 'Поточний', 'previous': 'Попередній', 'average_duration_ms': 'Середня тривалість (мс)', 'anomaly_detection': '## 🚨 Виявлення аномалій', 'insufficient_anomaly_data': 'Поки що недостатньо даних для виявлення операційних аномалій.', 'none': 'Немає', 'detected_anomalies': 'Виявлені аномалії', 'highest_severity': 'Найвища серйозність', 'current_period_failures': 'Помилки в поточному періоді', 'current_p95': 'Поточний P95', 'current_failure_rate': 'Поточний рівень помилок', 'baseline_failure_rate': 'Базовий рівень помилок', 'current_confidence': 'Поточна довіра', 'baseline_confidence': 'Базова довіра', 'no_relevant_anomalies': 'У проаналізованих часових вікнах не виявлено релевантних операційних аномалій.', 'anomalies_by_severity': '### Аномалії за рівнем серйозності', 'critical': 'Критичні', 'high': 'Високі', 'medium': 'Середні', 'low': 'Низькі', 'informational': 'Інформаційні', 'detected_alerts': '### Виявлені попередження', 'anomaly': 'Аномалія', 'severity': 'Серйозність', 'metric': 'Метрика', 'recommendation': 'Рекомендація', 'outlier_executions': '### Виконання поза нормою', 'event_index': 'Індекс події', 'duration_ms': 'Тривалість (мс)', 'modified_z_score': 'Модифікований Z-показник', 'how_detection_works': 'Як працює виявлення', 'detection_explanation': '\nINNA порівнює поточний період із попередньою базовою лінією.\n\nАналізуються:\n\n- рівень помилок;\n- середня довіра Router;\n- P95 тривалості;\n- частка подій без інструмента;\n- середній погодинний обсяг;\n- окремі виконання поза нормою.\n\nДля виявлення аномальних значень тривалості використовуються **медіана та MAD**, що є стійкішим підходом до екстремальних значень, ніж середнє та стандартне відхилення.\n', 'tool': 'Інструмент', 'successes': 'Успіхи', 'success_rate': 'Рівень успіху (%)', 'average_confidence': 'Середня довіра (%)', 'average_ms': 'Середнє (мс)', 'minimum_ms': 'Мінімум (мс)', 'maximum_ms': 'Максимум (мс)', 'ranking_performance': '## Рейтинг і продуктивність інструментів', 'no_tool_found': 'Інструментів не знайдено.', 'usage_by_tool': '### Використання за інструментом', 'executions_hover': 'Виконання', 'p95_by_tool': '### P95 за інструментом', 'p95_latency': 'Затримка P95 (мс)', 'distributions': '## Розподіли', 'intentions': '### Наміри', 'origins': '### Джерела', 'intention': 'Намір', 'origin': 'Джерело', 'total': 'Усього', 'events': 'Події', 'temporal_evolution': '## Динаміка в часі', 'grouping': 'Групування', 'hour': 'Година', 'day': 'День', 'week': 'Тиждень', 'month': 'Місяць', 'insufficient_time_series': 'Недостатньо подій для побудови часового ряду.', 'period_label': 'Період', 'successful_executions': 'Успішні виконання', 'failed_executions': 'Невдалі виконання', 'most_active_users': '## Найактивніші користувачі', 'user': 'Користувач', 'no_user': 'без користувача', 'analytic_overview': '## Аналітичний огляд', 'analysed_events': 'Проаналізовані події', 'success_rate_metric': 'Рівень успіху', 'executions_without_tool': 'Виконання без інструмента', 'average_confidence_metric': 'Середня довіра', 'average_duration_metric': 'Середня тривалість', 'distinct_tools': 'Унікальні інструменти', 'unique_users': 'Унікальні користувачі'}


# TOOLS_ANALYTICS_RUSSIAN_NATIVE_TRANSLATIONS
TOOLS_ANALYTICS_TEXTS["ru"] = {'title': '📊 Аналитика Инструментов', 'caption': 'Операционный анализ использования, доверия, производительности, ошибок и поведения финансовых инструментов INNA.', 'loaded_events': 'Загруженные события', 'comparison_window': 'Окно сравнения', 'hours': 'часов', 'seven_days': '7 дней', 'refresh': '🔄 Обновить анализ', 'load_error': 'Не удалось загрузить события.', 'insufficient_events': 'Пока недостаточно событий для анализа.', 'operational_insights': '## 🧠 Операционные выводы INNA', 'health_score': 'Оценка состояния', 'no_summary': 'Сводка недоступна.', 'highlights': '### ✅ Сильные стороны', 'alerts': '### ⚠️ Предупреждения', 'no_critical_alert': 'Критических предупреждений не обнаружено.', 'technical_recommendations': '🛠️ Технические рекомендации', 'full_narrative': '📄 Показать полный анализ', 'period_comparison': '## Сравнение периодов', 'executions': 'Выполнения', 'failures': 'Ошибки', 'average_duration': 'Средняя длительность', 'detailed_comparison': 'Показать подробное сравнение', 'period': 'Период', 'current': 'Текущий', 'previous': 'Предыдущий', 'average_duration_ms': 'Средняя длительность (мс)', 'anomaly_detection': '## 🚨 Обнаружение аномалий', 'insufficient_anomaly_data': 'Пока недостаточно данных для обнаружения операционных аномалий.', 'none': 'Нет', 'detected_anomalies': 'Обнаруженные аномалии', 'highest_severity': 'Наивысший уровень серьёзности', 'current_period_failures': 'Ошибки в текущем периоде', 'current_p95': 'Текущий P95', 'current_failure_rate': 'Текущий уровень ошибок', 'baseline_failure_rate': 'Базовый уровень ошибок', 'current_confidence': 'Текущая уверенность', 'baseline_confidence': 'Базовая уверенность', 'no_relevant_anomalies': 'Для проанализированных временных окон не обнаружено значимых операционных аномалий.', 'anomalies_by_severity': '### Аномалии по уровню серьёзности', 'critical': 'Критические', 'high': 'Высокие', 'medium': 'Средние', 'low': 'Низкие', 'informational': 'Информационные', 'detected_alerts': '### Обнаруженные предупреждения', 'anomaly': 'Аномалия', 'severity': 'Серьёзность', 'metric': 'Метрика', 'recommendation': 'Рекомендация', 'outlier_executions': '### Выполнения за пределами нормы', 'event_index': 'Индекс события', 'duration_ms': 'Длительность (мс)', 'modified_z_score': 'Модифицированный Z-показатель', 'how_detection_works': 'Как работает обнаружение', 'detection_explanation': '\nINNA сравнивает текущий период с предыдущей базовой линией.\n\nАнализируются:\n\n- уровень ошибок;\n- средняя уверенность Router;\n- P95 длительности;\n- доля событий без инструмента;\n- средний почасовой объём;\n- отдельные выполнения за пределами нормы.\n\nДля обнаружения аномальных значений длительности используются **медиана и MAD**. Этот подход устойчивее к экстремальным значениям, чем среднее и стандартное отклонение.\n', 'tool': 'Инструмент', 'successes': 'Успешные выполнения', 'success_rate': 'Уровень успеха (%)', 'average_confidence': 'Средняя уверенность (%)', 'average_ms': 'Среднее (мс)', 'minimum_ms': 'Минимум (мс)', 'maximum_ms': 'Максимум (мс)', 'ranking_performance': '## Рейтинг и производительность инструментов', 'no_tool_found': 'Инструменты не найдены.', 'usage_by_tool': '### Использование по инструментам', 'executions_hover': 'Выполнения', 'p95_by_tool': '### P95 по инструментам', 'p95_latency': 'Задержка P95 (мс)', 'distributions': '## Распределения', 'intentions': '### Намерения', 'origins': '### Источники', 'intention': 'Намерение', 'origin': 'Источник', 'total': 'Всего', 'events': 'События', 'temporal_evolution': '## Динамика во времени', 'grouping': 'Группировка', 'hour': 'Час', 'day': 'День', 'week': 'Неделя', 'month': 'Месяц', 'insufficient_time_series': 'Недостаточно событий для построения временного ряда.', 'period_label': 'Период', 'successful_executions': 'Успешные выполнения', 'failed_executions': 'Неудачные выполнения', 'most_active_users': '## Самые активные пользователи', 'user': 'Пользователь', 'no_user': 'без пользователя', 'analytic_overview': '## Аналитический обзор', 'analysed_events': 'Проанализированные события', 'success_rate_metric': 'Уровень успеха', 'executions_without_tool': 'Выполнения без инструмента', 'average_confidence_metric': 'Средняя уверенность', 'average_duration_metric': 'Средняя длительность', 'distinct_tools': 'Уникальные инструменты', 'unique_users': 'Уникальные пользователи'}


# TOOLS_ANALYTICS_ARABIC_NATIVE_TRANSLATIONS
TOOLS_ANALYTICS_TEXTS["sa"] = {'title': '📊 تحليلات الأدوات', 'caption': 'تحليل تشغيلي لاستخدام أدوات INNA المالية ودرجة الثقة والأداء والإخفاقات والسلوك.', 'loaded_events': 'الأحداث المحمّلة', 'comparison_window': 'نافذة المقارنة', 'hours': 'ساعات', 'seven_days': '7 أيام', 'refresh': '🔄 تحديث التحليل', 'load_error': 'تعذر تحميل الأحداث.', 'insufficient_events': 'لا توجد أحداث كافية للتحليل حتى الآن.', 'operational_insights': '## 🧠 الرؤى التشغيلية لـ INNA', 'health_score': 'درجة صحة النظام', 'no_summary': 'لا يتوفر ملخص.', 'highlights': '### ✅ أبرز النقاط', 'alerts': '### ⚠️ التنبيهات', 'no_critical_alert': 'لم يتم اكتشاف أي تنبيه حرج.', 'technical_recommendations': '🛠️ التوصيات التقنية', 'full_narrative': '📄 عرض التحليل الكامل', 'period_comparison': '## مقارنة الفترات', 'executions': 'عمليات التنفيذ', 'failures': 'الإخفاقات', 'average_duration': 'متوسط المدة', 'detailed_comparison': 'عرض المقارنة التفصيلية', 'period': 'الفترة', 'current': 'الحالية', 'previous': 'السابقة', 'average_duration_ms': 'متوسط المدة (مللي ثانية)', 'anomaly_detection': '## 🚨 اكتشاف الحالات الشاذة', 'insufficient_anomaly_data': 'لا توجد بيانات كافية حتى الآن لاكتشاف الحالات التشغيلية الشاذة.', 'none': 'لا يوجد', 'detected_anomalies': 'الحالات الشاذة المكتشفة', 'highest_severity': 'أعلى مستوى خطورة', 'current_period_failures': 'إخفاقات الفترة الحالية', 'current_p95': 'قيمة P95 الحالية', 'current_failure_rate': 'معدل الإخفاق الحالي', 'baseline_failure_rate': 'معدل الإخفاق المرجعي', 'current_confidence': 'درجة الثقة الحالية', 'baseline_confidence': 'درجة الثقة المرجعية', 'no_relevant_anomalies': 'لم يتم اكتشاف حالات تشغيلية شاذة مهمة ضمن النوافذ التي تم تحليلها.', 'anomalies_by_severity': '### الحالات الشاذة حسب مستوى الخطورة', 'critical': 'حرجة', 'high': 'مرتفعة', 'medium': 'متوسطة', 'low': 'منخفضة', 'informational': 'معلوماتية', 'detected_alerts': '### التنبيهات المكتشفة', 'anomaly': 'الحالة الشاذة', 'severity': 'مستوى الخطورة', 'metric': 'المقياس', 'recommendation': 'التوصية', 'outlier_executions': '### عمليات التنفيذ الخارجة عن النمط', 'event_index': 'فهرس الحدث', 'duration_ms': 'المدة (مللي ثانية)', 'modified_z_score': 'درجة Z المعدلة', 'how_detection_works': 'كيفية عمل الاكتشاف', 'detection_explanation': '\nتقارن INNA الفترة الحالية بخط أساس سابق.\n\nيتم تحليل ما يلي:\n\n- معدل الإخفاق؛\n- متوسط درجة ثقة Router؛\n- قيمة P95 للمدة؛\n- نسبة الأحداث التي لم تستخدم أداة؛\n- متوسط حجم الأحداث في الساعة؛\n- عمليات التنفيذ الفردية الخارجة عن النمط.\n\nيستخدم اكتشاف القيم الشاذة للمدة **الوسيط وMAD**، وهو أسلوب أكثر مقاومة للقيم المتطرفة من المتوسط والانحراف المعياري.\n', 'tool': 'الأداة', 'successes': 'العمليات الناجحة', 'success_rate': 'معدل النجاح (%)', 'average_confidence': 'متوسط درجة الثقة (%)', 'average_ms': 'المتوسط (مللي ثانية)', 'minimum_ms': 'الحد الأدنى (مللي ثانية)', 'maximum_ms': 'الحد الأقصى (مللي ثانية)', 'ranking_performance': '## ترتيب الأدوات وأداؤها', 'no_tool_found': 'لم يتم العثور على أي أداة.', 'usage_by_tool': '### الاستخدام حسب الأداة', 'executions_hover': 'عمليات التنفيذ', 'p95_by_tool': '### قيمة P95 حسب الأداة', 'p95_latency': 'زمن الاستجابة P95 (مللي ثانية)', 'distributions': '## التوزيعات', 'intentions': '### النوايا', 'origins': '### المصادر', 'intention': 'النية', 'origin': 'المصدر', 'total': 'الإجمالي', 'events': 'الأحداث', 'temporal_evolution': '## التطور الزمني', 'grouping': 'التجميع', 'hour': 'ساعة', 'day': 'يوم', 'week': 'أسبوع', 'month': 'شهر', 'insufficient_time_series': 'لا توجد أحداث كافية لإنشاء السلسلة الزمنية.', 'period_label': 'الفترة', 'successful_executions': 'عمليات التنفيذ الناجحة', 'failed_executions': 'عمليات التنفيذ الفاشلة', 'most_active_users': '## المستخدمون الأكثر نشاطًا', 'user': 'المستخدم', 'no_user': 'من دون مستخدم', 'analytic_overview': '## النظرة التحليلية', 'analysed_events': 'الأحداث التي تم تحليلها', 'success_rate_metric': 'معدل النجاح', 'executions_without_tool': 'عمليات التنفيذ من دون أداة', 'average_confidence_metric': 'متوسط درجة الثقة', 'average_duration_metric': 'متوسط المدة', 'distinct_tools': 'الأدوات المختلفة', 'unique_users': 'المستخدمون الفريدون'}


# TOOLS_ANALYTICS_ITALIAN_ANOMALY_TRANSLATIONS
# Completa a área de detecção de anomalias que ainda
# utilizava textos em inglês no pacote italiano.

TOOLS_ANALYTICS_TEXTS["it"].update(
    {
        "anomaly_detection": (
            "## 🚨 Rilevamento delle anomalie"
        ),
        "insufficient_anomaly_data": (
            "Non sono ancora disponibili dati sufficienti "
            "per rilevare anomalie operative."
        ),
        "none": "Nessuna",
        "detected_anomalies": (
            "Anomalie rilevate"
        ),
        "highest_severity": (
            "Gravità massima"
        ),
        "current_period_failures": (
            "Errori nel periodo attuale"
        ),
        "current_p95": "P95 attuale",
        "current_failure_rate": (
            "Tasso di errore attuale"
        ),
        "baseline_failure_rate": (
            "Tasso di errore di riferimento"
        ),
        "current_confidence": (
            "Affidabilità attuale"
        ),
        "baseline_confidence": (
            "Affidabilità di riferimento"
        ),
        "no_relevant_anomalies": (
            "Non sono state rilevate anomalie operative "
            "rilevanti nelle finestre analizzate."
        ),
        "anomalies_by_severity": (
            "### Anomalie per gravità"
        ),
        "critical": "Critiche",
        "high": "Elevate",
        "medium": "Medie",
        "low": "Basse",
        "informational": "Informative",
        "detected_alerts": (
            "### Avvisi rilevati"
        ),
        "anomaly": "Anomalia",
        "severity": "Gravità",
        "metric": "Metrica",
        "recommendation": "Raccomandazione",
        "outlier_executions": (
            "### Esecuzioni fuori norma"
        ),
        "event_index": (
            "Indice dell’evento"
        ),
        "duration_ms": "Durata (ms)",
        "modified_z_score": (
            "Punteggio Z modificato"
        ),
        "how_detection_works": (
            "Come funziona il rilevamento"
        ),
    }
)



# TOOLS_ANALYTICS_VISUAL_LABEL_TRANSLATIONS
# Rótulos visuais que antes estavam fixos em português.

TOOLS_ANALYTICS_TEXTS["pt"].update(
    {
        "current_value": "Valor atual",
        "reference": "Referência",
    }
)

TOOLS_ANALYTICS_TEXTS["en_us"].update(
    {
        "current_value": "Current value",
        "reference": "Reference",
    }
)

TOOLS_ANALYTICS_TEXTS["en_gb"].update(
    {
        "current_value": "Current value",
        "reference": "Reference",
    }
)

TOOLS_ANALYTICS_TEXTS["es"].update(
    {
        "current_value": "Valor actual",
        "reference": "Referencia",
    }
)

TOOLS_ANALYTICS_TEXTS["fr"].update(
    {
        "current_value": "Valeur actuelle",
        "reference": "Référence",
    }
)

TOOLS_ANALYTICS_TEXTS["de"].update(
    {
        "current_value": "Aktueller Wert",
        "reference": "Referenz",
    }
)

TOOLS_ANALYTICS_TEXTS["it"].update(
    {
        "current_value": "Valore attuale",
        "reference": "Riferimento",
    }
)

TOOLS_ANALYTICS_TEXTS["ro"].update(
    {
        "current_value": "Valoare actuală",
        "reference": "Referință",
    }
)

TOOLS_ANALYTICS_TEXTS["ua"].update(
    {
        "current_value": "Поточне значення",
        "reference": "Орієнтир",
    }
)

TOOLS_ANALYTICS_TEXTS["ru"].update(
    {
        "current_value": "Текущее значение",
        "reference": "Ориентир",
    }
)

TOOLS_ANALYTICS_TEXTS["sa"].update(
    {
        "current_value": "القيمة الحالية",
        "reference": "القيمة المرجعية",
    }
)

TOOLS_ANALYTICS_TEXTS["ch"].update(
    {
        "current_value": "Aktueller Wert",
        "reference": "Referenz",
    }
)


# TOOLS_ANALYTICS_DETACHED_LANGUAGE_PACKS
# Impede que um idioma sobrescreva outro quando
# os pacotes antigos compartilham o mesmo objeto.

for _language in (
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
):
    if _language in TOOLS_ANALYTICS_TEXTS:
        TOOLS_ANALYTICS_TEXTS[
            _language
        ] = dict(
            TOOLS_ANALYTICS_TEXTS[
                _language
            ]
        )

# Traduções nativas da seção de detecção de anomalias.
TOOLS_ANALYTICS_ANOMALY_TEXTS["it"].update(
    {
        "anomaly_detection": "## 🚨 Rilevamento delle anomalie",
        "insufficient_anomaly_data": (
            "Non sono ancora disponibili dati sufficienti "
            "per rilevare anomalie operative."
        ),
        "none": "Nessuna",
        "detected_anomalies": "Anomalie rilevate",
        "highest_severity": "Gravità più elevata",
        "current_period_failures": "Errori del periodo corrente",
        "current_p95": "P95 corrente",
        "current_failure_rate": "Tasso di errore corrente",
        "baseline_failure_rate": "Tasso di errore di riferimento",
        "current_confidence": "Confidenza corrente",
        "baseline_confidence": "Confidenza di riferimento",
        "no_relevant_anomalies": (
            "Non sono state rilevate anomalie operative "
            "rilevanti nelle finestre analizzate."
        ),
        "anomalies_by_severity": "### Anomalie per gravità",
        "critical": "Critica",
        "high": "Alta",
        "medium": "Media",
        "low": "Bassa",
        "informational": "Informativa",
        "detected_alerts": "### Avvisi rilevati",
        "anomaly": "Anomalia",
        "severity": "Gravità",
        "metric": "Metrica",
        "recommendation": "Raccomandazione",
        "outlier_executions": "### Esecuzioni anomale",
        "event_index": "Indice dell’evento",
        "duration_ms": "Durata (ms)",
        "modified_z_score": "Modified Z-Score",
        "how_detection_works": "Come funziona il rilevamento",
        "detection_explanation": """
INNA confronta il periodo corrente con un periodo precedente
utilizzato come riferimento.

Vengono analizzati:

- tasso di errore;
- confidenza media del Router;
- latenza P95;
- volume delle esecuzioni;
- singole esecuzioni anomale.

Le anomalie di durata utilizzano **mediana e MAD**, un approccio
più resistente ai valori estremi rispetto a media e deviazione standard.
""",
    }
)

TOOLS_ANALYTICS_ANOMALY_TEXTS["ro"].update(
    {
        "anomaly_detection": "## 🚨 Detectarea anomaliilor",
        "insufficient_anomaly_data": (
            "Nu există încă suficiente date pentru "
            "detectarea anomaliilor operaționale."
        ),
        "none": "Niciuna",
        "detected_anomalies": "Anomalii detectate",
        "highest_severity": "Cea mai mare severitate",
        "current_period_failures": "Eșecuri în perioada curentă",
        "current_p95": "P95 curent",
        "current_failure_rate": "Rata curentă de eșec",
        "baseline_failure_rate": "Rata de eșec de referință",
        "current_confidence": "Încredere curentă",
        "baseline_confidence": "Încredere de referință",
        "no_relevant_anomalies": (
            "Nu a fost detectată nicio anomalie operațională "
            "relevantă în intervalele analizate."
        ),
        "anomalies_by_severity": "### Anomalii după severitate",
        "critical": "Critică",
        "high": "Ridicată",
        "medium": "Medie",
        "low": "Scăzută",
        "informational": "Informativă",
        "detected_alerts": "### Alerte detectate",
        "anomaly": "Anomalie",
        "severity": "Severitate",
        "metric": "Metrică",
        "recommendation": "Recomandare",
        "outlier_executions": "### Execuții atipice",
        "event_index": "Indexul evenimentului",
        "duration_ms": "Durată (ms)",
        "modified_z_score": "Modified Z-Score",
        "how_detection_works": "Cum funcționează detectarea",
        "detection_explanation": """
INNA compară perioada curentă cu o perioadă anterioară
folosită drept referință.

Sunt analizate:

- rata de eșec;
- încrederea medie a Routerului;
- latența P95;
- volumul execuțiilor;
- execuțiile individuale atipice.

Valorile atipice de durată folosesc **mediana și MAD**, o abordare
mai rezistentă la valori extreme decât media și abaterea standard.
""",
    }
)

TOOLS_ANALYTICS_ANOMALY_TEXTS["ua"].update(
    {
        "anomaly_detection": "## 🚨 Виявлення аномалій",
        "insufficient_anomaly_data": (
            "Поки що недостатньо даних для виявлення "
            "операційних аномалій."
        ),
        "none": "Немає",
        "detected_anomalies": "Виявлені аномалії",
        "highest_severity": "Найвищий рівень серйозності",
        "current_period_failures": "Помилки поточного періоду",
        "current_p95": "Поточний P95",
        "current_failure_rate": "Поточна частота помилок",
        "baseline_failure_rate": "Базова частота помилок",
        "current_confidence": "Поточна впевненість",
        "baseline_confidence": "Базова впевненість",
        "no_relevant_anomalies": (
            "У проаналізованих часових вікнах не виявлено "
            "суттєвих операційних аномалій."
        ),
        "anomalies_by_severity": "### Аномалії за рівнем серйозності",
        "critical": "Критична",
        "high": "Висока",
        "medium": "Середня",
        "low": "Низька",
        "informational": "Інформаційна",
        "detected_alerts": "### Виявлені попередження",
        "anomaly": "Аномалія",
        "severity": "Серйозність",
        "metric": "Метрика",
        "recommendation": "Рекомендація",
        "outlier_executions": "### Нетипові виконання",
        "event_index": "Індекс події",
        "duration_ms": "Тривалість (ms)",
        "modified_z_score": "Modified Z-Score",
        "how_detection_works": "Як працює виявлення",
        "detection_explanation": """
INNA порівнює поточний період із попереднім базовим періодом.

Аналізуються:

- частота помилок;
- середня впевненість Router;
- затримка P95;
- обсяг виконань;
- окремі нетипові виконання.

Для виявлення аномалій тривалості використовуються
**медіана та MAD** — підхід, стійкіший до екстремальних значень,
ніж середнє значення та стандартне відхилення.
""",
    }
)

TOOLS_ANALYTICS_ANOMALY_TEXTS["ru"].update(
    {
        "anomaly_detection": "## 🚨 Обнаружение аномалий",
        "insufficient_anomaly_data": (
            "Пока недостаточно данных для обнаружения "
            "операционных аномалий."
        ),
        "none": "Нет",
        "detected_anomalies": "Обнаруженные аномалии",
        "highest_severity": "Наивысшая серьёзность",
        "current_period_failures": "Ошибки текущего периода",
        "current_p95": "Текущий P95",
        "current_failure_rate": "Текущая частота ошибок",
        "baseline_failure_rate": "Базовая частота ошибок",
        "current_confidence": "Текущая уверенность",
        "baseline_confidence": "Базовая уверенность",
        "no_relevant_anomalies": (
            "В проанализированных временных окнах не обнаружено "
            "значимых операционных аномалий."
        ),
        "anomalies_by_severity": "### Аномалии по уровню серьёзности",
        "critical": "Критическая",
        "high": "Высокая",
        "medium": "Средняя",
        "low": "Низкая",
        "informational": "Информационная",
        "detected_alerts": "### Обнаруженные предупреждения",
        "anomaly": "Аномалия",
        "severity": "Серьёзность",
        "metric": "Метрика",
        "recommendation": "Рекомендация",
        "outlier_executions": "### Нетипичные выполнения",
        "event_index": "Индекс события",
        "duration_ms": "Длительность (ms)",
        "modified_z_score": "Modified Z-Score",
        "how_detection_works": "Как работает обнаружение",
        "detection_explanation": """
INNA сравнивает текущий период с предыдущим базовым периодом.

Анализируются:

- частота ошибок;
- средняя уверенность Router;
- задержка P95;
- объём выполнений;
- отдельные нетипичные выполнения.

Для аномалий длительности используются **медиана и MAD** —
подход, более устойчивый к экстремальным значениям,
чем среднее значение и стандартное отклонение.
""",
    }
)

TOOLS_ANALYTICS_ANOMALY_TEXTS["sa"].update(
    {
        "anomaly_detection": "## 🚨 اكتشاف الحالات الشاذة",
        "insufficient_anomaly_data": (
            "لا تتوفر بيانات كافية بعد لاكتشاف "
            "الحالات التشغيلية الشاذة."
        ),
        "none": "لا يوجد",
        "detected_anomalies": "الحالات الشاذة المكتشفة",
        "highest_severity": "أعلى درجة خطورة",
        "current_period_failures": "إخفاقات الفترة الحالية",
        "current_p95": "قيمة P95 الحالية",
        "current_failure_rate": "معدل الإخفاق الحالي",
        "baseline_failure_rate": "معدل الإخفاق المرجعي",
        "current_confidence": "الثقة الحالية",
        "baseline_confidence": "الثقة المرجعية",
        "no_relevant_anomalies": (
            "لم يتم اكتشاف حالات تشغيلية شاذة مهمة "
            "ضمن الفترات التي جرى تحليلها."
        ),
        "anomalies_by_severity": "### الحالات الشاذة حسب الخطورة",
        "critical": "حرجة",
        "high": "مرتفعة",
        "medium": "متوسطة",
        "low": "منخفضة",
        "informational": "معلوماتية",
        "detected_alerts": "### التنبيهات المكتشفة",
        "anomaly": "حالة شاذة",
        "severity": "الخطورة",
        "metric": "المقياس",
        "recommendation": "التوصية",
        "outlier_executions": "### عمليات التنفيذ الشاذة",
        "event_index": "فهرس الحدث",
        "duration_ms": "المدة (ms)",
        "modified_z_score": "Modified Z-Score",
        "how_detection_works": "كيفية عمل الاكتشاف",
        "detection_explanation": """
تقارن INNA الفترة الحالية بفترة سابقة تُستخدم كمرجع.

يتم تحليل ما يلي:

- معدل الإخفاق؛
- متوسط ثقة Router؛
- زمن الاستجابة P95؛
- حجم عمليات التنفيذ؛
- عمليات التنفيذ الفردية الشاذة.

تستخدم القيم الشاذة للمدة **الوسيط وMAD**، وهي طريقة
أكثر مقاومة للقيم المتطرفة من المتوسط والانحراف المعياري.
""",
    }
)

# O código ch segue o catálogo alemão do projeto.
TOOLS_ANALYTICS_ANOMALY_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_ANOMALY_TEXTS["de"]
)


# Traduções nativas da comparação entre períodos.
TOOLS_ANALYTICS_PERIOD_TEXTS["ro"].update(
    {
        "period_comparison": (
            "## Comparație între perioade"
        ),
        "executions": "Execuții",
        "failures": "Eșecuri",
        "average_duration": "Durată medie",
        "detailed_comparison": (
            "Vizualizează comparația detaliată"
        ),
        "period": "Perioadă",
        "current": "Curentă",
        "previous": "Anterioară",
        "average_duration_ms": (
            "Durată medie (ms)"
        ),
    }
)

TOOLS_ANALYTICS_PERIOD_TEXTS["ua"].update(
    {
        "period_comparison": (
            "## Порівняння періодів"
        ),
        "executions": "Виконання",
        "failures": "Помилки",
        "average_duration": (
            "Середня тривалість"
        ),
        "detailed_comparison": (
            "Переглянути детальне порівняння"
        ),
        "period": "Період",
        "current": "Поточний",
        "previous": "Попередній",
        "average_duration_ms": (
            "Середня тривалість (ms)"
        ),
    }
)

TOOLS_ANALYTICS_PERIOD_TEXTS["ru"].update(
    {
        "period_comparison": (
            "## Сравнение периодов"
        ),
        "executions": "Выполнения",
        "failures": "Ошибки",
        "average_duration": (
            "Средняя длительность"
        ),
        "detailed_comparison": (
            "Показать подробное сравнение"
        ),
        "period": "Период",
        "current": "Текущий",
        "previous": "Предыдущий",
        "average_duration_ms": (
            "Средняя длительность (ms)"
        ),
    }
)

TOOLS_ANALYTICS_PERIOD_TEXTS["sa"].update(
    {
        "period_comparison": (
            "## مقارنة الفترات"
        ),
        "executions": "عمليات التنفيذ",
        "failures": "الإخفاقات",
        "average_duration": (
            "متوسط المدة"
        ),
        "detailed_comparison": (
            "عرض المقارنة التفصيلية"
        ),
        "period": "الفترة",
        "current": "الحالية",
        "previous": "السابقة",
        "average_duration_ms": (
            "متوسط المدة (ms)"
        ),
    }
)

# الرمز ch يتبع اللغة الألمانية في المشروع.
TOOLS_ANALYTICS_PERIOD_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_PERIOD_TEXTS["de"]
)


# Traduções nativas do ranking e desempenho por ferramenta.
TOOLS_ANALYTICS_RANKING_TEXTS["ro"].update(
    {
        "successes": "Succese",
        "success_rate": "Rată de succes (%)",
        "average_confidence": "Încredere medie (%)",
        "average_ms": "Medie (ms)",
        "minimum_ms": "Minim (ms)",
        "maximum_ms": "Maxim (ms)",
        "ranking_performance": (
            "## Clasamentul și performanța instrumentelor"
        ),
        "no_tool_found": (
            "Nu a fost găsit niciun instrument."
        ),
        "usage_by_tool": (
            "### Utilizare după instrument"
        ),
        "executions_hover": "Execuții",
        "p95_by_tool": (
            "### P95 după instrument"
        ),
        "p95_latency": "Latență P95 (ms)",
    }
)

TOOLS_ANALYTICS_RANKING_TEXTS["ua"].update(
    {
        "successes": "Успішні виконання",
        "success_rate": "Рівень успіху (%)",
        "average_confidence": (
            "Середня впевненість (%)"
        ),
        "average_ms": "Середнє (ms)",
        "minimum_ms": "Мінімум (ms)",
        "maximum_ms": "Максимум (ms)",
        "ranking_performance": (
            "## Рейтинг і продуктивність інструментів"
        ),
        "no_tool_found": (
            "Інструментів не знайдено."
        ),
        "usage_by_tool": (
            "### Використання за інструментами"
        ),
        "executions_hover": "Виконання",
        "p95_by_tool": (
            "### P95 за інструментами"
        ),
        "p95_latency": "Затримка P95 (ms)",
    }
)

TOOLS_ANALYTICS_RANKING_TEXTS["ru"].update(
    {
        "successes": "Успешные выполнения",
        "success_rate": "Уровень успешности (%)",
        "average_confidence": (
            "Средняя уверенность (%)"
        ),
        "average_ms": "Среднее (ms)",
        "minimum_ms": "Минимум (ms)",
        "maximum_ms": "Максимум (ms)",
        "ranking_performance": (
            "## Рейтинг и производительность инструментов"
        ),
        "no_tool_found": (
            "Инструменты не найдены."
        ),
        "usage_by_tool": (
            "### Использование по инструментам"
        ),
        "executions_hover": "Выполнения",
        "p95_by_tool": (
            "### P95 по инструментам"
        ),
        "p95_latency": "Задержка P95 (ms)",
    }
)

TOOLS_ANALYTICS_RANKING_TEXTS["sa"].update(
    {
        "successes": "عمليات التنفيذ الناجحة",
        "success_rate": "معدل النجاح (%)",
        "average_confidence": (
            "متوسط الثقة (%)"
        ),
        "average_ms": "المتوسط (ms)",
        "minimum_ms": "الحد الأدنى (ms)",
        "maximum_ms": "الحد الأقصى (ms)",
        "ranking_performance": (
            "## ترتيب الأدوات وأداؤها"
        ),
        "no_tool_found": (
            "لم يتم العثور على أي أداة."
        ),
        "usage_by_tool": (
            "### الاستخدام حسب الأداة"
        ),
        "executions_hover": "عمليات التنفيذ",
        "p95_by_tool": (
            "### قيمة P95 حسب الأداة"
        ),
        "p95_latency": "زمن الاستجابة P95 (ms)",
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TOOLS_ANALYTICS_RANKING_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_RANKING_TEXTS["de"]
)


# Traduções nativas das distribuições.
TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["ro"].update(
    {
        "distributions": "## Distribuții",
        "intentions": "### Intenții",
        "origins": "### Origini",
        "intention": "Intenție",
        "origin": "Origine",
        "total": "Total",
        "events": "Evenimente",
    }
)

TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["ua"].update(
    {
        "distributions": "## Розподіли",
        "intentions": "### Наміри",
        "origins": "### Джерела",
        "intention": "Намір",
        "origin": "Джерело",
        "total": "Загалом",
        "events": "Події",
    }
)

TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["ru"].update(
    {
        "distributions": "## Распределения",
        "intentions": "### Намерения",
        "origins": "### Источники",
        "intention": "Намерение",
        "origin": "Источник",
        "total": "Всего",
        "events": "События",
    }
)

TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["sa"].update(
    {
        "distributions": "## التوزيعات",
        "intentions": "### النوايا",
        "origins": "### المصادر",
        "intention": "النية",
        "origin": "المصدر",
        "total": "الإجمالي",
        "events": "الأحداث",
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["de"]
)


# Traduções nativas da evolução temporal.
TOOLS_ANALYTICS_TEMPORAL_TEXTS["ro"].update(
    {
        "temporal_evolution": (
            "## Evoluție temporală"
        ),
        "grouping": "Grupare",
        "hour": "Oră",
        "day": "Zi",
        "week": "Săptămână",
        "month": "Lună",
        "insufficient_time_series": (
            "Nu există suficiente evenimente "
            "pentru seria temporală."
        ),
        "period_label": "Perioadă",
        "successful_executions": (
            "Execuții reușite"
        ),
        "failed_executions": (
            "Execuții eșuate"
        ),
        "most_active_users": (
            "## Cei mai activi utilizatori"
        ),
        "user": "Utilizator",
        "no_user": "fără utilizator",
    }
)

TOOLS_ANALYTICS_TEMPORAL_TEXTS["ua"].update(
    {
        "temporal_evolution": (
            "## Часова динаміка"
        ),
        "grouping": "Групування",
        "hour": "Година",
        "day": "День",
        "week": "Тиждень",
        "month": "Місяць",
        "insufficient_time_series": (
            "Недостатньо подій для побудови "
            "часового ряду."
        ),
        "period_label": "Період",
        "successful_executions": (
            "Успішні виконання"
        ),
        "failed_executions": (
            "Невдалі виконання"
        ),
        "most_active_users": (
            "## Найактивніші користувачі"
        ),
        "user": "Користувач",
        "no_user": "без користувача",
    }
)

TOOLS_ANALYTICS_TEMPORAL_TEXTS["ru"].update(
    {
        "temporal_evolution": (
            "## Временная динамика"
        ),
        "grouping": "Группировка",
        "hour": "Час",
        "day": "День",
        "week": "Неделя",
        "month": "Месяц",
        "insufficient_time_series": (
            "Недостаточно событий для построения "
            "временного ряда."
        ),
        "period_label": "Период",
        "successful_executions": (
            "Успешные выполнения"
        ),
        "failed_executions": (
            "Неудачные выполнения"
        ),
        "most_active_users": (
            "## Самые активные пользователи"
        ),
        "user": "Пользователь",
        "no_user": "без пользователя",
    }
)

TOOLS_ANALYTICS_TEMPORAL_TEXTS["sa"].update(
    {
        "temporal_evolution": (
            "## التطور الزمني"
        ),
        "grouping": "التجميع",
        "hour": "الساعة",
        "day": "اليوم",
        "week": "الأسبوع",
        "month": "الشهر",
        "insufficient_time_series": (
            "لا توجد أحداث كافية لإنشاء "
            "السلسلة الزمنية."
        ),
        "period_label": "الفترة",
        "successful_executions": (
            "عمليات التنفيذ الناجحة"
        ),
        "failed_executions": (
            "عمليات التنفيذ الفاشلة"
        ),
        "most_active_users": (
            "## المستخدمون الأكثر نشاطًا"
        ),
        "user": "المستخدم",
        "no_user": "من دون مستخدم",
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TOOLS_ANALYTICS_TEMPORAL_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_TEMPORAL_TEXTS["de"]
)


# Traduções nativas da visão geral analítica.
TOOLS_ANALYTICS_OVERVIEW_TEXTS["ro"].update(
    {
        "analytic_overview": (
            "## Prezentare generală analitică"
        ),
        "analysed_events": (
            "Evenimente analizate"
        ),
        "success_rate_metric": (
            "Rată de succes"
        ),
        "executions_without_tool": (
            "Execuții fără instrument"
        ),
        "average_confidence_metric": (
            "Încredere medie"
        ),
        "average_duration_metric": (
            "Durată medie"
        ),
        "distinct_tools": (
            "Instrumente distincte"
        ),
        "unique_users": (
            "Utilizatori unici"
        ),
        "detection_explanation": """
INNA compară perioada curentă cu o perioadă anterioară
folosită drept referință.

Sunt analizate:

- rata de eșec;
- încrederea medie a Routerului;
- durata P95;
- procentul evenimentelor fără instrument;
- volumul mediu pe oră;
- execuțiile individuale atipice.

Valorile atipice de durată folosesc **mediana și MAD**, o abordare
mai rezistentă la valori extreme decât media și abaterea standard.
""",
    }
)

TOOLS_ANALYTICS_OVERVIEW_TEXTS["ua"].update(
    {
        "analytic_overview": (
            "## Аналітичний огляд"
        ),
        "analysed_events": (
            "Проаналізовані події"
        ),
        "success_rate_metric": (
            "Рівень успіху"
        ),
        "executions_without_tool": (
            "Виконання без інструмента"
        ),
        "average_confidence_metric": (
            "Середня впевненість"
        ),
        "average_duration_metric": (
            "Середня тривалість"
        ),
        "distinct_tools": (
            "Різні інструменти"
        ),
        "unique_users": (
            "Унікальні користувачі"
        ),
        "detection_explanation": """
INNA порівнює поточний період із попереднім базовим періодом.

Аналізуються:

- частота помилок;
- середня впевненість Router;
- тривалість P95;
- частка подій без інструмента;
- середній погодинний обсяг;
- окремі нетипові виконання.

Для виявлення аномалій тривалості використовуються
**медіана та MAD** — підхід, стійкіший до екстремальних значень,
ніж середнє значення та стандартне відхилення.
""",
    }
)

TOOLS_ANALYTICS_OVERVIEW_TEXTS["ru"].update(
    {
        "analytic_overview": (
            "## Аналитический обзор"
        ),
        "analysed_events": (
            "Проанализированные события"
        ),
        "success_rate_metric": (
            "Уровень успешности"
        ),
        "executions_without_tool": (
            "Выполнения без инструмента"
        ),
        "average_confidence_metric": (
            "Средняя уверенность"
        ),
        "average_duration_metric": (
            "Средняя длительность"
        ),
        "distinct_tools": (
            "Различные инструменты"
        ),
        "unique_users": (
            "Уникальные пользователи"
        ),
        "detection_explanation": """
INNA сравнивает текущий период с предыдущим базовым периодом.

Анализируются:

- частота ошибок;
- средняя уверенность Router;
- длительность P95;
- доля событий без инструмента;
- средний почасовой объём;
- отдельные нетипичные выполнения.

Для аномалий длительности используются **медиана и MAD** —
подход, более устойчивый к экстремальным значениям,
чем среднее значение и стандартное отклонение.
""",
    }
)

TOOLS_ANALYTICS_OVERVIEW_TEXTS["sa"].update(
    {
        "analytic_overview": (
            "## النظرة العامة التحليلية"
        ),
        "analysed_events": (
            "الأحداث التي جرى تحليلها"
        ),
        "success_rate_metric": (
            "معدل النجاح"
        ),
        "executions_without_tool": (
            "عمليات التنفيذ من دون أداة"
        ),
        "average_confidence_metric": (
            "متوسط الثقة"
        ),
        "average_duration_metric": (
            "متوسط المدة"
        ),
        "distinct_tools": (
            "الأدوات المختلفة"
        ),
        "unique_users": (
            "المستخدمون الفريدون"
        ),
        "detection_explanation": """
تقارن INNA الفترة الحالية بفترة سابقة تُستخدم كمرجع.

يتم تحليل ما يلي:

- معدل الإخفاق؛
- متوسط ثقة Router؛
- مدة P95؛
- نسبة الأحداث التي لم تستخدم أداة؛
- متوسط الحجم في الساعة؛
- عمليات التنفيذ الفردية الشاذة.

تستخدم القيم الشاذة للمدة **الوسيط وMAD**، وهي طريقة
أكثر مقاومة للقيم المتطرفة من المتوسط والانحراف المعياري.
""",
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TOOLS_ANALYTICS_OVERVIEW_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_OVERVIEW_TEXTS["de"]
)


# Ajustes finais dos rótulos nativos da análise de ferramentas.
TOOLS_ANALYTICS_TEXTS["fr"].update(
    {
        "minimum_ms": "Minimum (ms)",
        "maximum_ms": "Maximum (ms)",
        "distributions": "## Répartitions",
        "intentions": "### Intentions détectées",
        "intention": "Intention détectée",
    }
)

TOOLS_ANALYTICS_TEXTS["de"].update(
    {
        "minimum_ms": "Minimalwert (ms)",
        "maximum_ms": "Maximalwert (ms)",
    }
)

TOOLS_ANALYTICS_RANKING_TEXTS["fr"].update(
    {
        "minimum_ms": "Minimum (ms)",
        "maximum_ms": "Maximum (ms)",
    }
)

TOOLS_ANALYTICS_RANKING_TEXTS["de"].update(
    {
        "minimum_ms": "Minimalwert (ms)",
        "maximum_ms": "Maximalwert (ms)",
    }
)

TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["fr"].update(
    {
        "distributions": "## Répartitions",
        "intentions": "### Intentions détectées",
        "intention": "Intention détectée",
    }
)

# O código ch segue os catálogos alemães do projeto.
TOOLS_ANALYTICS_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_TEXTS["de"]
)

TOOLS_ANALYTICS_RANKING_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_RANKING_TEXTS["de"]
)

TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["ch"] = dict(
    TOOLS_ANALYTICS_DISTRIBUTION_TEXTS["de"]
)


def tools_analytics_lang() -> str:
    return normalize_language(
        st.session_state.get(
            "dashboard_interface_lang",
            "pt",
        )
    )


def tools_analytics_t(
    key: str,
    default: str | None = None,
    **format_values: Any,
) -> str:
    return page_translate(
        TOOLS_ANALYTICS_TEXTS,
        key,
        language=tools_analytics_lang(),
        default=default,
        **format_values,
    )


def formatar_delta_percentual(
    valor: float,
) -> str:
    """
    Formata variação percentual para exibição.
    """
    return f"{float(valor):+.2f}%"


def preparar_ranking_exibicao(
    ranking: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Converte nomes técnicos em nomes amigáveis.
    """
    if ranking is None or ranking.empty:
        return pd.DataFrame()

    tabela = ranking.copy()

    colunas = {
        "ferramenta": tools_analytics_t("tool"),
        "execucoes": tools_analytics_t("executions"),
        "sucessos": tools_analytics_t("successes"),
        "falhas": tools_analytics_t("failures"),
        "taxa_sucesso_percentual": tools_analytics_t(
            "success_rate"
        ),
        "confianca_media_percentual": tools_analytics_t(
            "average_confidence"
        ),
        "duracao_media_ms": tools_analytics_t(
            "average_ms"
        ),
        "duracao_minima_ms": tools_analytics_t(
            "minimum_ms"
        ),
        "duracao_maxima_ms": tools_analytics_t(
            "maximum_ms"
        ),
        "p50_ms": "P50 (ms)",
        "p95_ms": "P95 (ms)",
        "p99_ms": "P99 (ms)",
    }

    existentes = {
        coluna: nome
        for coluna, nome in colunas.items()
        if coluna in tabela.columns
    }

    return tabela[list(existentes)].rename(
        columns=existentes
    )


def render_comparacao_periodos(
    comparacao: dict[str, Any],
) -> None:
    """
    Exibe o período atual versus o anterior.
    """
    atual = comparacao.get(
        "periodo_atual",
        {},
    )

    anterior = comparacao.get(
        "periodo_anterior",
        {},
    )

    st.markdown(
        tools_analytics_t(
            "period_comparison"
        )
    )

    col_1, col_2, col_3 = st.columns(3)

    col_1.metric(
        tools_analytics_t("executions"),
        atual.get("execucoes", 0),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_execucoes_percentual",
                0,
            )
        ),
    )

    col_2.metric(
        tools_analytics_t("failures"),
        atual.get("falhas", 0),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_falhas_percentual",
                0,
            )
        ),
        delta_color="inverse",
    )

    col_3.metric(
        tools_analytics_t(
            "average_duration"
        ),
        (
            f"{float(atual.get('duracao_media_ms', 0)):.3f} ms"
        ),
        delta=formatar_delta_percentual(
            comparacao.get(
                "variacao_duracao_percentual",
                0,
            )
        ),
        delta_color="inverse",
    )

    with st.expander(
        tools_analytics_t(
            "detailed_comparison"
        ),
        expanded=False,
    ):
        tabela = pd.DataFrame([
            {
                tools_analytics_t("period"): (
                    tools_analytics_t("current")
                ),
                tools_analytics_t("executions"): atual.get(
                    "execucoes",
                    0,
                ),
                tools_analytics_t("failures"): atual.get(
                    "falhas",
                    0,
                ),
                tools_analytics_t(
                    "average_duration_ms"
                ): atual.get(
                    "duracao_media_ms",
                    0,
                ),
            },
            {
                tools_analytics_t("period"): (
                    tools_analytics_t("previous")
                ),
                tools_analytics_t("executions"): anterior.get(
                    "execucoes",
                    0,
                ),
                tools_analytics_t("failures"): anterior.get(
                    "falhas",
                    0,
                ),
                tools_analytics_t(
                    "average_duration_ms"
                ): anterior.get(
                    "duracao_media_ms",
                    0,
                ),
            },
        ])

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
        )


def render_anomalias_operacionais(
    resultado: dict[str, Any],
) -> None:
    """
    Renderiza alertas e métricas de anomalias.
    """
    st.markdown(
        tools_analytics_t("anomaly_detection")
    )

    if not resultado.get("tem_dados"):
        st.info(
            tools_analytics_t(
                "insufficient_anomaly_data"
            )
        )
        return

    anomalias = resultado.get(
        "anomalias",
        [],
    )

    total = int(
        resultado.get(
            "total_anomalias",
            0,
        )
    )

    maior_severidade = (
        resultado.get(
            "maior_severidade"
        )
        or tools_analytics_t("none")
    )

    atual = resultado.get(
        "periodo_atual",
        {},
    )

    base = resultado.get(
        "linha_base",
        {},
    )

    linha_1 = st.columns(4)

    linha_1[0].metric(
        tools_analytics_t("detected_anomalies"),
        total,
    )

    linha_1[1].metric(
        tools_analytics_t("highest_severity"),
        maior_severidade.title(),
    )

    linha_1[2].metric(
        tools_analytics_t("current_period_failures"),
        int(
            atual.get(
                "falhas",
                0,
            )
        ),
    )

    linha_1[3].metric(
        tools_analytics_t("current_p95"),
        (
            f"{float(atual.get('duracao_p95_ms', 0)):.3f} ms"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        tools_analytics_t("current_failure_rate"),
        (
            f"{float(atual.get('taxa_falhas_percentual', 0)):.2f}%"
        ),
    )

    linha_2[1].metric(
        tools_analytics_t("baseline_failure_rate"),
        (
            f"{float(base.get('taxa_falhas_percentual', 0)):.2f}%"
        ),
    )

    linha_2[2].metric(
        tools_analytics_t("current_confidence"),
        (
            f"{float(atual.get('confianca_media_percentual', 0)):.2f}%"
        ),
    )

    linha_2[3].metric(
        tools_analytics_t("baseline_confidence"),
        (
            f"{float(base.get('confianca_media_percentual', 0)):.2f}%"
        ),
    )

    if not anomalias:
        st.success(
            tools_analytics_t(
                "no_relevant_anomalies"
            )
        )
        return

    contagem_severidade = {
        "critica": 0,
        "alta": 0,
        "media": 0,
        "baixa": 0,
        "informativa": 0,
    }

    for item in anomalias:
        severidade = item.get(
            "severidade",
            "informativa",
        )

        contagem_severidade[
            severidade
        ] = (
            contagem_severidade.get(
                severidade,
                0,
            )
            + 1
        )

    st.markdown(
        tools_analytics_t("anomalies_by_severity")
    )

    colunas = st.columns(5)

    colunas[0].metric(
        tools_analytics_t("critical"),
        contagem_severidade["critica"],
    )

    colunas[1].metric(
        tools_analytics_t("high"),
        contagem_severidade["alta"],
    )

    colunas[2].metric(
        tools_analytics_t("medium"),
        contagem_severidade["media"],
    )

    colunas[3].metric(
        tools_analytics_t("low"),
        contagem_severidade["baixa"],
    )

    colunas[4].metric(
        tools_analytics_t("informational"),
        contagem_severidade[
            "informativa"
        ],
    )

    st.markdown(
        tools_analytics_t("detected_alerts")
    )

    for indice, item in enumerate(
        anomalias,
        start=1,
    ):
        severidade = item.get(
            "severidade",
            "informativa",
        )

        simbolo = {
            "critica": "🔴",
            "alta": "🟠",
            "media": "🟡",
            "baixa": "🔵",
            "informativa": "ℹ️",
        }.get(
            severidade,
            "ℹ️",
        )

        titulo = item.get(
            "titulo",
            tools_analytics_t("anomaly"),
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### {simbolo} {indice}. {titulo}"
            )

            col_1, col_2, col_3 = st.columns(
                [2, 1, 1]
            )

            col_1.markdown(
                item.get(
                    "descricao",
                    "",
                )
            )

            col_2.metric(
                tools_analytics_t(
                    "current_value"
                ),
                item.get(
                    "valor_atual",
                    0,
                ),
            )

            col_3.metric(
                tools_analytics_t(
                    "reference"
                ),
                item.get(
                    "valor_referencia",
                    0,
                ),
            )

            st.caption(
                f"{tools_analytics_t('severity')}: "
                f"{severidade.title()} | "
                f"{tools_analytics_t('metric')}: "
                f"{item.get('metrica', '')}"
            )

            st.info(
                f"{tools_analytics_t('recommendation')}: "
                + str(
                    item.get(
                        "recomendacao",
                        "",
                    )
                )
            )

    outliers = resultado.get(
        "outliers_duracao"
    )

    if (
        outliers is not None
        and not outliers.empty
    ):
        st.markdown(
            tools_analytics_t("outlier_executions")
        )

        tabela_outliers = (
            outliers.copy()
            .rename(
                columns={
                    "indice": tools_analytics_t(
                        "event_index"
                    ),
                    "valor": tools_analytics_t(
                        "duration_ms"
                    ),
                    "score_robusto": tools_analytics_t(
                        "modified_z_score"
                    ),
                }
            )
        )

        st.dataframe(
            tabela_outliers,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander(
        tools_analytics_t(
            "how_detection_works"
        ),
        expanded=False,
    ):
        st.markdown(
            tools_analytics_t(
                "detection_explanation"
            )
        )


def render_tools_analytics_page() -> None:
    """
    Renderiza o Analytics Avançado das Tools.
    """
    try:
        from observability.analytics import (
            calcular_distribuicao_coluna,
            calcular_execucoes_sem_tool,
            calcular_ranking_tools,
            calcular_serie_temporal_analytics,
            comparar_periodos,
            preparar_eventos_analytics,
        )
        from tools.observability import (
            carregar_eventos_tools,
        )
    except ImportError:
        from src.observability.analytics import (
            calcular_distribuicao_coluna,
            calcular_execucoes_sem_tool,
            calcular_ranking_tools,
            calcular_serie_temporal_analytics,
            comparar_periodos,
            preparar_eventos_analytics,
        )
        from src.tools.observability import (
            carregar_eventos_tools,
        )

    st.title(
        tools_analytics_t("title")
    )

    st.caption(
        tools_analytics_t("caption")
    )

    controle_1, controle_2, controle_3 = st.columns(
        [1, 1, 2]
    )

    limite = controle_1.selectbox(
        tools_analytics_t("loaded_events"),
        options=[
            100,
            250,
            500,
            1000,
        ],
        index=1,
        key="tools_analytics_limit",
    )

    periodo_horas = controle_2.selectbox(
        tools_analytics_t("comparison_window"),
        options=[
            24,
            48,
            72,
            168,
        ],
        index=0,
        format_func=lambda valor: (
            f"{valor} {tools_analytics_t('hours')}"
            if valor < 168
            else tools_analytics_t("seven_days")
        ),
        key="tools_analytics_period",
    )

    with controle_3:
        st.write("")

        if st.button(
            tools_analytics_t("refresh"),
            use_container_width=True,
            key="tools_analytics_refresh",
        ):
            st.rerun()

    resultado = carregar_eventos_tools(
        limite=int(limite)
    )

    if not resultado.get("ok"):
        st.error(
            resultado.get(
                "message",
                tools_analytics_t("load_error"),
            )
        )
        return

    df = resultado.get("df")

    if df is None or df.empty:
        st.info(
            tools_analytics_t(
                "insufficient_events"
            )
        )
        return

    base = preparar_eventos_analytics(
        df
    )

    ranking = calcular_ranking_tools(
        base
    )

    sem_tool = calcular_execucoes_sem_tool(
        base
    )

    total_eventos = len(base)

    total_sucesso = int(
        base["sucesso"].sum()
        if "sucesso" in base.columns
        else 0
    )

    total_falhas = max(
        total_eventos - total_sucesso,
        0,
    )

    taxa_sucesso = (
        round(
            (
                total_sucesso
                / total_eventos
            )
            * 100,
            2,
        )
        if total_eventos
        else 0.0
    )

    confianca_media = (
        round(
            float(
                base["confianca"]
                .dropna()
                .mean()
            )
            * 100,
            2,
        )
        if (
            "confianca" in base.columns
            and base["confianca"].notna().any()
        )
        else 0.0
    )

    duracao_media = (
        round(
            float(
                base["duracao_ms"]
                .dropna()
                .mean()
            ),
            3,
        )
        if (
            "duracao_ms" in base.columns
            and base["duracao_ms"].notna().any()
        )
        else 0.0
    )

    try:
        from observability.narrative import (
            gerar_insights_operacionais,
            gerar_texto_narrativa,
        )
    except ImportError:
        from src.observability.narrative import (
            gerar_insights_operacionais,
            gerar_texto_narrativa,
        )

    idioma_interface = tools_analytics_lang()

    insights = gerar_insights_operacionais(
        base,
        horas_comparacao=int(periodo_horas),
        idioma=idioma_interface,
    )

    st.markdown(
        tools_analytics_t(
            "operational_insights"
        )
    )

    saude = insights.get(
        "saude",
        {},
    )

    col_saude_1, col_saude_2 = st.columns(
        [1, 3]
    )

    col_saude_1.metric(
        tools_analytics_t("health_score"),
        f"{saude.get('score', 0):.1f}/100",
    )

    col_saude_2.info(
        insights.get(
            "resumo_executivo",
            tools_analytics_t("no_summary"),
        )
    )

    col_insight_1, col_insight_2 = st.columns(2)

    with col_insight_1:
        st.markdown(
            tools_analytics_t("highlights")
        )

        for item in insights.get(
            "destaques",
            [],
        ):
            st.success(item)

    with col_insight_2:
        st.markdown(
            tools_analytics_t("alerts")
        )

        alertas = insights.get(
            "alertas",
            [],
        )

        if alertas:
            for item in alertas:
                st.warning(item)
        else:
            st.success(
                tools_analytics_t(
                    "no_critical_alert"
                )
            )

    with st.expander(
        tools_analytics_t(
            "technical_recommendations"
        ),
        expanded=False,
    ):
        for item in insights.get(
            "recomendacoes",
            [],
        ):
            st.markdown(
                f"- {item}"
            )

    with st.expander(
        tools_analytics_t(
            "full_narrative"
        ),
        expanded=False,
    ):
        st.markdown(
            gerar_texto_narrativa(
                insights,
                idioma=idioma_interface,
            )
        )

    st.divider()

    try:
        from observability.anomalies import (
            detectar_anomalias_operacionais,
        )
    except ImportError:
        from src.observability.anomalies import (
            detectar_anomalias_operacionais,
        )

    resultado_anomalias = (
        detectar_anomalias_operacionais(
            base,
            horas_periodo_atual=int(
                periodo_horas
            ),
            horas_linha_base=168,
        )
    )

    render_anomalias_operacionais(
        resultado_anomalias
    )

    st.divider()

    st.markdown(
        tools_analytics_t(
            "analytic_overview"
        )
    )

    linha_1 = st.columns(4)

    linha_1[0].metric(
        tools_analytics_t(
            "analysed_events"
        ),
        total_eventos,
    )

    linha_1[1].metric(
        tools_analytics_t(
            "success_rate_metric"
        ),
        f"{taxa_sucesso:.2f}%",
    )

    linha_1[2].metric(
        tools_analytics_t("failures"),
        total_falhas,
    )

    linha_1[3].metric(
        tools_analytics_t(
            "executions_without_tool"
        ),
        (
            f"{sem_tool['total']} "
            f"({sem_tool['percentual']:.2f}%)"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        tools_analytics_t(
            "average_confidence_metric"
        ),
        f"{confianca_media:.2f}%",
    )

    linha_2[1].metric(
        tools_analytics_t(
            "average_duration_metric"
        ),
        f"{duracao_media:.3f} ms",
    )

    linha_2[2].metric(
        tools_analytics_t(
            "distinct_tools"
        ),
        (
            int(
                base["tool_exibicao"]
                .nunique()
            )
            if "tool_exibicao" in base.columns
            else 0
        ),
    )

    linha_2[3].metric(
        tools_analytics_t(
            "unique_users"
        ),
        (
            int(
                base["usuario_id"]
                .dropna()
                .nunique()
            )
            if "usuario_id" in base.columns
            else 0
        ),
    )

    comparacao = comparar_periodos(
        base,
        horas=int(periodo_horas),
    )

    render_comparacao_periodos(
        comparacao
    )

    st.divider()
    st.markdown(
        tools_analytics_t(
            "ranking_performance"
        )
    )

    idioma_interface = tools_analytics_lang()

    ranking_visual = (
        ranking.copy()
        if ranking is not None
        else pd.DataFrame()
    )

    if (
        not ranking_visual.empty
        and "ferramenta" in ranking_visual.columns
    ):
        ranking_visual["ferramenta"] = (
            ranking_visual["ferramenta"].map(
                lambda value: translate_tool_name(
                    value,
                    language=idioma_interface,
                )
            )
        )

    ranking_exibicao = preparar_ranking_exibicao(
        ranking_visual
    )

    if ranking_exibicao.empty:
        st.info(
            tools_analytics_t(
                "no_tool_found"
            )
        )
    else:
        st.dataframe(
            ranking_exibicao,
            use_container_width=True,
            hide_index=True,
        )

        col_grafico_1, col_grafico_2 = st.columns(2)

        with col_grafico_1:
            st.markdown(
                tools_analytics_t(
                    "usage_by_tool"
                )
            )

            ranking_uso = (
                ranking_visual[
                    [
                        "ferramenta",
                        "execucoes",
                    ]
                ]
                .copy()
                .sort_values(
                    "execucoes",
                    ascending=True,
                )
            )

            fig_uso_tools = px.bar(
                ranking_uso,
                x="execucoes",
                y="ferramenta",
                orientation="h",
                text="execucoes",
                color="execucoes",
                color_continuous_scale=[
                    "#172554",
                    "#2563EB",
                    "#38BDF8",
                ],
            )

            fig_uso_tools.update_traces(
                texttemplate="%{x:,.0f}",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    + tools_analytics_t(
                        "executions_hover"
                    )
                    + ": %{x:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig_uso_tools.update_layout(
                xaxis_title=tools_analytics_t(
                    "executions"
                ),
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            aplicar_tema_tools_analytics_chart(
                fig_uso_tools,
                height=max(
                    380,
                    120 + len(ranking_uso) * 46,
                ),
            )

            st.plotly_chart(
                fig_uso_tools,
                width="stretch",
                key="tools_analytics_usage_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

        with col_grafico_2:
            st.markdown(
                tools_analytics_t(
                    "p95_by_tool"
                )
            )

            ranking_p95 = (
                ranking_visual[
                    [
                        "ferramenta",
                        "p95_ms",
                    ]
                ]
                .copy()
                .fillna({
                    "p95_ms": 0,
                })
                .sort_values(
                    "p95_ms",
                    ascending=True,
                )
            )

            fig_p95_tools = px.bar(
                ranking_p95,
                x="p95_ms",
                y="ferramenta",
                orientation="h",
                text="p95_ms",
                color="p95_ms",
                color_continuous_scale=[
                    "#312E81",
                    "#7C3AED",
                    "#F59E0B",
                ],
            )

            fig_p95_tools.update_traces(
                texttemplate="%{x:,.0f} ms",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "P95: %{x:,.2f} ms"
                    "<extra></extra>"
                ),
            )

            fig_p95_tools.update_layout(
                xaxis_title=tools_analytics_t(
                    "p95_latency"
                ),
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            aplicar_tema_tools_analytics_chart(
                fig_p95_tools,
                height=max(
                    380,
                    120 + len(ranking_p95) * 46,
                ),
            )

            st.plotly_chart(
                fig_p95_tools,
                width="stretch",
                key="tools_analytics_p95_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

    st.divider()
    st.markdown(
        tools_analytics_t("distributions")
    )

    col_dist_1, col_dist_2 = st.columns(2)

    distribuicao_intencoes = (
        calcular_distribuicao_coluna(
            base,
            "intencao",
        )
    )

    distribuicao_origens = (
        calcular_distribuicao_coluna(
            base,
            "origem",
        )
    )

    if not distribuicao_intencoes.empty:
        distribuicao_intencoes = (
            distribuicao_intencoes.copy()
        )

        if (
            "intencao"
            in distribuicao_intencoes.columns
        ):
            distribuicao_intencoes["intencao"] = (
                distribuicao_intencoes[
                    "intencao"
                ].map(
                    lambda value: translate_intention(
                        value,
                        language=idioma_interface,
                    )
                )
            )

    if not distribuicao_origens.empty:
        distribuicao_origens = (
            distribuicao_origens.copy()
        )

        if (
            "origem"
            in distribuicao_origens.columns
        ):
            distribuicao_origens["origem"] = (
                distribuicao_origens[
                    "origem"
                ].map(
                    lambda value: translate_origin(
                        value,
                        language=idioma_interface,
                    )
                )
            )

    with col_dist_1:
        st.markdown(
            tools_analytics_t("intentions")
        )

        if not distribuicao_intencoes.empty:
            tabela_intencoes = (
                distribuicao_intencoes.rename(
                    columns={
                        "intencao": tools_analytics_t(
                            "intention"
                        ),
                        "total": tools_analytics_t(
                            "total"
                        ),
                    }
                )
            )

            st.dataframe(
                tabela_intencoes,
                use_container_width=True,
                hide_index=True,
            )

            intencoes_grafico = (
                distribuicao_intencoes.copy()
                .sort_values(
                    "total",
                    ascending=True,
                )
            )

            fig_intencoes = px.bar(
                intencoes_grafico,
                x="total",
                y="intencao",
                orientation="h",
                text="total",
                color="total",
                color_continuous_scale=[
                    "#164E63",
                    "#0891B2",
                    "#22D3EE",
                ],
            )

            fig_intencoes.update_traces(
                texttemplate="%{x:,.0f}",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    + tools_analytics_t("events")
                    + ": %{x:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig_intencoes.update_layout(
                xaxis_title=tools_analytics_t(
                    "events"
                ),
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            aplicar_tema_tools_analytics_chart(
                fig_intencoes,
                height=max(
                    360,
                    120 + len(intencoes_grafico) * 44,
                ),
            )

            st.plotly_chart(
                fig_intencoes,
                width="stretch",
                key="tools_analytics_intentions_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

    with col_dist_2:
        st.markdown(
            tools_analytics_t("origins")
        )

        if not distribuicao_origens.empty:
            tabela_origens = (
                distribuicao_origens.rename(
                    columns={
                        "origem": tools_analytics_t(
                            "origin"
                        ),
                        "total": tools_analytics_t(
                            "total"
                        ),
                    }
                )
            )

            st.dataframe(
                tabela_origens,
                use_container_width=True,
                hide_index=True,
            )

            origens_grafico = (
                distribuicao_origens.copy()
                .sort_values(
                    "total",
                    ascending=True,
                )
            )

            fig_origens = px.bar(
                origens_grafico,
                x="total",
                y="origem",
                orientation="h",
                text="total",
                color="total",
                color_continuous_scale=[
                    "#312E81",
                    "#7C3AED",
                    "#A78BFA",
                ],
            )

            fig_origens.update_traces(
                texttemplate="%{x:,.0f}",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    + tools_analytics_t("events")
                    + ": %{x:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig_origens.update_layout(
                xaxis_title=tools_analytics_t(
                    "events"
                ),
                yaxis_title=None,
                coloraxis_showscale=False,
                showlegend=False,
            )

            aplicar_tema_tools_analytics_chart(
                fig_origens,
                height=max(
                    360,
                    120 + len(origens_grafico) * 44,
                ),
            )

            st.plotly_chart(
                fig_origens,
                width="stretch",
                key="tools_analytics_origins_chart",
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )

    st.divider()
    st.markdown(
        tools_analytics_t(
            "temporal_evolution"
        )
    )

    frequency_options = (
        "hour",
        "day",
        "week",
        "month",
    )

    frequency_labels = {
        "hour": tools_analytics_t("hour"),
        "day": tools_analytics_t("day"),
        "week": tools_analytics_t("week"),
        "month": tools_analytics_t("month"),
    }

    frequencia_label = st.radio(
        tools_analytics_t("grouping"),
        options=frequency_options,
        format_func=lambda value: (
            frequency_labels[value]
        ),
        horizontal=True,
        key="tools_analytics_frequency",
    )

    mapa_frequencia = {
        "hour": "h",
        "day": "D",
        "week": "W",
        "month": "ME",
    }

    serie = calcular_serie_temporal_analytics(
        base,
        mapa_frequencia[
            frequencia_label
        ],
    )

    if serie.empty:
        st.info(
            tools_analytics_t(
                "insufficient_time_series"
            )
        )
    else:
        serie_grafico = serie.copy()

        period_column = tools_analytics_t(
            "period_label"
        )

        serie_grafico[period_column] = (
            pd.to_datetime(
                serie_grafico["criado_em"],
                errors="coerce",
            )
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        serie_plot = (
            serie_grafico[
                [
                    period_column,
                    "execucoes",
                    "sucessos",
                    "falhas",
                ]
            ]
            .rename(
                columns={
                    "execucoes": tools_analytics_t(
                        "executions"
                    ),
                    "sucessos": tools_analytics_t(
                        "successful_executions"
                    ),
                    "falhas": tools_analytics_t(
                        "failed_executions"
                    ),
                }
            )
        )

        fig_evolucao = px.line(
            serie_plot,
            x=period_column,
            y=[
                tools_analytics_t("executions"),
                tools_analytics_t(
                    "successful_executions"
                ),
                tools_analytics_t(
                    "failed_executions"
                ),
            ],
            markers=True,
            color_discrete_sequence=[
                "#38BDF8",
                "#34D399",
                "#F87171",
            ],
        )

        fig_evolucao.update_traces(
            line={
                "width": 3,
            },
            marker={
                "size": 7,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                "%{fullData.name}: %{y:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_evolucao.update_layout(
            xaxis_title=None,
            yaxis_title=tools_analytics_t(
                "events"
            ),
            legend_title_text=None,
            hovermode="x unified",
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "center",
                "x": 0.5,
            },
        )

        fig_evolucao.update_yaxes(
            rangemode="tozero",
        )

        aplicar_tema_tools_analytics_chart(
            fig_evolucao,
            height=450,
        )

        st.plotly_chart(
            fig_evolucao,
            width="stretch",
            key="tools_analytics_evolution_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

        temporal_column_labels = {
            "criado_em": tools_analytics_t(
                "period_label"
            ),
            "execucoes": tools_analytics_t(
                "executions"
            ),
            "sucessos": tools_analytics_t(
                "successful_executions"
            ),
            "falhas": tools_analytics_t(
                "failed_executions"
            ),
            "duracao_media_ms": tools_analytics_t(
                "average_duration_ms"
            ),
            "confianca_media": tools_analytics_t(
                "average_confidence_metric"
            ),
            "usuarios_ativos": tools_analytics_t(
                "unique_users"
            ),
        }

        temporal_columns = {
            column: label
            for column, label
            in temporal_column_labels.items()
            if column in serie_grafico.columns
        }

        tabela_temporal = (
            serie_grafico[
                list(temporal_columns)
            ]
            .rename(
                columns=temporal_columns
            )
            .copy()
        )

        st.dataframe(
            tabela_temporal,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown(
        tools_analytics_t(
            "most_active_users"
        )
    )

    usuarios = (
        base["usuario_id"]
        .fillna(
            tools_analytics_t("no_user")
        )
        .value_counts()
        .rename_axis(
            tools_analytics_t("user")
        )
        .reset_index(
            name=tools_analytics_t("executions")
        )
    )

    usuarios_grafico = usuarios.sort_values(
        tools_analytics_t("executions"),
        ascending=True,
    ).copy()

    fig_usuarios = px.bar(
        usuarios_grafico,
        x=tools_analytics_t("executions"),
        y=tools_analytics_t("user"),
        orientation="h",
        text=tools_analytics_t("executions"),
        color=tools_analytics_t("executions"),
        color_continuous_scale=[
            "#064E3B",
            "#059669",
            "#34D399",
        ],
    )

    fig_usuarios.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            + tools_analytics_t("executions")
            + ": %{x:,.0f}"
            "<extra></extra>"
        ),
    )

    fig_usuarios.update_layout(
        xaxis_title=tools_analytics_t(
            "executions"
        ),
        yaxis_title=None,
        coloraxis_showscale=False,
        showlegend=False,
    )

    aplicar_tema_tools_analytics_chart(
        fig_usuarios,
        height=max(
            380,
            120 + len(usuarios_grafico) * 44,
        ),
    )

    st.plotly_chart(
        fig_usuarios,
        width="stretch",
        key="tools_analytics_active_users_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.dataframe(
        usuarios,
        use_container_width=True,
        hide_index=True,
    )


def audit_tools_analytics_language_packs(
) -> dict[str, dict[str, object]]:
    """
    Audita os pacotes finais já consolidados da página.

    Detecta:
    - chaves ausentes;
    - chaves extras;
    - textos vazios;
    - pacotes inteiros iguais ao inglês;
    - dicionários que ainda compartilham identidade.
    """
    reference = set(
        TOOLS_ANALYTICS_TEXTS[
            "pt"
        ]
    )

    english = dict(
        TOOLS_ANALYTICS_TEXTS[
            "en_us"
        ]
    )

    report: dict[
        str,
        dict[str, object],
    ] = {}

    languages = (
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
    )

    for language in languages:
        texts = TOOLS_ANALYTICS_TEXTS.get(
            language,
            {},
        )

        keys = set(texts)

        report[language] = {
            "total": len(texts),
            "missing": reference - keys,
            "extra": keys - reference,
            "empty": {
                key
                for key, value in texts.items()
                if value is None
                or not str(value).strip()
            },
            "same_as_english": (
                language
                not in {
                    "en_us",
                    "en_gb",
                }
                and dict(texts) == english
            ),
            "object_id": id(texts),
        }

    return report


__all__ = [
    "audit_tools_analytics_language_packs",
    "formatar_delta_percentual",
    "preparar_ranking_exibicao",
    "render_comparacao_periodos",
    "render_anomalias_operacionais",
    "render_tools_analytics_page",
]

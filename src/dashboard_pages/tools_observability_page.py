"""
Operations Center das Tools financeiras da INNA.
"""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

TOOLS_OBSERVABILITY_BG = "#020617"
TOOLS_OBSERVABILITY_TEXT = "#F8FAFC"
TOOLS_OBSERVABILITY_GRID = (
    "rgba(148, 163, 184, 0.16)"
)


TOOLS_OBSERVABILITY_TEXTS = {
    "pt": {
        "page_title": "🛠️ Operations Center — Tools da INNA",
        "page_caption": (
            "Monitoramento operacional, desempenho, uso e "
            "integridade das ferramentas financeiras."
        ),
        "loaded_events": "Eventos carregados",
        "time_grouping": "Agrupamento temporal",
        "hour": "Hora",
        "day": "Dia",
        "refresh": "🔄 Atualizar Operations Center",
        "executive_view": "## Visão executiva",
        "registered_events": "Eventos registrados",
        "executions_today": "Execuções hoje",
        "last_24_hours": "Últimas 24 horas",
        "active_users": "Usuários ativos",
        "success_rate": "Taxa de sucesso",
        "successful_executions": "Execuções com sucesso",
        "failures": "Falhas",
        "average_confidence": "Confiança média",
        "average_duration": "Duração média",
        "minimum_duration": "Duração mínima",
        "p95_duration": "Duração P95",
        "p95_help": (
            "95% das execuções terminaram abaixo deste tempo."
        ),
        "maximum_duration": "Duração máxima",
        "most_used_tool": "### Tool mais utilizada",
        "execution_count": "{count} execução(ões)",
        "no_dominant_tool": "Ainda não há Tool predominante.",
        "last_execution": "### Última execução",
        "no_execution": "Nenhuma execução registrada.",
        "infrastructure_state": "## Estado da infraestrutura",
        "operational_components": (
            "{operational} de {total} componentes operacionais."
        ),
        "no_events": "Ainda não existem eventos para análise.",
        "search_filters": "## Pesquisa e filtros",
        "search_label": (
            "Pesquisar usuário, pergunta, Tool ou intenção"
        ),
        "search_placeholder": (
            "Ex.: demo_user, quanto sobra, orçamento..."
        ),
        "tool": "Ferramenta",
        "origin": "Origem",
        "user": "Usuário",
        "status": "Status",
        "all_feminine": "Todas",
        "all_masculine": "Todos",
        "success": "Sucesso",
        "failure": "Falha",
        "events_found": "{count} evento(s) encontrados.",
        "temporal_evolution": "## Evolução temporal",
        "period": "Período",
        "executions": "Execuções",
        "successes": "Sucessos",
        "events": "Eventos",
        "tool_performance": "## Performance por Tool",
        "active_users_title": "## Usuários mais ativos",
        "searchable_history": "## Histórico pesquisável",
        "export_data": "## Exportar dados",
        "export_csv": "⬇️ Exportar CSV",
        "export_json": "⬇️ Exportar JSON",
        "export_excel": "⬇️ Exportar Excel",
        "date": "Data",
        "question": "Pergunta",
        "intention": "Intenção",
        "confidence": "Confiança",
        "duration": "Duração",
        "message": "Mensagem",
        "error": "Erro",
        "no_tool": "Sem Tool",
        "no_user": "sem_usuario",
        "average_ms": "Média_ms",
        "minimum_ms": "Mínimo_ms",
        "maximum_ms": "Máximo_ms",
        "success_rate_column": "Taxa de sucesso (%)",
    },
    "en_us": {
        "page_title": "🛠️ Operations Center — INNA Tools",
        "page_caption": (
            "Operational monitoring, performance, usage, and "
            "integrity of financial tools."
        ),
        "loaded_events": "Loaded events",
        "time_grouping": "Time grouping",
        "hour": "Hour",
        "day": "Day",
        "refresh": "🔄 Refresh Operations Center",
        "executive_view": "## Executive overview",
        "registered_events": "Recorded events",
        "executions_today": "Executions today",
        "last_24_hours": "Last 24 hours",
        "active_users": "Active users",
        "success_rate": "Success rate",
        "successful_executions": "Successful executions",
        "failures": "Failures",
        "average_confidence": "Average confidence",
        "average_duration": "Average duration",
        "minimum_duration": "Minimum duration",
        "p95_duration": "P95 duration",
        "p95_help": (
            "95% of executions finished below this duration."
        ),
        "maximum_duration": "Maximum duration",
        "most_used_tool": "### Most used tool",
        "execution_count": "{count} execution(s)",
        "no_dominant_tool": "There is no predominant tool yet.",
        "last_execution": "### Latest execution",
        "no_execution": "No execution has been recorded.",
        "infrastructure_state": "## Infrastructure status",
        "operational_components": (
            "{operational} of {total} components are operational."
        ),
        "no_events": "There are no events available for analysis.",
        "search_filters": "## Search and filters",
        "search_label": "Search user, question, tool, or intent",
        "search_placeholder": (
            "Example: demo_user, remaining balance, budget..."
        ),
        "tool": "Tool",
        "origin": "Origin",
        "user": "User",
        "status": "Status",
        "all_feminine": "All",
        "all_masculine": "All",
        "success": "Success",
        "failure": "Failure",
        "events_found": "{count} event(s) found.",
        "temporal_evolution": "## Temporal evolution",
        "period": "Period",
        "executions": "Executions",
        "successes": "Successes",
        "events": "Events",
        "tool_performance": "## Performance by tool",
        "active_users_title": "## Most active users",
        "searchable_history": "## Searchable history",
        "export_data": "## Export data",
        "export_csv": "⬇️ Export CSV",
        "export_json": "⬇️ Export JSON",
        "export_excel": "⬇️ Export Excel",
        "date": "Date",
        "question": "Question",
        "intention": "Intent",
        "confidence": "Confidence",
        "duration": "Duration",
        "message": "Message",
        "error": "Error",
        "no_tool": "No tool",
        "no_user": "no_user",
        "average_ms": "Average_ms",
        "minimum_ms": "Minimum_ms",
        "maximum_ms": "Maximum_ms",
        "success_rate_column": "Success rate (%)",
    },
    "es": {
        "page_title": "🛠️ Centro de Operaciones — Herramientas INNA",
        "page_caption": (
            "Monitoreo operativo, rendimiento, uso e integridad "
            "de las herramientas financieras."
        ),
        "loaded_events": "Eventos cargados",
        "time_grouping": "Agrupación temporal",
        "hour": "Hora",
        "day": "Día",
        "refresh": "🔄 Actualizar Centro de Operaciones",
        "executive_view": "## Visión ejecutiva",
        "registered_events": "Eventos registrados",
        "executions_today": "Ejecuciones de hoy",
        "last_24_hours": "Últimas 24 horas",
        "active_users": "Usuarios activos",
        "success_rate": "Tasa de éxito",
        "successful_executions": "Ejecuciones exitosas",
        "failures": "Fallos",
        "average_confidence": "Confianza media",
        "average_duration": "Duración media",
        "minimum_duration": "Duración mínima",
        "p95_duration": "Duración P95",
        "p95_help": (
            "El 95% de las ejecuciones terminó por debajo "
            "de esta duración."
        ),
        "maximum_duration": "Duración máxima",
        "most_used_tool": "### Herramienta más utilizada",
        "execution_count": "{count} ejecución(es)",
        "no_dominant_tool": "Aún no hay una herramienta predominante.",
        "last_execution": "### Última ejecución",
        "no_execution": "No se ha registrado ninguna ejecución.",
        "infrastructure_state": "## Estado de la infraestructura",
        "operational_components": (
            "{operational} de {total} componentes están operativos."
        ),
        "no_events": "No hay eventos disponibles para analizar.",
        "search_filters": "## Búsqueda y filtros",
        "search_label": (
            "Buscar usuario, pregunta, herramienta o intención"
        ),
        "search_placeholder": (
            "Ej.: demo_user, saldo restante, presupuesto..."
        ),
        "tool": "Herramienta",
        "origin": "Origen",
        "user": "Usuario",
        "status": "Estado",
        "all_feminine": "Todas",
        "all_masculine": "Todos",
        "success": "Éxito",
        "failure": "Fallo",
        "events_found": "{count} evento(s) encontrado(s).",
        "temporal_evolution": "## Evolución temporal",
        "period": "Período",
        "executions": "Ejecuciones",
        "successes": "Éxitos",
        "events": "Eventos",
        "tool_performance": "## Rendimiento por herramienta",
        "active_users_title": "## Usuarios más activos",
        "searchable_history": "## Historial consultable",
        "export_data": "## Exportar datos",
        "export_csv": "⬇️ Exportar CSV",
        "export_json": "⬇️ Exportar JSON",
        "export_excel": "⬇️ Exportar Excel",
        "date": "Fecha",
        "question": "Pregunta",
        "intention": "Intención",
        "confidence": "Confianza",
        "duration": "Duración",
        "message": "Mensaje",
        "error": "Error",
        "no_tool": "Sin herramienta",
        "no_user": "sin_usuario",
        "average_ms": "Media_ms",
        "minimum_ms": "Mínimo_ms",
        "maximum_ms": "Máximo_ms",
        "success_rate_column": "Tasa de éxito (%)",
    },
    "fr": {
        "page_title": "🛠️ Centre des opérations — Outils INNA",
        "page_caption": (
            "Surveillance opérationnelle, performances, utilisation "
            "et intégrité des outils financiers."
        ),
        "loaded_events": "Événements chargés",
        "time_grouping": "Regroupement temporel",
        "hour": "Heure",
        "day": "Jour",
        "refresh": "🔄 Actualiser le centre des opérations",
        "executive_view": "## Vue exécutive",
        "registered_events": "Événements enregistrés",
        "executions_today": "Exécutions aujourd’hui",
        "last_24_hours": "Dernières 24 heures",
        "active_users": "Utilisateurs actifs",
        "success_rate": "Taux de réussite",
        "successful_executions": "Exécutions réussies",
        "failures": "Échecs",
        "average_confidence": "Confiance moyenne",
        "average_duration": "Durée moyenne",
        "minimum_duration": "Durée minimale",
        "p95_duration": "Durée P95",
        "p95_help": (
            "95 % des exécutions se sont terminées sous cette durée."
        ),
        "maximum_duration": "Durée maximale",
        "most_used_tool": "### Outil le plus utilisé",
        "execution_count": "{count} exécution(s)",
        "no_dominant_tool": "Aucun outil prédominant pour le moment.",
        "last_execution": "### Dernière exécution",
        "no_execution": "Aucune exécution enregistrée.",
        "infrastructure_state": "## État de l’infrastructure",
        "operational_components": (
            "{operational} composants opérationnels sur {total}."
        ),
        "no_events": "Aucun événement disponible pour l’analyse.",
        "search_filters": "## Recherche et filtres",
        "search_label": (
            "Rechercher un utilisateur, une question, "
            "un outil ou une intention"
        ),
        "search_placeholder": (
            "Ex. : demo_user, solde restant, budget..."
        ),
        "tool": "Outil",
        "origin": "Origine",
        "user": "Utilisateur",
        "status": "Statut",
        "all_feminine": "Toutes",
        "all_masculine": "Tous",
        "success": "Succès",
        "failure": "Échec",
        "events_found": "{count} événement(s) trouvé(s).",
        "temporal_evolution": "## Évolution temporelle",
        "period": "Période",
        "executions": "Exécutions",
        "successes": "Succès",
        "events": "Événements",
        "tool_performance": "## Performance par outil",
        "active_users_title": "## Utilisateurs les plus actifs",
        "searchable_history": "## Historique consultable",
        "export_data": "## Exporter les données",
        "export_csv": "⬇️ Exporter en CSV",
        "export_json": "⬇️ Exporter en JSON",
        "export_excel": "⬇️ Exporter en Excel",
        "date": "Date",
        "question": "Question",
        "intention": "Intention",
        "confidence": "Confiance",
        "duration": "Durée",
        "message": "Message",
        "error": "Erreur",
        "no_tool": "Aucun outil",
        "no_user": "sans_utilisateur",
        "average_ms": "Moyenne_ms",
        "minimum_ms": "Minimum_ms",
        "maximum_ms": "Maximum_ms",
        "success_rate_column": "Taux de réussite (%)",
    },
}

TOOLS_OBSERVABILITY_TEXTS["en_gb"] = (
    TOOLS_OBSERVABILITY_TEXTS["en_us"]
)

TOOLS_OBSERVABILITY_TEXTS["de"] = {
    "page_title": "🛠️ Betriebszentrum — INNA-Tools",
    "page_caption": (
        "Operative Überwachung, Leistung, Nutzung und "
        "Integrität der Finanzwerkzeuge."
    ),
    "loaded_events": "Geladene Ereignisse",
    "time_grouping": "Zeitliche Gruppierung",
    "hour": "Stunde",
    "day": "Tag",
    "refresh": "🔄 Betriebszentrum aktualisieren",
    "executive_view": "## Übersicht",
    "registered_events": "Erfasste Ereignisse",
    "executions_today": "Ausführungen heute",
    "last_24_hours": "Letzte 24 Stunden",
    "active_users": "Aktive Benutzer",
    "success_rate": "Erfolgsquote",
    "successful_executions": "Erfolgreiche Ausführungen",
    "failures": "Fehler",
    "average_confidence": "Durchschnittliche Konfidenz",
    "average_duration": "Durchschnittliche Dauer",
    "minimum_duration": "Minimale Dauer",
    "p95_duration": "P95-Dauer",
    "p95_help": (
        "95 % der Ausführungen wurden unterhalb "
        "dieser Dauer abgeschlossen."
    ),
    "maximum_duration": "Maximale Dauer",
    "most_used_tool": "### Meistverwendetes Tool",
    "execution_count": "{count} Ausführung(en)",
    "no_dominant_tool": "Noch kein vorherrschendes Tool.",
    "last_execution": "### Letzte Ausführung",
    "no_execution": "Keine Ausführung erfasst.",
    "infrastructure_state": "## Infrastrukturstatus",
    "operational_components": (
        "{operational} von {total} Komponenten sind betriebsbereit."
    ),
    "no_events": "Keine Ereignisse zur Analyse vorhanden.",
    "search_filters": "## Suche und Filter",
    "search_label": (
        "Benutzer, Frage, Tool oder Absicht suchen"
    ),
    "search_placeholder": (
        "Beispiel: demo_user, Restbetrag, Budget..."
    ),
    "tool": "Tool",
    "origin": "Quelle",
    "user": "Benutzer",
    "status": "Status",
    "all_feminine": "Alle",
    "all_masculine": "Alle",
    "success": "Erfolg",
    "failure": "Fehler",
    "events_found": "{count} Ereignis(se) gefunden.",
    "temporal_evolution": "## Zeitliche Entwicklung",
    "period": "Zeitraum",
    "executions": "Ausführungen",
    "successes": "Erfolge",
    "events": "Ereignisse",
    "tool_performance": "## Leistung nach Tool",
    "active_users_title": "## Aktivste Benutzer",
    "searchable_history": "## Durchsuchbarer Verlauf",
    "export_data": "## Daten exportieren",
    "export_csv": "⬇️ CSV exportieren",
    "export_json": "⬇️ JSON exportieren",
    "export_excel": "⬇️ Excel exportieren",
    "date": "Datum",
    "question": "Frage",
    "intention": "Absicht",
    "confidence": "Konfidenz",
    "duration": "Dauer",
    "message": "Nachricht",
    "error": "Fehler",
    "no_tool": "Kein Tool",
    "no_user": "kein_benutzer",
    "average_ms": "Durchschnitt_ms",
    "minimum_ms": "Minimum_ms",
    "maximum_ms": "Maximum_ms",
    "success_rate_column": "Erfolgsquote (%)",
}

TOOLS_OBSERVABILITY_TEXTS["it"] = {
    "page_title": "🛠️ Centro operativo — Strumenti INNA",
    "page_caption": (
        "Monitoraggio operativo, prestazioni, utilizzo e "
        "integrità degli strumenti finanziari."
    ),
    "loaded_events": "Eventi caricati",
    "time_grouping": "Raggruppamento temporale",
    "hour": "Ora",
    "day": "Giorno",
    "refresh": "🔄 Aggiorna Centro operativo",
    "executive_view": "## Panoramica esecutiva",
    "registered_events": "Eventi registrati",
    "executions_today": "Esecuzioni di oggi",
    "last_24_hours": "Ultime 24 ore",
    "active_users": "Utenti attivi",
    "success_rate": "Tasso di successo",
    "successful_executions": "Esecuzioni riuscite",
    "failures": "Errori",
    "average_confidence": "Affidabilità media",
    "average_duration": "Durata media",
    "minimum_duration": "Durata minima",
    "p95_duration": "Durata P95",
    "p95_help": (
        "Il 95% delle esecuzioni è terminato al di sotto "
        "di questa durata."
    ),
    "maximum_duration": "Durata massima",
    "most_used_tool": "### Strumento più utilizzato",
    "execution_count": "{count} esecuzione/i",
    "no_dominant_tool": "Nessuno strumento predominante.",
    "last_execution": "### Ultima esecuzione",
    "no_execution": "Nessuna esecuzione registrata.",
    "infrastructure_state": "## Stato dell’infrastruttura",
    "operational_components": (
        "{operational} componenti operativi su {total}."
    ),
    "no_events": "Nessun evento disponibile per l’analisi.",
    "search_filters": "## Ricerca e filtri",
    "search_label": (
        "Cerca utente, domanda, strumento o intenzione"
    ),
    "search_placeholder": (
        "Esempio: demo_user, saldo residuo, budget..."
    ),
    "tool": "Strumento",
    "origin": "Origine",
    "user": "Utente",
    "status": "Stato",
    "all_feminine": "Tutte",
    "all_masculine": "Tutti",
    "success": "Successo",
    "failure": "Errore",
    "events_found": "{count} evento/i trovato/i.",
    "temporal_evolution": "## Evoluzione temporale",
    "period": "Periodo",
    "executions": "Esecuzioni",
    "successes": "Successi",
    "events": "Eventi",
    "tool_performance": "## Prestazioni per strumento",
    "active_users_title": "## Utenti più attivi",
    "searchable_history": "## Cronologia ricercabile",
    "export_data": "## Esporta dati",
    "export_csv": "⬇️ Esporta CSV",
    "export_json": "⬇️ Esporta JSON",
    "export_excel": "⬇️ Esporta Excel",
    "date": "Data",
    "question": "Domanda",
    "intention": "Intenzione",
    "confidence": "Affidabilità",
    "duration": "Durata",
    "message": "Messaggio",
    "error": "Errore",
    "no_tool": "Nessuno strumento",
    "no_user": "nessun_utente",
    "average_ms": "Media_ms",
    "minimum_ms": "Minimo_ms",
    "maximum_ms": "Massimo_ms",
    "success_rate_column": "Tasso di successo (%)",
}

TOOLS_OBSERVABILITY_TEXTS["ro"] = {
    "page_title": "🛠️ Centru operațional — Instrumente INNA",
    "page_caption": (
        "Monitorizarea operațională, performanța, utilizarea și "
        "integritatea instrumentelor financiare."
    ),
    "loaded_events": "Evenimente încărcate",
    "time_grouping": "Grupare temporală",
    "hour": "Oră",
    "day": "Zi",
    "refresh": "🔄 Actualizează centrul operațional",
    "executive_view": "## Prezentare executivă",
    "registered_events": "Evenimente înregistrate",
    "executions_today": "Execuții astăzi",
    "last_24_hours": "Ultimele 24 de ore",
    "active_users": "Utilizatori activi",
    "success_rate": "Rată de succes",
    "successful_executions": "Execuții reușite",
    "failures": "Eșecuri",
    "average_confidence": "Încredere medie",
    "average_duration": "Durată medie",
    "minimum_duration": "Durată minimă",
    "p95_duration": "Durată P95",
    "p95_help": (
        "95% dintre execuții s-au încheiat sub această durată."
    ),
    "maximum_duration": "Durată maximă",
    "most_used_tool": "### Cel mai utilizat instrument",
    "execution_count": "{count} execuție/execuții",
    "no_dominant_tool": "Nu există încă un instrument predominant.",
    "last_execution": "### Ultima execuție",
    "no_execution": "Nu a fost înregistrată nicio execuție.",
    "infrastructure_state": "## Starea infrastructurii",
    "operational_components": (
        "{operational} din {total} componente sunt operaționale."
    ),
    "no_events": "Nu există evenimente disponibile pentru analiză.",
    "search_filters": "## Căutare și filtre",
    "search_label": (
        "Caută utilizator, întrebare, instrument sau intenție"
    ),
    "search_placeholder": (
        "Exemplu: demo_user, sold rămas, buget..."
    ),
    "tool": "Instrument",
    "origin": "Origine",
    "user": "Utilizator",
    "status": "Stare",
    "all_feminine": "Toate",
    "all_masculine": "Toți",
    "success": "Succes",
    "failure": "Eșec",
    "events_found": "{count} eveniment(e) găsit(e).",
    "temporal_evolution": "## Evoluție temporală",
    "period": "Perioadă",
    "executions": "Execuții",
    "successes": "Succese",
    "events": "Evenimente",
    "tool_performance": "## Performanță după instrument",
    "active_users_title": "## Cei mai activi utilizatori",
    "searchable_history": "## Istoric căutabil",
    "export_data": "## Exportă datele",
    "export_csv": "⬇️ Exportă CSV",
    "export_json": "⬇️ Exportă JSON",
    "export_excel": "⬇️ Exportă Excel",
    "date": "Dată",
    "question": "Întrebare",
    "intention": "Intenție",
    "confidence": "Încredere",
    "duration": "Durată",
    "message": "Mesaj",
    "error": "Eroare",
    "no_tool": "Fără instrument",
    "no_user": "fără_utilizator",
    "average_ms": "Medie_ms",
    "minimum_ms": "Minim_ms",
    "maximum_ms": "Maxim_ms",
    "success_rate_column": "Rată de succes (%)",
}

TOOLS_OBSERVABILITY_TEXTS["ua"] = {
    "page_title": "🛠️ Операційний центр — Інструменти INNA",
    "page_caption": (
        "Операційний моніторинг, продуктивність, використання "
        "та цілісність фінансових інструментів."
    ),
    "loaded_events": "Завантажені події",
    "time_grouping": "Часове групування",
    "hour": "Година",
    "day": "День",
    "refresh": "🔄 Оновити операційний центр",
    "executive_view": "## Операційний огляд",
    "registered_events": "Зареєстровані події",
    "executions_today": "Виконання сьогодні",
    "last_24_hours": "Останні 24 години",
    "active_users": "Активні користувачі",
    "success_rate": "Рівень успіху",
    "successful_executions": "Успішні виконання",
    "failures": "Помилки",
    "average_confidence": "Середня впевненість",
    "average_duration": "Середня тривалість",
    "minimum_duration": "Мінімальна тривалість",
    "p95_duration": "Тривалість P95",
    "p95_help": (
        "95% виконань завершилися швидше за цей час."
    ),
    "maximum_duration": "Максимальна тривалість",
    "most_used_tool": "### Найуживаніший інструмент",
    "execution_count": "{count} виконання",
    "no_dominant_tool": "Переважного інструмента ще немає.",
    "last_execution": "### Останнє виконання",
    "no_execution": "Виконання ще не зареєстровані.",
    "infrastructure_state": "## Стан інфраструктури",
    "operational_components": (
        "{operational} із {total} компонентів працюють."
    ),
    "no_events": "Немає подій для аналізу.",
    "search_filters": "## Пошук і фільтри",
    "search_label": (
        "Пошук користувача, запитання, інструмента або наміру"
    ),
    "search_placeholder": (
        "Приклад: demo_user, залишок, бюджет..."
    ),
    "tool": "Інструмент",
    "origin": "Джерело",
    "user": "Користувач",
    "status": "Статус",
    "all_feminine": "Усі",
    "all_masculine": "Усі",
    "success": "Успіх",
    "failure": "Помилка",
    "events_found": "Знайдено подій: {count}.",
    "temporal_evolution": "## Динаміка в часі",
    "period": "Період",
    "executions": "Виконання",
    "successes": "Успіхи",
    "events": "Події",
    "tool_performance": "## Продуктивність за інструментом",
    "active_users_title": "## Найактивніші користувачі",
    "searchable_history": "## Історія з пошуком",
    "export_data": "## Експорт даних",
    "export_csv": "⬇️ Експортувати CSV",
    "export_json": "⬇️ Експортувати JSON",
    "export_excel": "⬇️ Експортувати Excel",
    "date": "Дата",
    "question": "Запитання",
    "intention": "Намір",
    "confidence": "Впевненість",
    "duration": "Тривалість",
    "message": "Повідомлення",
    "error": "Помилка",
    "no_tool": "Без інструмента",
    "no_user": "без_користувача",
    "average_ms": "Середнє_мс",
    "minimum_ms": "Мінімум_мс",
    "maximum_ms": "Максимум_мс",
    "success_rate_column": "Рівень успіху (%)",
}

TOOLS_OBSERVABILITY_TEXTS["ru"] = {
    "page_title": "🛠️ Операционный центр — Инструменты INNA",
    "page_caption": (
        "Операционный мониторинг, производительность, использование "
        "и целостность финансовых инструментов."
    ),
    "loaded_events": "Загруженные события",
    "time_grouping": "Группировка по времени",
    "hour": "Час",
    "day": "День",
    "refresh": "🔄 Обновить операционный центр",
    "executive_view": "## Операционный обзор",
    "registered_events": "Зарегистрированные события",
    "executions_today": "Выполнения сегодня",
    "last_24_hours": "Последние 24 часа",
    "active_users": "Активные пользователи",
    "success_rate": "Уровень успеха",
    "successful_executions": "Успешные выполнения",
    "failures": "Ошибки",
    "average_confidence": "Средняя уверенность",
    "average_duration": "Средняя длительность",
    "minimum_duration": "Минимальная длительность",
    "p95_duration": "Длительность P95",
    "p95_help": (
        "95% выполнений завершились быстрее этого времени."
    ),
    "maximum_duration": "Максимальная длительность",
    "most_used_tool": "### Самый используемый инструмент",
    "execution_count": "{count} выполнений",
    "no_dominant_tool": "Преобладающего инструмента пока нет.",
    "last_execution": "### Последнее выполнение",
    "no_execution": "Выполнения ещё не зарегистрированы.",
    "infrastructure_state": "## Состояние инфраструктуры",
    "operational_components": (
        "{operational} из {total} компонентов работают."
    ),
    "no_events": "Нет событий для анализа.",
    "search_filters": "## Поиск и фильтры",
    "search_label": (
        "Поиск пользователя, вопроса, инструмента или намерения"
    ),
    "search_placeholder": (
        "Пример: demo_user, остаток, бюджет..."
    ),
    "tool": "Инструмент",
    "origin": "Источник",
    "user": "Пользователь",
    "status": "Статус",
    "all_feminine": "Все",
    "all_masculine": "Все",
    "success": "Успех",
    "failure": "Ошибка",
    "events_found": "Найдено событий: {count}.",
    "temporal_evolution": "## Динамика во времени",
    "period": "Период",
    "executions": "Выполнения",
    "successes": "Успехи",
    "events": "События",
    "tool_performance": "## Производительность по инструментам",
    "active_users_title": "## Самые активные пользователи",
    "searchable_history": "## История с поиском",
    "export_data": "## Экспорт данных",
    "export_csv": "⬇️ Экспортировать CSV",
    "export_json": "⬇️ Экспортировать JSON",
    "export_excel": "⬇️ Экспортировать Excel",
    "date": "Дата",
    "question": "Вопрос",
    "intention": "Намерение",
    "confidence": "Уверенность",
    "duration": "Длительность",
    "message": "Сообщение",
    "error": "Ошибка",
    "no_tool": "Без инструмента",
    "no_user": "без_пользователя",
    "average_ms": "Среднее_мс",
    "minimum_ms": "Минимум_мс",
    "maximum_ms": "Максимум_мс",
    "success_rate_column": "Уровень успеха (%)",
}

TOOLS_OBSERVABILITY_TEXTS["sa"] = {
    "page_title": "🛠️ مركز العمليات — أدوات INNA",
    "page_caption": (
        "مراقبة التشغيل والأداء والاستخدام وسلامة الأدوات المالية."
    ),
    "loaded_events": "الأحداث المحملة",
    "time_grouping": "التجميع الزمني",
    "hour": "ساعة",
    "day": "يوم",
    "refresh": "🔄 تحديث مركز العمليات",
    "executive_view": "## النظرة التنفيذية",
    "registered_events": "الأحداث المسجلة",
    "executions_today": "عمليات التنفيذ اليوم",
    "last_24_hours": "آخر 24 ساعة",
    "active_users": "المستخدمون النشطون",
    "success_rate": "معدل النجاح",
    "successful_executions": "عمليات التنفيذ الناجحة",
    "failures": "الإخفاقات",
    "average_confidence": "متوسط الثقة",
    "average_duration": "متوسط المدة",
    "minimum_duration": "المدة الدنيا",
    "p95_duration": "مدة P95",
    "p95_help": (
        "اكتمل 95٪ من عمليات التنفيذ خلال مدة أقل من هذه."
    ),
    "maximum_duration": "المدة القصوى",
    "most_used_tool": "### الأداة الأكثر استخدامًا",
    "execution_count": "{count} عملية تنفيذ",
    "no_dominant_tool": "لا توجد أداة مهيمنة حتى الآن.",
    "last_execution": "### آخر تنفيذ",
    "no_execution": "لم يتم تسجيل أي تنفيذ.",
    "infrastructure_state": "## حالة البنية التحتية",
    "operational_components": (
        "{operational} من أصل {total} مكونات تعمل."
    ),
    "no_events": "لا توجد أحداث متاحة للتحليل.",
    "search_filters": "## البحث والتصفية",
    "search_label": (
        "البحث عن مستخدم أو سؤال أو أداة أو نية"
    ),
    "search_placeholder": (
        "مثال: demo_user، الرصيد المتبقي، الميزانية..."
    ),
    "tool": "الأداة",
    "origin": "المصدر",
    "user": "المستخدم",
    "status": "الحالة",
    "all_feminine": "الكل",
    "all_masculine": "الكل",
    "success": "نجاح",
    "failure": "فشل",
    "events_found": "تم العثور على {count} حدث.",
    "temporal_evolution": "## التطور الزمني",
    "period": "الفترة",
    "executions": "عمليات التنفيذ",
    "successes": "النجاحات",
    "events": "الأحداث",
    "tool_performance": "## الأداء حسب الأداة",
    "active_users_title": "## المستخدمون الأكثر نشاطًا",
    "searchable_history": "## السجل القابل للبحث",
    "export_data": "## تصدير البيانات",
    "export_csv": "⬇️ تصدير CSV",
    "export_json": "⬇️ تصدير JSON",
    "export_excel": "⬇️ تصدير Excel",
    "date": "التاريخ",
    "question": "السؤال",
    "intention": "النية",
    "confidence": "الثقة",
    "duration": "المدة",
    "message": "الرسالة",
    "error": "الخطأ",
    "no_tool": "بدون أداة",
    "no_user": "بدون_مستخدم",
    "average_ms": "المتوسط_مللي_ثانية",
    "minimum_ms": "الحد_الأدنى_مللي_ثانية",
    "maximum_ms": "الحد_الأقصى_مللي_ثانية",
    "success_rate_column": "معدل النجاح (%)",
}

TOOLS_OBSERVABILITY_TEXTS["ch"] = (
    TOOLS_OBSERVABILITY_TEXTS["de"]
)


# Ajustes finais dos textos visíveis conforme o seletor.
TOOLS_OBSERVABILITY_TEXTS["pt"].update(
    {
        "page_title": (
            "🛠️ Centro de Operações — "
            "Ferramentas da INNA"
        ),
    }
)

TOOLS_OBSERVABILITY_TEXTS["en_us"].update(
    {
        "page_title": (
            "🛠️ Operations Center — "
            "INNA Tools"
        ),
    }
)

TOOLS_OBSERVABILITY_TEXTS["en_gb"] = dict(
    TOOLS_OBSERVABILITY_TEXTS["en_us"]
)

TOOLS_OBSERVABILITY_TEXTS["fr"].update(
    {
        "minimum_ms": "Minimum (ms)",
        "maximum_ms": "Maximum (ms)",
    }
)

TOOLS_OBSERVABILITY_TEXTS["de"].update(
    {
        "minimum_ms": "Minimum (ms)",
        "maximum_ms": "Maximum (ms)",
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TOOLS_OBSERVABILITY_TEXTS["ch"] = dict(
    TOOLS_OBSERVABILITY_TEXTS["de"]
)


def tools_observability_lang() -> str:
    language = st.session_state.get(
        "dashboard_interface_lang",
        "pt",
    )

    aliases = {
        "en": "en_us",
        "en-US": "en_us",
        "en-GB": "en_gb",
        "English (US)": "en_us",
        "English (UK)": "en_gb",
    }

    language = aliases.get(
        str(language),
        str(language),
    )

    if language in TOOLS_OBSERVABILITY_TEXTS:
        return language

    return "pt"


def tools_observability_t(
    key: str,
    default: str | None = None,
) -> str:
    language = tools_observability_lang()

    language_texts = TOOLS_OBSERVABILITY_TEXTS.get(
        language,
        {},
    )

    if key in language_texts:
        return language_texts[key]

    portuguese_texts = TOOLS_OBSERVABILITY_TEXTS["pt"]

    if key in portuguese_texts:
        return portuguese_texts[key]

    if default is not None:
        return default

    return key



def aplicar_tema_tools_observability_chart(
    fig,
    *,
    height=420,
):
    """Aplica o tema visual da Observabilidade Tools."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=TOOLS_OBSERVABILITY_BG,
        plot_bgcolor=TOOLS_OBSERVABILITY_BG,
        font={
            "color": TOOLS_OBSERVABILITY_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": TOOLS_OBSERVABILITY_TEXT,
        },
        margin={
            "l": 30,
            "r": 42,
            "t": 18,
            "b": 38,
        },
        height=height,
    )

    fig.update_xaxes(
        color=TOOLS_OBSERVABILITY_TEXT,
        gridcolor=TOOLS_OBSERVABILITY_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    fig.update_yaxes(
        color=TOOLS_OBSERVABILITY_TEXT,
        gridcolor=TOOLS_OBSERVABILITY_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    return fig


try:
    from observability.metrics import (
        calcular_metricas_executivas,
    )
except ImportError:
    from src.observability.metrics import (
        calcular_metricas_executivas,
    )



TOOLS_DYNAMIC_TEXTS = {
    "pt": {
        "weekly_capacity": "Cálculo de capacidade semanal",
        "reserve_simulation": "Simulação de formação de reserva",
        "tool_success": "Ferramenta executada com sucesso.",
        "tool_missing_data": (
            "Ainda faltam dados para executar a ferramenta."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Extensão pgvector",
        "tools_events_table": "Tabela de eventos das Tools",
        "rag_vector_base": "Base vetorial RAG",
        "persistent_memory": "Memória persistente",
        "gemini_configuration": "Configuração Gemini",
        "operational_connection": "Conexão operacional.",
        "active_extension": "Extensão ativa.",
        "tools_table_available": (
            "Tabela tools_eventos_inna disponível."
        ),
        "rag_table_available": (
            "Tabela chunks_embeddings_rag disponível."
        ),
        "memory_table_available": (
            "Tabela memoria_usuarios_inna disponível."
        ),
        "configured_key": "Chave configurada.",
    },
    "en_us": {
        "weekly_capacity": "Weekly capacity calculation",
        "reserve_simulation": "Emergency reserve simulation",
        "tool_success": "Tool executed successfully.",
        "tool_missing_data": (
            "More data is required to execute the tool."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "pgvector extension",
        "tools_events_table": "Tools events table",
        "rag_vector_base": "RAG vector database",
        "persistent_memory": "Persistent memory",
        "gemini_configuration": "Gemini configuration",
        "operational_connection": "Operational connection.",
        "active_extension": "Extension active.",
        "tools_table_available": (
            "The tools_eventos_inna table is available."
        ),
        "rag_table_available": (
            "The chunks_embeddings_rag table is available."
        ),
        "memory_table_available": (
            "The memoria_usuarios_inna table is available."
        ),
        "configured_key": "Key configured.",
    },
    "es": {
        "weekly_capacity": "Cálculo de capacidad semanal",
        "reserve_simulation": "Simulación de creación de reserva",
        "tool_success": "Herramienta ejecutada correctamente.",
        "tool_missing_data": (
            "Aún faltan datos para ejecutar la herramienta."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Extensión pgvector",
        "tools_events_table": "Tabla de eventos de las herramientas",
        "rag_vector_base": "Base vectorial RAG",
        "persistent_memory": "Memoria persistente",
        "gemini_configuration": "Configuración de Gemini",
        "operational_connection": "Conexión operativa.",
        "active_extension": "Extensión activa.",
        "tools_table_available": (
            "La tabla tools_eventos_inna está disponible."
        ),
        "rag_table_available": (
            "La tabla chunks_embeddings_rag está disponible."
        ),
        "memory_table_available": (
            "La tabla memoria_usuarios_inna está disponible."
        ),
        "configured_key": "Clave configurada.",
    },
    "fr": {
        "weekly_capacity": "Calcul de la capacité hebdomadaire",
        "reserve_simulation": "Simulation de création d’une réserve",
        "tool_success": "Outil exécuté avec succès.",
        "tool_missing_data": (
            "Des données supplémentaires sont nécessaires "
            "pour exécuter l’outil."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Extension pgvector",
        "tools_events_table": "Table des événements des outils",
        "rag_vector_base": "Base vectorielle RAG",
        "persistent_memory": "Mémoire persistante",
        "gemini_configuration": "Configuration Gemini",
        "operational_connection": "Connexion opérationnelle.",
        "active_extension": "Extension active.",
        "tools_table_available": (
            "La table tools_eventos_inna est disponible."
        ),
        "rag_table_available": (
            "La table chunks_embeddings_rag est disponible."
        ),
        "memory_table_available": (
            "La table memoria_usuarios_inna est disponible."
        ),
        "configured_key": "Clé configurée.",
    },
    "de": {
        "weekly_capacity": "Berechnung der Wochenkapazität",
        "reserve_simulation": "Simulation des Reserveaufbaus",
        "tool_success": "Tool erfolgreich ausgeführt.",
        "tool_missing_data": (
            "Für die Ausführung des Tools werden weitere Daten benötigt."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "pgvector-Erweiterung",
        "tools_events_table": "Ereignistabelle der Tools",
        "rag_vector_base": "RAG-Vektordatenbank",
        "persistent_memory": "Persistenter Speicher",
        "gemini_configuration": "Gemini-Konfiguration",
        "operational_connection": "Verbindung betriebsbereit.",
        "active_extension": "Erweiterung aktiv.",
        "tools_table_available": (
            "Die Tabelle tools_eventos_inna ist verfügbar."
        ),
        "rag_table_available": (
            "Die Tabelle chunks_embeddings_rag ist verfügbar."
        ),
        "memory_table_available": (
            "Die Tabelle memoria_usuarios_inna ist verfügbar."
        ),
        "configured_key": "Schlüssel konfiguriert.",
    },
    "it": {
        "weekly_capacity": "Calcolo della capacità settimanale",
        "reserve_simulation": "Simulazione della creazione della riserva",
        "tool_success": "Strumento eseguito correttamente.",
        "tool_missing_data": (
            "Sono necessari altri dati per eseguire lo strumento."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Estensione pgvector",
        "tools_events_table": "Tabella degli eventi degli strumenti",
        "rag_vector_base": "Database vettoriale RAG",
        "persistent_memory": "Memoria persistente",
        "gemini_configuration": "Configurazione Gemini",
        "operational_connection": "Connessione operativa.",
        "active_extension": "Estensione attiva.",
        "tools_table_available": (
            "La tabella tools_eventos_inna è disponibile."
        ),
        "rag_table_available": (
            "La tabella chunks_embeddings_rag è disponibile."
        ),
        "memory_table_available": (
            "La tabella memoria_usuarios_inna è disponibile."
        ),
        "configured_key": "Chiave configurata.",
    },
    "ro": {
        "weekly_capacity": "Calculul capacității săptămânale",
        "reserve_simulation": "Simularea constituirii rezervei",
        "tool_success": "Instrument executat cu succes.",
        "tool_missing_data": (
            "Sunt necesare date suplimentare pentru executarea instrumentului."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Extensie pgvector",
        "tools_events_table": "Tabelul evenimentelor instrumentelor",
        "rag_vector_base": "Bază vectorială RAG",
        "persistent_memory": "Memorie persistentă",
        "gemini_configuration": "Configurare Gemini",
        "operational_connection": "Conexiune operațională.",
        "active_extension": "Extensie activă.",
        "tools_table_available": (
            "Tabelul tools_eventos_inna este disponibil."
        ),
        "rag_table_available": (
            "Tabelul chunks_embeddings_rag este disponibil."
        ),
        "memory_table_available": (
            "Tabelul memoria_usuarios_inna este disponibil."
        ),
        "configured_key": "Cheie configurată.",
    },
    "ua": {
        "weekly_capacity": "Розрахунок тижневої спроможності",
        "reserve_simulation": "Моделювання формування резерву",
        "tool_success": "Інструмент успішно виконано.",
        "tool_missing_data": (
            "Для виконання інструмента потрібні додаткові дані."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Розширення pgvector",
        "tools_events_table": "Таблиця подій інструментів",
        "rag_vector_base": "Векторна база RAG",
        "persistent_memory": "Постійна пам’ять",
        "gemini_configuration": "Конфігурація Gemini",
        "operational_connection": "З’єднання працює.",
        "active_extension": "Розширення активне.",
        "tools_table_available": (
            "Таблиця tools_eventos_inna доступна."
        ),
        "rag_table_available": (
            "Таблиця chunks_embeddings_rag доступна."
        ),
        "memory_table_available": (
            "Таблиця memoria_usuarios_inna доступна."
        ),
        "configured_key": "Ключ налаштовано.",
    },
    "ru": {
        "weekly_capacity": "Расчёт недельной возможности",
        "reserve_simulation": "Моделирование формирования резерва",
        "tool_success": "Инструмент успешно выполнен.",
        "tool_missing_data": (
            "Для выполнения инструмента требуются дополнительные данные."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "Расширение pgvector",
        "tools_events_table": "Таблица событий инструментов",
        "rag_vector_base": "Векторная база RAG",
        "persistent_memory": "Постоянная память",
        "gemini_configuration": "Конфигурация Gemini",
        "operational_connection": "Соединение работает.",
        "active_extension": "Расширение активно.",
        "tools_table_available": (
            "Таблица tools_eventos_inna доступна."
        ),
        "rag_table_available": (
            "Таблица chunks_embeddings_rag доступна."
        ),
        "memory_table_available": (
            "Таблица memoria_usuarios_inna доступна."
        ),
        "configured_key": "Ключ настроен.",
    },
    "sa": {
        "weekly_capacity": "حساب القدرة الأسبوعية",
        "reserve_simulation": "محاكاة تكوين الاحتياطي",
        "tool_success": "تم تنفيذ الأداة بنجاح.",
        "tool_missing_data": (
            "يلزم توفير بيانات إضافية لتنفيذ الأداة."
        ),
        "postgresql_neon": "PostgreSQL / Neon",
        "pgvector_extension": "امتداد pgvector",
        "tools_events_table": "جدول أحداث الأدوات",
        "rag_vector_base": "قاعدة المتجهات RAG",
        "persistent_memory": "الذاكرة الدائمة",
        "gemini_configuration": "إعداد Gemini",
        "operational_connection": "الاتصال يعمل.",
        "active_extension": "الامتداد نشط.",
        "tools_table_available": (
            "الجدول tools_eventos_inna متاح."
        ),
        "rag_table_available": (
            "الجدول chunks_embeddings_rag متاح."
        ),
        "memory_table_available": (
            "الجدول memoria_usuarios_inna متاح."
        ),
        "configured_key": "تم إعداد المفتاح.",
    },
}

TOOLS_DYNAMIC_TEXTS["en_gb"] = (
    TOOLS_DYNAMIC_TEXTS["en_us"]
)

TOOLS_DYNAMIC_TEXTS["ch"] = (
    TOOLS_DYNAMIC_TEXTS["de"]
)


TOOLS_DYNAMIC_KEYS = {
    "Cálculo de capacidade semanal": "weekly_capacity",
    "calcular_capacidade_semanal": "weekly_capacity",
    "Simulação de formação de reserva": "reserve_simulation",
    "simular_formacao_reserva": "reserve_simulation",
    "Ferramenta executada com sucesso.": "tool_success",
    "Ainda faltam dados para executar a ferramenta.": (
        "tool_missing_data"
    ),
    "PostgreSQL / Neon": "postgresql_neon",
    "Extensão pgvector": "pgvector_extension",
    "Tabela de eventos das Tools": "tools_events_table",
    "Base vetorial RAG": "rag_vector_base",
    "Memória persistente": "persistent_memory",
    "Configuração Gemini": "gemini_configuration",
    "Conexão operacional.": "operational_connection",
    "Extensão ativa.": "active_extension",
    "Tabela tools_eventos_inna disponível.": (
        "tools_table_available"
    ),
    "Tabela chunks_embeddings_rag disponível.": (
        "rag_table_available"
    ),
    "Tabela memoria_usuarios_inna disponível.": (
        "memory_table_available"
    ),
    "Chave configurada.": "configured_key",
}


def tools_translate_dynamic(
    value: Any,
) -> str:
    if value is None or pd.isna(value):
        return ""

    original = str(value).strip()
    key = TOOLS_DYNAMIC_KEYS.get(
        original
    )

    if key is None:
        return original

    language = tools_observability_lang()

    texts = TOOLS_DYNAMIC_TEXTS.get(
        language,
        TOOLS_DYNAMIC_TEXTS["pt"],
    )

    return texts.get(
        key,
        original,
    )


def calcular_taxa_sucesso(
    total_sucesso: int,
    total_executadas: int,
) -> float:
    if total_executadas <= 0:
        return 0.0

    return round(
        (total_sucesso / total_executadas) * 100,
        2,
    )


def preparar_ranking_tools(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    base = df.copy()

    base["tool_label"] = (
        base["tool_label"]
        .fillna(base["tool_nome"])
        .fillna("Sem Tool")
    )

    ranking = (
        base.groupby("tool_label")
        .agg(
            Execuções=("id", "count"),
            Sucessos=("sucesso", "sum"),
            Falhas=(
                "sucesso",
                lambda valores: int(
                    (~valores.astype(bool)).sum()
                ),
            ),
            Média_ms=("duracao_ms", "mean"),
            Mínimo_ms=("duracao_ms", "min"),
            Máximo_ms=("duracao_ms", "max"),
        )
        .reset_index()
        .rename(
            columns={
                "tool_label": "Ferramenta",
            }
        )
    )

    ranking["Ferramenta"] = ranking[
        "Ferramenta"
    ].map(
        tools_translate_dynamic
    )

    ranking["Taxa de sucesso (%)"] = ranking.apply(
        lambda row: calcular_taxa_sucesso(
            int(row["Sucessos"]),
            int(row["Execuções"]),
        ),
        axis=1,
    )

    for coluna in [
        "Média_ms",
        "Mínimo_ms",
        "Máximo_ms",
    ]:
        ranking[coluna] = (
            ranking[coluna]
            .fillna(0)
            .round(3)
        )

    return ranking.sort_values(
        by=["Execuções", "Taxa de sucesso (%)"],
        ascending=[False, False],
    ).reset_index(drop=True)


def preparar_serie_temporal(
    df: pd.DataFrame,
    frequencia: str,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    temporal = df.copy()

    temporal["criado_em"] = pd.to_datetime(
        temporal["criado_em"],
        errors="coerce",
        utc=True,
    )

    temporal = temporal.dropna(
        subset=["criado_em"]
    )

    if frequencia == "Hora":
        temporal["Período"] = (
            temporal["criado_em"]
            .dt.floor("h")
            .dt.strftime("%d/%m %H:00")
        )
    else:
        temporal["Período"] = (
            temporal["criado_em"]
            .dt.floor("D")
            .dt.strftime("%d/%m/%Y")
        )

    return (
        temporal.groupby("Período")
        .agg(
            Execuções=("id", "count"),
            Sucessos=("sucesso", "sum"),
            Duração_média_ms=(
                "duracao_ms",
                "mean",
            ),
        )
        .reset_index()
    )


def preparar_eventos_exibicao(
    df: pd.DataFrame,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    tabela = df.copy()

    tabela["Ferramenta"] = (
        tabela["tool_label"]
        .fillna(tabela["tool_nome"])
        .fillna(
            tools_observability_t(
                "no_tool"
            )
        )
        .map(
            tools_translate_dynamic
        )
    )

    if "mensagem" in tabela.columns:
        tabela["mensagem"] = tabela[
            "mensagem"
        ].map(
            tools_translate_dynamic
        )

    tabela["Status"] = tabela["sucesso"].map({
        True: tools_observability_t(
            "success"
        ),
        False: tools_observability_t(
            "failure"
        ),
    })

    tabela["Confiança"] = (
        tabela["confianca"]
        .fillna(0)
        .apply(
            lambda valor: f"{float(valor) * 100:.0f}%"
        )
    )

    tabela["Duração"] = (
        tabela["duracao_ms"]
        .fillna(0)
        .apply(
            lambda valor: f"{float(valor):.3f} ms"
        )
    )

    tabela["Data"] = pd.to_datetime(
        tabela["criado_em"],
        errors="coerce",
    ).dt.strftime("%d/%m/%Y %H:%M:%S")

    colunas = [
        "Data",
        "usuario_id",
        "pergunta",
        "Ferramenta",
        "intencao",
        "Confiança",
        "Status",
        "Duração",
        "origem",
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
            "usuario_id": "Usuário",
            "pergunta": "Pergunta",
            "intencao": "Intenção",
            "origem": "Origem",
            "mensagem": "Mensagem",
            "erro": "Erro",
        }
    )


def gerar_excel(
    df_eventos: pd.DataFrame,
    df_ranking: pd.DataFrame,
) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        df_eventos.to_excel(
            writer,
            sheet_name=tools_observability_t("events"),
            index=False,
        )

        df_ranking.to_excel(
            writer,
            sheet_name="Ranking",
            index=False,
        )

    return output.getvalue()


def render_metricas_executivas(
    df: pd.DataFrame,
) -> dict:
    """
    Renderiza os KPIs executivos do Operations Center.
    """
    metricas = calcular_metricas_executivas(
        df
    )

    st.markdown(tools_observability_t("executive_view"))

    linha_1 = st.columns(4)

    linha_1[0].metric(
        tools_observability_t("registered_events"),
        metricas["total_eventos"],
    )

    linha_1[1].metric(
        tools_observability_t("executions_today"),
        metricas["execucoes_hoje"],
    )

    linha_1[2].metric(
        tools_observability_t("last_24_hours"),
        metricas["execucoes_ultimas_24h"],
    )

    linha_1[3].metric(
        tools_observability_t("active_users"),
        metricas["usuarios_ativos"],
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        tools_observability_t("success_rate"),
        (
            f"{metricas['taxa_sucesso_percentual']:.2f}%"
        ),
    )

    linha_2[1].metric(
        tools_observability_t("successful_executions"),
        metricas["total_sucesso"],
    )

    linha_2[2].metric(
        tools_observability_t("failures"),
        metricas["total_falhas"],
    )

    linha_2[3].metric(
        tools_observability_t("average_confidence"),
        (
            f"{metricas['confianca_media_percentual']:.2f}%"
        ),
    )

    linha_3 = st.columns(4)

    linha_3[0].metric(
        tools_observability_t("average_duration"),
        (
            f"{metricas['duracao_media_ms']:.3f} ms"
        ),
    )

    linha_3[1].metric(
        tools_observability_t("minimum_duration"),
        (
            f"{metricas['duracao_minima_ms']:.3f} ms"
        ),
    )

    linha_3[2].metric(
        tools_observability_t("p95_duration"),
        (
            f"{metricas['duracao_p95_ms']:.3f} ms"
        ),
        help=tools_observability_t(
            "p95_help"
        ),
    )

    linha_3[3].metric(
        tools_observability_t("maximum_duration"),
        (
            f"{metricas['duracao_maxima_ms']:.3f} ms"
        ),
    )

    tool_top = metricas.get(
        "tool_mais_utilizada",
        {},
    )

    ultima_execucao = metricas.get(
        "ultima_execucao"
    )

    col_destaque_1, col_destaque_2 = st.columns(2)

    with col_destaque_1:
        st.markdown(tools_observability_t("most_used_tool"))

        if tool_top.get("nome"):
            st.success(
                tools_translate_dynamic(
                    tool_top["nome"]
                )
                + " — "
                + tools_observability_t(
                    "execution_count"
                ).format(
                    count=tool_top["total"]
                )
            )
        else:
            st.info(
                tools_observability_t(
                    "no_dominant_tool"
                )
            )

    with col_destaque_2:
        st.markdown(tools_observability_t("last_execution"))

        if ultima_execucao:
            data_formatada = pd.to_datetime(
                ultima_execucao,
                errors="coerce",
            )

            if pd.notna(data_formatada):
                st.info(
                    data_formatada.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                )
            else:
                st.info(str(ultima_execucao))
        else:
            st.info(
                tools_observability_t(
                    "no_execution"
                )
            )

    return metricas


def render_status_infraestrutura(
    resultado_status: dict[str, Any],
) -> None:
    st.markdown(tools_observability_t("infrastructure_state"))

    status = resultado_status.get(
        "status",
        {},
    )

    total = resultado_status.get(
        "total_componentes",
        0,
    )

    operacionais = resultado_status.get(
        "total_operacionais",
        0,
    )

    st.progress(
        operacionais / total
        if total
        else 0
    )

    st.caption(
        tools_observability_t(
            "operational_components"
        ).format(
            operational=operacionais,
            total=total,
        )
    )

    colunas = st.columns(3)

    for indice, item in enumerate(
        status.values()
    ):
        coluna = colunas[
            indice % len(colunas)
        ]

        simbolo = "🟢" if item["ok"] else "🔴"

        label_traduzido = (
            tools_translate_dynamic(
                item["label"]
            )
        )

        mensagem_traduzida = (
            tools_translate_dynamic(
                item["message"]
            )
        )

        coluna.markdown(
            f"**{simbolo} {label_traduzido}**"
        )

        coluna.caption(
            mensagem_traduzida
        )


def render_tools_observability_page() -> None:
    try:
        from tools.observability import (
            carregar_eventos_tools,
            carregar_resumo_tools,
            carregar_status_infraestrutura,
        )
    except ImportError:
        from src.tools.observability import (
            carregar_eventos_tools,
            carregar_resumo_tools,
            carregar_status_infraestrutura,
        )

    st.title(tools_observability_t("page_title"))

    st.caption(
        tools_observability_t(
            "page_caption"
        )
    )

    controle_1, controle_2, controle_3 = st.columns(
        [1, 1, 2]
    )

    limite = controle_1.selectbox(
        tools_observability_t(
            "loaded_events"
        ),
        [50, 100, 250, 500, 1000],
        index=1,
    )

    frequencia_id = controle_2.selectbox(
        tools_observability_t(
            "time_grouping"
        ),
        ["hour", "day"],
        format_func=lambda value: (
            tools_observability_t(value)
        ),
    )

    frequencia = (
        "Hora"
        if frequencia_id == "hour"
        else "Dia"
    )

    with controle_3:
        st.write("")

        if st.button(
            tools_observability_t(
                "refresh"
            ),
            use_container_width=True,
        ):
            st.rerun()

    resumo_resultado = carregar_resumo_tools()
    eventos_resultado = carregar_eventos_tools(
        limite=int(limite)
    )

    if not resumo_resultado.get("ok"):
        st.error(resumo_resultado["message"])
        return

    if not eventos_resultado.get("ok"):
        st.error(eventos_resultado["message"])
        return

    df = eventos_resultado.get("df")

    if df is None:
        df = pd.DataFrame()

    render_metricas_executivas(
        df
    )

    st.divider()

    status_resultado = (
        carregar_status_infraestrutura()
    )

    render_status_infraestrutura(
        status_resultado
    )

    if df.empty:
        st.info(
            tools_observability_t(
                "no_events"
            )
        )
        return

    st.divider()
    st.markdown(tools_observability_t("search_filters"))

    pesquisa = st.text_input(
        tools_observability_t(
            "search_label"
        ),
        placeholder=tools_observability_t(
            "search_placeholder"
        ),
    )

    filtro_1, filtro_2, filtro_3 = st.columns(3)

    ferramentas = sorted(
        df["tool_label"]
        .fillna(df["tool_nome"])
        .dropna()
        .unique()
        .tolist()
    )

    origens = sorted(
        df["origem"]
        .dropna()
        .unique()
        .tolist()
    )

    usuarios = sorted(
        df["usuario_id"]
        .dropna()
        .unique()
        .tolist()
    )

    ferramenta = filtro_1.selectbox(
        tools_observability_t("tool"),
        ["__all__"] + ferramentas,
        format_func=lambda value: (
            tools_observability_t(
                "all_feminine"
            )
            if value == "__all__"
            else tools_translate_dynamic(
                value
            )
        ),
    )

    origem = filtro_2.selectbox(
        tools_observability_t("origin"),
        ["__all__"] + origens,
        format_func=lambda value: (
            tools_observability_t(
                "all_feminine"
            )
            if value == "__all__"
            else value
        ),
    )

    usuario = filtro_3.selectbox(
        tools_observability_t("user"),
        ["__all__"] + usuarios,
        format_func=lambda value: (
            tools_observability_t(
                "all_masculine"
            )
            if value == "__all__"
            else value
        ),
    )

    status = st.radio(
        tools_observability_t("status"),
        ["all", "success", "failure"],
        format_func=lambda value: (
            tools_observability_t(
                {
                    "all": "all_masculine",
                    "success": "success",
                    "failure": "failure",
                }[value]
            )
        ),
        horizontal=True,
    )

    filtrado = df.copy()

    if pesquisa.strip():
        termo = pesquisa.strip().lower()

        colunas_busca = [
            coluna
            for coluna in [
                "usuario_id",
                "pergunta",
                "tool_nome",
                "tool_label",
                "intencao",
            ]
            if coluna in filtrado.columns
        ]

        mascara = pd.Series(
            False,
            index=filtrado.index,
        )

        for coluna in colunas_busca:
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

        filtrado = filtrado[mascara]

    labels = filtrado[
        "tool_label"
    ].fillna(
        filtrado["tool_nome"]
    )

    if ferramenta != "__all__":
        filtrado = filtrado[
            labels == ferramenta
        ]

    if origem != "__all__":
        filtrado = filtrado[
            filtrado["origem"] == origem
        ]

    if usuario != "__all__":
        filtrado = filtrado[
            filtrado["usuario_id"] == usuario
        ]

    if status == "success":
        filtrado = filtrado[
            filtrado["sucesso"].eq(True)
        ]

    elif status == "failure":
        filtrado = filtrado[
            filtrado["sucesso"].eq(False)
        ]

    st.caption(
        tools_observability_t(
            "events_found"
        ).format(
            count=len(filtrado)
        )
    )

    st.divider()
    st.markdown(tools_observability_t("temporal_evolution"))

    serie_temporal = preparar_serie_temporal(
        filtrado,
        frequencia,
    )

    if not serie_temporal.empty:
        serie_grafico = (
            serie_temporal[
                [
                    "Período",
                    "Execuções",
                    "Sucessos",
                ]
            ]
            .copy()
        )

        period_label = tools_observability_t(
            "period"
        )
        executions_label = tools_observability_t(
            "executions"
        )
        successes_label = tools_observability_t(
            "successes"
        )

        serie_grafico = serie_grafico.rename(
            columns={
                "Período": period_label,
                "Execuções": executions_label,
                "Sucessos": successes_label,
            }
        )

        fig_evolucao = px.line(
            serie_grafico,
            x=period_label,
            y=[
                executions_label,
                successes_label,
            ],
            markers=True,
            color_discrete_sequence=[
                "#38BDF8",
                "#34D399",
            ],
        )

        fig_evolucao.update_traces(
            line={
                "width": 3,
            },
            marker={
                "size": 8,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                "%{fullData.name}: %{y:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_evolucao.update_layout(
            xaxis_title=None,
            yaxis_title=tools_observability_t(
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

        aplicar_tema_tools_observability_chart(
            fig_evolucao,
            height=440,
        )

        st.plotly_chart(
            fig_evolucao,
            width="stretch",
            key="tools_observability_evolution_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    st.divider()
    st.markdown(tools_observability_t("tool_performance"))

    ranking = preparar_ranking_tools(
        filtrado
    )

    if not ranking.empty:
        ranking_exibicao = ranking.rename(
            columns={
                "Ferramenta": tools_observability_t(
                    "tool"
                ),
                "Execuções": tools_observability_t(
                    "executions"
                ),
                "Sucessos": tools_observability_t(
                    "successes"
                ),
                "Falhas": tools_observability_t(
                    "failures"
                ),
                "Média_ms": tools_observability_t(
                    "average_ms"
                ),
                "Mínimo_ms": tools_observability_t(
                    "minimum_ms"
                ),
                "Máximo_ms": tools_observability_t(
                    "maximum_ms"
                ),
                "Taxa de sucesso (%)": (
                    tools_observability_t(
                        "success_rate_column"
                    )
                ),
            }
        )

        st.dataframe(
            ranking_exibicao,
            use_container_width=True,
            hide_index=True,
        )

        tool_label = tools_observability_t(
            "tool"
        )
        executions_label = tools_observability_t(
            "executions"
        )

        ranking_grafico = (
            ranking[
                [
                    "Ferramenta",
                    "Execuções",
                ]
            ]
            .copy()
            .rename(
                columns={
                    "Ferramenta": tool_label,
                    "Execuções": executions_label,
                }
            )
            .sort_values(
                executions_label,
                ascending=True,
            )
        )

        fig_performance = px.bar(
            ranking_grafico,
            x=executions_label,
            y=tool_label,
            orientation="h",
            text=executions_label,
            color=executions_label,
            color_continuous_scale=[
                "#172554",
                "#2563EB",
                "#38BDF8",
            ],
        )

        fig_performance.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                + tools_observability_t(
                    "executions"
                )
                + ": %{x:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_performance.update_layout(
            xaxis_title=tools_observability_t(
                "executions"
            ),
            yaxis_title=None,
            coloraxis_showscale=False,
            showlegend=False,
        )

        aplicar_tema_tools_observability_chart(
            fig_performance,
            height=max(
                390,
                130 + len(ranking_grafico) * 46,
            ),
        )

        st.plotly_chart(
            fig_performance,
            width="stretch",
            key="tools_observability_performance_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    st.divider()
    st.markdown(tools_observability_t("active_users_title"))

    user_label = tools_observability_t(
        "user"
    )
    executions_label = tools_observability_t(
        "executions"
    )

    usuarios_ranking = (
        filtrado["usuario_id"]
        .fillna(
            tools_observability_t(
                "no_user"
            )
        )
        .value_counts()
        .rename_axis(user_label)
        .reset_index(
            name=executions_label
        )
    )

    usuarios_grafico = (
        usuarios_ranking.copy()
        .sort_values(
            executions_label,
            ascending=True,
        )
    )

    fig_usuarios = px.bar(
        usuarios_grafico,
        x=executions_label,
        y=user_label,
        orientation="h",
        text=executions_label,
        color=executions_label,
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
            + tools_observability_t(
                "executions"
            )
            + ": %{x:,.0f}"
            "<extra></extra>"
        ),
    )

    fig_usuarios.update_layout(
        xaxis_title=tools_observability_t(
            "executions"
        ),
        yaxis_title=None,
        coloraxis_showscale=False,
        showlegend=False,
    )

    aplicar_tema_tools_observability_chart(
        fig_usuarios,
        height=max(
            380,
            130 + len(usuarios_grafico) * 44,
        ),
    )

    st.plotly_chart(
        fig_usuarios,
        width="stretch",
        key="tools_observability_active_users_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.divider()
    st.markdown(tools_observability_t("searchable_history"))

    tabela = preparar_eventos_exibicao(
        filtrado
    ).rename(
        columns={
            "Data": tools_observability_t(
                "date"
            ),
            "Usuário": tools_observability_t(
                "user"
            ),
            "Pergunta": tools_observability_t(
                "question"
            ),
            "Ferramenta": tools_observability_t(
                "tool"
            ),
            "Intenção": tools_observability_t(
                "intention"
            ),
            "Confiança": tools_observability_t(
                "confidence"
            ),
            "Status": tools_observability_t(
                "status"
            ),
            "Duração": tools_observability_t(
                "duration"
            ),
            "Origem": tools_observability_t(
                "origin"
            ),
            "Mensagem": tools_observability_t(
                "message"
            ),
            "Erro": tools_observability_t(
                "error"
            ),
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown(tools_observability_t("export_data"))

    export_1, export_2, export_3 = st.columns(3)

    csv_bytes = tabela.to_csv(
        index=False,
    ).encode("utf-8-sig")

    export_1.download_button(
        tools_observability_t("export_csv"),
        data=csv_bytes,
        file_name="inna_tools_eventos.csv",
        mime="text/csv",
        use_container_width=True,
    )

    json_bytes = json.dumps(
        filtrado.to_dict(
            orient="records"
        ),
        ensure_ascii=False,
        indent=2,
        default=str,
    ).encode("utf-8")

    export_2.download_button(
        tools_observability_t("export_json"),
        data=json_bytes,
        file_name="inna_tools_eventos.json",
        mime="application/json",
        use_container_width=True,
    )

    excel_bytes = gerar_excel(
        tabela,
        ranking,
    )

    export_3.download_button(
        tools_observability_t("export_excel"),
        data=excel_bytes,
        file_name="inna_tools_operations.xlsx",
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )


__all__ = [
    "calcular_taxa_sucesso",
    "preparar_ranking_tools",
    "preparar_serie_temporal",
    "preparar_eventos_exibicao",
    "gerar_excel",
    "render_metricas_executivas",
    "render_status_infraestrutura",
    "render_tools_observability_page",
]
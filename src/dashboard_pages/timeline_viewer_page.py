"""
Timeline Viewer das execuções da INNA.

Permite:
- listar traces recentes;
- filtrar execuções;
- visualizar etapas em ordem;
- identificar gargalos;
- inspecionar metadata e erros;
- comparar traces.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

TIMELINE_CHART_BG = "#020617"
TIMELINE_CHART_TEXT = "#F8FAFC"
TIMELINE_CHART_GRID = "rgba(148, 163, 184, 0.16)"


TIMELINE_TEXTS = {
    "pt": {
        "page_title": "🧭 Timeline Viewer — INNA",
        "page_caption": (
            "Visualize o caminho completo de cada resposta: "
            "memória, Router, Tools, RAG, Gemini e entrega."
        ),
        "trace_quantity": "Quantidade de traces",
        "refresh": "🔄 Atualizar Timeline",
        "no_traces": "Ainda não existem traces registrados.",
        "search_filters": "## Pesquisa e filtros",
        "search_label": "Pesquisar usuário, pergunta ou Trace ID",
        "search_placeholder": "Ex.: demo_user, quanto sobra...",
        "user": "Usuário",
        "origin": "Origem",
        "all_masculine": "Todos",
        "all_feminine": "Todas",
        "only_failures": "Mostrar somente traces com falhas",
        "traces_found": "{count} trace(s) encontrado(s).",
        "recent_traces": "## Traces recentes",
        "select_trace": "Selecione um Trace ID",
        "execution_summary": "## Resumo da execução",
        "steps": "Etapas",
        "failures": "Falhas",
        "ignored": "Ignoradas",
        "total_duration": "Duração total",
        "cold_start_warning": (
            "Possível cold start detectado: a execução ultrapassou 30 segundos."
        ),
        "execution_ok": ("Execução dentro do limite esperado para o ambiente atual."),
        "slowest_step": "Etapa mais lenta",
        "question": "### Pergunta",
        "execution_path": "## Caminho da execução",
        "technical_table": "## Tabela técnica",
        "compare_traces": "## Comparar traces",
        "duration": "Duração",
        "view_metadata": "Ver metadata",
        "not_measured": "Não medida",
        "success": "✅ Sucesso",
        "failure": "❌ Falha",
        "skipped": "⏭️ Ignorado",
        "started": "🔄 Iniciado",
        "with_failure": "❌ Com falha",
        "possible": "Possível",
        "no": "Não",
        "start": "Início",
        "status": "Status",
        "cold_start": "Cold start",
        "order": "Ordem",
        "step": "Etapa",
        "message": "Mensagem",
        "error": "Erro",
        "minimum_two_traces": (
            "São necessários pelo menos dois traces para fazer uma comparação."
        ),
        "ignore_cold_start": ("Ignorar traces classificados como cold start"),
        "not_enough_after_filter": (
            "Não existem dois traces disponíveis após aplicar o filtro de cold start."
        ),
        "chart_scale": "Escala do gráfico",
        "linear": "Linear",
        "logarithmic": "Logarítmica",
        "different_traces": "Selecione dois traces diferentes.",
        "trace_b_slower": ("O Trace B foi {percent:.2f}% mais lento que o Trace A."),
        "trace_b_faster": ("O Trace B foi {percent:.2f}% mais rápido que o Trace A."),
        "same_duration": ("Os dois traces tiveram a mesma duração total."),
        "absolute_difference": "Diferença absoluta",
        "percentage_difference": "Diferença percentual",
        "slowest_step_column": "Etapa mais lenta",
        "log_caption": (
            "Escala logarítmica: os valores exibidos "
            "representam log10(duração em ms + 1)."
        ),
        "log_axis": "log10(duração em ms + 1)",
        "duration_axis": "Duração (ms)",
        "formatted_duration": "Duração formatada",
    },
    "en_us": {
        "page_title": "🧭 Timeline Viewer — INNA",
        "page_caption": (
            "View the complete path of each response: memory, "
            "Router, Tools, RAG, Gemini, and delivery."
        ),
        "trace_quantity": "Number of traces",
        "refresh": "🔄 Refresh Timeline",
        "no_traces": "No traces have been recorded yet.",
        "search_filters": "## Search and filters",
        "search_label": "Search user, question, or Trace ID",
        "search_placeholder": ("Example: demo_user, remaining balance..."),
        "user": "User",
        "origin": "Origin",
        "all_masculine": "All",
        "all_feminine": "All",
        "only_failures": "Show only traces with failures",
        "traces_found": "{count} trace(s) found.",
        "recent_traces": "## Recent traces",
        "select_trace": "Select a Trace ID",
        "execution_summary": "## Execution summary",
        "steps": "Steps",
        "failures": "Failures",
        "ignored": "Skipped",
        "total_duration": "Total duration",
        "cold_start_warning": (
            "Possible cold start detected: the execution exceeded 30 seconds."
        ),
        "execution_ok": (
            "Execution completed within the expected limit for the current environment."
        ),
        "slowest_step": "Slowest step",
        "question": "### Question",
        "execution_path": "## Execution path",
        "technical_table": "## Technical table",
        "compare_traces": "## Compare traces",
        "duration": "Duration",
        "view_metadata": "View metadata",
        "not_measured": "Not measured",
        "success": "✅ Success",
        "failure": "❌ Failure",
        "skipped": "⏭️ Skipped",
        "started": "🔄 Started",
        "with_failure": "❌ Failed",
        "possible": "Possible",
        "no": "No",
        "start": "Start",
        "status": "Status",
        "cold_start": "Cold start",
        "order": "Order",
        "step": "Step",
        "message": "Message",
        "error": "Error",
        "minimum_two_traces": ("At least two traces are required for comparison."),
        "ignore_cold_start": ("Ignore traces classified as cold starts"),
        "not_enough_after_filter": (
            "Two traces are not available after applying the cold-start filter."
        ),
        "chart_scale": "Chart scale",
        "linear": "Linear",
        "logarithmic": "Logarithmic",
        "different_traces": "Select two different traces.",
        "trace_b_slower": ("Trace B was {percent:.2f}% slower than Trace A."),
        "trace_b_faster": ("Trace B was {percent:.2f}% faster than Trace A."),
        "same_duration": ("Both traces had the same total duration."),
        "absolute_difference": "Absolute difference",
        "percentage_difference": "Percentage difference",
        "slowest_step_column": "Slowest step",
        "log_caption": (
            "Logarithmic scale: displayed values represent log10(duration in ms + 1)."
        ),
        "log_axis": "log10(duration in ms + 1)",
        "duration_axis": "Duration (ms)",
        "formatted_duration": "Formatted duration",
    },
    "es": {
        "page_title": "🧭 Visor de línea de tiempo — INNA",
        "page_caption": (
            "Visualiza el recorrido completo de cada respuesta: "
            "memoria, Router, Tools, RAG, Gemini y entrega."
        ),
        "trace_quantity": "Cantidad de trazas",
        "refresh": "🔄 Actualizar línea de tiempo",
        "no_traces": "Todavía no hay trazas registradas.",
        "search_filters": "## Búsqueda y filtros",
        "search_label": "Buscar usuario, pregunta o Trace ID",
        "search_placeholder": ("Ej.: demo_user, saldo restante..."),
        "user": "Usuario",
        "origin": "Origen",
        "all_masculine": "Todos",
        "all_feminine": "Todas",
        "only_failures": "Mostrar solo trazas con fallos",
        "traces_found": "{count} traza(s) encontrada(s).",
        "recent_traces": "## Trazas recientes",
        "select_trace": "Selecciona un Trace ID",
        "execution_summary": "## Resumen de ejecución",
        "steps": "Etapas",
        "failures": "Fallos",
        "ignored": "Omitidas",
        "total_duration": "Duración total",
        "cold_start_warning": (
            "Posible cold start detectado: la ejecución superó los 30 segundos."
        ),
        "execution_ok": (
            "Ejecución dentro del límite esperado para el entorno actual."
        ),
        "slowest_step": "Etapa más lenta",
        "question": "### Pregunta",
        "execution_path": "## Ruta de ejecución",
        "technical_table": "## Tabla técnica",
        "compare_traces": "## Comparar trazas",
        "duration": "Duración",
        "view_metadata": "Ver metadatos",
        "not_measured": "No medida",
        "success": "✅ Éxito",
        "failure": "❌ Fallo",
        "skipped": "⏭️ Omitida",
        "started": "🔄 Iniciada",
        "with_failure": "❌ Con fallo",
        "possible": "Posible",
        "no": "No",
        "start": "Inicio",
        "status": "Estado",
        "cold_start": "Cold start",
        "order": "Orden",
        "step": "Etapa",
        "message": "Mensaje",
        "error": "Error",
        "minimum_two_traces": ("Se necesitan al menos dos trazas para compararlas."),
        "ignore_cold_start": ("Ignorar trazas clasificadas como cold start"),
        "not_enough_after_filter": (
            "No hay dos trazas disponibles después de aplicar el filtro de cold start."
        ),
        "chart_scale": "Escala del gráfico",
        "linear": "Lineal",
        "logarithmic": "Logarítmica",
        "different_traces": "Selecciona dos trazas diferentes.",
        "trace_b_slower": ("La traza B fue un {percent:.2f}% más lenta que la A."),
        "trace_b_faster": ("La traza B fue un {percent:.2f}% más rápida que la A."),
        "same_duration": ("Las dos trazas tuvieron la misma duración total."),
        "absolute_difference": "Diferencia absoluta",
        "percentage_difference": "Diferencia porcentual",
        "slowest_step_column": "Etapa más lenta",
        "log_caption": (
            "Escala logarítmica: los valores representan log10(duración en ms + 1)."
        ),
        "log_axis": "log10(duración en ms + 1)",
        "duration_axis": "Duración (ms)",
        "formatted_duration": "Duración formateada",
    },
    "sa": {
        "page_title": "🧭 عارض المسار الزمني — INNA",
        "page_caption": (
            "اعرض المسار الكامل لكل إجابة: الذاكرة والموجّه "
            "والأدوات وRAG وGemini والتسليم."
        ),
        "trace_quantity": "عدد المسارات",
        "refresh": "🔄 تحديث المسار الزمني",
        "no_traces": "لا توجد مسارات مسجلة حتى الآن.",
        "search_filters": "## البحث والتصفية",
        "search_label": "البحث عن مستخدم أو سؤال أو Trace ID",
        "search_placeholder": ("مثال: demo_user، الرصيد المتبقي..."),
        "user": "المستخدم",
        "origin": "المصدر",
        "all_masculine": "الكل",
        "all_feminine": "الكل",
        "only_failures": "عرض المسارات التي تحتوي على إخفاقات فقط",
        "traces_found": "تم العثور على {count} مسار.",
        "recent_traces": "## المسارات الحديثة",
        "select_trace": "اختر Trace ID",
        "execution_summary": "## ملخص التنفيذ",
        "steps": "المراحل",
        "failures": "الإخفاقات",
        "ignored": "المتجاهلة",
        "total_duration": "المدة الإجمالية",
        "cold_start_warning": ("تم اكتشاف بدء بارد محتمل: تجاوز التنفيذ 30 ثانية."),
        "execution_ok": ("اكتمل التنفيذ ضمن الحد المتوقع للبيئة الحالية."),
        "slowest_step": "أبطأ مرحلة",
        "question": "### السؤال",
        "execution_path": "## مسار التنفيذ",
        "technical_table": "## الجدول الفني",
        "compare_traces": "## مقارنة المسارات",
        "duration": "المدة",
        "view_metadata": "عرض البيانات الوصفية",
        "not_measured": "غير مقاسة",
        "success": "✅ نجاح",
        "failure": "❌ فشل",
        "skipped": "⏭️ تم التجاوز",
        "started": "🔄 بدأ",
        "with_failure": "❌ يحتوي على فشل",
        "possible": "محتمل",
        "no": "لا",
        "start": "البداية",
        "status": "الحالة",
        "cold_start": "بدء بارد",
        "order": "الترتيب",
        "step": "المرحلة",
        "message": "الرسالة",
        "error": "الخطأ",
        "minimum_two_traces": ("يلزم وجود مسارين على الأقل لإجراء المقارنة."),
        "ignore_cold_start": ("تجاهل المسارات المصنفة كبداية باردة"),
        "not_enough_after_filter": ("لا يتوفر مساران بعد تطبيق مرشح البداية الباردة."),
        "chart_scale": "مقياس الرسم",
        "linear": "خطي",
        "logarithmic": "لوغاريتمي",
        "different_traces": "اختر مسارين مختلفين.",
        "trace_b_slower": ("كان المسار B أبطأ بنسبة {percent:.2f}% من المسار A."),
        "trace_b_faster": ("كان المسار B أسرع بنسبة {percent:.2f}% من المسار A."),
        "same_duration": ("كان للمسارين المدة الإجمالية نفسها."),
        "absolute_difference": "الفرق المطلق",
        "percentage_difference": "الفرق النسبي",
        "slowest_step_column": "أبطأ مرحلة",
        "log_caption": (
            "المقياس اللوغاريتمي: تمثل القيم log10(المدة بالمللي ثانية + 1)."
        ),
        "log_axis": "log10(المدة بالمللي ثانية + 1)",
        "duration_axis": "المدة (مللي ثانية)",
        "formatted_duration": "المدة المنسقة",
    },
}

TIMELINE_TEXTS["en_gb"] = TIMELINE_TEXTS["en_us"]

TIMELINE_TEXTS["fr"] = {
    "page_title": "🧭 Visionneuse de chronologie — INNA",
    "page_caption": (
        "Visualisez le parcours complet de chaque réponse : "
        "mémoire, Router, Tools, RAG, Gemini et livraison."
    ),
    "trace_quantity": "Nombre de traces",
    "refresh": "🔄 Actualiser la chronologie",
    "no_traces": "Aucune trace n’a encore été enregistrée.",
    "search_filters": "## Recherche et filtres",
    "search_label": "Rechercher un utilisateur, une question ou un Trace ID",
    "search_placeholder": "Exemple : demo_user, solde restant...",
    "user": "Utilisateur",
    "origin": "Origine",
    "all_masculine": "Tous",
    "all_feminine": "Toutes",
    "only_failures": "Afficher uniquement les traces avec des erreurs",
    "traces_found": "{count} trace(s) trouvée(s).",
    "recent_traces": "## Traces récentes",
    "select_trace": "Sélectionnez un Trace ID",
    "execution_summary": "## Résumé de l’exécution",
    "steps": "Étapes",
    "failures": "Erreurs",
    "ignored": "Ignorées",
    "total_duration": "Durée totale",
    "cold_start_warning": (
        "Démarrage à froid possible détecté : l’exécution a dépassé 30 secondes."
    ),
    "execution_ok": (
        "Exécution terminée dans la limite attendue pour l’environnement actuel."
    ),
    "slowest_step": "Étape la plus lente",
    "question": "### Question",
    "execution_path": "## Parcours de l’exécution",
    "technical_table": "## Tableau technique",
    "compare_traces": "## Comparer les traces",
    "duration": "Durée",
    "view_metadata": "Voir les métadonnées",
    "not_measured": "Non mesurée",
    "success": "✅ Succès",
    "failure": "❌ Échec",
    "skipped": "⏭️ Ignorée",
    "started": "🔄 Démarrée",
    "with_failure": "❌ Avec erreur",
    "possible": "Possible",
    "no": "Non",
    "start": "Début",
    "status": "Statut",
    "cold_start": "Démarrage à froid",
    "order": "Ordre",
    "step": "Étape",
    "message": "Message",
    "error": "Erreur",
    "minimum_two_traces": (
        "Au moins deux traces sont nécessaires pour la comparaison."
    ),
    "ignore_cold_start": ("Ignorer les traces classées comme démarrage à froid"),
    "not_enough_after_filter": (
        "Deux traces ne sont pas disponibles après "
        "l’application du filtre de démarrage à froid."
    ),
    "chart_scale": "Échelle du graphique",
    "linear": "Linéaire",
    "logarithmic": "Logarithmique",
    "different_traces": "Sélectionnez deux traces différentes.",
    "trace_b_slower": ("La trace B était {percent:.2f}% plus lente que la trace A."),
    "trace_b_faster": ("La trace B était {percent:.2f}% plus rapide que la trace A."),
    "same_duration": ("Les deux traces avaient la même durée totale."),
    "absolute_difference": "Différence absolue",
    "percentage_difference": "Différence en pourcentage",
    "slowest_step_column": "Étape la plus lente",
    "log_caption": (
        "Échelle logarithmique : les valeurs affichées représentent "
        "log10(durée en ms + 1)."
    ),
    "log_axis": "log10(durée en ms + 1)",
    "duration_axis": "Durée (ms)",
    "formatted_duration": "Durée formatée",
}

TIMELINE_TEXTS["de"] = {
    "page_title": "🧭 Timeline-Ansicht — INNA",
    "page_caption": (
        "Zeigt den vollständigen Ablauf jeder Antwort: Speicher, "
        "Router, Tools, RAG, Gemini und Ausgabe."
    ),
    "trace_quantity": "Anzahl der Traces",
    "refresh": "🔄 Timeline aktualisieren",
    "no_traces": "Es wurden noch keine Traces erfasst.",
    "search_filters": "## Suche und Filter",
    "search_label": "Benutzer, Frage oder Trace ID suchen",
    "search_placeholder": "Beispiel: demo_user, Restbetrag...",
    "user": "Benutzer",
    "origin": "Quelle",
    "all_masculine": "Alle",
    "all_feminine": "Alle",
    "only_failures": "Nur Traces mit Fehlern anzeigen",
    "traces_found": "{count} Trace(s) gefunden.",
    "recent_traces": "## Aktuelle Traces",
    "select_trace": "Trace ID auswählen",
    "execution_summary": "## Ausführungsübersicht",
    "steps": "Schritte",
    "failures": "Fehler",
    "ignored": "Übersprungen",
    "total_duration": "Gesamtdauer",
    "cold_start_warning": (
        "Möglicher Kaltstart erkannt: Die Ausführung dauerte länger als 30 Sekunden."
    ),
    "execution_ok": (
        "Die Ausführung lag innerhalb des erwarteten Grenzwerts "
        "für die aktuelle Umgebung."
    ),
    "slowest_step": "Langsamster Schritt",
    "question": "### Frage",
    "execution_path": "## Ausführungsablauf",
    "technical_table": "## Technische Tabelle",
    "compare_traces": "## Traces vergleichen",
    "duration": "Dauer",
    "view_metadata": "Metadaten anzeigen",
    "not_measured": "Nicht gemessen",
    "success": "✅ Erfolg",
    "failure": "❌ Fehler",
    "skipped": "⏭️ Übersprungen",
    "started": "🔄 Gestartet",
    "with_failure": "❌ Mit Fehler",
    "possible": "Möglich",
    "no": "Nein",
    "start": "Start",
    "status": "Status",
    "cold_start": "Kaltstart",
    "order": "Reihenfolge",
    "step": "Schritt",
    "message": "Nachricht",
    "error": "Fehler",
    "minimum_two_traces": (
        "Für einen Vergleich sind mindestens zwei Traces erforderlich."
    ),
    "ignore_cold_start": ("Als Kaltstart klassifizierte Traces ignorieren"),
    "not_enough_after_filter": (
        "Nach Anwendung des Kaltstartfilters sind keine zwei Traces verfügbar."
    ),
    "chart_scale": "Diagrammskala",
    "linear": "Linear",
    "logarithmic": "Logarithmisch",
    "different_traces": "Wählen Sie zwei unterschiedliche Traces.",
    "trace_b_slower": ("Trace B war {percent:.2f}% langsamer als Trace A."),
    "trace_b_faster": ("Trace B war {percent:.2f}% schneller als Trace A."),
    "same_duration": ("Beide Traces hatten dieselbe Gesamtdauer."),
    "absolute_difference": "Absolute Differenz",
    "percentage_difference": "Prozentuale Differenz",
    "slowest_step_column": "Langsamster Schritt",
    "log_caption": (
        "Logarithmische Skala: Die angezeigten Werte entsprechen "
        "log10(Dauer in ms + 1)."
    ),
    "log_axis": "log10(Dauer in ms + 1)",
    "duration_axis": "Dauer (ms)",
    "formatted_duration": "Formatierte Dauer",
}

TIMELINE_TEXTS["it"] = {
    "page_title": "🧭 Visualizzatore timeline — INNA",
    "page_caption": (
        "Visualizza il percorso completo di ogni risposta: memoria, "
        "Router, Tools, RAG, Gemini e consegna."
    ),
    "trace_quantity": "Numero di trace",
    "refresh": "🔄 Aggiorna timeline",
    "no_traces": "Non sono ancora stati registrati trace.",
    "search_filters": "## Ricerca e filtri",
    "search_label": "Cerca utente, domanda o Trace ID",
    "search_placeholder": "Esempio: demo_user, saldo residuo...",
    "user": "Utente",
    "origin": "Origine",
    "all_masculine": "Tutti",
    "all_feminine": "Tutte",
    "only_failures": "Mostra solo i trace con errori",
    "traces_found": "{count} trace trovato/i.",
    "recent_traces": "## Trace recenti",
    "select_trace": "Seleziona un Trace ID",
    "execution_summary": "## Riepilogo dell’esecuzione",
    "steps": "Fasi",
    "failures": "Errori",
    "ignored": "Ignorate",
    "total_duration": "Durata totale",
    "cold_start_warning": (
        "Possibile cold start rilevato: l’esecuzione ha superato i 30 secondi."
    ),
    "execution_ok": (
        "Esecuzione completata entro il limite previsto per l’ambiente attuale."
    ),
    "slowest_step": "Fase più lenta",
    "question": "### Domanda",
    "execution_path": "## Percorso di esecuzione",
    "technical_table": "## Tabella tecnica",
    "compare_traces": "## Confronta trace",
    "duration": "Durata",
    "view_metadata": "Visualizza metadati",
    "not_measured": "Non misurata",
    "success": "✅ Successo",
    "failure": "❌ Errore",
    "skipped": "⏭️ Ignorata",
    "started": "🔄 Avviata",
    "with_failure": "❌ Con errore",
    "possible": "Possibile",
    "no": "No",
    "start": "Inizio",
    "status": "Stato",
    "cold_start": "Cold start",
    "order": "Ordine",
    "step": "Fase",
    "message": "Messaggio",
    "error": "Errore",
    "minimum_two_traces": ("Sono necessari almeno due trace per il confronto."),
    "ignore_cold_start": ("Ignora i trace classificati come cold start"),
    "not_enough_after_filter": (
        "Non sono disponibili due trace dopo l’applicazione del filtro cold start."
    ),
    "chart_scale": "Scala del grafico",
    "linear": "Lineare",
    "logarithmic": "Logaritmica",
    "different_traces": "Seleziona due trace differenti.",
    "trace_b_slower": (
        "Il trace B è stato più lento del {percent:.2f}% rispetto al trace A."
    ),
    "trace_b_faster": (
        "Il trace B è stato più veloce del {percent:.2f}% rispetto al trace A."
    ),
    "same_duration": ("I due trace hanno avuto la stessa durata totale."),
    "absolute_difference": "Differenza assoluta",
    "percentage_difference": "Differenza percentuale",
    "slowest_step_column": "Fase più lenta",
    "log_caption": (
        "Scala logaritmica: i valori visualizzati rappresentano "
        "log10(durata in ms + 1)."
    ),
    "log_axis": "log10(durata in ms + 1)",
    "duration_axis": "Durata (ms)",
    "formatted_duration": "Durata formattata",
}

TIMELINE_TEXTS["ro"] = {
    "page_title": "🧭 Vizualizator cronologie — INNA",
    "page_caption": (
        "Vizualizează traseul complet al fiecărui răspuns: "
        "memorie, Router, Tools, RAG, Gemini și livrare."
    ),
    "trace_quantity": "Număr de trasări",
    "refresh": "🔄 Actualizează cronologia",
    "no_traces": "Nu există încă trasări înregistrate.",
    "search_filters": "## Căutare și filtre",
    "search_label": ("Caută utilizator, întrebare sau Trace ID"),
    "search_placeholder": ("Exemplu: demo_user, sold rămas..."),
    "user": "Utilizator",
    "origin": "Origine",
    "all_masculine": "Toți",
    "all_feminine": "Toate",
    "only_failures": ("Afișează numai trasările cu erori"),
    "traces_found": ("{count} trasare/trasări găsită/găsite."),
    "recent_traces": "## Trasări recente",
    "select_trace": "Selectează un Trace ID",
    "execution_summary": "## Rezumatul execuției",
    "steps": "Etape",
    "failures": "Erori",
    "ignored": "Ignorate",
    "total_duration": "Durată totală",
    "cold_start_warning": (
        "A fost detectat un posibil cold start: execuția a depășit 30 de secunde."
    ),
    "execution_ok": ("Execuția s-a încheiat în limita așteptată pentru mediul actual."),
    "slowest_step": "Cea mai lentă etapă",
    "question": "### Întrebare",
    "execution_path": "## Traseul execuției",
    "technical_table": "## Tabel tehnic",
    "compare_traces": "## Compară trasările",
    "duration": "Durată",
    "view_metadata": "Vezi metadatele",
    "not_measured": "Nemăsurată",
    "success": "✅ Succes",
    "failure": "❌ Eroare",
    "skipped": "⏭️ Ignorată",
    "started": "🔄 Pornită",
    "with_failure": "❌ Cu eroare",
    "possible": "Posibil",
    "no": "Nu",
    "start": "Început",
    "status": "Stare",
    "cold_start": "Cold start",
    "order": "Ordine",
    "step": "Etapă",
    "message": "Mesaj",
    "error": "Eroare",
    "minimum_two_traces": ("Sunt necesare cel puțin două trasări pentru comparație."),
    "ignore_cold_start": ("Ignoră trasările clasificate drept cold start"),
    "not_enough_after_filter": (
        "Nu sunt disponibile două trasări după aplicarea filtrului cold start."
    ),
    "chart_scale": "Scara graficului",
    "linear": "Liniară",
    "logarithmic": "Logaritmică",
    "different_traces": ("Selectează două trasări diferite."),
    "trace_b_slower": (
        "Trasarea B a fost cu {percent:.2f}% mai lentă decât trasarea A."
    ),
    "trace_b_faster": (
        "Trasarea B a fost cu {percent:.2f}% mai rapidă decât trasarea A."
    ),
    "same_duration": ("Cele două trasări au avut aceeași durată totală."),
    "absolute_difference": "Diferență absolută",
    "percentage_difference": "Diferență procentuală",
    "slowest_step_column": "Cea mai lentă etapă",
    "log_caption": (
        "Scară logaritmică: valorile afișate reprezintă log10(durata în ms + 1)."
    ),
    "log_axis": "log10(durata în ms + 1)",
    "duration_axis": "Durată (ms)",
    "formatted_duration": "Durată formatată",
}

TIMELINE_TEXTS["ua"] = {
    "page_title": "🧭 Перегляд часової шкали — INNA",
    "page_caption": (
        "Переглядайте повний шлях кожної відповіді: пам’ять, "
        "Router, Tools, RAG, Gemini та доставлення."
    ),
    "trace_quantity": "Кількість трасувань",
    "refresh": "🔄 Оновити часову шкалу",
    "no_traces": "Трасування ще не зареєстровані.",
    "search_filters": "## Пошук і фільтри",
    "search_label": ("Пошук користувача, запитання або Trace ID"),
    "search_placeholder": ("Приклад: demo_user, залишок коштів..."),
    "user": "Користувач",
    "origin": "Джерело",
    "all_masculine": "Усі",
    "all_feminine": "Усі",
    "only_failures": ("Показувати лише трасування з помилками"),
    "traces_found": "Знайдено трасувань: {count}.",
    "recent_traces": "## Останні трасування",
    "select_trace": "Виберіть Trace ID",
    "execution_summary": "## Підсумок виконання",
    "steps": "Етапи",
    "failures": "Помилки",
    "ignored": "Пропущені",
    "total_duration": "Загальна тривалість",
    "cold_start_warning": (
        "Виявлено можливий холодний запуск: виконання тривало понад 30 секунд."
    ),
    "execution_ok": (
        "Виконання завершилося в межах очікуваного часу для поточного середовища."
    ),
    "slowest_step": "Найповільніший етап",
    "question": "### Запитання",
    "execution_path": "## Шлях виконання",
    "technical_table": "## Технічна таблиця",
    "compare_traces": "## Порівняння трасувань",
    "duration": "Тривалість",
    "view_metadata": "Переглянути метадані",
    "not_measured": "Не виміряно",
    "success": "✅ Успіх",
    "failure": "❌ Помилка",
    "skipped": "⏭️ Пропущено",
    "started": "🔄 Розпочато",
    "with_failure": "❌ З помилкою",
    "possible": "Можливо",
    "no": "Ні",
    "start": "Початок",
    "status": "Статус",
    "cold_start": "Холодний запуск",
    "order": "Порядок",
    "step": "Етап",
    "message": "Повідомлення",
    "error": "Помилка",
    "minimum_two_traces": ("Для порівняння потрібно щонайменше два трасування."),
    "ignore_cold_start": ("Ігнорувати трасування, класифіковані як холодний запуск"),
    "not_enough_after_filter": (
        "Після застосування фільтра холодного запуску немає двох доступних трасувань."
    ),
    "chart_scale": "Масштаб графіка",
    "linear": "Лінійний",
    "logarithmic": "Логарифмічний",
    "different_traces": ("Виберіть два різні трасування."),
    "trace_b_slower": (
        "Трасування B було на {percent:.2f}% повільнішим за трасування A."
    ),
    "trace_b_faster": ("Трасування B було на {percent:.2f}% швидшим за трасування A."),
    "same_duration": ("Обидва трасування мали однакову загальну тривалість."),
    "absolute_difference": "Абсолютна різниця",
    "percentage_difference": "Відсоткова різниця",
    "slowest_step_column": "Найповільніший етап",
    "log_caption": (
        "Логарифмічний масштаб: показані значення відповідають "
        "log10(тривалість у мс + 1)."
    ),
    "log_axis": "log10(тривалість у мс + 1)",
    "duration_axis": "Тривалість (мс)",
    "formatted_duration": "Форматована тривалість",
}

TIMELINE_TEXTS["ru"] = {
    "page_title": "🧭 Просмотр временной шкалы — INNA",
    "page_caption": (
        "Просматривайте полный путь каждого ответа: память, "
        "Router, Tools, RAG, Gemini и доставка."
    ),
    "trace_quantity": "Количество трассировок",
    "refresh": "🔄 Обновить временную шкалу",
    "no_traces": "Трассировки ещё не зарегистрированы.",
    "search_filters": "## Поиск и фильтры",
    "search_label": ("Поиск пользователя, вопроса или Trace ID"),
    "search_placeholder": ("Пример: demo_user, остаток средств..."),
    "user": "Пользователь",
    "origin": "Источник",
    "all_masculine": "Все",
    "all_feminine": "Все",
    "only_failures": ("Показывать только трассировки с ошибками"),
    "traces_found": "Найдено трассировок: {count}.",
    "recent_traces": "## Последние трассировки",
    "select_trace": "Выберите Trace ID",
    "execution_summary": "## Сводка выполнения",
    "steps": "Этапы",
    "failures": "Ошибки",
    "ignored": "Пропущенные",
    "total_duration": "Общая длительность",
    "cold_start_warning": (
        "Обнаружен возможный холодный запуск: выполнение заняло более 30 секунд."
    ),
    "execution_ok": (
        "Выполнение завершилось в пределах ожидаемого времени для текущей среды."
    ),
    "slowest_step": "Самый медленный этап",
    "question": "### Вопрос",
    "execution_path": "## Путь выполнения",
    "technical_table": "## Техническая таблица",
    "compare_traces": "## Сравнение трассировок",
    "duration": "Длительность",
    "view_metadata": "Просмотреть метаданные",
    "not_measured": "Не измерено",
    "success": "✅ Успех",
    "failure": "❌ Ошибка",
    "skipped": "⏭️ Пропущено",
    "started": "🔄 Запущено",
    "with_failure": "❌ С ошибкой",
    "possible": "Возможно",
    "no": "Нет",
    "start": "Начало",
    "status": "Статус",
    "cold_start": "Холодный запуск",
    "order": "Порядок",
    "step": "Этап",
    "message": "Сообщение",
    "error": "Ошибка",
    "minimum_two_traces": ("Для сравнения необходимы как минимум две трассировки."),
    "ignore_cold_start": (
        "Игнорировать трассировки, классифицированные как холодный запуск"
    ),
    "not_enough_after_filter": (
        "После применения фильтра холодного запуска нет двух доступных трассировок."
    ),
    "chart_scale": "Масштаб графика",
    "linear": "Линейный",
    "logarithmic": "Логарифмический",
    "different_traces": ("Выберите две разные трассировки."),
    "trace_b_slower": ("Трассировка B была на {percent:.2f}% медленнее трассировки A."),
    "trace_b_faster": ("Трассировка B была на {percent:.2f}% быстрее трассировки A."),
    "same_duration": ("Обе трассировки имели одинаковую общую длительность."),
    "absolute_difference": "Абсолютная разница",
    "percentage_difference": "Процентная разница",
    "slowest_step_column": "Самый медленный этап",
    "log_caption": (
        "Логарифмический масштаб: отображаемые значения "
        "соответствуют log10(длительность в мс + 1)."
    ),
    "log_axis": "log10(длительность в мс + 1)",
    "duration_axis": "Длительность (мс)",
    "formatted_duration": "Форматированная длительность",
}

# Ajustes finais dos textos visíveis conforme o seletor.
TIMELINE_TEXTS["pt"].update(
    {
        "page_title": ("🧭 Linha do tempo das execuções — INNA"),
        "status": "Situação",
        "linear": "Escala linear",
    }
)

TIMELINE_TEXTS["en_us"].update(
    {
        "page_title": ("🧭 Execution timeline — INNA"),
    }
)

TIMELINE_TEXTS["en_gb"] = dict(TIMELINE_TEXTS["en_us"])

TIMELINE_TEXTS["es"].update(
    {
        "page_title": ("🧭 Línea de tiempo de las ejecuciones — INNA"),
    }
)

TIMELINE_TEXTS["fr"].update(
    {
        "page_title": ("🧭 Chronologie des exécutions — INNA"),
        "question": "### Question posée",
        "possible": "Éventuel",
        "message": "Message technique",
    }
)

TIMELINE_TEXTS["de"].update(
    {
        "page_title": ("🧭 Zeitachse der Ausführungen — INNA"),
        "start": "Beginn",
        "status": "Zustand",
        "linear": "Lineare Skala",
    }
)

TIMELINE_TEXTS["it"].update(
    {
        "page_title": ("🧭 Cronologia delle esecuzioni — INNA"),
    }
)

TIMELINE_TEXTS["ro"].update(
    {
        "page_title": ("🧭 Cronologia execuțiilor — INNA"),
    }
)

TIMELINE_TEXTS["ua"].update(
    {
        "page_title": ("🧭 Хронологія виконань — INNA"),
    }
)

TIMELINE_TEXTS["ru"].update(
    {
        "page_title": ("🧭 Хронология выполнений — INNA"),
    }
)

TIMELINE_TEXTS["sa"].update(
    {
        "page_title": ("🧭 المخطط الزمني لعمليات التنفيذ — INNA"),
    }
)

# O código ch segue o alemão utilizado pelo projeto.
TIMELINE_TEXTS["ch"] = dict(TIMELINE_TEXTS["de"])


def timeline_lang() -> str:
    language = str(
        st.session_state.get(
            "dashboard_interface_lang",
            "pt",
        )
    )

    aliases = {
        "en": "en_us",
        "en-US": "en_us",
        "en-GB": "en_gb",
        "ar": "sa",
        "ar-SA": "sa",
    }

    language = aliases.get(
        language,
        language,
    )

    if language in TIMELINE_TEXTS:
        return language

    return "pt"


def timeline_t(
    key: str,
    default: str | None = None,
) -> str:
    language = timeline_lang()

    language_texts = TIMELINE_TEXTS.get(
        language,
        {},
    )

    if key in language_texts:
        return language_texts[key]

    if key in TIMELINE_TEXTS["pt"]:
        return TIMELINE_TEXTS["pt"][key]

    if default is not None:
        return default

    return key


def aplicar_tema_timeline_chart(
    fig,
    *,
    height=440,
):
    """Aplica o tema visual do Timeline Viewer."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=TIMELINE_CHART_BG,
        plot_bgcolor=TIMELINE_CHART_BG,
        font={
            "color": TIMELINE_CHART_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": TIMELINE_CHART_TEXT,
        },
        margin={
            "l": 30,
            "r": 55,
            "t": 22,
            "b": 42,
        },
        height=height,
    )

    fig.update_xaxes(
        color=TIMELINE_CHART_TEXT,
        gridcolor=TIMELINE_CHART_GRID,
        zerolinecolor=("rgba(148, 163, 184, 0.25)"),
    )

    fig.update_yaxes(
        color=TIMELINE_CHART_TEXT,
        gridcolor=TIMELINE_CHART_GRID,
        zerolinecolor=("rgba(148, 163, 184, 0.25)"),
    )

    return fig


def timeline_status_labels() -> dict[str, str]:
    return {
        "sucesso": timeline_t("success"),
        "falha": timeline_t("failure"),
        "ignorado": timeline_t("skipped"),
        "iniciado": timeline_t("started"),
    }


STATUS_LABELS = {
    "sucesso": "✅ Sucesso",
    "falha": "❌ Falha",
    "ignorado": "⏭️ Ignorado",
    "iniciado": "🔄 Iniciado",
}


TIMELINE_DYNAMIC_TEXTS = {
    "pt": {
        "steps": {
            "Busca RAG concluída": "Busca RAG concluída",
            "Gemini executado": "Gemini executado",
            "Memória consultada": "Memória consultada",
            "Pergunta recebida": "Pergunta recebida",
            "Prompt estruturado": "Prompt estruturado",
            "Resposta entregue": "Resposta entregue",
            "Resposta formatada": "Resposta formatada",
            "Router executado": "Router executado",
            "Tool financeira executada": "Tool financeira executada",
        },
        "step_completed": "Etapa concluída com sucesso: {step}.",
        "completed": "{step} concluída com sucesso.",
        "question_received_rag": "Pergunta recebida pelo fluxo RAG.",
        "final_response_ready": ("Resposta final preparada para entrega ao dashboard."),
        "tool_result": (
            "Resultado da Tool registrado. O tempo total foi "
            "contabilizado na etapa do Router/Orquestrador."
        ),
    },
    "en_us": {
        "steps": {
            "Busca RAG concluída": "RAG search completed",
            "Gemini executado": "Gemini executed",
            "Memória consultada": "Memory retrieved",
            "Pergunta recebida": "Question received",
            "Prompt estruturado": "Prompt structured",
            "Resposta entregue": "Response delivered",
            "Resposta formatada": "Response formatted",
            "Router executado": "Router executed",
            "Tool financeira executada": "Financial tool executed",
        },
        "step_completed": "Step completed successfully: {step}.",
        "completed": "{step} completed successfully.",
        "question_received_rag": ("Question received by the RAG flow."),
        "final_response_ready": (
            "Final response prepared for delivery to the dashboard."
        ),
        "tool_result": (
            "Tool result recorded. The total time was accounted "
            "for in the Router/Orchestrator step."
        ),
    },
    "es": {
        "steps": {
            "Busca RAG concluída": "Búsqueda RAG completada",
            "Gemini executado": "Gemini ejecutado",
            "Memória consultada": "Memoria consultada",
            "Pergunta recebida": "Pregunta recibida",
            "Prompt estruturado": "Prompt estructurado",
            "Resposta entregue": "Respuesta entregada",
            "Resposta formatada": "Respuesta formateada",
            "Router executado": "Router ejecutado",
            "Tool financeira executada": "Herramienta financiera ejecutada",
        },
        "step_completed": "Etapa completada correctamente: {step}.",
        "completed": "{step} completada correctamente.",
        "question_received_rag": ("Pregunta recibida por el flujo RAG."),
        "final_response_ready": ("Respuesta final preparada para entregarse al panel."),
        "tool_result": (
            "Resultado de la herramienta registrado. El tiempo total "
            "se contabilizó en la etapa Router/Orquestador."
        ),
    },
    "fr": {
        "steps": {
            "Busca RAG concluída": "Recherche RAG terminée",
            "Gemini executado": "Gemini exécuté",
            "Memória consultada": "Mémoire consultée",
            "Pergunta recebida": "Question reçue",
            "Prompt estruturado": "Prompt structuré",
            "Resposta entregue": "Réponse livrée",
            "Resposta formatada": "Réponse formatée",
            "Router executado": "Router exécuté",
            "Tool financeira executada": "Outil financier exécuté",
        },
        "step_completed": "Étape terminée avec succès : {step}.",
        "completed": "{step} terminé avec succès.",
        "question_received_rag": ("Question reçue par le flux RAG."),
        "final_response_ready": ("Réponse finale préparée pour le tableau de bord."),
        "tool_result": (
            "Résultat de l’outil enregistré. Le temps total a été "
            "comptabilisé dans l’étape Router/Orchestrateur."
        ),
    },
    "de": {
        "steps": {
            "Busca RAG concluída": "RAG-Suche abgeschlossen",
            "Gemini executado": "Gemini ausgeführt",
            "Memória consultada": "Speicher abgerufen",
            "Pergunta recebida": "Frage empfangen",
            "Prompt estruturado": "Prompt strukturiert",
            "Resposta entregue": "Antwort ausgeliefert",
            "Resposta formatada": "Antwort formatiert",
            "Router executado": "Router ausgeführt",
            "Tool financeira executada": "Finanztool ausgeführt",
        },
        "step_completed": "Schritt erfolgreich abgeschlossen: {step}.",
        "completed": "{step} erfolgreich abgeschlossen.",
        "question_received_rag": ("Frage vom RAG-Ablauf empfangen."),
        "final_response_ready": ("Endgültige Antwort für das Dashboard vorbereitet."),
        "tool_result": (
            "Tool-Ergebnis erfasst. Die Gesamtzeit wurde dem "
            "Router-/Orchestrator-Schritt zugerechnet."
        ),
    },
    "it": {
        "steps": {
            "Busca RAG concluída": "Ricerca RAG completata",
            "Gemini executado": "Gemini eseguito",
            "Memória consultada": "Memoria consultata",
            "Pergunta recebida": "Domanda ricevuta",
            "Prompt estruturado": "Prompt strutturato",
            "Resposta entregue": "Risposta consegnata",
            "Resposta formatada": "Risposta formattata",
            "Router executado": "Router eseguito",
            "Tool financeira executada": "Strumento finanziario eseguito",
        },
        "step_completed": "Fase completata correttamente: {step}.",
        "completed": "{step} completata correttamente.",
        "question_received_rag": ("Domanda ricevuta dal flusso RAG."),
        "final_response_ready": ("Risposta finale preparata per il dashboard."),
        "tool_result": (
            "Risultato dello strumento registrato. Il tempo totale "
            "è stato conteggiato nella fase Router/Orchestratore."
        ),
    },
    "ro": {
        "steps": {
            "Busca RAG concluída": "Căutare RAG finalizată",
            "Gemini executado": "Gemini executat",
            "Memória consultada": "Memorie consultată",
            "Pergunta recebida": "Întrebare primită",
            "Prompt estruturado": "Prompt structurat",
            "Resposta entregue": "Răspuns livrat",
            "Resposta formatada": "Răspuns formatat",
            "Router executado": "Router executat",
            "Tool financeira executada": "Instrument financiar executat",
        },
        "step_completed": "Etapă finalizată cu succes: {step}.",
        "completed": "{step} finalizată cu succes.",
        "question_received_rag": ("Întrebare primită de fluxul RAG."),
        "final_response_ready": ("Răspuns final pregătit pentru dashboard."),
        "tool_result": (
            "Rezultatul instrumentului a fost înregistrat. Timpul "
            "total a fost atribuit etapei Router/Orchestrator."
        ),
    },
    "ua": {
        "steps": {
            "Busca RAG concluída": "Пошук RAG завершено",
            "Gemini executado": "Gemini виконано",
            "Memória consultada": "Пам’ять опрацьовано",
            "Pergunta recebida": "Запитання отримано",
            "Prompt estruturado": "Промпт структуровано",
            "Resposta entregue": "Відповідь доставлено",
            "Resposta formatada": "Відповідь відформатовано",
            "Router executado": "Router виконано",
            "Tool financeira executada": "Фінансовий інструмент виконано",
        },
        "step_completed": "Етап успішно завершено: {step}.",
        "completed": "{step} успішно завершено.",
        "question_received_rag": ("Запитання отримано потоком RAG."),
        "final_response_ready": ("Фінальну відповідь підготовлено для панелі."),
        "tool_result": (
            "Результат інструмента зареєстровано. Загальний час "
            "враховано на етапі Router/Оркестратор."
        ),
    },
    "ru": {
        "steps": {
            "Busca RAG concluída": "Поиск RAG завершён",
            "Gemini executado": "Gemini выполнен",
            "Memória consultada": "Память проверена",
            "Pergunta recebida": "Вопрос получен",
            "Prompt estruturado": "Промпт структурирован",
            "Resposta entregue": "Ответ доставлен",
            "Resposta formatada": "Ответ отформатирован",
            "Router executado": "Router выполнен",
            "Tool financeira executada": "Финансовый инструмент выполнен",
        },
        "step_completed": "Этап успешно завершён: {step}.",
        "completed": "{step} успешно завершён.",
        "question_received_rag": ("Вопрос получен потоком RAG."),
        "final_response_ready": ("Финальный ответ подготовлен для панели."),
        "tool_result": (
            "Результат инструмента зарегистрирован. Общее время "
            "учтено на этапе Router/Оркестратор."
        ),
    },
    "sa": {
        "steps": {
            "Busca RAG concluída": "اكتمل بحث RAG",
            "Gemini executado": "تم تنفيذ Gemini",
            "Memória consultada": "تمت مراجعة الذاكرة",
            "Pergunta recebida": "تم استلام السؤال",
            "Prompt estruturado": "تمت هيكلة الموجّه",
            "Resposta entregue": "تم تسليم الإجابة",
            "Resposta formatada": "تم تنسيق الإجابة",
            "Router executado": "تم تنفيذ الموجّه",
            "Tool financeira executada": "تم تنفيذ الأداة المالية",
        },
        "step_completed": "اكتملت المرحلة بنجاح: {step}.",
        "completed": "اكتملت بنجاح: {step}.",
        "question_received_rag": ("تم استلام السؤال بواسطة تدفق RAG."),
        "final_response_ready": ("تم إعداد الإجابة النهائية لإرسالها إلى لوحة التحكم."),
        "tool_result": (
            "تم تسجيل نتيجة الأداة. تم احتساب الوقت الإجمالي في مرحلة الموجّه والمنسق."
        ),
    },
}

TIMELINE_DYNAMIC_TEXTS["en_gb"] = TIMELINE_DYNAMIC_TEXTS["en_us"]

TIMELINE_DYNAMIC_TEXTS["ch"] = TIMELINE_DYNAMIC_TEXTS["de"]


def timeline_translate_step(
    value: Any,
) -> str:
    if value is None or pd.isna(value):
        return ""

    original = str(value).strip()
    language = timeline_lang()

    texts = TIMELINE_DYNAMIC_TEXTS.get(
        language,
        TIMELINE_DYNAMIC_TEXTS["pt"],
    )

    return texts["steps"].get(
        original,
        original,
    )


def timeline_translate_message(
    value: Any,
) -> str:
    if value is None or pd.isna(value):
        return ""

    original = str(value).strip()
    language = timeline_lang()

    texts = TIMELINE_DYNAMIC_TEXTS.get(
        language,
        TIMELINE_DYNAMIC_TEXTS["pt"],
    )

    exact_messages = {
        "Pergunta recebida pelo fluxo RAG.": (texts["question_received_rag"]),
        "Resposta final preparada para entrega ao dashboard.": (
            texts["final_response_ready"]
        ),
        (
            "Resultado da Tool registrado. O tempo total foi "
            "contabilizado na etapa do Router/Orquestrador."
        ): texts["tool_result"],
    }

    if original in exact_messages:
        return exact_messages[original]

    prefix = "Etapa concluída com sucesso: "

    if original.startswith(prefix) and original.endswith("."):
        step = original[len(prefix) : -1]

        return texts["step_completed"].format(step=timeline_translate_step(step))

    suffix = " concluída com sucesso."

    if original.endswith(suffix):
        step = original[: -len(suffix)]

        return texts["completed"].format(step=timeline_translate_step(step))

    return original


def formatar_duracao_ms(
    valor: Any,
) -> str:
    """
    Formata duração em ms ou segundos.
    """
    if valor is None or pd.isna(valor):
        return timeline_t("not_measured")

    duracao = float(valor)

    if duracao >= 1000:
        return f"{duracao / 1000:.3f} s"

    return f"{duracao:.3f} ms"


def calcular_resumo_trace(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Calcula os indicadores principais de um trace.
    """
    if df is None or df.empty:
        return {
            "total_etapas": 0,
            "total_falhas": 0,
            "total_ignoradas": 0,
            "duracao_total_ms": 0.0,
            "etapa_mais_lenta": None,
            "duracao_etapa_mais_lenta_ms": 0.0,
            "possivel_cold_start": False,
        }

    base = df.copy()

    duracoes = pd.to_numeric(
        base.get(
            "duracao_ms",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    )

    duracao_total = float(duracoes.fillna(0).sum())

    etapa_mais_lenta = None
    duracao_mais_lenta = 0.0

    if duracoes.notna().any():
        indice = duracoes.idxmax()

        etapa_mais_lenta = base.loc[
            indice,
            "etapa_label",
        ]

        duracao_mais_lenta = float(duracoes.loc[indice])

    total_falhas = int(
        (
            base.get(
                "status",
                pd.Series(dtype=str),
            )
            == "falha"
        ).sum()
    )

    total_ignoradas = int(
        (
            base.get(
                "status",
                pd.Series(dtype=str),
            )
            == "ignorado"
        ).sum()
    )

    return {
        "total_etapas": len(base),
        "total_falhas": total_falhas,
        "total_ignoradas": total_ignoradas,
        "duracao_total_ms": round(
            duracao_total,
            3,
        ),
        "etapa_mais_lenta": etapa_mais_lenta,
        "duracao_etapa_mais_lenta_ms": round(
            duracao_mais_lenta,
            3,
        ),
        "possivel_cold_start": (duracao_total >= 30000),
    }


def preparar_traces_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara a tabela de traces recentes.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    tabela = df.copy()

    tabela["Início"] = pd.to_datetime(
        tabela["inicio_trace"],
        errors="coerce",
    ).dt.strftime("%d/%m/%Y %H:%M:%S")

    tabela["Duração total"] = tabela["duracao_total_ms"].apply(formatar_duracao_ms)

    tabela["Status"] = tabela["total_falhas"].apply(
        lambda total: (
            timeline_t("with_failure") if int(total or 0) > 0 else timeline_t("success")
        )
    )

    tabela["Cold start"] = tabela["duracao_total_ms"].apply(
        lambda valor: (
            timeline_t("possible") if float(valor or 0) >= 30000 else timeline_t("no")
        )
    )

    colunas = [
        "trace_id",
        "Início",
        "usuario_id",
        "pergunta",
        "total_etapas",
        "total_falhas",
        "Duração total",
        "Cold start",
        "origem",
        "Status",
    ]

    return tabela[[coluna for coluna in colunas if coluna in tabela.columns]].rename(
        columns={
            "trace_id": "Trace ID",
            "usuario_id": "Usuário",
            "pergunta": "Pergunta",
            "total_etapas": "Etapas",
            "total_falhas": "Falhas",
            "origem": "Origem",
        }
    )


def preparar_timeline_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara as etapas de um trace.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    tabela = df.copy()

    tabela["etapa_label"] = tabela["etapa_label"].map(timeline_translate_step)

    if "mensagem" in tabela.columns:
        tabela["mensagem"] = tabela["mensagem"].map(timeline_translate_message)

    tabela["Status visual"] = (
        tabela["status"].map(timeline_status_labels()).fillna(tabela["status"])
    )

    tabela["Duração"] = tabela["duracao_ms"].apply(formatar_duracao_ms)

    tabela["Início"] = (
        pd.to_datetime(
            tabela["inicio_em"],
            errors="coerce",
        )
        .dt.strftime("%H:%M:%S.%f")
        .str[:-3]
    )

    colunas = [
        "ordem",
        "etapa_label",
        "Status visual",
        "Duração",
        "Início",
        "mensagem",
        "erro",
    ]

    return tabela[[coluna for coluna in colunas if coluna in tabela.columns]].rename(
        columns={
            "ordem": "Ordem",
            "etapa_label": "Etapa",
            "mensagem": "Mensagem",
            "erro": "Erro",
        }
    )


def render_etapas_timeline(
    df: pd.DataFrame,
) -> None:
    """
    Renderiza a sequência visual das etapas.
    """
    for _, evento in df.sort_values(
        by=[
            "ordem",
            "criado_em",
        ]
    ).iterrows():
        status = str(evento.get("status") or "")

        simbolo = {
            "sucesso": "✅",
            "falha": "❌",
            "ignorado": "⏭️",
            "iniciado": "🔄",
        }.get(
            status,
            "ℹ️",
        )

        etapa = timeline_translate_step(evento.get("etapa_label"))

        duracao = formatar_duracao_ms(evento.get("duracao_ms"))

        with st.container(border=True):
            col_1, col_2, col_3 = st.columns([0.5, 3, 1.2])

            col_1.markdown(f"### {simbolo}")

            col_2.markdown(f"**{etapa}**")

            col_2.caption(timeline_translate_message(evento.get("mensagem")))

            col_3.metric(
                timeline_t("duration"),
                duracao,
            )

            erro = evento.get("erro")

            if erro and not pd.isna(erro):
                st.error(str(erro))

            metadata = evento.get("metadata")

            if metadata:
                with st.popover(timeline_t("view_metadata")):
                    if isinstance(
                        metadata,
                        str,
                    ):
                        try:
                            metadata = json.loads(metadata)
                        except Exception:
                            pass

                    st.json(metadata)


def calcular_diferenca_traces(
    duracao_a_ms: float,
    duracao_b_ms: float,
) -> dict[str, float]:
    """
    Calcula diferença absoluta e percentual entre traces.

    O percentual usa o Trace A como referência.
    """
    duracao_a = float(duracao_a_ms or 0)

    duracao_b = float(duracao_b_ms or 0)

    diferenca_absoluta = duracao_b - duracao_a

    diferenca_percentual = (
        (diferenca_absoluta / duracao_a) * 100 if duracao_a > 0 else 0.0
    )

    return {
        "diferenca_absoluta_ms": round(
            diferenca_absoluta,
            3,
        ),
        "diferenca_percentual": round(
            diferenca_percentual,
            2,
        ),
    }


def render_comparacao_traces(
    traces_df: pd.DataFrame,
) -> None:
    """
    Compara dois traces com filtro de cold start,
    escala selecionável e diferença percentual.
    """
    if traces_df is None or len(traces_df) < 2:
        st.info(timeline_t("minimum_two_traces"))
        return

    base = traces_df.copy()

    ignorar_cold_start = st.checkbox(
        timeline_t("ignore_cold_start"),
        value=False,
        key="timeline_compare_ignore_cold_start",
    )

    if ignorar_cold_start:
        base = base[
            pd.to_numeric(
                base["duracao_total_ms"],
                errors="coerce",
            ).fillna(0)
            < 30000
        ]

    if len(base) < 2:
        st.warning(timeline_t("not_enough_after_filter"))
        return

    escala = st.radio(
        timeline_t("chart_scale"),
        options=[
            "linear",
            "logarithmic",
        ],
        format_func=lambda value: timeline_t(value),
        horizontal=True,
        key="timeline_compare_scale",
    )

    opcoes = base["trace_id"].astype(str).tolist()

    col_1, col_2 = st.columns(2)

    trace_a = col_1.selectbox(
        "Trace A",
        options=opcoes,
        index=0,
        key="timeline_compare_a",
    )

    trace_b = col_2.selectbox(
        "Trace B",
        options=opcoes,
        index=min(
            1,
            len(opcoes) - 1,
        ),
        key="timeline_compare_b",
    )

    if trace_a == trace_b:
        st.warning(timeline_t("different_traces"))
        return

    try:
        from observability.timeline import (
            carregar_timeline_trace,
        )
    except ImportError:
        from src.observability.timeline import (
            carregar_timeline_trace,
        )

    resultado_a = carregar_timeline_trace(trace_a)

    resultado_b = carregar_timeline_trace(trace_b)

    df_a = resultado_a.get("df")
    df_b = resultado_b.get("df")

    resumo_a = calcular_resumo_trace(df_a)

    resumo_b = calcular_resumo_trace(df_b)

    duracao_a = float(resumo_a["duracao_total_ms"])

    duracao_b = float(resumo_b["duracao_total_ms"])

    diferenca = calcular_diferenca_traces(
        duracao_a,
        duracao_b,
    )

    diferenca_absoluta = diferenca["diferenca_absoluta_ms"]

    diferenca_percentual = diferenca["diferenca_percentual"]

    comparacao = pd.DataFrame(
        [
            {
                "Trace": "A",
                "Trace ID": trace_a,
                "Etapas": resumo_a["total_etapas"],
                "Falhas": resumo_a["total_falhas"],
                "Duração total": (formatar_duracao_ms(duracao_a)),
                "Etapa mais lenta": (
                    timeline_translate_step(resumo_a["etapa_mais_lenta"])
                ),
                "Cold start": (
                    timeline_t("possible")
                    if resumo_a["possivel_cold_start"]
                    else timeline_t("no")
                ),
            },
            {
                "Trace": "B",
                "Trace ID": trace_b,
                "Etapas": resumo_b["total_etapas"],
                "Falhas": resumo_b["total_falhas"],
                "Duração total": (formatar_duracao_ms(duracao_b)),
                "Etapa mais lenta": (
                    timeline_translate_step(resumo_b["etapa_mais_lenta"])
                ),
                "Cold start": (
                    timeline_t("possible")
                    if resumo_b["possivel_cold_start"]
                    else timeline_t("no")
                ),
            },
        ]
    )

    comparacao_exibicao = comparacao.rename(
        columns={
            "Etapas": timeline_t("steps"),
            "Falhas": timeline_t("failures"),
            "Duração total": timeline_t("total_duration"),
            "Etapa mais lenta": timeline_t("slowest_step_column"),
            "Cold start": timeline_t("cold_start"),
        }
    )

    st.dataframe(
        comparacao_exibicao,
        use_container_width=True,
        hide_index=True,
    )

    if diferenca_percentual > 0:
        st.warning(
            timeline_t("trace_b_slower").format(percent=abs(diferenca_percentual))
        )

    elif diferenca_percentual < 0:
        st.success(
            timeline_t("trace_b_faster").format(percent=abs(diferenca_percentual))
        )

    else:
        st.info(timeline_t("same_duration"))

    col_delta_1, col_delta_2 = st.columns(2)

    col_delta_1.metric(
        timeline_t("absolute_difference"),
        formatar_duracao_ms(abs(diferenca_absoluta)),
    )

    col_delta_2.metric(
        timeline_t("percentage_difference"),
        f"{abs(diferenca_percentual):.2f}%",
    )

    etapas_a = df_a[
        [
            "etapa_label",
            "duracao_ms",
        ]
    ].rename(
        columns={
            "duracao_ms": "Trace A",
        }
    )

    etapas_b = df_b[
        [
            "etapa_label",
            "duracao_ms",
        ]
    ].rename(
        columns={
            "duracao_ms": "Trace B",
        }
    )

    grafico = etapas_a.merge(
        etapas_b,
        on="etapa_label",
        how="outer",
    ).fillna(0)

    grafico["etapa_label"] = grafico["etapa_label"].map(timeline_translate_step)

    grafico["Trace A"] = pd.to_numeric(
        grafico["Trace A"],
        errors="coerce",
    ).fillna(0)

    grafico["Trace B"] = pd.to_numeric(
        grafico["Trace B"],
        errors="coerce",
    ).fillna(0)

    if escala == "logarithmic":
        import numpy as np

        grafico_plot = grafico.copy()

        grafico_plot["Trace A"] = np.log10(grafico_plot["Trace A"] + 1)

        grafico_plot["Trace B"] = np.log10(grafico_plot["Trace B"] + 1)

        st.caption(timeline_t("log_caption"))
    else:
        grafico_plot = grafico

    grafico_real_longo = grafico.melt(
        id_vars="etapa_label",
        value_vars=[
            "Trace A",
            "Trace B",
        ],
        var_name="Trace",
        value_name="Duracao_real_ms",
    )

    grafico_plot_longo = grafico_plot.melt(
        id_vars="etapa_label",
        value_vars=[
            "Trace A",
            "Trace B",
        ],
        var_name="Trace",
        value_name="Valor_grafico",
    )

    grafico_longo = grafico_plot_longo.merge(
        grafico_real_longo,
        on=[
            "etapa_label",
            "Trace",
        ],
        how="left",
    )

    grafico_longo["Duração formatada"] = grafico_longo["Duracao_real_ms"].map(
        formatar_duracao_ms
    )

    ordem_etapas = (
        grafico.assign(
            duracao_maxima=grafico[
                [
                    "Trace A",
                    "Trace B",
                ]
            ].max(axis=1)
        )
        .sort_values(
            "duracao_maxima",
            ascending=True,
        )["etapa_label"]
        .tolist()
    )

    fig_comparacao = px.bar(
        grafico_longo,
        x="Valor_grafico",
        y="etapa_label",
        color="Trace",
        orientation="h",
        barmode="group",
        text="Duração formatada",
        custom_data=[
            "Duração formatada",
            "Duracao_real_ms",
        ],
        color_discrete_map={
            "Trace A": "#38BDF8",
            "Trace B": "#A78BFA",
        },
    )

    fig_comparacao.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>%{fullData.name}: %{customdata[0]}<extra></extra>"
        ),
    )

    titulo_eixo = (
        timeline_t("log_axis")
        if escala == "logarithmic"
        else timeline_t("duration_axis")
    )

    fig_comparacao.update_layout(
        xaxis_title=titulo_eixo,
        yaxis_title=None,
        legend_title_text=None,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    fig_comparacao.update_yaxes(
        categoryorder="array",
        categoryarray=ordem_etapas,
    )

    aplicar_tema_timeline_chart(
        fig_comparacao,
        height=max(
            420,
            150 + len(ordem_etapas) * 62,
        ),
    )

    st.plotly_chart(
        fig_comparacao,
        width="stretch",
        key="timeline_trace_comparison_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


def render_timeline_viewer_page() -> None:
    """
    Renderiza o Timeline Viewer.
    """
    try:
        from observability.timeline import (
            carregar_timeline_trace,
            carregar_traces_recentes,
        )
    except ImportError:
        from src.observability.timeline import (
            carregar_timeline_trace,
            carregar_traces_recentes,
        )

    st.title(timeline_t("page_title"))

    st.caption(timeline_t("page_caption"))

    col_1, col_2 = st.columns([1, 3])

    limite = col_1.selectbox(
        timeline_t("trace_quantity"),
        options=[
            10,
            25,
            50,
            100,
        ],
        index=1,
        key="timeline_viewer_limit",
    )

    with col_2:
        st.write("")

        if st.button(
            timeline_t("refresh"),
            use_container_width=True,
            key="timeline_viewer_refresh",
        ):
            st.rerun()

    resultado_traces = carregar_traces_recentes(limite=int(limite))

    if not resultado_traces.get("ok"):
        st.error(resultado_traces.get("message"))
        return

    traces_df = resultado_traces.get("df")

    if traces_df is None or traces_df.empty:
        st.info(timeline_t("no_traces"))
        return

    st.markdown(timeline_t("search_filters"))

    pesquisa = st.text_input(
        timeline_t("search_label"),
        placeholder=timeline_t("search_placeholder"),
        key="timeline_viewer_search",
    )

    filtro_1, filtro_2 = st.columns(2)

    usuarios = sorted(traces_df["usuario_id"].dropna().astype(str).unique().tolist())

    origens = sorted(traces_df["origem"].dropna().astype(str).unique().tolist())

    usuario = filtro_1.selectbox(
        timeline_t("user"),
        options=["__all__"] + usuarios,
        format_func=lambda value: (
            timeline_t("all_masculine") if value == "__all__" else value
        ),
        key="timeline_viewer_user",
    )

    origem = filtro_2.selectbox(
        timeline_t("origin"),
        options=["__all__"] + origens,
        format_func=lambda value: (
            timeline_t("all_feminine") if value == "__all__" else value
        ),
        key="timeline_viewer_origin",
    )

    somente_falhas = st.checkbox(
        timeline_t("only_failures"),
        value=False,
        key="timeline_viewer_failures",
    )

    filtrado = traces_df.copy()

    if pesquisa.strip():
        termo = pesquisa.strip().lower()

        mascara = (
            filtrado["trace_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                termo,
                regex=False,
            )
        )

        for coluna in [
            "usuario_id",
            "pergunta",
        ]:
            if coluna in filtrado.columns:
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

    if usuario != "__all__":
        filtrado = filtrado[filtrado["usuario_id"].astype(str) == usuario]

    if origem != "__all__":
        filtrado = filtrado[filtrado["origem"].astype(str) == origem]

    if somente_falhas:
        filtrado = filtrado[filtrado["total_falhas"] > 0]

    st.caption(timeline_t("traces_found").format(count=len(filtrado)))

    st.markdown(timeline_t("recent_traces"))

    traces_exibicao = preparar_traces_exibicao(filtrado).rename(
        columns={
            "Início": timeline_t("start"),
            "Usuário": timeline_t("user"),
            "Pergunta": timeline_t("question").removeprefix("### "),
            "Etapas": timeline_t("steps"),
            "Falhas": timeline_t("failures"),
            "Duração total": timeline_t("total_duration"),
            "Cold start": timeline_t("cold_start"),
            "Origem": timeline_t("origin"),
            "Status": timeline_t("status"),
        }
    )

    st.dataframe(
        traces_exibicao,
        use_container_width=True,
        hide_index=True,
    )

    if filtrado.empty:
        return

    opcoes_trace = filtrado["trace_id"].astype(str).tolist()

    trace_selecionado = st.selectbox(
        timeline_t("select_trace"),
        options=opcoes_trace,
        key="timeline_viewer_trace",
    )

    resultado_timeline = carregar_timeline_trace(trace_selecionado)

    if not resultado_timeline.get("ok"):
        st.error(resultado_timeline.get("message"))
        return

    timeline_df = resultado_timeline.get("df")

    resumo = calcular_resumo_trace(timeline_df)

    st.divider()
    st.markdown(timeline_t("execution_summary"))

    linha_1 = st.columns(4)

    linha_1[0].metric(
        timeline_t("steps"),
        resumo["total_etapas"],
    )

    linha_1[1].metric(
        timeline_t("failures"),
        resumo["total_falhas"],
    )

    linha_1[2].metric(
        timeline_t("ignored"),
        resumo["total_ignoradas"],
    )

    linha_1[3].metric(
        timeline_t("total_duration"),
        formatar_duracao_ms(resumo["duracao_total_ms"]),
    )

    if resumo["possivel_cold_start"]:
        st.warning(timeline_t("cold_start_warning"))
    else:
        st.success(timeline_t("execution_ok"))

    if resumo["etapa_mais_lenta"]:
        duracao_etapa_mais_lenta = formatar_duracao_ms(
            resumo["duracao_etapa_mais_lenta_ms"]
        )

        st.info(
            timeline_t("slowest_step")
            + ": "
            + timeline_translate_step(resumo["etapa_mais_lenta"])
            + " — "
            + duracao_etapa_mais_lenta
        )

    pergunta = timeline_df["pergunta"].dropna().astype(str)

    if not pergunta.empty:
        st.markdown(timeline_t("question"))

        st.code(
            pergunta.iloc[0],
            language=None,
        )

    st.markdown(timeline_t("execution_path"))

    render_etapas_timeline(timeline_df)

    st.markdown(timeline_t("technical_table"))

    timeline_exibicao = preparar_timeline_exibicao(timeline_df).rename(
        columns={
            "Ordem": timeline_t("order"),
            "Etapa": timeline_t("step"),
            "Status visual": timeline_t("status"),
            "Duração": timeline_t("duration"),
            "Início": timeline_t("start"),
            "Mensagem": timeline_t("message"),
            "Erro": timeline_t("error"),
        }
    )

    st.dataframe(
        timeline_exibicao,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown(timeline_t("compare_traces"))

    render_comparacao_traces(traces_df)


__all__ = [
    "STATUS_LABELS",
    "formatar_duracao_ms",
    "calcular_resumo_trace",
    "calcular_diferenca_traces",
    "preparar_traces_exibicao",
    "preparar_timeline_exibicao",
    "render_etapas_timeline",
    "render_comparacao_traces",
    "render_timeline_viewer_page",
]

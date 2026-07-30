from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard_theme import apply_admin_dark_theme

from src.evaluation.dashboard_data import (
    build_dashboard_summary,
    build_metric_series,
    build_metric_snapshot,
    build_pass_rate_series,
    build_runs_table,
    filter_history,
    get_metric_ids,
    load_dashboard_history,
)
from src.observability.infrastructure_health import (
    collect_infrastructure_health,
)
from src.observability.phoenix_runtime import (
    initialize_phoenix,
)

LLMOPS_CHART_BG = "#020617"
LLMOPS_CHART_TEXT = "#F8FAFC"
LLMOPS_CHART_GRID = (
    "rgba(148, 163, 184, 0.16)"
)

LLMOPS_METRIC_COLORS = [
    "#38BDF8",
    "#34D399",
    "#A78BFA",
    "#F59E0B",
    "#F87171",
    "#22D3EE",
    "#FB7185",
    "#C084FC",
]


def aplicar_tema_llmops_chart(
    fig,
    *,
    height=440,
):
    """Aplica o tema visual do INNA LLMOps."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=LLMOPS_CHART_BG,
        plot_bgcolor=LLMOPS_CHART_BG,
        font={
            "color": LLMOPS_CHART_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": LLMOPS_CHART_TEXT,
        },
        margin={
            "l": 38,
            "r": 28,
            "t": 25,
            "b": 48,
        },
        height=height,
    )

    fig.update_xaxes(
        color=LLMOPS_CHART_TEXT,
        gridcolor=LLMOPS_CHART_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    fig.update_yaxes(
        color=LLMOPS_CHART_TEXT,
        gridcolor=LLMOPS_CHART_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    return fig


DEFAULT_HISTORY_PATH = Path(
    "evaluation/history/evaluation-history.json"
)


LLMOPS_TEXTS = {
    "pt": {
        "title": "🛰️ Operações de IA (LLMOps) e Observabilidade da INNA",
        "caption": (
            "Monitoramento de qualidade, regressões, baselines "
            "e tendências das avaliações de Inteligência Artificial."
        ),
        "latest_snapshot": "Snapshot da execução mais recente",
        "runs_history": "Histórico de execuções",
        "no_registered_run": "Nenhuma execução registrada.",
        "no_filtered_runs": (
            "Nenhuma execução encontrada para os filtros selecionados."
        ),
        "pass_rate": "Taxa de aprovação",
        "approved": "Aprovada",
        "quality_gate": "Quality Gate",
    },
    "en_us": {
        "title": "🛰️ INNA AI Operations (LLMOps) and Observability",
        "caption": (
            "Monitoring of quality, regressions, baselines "
            "and trends in Artificial Intelligence evaluations."
        ),
        "latest_snapshot": "Latest execution snapshot",
        "runs_history": "Execution history",
        "no_registered_run": "No execution has been recorded.",
        "no_filtered_runs": (
            "No execution was found for the selected filters."
        ),
        "pass_rate": "Pass rate",
        "approved": "Approved",
        "quality_gate": "Quality Gate",
    },
    "en_gb": {
        "title": "🛰️ INNA AI Operations (LLMOps) and Observability",
        "caption": (
            "Monitoring of quality, regressions, baselines "
            "and trends in Artificial Intelligence evaluations."
        ),
        "latest_snapshot": "Latest execution snapshot",
        "runs_history": "Execution history",
        "no_registered_run": "No execution has been recorded.",
        "no_filtered_runs": (
            "No execution was found for the selected filters."
        ),
        "pass_rate": "Pass rate",
        "approved": "Approved",
        "quality_gate": "Quality Gate",
    },
    "es": {
        "title": "🛰️ Operaciones de IA (LLMOps) y Observabilidad de INNA",
        "caption": (
            "Monitoreo de calidad, regresiones, líneas base "
            "y tendencias de las evaluaciones de Inteligencia Artificial."
        ),
        "latest_snapshot": "Instantánea de la ejecución más reciente",
        "runs_history": "Historial de ejecuciones",
        "no_registered_run": "No hay ninguna ejecución registrada.",
        "no_filtered_runs": (
            "No se encontraron ejecuciones para los filtros seleccionados."
        ),
        "pass_rate": "Tasa de aprobación",
        "approved": "Aprobada",
        "quality_gate": "Puerta de calidad",
    },
    "fr": {
        "title": "🛰️ Opérations IA (LLMOps) et Observabilité d’INNA",
        "caption": (
            "Suivi de la qualité, des régressions, des références "
            "et des tendances des évaluations d’intelligence artificielle."
        ),
        "latest_snapshot": "Aperçu de la dernière exécution",
        "runs_history": "Historique des exécutions",
        "no_registered_run": "Aucune exécution enregistrée.",
        "no_filtered_runs": (
            "Aucune exécution trouvée pour les filtres sélectionnés."
        ),
        "pass_rate": "Taux de réussite",
        "approved": "Approuvée",
        "quality_gate": "Contrôle qualité",
    },
    "de": {
        "title": "🛰️ INNA KI-Betrieb (LLMOps) und Beobachtbarkeit",
        "caption": (
            "Überwachung von Qualität, Regressionen, Baselines "
            "und Trends der KI-Auswertungen."
        ),
        "latest_snapshot": "Snapshot der neuesten Ausführung",
        "runs_history": "Ausführungsverlauf",
        "no_registered_run": "Keine Ausführung registriert.",
        "no_filtered_runs": (
            "Keine Ausführung für die ausgewählten Filter gefunden."
        ),
        "pass_rate": "Erfolgsquote",
        "approved": "Genehmigt",
        "quality_gate": "Qualitätsprüfung",
    },
    "it": {
        "title": "🛰️ Operazioni IA (LLMOps) e Osservabilità di INNA",
        "caption": (
            "Monitoraggio di qualità, regressioni, baseline "
            "e tendenze delle valutazioni di intelligenza artificiale."
        ),
        "latest_snapshot": "Snapshot dell’esecuzione più recente",
        "runs_history": "Cronologia delle esecuzioni",
        "no_registered_run": "Nessuna esecuzione registrata.",
        "no_filtered_runs": (
            "Nessuna esecuzione trovata per i filtri selezionati."
        ),
        "pass_rate": "Tasso di approvazione",
        "approved": "Approvata",
        "quality_gate": "Controllo qualità",
    },
    "ro": {
        "title": "🛰️ Operațiuni IA (LLMOps) și Observabilitate INNA",
        "caption": (
            "Monitorizarea calității, regresiilor, valorilor de referință "
            "și tendințelor evaluărilor de inteligență artificială."
        ),
        "latest_snapshot": "Instantaneul celei mai recente execuții",
        "runs_history": "Istoricul execuțiilor",
        "no_registered_run": "Nu există nicio execuție înregistrată.",
        "no_filtered_runs": (
            "Nu a fost găsită nicio execuție pentru filtrele selectate."
        ),
        "pass_rate": "Rată de aprobare",
        "approved": "Aprobată",
        "quality_gate": "Controlul calității",
    },
    "ua": {
        "title": "🛰️ Операції ШІ (LLMOps) та спостережуваність INNA",
        "caption": (
            "Моніторинг якості, регресій, базових показників "
            "і тенденцій оцінювання штучного інтелекту."
        ),
        "latest_snapshot": "Знімок останнього виконання",
        "runs_history": "Історія виконань",
        "no_registered_run": "Немає зареєстрованих виконань.",
        "no_filtered_runs": (
            "Для вибраних фільтрів виконань не знайдено."
        ),
        "pass_rate": "Рівень успішності",
        "approved": "Схвалено",
        "quality_gate": "Контроль якості",
    },
    "ru": {
        "title": "🛰️ Операции ИИ (LLMOps) и наблюдаемость INNA",
        "caption": (
            "Мониторинг качества, регрессий, базовых показателей "
            "и тенденций оценки искусственного интеллекта."
        ),
        "latest_snapshot": "Снимок последнего выполнения",
        "runs_history": "История выполнений",
        "no_registered_run": "Нет зарегистрированных выполнений.",
        "no_filtered_runs": (
            "Для выбранных фильтров выполнения не найдены."
        ),
        "pass_rate": "Уровень успешности",
        "approved": "Одобрено",
        "quality_gate": "Контроль качества",
    },
    "sa": {
        "title": "🛰️ عمليات الذكاء الاصطناعي (LLMOps) والمراقبة في INNA",
        "caption": (
            "مراقبة الجودة والانحدارات والخطوط الأساسية "
            "واتجاهات تقييمات الذكاء الاصطناعي."
        ),
        "latest_snapshot": "لقطة لأحدث عملية تشغيل",
        "runs_history": "سجل عمليات التشغيل",
        "no_registered_run": "لا توجد عملية تشغيل مسجلة.",
        "no_filtered_runs": (
            "لم يتم العثور على عمليات تشغيل للفلاتر المحددة."
        ),
        "pass_rate": "معدل النجاح",
        "approved": "معتمدة",
        "quality_gate": "بوابة الجودة",
    },
}


# LLMOps filter and summary translations.
LLMOPS_FILTER_SUMMARY_TEXTS = {'pt': {'filters': 'Filtros', 'branches': 'Branches', 'environments': 'Ambientes', 'run_status': 'Status da execução', 'all_runs': 'Todas', 'approved_runs_option': 'Aprovadas', 'failed_runs_option': 'Reprovadas', 'total_runs': 'Execuções', 'approval_rate': 'Taxa de aprovação', 'latest_pass_rate': 'Taxa de aprovação mais recente', 'tracked_metrics': 'Métricas monitoradas', 'approved_runs': 'Execuções aprovadas', 'failed_runs': 'Execuções reprovadas', 'recent_regressions': 'Regressões recentes', 'recent_violations': 'Violações recentes', 'gate_approved': 'Quality Gate mais recente: aprovado.', 'gate_failed': 'Quality Gate mais recente: reprovado.', 'no_runs': 'Nenhuma execução disponível.'}, 'en_us': {'filters': 'Filters', 'branches': 'Branches', 'environments': 'Environments', 'run_status': 'Execution status', 'all_runs': 'All', 'approved_runs_option': 'Approved', 'failed_runs_option': 'Failed', 'total_runs': 'Executions', 'approval_rate': 'Approval rate', 'latest_pass_rate': 'Latest pass rate', 'tracked_metrics': 'Tracked metrics', 'approved_runs': 'Approved executions', 'failed_runs': 'Failed executions', 'recent_regressions': 'Recent regressions', 'recent_violations': 'Recent violations', 'gate_approved': 'Latest Quality Gate: approved.', 'gate_failed': 'Latest Quality Gate: failed.', 'no_runs': 'No execution is available.'}, 'es': {'filters': 'Filtros', 'branches': 'Ramas', 'environments': 'Entornos', 'run_status': 'Estado de la ejecución', 'all_runs': 'Todas', 'approved_runs_option': 'Aprobadas', 'failed_runs_option': 'Reprobadas', 'total_runs': 'Ejecuciones', 'approval_rate': 'Tasa de aprobación', 'latest_pass_rate': 'Última tasa de aprobación', 'tracked_metrics': 'Métricas monitoreadas', 'approved_runs': 'Ejecuciones aprobadas', 'failed_runs': 'Ejecuciones reprobadas', 'recent_regressions': 'Regresiones recientes', 'recent_violations': 'Infracciones recientes', 'gate_approved': 'Última puerta de calidad: aprobada.', 'gate_failed': 'Última puerta de calidad: reprobada.', 'no_runs': 'No hay ejecuciones disponibles.'}, 'fr': {'filters': 'Filtres', 'branches': 'Branches', 'environments': 'Environnements', 'run_status': 'État de l’exécution', 'all_runs': 'Toutes', 'approved_runs_option': 'Approuvées', 'failed_runs_option': 'Échouées', 'total_runs': 'Exécutions', 'approval_rate': 'Taux d’approbation', 'latest_pass_rate': 'Dernier taux de réussite', 'tracked_metrics': 'Métriques surveillées', 'approved_runs': 'Exécutions approuvées', 'failed_runs': 'Exécutions échouées', 'recent_regressions': 'Régressions récentes', 'recent_violations': 'Violations récentes', 'gate_approved': 'Dernier contrôle qualité : approuvé.', 'gate_failed': 'Dernier contrôle qualité : échoué.', 'no_runs': 'Aucune exécution disponible.'}, 'de': {'filters': 'Filter', 'branches': 'Branches', 'environments': 'Umgebungen', 'run_status': 'Ausführungsstatus', 'all_runs': 'Alle', 'approved_runs_option': 'Genehmigt', 'failed_runs_option': 'Fehlgeschlagen', 'total_runs': 'Ausführungen', 'approval_rate': 'Genehmigungsquote', 'latest_pass_rate': 'Neueste Erfolgsquote', 'tracked_metrics': 'Überwachte Metriken', 'approved_runs': 'Genehmigte Ausführungen', 'failed_runs': 'Fehlgeschlagene Ausführungen', 'recent_regressions': 'Aktuelle Regressionen', 'recent_violations': 'Aktuelle Verstöße', 'gate_approved': 'Neueste Qualitätsprüfung: genehmigt.', 'gate_failed': 'Neueste Qualitätsprüfung: fehlgeschlagen.', 'no_runs': 'Keine Ausführung verfügbar.'}, 'it': {'filters': 'Filtri', 'branches': 'Branch', 'environments': 'Ambienti', 'run_status': 'Stato dell’esecuzione', 'all_runs': 'Tutte', 'approved_runs_option': 'Approvate', 'failed_runs_option': 'Non approvate', 'total_runs': 'Esecuzioni', 'approval_rate': 'Tasso di approvazione', 'latest_pass_rate': 'Ultimo tasso di approvazione', 'tracked_metrics': 'Metriche monitorate', 'approved_runs': 'Esecuzioni approvate', 'failed_runs': 'Esecuzioni non approvate', 'recent_regressions': 'Regressioni recenti', 'recent_violations': 'Violazioni recenti', 'gate_approved': 'Ultimo controllo qualità: approvato.', 'gate_failed': 'Ultimo controllo qualità: non approvato.', 'no_runs': 'Nessuna esecuzione disponibile.'}, 'ro': {'filters': 'Filtre', 'branches': 'Ramuri', 'environments': 'Medii', 'run_status': 'Starea execuției', 'all_runs': 'Toate', 'approved_runs_option': 'Aprobate', 'failed_runs_option': 'Respinse', 'total_runs': 'Execuții', 'approval_rate': 'Rată de aprobare', 'latest_pass_rate': 'Cea mai recentă rată de aprobare', 'tracked_metrics': 'Metrici monitorizate', 'approved_runs': 'Execuții aprobate', 'failed_runs': 'Execuții respinse', 'recent_regressions': 'Regresii recente', 'recent_violations': 'Încălcări recente', 'gate_approved': 'Cel mai recent control: aprobat.', 'gate_failed': 'Cel mai recent control: respins.', 'no_runs': 'Nu există execuții disponibile.'}, 'ua': {'filters': 'Фільтри', 'branches': 'Гілки', 'environments': 'Середовища', 'run_status': 'Статус виконання', 'all_runs': 'Усі', 'approved_runs_option': 'Схвалені', 'failed_runs_option': 'Відхилені', 'total_runs': 'Виконання', 'approval_rate': 'Рівень схвалення', 'latest_pass_rate': 'Останній рівень успішності', 'tracked_metrics': 'Відстежувані метрики', 'approved_runs': 'Схвалені виконання', 'failed_runs': 'Відхилені виконання', 'recent_regressions': 'Останні регресії', 'recent_violations': 'Останні порушення', 'gate_approved': 'Останній контроль якості: схвалено.', 'gate_failed': 'Останній контроль якості: відхилено.', 'no_runs': 'Немає доступних виконань.'}, 'ru': {'filters': 'Фильтры', 'branches': 'Ветки', 'environments': 'Среды', 'run_status': 'Статус выполнения', 'all_runs': 'Все', 'approved_runs_option': 'Одобрено', 'failed_runs_option': 'Отклонено', 'total_runs': 'Выполнения', 'approval_rate': 'Уровень одобрения', 'latest_pass_rate': 'Последний уровень успешности', 'tracked_metrics': 'Отслеживаемые метрики', 'approved_runs': 'Одобренные выполнения', 'failed_runs': 'Отклонённые выполнения', 'recent_regressions': 'Последние регрессии', 'recent_violations': 'Последние нарушения', 'gate_approved': 'Последний контроль качества: одобрено.', 'gate_failed': 'Последний контроль качества: отклонено.', 'no_runs': 'Нет доступных выполнений.'}, 'sa': {'filters': 'الفلاتر', 'branches': 'الفروع', 'environments': 'البيئات', 'run_status': 'حالة التشغيل', 'all_runs': 'الكل', 'approved_runs_option': 'معتمدة', 'failed_runs_option': 'مرفوضة', 'total_runs': 'عمليات التشغيل', 'approval_rate': 'معدل الاعتماد', 'latest_pass_rate': 'أحدث معدل نجاح', 'tracked_metrics': 'المقاييس المراقبة', 'approved_runs': 'عمليات معتمدة', 'failed_runs': 'عمليات مرفوضة', 'recent_regressions': 'الانحدارات الأخيرة', 'recent_violations': 'المخالفات الأخيرة', 'gate_approved': 'أحدث بوابة جودة: معتمدة.', 'gate_failed': 'أحدث بوابة جودة: مرفوضة.', 'no_runs': 'لا توجد عمليات تشغيل متاحة.'}, 'en_gb': {'filters': 'Filters', 'branches': 'Branches', 'environments': 'Environments', 'run_status': 'Execution status', 'all_runs': 'All', 'approved_runs_option': 'Approved', 'failed_runs_option': 'Failed', 'total_runs': 'Executions', 'approval_rate': 'Approval rate', 'latest_pass_rate': 'Latest pass rate', 'tracked_metrics': 'Tracked metrics', 'approved_runs': 'Approved executions', 'failed_runs': 'Failed executions', 'recent_regressions': 'Recent regressions', 'recent_violations': 'Recent violations', 'gate_approved': 'Latest Quality Gate: approved.', 'gate_failed': 'Latest Quality Gate: failed.', 'no_runs': 'No execution is available.'}, 'ch': {'filters': 'Filter', 'branches': 'Branches', 'environments': 'Umgebungen', 'run_status': 'Ausführungsstatus', 'all_runs': 'Alle', 'approved_runs_option': 'Genehmigt', 'failed_runs_option': 'Fehlgeschlagen', 'total_runs': 'Ausführungen', 'approval_rate': 'Genehmigungsquote', 'latest_pass_rate': 'Neueste Erfolgsquote', 'tracked_metrics': 'Überwachte Metriken', 'approved_runs': 'Genehmigte Ausführungen', 'failed_runs': 'Fehlgeschlagene Ausführungen', 'recent_regressions': 'Aktuelle Regressionen', 'recent_violations': 'Aktuelle Verstöße', 'gate_approved': 'Neueste Qualitätsprüfung: genehmigt.', 'gate_failed': 'Neueste Qualitätsprüfung: fehlgeschlagen.', 'no_runs': 'Keine Ausführung verfügbar.'}}

for idioma, textos in LLMOPS_FILTER_SUMMARY_TEXTS.items():
    LLMOPS_TEXTS.setdefault(idioma, {}).update(textos)


LLMOPS_INFRA_TEXTS = {'pt': {'infra_error': 'Não foi possível coletar o status da infraestrutura neste momento.', 'technical_details': 'Detalhes técnicos', 'infrastructure_title': 'Infraestrutura e observabilidade', 'operational': 'Operacional', 'degraded': 'Degradada', 'unavailable': 'Indisponível', 'general_status': 'Status geral', 'available': 'Disponível', 'inactive': 'Inativo', 'active': 'Ativo', 'no_measurement': 'sem medição', 'sample': 'Amostragem', 'project': 'Projeto', 'execution': 'Execução', 'local': 'Local', 'service': 'Serviço', 'infrastructure_details': 'Detalhes técnicos da infraestrutura', 'pool_size': 'Tamanho do pool', 'available_connections': 'Conexões disponíveis', 'waiting_requests': 'Requisições aguardando', 'application_tracing': 'Aplicação e rastreamento', 'environment': 'Ambiente', 'region': 'Região', 'phoenix_processor': 'Processador do Phoenix', 'content_capture': 'Captura de conteúdo', 'unavailable_components': 'Componentes indisponíveis', 'degraded_components': 'Componentes degradados'}, 'en_us': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'es': {'infra_error': 'No fue posible recopilar el estado de la infraestructura.', 'technical_details': 'Detalles técnicos', 'infrastructure_title': 'Infraestructura y observabilidad', 'operational': 'Operativa', 'degraded': 'Degradada', 'unavailable': 'No disponible', 'general_status': 'Estado general', 'available': 'Disponible', 'inactive': 'Inactivo', 'active': 'Activo', 'no_measurement': 'sin medición', 'sample': 'Muestreo', 'project': 'Proyecto', 'execution': 'Ejecución', 'local': 'Local', 'service': 'Servicio', 'infrastructure_details': 'Detalles técnicos de la infraestructura', 'pool_size': 'Tamaño del pool', 'available_connections': 'Conexiones disponibles', 'waiting_requests': 'Solicitudes en espera', 'application_tracing': 'Aplicación y rastreo', 'environment': 'Entorno', 'region': 'Región', 'phoenix_processor': 'Procesador de Phoenix', 'content_capture': 'Captura de contenido', 'unavailable_components': 'Componentes no disponibles', 'degraded_components': 'Componentes degradados'}, 'en_gb': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'fr': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'de': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'it': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'ro': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'ua': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'ru': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'sa': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}, 'ch': {'infra_error': 'The infrastructure status could not be collected at this time.', 'technical_details': 'Technical details', 'infrastructure_title': 'Infrastructure and observability', 'operational': 'Operational', 'degraded': 'Degraded', 'unavailable': 'Unavailable', 'general_status': 'Overall status', 'available': 'Available', 'inactive': 'Inactive', 'active': 'Active', 'no_measurement': 'no measurement', 'sample': 'Sampling', 'project': 'Project', 'execution': 'Execution', 'local': 'Local', 'service': 'Service', 'infrastructure_details': 'Infrastructure technical details', 'pool_size': 'Pool size', 'available_connections': 'Available connections', 'waiting_requests': 'Waiting requests', 'application_tracing': 'Application and tracing', 'environment': 'Environment', 'region': 'Region', 'phoenix_processor': 'Phoenix processor', 'content_capture': 'Content capture', 'unavailable_components': 'Unavailable components', 'degraded_components': 'Degraded components'}}


# LLMOPS_NATIVE_INFRA_TRANSLATIONS

LLMOPS_NATIVE_INFRA_TEXTS = {
    "fr": {
        "infra_error": (
            "Impossible de collecter l’état de "
            "l’infrastructure pour le moment."
        ),
        "technical_details": "Détails techniques",
        "infrastructure_title": (
            "Infrastructure et observabilité"
        ),
        "operational": "Opérationnelle",
        "degraded": "Dégradée",
        "unavailable": "Indisponible",
        "general_status": "État général",
        "available": "Disponible",
        "inactive": "Inactif",
        "active": "Actif",
        "no_measurement": "aucune mesure",
        "sample": "Échantillonnage",
        "project": "Projet",
        "execution": "Exécution",
        "local": "Locale",
        "service": "Service",
        "infrastructure_details": (
            "Détails techniques de l’infrastructure"
        ),
        "pool_size": "Taille du pool",
        "available_connections": (
            "Connexions disponibles"
        ),
        "waiting_requests": "Requêtes en attente",
        "application_tracing": (
            "Application et traçage"
        ),
        "environment": "Environnement",
        "region": "Région",
        "phoenix_processor": "Processeur Phoenix",
        "content_capture": "Capture du contenu",
        "unavailable_components": (
            "Composants indisponibles"
        ),
        "degraded_components": (
            "Composants dégradés"
        ),
    },
    "de": {
        "infra_error": (
            "Der Infrastrukturstatus konnte derzeit "
            "nicht erfasst werden."
        ),
        "technical_details": "Technische Details",
        "infrastructure_title": (
            "Infrastruktur und Beobachtbarkeit"
        ),
        "operational": "Betriebsbereit",
        "degraded": "Beeinträchtigt",
        "unavailable": "Nicht verfügbar",
        "general_status": "Gesamtstatus",
        "available": "Verfügbar",
        "inactive": "Inaktiv",
        "active": "Aktiv",
        "no_measurement": "keine Messung",
        "sample": "Abtastrate",
        "project": "Projekt",
        "execution": "Ausführung",
        "local": "Lokal",
        "service": "Dienst",
        "infrastructure_details": (
            "Technische Infrastrukturdetails"
        ),
        "pool_size": "Poolgröße",
        "available_connections": (
            "Verfügbare Verbindungen"
        ),
        "waiting_requests": "Wartende Anfragen",
        "application_tracing": (
            "Anwendung und Tracing"
        ),
        "environment": "Umgebung",
        "region": "Region",
        "phoenix_processor": "Phoenix-Prozessor",
        "content_capture": "Inhaltserfassung",
        "unavailable_components": (
            "Nicht verfügbare Komponenten"
        ),
        "degraded_components": (
            "Beeinträchtigte Komponenten"
        ),
    },
    "it": {
        "infra_error": (
            "Al momento non è stato possibile raccogliere "
            "lo stato dell’infrastruttura."
        ),
        "technical_details": "Dettagli tecnici",
        "infrastructure_title": (
            "Infrastruttura e osservabilità"
        ),
        "operational": "Operativa",
        "degraded": "Degradata",
        "unavailable": "Non disponibile",
        "general_status": "Stato generale",
        "available": "Disponibile",
        "inactive": "Inattivo",
        "active": "Attivo",
        "no_measurement": "nessuna misurazione",
        "sample": "Campionamento",
        "project": "Progetto",
        "execution": "Esecuzione",
        "local": "Locale",
        "service": "Servizio",
        "infrastructure_details": (
            "Dettagli tecnici dell’infrastruttura"
        ),
        "pool_size": "Dimensione del pool",
        "available_connections": (
            "Connessioni disponibili"
        ),
        "waiting_requests": "Richieste in attesa",
        "application_tracing": (
            "Applicazione e tracciamento"
        ),
        "environment": "Ambiente",
        "region": "Regione",
        "phoenix_processor": "Processore Phoenix",
        "content_capture": "Acquisizione dei contenuti",
        "unavailable_components": (
            "Componenti non disponibili"
        ),
        "degraded_components": (
            "Componenti degradati"
        ),
    },
    "ro": {
        "infra_error": (
            "Starea infrastructurii nu a putut fi "
            "colectată în acest moment."
        ),
        "technical_details": "Detalii tehnice",
        "infrastructure_title": (
            "Infrastructură și observabilitate"
        ),
        "operational": "Operațională",
        "degraded": "Degradată",
        "unavailable": "Indisponibilă",
        "general_status": "Stare generală",
        "available": "Disponibil",
        "inactive": "Inactiv",
        "active": "Activ",
        "no_measurement": "fără măsurare",
        "sample": "Eșantionare",
        "project": "Proiect",
        "execution": "Execuție",
        "local": "Locală",
        "service": "Serviciu",
        "infrastructure_details": (
            "Detalii tehnice ale infrastructurii"
        ),
        "pool_size": "Dimensiunea pool-ului",
        "available_connections": (
            "Conexiuni disponibile"
        ),
        "waiting_requests": "Cereri în așteptare",
        "application_tracing": (
            "Aplicație și trasare"
        ),
        "environment": "Mediu",
        "region": "Regiune",
        "phoenix_processor": "Procesor Phoenix",
        "content_capture": "Capturarea conținutului",
        "unavailable_components": (
            "Componente indisponibile"
        ),
        "degraded_components": (
            "Componente degradate"
        ),
    },
    "ua": {
        "infra_error": (
            "Наразі не вдалося отримати стан "
            "інфраструктури."
        ),
        "technical_details": "Технічні відомості",
        "infrastructure_title": (
            "Інфраструктура та спостережуваність"
        ),
        "operational": "Працює",
        "degraded": "Працює з обмеженнями",
        "unavailable": "Недоступна",
        "general_status": "Загальний стан",
        "available": "Доступний",
        "inactive": "Неактивний",
        "active": "Активний",
        "no_measurement": "без вимірювання",
        "sample": "Вибірка",
        "project": "Проєкт",
        "execution": "Виконання",
        "local": "Локально",
        "service": "Сервіс",
        "infrastructure_details": (
            "Технічні відомості інфраструктури"
        ),
        "pool_size": "Розмір пулу",
        "available_connections": (
            "Доступні з’єднання"
        ),
        "waiting_requests": "Запити в очікуванні",
        "application_tracing": (
            "Застосунок і трасування"
        ),
        "environment": "Середовище",
        "region": "Регіон",
        "phoenix_processor": "Процесор Phoenix",
        "content_capture": "Захоплення вмісту",
        "unavailable_components": (
            "Недоступні компоненти"
        ),
        "degraded_components": (
            "Компоненти з обмеженнями"
        ),
    },
    "ru": {
        "infra_error": (
            "В настоящее время не удалось получить "
            "состояние инфраструктуры."
        ),
        "technical_details": "Технические сведения",
        "infrastructure_title": (
            "Инфраструктура и наблюдаемость"
        ),
        "operational": "Работает",
        "degraded": "Работает с ограничениями",
        "unavailable": "Недоступна",
        "general_status": "Общее состояние",
        "available": "Доступен",
        "inactive": "Неактивен",
        "active": "Активен",
        "no_measurement": "нет измерения",
        "sample": "Выборка",
        "project": "Проект",
        "execution": "Выполнение",
        "local": "Локально",
        "service": "Сервис",
        "infrastructure_details": (
            "Технические сведения об инфраструктуре"
        ),
        "pool_size": "Размер пула",
        "available_connections": (
            "Доступные соединения"
        ),
        "waiting_requests": "Ожидающие запросы",
        "application_tracing": (
            "Приложение и трассировка"
        ),
        "environment": "Среда",
        "region": "Регион",
        "phoenix_processor": "Процессор Phoenix",
        "content_capture": "Захват содержимого",
        "unavailable_components": (
            "Недоступные компоненты"
        ),
        "degraded_components": (
            "Компоненты с ограничениями"
        ),
    },
    "sa": {
        "infra_error": (
            "تعذر جمع حالة البنية التحتية في الوقت الحالي."
        ),
        "technical_details": "التفاصيل التقنية",
        "infrastructure_title": (
            "البنية التحتية وقابلية المراقبة"
        ),
        "operational": "تعمل",
        "degraded": "متدهورة",
        "unavailable": "غير متاحة",
        "general_status": "الحالة العامة",
        "available": "متاح",
        "inactive": "غير نشط",
        "active": "نشط",
        "no_measurement": "لا يوجد قياس",
        "sample": "أخذ العينات",
        "project": "المشروع",
        "execution": "التنفيذ",
        "local": "محلي",
        "service": "الخدمة",
        "infrastructure_details": (
            "التفاصيل التقنية للبنية التحتية"
        ),
        "pool_size": "حجم مجمع الاتصالات",
        "available_connections": (
            "الاتصالات المتاحة"
        ),
        "waiting_requests": "الطلبات المنتظرة",
        "application_tracing": (
            "التطبيق والتتبع"
        ),
        "environment": "البيئة",
        "region": "المنطقة",
        "phoenix_processor": "معالج Phoenix",
        "content_capture": "التقاط المحتوى",
        "unavailable_components": (
            "المكونات غير المتاحة"
        ),
        "degraded_components": (
            "المكونات المتدهورة"
        ),
    },
}

LLMOPS_NATIVE_INFRA_TEXTS["ch"] = dict(
    LLMOPS_NATIVE_INFRA_TEXTS["de"]
)

for idioma, textos in LLMOPS_NATIVE_INFRA_TEXTS.items():
    LLMOPS_INFRA_TEXTS[idioma] = dict(
        textos
    )

for idioma, textos in LLMOPS_INFRA_TEXTS.items():
    LLMOPS_TEXTS.setdefault(idioma, {}).update(textos)


LLMOPS_CHART_TEXTS = {'pt': {'pass_rate_chart': 'Evolução da taxa de aprovação', 'no_runs_chart': 'Não há execuções para exibir.', 'date': 'Data', 'metric_trend_chart': 'Tendência das métricas', 'no_metrics': 'Não há métricas disponíveis.', 'displayed_metrics': 'Métricas exibidas', 'select_metric': 'Selecione pelo menos uma métrica.', 'no_metric_data': 'Nenhum dado encontrado para as métricas selecionadas.', 'average_score': 'Pontuação média', 'metric': 'Métrica', 'llmops_filters': 'Filtros LLMOps', 'history_file': 'Arquivo de histórico', 'history_load_error': 'Não foi possível carregar o histórico'}, 'en_us': {'pass_rate_chart': 'Pass rate evolution', 'no_runs_chart': 'There are no executions to display.', 'date': 'Date', 'metric_trend_chart': 'Metric trends', 'no_metrics': 'No metrics are available.', 'displayed_metrics': 'Displayed metrics', 'select_metric': 'Select at least one metric.', 'no_metric_data': 'No data was found for the selected metrics.', 'average_score': 'Average score', 'metric': 'Metric', 'llmops_filters': 'LLMOps filters', 'history_file': 'History file', 'history_load_error': 'Could not load the history'}, 'en_gb': {'pass_rate_chart': 'Pass rate evolution', 'no_runs_chart': 'There are no executions to display.', 'date': 'Date', 'metric_trend_chart': 'Metric trends', 'no_metrics': 'No metrics are available.', 'displayed_metrics': 'Displayed metrics', 'select_metric': 'Select at least one metric.', 'no_metric_data': 'No data was found for the selected metrics.', 'average_score': 'Average score', 'metric': 'Metric', 'llmops_filters': 'LLMOps filters', 'history_file': 'History file', 'history_load_error': 'Could not load the history'}, 'es': {'pass_rate_chart': 'Evolución de la tasa de aprobación', 'no_runs_chart': 'No hay ejecuciones para mostrar.', 'date': 'Fecha', 'metric_trend_chart': 'Tendencia de las métricas', 'no_metrics': 'No hay métricas disponibles.', 'displayed_metrics': 'Métricas mostradas', 'select_metric': 'Seleccione al menos una métrica.', 'no_metric_data': 'No se encontraron datos para las métricas seleccionadas.', 'average_score': 'Puntuación media', 'metric': 'Métrica', 'llmops_filters': 'Filtros LLMOps', 'history_file': 'Archivo de historial', 'history_load_error': 'No fue posible cargar el historial'}, 'fr': {'pass_rate_chart': 'Évolution du taux de réussite', 'no_runs_chart': 'Aucune exécution à afficher.', 'date': 'Date', 'metric_trend_chart': 'Tendance des métriques', 'no_metrics': 'Aucune métrique disponible.', 'displayed_metrics': 'Métriques affichées', 'select_metric': 'Sélectionnez au moins une métrique.', 'no_metric_data': 'Aucune donnée trouvée pour les métriques sélectionnées.', 'average_score': 'Score moyen', 'metric': 'Métrique', 'llmops_filters': 'Filtres LLMOps', 'history_file': 'Fichier d’historique', 'history_load_error': 'Impossible de charger l’historique'}, 'de': {'pass_rate_chart': 'Entwicklung der Erfolgsquote', 'no_runs_chart': 'Keine Ausführungen zum Anzeigen.', 'date': 'Datum', 'metric_trend_chart': 'Metriktrends', 'no_metrics': 'Keine Metriken verfügbar.', 'displayed_metrics': 'Angezeigte Metriken', 'select_metric': 'Wählen Sie mindestens eine Metrik.', 'no_metric_data': 'Keine Daten für die ausgewählten Metriken gefunden.', 'average_score': 'Durchschnittswert', 'metric': 'Metrik', 'llmops_filters': 'LLMOps-Filter', 'history_file': 'Verlaufsdatei', 'history_load_error': 'Verlauf konnte nicht geladen werden'}, 'it': {'pass_rate_chart': 'Evoluzione del tasso di approvazione', 'no_runs_chart': 'Nessuna esecuzione da mostrare.', 'date': 'Data', 'metric_trend_chart': 'Tendenza delle metriche', 'no_metrics': 'Nessuna metrica disponibile.', 'displayed_metrics': 'Metriche visualizzate', 'select_metric': 'Seleziona almeno una metrica.', 'no_metric_data': 'Nessun dato trovato per le metriche selezionate.', 'average_score': 'Punteggio medio', 'metric': 'Metrica', 'llmops_filters': 'Filtri LLMOps', 'history_file': 'File storico', 'history_load_error': 'Impossibile caricare lo storico'}, 'ro': {'pass_rate_chart': 'Evoluția ratei de aprobare', 'no_runs_chart': 'Nu există execuții de afișat.', 'date': 'Dată', 'metric_trend_chart': 'Tendința metricilor', 'no_metrics': 'Nu există metrici disponibile.', 'displayed_metrics': 'Metrici afișate', 'select_metric': 'Selectați cel puțin o metrică.', 'no_metric_data': 'Nu au fost găsite date pentru metricile selectate.', 'average_score': 'Scor mediu', 'metric': 'Metrică', 'llmops_filters': 'Filtre LLMOps', 'history_file': 'Fișier istoric', 'history_load_error': 'Istoricul nu a putut fi încărcat'}, 'ua': {'pass_rate_chart': 'Динаміка рівня успішності', 'no_runs_chart': 'Немає виконань для відображення.', 'date': 'Дата', 'metric_trend_chart': 'Тенденції метрик', 'no_metrics': 'Немає доступних метрик.', 'displayed_metrics': 'Відображені метрики', 'select_metric': 'Виберіть принаймні одну метрику.', 'no_metric_data': 'Для вибраних метрик даних не знайдено.', 'average_score': 'Середня оцінка', 'metric': 'Метрика', 'llmops_filters': 'Фільтри LLMOps', 'history_file': 'Файл історії', 'history_load_error': 'Не вдалося завантажити історію'}, 'ru': {'pass_rate_chart': 'Динамика уровня успешности', 'no_runs_chart': 'Нет выполнений для отображения.', 'date': 'Дата', 'metric_trend_chart': 'Тенденции метрик', 'no_metrics': 'Нет доступных метрик.', 'displayed_metrics': 'Отображаемые метрики', 'select_metric': 'Выберите хотя бы одну метрику.', 'no_metric_data': 'Для выбранных метрик данные не найдены.', 'average_score': 'Средняя оценка', 'metric': 'Метрика', 'llmops_filters': 'Фильтры LLMOps', 'history_file': 'Файл истории', 'history_load_error': 'Не удалось загрузить историю'}, 'sa': {'pass_rate_chart': 'تطور معدل النجاح', 'no_runs_chart': 'لا توجد عمليات تشغيل للعرض.', 'date': 'التاريخ', 'metric_trend_chart': 'اتجاهات المقاييس', 'no_metrics': 'لا توجد مقاييس متاحة.', 'displayed_metrics': 'المقاييس المعروضة', 'select_metric': 'حدد مقياسًا واحدًا على الأقل.', 'no_metric_data': 'لم يتم العثور على بيانات للمقاييس المحددة.', 'average_score': 'متوسط النتيجة', 'metric': 'المقياس', 'llmops_filters': 'فلاتر LLMOps', 'history_file': 'ملف السجل', 'history_load_error': 'تعذر تحميل السجل'}, 'ch': {'pass_rate_chart': 'Entwicklung der Erfolgsquote', 'no_runs_chart': 'Keine Ausführungen zum Anzeigen.', 'date': 'Datum', 'metric_trend_chart': 'Metriktrends', 'no_metrics': 'Keine Metriken verfügbar.', 'displayed_metrics': 'Angezeigte Metriken', 'select_metric': 'Wählen Sie mindestens eine Metrik.', 'no_metric_data': 'Keine Daten für die ausgewählten Metriken gefunden.', 'average_score': 'Durchschnittswert', 'metric': 'Metrik', 'llmops_filters': 'LLMOps-Filter', 'history_file': 'Verlaufsdatei', 'history_load_error': 'Verlauf konnte nicht geladen werden'}}

for idioma, textos in LLMOPS_CHART_TEXTS.items():
    LLMOPS_TEXTS.setdefault(idioma, {}).update(textos)

LLMOPS_TEXTS["ch"] = LLMOPS_TEXTS["de"]


def llmops_lang() -> str:
    idioma = st.session_state.get(
        "dashboard_interface_lang",
        "pt",
    )

    if idioma in LLMOPS_TEXTS:
        return idioma

    return "pt"


def llmops_t(
    key: str,
    default: str | None = None,
) -> str:
    idioma = llmops_lang()

    return LLMOPS_TEXTS.get(
        idioma,
        LLMOPS_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


LLMOPS_COLUMN_TEXTS = {
    "pt": {
        "metric_id": "Métrica",
        "average_score": "Pontuação média",
        "sample_count": "Amostras",
        "run_reference": "Referência da execução",
        "branch": "Branch",
        "commit_sha": "Commit",
        "environment": "Ambiente",
        "evaluation_mode": "Modo de avaliação",
        "baseline_id": "Baseline",
        "recorded_at": "Data e hora",
        "pass_rate": "Taxa de aprovação",
        "passed": "Aprovada",
        "quality_gate_passed": "Quality Gate",
        "regressions": "Regressões",
        "violations": "Violações",
    },
    "en_us": {
        "metric_id": "Metric",
        "average_score": "Average score",
        "sample_count": "Samples",
        "run_reference": "Run reference",
        "branch": "Branch",
        "commit_sha": "Commit",
        "environment": "Environment",
        "evaluation_mode": "Evaluation mode",
        "baseline_id": "Baseline",
        "recorded_at": "Date and time",
        "pass_rate": "Pass rate",
        "passed": "Approved",
        "quality_gate_passed": "Quality Gate",
        "regressions": "Regressions",
        "violations": "Violations",
    },
    "es": {
        "metric_id": "Métrica",
        "average_score": "Puntuación media",
        "sample_count": "Muestras",
        "run_reference": "Referencia de ejecución",
        "branch": "Rama",
        "commit_sha": "Commit",
        "environment": "Entorno",
        "evaluation_mode": "Modo de evaluación",
        "baseline_id": "Línea base",
        "recorded_at": "Fecha y hora",
        "pass_rate": "Tasa de aprobación",
        "passed": "Aprobada",
        "quality_gate_passed": "Puerta de calidad",
        "regressions": "Regresiones",
        "violations": "Infracciones",
    },
}

LLMOPS_COLUMN_TEXTS["en_gb"] = LLMOPS_COLUMN_TEXTS["en_us"]

for idioma in (
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
    "ch",
):
    LLMOPS_COLUMN_TEXTS.setdefault(
        idioma,
        LLMOPS_COLUMN_TEXTS["en_us"],
    )


def llmops_column_labels() -> dict[str, str]:
    idioma = llmops_lang()

    return LLMOPS_COLUMN_TEXTS.get(
        idioma,
        LLMOPS_COLUMN_TEXTS["pt"],
    )


def traduzir_colunas_llmops(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    return frame.rename(
        columns=llmops_column_labels()
    )


def _percentage(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.2%}"


def _render_header() -> None:
    st.title(
        llmops_t("title")
    )

    st.caption(
        llmops_t("caption")
    )


def _render_infrastructure_status() -> None:
    """
    Exibe a saúde operacional sem revelar
    credenciais ou identificadores privados.
    """

    try:
        initialize_phoenix()
        health = collect_infrastructure_health()
    except Exception as exc:
        st.warning(
            llmops_t("infra_error")
        )

        with st.expander(
            llmops_t("technical_details"),
            expanded=False,
        ):
            st.code(type(exc).__name__)

        return

    st.subheader(
        llmops_t("infrastructure_title")
    )

    status_labels = {
        "operational": llmops_t(
            "operational"
        ),
        "degraded": llmops_t(
            "degraded"
        ),
        "unavailable": llmops_t(
            "unavailable"
        ),
    }

    status_label = status_labels.get(
        health.status,
        health.status,
    )

    status_message = (
        f"{llmops_t('general_status')}: "
        f"{status_label}"
    )

    if health.status == "operational":
        st.success(status_message)
    elif health.status == "degraded":
        st.warning(status_message)
    else:
        st.error(status_message)

    neon_column, phoenix_column, render_column = (
        st.columns(3)
    )

    with neon_column:
        st.metric(
            "Neon PostgreSQL",
            (
                llmops_t("available")
                if health.neon.available
                else llmops_t("unavailable")
            ),
            (
                f"{health.neon.latency_ms:.0f} ms"
                if health.neon.latency_ms
                is not None
                else llmops_t(
                    "no_measurement"
                )
            ),
        )

        st.caption(
            f"Pool: {health.neon.pool_status}"
        )

    with phoenix_column:
        st.metric(
            "Phoenix",
            (
                llmops_t("active")
                if health.phoenix.ready
                else llmops_t("inactive")
            ),
            (
                f"{llmops_t('sample')} "
                f"{health.phoenix.sample_rate:.0%}"
            ),
        )

        st.caption(
            f"{llmops_t('project')}: "
            f"{health.phoenix.project_name}"
        )

    with render_column:
        st.metric(
            llmops_t("execution"),
            (
                "Render"
                if health.render.running_on_render
                else llmops_t("local")
            ),
            health.render.environment,
        )

        st.caption(
            f"{llmops_t('service')}: "
            f"{health.render.service_name}"
        )

    with st.expander(
        llmops_t(
            "infrastructure_details"
        ),
        expanded=False,
    ):
        detail_column_1, detail_column_2 = (
            st.columns(2)
        )

        with detail_column_1:
            st.write("**Neon**")

            st.write(
                "PostgreSQL: "
                f"{health.neon.server_version or '—'}"
            )

            st.write(
                f"{llmops_t('pool_size')}: "
                f"{health.neon.pool_size}"
            )

            st.write(
                f"{llmops_t('available_connections')}: "
                f"{health.neon.pool_available}"
            )

            st.write(
                f"{llmops_t('waiting_requests')}: "
                f"{health.neon.pool_waiting}"
            )

        with detail_column_2:
            st.write(
                f"**{llmops_t('application_tracing')}**"
            )

            st.write(
                f"{llmops_t('environment')}: "
                f"{health.render.environment}"
            )

            st.write(
                f"{llmops_t('region')}: "
                f"{health.render.region}"
            )

            st.write(
                f"{llmops_t('phoenix_processor')}: "
                f"{health.phoenix.processor}"
            )

            st.write(
                f"{llmops_t('content_capture')}: "
                f"{health.phoenix.capture_content}"
            )

        if health.unavailable_components:
            st.error(
                f"{llmops_t('unavailable_components')}: "
                + ", ".join(
                    health.unavailable_components
                )
            )

        if health.degraded_components:
            st.warning(
                f"{llmops_t('degraded_components')}: "
                + ", ".join(
                    health.degraded_components
                )
            )

def _render_filters(
    history,
    controls,
):
    controls.header(
        llmops_t("filters")
    )

    available_branches = sorted(
        {
            entry.branch
            for entry in history.entries
        }
    )

    available_environments = sorted(
        {
            entry.environment
            for entry in history.entries
        }
    )

    branches = controls.multiselect(
        llmops_t("branches"),
        available_branches,
        default=available_branches,
    )

    environments = controls.multiselect(
        llmops_t("environments"),
        available_environments,
        default=available_environments,
    )

    status_options = (
        "all",
        "approved",
        "failed",
    )

    status_labels = {
        "all": llmops_t("all_runs"),
        "approved": llmops_t(
            "approved_runs_option"
        ),
        "failed": llmops_t(
            "failed_runs_option"
        ),
    }

    status_option = controls.selectbox(
        llmops_t("run_status"),
        status_options,
        format_func=lambda value: (
            status_labels[value]
        ),
    )

    passed_filter = {
        "all": None,
        "approved": True,
        "failed": False,
    }[status_option]

    selected_branches = (
        set(branches)
        if branches
        else set()
    )

    selected_environments = (
        set(environments)
        if environments
        else set()
    )

    return filter_history(
        history,
        branches=selected_branches,
        environments=selected_environments,
        passed=passed_filter,
    )

def _render_summary(history) -> None:
    summary = build_dashboard_summary(
        history
    )

    first, second, third, fourth = (
        st.columns(4)
    )

    first.metric(
        llmops_t("total_runs"),
        summary.total_runs,
    )

    second.metric(
        llmops_t("approval_rate"),
        _percentage(
            summary.approval_rate
        ),
    )

    third.metric(
        llmops_t("latest_pass_rate"),
        _percentage(
            summary.latest_pass_rate
        ),
    )

    fourth.metric(
        llmops_t("tracked_metrics"),
        summary.tracked_metrics,
    )

    fifth, sixth, seventh, eighth = (
        st.columns(4)
    )

    fifth.metric(
        llmops_t("approved_runs"),
        summary.approved_runs,
    )

    sixth.metric(
        llmops_t("failed_runs"),
        summary.failed_runs,
    )

    seventh.metric(
        llmops_t("recent_regressions"),
        summary.latest_regressions,
    )

    eighth.metric(
        llmops_t("recent_violations"),
        summary.latest_violations,
    )

    if (
        summary.latest_quality_gate_passed
        is True
    ):
        st.success(
            llmops_t("gate_approved")
        )
    elif (
        summary.latest_quality_gate_passed
        is False
    ):
        st.error(
            llmops_t("gate_failed")
        )
    else:
        st.info(
            llmops_t("no_runs")
        )


def _render_pass_rate_chart(history) -> None:
    st.subheader(
        llmops_t("pass_rate_chart")
    )

    rows = build_pass_rate_series(history)

    if not rows:
        st.info(
            llmops_t("no_runs_chart")
        )
        return

    frame = pd.DataFrame(rows)

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
    )

    fig_pass_rate = px.line(
        frame.sort_values("recorded_at"),
        x="recorded_at",
        y="pass_rate",
        markers=True,
        color_discrete_sequence=[
            "#34D399",
        ],
        labels={
            "recorded_at": llmops_t("date"),
            "pass_rate": llmops_t(
                "approval_rate"
            ),
        },
    )

    fig_pass_rate.update_traces(
        line={"width": 3},
        marker={
            "size": 9,
            "color": "#D1FAE5",
            "line": {
                "color": "#34D399",
                "width": 2,
            },
        },
        fill="tozeroy",
        fillcolor="rgba(52, 211, 153, 0.15)",
        hovertemplate=(
            "<b>%{x|%d/%m/%Y %H:%M}</b><br>"
            + llmops_t("approval_rate")
            + ": %{y:.2%}<extra></extra>"
        ),
    )

    fig_pass_rate.update_layout(
        xaxis_title=None,
        yaxis_title=llmops_t(
            "approval_rate"
        ),
        showlegend=False,
        hovermode="x unified",
    )

    fig_pass_rate.update_xaxes(
        tickformat="%d/%m<br>%H:%M",
    )

    fig_pass_rate.update_yaxes(
        range=[0, 1],
        tickformat=".0%",
    )

    aplicar_tema_llmops_chart(
        fig_pass_rate,
        height=430,
    )

    st.plotly_chart(
        fig_pass_rate,
        width="stretch",
        key="llmops_pass_rate_evolution_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

def _render_metric_chart(history) -> None:
    st.subheader(
        llmops_t("metric_trend_chart")
    )

    available_metrics = get_metric_ids(
        history
    )

    if not available_metrics:
        st.info(
            llmops_t("no_metrics")
        )
        return

    selected_metrics = st.multiselect(
        llmops_t("displayed_metrics"),
        available_metrics,
        default=list(
            available_metrics[:5]
        ),
    )

    if not selected_metrics:
        st.warning(
            llmops_t("select_metric")
        )
        return

    rows = build_metric_series(
        history,
        metric_ids=set(selected_metrics),
    )

    frame = pd.DataFrame(rows)

    if frame.empty:
        st.info(
            llmops_t("no_metric_data")
        )
        return

    frame["recorded_at"] = pd.to_datetime(
        frame["recorded_at"],
        utc=True,
    )

    pivot = frame.pivot_table(
        index="recorded_at",
        columns="metric_id",
        values="average_score",
        aggfunc="last",
    ).sort_index()

    metricas_disponiveis = list(
        pivot.columns
    )

    metricas_plot = pivot.reset_index()

    fig_metricas = px.line(
        metricas_plot,
        x="recorded_at",
        y=metricas_disponiveis,
        markers=True,
        color_discrete_sequence=(
            LLMOPS_METRIC_COLORS
        ),
        labels={
            "recorded_at": llmops_t("date"),
            "value": llmops_t(
                "average_score"
            ),
            "variable": llmops_t("metric"),
        },
    )

    fig_metricas.update_traces(
        line={"width": 2.7},
        marker={"size": 7},
        connectgaps=False,
        hovertemplate=(
            "<b>%{x|%d/%m/%Y %H:%M}</b><br>"
            "%{fullData.name}: %{y:.2%}"
            "<extra></extra>"
        ),
    )

    fig_metricas.update_layout(
        xaxis_title=None,
        yaxis_title=llmops_t(
            "average_score"
        ),
        legend_title_text=llmops_t(
            "metric"
        ),
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.22,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    fig_metricas.update_xaxes(
        tickformat="%d/%m<br>%H:%M",
    )

    fig_metricas.update_yaxes(
        range=[0, 1],
        tickformat=".0%",
    )

    aplicar_tema_llmops_chart(
        fig_metricas,
        height=510,
    )

    st.plotly_chart(
        fig_metricas,
        width="stretch",
        key="llmops_metrics_trend_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

def _render_latest_snapshot(history) -> None:
    st.subheader(
        llmops_t("latest_snapshot")
    )

    latest = history.latest()

    if latest is None:
        st.info(
            llmops_t("no_registered_run")
        )
        return

    column_labels = llmops_column_labels()

    st.write(
        {
            column_labels["run_reference"]: (
                latest.run_reference
            ),
            column_labels["branch"]: (
                latest.branch
            ),
            column_labels["commit_sha"]: (
                latest.commit_sha
            ),
            column_labels["environment"]: (
                latest.environment
            ),
            column_labels["evaluation_mode"]: (
                latest.evaluation_mode
            ),
            column_labels["baseline_id"]: (
                latest.baseline_id
            ),
            column_labels["recorded_at"]: (
                latest.recorded_at
            ),
        }
    )

    snapshot = build_metric_snapshot(
        latest
    )

    if snapshot:
        frame = pd.DataFrame(snapshot)
        frame = traduzir_colunas_llmops(
            frame
        )

        st.dataframe(
            frame,
            width="stretch",
            hide_index=True,
        )


def _render_runs_table(history) -> None:
    st.subheader(
        llmops_t("runs_history")
    )

    rows = build_runs_table(history)

    if not rows:
        st.info(
            llmops_t("no_filtered_runs")
        )
        return

    frame = pd.DataFrame(rows)
    column_labels = llmops_column_labels()

    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "run_reference": (
                st.column_config.TextColumn(
                    column_labels["run_reference"]
                )
            ),
            "branch": (
                st.column_config.TextColumn(
                    column_labels["branch"]
                )
            ),
            "commit_sha": (
                st.column_config.TextColumn(
                    column_labels["commit_sha"]
                )
            ),
            "environment": (
                st.column_config.TextColumn(
                    column_labels["environment"]
                )
            ),
            "evaluation_mode": (
                st.column_config.TextColumn(
                    column_labels["evaluation_mode"]
                )
            ),
            "baseline_id": (
                st.column_config.TextColumn(
                    column_labels["baseline_id"]
                )
            ),
            "recorded_at": (
                st.column_config.DatetimeColumn(
                    column_labels["recorded_at"]
                )
            ),
            "regressions": (
                st.column_config.NumberColumn(
                    column_labels["regressions"]
                )
            ),
            "violations": (
                st.column_config.NumberColumn(
                    column_labels["violations"]
                )
            ),
            "pass_rate": (
                st.column_config.ProgressColumn(
                    llmops_t("pass_rate"),
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f",
                )
            ),
            "passed": (
                st.column_config.CheckboxColumn(
                    llmops_t("approved")
                )
            ),
            "quality_gate_passed": (
                st.column_config.CheckboxColumn(
                    llmops_t("quality_gate")
                )
            ),
        },
    )


def render_llmops_dashboard(
    *,
    integrated: bool = False,
) -> None:
    """
    Renderiza o painel LLMOps.

    integrated=False:
        execução Streamlit independente.

    integrated=True:
        execução incorporada ao dashboard
        administrativo principal da INNA.
    """
    _render_header()
    _render_infrastructure_status()

    st.divider()

    if integrated:
        controls = st.expander(
            llmops_t("llmops_filters"),
            expanded=False,
        )
        history_key = (
            "llmops_integrated_history_path"
        )
    else:
        controls = st.sidebar
        history_key = (
            "llmops_standalone_history_path"
        )

    history_path = controls.text_input(
        llmops_t("history_file"),
        str(DEFAULT_HISTORY_PATH),
        key=history_key,
    )

    try:
        history = load_dashboard_history(
            history_path
        )
    except Exception as exc:
        st.error(
            f"{llmops_t('history_load_error')}: "
            f"{exc}"
        )
        return

    filtered_history = _render_filters(
        history,
        controls,
    )

    _render_summary(filtered_history)

    st.divider()

    _render_pass_rate_chart(
        filtered_history
    )

    _render_metric_chart(
        filtered_history
    )

    st.divider()

    _render_latest_snapshot(
        filtered_history
    )

    _render_runs_table(
        filtered_history
    )


def main() -> None:
    st.set_page_config(
        page_title="INNA LLMOps",
        page_icon="📊",
        layout="wide",
    )

    apply_admin_dark_theme()

    render_llmops_dashboard(
        integrated=False
    )


if __name__ == "__main__":
    main()

from .health_runtime import (
    coletar_health_score_real,
)

from .health import (
    PESOS_COMPONENTES,
    calcular_health_score_global,
    calcular_score_infraestrutura,
    calcular_score_memoria,
    calcular_score_performance,
    calcular_score_rag,
    calcular_score_timeline,
    calcular_score_tools,
    classificar_score,
    limitar_score,
)

from .anomalies import (
    SEVERIDADE_ORDEM,
    calcular_mad,
    detectar_anomalias_operacionais,
    detectar_outliers_mad,
)

from .narrative import (
    classificar_saude_operacional,
    gerar_insights_operacionais,
    gerar_texto_narrativa,
)

from .analytics import (
    calcular_distribuicao_coluna,
    calcular_execucoes_sem_tool,
    calcular_percentis,
    calcular_ranking_tools,
    calcular_serie_temporal_analytics,
    comparar_periodos,
    preparar_eventos_analytics,
)

"""
Camada de observabilidade inteligente da INNA.
"""

from .timeline import (
    ETAPAS_TIMELINE,
    LABELS_ETAPAS,
    carregar_timeline_trace,
    carregar_traces_recentes,
    executar_etapa_timeline,
    gerar_trace_id,
    preparar_tabela_timeline,
    registrar_evento_timeline,
)

from .metrics import (
    calcular_metricas_executivas,
    calcular_percentil_95,
    calcular_taxa_sucesso,
    identificar_tool_mais_utilizada,
)


__all__ = [
    "coletar_health_score_real",
    "calcular_health_score_global",
    "calcular_score_performance",
    "calcular_score_timeline",
    "calcular_score_memoria",
    "calcular_score_rag",
    "calcular_score_infraestrutura",
    "calcular_score_tools",
    "classificar_score",
    "limitar_score",
    "PESOS_COMPONENTES",
    "detectar_anomalias_operacionais",
    "detectar_outliers_mad",
    "calcular_mad",
    "SEVERIDADE_ORDEM",
    "gerar_texto_narrativa",
    "gerar_insights_operacionais",
    "classificar_saude_operacional",
    "comparar_periodos",
    "calcular_serie_temporal_analytics",
    "calcular_execucoes_sem_tool",
    "calcular_distribuicao_coluna",
    "calcular_ranking_tools",
    "preparar_eventos_analytics",
    "calcular_percentis",
    "carregar_traces_recentes",
    "carregar_timeline_trace",
    "executar_etapa_timeline",
    "registrar_evento_timeline",
    "preparar_tabela_timeline",
    "gerar_trace_id",
    "LABELS_ETAPAS",
    "ETAPAS_TIMELINE",
    "calcular_metricas_executivas",
    "calcular_percentil_95",
    "calcular_taxa_sucesso",
    "identificar_tool_mais_utilizada",
]

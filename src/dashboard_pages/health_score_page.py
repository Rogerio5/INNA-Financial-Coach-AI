"""
INNA Health Center.

Painel global da saúde operacional da aplicação.
"""

from __future__ import annotations

import unicodedata
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

HEALTH_CHART_BG = "#020617"
HEALTH_CHART_TEXT = "#F8FAFC"
HEALTH_CHART_GRID = "rgba(148, 163, 184, 0.16)"

HEALTH_SERIES_COLORS = [
    "#38BDF8",
    "#34D399",
    "#A78BFA",
    "#F59E0B",
    "#F87171",
    "#22D3EE",
]


def aplicar_tema_health_chart(
    fig,
    *,
    height=410,
):
    """Aplica o tema visual do INNA Health Center."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=HEALTH_CHART_BG,
        plot_bgcolor=HEALTH_CHART_BG,
        font={
            "color": HEALTH_CHART_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": HEALTH_CHART_TEXT,
        },
        margin={
            "l": 28,
            "r": 28,
            "t": 18,
            "b": 28,
        },
        height=height,
    )

    fig.update_xaxes(
        color=HEALTH_CHART_TEXT,
        gridcolor=HEALTH_CHART_GRID,
        zerolinecolor=("rgba(148, 163, 184, 0.25)"),
    )

    fig.update_yaxes(
        color=HEALTH_CHART_TEXT,
        gridcolor=HEALTH_CHART_GRID,
        zerolinecolor=("rgba(148, 163, 184, 0.25)"),
    )

    return fig


NOMES_COMPONENTES = {
    "tools": "Tools",
    "rag": "RAG",
    "memoria": "Memória",
    "infraestrutura": "Infraestrutura",
    "timeline": "Timeline",
    "performance": "Performance",
}


HEALTH_TABLE_TEXTS = {
    "pt": {
        "id": "ID",
        "date": "Data e hora",
        "global": "Score global",
        "tools": "Ferramentas",
        "rag": "RAG",
        "memory": "Memória",
        "infrastructure": "Infraestrutura",
        "timeline": "Linha do tempo",
        "performance": "Desempenho",
        "classification": "Classificação",
        "priority_component": "Componente prioritário",
        "anomalies": "Anomalias",
        "origin": "Origem",
        "component": "Componente",
        "score": "Score",
        "weight": "Peso (%)",
        "contribution": "Contribuição",
        "status": "Status",
        "component_comparison": ("### Comparativo dos componentes"),
        "export_history": ("⬇️ Exportar histórico em CSV"),
    },
    "en_us": {
        "id": "ID",
        "date": "Date and time",
        "global": "Global score",
        "tools": "Tools",
        "rag": "RAG",
        "memory": "Memory",
        "infrastructure": "Infrastructure",
        "timeline": "Timeline",
        "performance": "Performance",
        "classification": "Classification",
        "priority_component": "Priority component",
        "anomalies": "Anomalies",
        "origin": "Origin",
        "component": "Component",
        "score": "Score",
        "weight": "Weight (%)",
        "contribution": "Contribution",
        "status": "Status",
        "component_comparison": ("### Component comparison"),
        "export_history": ("⬇️ Export history as CSV"),
    },
    "es": {
        "id": "ID",
        "date": "Fecha y hora",
        "global": "Puntuación global",
        "tools": "Herramientas",
        "rag": "RAG",
        "memory": "Memoria",
        "infrastructure": "Infraestructura",
        "timeline": "Línea de tiempo",
        "performance": "Rendimiento",
        "classification": "Clasificación",
        "priority_component": "Componente prioritario",
        "anomalies": "Anomalías",
        "origin": "Origen",
        "component": "Componente",
        "score": "Puntuación",
        "weight": "Peso (%)",
        "contribution": "Contribución",
        "status": "Estado",
        "component_comparison": ("### Comparación de componentes"),
        "export_history": ("⬇️ Exportar historial en CSV"),
    },
    "fr": {
        "id": "ID",
        "date": "Date et heure",
        "global": "Score global",
        "tools": "Outils",
        "rag": "RAG",
        "memory": "Mémoire",
        "infrastructure": "Infrastructure",
        "timeline": "Chronologie",
        "performance": "Performance",
        "classification": "Classement",
        "priority_component": "Composant prioritaire",
        "anomalies": "Anomalies",
        "origin": "Origine",
        "component": "Composant",
        "score": "Score",
        "weight": "Poids (%)",
        "contribution": "Contribution",
        "status": "Statut",
        "component_comparison": ("### Comparaison des composants"),
        "export_history": ("⬇️ Exporter l’historique en CSV"),
    },
    "de": {
        "id": "ID",
        "date": "Datum und Uhrzeit",
        "global": "Gesamtscore",
        "tools": "Werkzeuge",
        "rag": "RAG",
        "memory": "Speicher",
        "infrastructure": "Infrastruktur",
        "timeline": "Zeitleiste",
        "performance": "Leistung",
        "classification": "Klassifizierung",
        "priority_component": "Prioritätskomponente",
        "anomalies": "Anomalien",
        "origin": "Ursprung",
        "component": "Komponente",
        "score": "Score",
        "weight": "Gewicht (%)",
        "contribution": "Beitrag",
        "status": "Status",
        "component_comparison": ("### Komponentenvergleich"),
        "export_history": ("⬇️ Verlauf als CSV exportieren"),
    },
    "it": {
        "id": "ID",
        "date": "Data e ora",
        "global": "Punteggio globale",
        "tools": "Strumenti",
        "rag": "RAG",
        "memory": "Memoria",
        "infrastructure": "Infrastruttura",
        "timeline": "Cronologia",
        "performance": "Prestazioni",
        "classification": "Classificazione",
        "priority_component": "Componente prioritario",
        "anomalies": "Anomalie",
        "origin": "Origine",
        "component": "Componente",
        "score": "Punteggio",
        "weight": "Peso (%)",
        "contribution": "Contributo",
        "status": "Stato",
        "component_comparison": ("### Confronto dei componenti"),
        "export_history": ("⬇️ Esporta cronologia in CSV"),
    },
    "ro": {
        "id": "ID",
        "date": "Data și ora",
        "global": "Scor global",
        "tools": "Instrumente",
        "rag": "RAG",
        "memory": "Memorie",
        "infrastructure": "Infrastructură",
        "timeline": "Cronologie",
        "performance": "Performanță",
        "classification": "Clasificare",
        "priority_component": "Componentă prioritară",
        "anomalies": "Anomalii",
        "origin": "Origine",
        "component": "Componentă",
        "score": "Scor",
        "weight": "Pondere (%)",
        "contribution": "Contribuție",
        "status": "Stare",
        "component_comparison": ("### Comparația componentelor"),
        "export_history": ("⬇️ Exportă istoricul CSV"),
    },
    "ua": {
        "id": "ID",
        "date": "Дата й час",
        "global": "Загальна оцінка",
        "tools": "Інструменти",
        "rag": "RAG",
        "memory": "Пам’ять",
        "infrastructure": "Інфраструктура",
        "timeline": "Часова шкала",
        "performance": "Продуктивність",
        "classification": "Класифікація",
        "priority_component": "Пріоритетний компонент",
        "anomalies": "Аномалії",
        "origin": "Джерело",
        "component": "Компонент",
        "score": "Оцінка",
        "weight": "Вага (%)",
        "contribution": "Внесок",
        "status": "Статус",
        "component_comparison": ("### Порівняння компонентів"),
        "export_history": ("⬇️ Експортувати історію CSV"),
    },
    "ru": {
        "id": "ID",
        "date": "Дата и время",
        "global": "Общая оценка",
        "tools": "Инструменты",
        "rag": "RAG",
        "memory": "Память",
        "infrastructure": "Инфраструктура",
        "timeline": "Временная шкала",
        "performance": "Производительность",
        "classification": "Классификация",
        "priority_component": "Приоритетный компонент",
        "anomalies": "Аномалии",
        "origin": "Источник",
        "component": "Компонент",
        "score": "Оценка",
        "weight": "Вес (%)",
        "contribution": "Вклад",
        "status": "Статус",
        "component_comparison": ("### Сравнение компонентов"),
        "export_history": ("⬇️ Экспортировать историю CSV"),
    },
    "sa": {
        "id": "المعرّف",
        "date": "التاريخ والوقت",
        "global": "الدرجة الإجمالية",
        "tools": "الأدوات",
        "rag": "RAG",
        "memory": "الذاكرة",
        "infrastructure": "البنية التحتية",
        "timeline": "الخط الزمني",
        "performance": "الأداء",
        "classification": "التصنيف",
        "priority_component": "المكوّن ذو الأولوية",
        "anomalies": "الحالات الشاذة",
        "origin": "المصدر",
        "component": "المكوّن",
        "score": "الدرجة",
        "weight": "الوزن (%)",
        "contribution": "المساهمة",
        "status": "الحالة",
        "component_comparison": ("### مقارنة المكوّنات"),
        "export_history": ("⬇️ تصدير السجل بصيغة CSV"),
    },
}

HEALTH_TABLE_TEXTS["en_gb"] = HEALTH_TABLE_TEXTS["en_us"]

HEALTH_TABLE_TEXTS["ch"] = HEALTH_TABLE_TEXTS["de"]


def health_table_lang() -> str:
    """Retorna o idioma atual do Dashboard."""
    idioma = st.session_state.get(
        "dashboard_interface_lang",
        "pt",
    )

    if idioma in HEALTH_TABLE_TEXTS:
        return idioma

    return "pt"


def health_table_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz textos das tabelas do Health Center."""
    idioma = health_table_lang()

    return HEALTH_TABLE_TEXTS.get(
        idioma,
        HEALTH_TABLE_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def nome_componente_health(
    nome: str,
    padrao: str | None = None,
) -> str:
    """Traduz nomes de componentes sem alterar dados internos."""
    chaves = {
        "tools": "tools",
        "rag": "rag",
        "memoria": "memory",
        "infraestrutura": "infrastructure",
        "timeline": "timeline",
        "performance": "performance",
    }

    chave = chaves.get(str(nome or "").strip().lower())

    if chave is None:
        return padrao if padrao is not None else str(nome or "").title()

    return health_table_t(
        chave,
        padrao,
    )


def health_date_format() -> str:
    """Formato de data conforme o idioma."""
    if health_table_lang() == "en_us":
        return "MM/DD/YYYY HH:mm"

    return "DD/MM/YYYY HH:mm"


HEALTH_VALUE_TEXTS = {
    "pt": {
        "excellent": "Excelente",
        "good": "Boa",
        "attention": "Atenção",
        "critical": "Crítica",
        "healthy": "Saudável",
        "operational": "Operacional",
        "degraded": "Degradado",
        "unavailable": "Indisponível",
        "no_data": "Sem dados",
    },
    "en_us": {
        "excellent": "Excellent",
        "good": "Good",
        "attention": "Attention",
        "critical": "Critical",
        "healthy": "Healthy",
        "operational": "Operational",
        "degraded": "Degraded",
        "unavailable": "Unavailable",
        "no_data": "No data",
    },
    "es": {
        "excellent": "Excelente",
        "good": "Buena",
        "attention": "Atención",
        "critical": "Crítica",
        "healthy": "Saludable",
        "operational": "Operativo",
        "degraded": "Degradado",
        "unavailable": "No disponible",
        "no_data": "Sin datos",
    },
    "fr": {
        "excellent": "Excellente",
        "good": "Bonne",
        "attention": "Attention",
        "critical": "Critique",
        "healthy": "Sain",
        "operational": "Opérationnel",
        "degraded": "Dégradé",
        "unavailable": "Indisponible",
        "no_data": "Aucune donnée",
    },
    "de": {
        "excellent": "Ausgezeichnet",
        "good": "Gut",
        "attention": "Achtung",
        "critical": "Kritisch",
        "healthy": "Gesund",
        "operational": "Betriebsbereit",
        "degraded": "Eingeschränkt",
        "unavailable": "Nicht verfügbar",
        "no_data": "Keine Daten",
    },
    "it": {
        "excellent": "Eccellente",
        "good": "Buona",
        "attention": "Attenzione",
        "critical": "Critica",
        "healthy": "Sano",
        "operational": "Operativo",
        "degraded": "Degradato",
        "unavailable": "Non disponibile",
        "no_data": "Nessun dato",
    },
    "ro": {
        "excellent": "Excelentă",
        "good": "Bună",
        "attention": "Atenție",
        "critical": "Critică",
        "healthy": "Sănătos",
        "operational": "Operațional",
        "degraded": "Degradat",
        "unavailable": "Indisponibil",
        "no_data": "Fără date",
    },
    "ua": {
        "excellent": "Відмінна",
        "good": "Добра",
        "attention": "Увага",
        "critical": "Критична",
        "healthy": "Справний",
        "operational": "Працює",
        "degraded": "Погіршений",
        "unavailable": "Недоступний",
        "no_data": "Немає даних",
    },
    "ru": {
        "excellent": "Отлично",
        "good": "Хорошо",
        "attention": "Внимание",
        "critical": "Критично",
        "healthy": "Исправно",
        "operational": "Работает",
        "degraded": "Снижено",
        "unavailable": "Недоступно",
        "no_data": "Нет данных",
    },
    "sa": {
        "excellent": "ممتاز",
        "good": "جيد",
        "attention": "انتباه",
        "critical": "حرج",
        "healthy": "سليم",
        "operational": "تشغيلي",
        "degraded": "متدهور",
        "unavailable": "غير متاح",
        "no_data": "لا توجد بيانات",
    },
}

HEALTH_VALUE_TEXTS["en_gb"] = HEALTH_VALUE_TEXTS["en_us"]

HEALTH_VALUE_TEXTS["ch"] = HEALTH_VALUE_TEXTS["de"]


HEALTH_SEMANTIC_ICONS = {
    "excellent": "🟢",
    "healthy": "🟢",
    "good": "🔵",
    "operational": "🔵",
    "attention": "🟠",
    "degraded": "🟠",
    "critical": "🔴",
    "unavailable": "🔴",
    "no_data": "⚪",
}


def health_value_t(
    key: str,
) -> str:
    """Traduz classificações e status."""
    idioma = health_table_lang()

    return HEALTH_VALUE_TEXTS.get(
        idioma,
        HEALTH_VALUE_TEXTS["pt"],
    ).get(
        key,
        HEALTH_VALUE_TEXTS["pt"].get(
            key,
            key,
        ),
    )


def classificacao_semantica_health(
    valor: Any,
) -> str:
    """Identifica a categoria da classificação."""
    texto = normalizar_valor_health(valor)

    if any(
        termo in texto
        for termo in (
            "critico",
            "critica",
            "critical",
            "ruim",
            "bad",
        )
    ):
        return "critical"

    if any(
        termo in texto
        for termo in (
            "atencao",
            "attention",
            "alerta",
            "regular",
        )
    ):
        return "attention"

    if any(
        termo in texto
        for termo in (
            "bom",
            "boa",
            "good",
        )
    ):
        return "good"

    if any(
        termo in texto
        for termo in (
            "excelente",
            "excellent",
            "otimo",
            "optimal",
        )
    ):
        return "excellent"

    return "no_data"


def status_semantico_health(
    valor: Any,
) -> str:
    """Identifica a categoria do status."""
    texto = normalizar_valor_health(valor)

    if any(
        termo in texto
        for termo in (
            "critico",
            "critical",
            "falha",
            "failed",
            "unhealthy",
        )
    ):
        return "critical"

    if any(
        termo in texto
        for termo in (
            "indisponivel",
            "unavailable",
            "offline",
        )
    ):
        return "unavailable"

    if any(
        termo in texto
        for termo in (
            "atencao",
            "attention",
            "degradado",
            "degraded",
            "warning",
        )
    ):
        return "degraded"

    if any(
        termo in texto
        for termo in (
            "operacional",
            "operational",
            "ativo",
            "active",
        )
    ):
        return "operational"

    if any(
        termo in texto
        for termo in (
            "saudavel",
            "healthy",
            "excelente",
            "excellent",
        )
    ):
        return "healthy"

    return "no_data"


def traduzir_classificacao_health(
    valor: Any,
) -> str:
    """Traduz classificação e acrescenta indicador."""
    categoria = classificacao_semantica_health(valor)

    return f"{HEALTH_SEMANTIC_ICONS[categoria]} {health_value_t(categoria)}"


def traduzir_status_health(
    valor: Any,
) -> str:
    """Traduz status e acrescenta indicador."""
    categoria = status_semantico_health(valor)

    return f"{HEALTH_SEMANTIC_ICONS[categoria]} {health_value_t(categoria)}"


def normalizar_valor_health(
    valor: Any,
) -> str:
    """Normaliza status e classificações."""
    texto = str(valor or "").strip().lower()

    texto = "".join(
        caractere
        for caractere in unicodedata.normalize(
            "NFKD",
            texto,
        )
        if not unicodedata.combining(caractere)
    )

    return texto


def estilo_semantico_health(
    valor: Any,
) -> str:
    """
    Mantém fundo preto e destaca somente
    a cor do texto semântico.
    """
    texto = str(valor or "")

    if "🔴" in texto:
        cor = "#F87171"
    elif "🟠" in texto:
        cor = "#F59E0B"
    elif "🔵" in texto:
        cor = "#60A5FA"
    elif "🟢" in texto:
        cor = "#22C55E"
    else:
        cor = "#94A3B8"

    return (
        "background-color: #020617;"
        f"color: {cor};"
        "font-weight: 800;"
        "border: 1px solid #1E293B;"
    )


def estilizar_tabela_health(
    tabela: pd.DataFrame,
):
    """
    Aplica fundo escuro e texto claro à tabela.
    """
    return tabela.style.set_properties(
        **{
            "background-color": "#020617",
            "color": "#F8FAFC",
            "border-color": "#1E293B",
            "font-weight": "600",
        }
    ).set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    (
                        "background-color",
                        "#0F172A",
                    ),
                    (
                        "color",
                        "#F8FAFC",
                    ),
                    (
                        "font-weight",
                        "700",
                    ),
                    (
                        "border",
                        "1px solid #334155",
                    ),
                ],
            },
            {
                "selector": "td",
                "props": [
                    (
                        "background-color",
                        "#020617",
                    ),
                    (
                        "color",
                        "#F8FAFC",
                    ),
                    (
                        "border",
                        "1px solid #1E293B",
                    ),
                ],
            },
        ]
    )


def estilizar_tabela_componentes_health(
    tabela: pd.DataFrame,
):
    """
    Aplica tema escuro e cores semânticas nas
    colunas de classificação e status.
    """
    styler = estilizar_tabela_health(tabela)

    colunas_semanticas = [
        health_table_t("classification"),
        health_table_t("status"),
    ]

    colunas_existentes = [
        coluna for coluna in colunas_semanticas if coluna in tabela.columns
    ]

    if not colunas_existentes:
        return styler

    return styler.apply(
        lambda coluna: [estilo_semantico_health(valor) for valor in coluna],
        subset=colunas_existentes,
    )


def preparar_componentes_exibicao(
    componentes: dict[str, Any],
) -> pd.DataFrame:
    """
    Converte componentes do Health Score em tabela.
    """
    linhas = []

    for nome, item in componentes.items():
        linhas.append(
            {
                "Componente": nome_componente_health(
                    nome,
                    nome.title(),
                ),
                "Score": float(
                    item.get(
                        "score",
                        0,
                    )
                ),
                "Peso (%)": round(
                    float(
                        item.get(
                            "peso",
                            0,
                        )
                    )
                    * 100,
                    1,
                ),
                "Contribuição": float(
                    item.get(
                        "contribuicao",
                        0,
                    )
                ),
                "Classificação": (
                    traduzir_classificacao_health(
                        item.get(
                            "classificacao",
                            "",
                        )
                    )
                ),
                "Status": (
                    traduzir_status_health(
                        item.get(
                            "status",
                            "",
                        )
                    )
                ),
            }
        )

    return pd.DataFrame(linhas)


def preparar_historico_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Prepara o histórico para gráficos e tabelas.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    base = df.copy()

    base["criado_em"] = pd.to_datetime(
        base["criado_em"],
        utc=True,
        errors="coerce",
    )

    colunas_numericas = [
        "score_global",
        "score_tools",
        "score_rag",
        "score_memoria",
        "score_infraestrutura",
        "score_timeline",
        "score_performance",
    ]

    for coluna in colunas_numericas:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(
                base[coluna],
                errors="coerce",
            )

    base = (
        base.dropna(subset=["criado_em"])
        .sort_values(
            "criado_em",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    return base


def render_health_history_section(
    *,
    resultado_atual: dict[str, Any],
) -> None:
    """
    Renderiza persistência, tendência e histórico.
    """
    try:
        from observability.health_history import (
            calcular_tendencia_health,
            carregar_health_history,
            salvar_health_snapshot,
        )
    except ImportError:
        from src.observability.health_history import (
            calcular_tendencia_health,
            carregar_health_history,
            salvar_health_snapshot,
        )

    st.divider()
    st.markdown(health_history_t("title"))

    st.caption(health_history_t("caption"))

    controle_1, controle_2, controle_3 = st.columns([1.2, 1.2, 2])

    periodo_label = controle_1.selectbox(
        health_history_t("period"),
        options=[
            7,
            30,
            90,
            None,
        ],
        format_func=lambda value: (
            health_history_t("period_all")
            if value is None
            else health_history_t(f"period_{value}")
        ),
        index=1,
        key="health_history_period",
    )

    limite = controle_2.selectbox(
        health_history_t("snapshot_limit"),
        options=[
            50,
            100,
            250,
            500,
        ],
        index=1,
        key="health_history_limit",
    )

    dias_selecionados = periodo_label

    with controle_3:
        st.write("")

        salvar = st.button(
            health_history_t("save_snapshot"),
            use_container_width=True,
            key="health_save_snapshot",
        )

    if salvar:
        resultado_salvar = salvar_health_snapshot(
            resultado_atual,
            origem="health_center",
            evitar_duplicado_minutos=5,
        )

        if not resultado_salvar.get("ok"):
            st.error(health_history_dynamic_t("save_error"))

        elif resultado_salvar.get("duplicado"):
            st.info(health_history_dynamic_t("duplicate_snapshot"))

        elif resultado_salvar.get("salvo"):
            st.success(health_history_dynamic_t("snapshot_saved"))

    historico_resultado = carregar_health_history(
        limite=int(limite),
        dias=dias_selecionados,
    )

    if not historico_resultado.get("ok"):
        st.error(health_history_dynamic_t("load_error"))
        return

    historico = preparar_historico_exibicao(historico_resultado.get("df"))

    if historico.empty:
        st.info(health_history_dynamic_t("empty_history"))
        return

    tendencia = calcular_tendencia_health(historico)

    snapshot_atual = historico.iloc[-1]

    snapshot_anterior = historico.iloc[-2] if len(historico) >= 2 else None

    delta_global = None

    if snapshot_anterior is not None:
        delta_global = float(snapshot_atual["score_global"]) - float(
            snapshot_anterior["score_global"]
        )

    metricas = st.columns(4)

    metricas[0].metric(
        health_history_t("snapshots"),
        len(historico),
    )

    metricas[1].metric(
        health_history_t("latest_score"),
        (f"{float(snapshot_atual['score_global']):.1f}/100"),
        delta=(f"{delta_global:+.1f}" if delta_global is not None else None),
    )

    metricas[2].metric(
        health_history_t("best_score"),
        (f"{float(historico['score_global'].max()):.1f}/100"),
    )

    metricas[3].metric(
        health_history_t("period_average"),
        (f"{float(historico['score_global'].mean()):.1f}/100"),
    )

    if tendencia.get("tem_comparacao"):
        direcao = tendencia.get("direcao")

        mensagem = (
            f"{tendencia.get('icone', '')} "
            f"{traduzir_tendencia_historico_health(tendencia)}"
        )

        if direcao == "melhora":
            st.success(mensagem)

        elif direcao == "piora":
            st.warning(mensagem)

        else:
            st.info(mensagem)

    else:
        st.info(health_history_dynamic_t("minimum_snapshots"))

    st.markdown(health_history_t("global_evolution"))

    history_date_label = health_history_t("date")
    history_score_label = health_history_t("health_score")

    grafico_global = (
        historico[
            [
                "criado_em",
                "score_global",
            ]
        ]
        .rename(
            columns={
                "criado_em": history_date_label,
                "score_global": history_score_label,
            }
        )
        .set_index(history_date_label)
    )

    fig_global = px.line(
        grafico_global.reset_index(),
        x=history_date_label,
        y=history_score_label,
        markers=True,
        color_discrete_sequence=[
            "#38BDF8",
        ],
    )

    fig_global.update_traces(
        line={
            "width": 3,
        },
        marker={
            "size": 9,
            "color": "#E0F2FE",
            "line": {
                "color": "#38BDF8",
                "width": 2,
            },
        },
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.14)",
        hovertemplate=(
            f"<b>%{{x}}</b><br>{history_score_label}: %{{y:.1f}}<extra></extra>"
        ),
    )

    fig_global.update_layout(
        xaxis_title=None,
        yaxis_title=history_score_label,
        showlegend=False,
    )

    fig_global.update_yaxes(
        range=[0, 100],
    )

    aplicar_tema_health_chart(
        fig_global,
        height=420,
    )

    st.plotly_chart(
        fig_global,
        width="stretch",
        key="health_global_evolution_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.markdown(health_history_t("component_evolution"))

    colunas_componentes = {
        "score_tools": health_table_t("tools"),
        "score_rag": health_table_t("rag"),
        "score_memoria": health_table_t("memory"),
        "score_infraestrutura": health_table_t("infrastructure"),
        "score_timeline": health_table_t("timeline"),
        "score_performance": health_table_t("performance"),
    }

    colunas_disponiveis = [
        coluna for coluna in colunas_componentes if coluna in historico.columns
    ]

    if colunas_disponiveis:
        grafico_componentes = (
            historico[
                [
                    "criado_em",
                    *colunas_disponiveis,
                ]
            ]
            .rename(
                columns={
                    "criado_em": history_date_label,
                    **colunas_componentes,
                }
            )
            .set_index(history_date_label)
        )

        componentes_series = list(grafico_componentes.columns)

        fig_componentes = px.line(
            grafico_componentes.reset_index(),
            x=history_date_label,
            y=componentes_series,
            markers=True,
            color_discrete_sequence=(HEALTH_SERIES_COLORS),
        )

        fig_componentes.update_traces(
            line={
                "width": 2.5,
            },
            marker={
                "size": 7,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{health_history_dynamic_t('score_hover')}: "
                "%{y:.1f}<extra></extra>"
            ),
        )

        fig_componentes.update_layout(
            xaxis_title=None,
            yaxis_title=health_history_dynamic_t("component_score"),
            legend_title_text=health_history_dynamic_t("component"),
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.28,
                "xanchor": "center",
                "x": 0.5,
            },
        )

        fig_componentes.update_yaxes(
            range=[0, 100],
        )

        aplicar_tema_health_chart(
            fig_componentes,
            height=470,
        )

        st.plotly_chart(
            fig_componentes,
            width="stretch",
            key="health_components_evolution_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    st.markdown(health_history_t("snapshot_audit"))

    tabela_colunas = [
        "id",
        "criado_em",
        "score_global",
        "score_tools",
        "score_rag",
        "score_memoria",
        "score_infraestrutura",
        "score_timeline",
        "score_performance",
        "classificacao",
        "componente_mais_fraco",
        "total_anomalias",
        "origem",
    ]

    tabela_colunas = [
        coluna for coluna in tabela_colunas if coluna in historico.columns
    ]

    tabela = (
        historico[tabela_colunas]
        .sort_values(
            "criado_em",
            ascending=False,
        )
        .rename(
            columns={
                "id": health_table_t("id"),
                "criado_em": health_table_t("date"),
                "score_global": health_table_t("global"),
                "score_tools": health_table_t("tools"),
                "score_rag": health_table_t("rag"),
                "score_memoria": health_table_t("memory"),
                "score_infraestrutura": (health_table_t("infrastructure")),
                "score_timeline": (health_table_t("timeline")),
                "score_performance": (health_table_t("performance")),
                "classificacao": (health_table_t("classification")),
                "componente_mais_fraco": (health_table_t("priority_component")),
                "total_anomalias": (health_table_t("anomalies")),
                "origem": health_table_t("origin"),
            }
        )
    )

    score_columns = [
        health_table_t("global"),
        health_table_t("tools"),
        health_table_t("rag"),
        health_table_t("memory"),
        health_table_t("infrastructure"),
        health_table_t("timeline"),
        health_table_t("performance"),
    ]

    history_column_config = {
        health_table_t("id"): (
            st.column_config.NumberColumn(
                health_table_t("id"),
                format="%d",
                width="small",
            )
        ),
        health_table_t("date"): (
            st.column_config.DatetimeColumn(
                health_table_t("date"),
                format=health_date_format(),
                width="medium",
            )
        ),
        health_table_t("anomalies"): (
            st.column_config.NumberColumn(
                health_table_t("anomalies"),
                format="%d",
                width="small",
            )
        ),
        health_table_t("classification"): (
            st.column_config.TextColumn(
                health_table_t("classification"),
                width="medium",
            )
        ),
        health_table_t("priority_component"): (
            st.column_config.TextColumn(
                health_table_t("priority_component"),
                width="medium",
            )
        ),
        health_table_t("origin"): (
            st.column_config.TextColumn(
                health_table_t("origin"),
                width="medium",
            )
        ),
    }

    for score_column in score_columns:
        if score_column in tabela.columns:
            history_column_config[score_column] = st.column_config.ProgressColumn(
                score_column,
                min_value=0.0,
                max_value=100.0,
                format="%.1f",
                width="small",
            )

    st.dataframe(
        estilizar_tabela_health(tabela),
        use_container_width=True,
        hide_index=True,
        height=430,
        column_config=history_column_config,
    )

    csv = tabela.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        health_table_t("export_history"),
        data=csv,
        file_name=("inna_health_score_history.csv"),
        mime="text/csv",
        use_container_width=True,
        key="health_history_download",
    )


HEALTH_PAGE_TEXTS = {
    "pt": {
        "title": "❤️ Central de Saúde da INNA",
        "caption": (
            "Saúde consolidada das ferramentas, RAG, "
            "memória, infraestrutura, linha do tempo "
            "e desempenho."
        ),
    },
    "en_us": {
        "title": "❤️ INNA Health Center",
        "caption": (
            "Consolidated health of tools, RAG, "
            "memory, infrastructure, timeline "
            "and performance."
        ),
    },
    "en_gb": {
        "title": "❤️ INNA Health Centre",
        "caption": (
            "Consolidated health of tools, RAG, "
            "memory, infrastructure, timeline "
            "and performance."
        ),
    },
    "es": {
        "title": "❤️ Centro de Salud de INNA",
        "caption": (
            "Salud consolidada de herramientas, RAG, "
            "memoria, infraestructura, línea de tiempo "
            "y rendimiento."
        ),
    },
    "fr": {
        "title": "❤️ Centre de santé d’INNA",
        "caption": (
            "État consolidé des outils, du RAG, "
            "de la mémoire, de l’infrastructure, "
            "de la chronologie et des performances."
        ),
    },
    "de": {
        "title": "❤️ INNA-Systemzustand",
        "caption": (
            "Konsolidierter Zustand von Tools, RAG, "
            "Speicher, Infrastruktur, Zeitachse "
            "und Leistung."
        ),
    },
    "it": {
        "title": "❤️ Centro salute INNA",
        "caption": (
            "Stato consolidato di strumenti, RAG, "
            "memoria, infrastruttura, timeline "
            "e prestazioni."
        ),
    },
    "ro": {
        "title": "❤️ Centrul de sănătate INNA",
        "caption": (
            "Starea consolidată a instrumentelor, RAG, "
            "memoriei, infrastructurii, cronologiei "
            "și performanței."
        ),
    },
    "ua": {
        "title": "❤️ Центр стану системи INNA",
        "caption": (
            "Зведений стан інструментів, RAG, пам’яті, "
            "інфраструктури, часової шкали "
            "та продуктивності."
        ),
    },
    "ru": {
        "title": "❤️ Центр состояния системы INNA",
        "caption": (
            "Сводное состояние инструментов, RAG, "
            "памяти, инфраструктуры, временной шкалы "
            "и производительности."
        ),
    },
    "sa": {
        "title": "❤️ مركز صحة نظام INNA",
        "caption": (
            "الحالة المجمعة للأدوات وRAG والذاكرة والبنية التحتية والخط الزمني والأداء."
        ),
    },
}

HEALTH_PAGE_TEXTS["ch"] = HEALTH_PAGE_TEXTS["de"]


# HEALTH_SCORE_MAIN_PANEL_I18N

HEALTH_PAGE_MAIN_TEXTS = {
    "pt": {
        "tools_events": "Eventos das Tools",
        "analysed_traces": "Traces analisados",
        "refresh": "🔄 Atualizar Health Score",
        "no_data": "Sem dados",
        "global_health": "## Saúde global",
        "health_score": "INNA Health Score",
        "classification": "Classificação",
        "strongest_component": "Componente mais forte",
        "priority_component": "Componente prioritário",
        "excellent_message": ("A INNA está operando em excelente estado."),
        "healthy_message": (
            "A INNA está saudável, com alguns pontos que merecem acompanhamento."
        ),
        "attention_message": ("A INNA apresenta componentes que precisam de atenção."),
        "critical_message": (
            "A saúde global está crítica. Priorize os componentes com menor score."
        ),
        "component_scores": "## Scores por componente",
        "score": "Score",
        "global_weight": "Peso no score global",
        "view_penalties": "Ver penalidades",
        "no_penalty": "Nenhuma penalidade aplicada.",
        "priority_recommendations": ("## Recomendações prioritárias"),
        "component_score": "Score do componente",
        "component": "Componente",
    },
    "en_us": {
        "tools_events": "Tool events",
        "analysed_traces": "Analysed traces",
        "refresh": "🔄 Refresh Health Score",
        "no_data": "No data",
        "global_health": "## Global health",
        "health_score": "INNA Health Score",
        "classification": "Classification",
        "strongest_component": "Strongest component",
        "priority_component": "Priority component",
        "excellent_message": ("INNA is operating in excellent condition."),
        "healthy_message": (
            "INNA is healthy, with a few points that should continue to be monitored."
        ),
        "attention_message": ("INNA has components that require attention."),
        "critical_message": (
            "Global health is critical. Prioritise the "
            "components with the lowest scores."
        ),
        "component_scores": "## Scores by component",
        "score": "Score",
        "global_weight": "Weight in global score",
        "view_penalties": "View penalties",
        "no_penalty": "No penalty was applied.",
        "priority_recommendations": ("## Priority recommendations"),
        "component_score": "Component score",
        "component": "Component",
    },
    "en_gb": {
        "tools_events": "Tool events",
        "analysed_traces": "Analysed traces",
        "refresh": "🔄 Refresh Health Score",
        "no_data": "No data",
        "global_health": "## Global health",
        "health_score": "INNA Health Score",
        "classification": "Classification",
        "strongest_component": "Strongest component",
        "priority_component": "Priority component",
        "excellent_message": ("INNA is operating in excellent condition."),
        "healthy_message": (
            "INNA is healthy, with a few points that should continue to be monitored."
        ),
        "attention_message": ("INNA has components that require attention."),
        "critical_message": (
            "Global health is critical. Prioritise the "
            "components with the lowest scores."
        ),
        "component_scores": "## Scores by component",
        "score": "Score",
        "global_weight": "Weight in global score",
        "view_penalties": "View penalties",
        "no_penalty": "No penalty was applied.",
        "priority_recommendations": ("## Priority recommendations"),
        "component_score": "Component score",
        "component": "Component",
    },
    "es": {
        "tools_events": "Eventos de las herramientas",
        "analysed_traces": "Trazas analizadas",
        "refresh": "🔄 Actualizar Health Score",
        "no_data": "Sin datos",
        "global_health": "## Salud global",
        "health_score": "Health Score de INNA",
        "classification": "Clasificación",
        "strongest_component": "Componente más fuerte",
        "priority_component": "Componente prioritario",
        "excellent_message": ("INNA está funcionando en un estado excelente."),
        "healthy_message": (
            "INNA está saludable, con algunos puntos "
            "que deben seguir siendo supervisados."
        ),
        "attention_message": ("INNA tiene componentes que requieren atención."),
        "critical_message": (
            "La salud global es crítica. Priorice los componentes con menor puntuación."
        ),
        "component_scores": "## Puntuaciones por componente",
        "score": "Puntuación",
        "global_weight": "Peso en la puntuación global",
        "view_penalties": "Ver penalizaciones",
        "no_penalty": "No se aplicó ninguna penalización.",
        "priority_recommendations": ("## Recomendaciones prioritarias"),
        "component_score": "Puntuación del componente",
        "component": "Componente",
    },
    "fr": {
        "tools_events": "Événements des outils",
        "analysed_traces": "Traces analysées",
        "refresh": "🔄 Actualiser le Health Score",
        "no_data": "Aucune donnée",
        "global_health": "## Santé globale",
        "health_score": "Health Score d’INNA",
        "classification": "Classement",
        "strongest_component": "Composant le plus fort",
        "priority_component": "Composant prioritaire",
        "excellent_message": ("INNA fonctionne dans un excellent état."),
        "healthy_message": (
            "INNA est en bonne santé, avec quelques points "
            "qui doivent rester sous surveillance."
        ),
        "attention_message": (
            "Certains composants d’INNA nécessitent une attention particulière."
        ),
        "critical_message": (
            "La santé globale est critique. Donnez la "
            "priorité aux composants ayant le score le plus bas."
        ),
        "component_scores": "## Scores par composant",
        "score": "Score",
        "global_weight": "Poids dans le score global",
        "view_penalties": "Voir les pénalités",
        "no_penalty": "Aucune pénalité appliquée.",
        "priority_recommendations": ("## Recommandations prioritaires"),
        "component_score": "Score du composant",
        "component": "Composant",
    },
    "de": {
        "tools_events": "Tool-Ereignisse",
        "analysed_traces": "Analysierte Traces",
        "refresh": "🔄 Health Score aktualisieren",
        "no_data": "Keine Daten",
        "global_health": "## Gesamtzustand",
        "health_score": "INNA Health Score",
        "classification": "Klassifizierung",
        "strongest_component": "Stärkste Komponente",
        "priority_component": "Prioritätskomponente",
        "excellent_message": ("INNA befindet sich in einem ausgezeichneten Zustand."),
        "healthy_message": (
            "INNA ist gesund. Einige Punkte sollten weiterhin überwacht werden."
        ),
        "attention_message": ("Einige INNA-Komponenten benötigen Aufmerksamkeit."),
        "critical_message": (
            "Der Gesamtzustand ist kritisch. Priorisieren "
            "Sie die Komponenten mit den niedrigsten Scores."
        ),
        "component_scores": "## Scores nach Komponente",
        "score": "Score",
        "global_weight": "Gewicht im Gesamtscore",
        "view_penalties": "Abzüge anzeigen",
        "no_penalty": "Keine Abzüge angewendet.",
        "priority_recommendations": ("## Priorisierte Empfehlungen"),
        "component_score": "Komponentenscore",
        "component": "Komponente",
    },
    "it": {
        "tools_events": "Eventi degli strumenti",
        "analysed_traces": "Trace analizzate",
        "refresh": "🔄 Aggiorna Health Score",
        "no_data": "Nessun dato",
        "global_health": "## Stato globale",
        "health_score": "Health Score INNA",
        "classification": "Classificazione",
        "strongest_component": "Componente più forte",
        "priority_component": "Componente prioritario",
        "excellent_message": ("INNA sta operando in condizioni eccellenti."),
        "healthy_message": (
            "INNA è in buona salute, con alcuni punti da continuare a monitorare."
        ),
        "attention_message": ("INNA presenta componenti che richiedono attenzione."),
        "critical_message": (
            "Lo stato globale è critico. Dare priorità ai "
            "componenti con il punteggio più basso."
        ),
        "component_scores": "## Punteggi per componente",
        "score": "Punteggio",
        "global_weight": "Peso nel punteggio globale",
        "view_penalties": "Visualizza penalità",
        "no_penalty": "Nessuna penalità applicata.",
        "priority_recommendations": ("## Raccomandazioni prioritarie"),
        "component_score": "Punteggio del componente",
        "component": "Componente",
    },
    "ro": {
        "tools_events": "Evenimentele instrumentelor",
        "analysed_traces": "Trace analizate",
        "refresh": "🔄 Actualizează Health Score",
        "no_data": "Fără date",
        "global_health": "## Stare globală",
        "health_score": "Health Score INNA",
        "classification": "Clasificare",
        "strongest_component": "Cea mai puternică componentă",
        "priority_component": "Componentă prioritară",
        "excellent_message": ("INNA funcționează într-o stare excelentă."),
        "healthy_message": (
            "INNA este sănătoasă, cu unele puncte care "
            "trebuie monitorizate în continuare."
        ),
        "attention_message": ("INNA are componente care necesită atenție."),
        "critical_message": (
            "Starea globală este critică. Prioritizați "
            "componentele cu cele mai mici scoruri."
        ),
        "component_scores": "## Scoruri pe componente",
        "score": "Scor",
        "global_weight": "Pondere în scorul global",
        "view_penalties": "Vezi penalizările",
        "no_penalty": "Nu a fost aplicată nicio penalizare.",
        "priority_recommendations": ("## Recomandări prioritare"),
        "component_score": "Scorul componentei",
        "component": "Componentă",
    },
    "ua": {
        "tools_events": "Події інструментів",
        "analysed_traces": "Проаналізовані трасування",
        "refresh": "🔄 Оновити Health Score",
        "no_data": "Немає даних",
        "global_health": "## Загальний стан",
        "health_score": "Health Score INNA",
        "classification": "Класифікація",
        "strongest_component": "Найсильніший компонент",
        "priority_component": "Пріоритетний компонент",
        "excellent_message": ("INNA працює у відмінному стані."),
        "healthy_message": (
            "INNA перебуває у доброму стані, але деякі "
            "показники слід продовжувати контролювати."
        ),
        "attention_message": ("Деякі компоненти INNA потребують уваги."),
        "critical_message": (
            "Загальний стан критичний. Надайте пріоритет "
            "компонентам із найнижчими оцінками."
        ),
        "component_scores": "## Оцінки за компонентами",
        "score": "Оцінка",
        "global_weight": "Вага в загальній оцінці",
        "view_penalties": "Переглянути штрафи",
        "no_penalty": "Штрафи не застосовувалися.",
        "priority_recommendations": ("## Пріоритетні рекомендації"),
        "component_score": "Оцінка компонента",
        "component": "Компонент",
    },
    "ru": {
        "tools_events": "События инструментов",
        "analysed_traces": "Проанализированные трассировки",
        "refresh": "🔄 Обновить Health Score",
        "no_data": "Нет данных",
        "global_health": "## Общее состояние",
        "health_score": "Health Score INNA",
        "classification": "Классификация",
        "strongest_component": "Самый сильный компонент",
        "priority_component": "Приоритетный компонент",
        "excellent_message": ("INNA работает в отличном состоянии."),
        "healthy_message": (
            "INNA находится в хорошем состоянии, однако "
            "некоторые показатели следует контролировать."
        ),
        "attention_message": ("Некоторые компоненты INNA требуют внимания."),
        "critical_message": (
            "Общее состояние критическое. Приоритет следует "
            "отдать компонентам с самыми низкими оценками."
        ),
        "component_scores": "## Оценки по компонентам",
        "score": "Оценка",
        "global_weight": "Вес в общей оценке",
        "view_penalties": "Показать штрафы",
        "no_penalty": "Штрафы не применялись.",
        "priority_recommendations": ("## Приоритетные рекомендации"),
        "component_score": "Оценка компонента",
        "component": "Компонент",
    },
    "sa": {
        "tools_events": "أحداث الأدوات",
        "analysed_traces": "عمليات التتبع المحللة",
        "refresh": "🔄 تحديث Health Score",
        "no_data": "لا توجد بيانات",
        "global_health": "## الحالة العامة",
        "health_score": "Health Score لـ INNA",
        "classification": "التصنيف",
        "strongest_component": "أقوى مكوّن",
        "priority_component": "المكوّن ذو الأولوية",
        "excellent_message": ("تعمل INNA في حالة ممتازة."),
        "healthy_message": (
            "تعمل INNA بحالة جيدة، مع وجود بعض المؤشرات "
            "التي ينبغي الاستمرار في مراقبتها."
        ),
        "attention_message": ("توجد مكوّنات في INNA تتطلب الانتباه."),
        "critical_message": (
            "الحالة العامة حرجة. أعطِ الأولوية للمكوّنات ذات الدرجات الأقل."
        ),
        "component_scores": "## الدرجات حسب المكوّن",
        "score": "الدرجة",
        "global_weight": "الوزن في الدرجة الإجمالية",
        "view_penalties": "عرض العقوبات",
        "no_penalty": "لم يتم تطبيق أي عقوبة.",
        "priority_recommendations": ("## التوصيات ذات الأولوية"),
        "component_score": "درجة المكوّن",
        "component": "المكوّن",
    },
    "ch": {
        "tools_events": "Tool-Ereignisse",
        "analysed_traces": "Analysierte Traces",
        "refresh": "🔄 Health Score aktualisieren",
        "no_data": "Keine Daten",
        "global_health": "## Gesamtzustand",
        "health_score": "INNA Health Score",
        "classification": "Klassifizierung",
        "strongest_component": "Stärkste Komponente",
        "priority_component": "Prioritätskomponente",
        "excellent_message": ("INNA befindet sich in einem ausgezeichneten Zustand."),
        "healthy_message": (
            "INNA ist gesund. Einige Punkte sollten weiterhin überwacht werden."
        ),
        "attention_message": ("Einige INNA-Komponenten benötigen Aufmerksamkeit."),
        "critical_message": (
            "Der Gesamtzustand ist kritisch. Priorisieren "
            "Sie die Komponenten mit den niedrigsten Scores."
        ),
        "component_scores": "## Scores nach Komponente",
        "score": "Score",
        "global_weight": "Gewicht im Gesamtscore",
        "view_penalties": "Abzüge anzeigen",
        "no_penalty": "Keine Abzüge angewendet.",
        "priority_recommendations": ("## Priorisierte Empfehlungen"),
        "component_score": "Komponentenscore",
        "component": "Komponente",
    },
}

for language, texts in HEALTH_PAGE_MAIN_TEXTS.items():
    HEALTH_PAGE_TEXTS.setdefault(
        language,
        {},
    ).update(texts)


# HEALTH_SCORE_HISTORY_I18N

HEALTH_HISTORY_TEXTS = {
    "pt": {
        "title": "## 📈 Histórico do Health Score",
        "caption": (
            "Acompanhe a evolução da saúde operacional da INNA ao longo do tempo."
        ),
        "period": "Período histórico",
        "period_7": "7 dias",
        "period_30": "30 dias",
        "period_90": "90 dias",
        "period_all": "Todo o histórico",
        "snapshot_limit": "Limite de snapshots",
        "save_snapshot": "💾 Salvar snapshot atual",
        "snapshots": "Snapshots",
        "latest_score": "Último score",
        "best_score": "Melhor score",
        "period_average": "Média do período",
        "global_evolution": "### Evolução do score global",
        "component_evolution": "### Evolução por componente",
        "snapshot_audit": "### Auditoria dos snapshots",
        "date": "Data",
        "health_score": "Health Score",
    },
    "en_us": {
        "title": "## 📈 Health Score history",
        "caption": ("Track the evolution of INNA's operational health over time."),
        "period": "History period",
        "period_7": "7 days",
        "period_30": "30 days",
        "period_90": "90 days",
        "period_all": "Entire history",
        "snapshot_limit": "Snapshot limit",
        "save_snapshot": "💾 Save current snapshot",
        "snapshots": "Snapshots",
        "latest_score": "Latest score",
        "best_score": "Best score",
        "period_average": "Period average",
        "global_evolution": "### Global score evolution",
        "component_evolution": "### Evolution by component",
        "snapshot_audit": "### Snapshot audit",
        "date": "Date",
        "health_score": "Health Score",
    },
    "en_gb": {
        "title": "## 📈 Health Score history",
        "caption": ("Track the evolution of INNA's operational health over time."),
        "period": "History period",
        "period_7": "7 days",
        "period_30": "30 days",
        "period_90": "90 days",
        "period_all": "Entire history",
        "snapshot_limit": "Snapshot limit",
        "save_snapshot": "💾 Save current snapshot",
        "snapshots": "Snapshots",
        "latest_score": "Latest score",
        "best_score": "Best score",
        "period_average": "Period average",
        "global_evolution": "### Global score evolution",
        "component_evolution": "### Evolution by component",
        "snapshot_audit": "### Snapshot audit",
        "date": "Date",
        "health_score": "Health Score",
    },
    "es": {
        "title": "## 📈 Historial del Health Score",
        "caption": (
            "Siga la evolución de la salud operativa de INNA a lo largo del tiempo."
        ),
        "period": "Período histórico",
        "period_7": "7 días",
        "period_30": "30 días",
        "period_90": "90 días",
        "period_all": "Todo el historial",
        "snapshot_limit": "Límite de snapshots",
        "save_snapshot": "💾 Guardar snapshot actual",
        "snapshots": "Snapshots",
        "latest_score": "Última puntuación",
        "best_score": "Mejor puntuación",
        "period_average": "Promedio del período",
        "global_evolution": "### Evolución de la puntuación global",
        "component_evolution": "### Evolución por componente",
        "snapshot_audit": "### Auditoría de snapshots",
        "date": "Fecha",
        "health_score": "Health Score",
    },
    "fr": {
        "title": "## 📈 Historique du Health Score",
        "caption": (
            "Suivez l’évolution de la santé opérationnelle d’INNA au fil du temps."
        ),
        "period": "Période historique",
        "period_7": "7 jours",
        "period_30": "30 jours",
        "period_90": "90 jours",
        "period_all": "Historique complet",
        "snapshot_limit": "Limite de snapshots",
        "save_snapshot": "💾 Enregistrer le snapshot actuel",
        "snapshots": "Snapshots",
        "latest_score": "Dernier score",
        "best_score": "Meilleur score",
        "period_average": "Moyenne de la période",
        "global_evolution": "### Évolution du score global",
        "component_evolution": "### Évolution par composant",
        "snapshot_audit": "### Audit des snapshots",
        "date": "Date",
        "health_score": "Health Score",
    },
    "de": {
        "title": "## 📈 Health-Score-Verlauf",
        "caption": (
            "Verfolgen Sie die Entwicklung des "
            "Betriebszustands von INNA im Zeitverlauf."
        ),
        "period": "Verlaufszeitraum",
        "period_7": "7 Tage",
        "period_30": "30 Tage",
        "period_90": "90 Tage",
        "period_all": "Gesamter Verlauf",
        "snapshot_limit": "Snapshot-Limit",
        "save_snapshot": "💾 Aktuellen Snapshot speichern",
        "snapshots": "Snapshots",
        "latest_score": "Letzter Score",
        "best_score": "Bester Score",
        "period_average": "Zeitraumdurchschnitt",
        "global_evolution": "### Entwicklung des Gesamtscores",
        "component_evolution": "### Entwicklung nach Komponente",
        "snapshot_audit": "### Snapshot-Audit",
        "date": "Datum",
        "health_score": "Health Score",
    },
    "it": {
        "title": "## 📈 Cronologia del Health Score",
        "caption": ("Segui l’evoluzione dello stato operativo di INNA nel tempo."),
        "period": "Periodo storico",
        "period_7": "7 giorni",
        "period_30": "30 giorni",
        "period_90": "90 giorni",
        "period_all": "Intera cronologia",
        "snapshot_limit": "Limite snapshot",
        "save_snapshot": "💾 Salva snapshot attuale",
        "snapshots": "Snapshot",
        "latest_score": "Ultimo punteggio",
        "best_score": "Miglior punteggio",
        "period_average": "Media del periodo",
        "global_evolution": "### Evoluzione del punteggio globale",
        "component_evolution": "### Evoluzione per componente",
        "snapshot_audit": "### Audit degli snapshot",
        "date": "Data",
        "health_score": "Health Score",
    },
    "ro": {
        "title": "## 📈 Istoricul Health Score",
        "caption": ("Urmăriți evoluția stării operaționale a INNA în timp."),
        "period": "Perioadă istorică",
        "period_7": "7 zile",
        "period_30": "30 de zile",
        "period_90": "90 de zile",
        "period_all": "Întregul istoric",
        "snapshot_limit": "Limită de snapshot-uri",
        "save_snapshot": "💾 Salvează snapshot-ul actual",
        "snapshots": "Snapshot-uri",
        "latest_score": "Ultimul scor",
        "best_score": "Cel mai bun scor",
        "period_average": "Media perioadei",
        "global_evolution": "### Evoluția scorului global",
        "component_evolution": "### Evoluția pe componente",
        "snapshot_audit": "### Auditul snapshot-urilor",
        "date": "Data",
        "health_score": "Health Score",
    },
    "ua": {
        "title": "## 📈 Історія Health Score",
        "caption": ("Відстежуйте зміну робочого стану INNA з часом."),
        "period": "Період історії",
        "period_7": "7 днів",
        "period_30": "30 днів",
        "period_90": "90 днів",
        "period_all": "Уся історія",
        "snapshot_limit": "Ліміт знімків",
        "save_snapshot": "💾 Зберегти поточний знімок",
        "snapshots": "Знімки",
        "latest_score": "Остання оцінка",
        "best_score": "Найкраща оцінка",
        "period_average": "Середнє за період",
        "global_evolution": "### Динаміка загальної оцінки",
        "component_evolution": "### Динаміка за компонентами",
        "snapshot_audit": "### Аудит знімків",
        "date": "Дата",
        "health_score": "Health Score",
    },
    "ru": {
        "title": "## 📈 История Health Score",
        "caption": (
            "Отслеживайте изменение рабочего состояния INNA с течением времени."
        ),
        "period": "Период истории",
        "period_7": "7 дней",
        "period_30": "30 дней",
        "period_90": "90 дней",
        "period_all": "Вся история",
        "snapshot_limit": "Лимит снимков",
        "save_snapshot": "💾 Сохранить текущий снимок",
        "snapshots": "Снимки",
        "latest_score": "Последняя оценка",
        "best_score": "Лучшая оценка",
        "period_average": "Среднее за период",
        "global_evolution": "### Динамика общей оценки",
        "component_evolution": "### Динамика по компонентам",
        "snapshot_audit": "### Аудит снимков",
        "date": "Дата",
        "health_score": "Health Score",
    },
    "sa": {
        "title": "## 📈 سجل Health Score",
        "caption": ("تابع تطور الحالة التشغيلية لنظام INNA بمرور الوقت."),
        "period": "الفترة التاريخية",
        "period_7": "7 أيام",
        "period_30": "30 يومًا",
        "period_90": "90 يومًا",
        "period_all": "السجل الكامل",
        "snapshot_limit": "حد اللقطات",
        "save_snapshot": "💾 حفظ اللقطة الحالية",
        "snapshots": "اللقطات",
        "latest_score": "آخر درجة",
        "best_score": "أفضل درجة",
        "period_average": "متوسط الفترة",
        "global_evolution": "### تطور الدرجة الإجمالية",
        "component_evolution": "### التطور حسب المكوّن",
        "snapshot_audit": "### تدقيق اللقطات",
        "date": "التاريخ",
        "health_score": "Health Score",
    },
}

HEALTH_HISTORY_TEXTS["ch"] = dict(HEALTH_HISTORY_TEXTS["de"])


def health_history_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz textos do histórico do Health Score."""
    idioma = health_table_lang()

    return HEALTH_HISTORY_TEXTS.get(
        idioma,
        HEALTH_HISTORY_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


# HEALTH_SCORE_HISTORY_DYNAMIC_I18N

HEALTH_HISTORY_DYNAMIC_TEXTS = {
    "pt": {
        "save_error": "Não foi possível salvar o snapshot.",
        "duplicate_snapshot": (
            "Um snapshot com o mesmo score já foi salvo nos últimos cinco minutos."
        ),
        "snapshot_saved": ("Snapshot salvo no PostgreSQL/Neon."),
        "load_error": ("Não foi possível carregar o histórico."),
        "empty_history": ("Nenhum snapshot foi encontrado para o período selecionado."),
        "minimum_snapshots": (
            "É necessário salvar pelo menos dois snapshots para calcular a tendência."
        ),
        "trend_improving": ("O Health Score apresentou melhora no período."),
        "trend_worsening": ("O Health Score apresentou queda no período."),
        "trend_stable": ("O Health Score permaneceu estável no período."),
        "score_hover": "Score",
        "component_score": "Score do componente",
        "component": "Componente",
    },
    "en_us": {
        "save_error": "The snapshot could not be saved.",
        "duplicate_snapshot": (
            "A snapshot with the same score was already saved in the last five minutes."
        ),
        "snapshot_saved": ("Snapshot saved to PostgreSQL/Neon."),
        "load_error": ("The history could not be loaded."),
        "empty_history": ("No snapshot was found for the selected period."),
        "minimum_snapshots": (
            "At least two snapshots must be saved to calculate the trend."
        ),
        "trend_improving": ("The Health Score improved during the period."),
        "trend_worsening": ("The Health Score declined during the period."),
        "trend_stable": ("The Health Score remained stable during the period."),
        "score_hover": "Score",
        "component_score": "Component score",
        "component": "Component",
    },
    "en_gb": {
        "save_error": "The snapshot could not be saved.",
        "duplicate_snapshot": (
            "A snapshot with the same score was already saved in the last five minutes."
        ),
        "snapshot_saved": ("Snapshot saved to PostgreSQL/Neon."),
        "load_error": ("The history could not be loaded."),
        "empty_history": ("No snapshot was found for the selected period."),
        "minimum_snapshots": (
            "At least two snapshots must be saved to calculate the trend."
        ),
        "trend_improving": ("The Health Score improved during the period."),
        "trend_worsening": ("The Health Score declined during the period."),
        "trend_stable": ("The Health Score remained stable during the period."),
        "score_hover": "Score",
        "component_score": "Component score",
        "component": "Component",
    },
    "es": {
        "save_error": "No fue posible guardar el snapshot.",
        "duplicate_snapshot": (
            "Ya se guardó un snapshot con la misma puntuación "
            "en los últimos cinco minutos."
        ),
        "snapshot_saved": ("Snapshot guardado en PostgreSQL/Neon."),
        "load_error": ("No fue posible cargar el historial."),
        "empty_history": (
            "No se encontró ningún snapshot para el período seleccionado."
        ),
        "minimum_snapshots": (
            "Es necesario guardar al menos dos snapshots para calcular la tendencia."
        ),
        "trend_improving": ("El Health Score mejoró durante el período."),
        "trend_worsening": ("El Health Score disminuyó durante el período."),
        "trend_stable": ("El Health Score permaneció estable durante el período."),
        "score_hover": "Puntuación",
        "component_score": "Puntuación del componente",
        "component": "Componente",
    },
    "fr": {
        "save_error": "Impossible d’enregistrer le snapshot.",
        "duplicate_snapshot": (
            "Un snapshot avec le même score a déjà été "
            "enregistré au cours des cinq dernières minutes."
        ),
        "snapshot_saved": ("Snapshot enregistré dans PostgreSQL/Neon."),
        "load_error": ("Impossible de charger l’historique."),
        "empty_history": ("Aucun snapshot trouvé pour la période sélectionnée."),
        "minimum_snapshots": (
            "Au moins deux snapshots doivent être enregistrés "
            "pour calculer la tendance."
        ),
        "trend_improving": ("Le Health Score s’est amélioré sur la période."),
        "trend_worsening": ("Le Health Score a diminué sur la période."),
        "trend_stable": ("Le Health Score est resté stable sur la période."),
        "score_hover": "Score",
        "component_score": "Score du composant",
        "component": "Composant",
    },
    "de": {
        "save_error": "Der Snapshot konnte nicht gespeichert werden.",
        "duplicate_snapshot": (
            "Ein Snapshot mit demselben Score wurde bereits "
            "in den letzten fünf Minuten gespeichert."
        ),
        "snapshot_saved": ("Snapshot in PostgreSQL/Neon gespeichert."),
        "load_error": ("Der Verlauf konnte nicht geladen werden."),
        "empty_history": (
            "Für den ausgewählten Zeitraum wurde kein Snapshot gefunden."
        ),
        "minimum_snapshots": (
            "Zur Berechnung des Trends müssen mindestens "
            "zwei Snapshots gespeichert werden."
        ),
        "trend_improving": ("Der Health Score hat sich im Zeitraum verbessert."),
        "trend_worsening": ("Der Health Score ist im Zeitraum gesunken."),
        "trend_stable": ("Der Health Score blieb im Zeitraum stabil."),
        "score_hover": "Score",
        "component_score": "Komponentenscore",
        "component": "Komponente",
    },
    "it": {
        "save_error": "Impossibile salvare lo snapshot.",
        "duplicate_snapshot": (
            "Uno snapshot con lo stesso punteggio è già stato "
            "salvato negli ultimi cinque minuti."
        ),
        "snapshot_saved": ("Snapshot salvato in PostgreSQL/Neon."),
        "load_error": ("Impossibile caricare la cronologia."),
        "empty_history": ("Nessuno snapshot trovato per il periodo selezionato."),
        "minimum_snapshots": (
            "È necessario salvare almeno due snapshot per calcolare la tendenza."
        ),
        "trend_improving": ("Il Health Score è migliorato nel periodo."),
        "trend_worsening": ("Il Health Score è diminuito nel periodo."),
        "trend_stable": ("Il Health Score è rimasto stabile nel periodo."),
        "score_hover": "Punteggio",
        "component_score": "Punteggio del componente",
        "component": "Componente",
    },
    "ro": {
        "save_error": "Snapshot-ul nu a putut fi salvat.",
        "duplicate_snapshot": (
            "Un snapshot cu același scor a fost deja salvat în ultimele cinci minute."
        ),
        "snapshot_saved": ("Snapshot salvat în PostgreSQL/Neon."),
        "load_error": ("Istoricul nu a putut fi încărcat."),
        "empty_history": ("Nu a fost găsit niciun snapshot pentru perioada selectată."),
        "minimum_snapshots": (
            "Trebuie salvate cel puțin două snapshot-uri pentru calcularea tendinței."
        ),
        "trend_improving": ("Health Score s-a îmbunătățit în această perioadă."),
        "trend_worsening": ("Health Score a scăzut în această perioadă."),
        "trend_stable": ("Health Score a rămas stabil în această perioadă."),
        "score_hover": "Scor",
        "component_score": "Scorul componentei",
        "component": "Componentă",
    },
    "ua": {
        "save_error": "Не вдалося зберегти знімок.",
        "duplicate_snapshot": (
            "Знімок із такою самою оцінкою вже було "
            "збережено протягом останніх п’яти хвилин."
        ),
        "snapshot_saved": ("Знімок збережено в PostgreSQL/Neon."),
        "load_error": ("Не вдалося завантажити історію."),
        "empty_history": ("Для вибраного періоду знімків не знайдено."),
        "minimum_snapshots": (
            "Для розрахунку тенденції потрібно зберегти щонайменше два знімки."
        ),
        "trend_improving": ("Health Score покращився за вибраний період."),
        "trend_worsening": ("Health Score знизився за вибраний період."),
        "trend_stable": ("Health Score залишався стабільним за вибраний період."),
        "score_hover": "Оцінка",
        "component_score": "Оцінка компонента",
        "component": "Компонент",
    },
    "ru": {
        "save_error": "Не удалось сохранить снимок.",
        "duplicate_snapshot": (
            "Снимок с такой же оценкой уже был сохранён в течение последних пяти минут."
        ),
        "snapshot_saved": ("Снимок сохранён в PostgreSQL/Neon."),
        "load_error": ("Не удалось загрузить историю."),
        "empty_history": ("Для выбранного периода снимки не найдены."),
        "minimum_snapshots": (
            "Для расчёта тенденции необходимо сохранить как минимум два снимка."
        ),
        "trend_improving": ("Health Score улучшился за выбранный период."),
        "trend_worsening": ("Health Score снизился за выбранный период."),
        "trend_stable": ("Health Score оставался стабильным за выбранный период."),
        "score_hover": "Оценка",
        "component_score": "Оценка компонента",
        "component": "Компонент",
    },
    "sa": {
        "save_error": "تعذر حفظ اللقطة.",
        "duplicate_snapshot": (
            "تم حفظ لقطة بالدرجة نفسها بالفعل خلال الدقائق الخمس الماضية."
        ),
        "snapshot_saved": ("تم حفظ اللقطة في PostgreSQL/Neon."),
        "load_error": ("تعذر تحميل السجل."),
        "empty_history": ("لم يتم العثور على لقطات للفترة المحددة."),
        "minimum_snapshots": ("يجب حفظ لقطتين على الأقل لحساب الاتجاه."),
        "trend_improving": ("تحسنت درجة Health Score خلال الفترة."),
        "trend_worsening": ("انخفضت درجة Health Score خلال الفترة."),
        "trend_stable": ("ظلت درجة Health Score مستقرة خلال الفترة."),
        "score_hover": "الدرجة",
        "component_score": "درجة المكوّن",
        "component": "المكوّن",
    },
}

HEALTH_HISTORY_DYNAMIC_TEXTS["ch"] = dict(HEALTH_HISTORY_DYNAMIC_TEXTS["de"])


def health_history_dynamic_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz mensagens e gráficos do histórico."""
    idioma = health_table_lang()

    return HEALTH_HISTORY_DYNAMIC_TEXTS.get(
        idioma,
        HEALTH_HISTORY_DYNAMIC_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def traduzir_tendencia_historico_health(
    tendencia: dict[str, Any],
) -> str:
    """Localiza a tendência sem modificar o resultado interno."""
    direcao = (
        str(
            tendencia.get(
                "direcao",
                "",
            )
        )
        .strip()
        .lower()
    )

    if direcao == "melhora":
        return health_history_dynamic_t("trend_improving")

    if direcao == "piora":
        return health_history_dynamic_t("trend_worsening")

    return health_history_dynamic_t("trend_stable")


# HEALTH_SCORE_RUNTIME_MESSAGES_I18N

HEALTH_RUNTIME_MESSAGE_TEXTS = {
    "pt": {
        "success_rate": "Taxa de sucesso",
        "router_confidence": "Confiança do Router",
        "events_without_tool": "Eventos sem Tool",
        "anomalies": "Anomalias",
        "no_active_document": "Nenhum documento ativo",
        "documents_without_embeddings": ("Documentos sem embeddings"),
        "no_embedding": "Nenhum embedding disponível",
        "inactive_embeddings": "Embeddings inativos",
        "memory_table_unavailable": ("Tabela de memória indisponível"),
        "no_memory": "Nenhuma memória registrada",
        "memory_errors": "Erros de memória",
        "no_trace": "Nenhum trace analisado",
        "failed_traces": "Traces com falha",
        "cold_starts": "Cold starts",
        "high_tools_p95": "P95 Tools elevado",
        "high_trace_p95": "P95 dos traces elevado",
        "prioritise_component": (
            "Priorizar melhorias no componente "
            "{component}, atualmente com score "
            "{score}/100."
        ),
        "all_healthy": (
            "Todos os componentes estão em nível saudável. "
            "Continue monitorando P95, falhas e cold starts."
        ),
    },
    "en_us": {
        "success_rate": "Success rate",
        "router_confidence": "Router confidence",
        "events_without_tool": "Events without a tool",
        "anomalies": "Anomalies",
        "no_active_document": "No active document",
        "documents_without_embeddings": ("Documents without embeddings"),
        "no_embedding": "No embedding available",
        "inactive_embeddings": "Inactive embeddings",
        "memory_table_unavailable": ("Memory table unavailable"),
        "no_memory": "No memory registered",
        "memory_errors": "Memory errors",
        "no_trace": "No trace analysed",
        "failed_traces": "Failed traces",
        "cold_starts": "Cold starts",
        "high_tools_p95": "High Tools P95",
        "high_trace_p95": "High trace P95",
        "prioritise_component": (
            "Prioritise improvements to the {component} "
            "component, currently scoring {score}/100."
        ),
        "all_healthy": (
            "All components are at a healthy level. "
            "Continue monitoring P95, failures and cold starts."
        ),
    },
    "en_gb": {
        "success_rate": "Success rate",
        "router_confidence": "Router confidence",
        "events_without_tool": "Events without a tool",
        "anomalies": "Anomalies",
        "no_active_document": "No active document",
        "documents_without_embeddings": ("Documents without embeddings"),
        "no_embedding": "No embedding available",
        "inactive_embeddings": "Inactive embeddings",
        "memory_table_unavailable": ("Memory table unavailable"),
        "no_memory": "No memory registered",
        "memory_errors": "Memory errors",
        "no_trace": "No trace analysed",
        "failed_traces": "Failed traces",
        "cold_starts": "Cold starts",
        "high_tools_p95": "High Tools P95",
        "high_trace_p95": "High trace P95",
        "prioritise_component": (
            "Prioritise improvements to the {component} "
            "component, currently scoring {score}/100."
        ),
        "all_healthy": (
            "All components are at a healthy level. "
            "Continue monitoring P95, failures and cold starts."
        ),
    },
    "es": {
        "success_rate": "Tasa de éxito",
        "router_confidence": "Confianza del Router",
        "events_without_tool": "Eventos sin herramienta",
        "anomalies": "Anomalías",
        "no_active_document": "Ningún documento activo",
        "documents_without_embeddings": ("Documentos sin embeddings"),
        "no_embedding": "Ningún embedding disponible",
        "inactive_embeddings": "Embeddings inactivos",
        "memory_table_unavailable": ("Tabla de memoria no disponible"),
        "no_memory": "Ninguna memoria registrada",
        "memory_errors": "Errores de memoria",
        "no_trace": "Ninguna traza analizada",
        "failed_traces": "Trazas con errores",
        "cold_starts": "Arranques en frío",
        "high_tools_p95": "P95 de herramientas elevado",
        "high_trace_p95": "P95 de trazas elevado",
        "prioritise_component": (
            "Priorice las mejoras del componente {component}, "
            "actualmente con una puntuación de {score}/100."
        ),
        "all_healthy": (
            "Todos los componentes están en un nivel saludable. "
            "Continúe supervisando P95, errores y arranques en frío."
        ),
    },
    "fr": {
        "success_rate": "Taux de réussite",
        "router_confidence": "Confiance du Router",
        "events_without_tool": "Événements sans outil",
        "anomalies": "Anomalies",
        "no_active_document": "Aucun document actif",
        "documents_without_embeddings": ("Documents sans embeddings"),
        "no_embedding": "Aucun embedding disponible",
        "inactive_embeddings": "Embeddings inactifs",
        "memory_table_unavailable": ("Table de mémoire indisponible"),
        "no_memory": "Aucune mémoire enregistrée",
        "memory_errors": "Erreurs de mémoire",
        "no_trace": "Aucune trace analysée",
        "failed_traces": "Traces en échec",
        "cold_starts": "Démarrages à froid",
        "high_tools_p95": "P95 des outils élevé",
        "high_trace_p95": "P95 des traces élevé",
        "prioritise_component": (
            "Priorisez les améliorations du composant "
            "{component}, actuellement à {score}/100."
        ),
        "all_healthy": (
            "Tous les composants sont à un niveau sain. "
            "Continuez à surveiller le P95, les échecs "
            "et les démarrages à froid."
        ),
    },
    "de": {
        "success_rate": "Erfolgsrate",
        "router_confidence": "Router-Vertrauen",
        "events_without_tool": "Ereignisse ohne Tool",
        "anomalies": "Anomalien",
        "no_active_document": "Kein aktives Dokument",
        "documents_without_embeddings": ("Dokumente ohne Embeddings"),
        "no_embedding": "Kein Embedding verfügbar",
        "inactive_embeddings": "Inaktive Embeddings",
        "memory_table_unavailable": ("Speichertabelle nicht verfügbar"),
        "no_memory": "Kein Speicher registriert",
        "memory_errors": "Speicherfehler",
        "no_trace": "Kein Trace analysiert",
        "failed_traces": "Fehlgeschlagene Traces",
        "cold_starts": "Cold Starts",
        "high_tools_p95": "Erhöhter Tools-P95",
        "high_trace_p95": "Erhöhter Trace-P95",
        "prioritise_component": (
            "Priorisieren Sie Verbesserungen der Komponente "
            "{component}, derzeit mit {score}/100."
        ),
        "all_healthy": (
            "Alle Komponenten befinden sich auf einem "
            "gesunden Niveau. Überwachen Sie weiterhin "
            "P95, Fehler und Cold Starts."
        ),
    },
    "it": {
        "success_rate": "Tasso di successo",
        "router_confidence": "Affidabilità del Router",
        "events_without_tool": "Eventi senza strumento",
        "anomalies": "Anomalie",
        "no_active_document": "Nessun documento attivo",
        "documents_without_embeddings": ("Documenti senza embeddings"),
        "no_embedding": "Nessun embedding disponibile",
        "inactive_embeddings": "Embeddings inattivi",
        "memory_table_unavailable": ("Tabella di memoria non disponibile"),
        "no_memory": "Nessuna memoria registrata",
        "memory_errors": "Errori di memoria",
        "no_trace": "Nessuna traccia analizzata",
        "failed_traces": "Tracce con errori",
        "cold_starts": "Avvii a freddo",
        "high_tools_p95": "P95 degli strumenti elevato",
        "high_trace_p95": "P95 delle tracce elevato",
        "prioritise_component": (
            "Dare priorità ai miglioramenti del componente "
            "{component}, attualmente con punteggio {score}/100."
        ),
        "all_healthy": (
            "Tutti i componenti sono a un livello sano. "
            "Continuare a monitorare P95, errori e avvii a freddo."
        ),
    },
    "ro": {
        "success_rate": "Rata de succes",
        "router_confidence": "Încrederea Router-ului",
        "events_without_tool": "Evenimente fără instrument",
        "anomalies": "Anomalii",
        "no_active_document": "Niciun document activ",
        "documents_without_embeddings": ("Documente fără embeddings"),
        "no_embedding": "Niciun embedding disponibil",
        "inactive_embeddings": "Embeddings inactive",
        "memory_table_unavailable": ("Tabelul de memorie este indisponibil"),
        "no_memory": "Nicio memorie înregistrată",
        "memory_errors": "Erori de memorie",
        "no_trace": "Niciun trace analizat",
        "failed_traces": "Trace-uri cu erori",
        "cold_starts": "Porniri la rece",
        "high_tools_p95": "P95 ridicat pentru instrumente",
        "high_trace_p95": "P95 ridicat pentru trace-uri",
        "prioritise_component": (
            "Prioritizați îmbunătățirile componentei "
            "{component}, care are în prezent scorul {score}/100."
        ),
        "all_healthy": (
            "Toate componentele se află la un nivel sănătos. "
            "Continuați monitorizarea P95, erorilor "
            "și pornirilor la rece."
        ),
    },
    "ua": {
        "success_rate": "Рівень успішності",
        "router_confidence": "Надійність Router",
        "events_without_tool": "Події без інструмента",
        "anomalies": "Аномалії",
        "no_active_document": "Немає активних документів",
        "documents_without_embeddings": ("Документи без embeddings"),
        "no_embedding": "Немає доступних embeddings",
        "inactive_embeddings": "Неактивні embeddings",
        "memory_table_unavailable": ("Таблиця пам’яті недоступна"),
        "no_memory": "Пам’ять не зареєстрована",
        "memory_errors": "Помилки пам’яті",
        "no_trace": "Не проаналізовано жодного trace",
        "failed_traces": "Trace з помилками",
        "cold_starts": "Холодні запуски",
        "high_tools_p95": "Високий P95 інструментів",
        "high_trace_p95": "Високий P95 trace",
        "prioritise_component": (
            "Надайте пріоритет покращенню компонента "
            "{component}, поточна оцінка — {score}/100."
        ),
        "all_healthy": (
            "Усі компоненти перебувають у здоровому стані. "
            "Продовжуйте контролювати P95, помилки "
            "та холодні запуски."
        ),
    },
    "ru": {
        "success_rate": "Доля успешных выполнений",
        "router_confidence": "Надёжность Router",
        "events_without_tool": "События без инструмента",
        "anomalies": "Аномалии",
        "no_active_document": "Нет активных документов",
        "documents_without_embeddings": ("Документы без embeddings"),
        "no_embedding": "Нет доступных embeddings",
        "inactive_embeddings": "Неактивные embeddings",
        "memory_table_unavailable": ("Таблица памяти недоступна"),
        "no_memory": "Память не зарегистрирована",
        "memory_errors": "Ошибки памяти",
        "no_trace": "Не проанализировано ни одного trace",
        "failed_traces": "Trace с ошибками",
        "cold_starts": "Холодные запуски",
        "high_tools_p95": "Высокий P95 инструментов",
        "high_trace_p95": "Высокий P95 trace",
        "prioritise_component": (
            "Приоритетно улучшите компонент {component}, текущая оценка — {score}/100."
        ),
        "all_healthy": (
            "Все компоненты находятся в нормальном состоянии. "
            "Продолжайте контролировать P95, ошибки "
            "и холодные запуски."
        ),
    },
    "sa": {
        "success_rate": "معدل النجاح",
        "router_confidence": "موثوقية Router",
        "events_without_tool": "أحداث دون أداة",
        "anomalies": "الحالات الشاذة",
        "no_active_document": "لا توجد مستندات نشطة",
        "documents_without_embeddings": ("مستندات دون embeddings"),
        "no_embedding": "لا تتوفر embeddings",
        "inactive_embeddings": "Embeddings غير نشطة",
        "memory_table_unavailable": ("جدول الذاكرة غير متاح"),
        "no_memory": "لا توجد ذاكرة مسجلة",
        "memory_errors": "أخطاء الذاكرة",
        "no_trace": "لم يتم تحليل أي trace",
        "failed_traces": "Trace تحتوي على أخطاء",
        "cold_starts": "عمليات التشغيل البارد",
        "high_tools_p95": "ارتفاع P95 للأدوات",
        "high_trace_p95": "ارتفاع P95 للتتبعات",
        "prioritise_component": (
            "أعطِ الأولوية لتحسين المكوّن {component}، ودرجة حالته الحالية {score}/100."
        ),
        "all_healthy": (
            "جميع المكوّنات في حالة سليمة. استمر في مراقبة "
            "P95 والأخطاء وعمليات التشغيل البارد."
        ),
    },
}

HEALTH_RUNTIME_MESSAGE_TEXTS["ch"] = dict(HEALTH_RUNTIME_MESSAGE_TEXTS["de"])


def health_runtime_message_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz mensagens produzidas pelo runtime."""
    idioma = health_table_lang()

    return HEALTH_RUNTIME_MESSAGE_TEXTS.get(
        idioma,
        HEALTH_RUNTIME_MESSAGE_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


HEALTH_PENALTY_PREFIXES = {
    "Taxa de sucesso": "success_rate",
    "Confiança do Router": "router_confidence",
    "Eventos sem Tool": "events_without_tool",
    "Anomalias": "anomalies",
    "Nenhum documento ativo": "no_active_document",
    "Documentos sem embeddings": ("documents_without_embeddings"),
    "Nenhum embedding disponível": "no_embedding",
    "Embeddings inativos": "inactive_embeddings",
    "Tabela de memória indisponível": ("memory_table_unavailable"),
    "Nenhuma memória registrada": "no_memory",
    "Erros de memória": "memory_errors",
    "Nenhum trace analisado": "no_trace",
    "Traces com falha": "failed_traces",
    "Cold starts": "cold_starts",
    "P95 Tools elevado": "high_tools_p95",
    "P95 dos traces elevado": "high_trace_p95",
}


def traduzir_penalidade_health(
    penalidade: Any,
) -> str:
    """Traduz o rótulo e preserva o valor da penalidade."""
    texto = str(penalidade or "").strip()

    for prefixo, chave in HEALTH_PENALTY_PREFIXES.items():
        if texto == prefixo:
            return health_runtime_message_t(
                chave,
                texto,
            )

        marcador = f"{prefixo}:"

        if texto.startswith(marcador):
            restante = texto[len(prefixo) :]

            return f"{health_runtime_message_t(chave, prefixo)}{restante}"

    return texto


def traduzir_recomendacao_health(
    recomendacao: Any,
) -> str:
    """Traduz recomendações conhecidas do Health Score."""
    texto = str(recomendacao or "").strip()

    if texto.startswith("Priorizar melhorias no componente "):
        prefixo = "Priorizar melhorias no componente "
        marcador_score = ", atualmente com score "

        restante = texto[len(prefixo) :]

        if marcador_score in restante:
            componente, score = restante.split(
                marcador_score,
                1,
            )

            score = score.removesuffix("/100.")

            return health_runtime_message_t("prioritise_component").format(
                component=nome_componente_health(
                    componente,
                    componente,
                ),
                score=score,
            )

    if texto.startswith("Todos os componentes estão em nível saudável."):
        return health_runtime_message_t("all_healthy")

    return texto


# Ajustes finais dos textos visíveis do Health Score.
HEALTH_HISTORY_TEXTS["pt"].update(
    {
        "snapshots": "Registros históricos",
    }
)

HEALTH_HISTORY_TEXTS["es"].update(
    {
        "snapshots": "Registros históricos",
    }
)

HEALTH_HISTORY_TEXTS["fr"].update(
    {
        "snapshots": "Instantanés historiques",
    }
)

HEALTH_HISTORY_TEXTS["de"].update(
    {
        "snapshots": "Historische Momentaufnahmen",
    }
)

HEALTH_RUNTIME_MESSAGE_TEXTS["pt"].update(
    {
        "cold_starts": "Inicializações a frio",
    }
)

# O código ch segue os catálogos alemães do projeto.
HEALTH_HISTORY_TEXTS["ch"] = dict(HEALTH_HISTORY_TEXTS["de"])

HEALTH_RUNTIME_MESSAGE_TEXTS["ch"] = dict(HEALTH_RUNTIME_MESSAGE_TEXTS["de"])


def health_page_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz o cabeçalho do Health Center."""
    idioma = health_table_lang()

    return HEALTH_PAGE_TEXTS.get(
        idioma,
        HEALTH_PAGE_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def render_health_score_page() -> None:
    """
    Renderiza o Health Center.
    """
    try:
        from observability.health_runtime import (
            coletar_health_score_real,
        )
    except ImportError:
        from src.observability.health_runtime import (
            coletar_health_score_real,
        )

    st.title(health_page_t("title"))

    st.caption(health_page_t("caption"))

    controle_1, controle_2, controle_3 = st.columns([1, 1, 2])

    limite_eventos = controle_1.selectbox(
        health_page_t("tools_events"),
        options=[
            100,
            250,
            500,
            1000,
        ],
        index=1,
        key="health_tools_limit",
    )

    limite_traces = controle_2.selectbox(
        health_page_t("analysed_traces"),
        options=[
            10,
            25,
            50,
            100,
        ],
        index=2,
        key="health_traces_limit",
    )

    with controle_3:
        st.write("")

        if st.button(
            health_page_t("refresh"),
            use_container_width=True,
            key="health_refresh",
        ):
            st.rerun()

    resultado = coletar_health_score_real(
        limite_eventos_tools=int(limite_eventos),
        limite_traces=int(limite_traces),
    )

    health = resultado.get("health", {})

    score_global = float(
        health.get(
            "score_global",
            0,
        )
    )

    classificacao = health.get(
        "classificacao",
        health_page_t("no_data"),
    )

    st.markdown(health_page_t("global_health"))

    col_1, col_2, col_3, col_4 = st.columns(4)

    col_1.metric(
        health_page_t("health_score"),
        f"{score_global:.1f}/100",
    )

    col_2.metric(
        health_page_t("classification"),
        traduzir_classificacao_health(classificacao),
    )

    col_3.metric(
        health_page_t("strongest_component"),
        nome_componente_health(
            health.get(
                "componente_mais_forte",
                "",
            ),
            health.get(
                "componente_mais_forte",
                "—",
            ),
        ),
    )

    col_4.metric(
        health_page_t("priority_component"),
        nome_componente_health(
            health.get(
                "componente_mais_fraco",
                "",
            ),
            health.get(
                "componente_mais_fraco",
                "—",
            ),
        ),
    )

    st.progress(
        max(
            0.0,
            min(
                score_global / 100,
                1.0,
            ),
        )
    )

    if score_global >= 95:
        st.success("A INNA está operando em excelente estado.")

    elif score_global >= 85:
        st.info("A INNA está saudável, com alguns pontos que merecem acompanhamento.")

    elif score_global >= 70:
        st.warning(health_page_t("attention_message"))

    else:
        st.error(health_page_t("critical_message"))

    componentes = health.get(
        "componentes",
        {},
    )

    st.divider()
    st.markdown(health_page_t("component_scores"))

    colunas = st.columns(3)

    for indice, (
        nome,
        item,
    ) in enumerate(componentes.items()):
        coluna = colunas[indice % 3]

        with coluna:
            with st.container(border=True):
                st.markdown(
                    f"### {item.get('icone', '')} {nome_componente_health(nome, nome)}"
                )

                st.metric(
                    health_page_t("score"),
                    f"{float(item.get('score', 0)):.1f}/100",
                )

                st.progress(
                    max(
                        0.0,
                        min(
                            float(
                                item.get(
                                    "score",
                                    0,
                                )
                            )
                            / 100,
                            1.0,
                        ),
                    )
                )

                st.caption(
                    f"{health_page_t('global_weight')}: "
                    f"{float(item.get('peso', 0)) * 100:.1f}%"
                )

                penalidades = item.get(
                    "penalidades",
                    [],
                )

                if penalidades:
                    with st.expander(
                        health_page_t("view_penalties"),
                        expanded=False,
                    ):
                        for penalidade in penalidades:
                            st.markdown("- " + traduzir_penalidade_health(penalidade))
                else:
                    st.success(health_page_t("no_penalty"))

    tabela = preparar_componentes_exibicao(componentes)

    st.markdown(health_table_t("component_comparison"))

    tabela_exibicao = tabela.rename(
        columns={
            "Componente": health_table_t("component"),
            "Score": health_table_t("score"),
            "Peso (%)": health_table_t("weight"),
            "Contribuição": health_table_t("contribution"),
            "Classificação": health_table_t("classification"),
            "Status": health_table_t("status"),
        }
    )

    st.dataframe(
        estilizar_tabela_componentes_health(tabela_exibicao),
        use_container_width=True,
        hide_index=True,
        height=300,
        column_config={
            health_table_t("component"): (
                st.column_config.TextColumn(
                    health_table_t("component"),
                    width="medium",
                )
            ),
            health_table_t("score"): (
                st.column_config.ProgressColumn(
                    health_table_t("score"),
                    min_value=0.0,
                    max_value=100.0,
                    format="%.1f",
                    width="medium",
                )
            ),
            health_table_t("weight"): (
                st.column_config.NumberColumn(
                    health_table_t("weight"),
                    format="%.1f%%",
                    width="small",
                )
            ),
            health_table_t("contribution"): (
                st.column_config.NumberColumn(
                    health_table_t("contribution"),
                    format="%.2f",
                    width="small",
                )
            ),
            health_table_t("classification"): (
                st.column_config.TextColumn(
                    health_table_t("classification"),
                    width="medium",
                )
            ),
            health_table_t("status"): (
                st.column_config.TextColumn(
                    health_table_t("status"),
                    width="medium",
                )
            ),
        },
    )

    if not tabela.empty:
        tabela_grafico = tabela.sort_values(
            "Score",
            ascending=True,
        ).copy()

        fig_comparativo = px.bar(
            tabela_grafico,
            x="Score",
            y="Componente",
            orientation="h",
            text="Score",
            color="Score",
            range_x=[0, 100],
            labels={
                "Score": health_page_t("score"),
                "Componente": health_page_t("component"),
            },
            color_continuous_scale=[
                "#F87171",
                "#F59E0B",
                "#34D399",
            ],
        )

        fig_comparativo.update_traces(
            texttemplate="%{x:.1f}",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{health_page_t('score')}: "
                "%{x:.1f}/100"
                "<extra></extra>"
            ),
        )

        fig_comparativo.update_layout(
            xaxis_title=health_page_t("score"),
            yaxis_title=None,
            coloraxis_showscale=False,
            showlegend=False,
        )

        fig_comparativo.update_xaxes(
            range=[0, 100],
        )

        aplicar_tema_health_chart(
            fig_comparativo,
            height=430,
        )

        st.plotly_chart(
            fig_comparativo,
            width="stretch",
            key="health_components_comparison_chart",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    st.divider()
    st.markdown("## " + health_page_t("priority_recommendations"))

    for recomendacao in health.get(
        "recomendacoes",
        [],
    ):
        st.info(traduzir_recomendacao_health(recomendacao))

    render_health_history_section(resultado_atual=resultado)

    metricas = resultado.get(
        "metricas",
        {},
    )

    with st.expander(
        "📋 Métricas técnicas utilizadas",
        expanded=False,
    ):
        st.json(metricas)

    erros = resultado.get(
        "erros_coleta",
        [],
    )

    if erros:
        with st.expander(
            "⚠️ Alertas durante a coleta",
            expanded=False,
        ):
            for erro in erros:
                st.warning(erro)


__all__ = [
    "render_health_history_section",
    "preparar_historico_exibicao",
    "NOMES_COMPONENTES",
    "preparar_componentes_exibicao",
    "render_health_score_page",
]

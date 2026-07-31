"""
LLM Cost Center da INNA.

Painel de tokens, custos estimados, desempenho e auditoria
das chamadas realizadas aos modelos de linguagem.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

LLM_COST_CHART_BG = "#020617"
LLM_COST_CHART_TEXT = "#F8FAFC"
LLM_COST_CHART_GRID = (
    "rgba(148, 163, 184, 0.16)"
)


LLM_TABLE_TEXTS = {
    "pt": {
        "model": "Modelo",
        "calls": "Chamadas",
        "tokens": "Tokens",
        "cost_usd": "Custo (USD)",
        "avg_duration": "Duração média (s)",
        "model_help": "Modelo de linguagem utilizado.",
        "calls_help": "Quantidade de chamadas realizadas.",
        "tokens_help": (
            "Total de tokens consumidos pelo modelo."
        ),
        "cost_help": "Custo estimado em dólares.",
        "duration_help": (
            "Tempo médio das chamadas em segundos."
        ),
        "operation": "Operação",
        "operation_help": (
            "Tipo de operação executada pelo modelo."
        ),
    },
    "en_us": {
        "model": "Model",
        "calls": "Calls",
        "tokens": "Tokens",
        "cost_usd": "Cost (USD)",
        "avg_duration": "Average duration (s)",
        "model_help": "Language model used.",
        "calls_help": "Number of calls performed.",
        "tokens_help": (
            "Total tokens consumed by the model."
        ),
        "cost_help": "Estimated cost in US dollars.",
        "duration_help": (
            "Average call duration in seconds."
        ),
        "operation": "Operation",
        "operation_help": (
            "Type of operation executed by the model."
        ),
    },
    "es": {
        "model": "Modelo",
        "calls": "Llamadas",
        "tokens": "Tokens",
        "cost_usd": "Costo (USD)",
        "avg_duration": "Duración media (s)",
        "model_help": "Modelo de lenguaje utilizado.",
        "calls_help": "Cantidad de llamadas realizadas.",
        "tokens_help": (
            "Total de tokens consumidos por el modelo."
        ),
        "cost_help": "Costo estimado en dólares.",
        "duration_help": (
            "Duración media de las llamadas en segundos."
        ),
        "operation": "Operación",
        "operation_help": (
            "Tipo de operación ejecutada por el modelo."
        ),
    },
    "fr": {
        "model": "Modèle",
        "calls": "Appels",
        "tokens": "Jetons",
        "cost_usd": "Coût (USD)",
        "avg_duration": "Durée moyenne (s)",
        "model_help": "Modèle de langage utilisé.",
        "calls_help": "Nombre d'appels effectués.",
        "tokens_help": (
            "Nombre total de jetons consommés."
        ),
        "cost_help": "Coût estimé en dollars.",
        "duration_help": (
            "Durée moyenne des appels en secondes."
        ),
        "operation": "Opération",
        "operation_help": (
            "Type d’opération exécutée par le modèle."
        ),
    },
    "de": {
        "model": "Modell",
        "calls": "Aufrufe",
        "tokens": "Token",
        "cost_usd": "Kosten (USD)",
        "avg_duration": "Durchschnittsdauer (s)",
        "model_help": "Verwendetes Sprachmodell.",
        "calls_help": "Anzahl der ausgeführten Aufrufe.",
        "tokens_help": (
            "Gesamtzahl der verbrauchten Token."
        ),
        "cost_help": "Geschätzte Kosten in US-Dollar.",
        "duration_help": (
            "Durchschnittliche Dauer in Sekunden."
        ),
        "operation": "Operation",
        "operation_help": (
            "Vom Modell ausgeführter Vorgangstyp."
        ),
    },
    "it": {
        "model": "Modello",
        "calls": "Chiamate",
        "tokens": "Token",
        "cost_usd": "Costo (USD)",
        "avg_duration": "Durata media (s)",
        "model_help": "Modello linguistico utilizzato.",
        "calls_help": "Numero di chiamate effettuate.",
        "tokens_help": (
            "Totale dei token consumati dal modello."
        ),
        "cost_help": "Costo stimato in dollari.",
        "duration_help": (
            "Durata media delle chiamate in secondi."
        ),
        "operation": "Operazione",
        "operation_help": (
            "Tipo di operazione eseguita dal modello."
        ),
    },
    "ro": {
        "model": "Model",
        "calls": "Apeluri",
        "tokens": "Tokenuri",
        "cost_usd": "Cost (USD)",
        "avg_duration": "Durată medie (s)",
        "model_help": "Modelul lingvistic utilizat.",
        "calls_help": "Numărul de apeluri efectuate.",
        "tokens_help": (
            "Totalul tokenurilor consumate."
        ),
        "cost_help": "Cost estimat în dolari.",
        "duration_help": (
            "Durata medie a apelurilor în secunde."
        ),
        "operation": "Operațiune",
        "operation_help": (
            "Tipul operațiunii executate de model."
        ),
    },
    "ua": {
        "model": "Модель",
        "calls": "Виклики",
        "tokens": "Токени",
        "cost_usd": "Вартість (USD)",
        "avg_duration": "Середня тривалість (с)",
        "model_help": "Використана мовна модель.",
        "calls_help": "Кількість виконаних викликів.",
        "tokens_help": (
            "Загальна кількість використаних токенів."
        ),
        "cost_help": "Орієнтовна вартість у доларах.",
        "duration_help": (
            "Середня тривалість викликів у секундах."
        ),
        "operation": "Операція",
        "operation_help": (
            "Тип операції, виконаної моделлю."
        ),
    },
    "ru": {
        "model": "Модель",
        "calls": "Вызовы",
        "tokens": "Токены",
        "cost_usd": "Стоимость (USD)",
        "avg_duration": "Средняя длительность (с)",
        "model_help": "Используемая языковая модель.",
        "calls_help": "Количество выполненных вызовов.",
        "tokens_help": (
            "Общее количество использованных токенов."
        ),
        "cost_help": "Расчетная стоимость в долларах.",
        "duration_help": (
            "Средняя длительность вызовов в секундах."
        ),
        "operation": "Операция",
        "operation_help": (
            "Тип операции, выполненной моделью."
        ),
    },
    "sa": {
        "model": "النموذج",
        "calls": "الاستدعاءات",
        "tokens": "الرموز",
        "cost_usd": "التكلفة (USD)",
        "avg_duration": "متوسط المدة (ث)",
        "model_help": "نموذج اللغة المستخدم.",
        "calls_help": "عدد الاستدعاءات المنفذة.",
        "tokens_help": (
            "إجمالي الرموز التي استهلكها النموذج."
        ),
        "cost_help": "التكلفة التقديرية بالدولار.",
        "duration_help": (
            "متوسط مدة الاستدعاءات بالثواني."
        ),
        "operation": "العملية",
        "operation_help": (
            "نوع العملية التي نفذها النموذج."
        ),
    },
}

LLM_TABLE_TEXTS["en_gb"] = LLM_TABLE_TEXTS["en_us"]
LLM_TABLE_TEXTS["ch"] = LLM_TABLE_TEXTS["de"]


def llm_table_lang() -> str:
    """Retorna o idioma atual do dashboard."""
    idioma = st.session_state.get(
        "dashboard_interface_lang",
        "pt",
    )

    if idioma in LLM_TABLE_TEXTS:
        return idioma

    return "pt"


def llm_table_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz textos das tabelas do Cost Center."""
    idioma = llm_table_lang()

    return LLM_TABLE_TEXTS.get(
        idioma,
        LLM_TABLE_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


LLM_DETAIL_TEXTS = {
    "pt": {
        "date": "Data",
        "provider": "Provedor",
        "origin": "Origem",
        "user": "Usuário",
        "trace": "Trace",
        "input_tokens": "Tokens de entrada",
        "output_tokens": "Tokens de saída",
        "total_tokens": "Tokens totais",
        "estimated_cost": "Custo estimado (USD)",
        "duration": "Duração (s)",
        "result": "Resultado",
        "error_type": "Tipo do erro",
        "success": "✅ Sucesso",
        "failure": "❌ Falha",
        "no_data": "⚪ Sem dados",
        "provider_help": (
            "Provedor responsável pela execução "
            "do modelo."
        ),
        "trace_help": (
            "Identificador técnico da execução "
            "observada."
        ),
    },
    "en_us": {
        "date": "Date",
        "provider": "Provider",
        "origin": "Origin",
        "user": "User",
        "trace": "Trace",
        "input_tokens": "Input tokens",
        "output_tokens": "Output tokens",
        "total_tokens": "Total tokens",
        "estimated_cost": "Estimated cost (USD)",
        "duration": "Duration (s)",
        "result": "Result",
        "error_type": "Error type",
        "success": "✅ Success",
        "failure": "❌ Failure",
        "no_data": "⚪ No data",
        "provider_help": (
            "Provider responsible for executing "
            "the model."
        ),
        "trace_help": (
            "Technical identifier of the observed "
            "execution."
        ),
    },
    "es": {
        "date": "Fecha",
        "provider": "Proveedor",
        "origin": "Origen",
        "user": "Usuario",
        "trace": "Traza",
        "input_tokens": "Tokens de entrada",
        "output_tokens": "Tokens de salida",
        "total_tokens": "Tokens totales",
        "estimated_cost": "Costo estimado (USD)",
        "duration": "Duración (s)",
        "result": "Resultado",
        "error_type": "Tipo de error",
        "success": "✅ Éxito",
        "failure": "❌ Fallo",
        "no_data": "⚪ Sin datos",
        "provider_help": (
            "Proveedor responsable de ejecutar "
            "el modelo."
        ),
        "trace_help": (
            "Identificador técnico de la ejecución."
        ),
    },
    "fr": {
        "date": "Date",
        "provider": "Fournisseur",
        "origin": "Origine",
        "user": "Utilisateur",
        "trace": "Trace",
        "input_tokens": "Jetons d'entrée",
        "output_tokens": "Jetons de sortie",
        "total_tokens": "Jetons totaux",
        "estimated_cost": "Coût estimé (USD)",
        "duration": "Durée (s)",
        "result": "Résultat",
        "error_type": "Type d'erreur",
        "success": "✅ Succès",
        "failure": "❌ Échec",
        "no_data": "⚪ Aucune donnée",
        "provider_help": (
            "Fournisseur responsable de "
            "l'exécution du modèle."
        ),
        "trace_help": (
            "Identifiant technique de l'exécution."
        ),
    },
    "de": {
        "date": "Datum",
        "provider": "Anbieter",
        "origin": "Quelle",
        "user": "Benutzer",
        "trace": "Trace",
        "input_tokens": "Eingabe-Token",
        "output_tokens": "Ausgabe-Token",
        "total_tokens": "Token gesamt",
        "estimated_cost": "Geschätzte Kosten (USD)",
        "duration": "Dauer (s)",
        "result": "Ergebnis",
        "error_type": "Fehlertyp",
        "success": "✅ Erfolgreich",
        "failure": "❌ Fehlgeschlagen",
        "no_data": "⚪ Keine Daten",
        "provider_help": (
            "Anbieter, der das Modell ausführt."
        ),
        "trace_help": (
            "Technische Kennung der Ausführung."
        ),
    },
    "it": {
        "date": "Data",
        "provider": "Provider",
        "origin": "Origine",
        "user": "Utente",
        "trace": "Trace",
        "input_tokens": "Token di input",
        "output_tokens": "Token di output",
        "total_tokens": "Token totali",
        "estimated_cost": "Costo stimato (USD)",
        "duration": "Durata (s)",
        "result": "Risultato",
        "error_type": "Tipo di errore",
        "success": "✅ Successo",
        "failure": "❌ Errore",
        "no_data": "⚪ Nessun dato",
        "provider_help": (
            "Provider responsabile "
            "dell'esecuzione del modello."
        ),
        "trace_help": (
            "Identificatore tecnico "
            "dell'esecuzione."
        ),
    },
    "ro": {
        "date": "Data",
        "provider": "Furnizor",
        "origin": "Origine",
        "user": "Utilizator",
        "trace": "Trasare",
        "input_tokens": "Tokenuri de intrare",
        "output_tokens": "Tokenuri de ieșire",
        "total_tokens": "Total tokenuri",
        "estimated_cost": "Cost estimat (USD)",
        "duration": "Durată (s)",
        "result": "Rezultat",
        "error_type": "Tipul erorii",
        "success": "✅ Succes",
        "failure": "❌ Eșec",
        "no_data": "⚪ Fără date",
        "provider_help": (
            "Furnizorul responsabil pentru "
            "execuția modelului."
        ),
        "trace_help": (
            "Identificatorul tehnic al execuției."
        ),
    },
    "ua": {
        "date": "Дата",
        "provider": "Провайдер",
        "origin": "Джерело",
        "user": "Користувач",
        "trace": "Трасування",
        "input_tokens": "Вхідні токени",
        "output_tokens": "Вихідні токени",
        "total_tokens": "Усього токенів",
        "estimated_cost": "Орієнтовна вартість (USD)",
        "duration": "Тривалість (с)",
        "result": "Результат",
        "error_type": "Тип помилки",
        "success": "✅ Успішно",
        "failure": "❌ Помилка",
        "no_data": "⚪ Немає даних",
        "provider_help": (
            "Провайдер, відповідальний "
            "за виконання моделі."
        ),
        "trace_help": (
            "Технічний ідентифікатор виконання."
        ),
    },
    "ru": {
        "date": "Дата",
        "provider": "Провайдер",
        "origin": "Источник",
        "user": "Пользователь",
        "trace": "Трассировка",
        "input_tokens": "Входные токены",
        "output_tokens": "Выходные токены",
        "total_tokens": "Всего токенов",
        "estimated_cost": "Расчетная стоимость (USD)",
        "duration": "Длительность (с)",
        "result": "Результат",
        "error_type": "Тип ошибки",
        "success": "✅ Успешно",
        "failure": "❌ Ошибка",
        "no_data": "⚪ Нет данных",
        "provider_help": (
            "Провайдер, отвечающий "
            "за выполнение модели."
        ),
        "trace_help": (
            "Технический идентификатор выполнения."
        ),
    },
    "sa": {
        "date": "التاريخ",
        "provider": "المزود",
        "origin": "المصدر",
        "user": "المستخدم",
        "trace": "التتبع",
        "input_tokens": "رموز الإدخال",
        "output_tokens": "رموز الإخراج",
        "total_tokens": "إجمالي الرموز",
        "estimated_cost": "التكلفة التقديرية (USD)",
        "duration": "المدة (ث)",
        "result": "النتيجة",
        "error_type": "نوع الخطأ",
        "success": "✅ ناجح",
        "failure": "❌ فشل",
        "no_data": "⚪ لا توجد بيانات",
        "provider_help": (
            "المزود المسؤول عن تنفيذ النموذج."
        ),
        "trace_help": (
            "المعرف التقني لعملية التنفيذ."
        ),
    },
}

LLM_DETAIL_TEXTS["en_gb"] = LLM_DETAIL_TEXTS["en_us"]
LLM_DETAIL_TEXTS["ch"] = LLM_DETAIL_TEXTS["de"]


def llm_detail_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz a tabela de consumo detalhado."""
    idioma = llm_table_lang()

    return LLM_DETAIL_TEXTS.get(
        idioma,
        LLM_DETAIL_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def estilizar_tabela_llm_costs(
    tabela,
):
    """
    Aplica fundo escuro e texto claro às tabelas
    do LLM Cost Center.
    """
    return (
        tabela.style
        .set_properties(
            **{
                "background-color": "#020617",
                "color": "#F8FAFC",
                "border-color": "#1E293B",
                "font-weight": "600",
            }
        )
        .set_table_styles(
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
    )


def estilo_status_llm_costs(
    valor,
) -> str:
    """Colore sucesso, falha e erros."""
    texto = str(valor or "").strip().lower()

    if (
        "✅" in texto
        or texto in {"sucesso", "success", "true"}
    ):
        cor = "#22C55E"
    elif (
        "❌" in texto
        or texto in {"falha", "failed", "false"}
    ):
        cor = "#F87171"
    elif texto not in {"", "none", "nan", "—"}:
        cor = "#F59E0B"
    else:
        cor = "#94A3B8"

    return (
        "background-color: #020617;"
        f"color: {cor};"
        "font-weight: 800;"
        "border: 1px solid #1E293B;"
    )


def estilizar_tabela_detalhada_llm(
    tabela,
):
    """
    Aplica tema escuro e cores semânticas
    ao consumo detalhado.
    """
    styler = estilizar_tabela_llm_costs(
        tabela
    )

    colunas = [
        coluna
        for coluna in (
            "Sucesso",
            "Tipo do erro",
        )
        if coluna in tabela.columns
    ]

    if not colunas:
        return styler

    return styler.apply(
        lambda coluna: [
            estilo_status_llm_costs(valor)
            for valor in coluna
        ],
        subset=colunas,
    )


def estilo_alerta_llm_costs(
    valor,
) -> str:
    """Aplica cores às severidades e aos status."""
    texto = str(valor or "").strip().lower()

    if "🔴" in texto or "crítica" in texto:
        cor = "#F87171"
    elif "🟠" in texto or "alta" in texto:
        cor = "#F59E0B"
    elif "🟢" in texto or "resolvido" in texto:
        cor = "#22C55E"
    elif "🔵" in texto or "aberto" in texto:
        cor = "#60A5FA"
    elif "informativa" in texto:
        cor = "#34D399"
    else:
        cor = "#94A3B8"

    return (
        "background-color: #020617;"
        f"color: {cor};"
        "font-weight: 800;"
        "border: 1px solid #1E293B;"
    )


LLM_ALERT_TEXTS = {
    "pt": {
        "created_at": "Criado em",
        "updated_at": "Atualizado em",
        "code": "Código",
        "title": "Título",
        "category": "Categoria",
        "severity": "Severidade",
        "status": "Status",
        "current_value": "Valor atual",
        "limit_value": "Valor limite",
        "unit": "Unidade",
        "resolved_at": "Resolvido em",
        "resolved_by": "Resolvido por",
        "informational": "🟢 Informativa",
        "low": "🔵 Baixa",
        "medium": "🟡 Média",
        "high": "🟠 Alta",
        "critical": "🔴 Crítica",
        "open": "🔵 Aberto",
        "resolved": "🟢 Resolvido",
        "closed": "🟢 Fechado",
        "cancelled": "⚪ Cancelado",
        "unclassified": "⚪ Sem classificação",
        "unknown": "⚪ Desconhecido",
    },
    "en_us": {
        "created_at": "Created at",
        "updated_at": "Updated at",
        "code": "Code",
        "title": "Title",
        "category": "Category",
        "severity": "Severity",
        "status": "Status",
        "current_value": "Current value",
        "limit_value": "Limit value",
        "unit": "Unit",
        "resolved_at": "Resolved at",
        "resolved_by": "Resolved by",
        "informational": "🟢 Informational",
        "low": "🔵 Low",
        "medium": "🟡 Medium",
        "high": "🟠 High",
        "critical": "🔴 Critical",
        "open": "🔵 Open",
        "resolved": "🟢 Resolved",
        "closed": "🟢 Closed",
        "cancelled": "⚪ Cancelled",
        "unclassified": "⚪ Unclassified",
        "unknown": "⚪ Unknown",
    },
    "es": {
        "created_at": "Creado en",
        "updated_at": "Actualizado en",
        "code": "Código",
        "title": "Título",
        "category": "Categoría",
        "severity": "Severidad",
        "status": "Estado",
        "current_value": "Valor actual",
        "limit_value": "Valor límite",
        "unit": "Unidad",
        "resolved_at": "Resuelto en",
        "resolved_by": "Resuelto por",
        "informational": "🟢 Informativa",
        "low": "🔵 Baja",
        "medium": "🟡 Media",
        "high": "🟠 Alta",
        "critical": "🔴 Crítica",
        "open": "🔵 Abierto",
        "resolved": "🟢 Resuelto",
        "closed": "🟢 Cerrado",
        "cancelled": "⚪ Cancelado",
        "unclassified": "⚪ Sin clasificación",
        "unknown": "⚪ Desconocido",
    },
    "fr": {
        "created_at": "Créé le",
        "updated_at": "Mis à jour le",
        "code": "Code",
        "title": "Titre",
        "category": "Catégorie",
        "severity": "Sévérité",
        "status": "Statut",
        "current_value": "Valeur actuelle",
        "limit_value": "Valeur limite",
        "unit": "Unité",
        "resolved_at": "Résolu le",
        "resolved_by": "Résolu par",
        "informational": "🟢 Informationnelle",
        "low": "🔵 Faible",
        "medium": "🟡 Moyenne",
        "high": "🟠 Élevée",
        "critical": "🔴 Critique",
        "open": "🔵 Ouvert",
        "resolved": "🟢 Résolu",
        "closed": "🟢 Fermé",
        "cancelled": "⚪ Annulé",
        "unclassified": "⚪ Non classé",
        "unknown": "⚪ Inconnu",
    },
    "de": {
        "created_at": "Erstellt am",
        "updated_at": "Aktualisiert am",
        "code": "Code",
        "title": "Titel",
        "category": "Kategorie",
        "severity": "Schweregrad",
        "status": "Status",
        "current_value": "Aktueller Wert",
        "limit_value": "Grenzwert",
        "unit": "Einheit",
        "resolved_at": "Gelöst am",
        "resolved_by": "Gelöst von",
        "informational": "🟢 Informativ",
        "low": "🔵 Niedrig",
        "medium": "🟡 Mittel",
        "high": "🟠 Hoch",
        "critical": "🔴 Kritisch",
        "open": "🔵 Offen",
        "resolved": "🟢 Gelöst",
        "closed": "🟢 Geschlossen",
        "cancelled": "⚪ Abgebrochen",
        "unclassified": "⚪ Nicht klassifiziert",
        "unknown": "⚪ Unbekannt",
    },
    "it": {
        "created_at": "Creato il",
        "updated_at": "Aggiornato il",
        "code": "Codice",
        "title": "Titolo",
        "category": "Categoria",
        "severity": "Gravità",
        "status": "Stato",
        "current_value": "Valore attuale",
        "limit_value": "Valore limite",
        "unit": "Unità",
        "resolved_at": "Risolto il",
        "resolved_by": "Risolto da",
        "informational": "🟢 Informativa",
        "low": "🔵 Bassa",
        "medium": "🟡 Media",
        "high": "🟠 Alta",
        "critical": "🔴 Critica",
        "open": "🔵 Aperto",
        "resolved": "🟢 Risolto",
        "closed": "🟢 Chiuso",
        "cancelled": "⚪ Annullato",
        "unclassified": "⚪ Non classificato",
        "unknown": "⚪ Sconosciuto",
    },
    "ro": {
        "created_at": "Creat la",
        "updated_at": "Actualizat la",
        "code": "Cod",
        "title": "Titlu",
        "category": "Categorie",
        "severity": "Severitate",
        "status": "Stare",
        "current_value": "Valoare actuală",
        "limit_value": "Valoare limită",
        "unit": "Unitate",
        "resolved_at": "Rezolvat la",
        "resolved_by": "Rezolvat de",
        "informational": "🟢 Informativă",
        "low": "🔵 Scăzută",
        "medium": "🟡 Medie",
        "high": "🟠 Ridicată",
        "critical": "🔴 Critică",
        "open": "🔵 Deschis",
        "resolved": "🟢 Rezolvat",
        "closed": "🟢 Închis",
        "cancelled": "⚪ Anulat",
        "unclassified": "⚪ Neclasificat",
        "unknown": "⚪ Necunoscut",
    },
    "ua": {
        "created_at": "Створено",
        "updated_at": "Оновлено",
        "code": "Код",
        "title": "Назва",
        "category": "Категорія",
        "severity": "Серйозність",
        "status": "Статус",
        "current_value": "Поточне значення",
        "limit_value": "Граничне значення",
        "unit": "Одиниця",
        "resolved_at": "Вирішено",
        "resolved_by": "Вирішив",
        "informational": "🟢 Інформаційна",
        "low": "🔵 Низька",
        "medium": "🟡 Середня",
        "high": "🟠 Висока",
        "critical": "🔴 Критична",
        "open": "🔵 Відкрито",
        "resolved": "🟢 Вирішено",
        "closed": "🟢 Закрито",
        "cancelled": "⚪ Скасовано",
        "unclassified": "⚪ Без класифікації",
        "unknown": "⚪ Невідомо",
    },
    "ru": {
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "code": "Код",
        "title": "Название",
        "category": "Категория",
        "severity": "Серьезность",
        "status": "Статус",
        "current_value": "Текущее значение",
        "limit_value": "Предельное значение",
        "unit": "Единица",
        "resolved_at": "Решено",
        "resolved_by": "Решил",
        "informational": "🟢 Информационная",
        "low": "🔵 Низкая",
        "medium": "🟡 Средняя",
        "high": "🟠 Высокая",
        "critical": "🔴 Критическая",
        "open": "🔵 Открыто",
        "resolved": "🟢 Решено",
        "closed": "🟢 Закрыто",
        "cancelled": "⚪ Отменено",
        "unclassified": "⚪ Без классификации",
        "unknown": "⚪ Неизвестно",
    },
    "sa": {
        "created_at": "تاريخ الإنشاء",
        "updated_at": "تاريخ التحديث",
        "code": "الرمز",
        "title": "العنوان",
        "category": "الفئة",
        "severity": "الخطورة",
        "status": "الحالة",
        "current_value": "القيمة الحالية",
        "limit_value": "القيمة الحدية",
        "unit": "الوحدة",
        "resolved_at": "تاريخ الحل",
        "resolved_by": "تم الحل بواسطة",
        "informational": "🟢 معلوماتي",
        "low": "🔵 منخفض",
        "medium": "🟡 متوسط",
        "high": "🟠 مرتفع",
        "critical": "🔴 حرج",
        "open": "🔵 مفتوح",
        "resolved": "🟢 محلول",
        "closed": "🟢 مغلق",
        "cancelled": "⚪ ملغى",
        "unclassified": "⚪ غير مصنف",
        "unknown": "⚪ غير معروف",
    },
}

LLM_ALERT_TEXTS["en_gb"] = LLM_ALERT_TEXTS["en_us"]
LLM_ALERT_TEXTS["ch"] = LLM_ALERT_TEXTS["de"]


def llm_alert_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz a tabela de auditoria dos alertas."""
    idioma = llm_table_lang()

    return LLM_ALERT_TEXTS.get(
        idioma,
        LLM_ALERT_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def estilizar_tabela_alertas_llm(
    tabela,
):
    """Aplica tema escuro e cores aos alertas."""
    styler = estilizar_tabela_llm_costs(
        tabela
    )

    colunas = [
        coluna
        for coluna in (
            "Severidade",
            "Status",
        )
        if coluna in tabela.columns
    ]

    if not colunas:
        return styler

    return styler.apply(
        lambda coluna: [
            estilo_alerta_llm_costs(valor)
            for valor in coluna
        ],
        subset=colunas,
    )


def estilo_notificacao_llm_costs(
    valor,
) -> str:
    """Colore status de envio, entrega e erros."""
    texto = str(valor or "").strip().lower()

    if (
        "🟢" in texto
        or "entregue" in texto
        or texto == "sucesso"
    ):
        cor = "#22C55E"
    elif (
        "🔵" in texto
        or "enviado" in texto
        or "clicado" in texto
        or "aberto" in texto
    ):
        cor = "#60A5FA"
    elif (
        "🟡" in texto
        or "aguardando" in texto
        or "atrasado" in texto
    ):
        cor = "#FACC15"
    elif (
        "🟠" in texto
        or "devolvido" in texto
    ):
        cor = "#F59E0B"
    elif (
        "🟣" in texto
        or "suprimido" in texto
    ):
        cor = "#C084FC"
    elif (
        "🔴" in texto
        or "falhou" in texto
        or "reclamação" in texto
        or "reclamacao" in texto
        or "erro" in texto
    ):
        cor = "#F87171"
    else:
        cor = "#94A3B8"

    return (
        "background-color: #020617;"
        f"color: {cor};"
        "font-weight: 800;"
        "border: 1px solid #1E293B;"
    )


LLM_NOTIFICATION_TEXTS = {
    "pt": {
        "alert": "Alerta",
        "send_status": "Status do envio",
        "delivery_status": "Status da entrega",
        "resend_event": "Evento do Resend",
        "recipient": "Destinatário",
        "subject": "Assunto",
        "attempts": "Tentativas",
        "message_id": "Message ID",
        "created_at": "Criado em",
        "sent_at": "Enviado em",
        "delivered_at": "Entregue em",
        "returned_at": "Devolvido em",
        "webhook_at": "Webhook recebido em",
        "delivery_reason": "Motivo da entrega/falha",
        "error_type": "Tipo do erro",
        "error_message": "Mensagem de erro",
        "recipient_help": (
            "Endereço mascarado para preservar "
            "a privacidade."
        ),
        "attempts_help": (
            "Quantidade de tentativas de envio. "
            "Limite: 3."
        ),
        "sent": "🔵 Enviado",
        "waiting": "🟡 Aguardando",
        "failed": "🔴 Falhou",
        "cancelled": "⚪ Cancelado",
        "delivered": "🟢 Entregue",
        "delayed": "🟡 Atrasado",
        "returned": "🟠 Devolvido",
        "suppressed": "🟣 Suprimido",
        "complaint": "🔴 Reclamação",
        "opened": "🔵 Aberto",
        "clicked": "🔵 Clicado",
        "unknown": "⚪ Desconhecido",
    },
    "en_us": {
        "alert": "Alert",
        "send_status": "Send status",
        "delivery_status": "Delivery status",
        "resend_event": "Resend event",
        "recipient": "Recipient",
        "subject": "Subject",
        "attempts": "Attempts",
        "message_id": "Message ID",
        "created_at": "Created at",
        "sent_at": "Sent at",
        "delivered_at": "Delivered at",
        "returned_at": "Returned at",
        "webhook_at": "Webhook received at",
        "delivery_reason": "Delivery/failure reason",
        "error_type": "Error type",
        "error_message": "Error message",
        "recipient_help": (
            "Masked address to preserve privacy."
        ),
        "attempts_help": (
            "Number of delivery attempts. Limit: 3."
        ),
        "sent": "🔵 Sent",
        "waiting": "🟡 Waiting",
        "failed": "🔴 Failed",
        "cancelled": "⚪ Cancelled",
        "delivered": "🟢 Delivered",
        "delayed": "🟡 Delayed",
        "returned": "🟠 Returned",
        "suppressed": "🟣 Suppressed",
        "complaint": "🔴 Complaint",
        "opened": "🔵 Opened",
        "clicked": "🔵 Clicked",
        "unknown": "⚪ Unknown",
    },
    "es": {
        "alert": "Alerta",
        "send_status": "Estado del envío",
        "delivery_status": "Estado de entrega",
        "resend_event": "Evento de Resend",
        "recipient": "Destinatario",
        "subject": "Asunto",
        "attempts": "Intentos",
        "message_id": "ID del mensaje",
        "created_at": "Creado en",
        "sent_at": "Enviado en",
        "delivered_at": "Entregado en",
        "returned_at": "Devuelto en",
        "webhook_at": "Webhook recibido en",
        "delivery_reason": "Motivo de entrega/fallo",
        "error_type": "Tipo de error",
        "error_message": "Mensaje de error",
        "recipient_help": (
            "Dirección enmascarada para preservar "
            "la privacidad."
        ),
        "attempts_help": (
            "Cantidad de intentos de envío. Límite: 3."
        ),
        "sent": "🔵 Enviado",
        "waiting": "🟡 En espera",
        "failed": "🔴 Falló",
        "cancelled": "⚪ Cancelado",
        "delivered": "🟢 Entregado",
        "delayed": "🟡 Retrasado",
        "returned": "🟠 Devuelto",
        "suppressed": "🟣 Suprimido",
        "complaint": "🔴 Reclamación",
        "opened": "🔵 Abierto",
        "clicked": "🔵 Clicado",
        "unknown": "⚪ Desconocido",
    },
    "fr": {
        "alert": "Alerte",
        "send_status": "Statut d'envoi",
        "delivery_status": "Statut de livraison",
        "resend_event": "Événement Resend",
        "recipient": "Destinataire",
        "subject": "Objet",
        "attempts": "Tentatives",
        "message_id": "ID du message",
        "created_at": "Créé le",
        "sent_at": "Envoyé le",
        "delivered_at": "Livré le",
        "returned_at": "Retourné le",
        "webhook_at": "Webhook reçu le",
        "delivery_reason": "Motif de livraison/échec",
        "error_type": "Type d'erreur",
        "error_message": "Message d'erreur",
        "recipient_help": (
            "Adresse masquée pour préserver "
            "la confidentialité."
        ),
        "attempts_help": (
            "Nombre de tentatives d'envoi. Limite : 3."
        ),
        "sent": "🔵 Envoyé",
        "waiting": "🟡 En attente",
        "failed": "🔴 Échec",
        "cancelled": "⚪ Annulé",
        "delivered": "🟢 Livré",
        "delayed": "🟡 Retardé",
        "returned": "🟠 Retourné",
        "suppressed": "🟣 Supprimé",
        "complaint": "🔴 Réclamation",
        "opened": "🔵 Ouvert",
        "clicked": "🔵 Cliqué",
        "unknown": "⚪ Inconnu",
    },
    "de": {
        "alert": "Warnung",
        "send_status": "Sendestatus",
        "delivery_status": "Zustellstatus",
        "resend_event": "Resend-Ereignis",
        "recipient": "Empfänger",
        "subject": "Betreff",
        "attempts": "Versuche",
        "message_id": "Nachrichten-ID",
        "created_at": "Erstellt am",
        "sent_at": "Gesendet am",
        "delivered_at": "Zugestellt am",
        "returned_at": "Zurückgesendet am",
        "webhook_at": "Webhook empfangen am",
        "delivery_reason": "Zustell-/Fehlergrund",
        "error_type": "Fehlertyp",
        "error_message": "Fehlermeldung",
        "recipient_help": (
            "Maskierte Adresse zum Schutz "
            "der Privatsphäre."
        ),
        "attempts_help": (
            "Anzahl der Sendeversuche. Grenze: 3."
        ),
        "sent": "🔵 Gesendet",
        "waiting": "🟡 Wartend",
        "failed": "🔴 Fehlgeschlagen",
        "cancelled": "⚪ Abgebrochen",
        "delivered": "🟢 Zugestellt",
        "delayed": "🟡 Verzögert",
        "returned": "🟠 Zurückgesendet",
        "suppressed": "🟣 Unterdrückt",
        "complaint": "🔴 Beschwerde",
        "opened": "🔵 Geöffnet",
        "clicked": "🔵 Geklickt",
        "unknown": "⚪ Unbekannt",
    },
    "it": {
        "alert": "Avviso",
        "send_status": "Stato invio",
        "delivery_status": "Stato consegna",
        "resend_event": "Evento Resend",
        "recipient": "Destinatario",
        "subject": "Oggetto",
        "attempts": "Tentativi",
        "message_id": "ID messaggio",
        "created_at": "Creato il",
        "sent_at": "Inviato il",
        "delivered_at": "Consegnato il",
        "returned_at": "Restituito il",
        "webhook_at": "Webhook ricevuto il",
        "delivery_reason": "Motivo consegna/errore",
        "error_type": "Tipo di errore",
        "error_message": "Messaggio di errore",
        "recipient_help": (
            "Indirizzo mascherato per preservare "
            "la privacy."
        ),
        "attempts_help": (
            "Numero di tentativi di invio. Limite: 3."
        ),
        "sent": "🔵 Inviato",
        "waiting": "🟡 In attesa",
        "failed": "🔴 Fallito",
        "cancelled": "⚪ Annullato",
        "delivered": "🟢 Consegnato",
        "delayed": "🟡 In ritardo",
        "returned": "🟠 Restituito",
        "suppressed": "🟣 Soppresso",
        "complaint": "🔴 Reclamo",
        "opened": "🔵 Aperto",
        "clicked": "🔵 Cliccato",
        "unknown": "⚪ Sconosciuto",
    },
    "ro": {
        "alert": "Alertă",
        "send_status": "Starea trimiterii",
        "delivery_status": "Starea livrării",
        "resend_event": "Eveniment Resend",
        "recipient": "Destinatar",
        "subject": "Subiect",
        "attempts": "Încercări",
        "message_id": "ID mesaj",
        "created_at": "Creat la",
        "sent_at": "Trimis la",
        "delivered_at": "Livrat la",
        "returned_at": "Returnat la",
        "webhook_at": "Webhook primit la",
        "delivery_reason": "Motiv livrare/eșec",
        "error_type": "Tipul erorii",
        "error_message": "Mesaj de eroare",
        "recipient_help": (
            "Adresă mascată pentru protejarea "
            "confidențialității."
        ),
        "attempts_help": (
            "Numărul încercărilor de trimitere. "
            "Limită: 3."
        ),
        "sent": "🔵 Trimis",
        "waiting": "🟡 În așteptare",
        "failed": "🔴 Eșuat",
        "cancelled": "⚪ Anulat",
        "delivered": "🟢 Livrat",
        "delayed": "🟡 Întârziat",
        "returned": "🟠 Returnat",
        "suppressed": "🟣 Suprimat",
        "complaint": "🔴 Reclamație",
        "opened": "🔵 Deschis",
        "clicked": "🔵 Accesat",
        "unknown": "⚪ Necunoscut",
    },
    "ua": {
        "alert": "Сповіщення",
        "send_status": "Статус надсилання",
        "delivery_status": "Статус доставки",
        "resend_event": "Подія Resend",
        "recipient": "Одержувач",
        "subject": "Тема",
        "attempts": "Спроби",
        "message_id": "ID повідомлення",
        "created_at": "Створено",
        "sent_at": "Надіслано",
        "delivered_at": "Доставлено",
        "returned_at": "Повернено",
        "webhook_at": "Webhook отримано",
        "delivery_reason": "Причина доставки/помилки",
        "error_type": "Тип помилки",
        "error_message": "Повідомлення про помилку",
        "recipient_help": (
            "Замаскована адреса для захисту "
            "конфіденційності."
        ),
        "attempts_help": (
            "Кількість спроб надсилання. Ліміт: 3."
        ),
        "sent": "🔵 Надіслано",
        "waiting": "🟡 Очікування",
        "failed": "🔴 Помилка",
        "cancelled": "⚪ Скасовано",
        "delivered": "🟢 Доставлено",
        "delayed": "🟡 Затримано",
        "returned": "🟠 Повернено",
        "suppressed": "🟣 Пригнічено",
        "complaint": "🔴 Скарга",
        "opened": "🔵 Відкрито",
        "clicked": "🔵 Натиснуто",
        "unknown": "⚪ Невідомо",
    },
    "ru": {
        "alert": "Оповещение",
        "send_status": "Статус отправки",
        "delivery_status": "Статус доставки",
        "resend_event": "Событие Resend",
        "recipient": "Получатель",
        "subject": "Тема",
        "attempts": "Попытки",
        "message_id": "ID сообщения",
        "created_at": "Создано",
        "sent_at": "Отправлено",
        "delivered_at": "Доставлено",
        "returned_at": "Возвращено",
        "webhook_at": "Webhook получен",
        "delivery_reason": "Причина доставки/ошибки",
        "error_type": "Тип ошибки",
        "error_message": "Сообщение об ошибке",
        "recipient_help": (
            "Замаскированный адрес для защиты "
            "конфиденциальности."
        ),
        "attempts_help": (
            "Количество попыток отправки. Лимит: 3."
        ),
        "sent": "🔵 Отправлено",
        "waiting": "🟡 Ожидание",
        "failed": "🔴 Ошибка",
        "cancelled": "⚪ Отменено",
        "delivered": "🟢 Доставлено",
        "delayed": "🟡 Задержано",
        "returned": "🟠 Возвращено",
        "suppressed": "🟣 Подавлено",
        "complaint": "🔴 Жалоба",
        "opened": "🔵 Открыто",
        "clicked": "🔵 Нажато",
        "unknown": "⚪ Неизвестно",
    },
    "sa": {
        "alert": "التنبيه",
        "send_status": "حالة الإرسال",
        "delivery_status": "حالة التسليم",
        "resend_event": "حدث Resend",
        "recipient": "المستلم",
        "subject": "الموضوع",
        "attempts": "المحاولات",
        "message_id": "معرف الرسالة",
        "created_at": "تاريخ الإنشاء",
        "sent_at": "تاريخ الإرسال",
        "delivered_at": "تاريخ التسليم",
        "returned_at": "تاريخ الإرجاع",
        "webhook_at": "تاريخ استلام Webhook",
        "delivery_reason": "سبب التسليم/الفشل",
        "error_type": "نوع الخطأ",
        "error_message": "رسالة الخطأ",
        "recipient_help": (
            "عنوان مخفي للحفاظ على الخصوصية."
        ),
        "attempts_help": (
            "عدد محاولات الإرسال. الحد: 3."
        ),
        "sent": "🔵 تم الإرسال",
        "waiting": "🟡 قيد الانتظار",
        "failed": "🔴 فشل",
        "cancelled": "⚪ ملغى",
        "delivered": "🟢 تم التسليم",
        "delayed": "🟡 متأخر",
        "returned": "🟠 مرتجع",
        "suppressed": "🟣 محظور",
        "complaint": "🔴 شكوى",
        "opened": "🔵 مفتوح",
        "clicked": "🔵 تم النقر",
        "unknown": "⚪ غير معروف",
    },
}

LLM_NOTIFICATION_TEXTS["en_gb"] = (
    LLM_NOTIFICATION_TEXTS["en_us"]
)
LLM_NOTIFICATION_TEXTS["ch"] = (
    LLM_NOTIFICATION_TEXTS["de"]
)


def llm_notification_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz a auditoria das notificações."""
    idioma = llm_table_lang()

    return LLM_NOTIFICATION_TEXTS.get(
        idioma,
        LLM_NOTIFICATION_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def traduzir_status_notificacao(
    valor: object,
) -> str:
    """Traduz status mantendo o ícone semântico."""
    texto = str(valor or "").strip().lower()

    status = (
        ("reclama", "complaint"),
        ("complaint", "complaint"),
        ("suprim", "suppressed"),
        ("suppress", "suppressed"),
        ("devolv", "returned"),
        ("return", "returned"),
        ("entreg", "delivered"),
        ("deliver", "delivered"),
        ("atras", "delayed"),
        ("delay", "delayed"),
        ("aguard", "waiting"),
        ("pendente", "waiting"),
        ("wait", "waiting"),
        ("enviado", "sent"),
        ("sent", "sent"),
        ("falh", "failed"),
        ("failed", "failed"),
        ("erro", "failed"),
        ("cancel", "cancelled"),
        ("aberto", "opened"),
        ("opened", "opened"),
        ("clic", "clicked"),
        ("click", "clicked"),
    )

    for termo, key in status:
        if termo in texto:
            return llm_notification_t(key)

    return llm_notification_t("unknown")


def estilizar_tabela_notificacoes_llm(
    tabela,
):
    """
    Aplica tema escuro e cores semânticas
    à auditoria das notificações.
    """
    styler = estilizar_tabela_llm_costs(
        tabela
    )

    colunas = [
        coluna
        for coluna in (
            "Status do envio",
            "Status da entrega",
            "Tipo do erro",
            "Mensagem de erro",
        )
        if coluna in tabela.columns
    ]

    if not colunas:
        return styler

    return styler.apply(
        lambda coluna: [
            estilo_notificacao_llm_costs(valor)
            for valor in coluna
        ],
        subset=colunas,
    )


def estilo_evento_resend_llm(
    valor,
) -> str:
    """Colore resultados, processamento e erros."""
    texto = str(valor or "").strip().lower()

    if (
        "🟢" in texto
        or texto in {
            "ok",
            "sucesso",
            "processado",
            "entregue",
        }
    ):
        cor = "#22C55E"
    elif (
        "🔴" in texto
        or texto in {
            "erro",
            "falha",
            "não",
            "nao",
        }
    ):
        cor = "#F87171"
    elif (
        "🟡" in texto
        or "pendente" in texto
        or "aguardando" in texto
    ):
        cor = "#FACC15"
    elif texto not in {
        "",
        "none",
        "nan",
        "—",
    }:
        cor = "#60A5FA"
    else:
        cor = "#94A3B8"

    return (
        "background-color: #020617;"
        f"color: {cor};"
        "font-weight: 800;"
        "border: 1px solid #1E293B;"
    )


LLM_RESEND_EVENT_TEXTS = {
    "pt": {
        "event_type": "Tipo do evento",
        "message_id": "Message ID",
        "received_at": "Recebido em",
        "processed": "Processado",
        "processed_at": "Processado em",
        "result": "Resultado",
        "error": "Erro",
        "svix_id": "Svix ID",
        "event_help": (
            "Evento recebido pelo webhook do Resend."
        ),
        "svix_help": (
            "Identificador de segurança do webhook."
        ),
        "yes": "🟢 Sim",
        "no": "🔴 Não",
        "success": "🟢 Sucesso",
        "processed_value": "🟢 Processado",
        "error_value": "🔴 Erro",
        "failure": "🔴 Falha",
        "pending": "🟡 Pendente",
        "ignored": "🔵 Ignorado",
        "no_result": "⚪ Sem resultado",
    },
    "en_us": {
        "event_type": "Event type",
        "message_id": "Message ID",
        "received_at": "Received at",
        "processed": "Processed",
        "processed_at": "Processed at",
        "result": "Result",
        "error": "Error",
        "svix_id": "Svix ID",
        "event_help": (
            "Event received by the Resend webhook."
        ),
        "svix_help": (
            "Webhook security identifier."
        ),
        "yes": "🟢 Yes",
        "no": "🔴 No",
        "success": "🟢 Success",
        "processed_value": "🟢 Processed",
        "error_value": "🔴 Error",
        "failure": "🔴 Failure",
        "pending": "🟡 Pending",
        "ignored": "🔵 Ignored",
        "no_result": "⚪ No result",
    },
    "es": {
        "event_type": "Tipo de evento",
        "message_id": "ID del mensaje",
        "received_at": "Recibido en",
        "processed": "Procesado",
        "processed_at": "Procesado en",
        "result": "Resultado",
        "error": "Error",
        "svix_id": "ID de Svix",
        "event_help": (
            "Evento recibido por el webhook de Resend."
        ),
        "svix_help": (
            "Identificador de seguridad del webhook."
        ),
        "yes": "🟢 Sí",
        "no": "🔴 No",
        "success": "🟢 Éxito",
        "processed_value": "🟢 Procesado",
        "error_value": "🔴 Error",
        "failure": "🔴 Fallo",
        "pending": "🟡 Pendiente",
        "ignored": "🔵 Ignorado",
        "no_result": "⚪ Sin resultado",
    },
    "fr": {
        "event_type": "Type d’événement",
        "message_id": "ID du message",
        "received_at": "Reçu le",
        "processed": "Traité",
        "processed_at": "Traité le",
        "result": "Résultat",
        "error": "Erreur",
        "svix_id": "ID Svix",
        "event_help": (
            "Événement reçu par le webhook Resend."
        ),
        "svix_help": (
            "Identifiant de sécurité du webhook."
        ),
        "yes": "🟢 Oui",
        "no": "🔴 Non",
        "success": "🟢 Succès",
        "processed_value": "🟢 Traité",
        "error_value": "🔴 Erreur",
        "failure": "🔴 Échec",
        "pending": "🟡 En attente",
        "ignored": "🔵 Ignoré",
        "no_result": "⚪ Aucun résultat",
    },
    "de": {
        "event_type": "Ereignistyp",
        "message_id": "Nachrichten-ID",
        "received_at": "Empfangen am",
        "processed": "Verarbeitet",
        "processed_at": "Verarbeitet am",
        "result": "Ergebnis",
        "error": "Fehler",
        "svix_id": "Svix-ID",
        "event_help": (
            "Vom Resend-Webhook empfangenes Ereignis."
        ),
        "svix_help": (
            "Sicherheitskennung des Webhooks."
        ),
        "yes": "🟢 Ja",
        "no": "🔴 Nein",
        "success": "🟢 Erfolgreich",
        "processed_value": "🟢 Verarbeitet",
        "error_value": "🔴 Fehler",
        "failure": "🔴 Fehlgeschlagen",
        "pending": "🟡 Ausstehend",
        "ignored": "🔵 Ignoriert",
        "no_result": "⚪ Kein Ergebnis",
    },
    "it": {
        "event_type": "Tipo di evento",
        "message_id": "ID messaggio",
        "received_at": "Ricevuto il",
        "processed": "Elaborato",
        "processed_at": "Elaborato il",
        "result": "Risultato",
        "error": "Errore",
        "svix_id": "ID Svix",
        "event_help": (
            "Evento ricevuto dal webhook Resend."
        ),
        "svix_help": (
            "Identificatore di sicurezza del webhook."
        ),
        "yes": "🟢 Sì",
        "no": "🔴 No",
        "success": "🟢 Successo",
        "processed_value": "🟢 Elaborato",
        "error_value": "🔴 Errore",
        "failure": "🔴 Fallimento",
        "pending": "🟡 In attesa",
        "ignored": "🔵 Ignorato",
        "no_result": "⚪ Nessun risultato",
    },
    "ro": {
        "event_type": "Tipul evenimentului",
        "message_id": "ID mesaj",
        "received_at": "Primit la",
        "processed": "Procesat",
        "processed_at": "Procesat la",
        "result": "Rezultat",
        "error": "Eroare",
        "svix_id": "ID Svix",
        "event_help": (
            "Eveniment primit de webhook-ul Resend."
        ),
        "svix_help": (
            "Identificatorul de securitate al webhook-ului."
        ),
        "yes": "🟢 Da",
        "no": "🔴 Nu",
        "success": "🟢 Succes",
        "processed_value": "🟢 Procesat",
        "error_value": "🔴 Eroare",
        "failure": "🔴 Eșec",
        "pending": "🟡 În așteptare",
        "ignored": "🔵 Ignorat",
        "no_result": "⚪ Fără rezultat",
    },
    "ua": {
        "event_type": "Тип події",
        "message_id": "ID повідомлення",
        "received_at": "Отримано",
        "processed": "Оброблено",
        "processed_at": "Оброблено о",
        "result": "Результат",
        "error": "Помилка",
        "svix_id": "ID Svix",
        "event_help": (
            "Подія, отримана webhook Resend."
        ),
        "svix_help": (
            "Ідентифікатор безпеки webhook."
        ),
        "yes": "🟢 Так",
        "no": "🔴 Ні",
        "success": "🟢 Успішно",
        "processed_value": "🟢 Оброблено",
        "error_value": "🔴 Помилка",
        "failure": "🔴 Невдача",
        "pending": "🟡 Очікування",
        "ignored": "🔵 Проігноровано",
        "no_result": "⚪ Немає результату",
    },
    "ru": {
        "event_type": "Тип события",
        "message_id": "ID сообщения",
        "received_at": "Получено",
        "processed": "Обработано",
        "processed_at": "Обработано в",
        "result": "Результат",
        "error": "Ошибка",
        "svix_id": "ID Svix",
        "event_help": (
            "Событие, полученное webhook Resend."
        ),
        "svix_help": (
            "Идентификатор безопасности webhook."
        ),
        "yes": "🟢 Да",
        "no": "🔴 Нет",
        "success": "🟢 Успешно",
        "processed_value": "🟢 Обработано",
        "error_value": "🔴 Ошибка",
        "failure": "🔴 Сбой",
        "pending": "🟡 Ожидание",
        "ignored": "🔵 Проигнорировано",
        "no_result": "⚪ Нет результата",
    },
    "sa": {
        "event_type": "نوع الحدث",
        "message_id": "معرف الرسالة",
        "received_at": "تاريخ الاستلام",
        "processed": "تمت المعالجة",
        "processed_at": "تاريخ المعالجة",
        "result": "النتيجة",
        "error": "الخطأ",
        "svix_id": "معرف Svix",
        "event_help": (
            "حدث تم استلامه من Webhook الخاص بـ Resend."
        ),
        "svix_help": (
            "معرف أمان Webhook."
        ),
        "yes": "🟢 نعم",
        "no": "🔴 لا",
        "success": "🟢 نجاح",
        "processed_value": "🟢 تمت المعالجة",
        "error_value": "🔴 خطأ",
        "failure": "🔴 فشل",
        "pending": "🟡 قيد الانتظار",
        "ignored": "🔵 تم التجاهل",
        "no_result": "⚪ لا توجد نتيجة",
    },
}

LLM_RESEND_EVENT_TEXTS["en_gb"] = (
    LLM_RESEND_EVENT_TEXTS["en_us"]
)
LLM_RESEND_EVENT_TEXTS["ch"] = (
    LLM_RESEND_EVENT_TEXTS["de"]
)


def llm_resend_event_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz a tabela de eventos do Resend."""
    idioma = llm_table_lang()

    return LLM_RESEND_EVENT_TEXTS.get(
        idioma,
        LLM_RESEND_EVENT_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def estilizar_tabela_eventos_resend(
    tabela,
):
    """
    Aplica tema escuro e cores semânticas
    aos eventos do webhook.
    """
    styler = estilizar_tabela_llm_costs(
        tabela
    )

    colunas = [
        coluna
        for coluna in (
            "Processado",
            "Resultado",
            "Erro",
        )
        if coluna in tabela.columns
    ]

    if not colunas:
        return styler

    return styler.apply(
        lambda coluna: [
            estilo_evento_resend_llm(valor)
            for valor in coluna
        ],
        subset=colunas,
    )


def aplicar_tema_llm_cost_chart(
    fig,
    *,
    height=420,
):
    """Aplica o tema visual do LLM Cost Center."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=LLM_COST_CHART_BG,
        plot_bgcolor=LLM_COST_CHART_BG,
        font={
            "color": LLM_COST_CHART_TEXT,
            "family": "Arial",
        },
        hoverlabel={
            "bgcolor": "#0F172A",
            "font_color": LLM_COST_CHART_TEXT,
        },
        margin={
            "l": 28,
            "r": 28,
            "t": 18,
            "b": 35,
        },
        height=height,
    )

    fig.update_xaxes(
        color=LLM_COST_CHART_TEXT,
        gridcolor=LLM_COST_CHART_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    fig.update_yaxes(
        color=LLM_COST_CHART_TEXT,
        gridcolor=LLM_COST_CHART_GRID,
        zerolinecolor=(
            "rgba(148, 163, 184, 0.25)"
        ),
    )

    return fig


def preparar_consumo_exibicao(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Normaliza os eventos para análises e gráficos.
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
        "tokens_entrada",
        "tokens_saida",
        "tokens_totais",
        "custo_entrada_usd",
        "custo_saida_usd",
        "custo_total_usd",
        "duracao_ms",
    ]

    for coluna in colunas_numericas:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(
                base[coluna],
                errors="coerce",
            ).fillna(0)

    if "sucesso" in base.columns:
        base["sucesso"] = (
            base["sucesso"]
            .fillna(False)
            .astype(bool)
        )

    return (
        base.dropna(
            subset=["criado_em"]
        )
        .sort_values(
            "criado_em",
            ascending=True,
        )
        .reset_index(drop=True)
    )


def resumir_consumo_llm(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Calcula os indicadores principais do Cost Center.
    """
    base = preparar_consumo_exibicao(df)

    if base.empty:
        return {
            "eventos": 0,
            "tokens_entrada": 0,
            "tokens_saida": 0,
            "tokens_totais": 0,
            "custo_total_usd": 0.0,
            "duracao_media_ms": 0.0,
            "duracao_p95_ms": 0.0,
            "taxa_sucesso": 0.0,
        }

    total = len(base)

    sucessos = int(
        base["sucesso"].sum()
    )

    return {
        "eventos": total,
        "tokens_entrada": int(
            base["tokens_entrada"].sum()
        ),
        "tokens_saida": int(
            base["tokens_saida"].sum()
        ),
        "tokens_totais": int(
            base["tokens_totais"].sum()
        ),
        "custo_total_usd": round(
            float(
                base["custo_total_usd"].sum()
            ),
            8,
        ),
        "duracao_media_ms": round(
            float(
                base["duracao_ms"].mean()
            ),
            3,
        ),
        "duracao_p95_ms": round(
            float(
                base["duracao_ms"].quantile(
                    0.95
                )
            ),
            3,
        ),
        "taxa_sucesso": round(
            (
                sucessos
                / total
            )
            * 100,
            2,
        ),
    }



LLM_ALERT_SECTION_TEXTS = {
    "pt": {
        "section_title": (
            "## 🚨 Alertas de custo e desempenho"
        ),
        "evaluate_now": (
            "🔎 Avaliar alertas agora"
        ),
        "evaluation_failed": (
            "Não foi possível concluir a avaliação."
        ),
        "load_failed": (
            "Não foi possível carregar os alertas."
        ),
        "no_alerts": (
            "Nenhum alerta encontrado para o filtro atual."
        ),
        "alerts_list": "### Lista de alertas",
        "email_disabled": (
            "As notificações por e-mail estão "
            "desabilitadas no ambiente."
        ),
        "recipient_missing": (
            "O destinatário dos alertas não está configurado."
        ),
        "resend_missing": (
            "A integração com o Resend não está configurada."
        ),
        "email_enabled": (
            "Notificações por e-mail habilitadas. "
            "Alertas altos e críticos podem ser enviados."
        ),
        "recommendation": "Recomendação",
        "notification_sent": (
            "📧 Notificação já enviada"
        ),
        "restricted_delivery": (
            "📧 Envio reservado para alertas "
            "altos e críticos."
        ),
        "send_email": (
            "📧 Enviar alerta por e-mail"
        ),
        "sending_alert": "Enviando alerta...",
        "alert_sent": (
            "Alerta enviado por e-mail."
        ),
        "already_sent": (
            "Este alerta já foi enviado por e-mail."
        ),
        "send_failed": (
            "Falha ao enviar o alerta"
        ),
        "resolve": (
            "✅ Marcar como resolvido"
        ),
        "resolved": "Alerta resolvido.",
        "already_resolved": (
            "O alerta já foi resolvido."
        ),
        "integration_health": (
            "### 🩺 Saúde das integrações"
        ),
        "integration_details": (
            "Detalhes técnicos das integrações"
        ),
        "partial_health": (
            "Saúde parcialmente indisponível."
        ),
        "health_failed": (
            "Não foi possível carregar a saúde "
            "das integrações"
        ),
        "webhook_events": (
            "### 📨 Eventos do webhook do Resend"
        ),
        "events_unavailable": (
            "Eventos indisponíveis."
        ),
        "no_webhook_events": (
            "Nenhum evento do webhook encontrado "
            "neste período."
        ),
        "export_webhook": (
            "⬇️ Exportar eventos do webhook em CSV"
        ),
        "notification_audit": (
            "### Auditoria das notificações"
        ),
        "notifications_load_failed": (
            "Não foi possível carregar as notificações."
        ),
        "no_notifications": (
            "Nenhuma notificação registrada."
        ),
        "export_notifications": (
            "⬇️ Exportar notificações em CSV"
        ),
        "retry_section": (
            "### 🔄 Reenvio de notificações"
        ),
        "no_retry": (
            "Nenhuma notificação disponível para reenvio."
        ),
        "no_failed_retry": (
            "Não existem notificações com falha "
            "aguardando reenvio."
        ),
        "retry_limit": (
            "O reenvio é limitado a três tentativas "
            "por notificação."
        ),
        "retry": "🔄 Reenviar",
        "retrying": (
            "Reenviando notificação..."
        ),
        "retry_success": (
            "Notificação reenviada."
        ),
        "retry_failed": "Falha no reenvio.",
        "alerts_audit": (
            "### Auditoria dos alertas"
        ),
        "export_alerts": (
            "⬇️ Exportar alertas em CSV"
        ),
    },
    "en_us": {
        "section_title": "## 🚨 Cost and performance alerts",
        "evaluate_now": "🔎 Evaluate alerts now",
        "evaluation_failed": (
            "The evaluation could not be completed."
        ),
        "load_failed": "Alerts could not be loaded.",
        "no_alerts": (
            "No alerts were found for the current filter."
        ),
        "alerts_list": "### Alert list",
        "email_disabled": (
            "Email notifications are disabled "
            "in this environment."
        ),
        "recipient_missing": (
            "The alert recipient is not configured."
        ),
        "resend_missing": (
            "The Resend integration is not configured."
        ),
        "email_enabled": (
            "Email notifications are enabled. "
            "High and critical alerts can be sent."
        ),
        "recommendation": "Recommendation",
        "notification_sent": "📧 Notification already sent",
        "restricted_delivery": (
            "📧 Delivery is reserved for high "
            "and critical alerts."
        ),
        "send_email": "📧 Send alert by email",
        "sending_alert": "Sending alert...",
        "alert_sent": "Alert sent by email.",
        "already_sent": (
            "This alert has already been sent by email."
        ),
        "send_failed": "Failed to send the alert",
        "resolve": "✅ Mark as resolved",
        "resolved": "Alert resolved.",
        "already_resolved": (
            "The alert has already been resolved."
        ),
        "integration_health": (
            "### 🩺 Integration health"
        ),
        "integration_details": (
            "Technical integration details"
        ),
        "partial_health": (
            "Integration health is partially unavailable."
        ),
        "health_failed": (
            "Could not load integration health"
        ),
        "webhook_events": (
            "### 📨 Resend webhook events"
        ),
        "events_unavailable": "Events are unavailable.",
        "no_webhook_events": (
            "No webhook events were found "
            "for this period."
        ),
        "export_webhook": (
            "⬇️ Export webhook events as CSV"
        ),
        "notification_audit": (
            "### Notification audit"
        ),
        "notifications_load_failed": (
            "Notifications could not be loaded."
        ),
        "no_notifications": (
            "No notifications have been recorded."
        ),
        "export_notifications": (
            "⬇️ Export notifications as CSV"
        ),
        "retry_section": (
            "### 🔄 Notification retry"
        ),
        "no_retry": (
            "No notification is available for retry."
        ),
        "no_failed_retry": (
            "There are no failed notifications "
            "waiting for retry."
        ),
        "retry_limit": (
            "Retry is limited to three attempts "
            "per notification."
        ),
        "retry": "🔄 Retry",
        "retrying": "Retrying notification...",
        "retry_success": "Notification resent.",
        "retry_failed": "Retry failed.",
        "alerts_audit": "### Alert audit",
        "export_alerts": "⬇️ Export alerts as CSV",
    },
    "es": {
        "section_title": (
            "## 🚨 Alertas de costo y rendimiento"
        ),
        "evaluate_now": "🔎 Evaluar alertas ahora",
        "evaluation_failed": (
            "No se pudo completar la evaluación."
        ),
        "load_failed": (
            "No se pudieron cargar las alertas."
        ),
        "no_alerts": (
            "No se encontraron alertas para el filtro actual."
        ),
        "alerts_list": "### Lista de alertas",
        "email_disabled": (
            "Las notificaciones por correo están "
            "deshabilitadas en el entorno."
        ),
        "recipient_missing": (
            "El destinatario de las alertas no está configurado."
        ),
        "resend_missing": (
            "La integración con Resend no está configurada."
        ),
        "email_enabled": (
            "Las notificaciones por correo están habilitadas. "
            "Se pueden enviar alertas altas y críticas."
        ),
        "recommendation": "Recomendación",
        "notification_sent": (
            "📧 Notificación ya enviada"
        ),
        "restricted_delivery": (
            "📧 El envío está reservado para alertas "
            "altas y críticas."
        ),
        "send_email": "📧 Enviar alerta por correo",
        "sending_alert": "Enviando alerta...",
        "alert_sent": "Alerta enviada por correo.",
        "already_sent": (
            "Esta alerta ya fue enviada por correo."
        ),
        "send_failed": "Error al enviar la alerta",
        "resolve": "✅ Marcar como resuelta",
        "resolved": "Alerta resuelta.",
        "already_resolved": (
            "La alerta ya fue resuelta."
        ),
        "integration_health": (
            "### 🩺 Estado de las integraciones"
        ),
        "integration_details": (
            "Detalles técnicos de las integraciones"
        ),
        "partial_health": (
            "El estado está parcialmente indisponible."
        ),
        "health_failed": (
            "No se pudo cargar el estado de las integraciones"
        ),
        "webhook_events": (
            "### 📨 Eventos del webhook de Resend"
        ),
        "events_unavailable": (
            "Los eventos no están disponibles."
        ),
        "no_webhook_events": (
            "No se encontraron eventos del webhook "
            "en este período."
        ),
        "export_webhook": (
            "⬇️ Exportar eventos del webhook en CSV"
        ),
        "notification_audit": (
            "### Auditoría de notificaciones"
        ),
        "notifications_load_failed": (
            "No se pudieron cargar las notificaciones."
        ),
        "no_notifications": (
            "No hay notificaciones registradas."
        ),
        "export_notifications": (
            "⬇️ Exportar notificaciones en CSV"
        ),
        "retry_section": (
            "### 🔄 Reenvío de notificaciones"
        ),
        "no_retry": (
            "No hay notificaciones disponibles para reenviar."
        ),
        "no_failed_retry": (
            "No hay notificaciones fallidas "
            "pendientes de reenvío."
        ),
        "retry_limit": (
            "El reenvío está limitado a tres intentos "
            "por notificación."
        ),
        "retry": "🔄 Reenviar",
        "retrying": "Reenviando notificación...",
        "retry_success": "Notificación reenviada.",
        "retry_failed": "Error en el reenvío.",
        "alerts_audit": "### Auditoría de alertas",
        "export_alerts": "⬇️ Exportar alertas en CSV",
    },
    "fr": {
        "section_title": (
            "## 🚨 Alertes de coût et de performance"
        ),
        "evaluate_now": "🔎 Évaluer les alertes",
        "evaluation_failed": (
            "L’évaluation n’a pas pu être terminée."
        ),
        "load_failed": (
            "Impossible de charger les alertes."
        ),
        "no_alerts": (
            "Aucune alerte trouvée pour le filtre actuel."
        ),
        "alerts_list": "### Liste des alertes",
        "email_disabled": (
            "Les notifications par e-mail sont désactivées."
        ),
        "recipient_missing": (
            "Le destinataire des alertes n’est pas configuré."
        ),
        "resend_missing": (
            "L’intégration Resend n’est pas configurée."
        ),
        "email_enabled": (
            "Les notifications par e-mail sont activées. "
            "Les alertes élevées et critiques peuvent être envoyées."
        ),
        "recommendation": "Recommandation",
        "notification_sent": (
            "📧 Notification déjà envoyée"
        ),
        "restricted_delivery": (
            "📧 Envoi réservé aux alertes élevées et critiques."
        ),
        "send_email": "📧 Envoyer l’alerte par e-mail",
        "sending_alert": "Envoi de l’alerte...",
        "alert_sent": "Alerte envoyée par e-mail.",
        "already_sent": (
            "Cette alerte a déjà été envoyée par e-mail."
        ),
        "send_failed": "Échec de l’envoi de l’alerte",
        "resolve": "✅ Marquer comme résolue",
        "resolved": "Alerte résolue.",
        "already_resolved": (
            "L’alerte est déjà résolue."
        ),
        "integration_health": (
            "### 🩺 État des intégrations"
        ),
        "integration_details": (
            "Détails techniques des intégrations"
        ),
        "partial_health": (
            "L’état est partiellement indisponible."
        ),
        "health_failed": (
            "Impossible de charger l’état des intégrations"
        ),
        "webhook_events": (
            "### 📨 Événements webhook Resend"
        ),
        "events_unavailable": (
            "Les événements sont indisponibles."
        ),
        "no_webhook_events": (
            "Aucun événement webhook trouvé pour cette période."
        ),
        "export_webhook": (
            "⬇️ Exporter les événements webhook en CSV"
        ),
        "notification_audit": (
            "### Audit des notifications"
        ),
        "notifications_load_failed": (
            "Impossible de charger les notifications."
        ),
        "no_notifications": (
            "Aucune notification enregistrée."
        ),
        "export_notifications": (
            "⬇️ Exporter les notifications en CSV"
        ),
        "retry_section": (
            "### 🔄 Renvoi des notifications"
        ),
        "no_retry": (
            "Aucune notification disponible pour un renvoi."
        ),
        "no_failed_retry": (
            "Aucune notification en échec n’attend un renvoi."
        ),
        "retry_limit": (
            "Le renvoi est limité à trois tentatives "
            "par notification."
        ),
        "retry": "🔄 Renvoyer",
        "retrying": "Renvoi de la notification...",
        "retry_success": "Notification renvoyée.",
        "retry_failed": "Échec du renvoi.",
        "alerts_audit": "### Audit des alertes",
        "export_alerts": "⬇️ Exporter les alertes en CSV",
    },
    "de": {
        "section_title": (
            "## 🚨 Kosten- und Leistungswarnungen"
        ),
        "evaluate_now": "🔎 Warnungen jetzt prüfen",
        "evaluation_failed": (
            "Die Auswertung konnte nicht abgeschlossen werden."
        ),
        "load_failed": (
            "Warnungen konnten nicht geladen werden."
        ),
        "no_alerts": (
            "Für den aktuellen Filter wurden "
            "keine Warnungen gefunden."
        ),
        "alerts_list": "### Warnungsliste",
        "email_disabled": (
            "E-Mail-Benachrichtigungen sind deaktiviert."
        ),
        "recipient_missing": (
            "Der Empfänger der Warnungen ist nicht konfiguriert."
        ),
        "resend_missing": (
            "Die Resend-Integration ist nicht konfiguriert."
        ),
        "email_enabled": (
            "E-Mail-Benachrichtigungen sind aktiviert. "
            "Hohe und kritische Warnungen können gesendet werden."
        ),
        "recommendation": "Empfehlung",
        "notification_sent": (
            "📧 Benachrichtigung bereits gesendet"
        ),
        "restricted_delivery": (
            "📧 Versand nur für hohe und kritische Warnungen."
        ),
        "send_email": "📧 Warnung per E-Mail senden",
        "sending_alert": "Warnung wird gesendet...",
        "alert_sent": "Warnung per E-Mail gesendet.",
        "already_sent": (
            "Diese Warnung wurde bereits per E-Mail gesendet."
        ),
        "send_failed": "Fehler beim Senden der Warnung",
        "resolve": "✅ Als gelöst markieren",
        "resolved": "Warnung gelöst.",
        "already_resolved": (
            "Die Warnung wurde bereits gelöst."
        ),
        "integration_health": (
            "### 🩺 Integrationsstatus"
        ),
        "integration_details": (
            "Technische Details der Integrationen"
        ),
        "partial_health": (
            "Der Status ist teilweise nicht verfügbar."
        ),
        "health_failed": (
            "Integrationsstatus konnte nicht geladen werden"
        ),
        "webhook_events": (
            "### 📨 Resend-Webhook-Ereignisse"
        ),
        "events_unavailable": (
            "Ereignisse sind nicht verfügbar."
        ),
        "no_webhook_events": (
            "Für diesen Zeitraum wurden "
            "keine Webhook-Ereignisse gefunden."
        ),
        "export_webhook": (
            "⬇️ Webhook-Ereignisse als CSV exportieren"
        ),
        "notification_audit": (
            "### Benachrichtigungsprüfung"
        ),
        "notifications_load_failed": (
            "Benachrichtigungen konnten nicht geladen werden."
        ),
        "no_notifications": (
            "Keine Benachrichtigungen vorhanden."
        ),
        "export_notifications": (
            "⬇️ Benachrichtigungen als CSV exportieren"
        ),
        "retry_section": (
            "### 🔄 Benachrichtigungen erneut senden"
        ),
        "no_retry": (
            "Keine Benachrichtigung zum erneuten Senden verfügbar."
        ),
        "no_failed_retry": (
            "Keine fehlgeschlagenen Benachrichtigungen "
            "warten auf einen erneuten Versand."
        ),
        "retry_limit": (
            "Der erneute Versand ist auf drei Versuche "
            "pro Benachrichtigung begrenzt."
        ),
        "retry": "🔄 Erneut senden",
        "retrying": "Benachrichtigung wird erneut gesendet...",
        "retry_success": "Benachrichtigung erneut gesendet.",
        "retry_failed": "Erneuter Versand fehlgeschlagen.",
        "alerts_audit": "### Warnungsprüfung",
        "export_alerts": "⬇️ Warnungen als CSV exportieren",
    },
    "ru": {
        "section_title": (
            "## 🚨 Оповещения о стоимости и производительности"
        ),
        "evaluate_now": "🔎 Проверить оповещения",
        "evaluation_failed": (
            "Не удалось завершить проверку."
        ),
        "load_failed": (
            "Не удалось загрузить оповещения."
        ),
        "no_alerts": (
            "Для текущего фильтра оповещения не найдены."
        ),
        "alerts_list": "### Список оповещений",
        "email_disabled": (
            "Уведомления по электронной почте отключены."
        ),
        "recipient_missing": (
            "Получатель оповещений не настроен."
        ),
        "resend_missing": (
            "Интеграция Resend не настроена."
        ),
        "email_enabled": (
            "Уведомления по электронной почте включены. "
            "Можно отправлять важные и критические оповещения."
        ),
        "recommendation": "Рекомендация",
        "notification_sent": (
            "📧 Уведомление уже отправлено"
        ),
        "restricted_delivery": (
            "📧 Отправка доступна для важных "
            "и критических оповещений."
        ),
        "send_email": (
            "📧 Отправить оповещение по электронной почте"
        ),
        "sending_alert": "Отправка оповещения...",
        "alert_sent": (
            "Оповещение отправлено по электронной почте."
        ),
        "already_sent": (
            "Это оповещение уже было отправлено."
        ),
        "send_failed": (
            "Не удалось отправить оповещение"
        ),
        "resolve": "✅ Отметить как решенное",
        "resolved": "Оповещение решено.",
        "already_resolved": (
            "Оповещение уже было решено."
        ),
        "integration_health": (
            "### 🩺 Состояние интеграций"
        ),
        "integration_details": (
            "Технические сведения об интеграциях"
        ),
        "partial_health": (
            "Сведения о состоянии доступны частично."
        ),
        "health_failed": (
            "Не удалось загрузить состояние интеграций"
        ),
        "webhook_events": (
            "### 📨 События webhook Resend"
        ),
        "events_unavailable": (
            "События недоступны."
        ),
        "no_webhook_events": (
            "За этот период события webhook не найдены."
        ),
        "export_webhook": (
            "⬇️ Экспортировать события webhook в CSV"
        ),
        "notification_audit": (
            "### Аудит уведомлений"
        ),
        "notifications_load_failed": (
            "Не удалось загрузить уведомления."
        ),
        "no_notifications": (
            "Уведомления не зарегистрированы."
        ),
        "export_notifications": (
            "⬇️ Экспортировать уведомления в CSV"
        ),
        "retry_section": (
            "### 🔄 Повторная отправка уведомлений"
        ),
        "no_retry": (
            "Нет уведомлений для повторной отправки."
        ),
        "no_failed_retry": (
            "Нет неудачных уведомлений, ожидающих "
            "повторной отправки."
        ),
        "retry_limit": (
            "Повторная отправка ограничена тремя попытками "
            "для каждого уведомления."
        ),
        "retry": "🔄 Отправить повторно",
        "retrying": "Повторная отправка уведомления...",
        "retry_success": "Уведомление отправлено повторно.",
        "retry_failed": (
            "Не удалось повторно отправить уведомление."
        ),
        "alerts_audit": "### Аудит оповещений",
        "export_alerts": (
            "⬇️ Экспортировать оповещения в CSV"
        ),
    },
}


LLM_ALERT_SECTION_TEXTS.update(
    {
        "it": {
            "section_title": (
                "## 🚨 Avvisi su costi e prestazioni"
            ),
            "evaluate_now": "🔎 Valuta gli avvisi ora",
            "evaluation_failed": (
                "Impossibile completare la valutazione."
            ),
            "load_failed": (
                "Impossibile caricare gli avvisi."
            ),
            "no_alerts": (
                "Nessun avviso trovato per il filtro attuale."
            ),
            "alerts_list": "### Elenco degli avvisi",
            "email_disabled": (
                "Le notifiche e-mail sono disabilitate "
                "in questo ambiente."
            ),
            "recipient_missing": (
                "Il destinatario degli avvisi "
                "non è configurato."
            ),
            "resend_missing": (
                "L’integrazione Resend non è configurata."
            ),
            "email_enabled": (
                "Le notifiche e-mail sono abilitate. "
                "Gli avvisi alti e critici possono "
                "essere inviati."
            ),
            "recommendation": "Raccomandazione",
            "notification_sent": (
                "📧 Notifica già inviata"
            ),
            "restricted_delivery": (
                "📧 L’invio è riservato agli avvisi "
                "alti e critici."
            ),
            "send_email": (
                "📧 Invia avviso tramite e-mail"
            ),
            "sending_alert": "Invio dell’avviso...",
            "alert_sent": (
                "Avviso inviato tramite e-mail."
            ),
            "already_sent": (
                "Questo avviso è già stato inviato "
                "tramite e-mail."
            ),
            "send_failed": (
                "Invio dell’avviso non riuscito"
            ),
            "resolve": "✅ Segna come risolto",
            "resolved": "Avviso risolto.",
            "already_resolved": (
                "L’avviso è già stato risolto."
            ),
            "integration_health": (
                "### 🩺 Stato delle integrazioni"
            ),
            "integration_details": (
                "Dettagli tecnici delle integrazioni"
            ),
            "partial_health": (
                "Lo stato delle integrazioni è "
                "parzialmente non disponibile."
            ),
            "health_failed": (
                "Impossibile caricare lo stato "
                "delle integrazioni"
            ),
            "webhook_events": (
                "### 📨 Eventi webhook di Resend"
            ),
            "events_unavailable": (
                "Gli eventi non sono disponibili."
            ),
            "no_webhook_events": (
                "Nessun evento webhook trovato "
                "in questo periodo."
            ),
            "export_webhook": (
                "⬇️ Esporta gli eventi webhook in CSV"
            ),
            "notification_audit": (
                "### Audit delle notifiche"
            ),
            "notifications_load_failed": (
                "Impossibile caricare le notifiche."
            ),
            "no_notifications": (
                "Nessuna notifica registrata."
            ),
            "export_notifications": (
                "⬇️ Esporta le notifiche in CSV"
            ),
            "retry_section": (
                "### 🔄 Nuovo invio delle notifiche"
            ),
            "no_retry": (
                "Nessuna notifica disponibile "
                "per un nuovo invio."
            ),
            "no_failed_retry": (
                "Non ci sono notifiche non riuscite "
                "in attesa di un nuovo invio."
            ),
            "retry_limit": (
                "Il nuovo invio è limitato a tre "
                "tentativi per notifica."
            ),
            "retry": "🔄 Invia nuovamente",
            "retrying": (
                "Nuovo invio della notifica..."
            ),
            "retry_success": (
                "Notifica inviata nuovamente."
            ),
            "retry_failed": (
                "Nuovo invio non riuscito."
            ),
            "alerts_audit": "### Audit degli avvisi",
            "export_alerts": (
                "⬇️ Esporta gli avvisi in CSV"
            ),
        },
        "ro": {
            "section_title": (
                "## 🚨 Alerte de cost și performanță"
            ),
            "evaluate_now": (
                "🔎 Evaluează alertele acum"
            ),
            "evaluation_failed": (
                "Evaluarea nu a putut fi finalizată."
            ),
            "load_failed": (
                "Alertele nu au putut fi încărcate."
            ),
            "no_alerts": (
                "Nu au fost găsite alerte pentru "
                "filtrul actual."
            ),
            "alerts_list": "### Lista alertelor",
            "email_disabled": (
                "Notificările prin e-mail sunt "
                "dezactivate în acest mediu."
            ),
            "recipient_missing": (
                "Destinatarul alertelor nu este configurat."
            ),
            "resend_missing": (
                "Integrarea Resend nu este configurată."
            ),
            "email_enabled": (
                "Notificările prin e-mail sunt activate. "
                "Alertele ridicate și critice pot fi trimise."
            ),
            "recommendation": "Recomandare",
            "notification_sent": (
                "📧 Notificare deja trimisă"
            ),
            "restricted_delivery": (
                "📧 Trimiterea este rezervată alertelor "
                "ridicate și critice."
            ),
            "send_email": (
                "📧 Trimite alerta prin e-mail"
            ),
            "sending_alert": "Se trimite alerta...",
            "alert_sent": (
                "Alerta a fost trimisă prin e-mail."
            ),
            "already_sent": (
                "Această alertă a fost deja trimisă "
                "prin e-mail."
            ),
            "send_failed": (
                "Trimiterea alertei a eșuat"
            ),
            "resolve": "✅ Marchează ca rezolvată",
            "resolved": "Alertă rezolvată.",
            "already_resolved": (
                "Alerta a fost deja rezolvată."
            ),
            "integration_health": (
                "### 🩺 Starea integrărilor"
            ),
            "integration_details": (
                "Detalii tehnice ale integrărilor"
            ),
            "partial_health": (
                "Starea integrărilor este disponibilă "
                "doar parțial."
            ),
            "health_failed": (
                "Starea integrărilor nu a putut fi încărcată"
            ),
            "webhook_events": (
                "### 📨 Evenimente webhook Resend"
            ),
            "events_unavailable": (
                "Evenimentele nu sunt disponibile."
            ),
            "no_webhook_events": (
                "Nu au fost găsite evenimente webhook "
                "în această perioadă."
            ),
            "export_webhook": (
                "⬇️ Exportă evenimentele webhook în CSV"
            ),
            "notification_audit": (
                "### Auditul notificărilor"
            ),
            "notifications_load_failed": (
                "Notificările nu au putut fi încărcate."
            ),
            "no_notifications": (
                "Nu există notificări înregistrate."
            ),
            "export_notifications": (
                "⬇️ Exportă notificările în CSV"
            ),
            "retry_section": (
                "### 🔄 Retrimiterea notificărilor"
            ),
            "no_retry": (
                "Nu există notificări disponibile "
                "pentru retrimitere."
            ),
            "no_failed_retry": (
                "Nu există notificări eșuate "
                "în așteptarea retrimiterii."
            ),
            "retry_limit": (
                "Retrimiterea este limitată la trei "
                "încercări pentru fiecare notificare."
            ),
            "retry": "🔄 Retrimite",
            "retrying": (
                "Se retrimite notificarea..."
            ),
            "retry_success": (
                "Notificarea a fost retrimisă."
            ),
            "retry_failed": "Retrimiterea a eșuat.",
            "alerts_audit": "### Auditul alertelor",
            "export_alerts": (
                "⬇️ Exportă alertele în CSV"
            ),
        },
        "ua": {
            "section_title": (
                "## 🚨 Сповіщення про вартість "
                "і продуктивність"
            ),
            "evaluate_now": (
                "🔎 Перевірити сповіщення"
            ),
            "evaluation_failed": (
                "Не вдалося завершити перевірку."
            ),
            "load_failed": (
                "Не вдалося завантажити сповіщення."
            ),
            "no_alerts": (
                "Для поточного фільтра сповіщень "
                "не знайдено."
            ),
            "alerts_list": "### Список сповіщень",
            "email_disabled": (
                "Сповіщення електронною поштою "
                "в цьому середовищі вимкнено."
            ),
            "recipient_missing": (
                "Одержувача сповіщень не налаштовано."
            ),
            "resend_missing": (
                "Інтеграцію Resend не налаштовано."
            ),
            "email_enabled": (
                "Сповіщення електронною поштою ввімкнено. "
                "Важливі та критичні сповіщення "
                "можна надсилати."
            ),
            "recommendation": "Рекомендація",
            "notification_sent": (
                "📧 Сповіщення вже надіслано"
            ),
            "restricted_delivery": (
                "📧 Надсилання доступне для важливих "
                "і критичних сповіщень."
            ),
            "send_email": (
                "📧 Надіслати сповіщення електронною поштою"
            ),
            "sending_alert": (
                "Надсилання сповіщення..."
            ),
            "alert_sent": (
                "Сповіщення надіслано електронною поштою."
            ),
            "already_sent": (
                "Це сповіщення вже було надіслано."
            ),
            "send_failed": (
                "Не вдалося надіслати сповіщення"
            ),
            "resolve": (
                "✅ Позначити як вирішене"
            ),
            "resolved": "Сповіщення вирішено.",
            "already_resolved": (
                "Сповіщення вже було вирішено."
            ),
            "integration_health": (
                "### 🩺 Стан інтеграцій"
            ),
            "integration_details": (
                "Технічні відомості про інтеграції"
            ),
            "partial_health": (
                "Відомості про стан інтеграцій "
                "доступні частково."
            ),
            "health_failed": (
                "Не вдалося завантажити стан інтеграцій"
            ),
            "webhook_events": (
                "### 📨 Події webhook Resend"
            ),
            "events_unavailable": (
                "Події недоступні."
            ),
            "no_webhook_events": (
                "За цей період подій webhook не знайдено."
            ),
            "export_webhook": (
                "⬇️ Експортувати події webhook у CSV"
            ),
            "notification_audit": (
                "### Аудит сповіщень"
            ),
            "notifications_load_failed": (
                "Не вдалося завантажити сповіщення."
            ),
            "no_notifications": (
                "Сповіщень не зареєстровано."
            ),
            "export_notifications": (
                "⬇️ Експортувати сповіщення у CSV"
            ),
            "retry_section": (
                "### 🔄 Повторне надсилання сповіщень"
            ),
            "no_retry": (
                "Немає сповіщень для повторного надсилання."
            ),
            "no_failed_retry": (
                "Немає невдалих сповіщень, які очікують "
                "повторного надсилання."
            ),
            "retry_limit": (
                "Повторне надсилання обмежено трьома "
                "спробами для кожного сповіщення."
            ),
            "retry": "🔄 Надіслати повторно",
            "retrying": (
                "Повторне надсилання сповіщення..."
            ),
            "retry_success": (
                "Сповіщення надіслано повторно."
            ),
            "retry_failed": (
                "Не вдалося повторно надіслати сповіщення."
            ),
            "alerts_audit": (
                "### Аудит системних сповіщень"
            ),
            "export_alerts": (
                "⬇️ Експортувати сповіщення у CSV"
            ),
        },
        "sa": {
            "section_title": (
                "## 🚨 تنبيهات التكلفة والأداء"
            ),
            "evaluate_now": (
                "🔎 تقييم التنبيهات الآن"
            ),
            "evaluation_failed": (
                "تعذر إكمال التقييم."
            ),
            "load_failed": (
                "تعذر تحميل التنبيهات."
            ),
            "no_alerts": (
                "لم يتم العثور على تنبيهات "
                "للتصفية الحالية."
            ),
            "alerts_list": "### قائمة التنبيهات",
            "email_disabled": (
                "إشعارات البريد الإلكتروني معطلة "
                "في هذه البيئة."
            ),
            "recipient_missing": (
                "مستلم التنبيهات غير مهيأ."
            ),
            "resend_missing": (
                "تكامل Resend غير مهيأ."
            ),
            "email_enabled": (
                "إشعارات البريد الإلكتروني مفعلة. "
                "يمكن إرسال التنبيهات العالية والحرجة."
            ),
            "recommendation": "التوصية",
            "notification_sent": (
                "📧 تم إرسال الإشعار مسبقًا"
            ),
            "restricted_delivery": (
                "📧 الإرسال مخصص للتنبيهات "
                "العالية والحرجة."
            ),
            "send_email": (
                "📧 إرسال التنبيه بالبريد الإلكتروني"
            ),
            "sending_alert": "جارٍ إرسال التنبيه...",
            "alert_sent": (
                "تم إرسال التنبيه بالبريد الإلكتروني."
            ),
            "already_sent": (
                "تم إرسال هذا التنبيه مسبقًا "
                "بالبريد الإلكتروني."
            ),
            "send_failed": (
                "فشل إرسال التنبيه"
            ),
            "resolve": (
                "✅ وضع علامة تم الحل"
            ),
            "resolved": "تم حل التنبيه.",
            "already_resolved": (
                "تم حل التنبيه مسبقًا."
            ),
            "integration_health": (
                "### 🩺 حالة عمليات التكامل"
            ),
            "integration_details": (
                "التفاصيل التقنية لعمليات التكامل"
            ),
            "partial_health": (
                "معلومات الحالة متاحة جزئيًا."
            ),
            "health_failed": (
                "تعذر تحميل حالة عمليات التكامل"
            ),
            "webhook_events": (
                "### 📨 أحداث webhook الخاصة بـ Resend"
            ),
            "events_unavailable": (
                "الأحداث غير متاحة."
            ),
            "no_webhook_events": (
                "لم يتم العثور على أحداث webhook "
                "في هذه الفترة."
            ),
            "export_webhook": (
                "⬇️ تصدير أحداث webhook بصيغة CSV"
            ),
            "notification_audit": (
                "### تدقيق الإشعارات"
            ),
            "notifications_load_failed": (
                "تعذر تحميل الإشعارات."
            ),
            "no_notifications": (
                "لا توجد إشعارات مسجلة."
            ),
            "export_notifications": (
                "⬇️ تصدير الإشعارات بصيغة CSV"
            ),
            "retry_section": (
                "### 🔄 إعادة إرسال الإشعارات"
            ),
            "no_retry": (
                "لا توجد إشعارات متاحة لإعادة الإرسال."
            ),
            "no_failed_retry": (
                "لا توجد إشعارات فاشلة "
                "بانتظار إعادة الإرسال."
            ),
            "retry_limit": (
                "إعادة الإرسال محدودة بثلاث محاولات "
                "لكل إشعار."
            ),
            "retry": "🔄 إعادة الإرسال",
            "retrying": (
                "جارٍ إعادة إرسال الإشعار..."
            ),
            "retry_success": (
                "تمت إعادة إرسال الإشعار."
            ),
            "retry_failed": (
                "فشلت إعادة إرسال الإشعار."
            ),
            "alerts_audit": "### تدقيق التنبيهات",
            "export_alerts": (
                "⬇️ تصدير التنبيهات بصيغة CSV"
            ),
        },
    }
)


# Idiomas que ainda não possuem bloco especializado usam
# inglês como fallback visual, sem afetar os dados internos.
for language_key in (
    "en_gb",
):
    LLM_ALERT_SECTION_TEXTS.setdefault(
        language_key,
        LLM_ALERT_SECTION_TEXTS["en_us"],
    )

LLM_ALERT_SECTION_TEXTS["ch"] = (
    LLM_ALERT_SECTION_TEXTS["de"]
)



LLM_ALERT_SECTION_DYNAMIC_TEXTS = {
    "pt": {
        "section_caption": (
            "Alertas persistentes de orçamento, projeção, "
            "tokens, falhas e latência."
        ),
        "evaluation_completed": "Avaliação concluída.",
        "detected": "Detectados",
        "saved": "Salvos",
        "duplicates": "Duplicados",
        "critical": "Críticos",
        "high": "Altos",
        "medium": "Médios",
        "open": "Abertos",
        "recommendation_label": "Recomendação",
        "code_label": "Código",
        "category_label": "Categoria",
        "send_criteria_failed": (
            "O alerta não atende aos critérios de envio."
        ),
        "database": "Banco de dados",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Conectado",
        "unavailable": "🔴 Indisponível",
        "configured": "🟢 Configurado",
        "not_configured": "🔴 Não configurado",
        "events_24h": "Eventos nas últimas 24h",
        "last_event": "Último evento",
        "last_email_delivered": "Último e-mail entregue em",
        "configured_recipient": "Destinatário configurado",
        "events_period": "Período dos eventos",
        "events_24_hours": "Últimas 24 horas",
        "events_7_days": "Últimos 7 dias",
        "all_history": "Todo o histórico",
        "notifications": "Notificações",
        "sent_plural": "Enviadas",
        "delivered_plural": "Entregues",
        "waiting_plural": "Aguardando",
        "delivery_rate": "Taxa de entrega",
        "delivery_status_filter": "Status de entrega",
        "recipient_filter": "Filtrar destinatário",
        "all": "Todos",
        "notification_label": "Notificação",
        "alert_label": "Alerta",
        "status_label": "Status",
        "attempts_label": "Tentativas",
        "recipient_label": "Destinatário",
        "health_error": (
            "Não foi possível carregar a saúde "
            "das integrações: {error}"
        ),
        "send_error": "Falha ao enviar o alerta: {error}",
    },
    "en_us": {
        "section_caption": (
            "Persistent alerts for budget, projection, "
            "tokens, failures, and latency."
        ),
        "evaluation_completed": "Evaluation completed.",
        "detected": "Detected",
        "saved": "Saved",
        "duplicates": "Duplicates",
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "open": "Open",
        "recommendation_label": "Recommendation",
        "code_label": "Code",
        "category_label": "Category",
        "send_criteria_failed": (
            "The alert does not meet the delivery criteria."
        ),
        "database": "Database",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Connected",
        "unavailable": "🔴 Unavailable",
        "configured": "🟢 Configured",
        "not_configured": "🔴 Not configured",
        "events_24h": "Events in the last 24 hours",
        "last_event": "Latest event",
        "last_email_delivered": "Latest email delivered at",
        "configured_recipient": "Configured recipient",
        "events_period": "Event period",
        "events_24_hours": "Last 24 hours",
        "events_7_days": "Last 7 days",
        "all_history": "All history",
        "notifications": "Notifications",
        "sent_plural": "Sent",
        "delivered_plural": "Delivered",
        "waiting_plural": "Waiting",
        "delivery_rate": "Delivery rate",
        "delivery_status_filter": "Delivery status",
        "recipient_filter": "Filter recipient",
        "all": "All",
        "notification_label": "Notification",
        "alert_label": "Alert",
        "status_label": "Status",
        "attempts_label": "Attempts",
        "recipient_label": "Recipient",
        "health_error": (
            "Could not load integration health: {error}"
        ),
        "send_error": "Failed to send the alert: {error}",
    },
    "es": {
        "section_caption": (
            "Alertas persistentes de presupuesto, proyección, "
            "tokens, fallos y latencia."
        ),
        "evaluation_completed": "Evaluación completada.",
        "detected": "Detectados",
        "saved": "Guardados",
        "duplicates": "Duplicados",
        "critical": "Críticos",
        "high": "Altos",
        "medium": "Medios",
        "open": "Abiertos",
        "recommendation_label": "Recomendación",
        "code_label": "Código",
        "category_label": "Categoría",
        "send_criteria_failed": (
            "La alerta no cumple los criterios de envío."
        ),
        "database": "Base de datos",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Conectado",
        "unavailable": "🔴 No disponible",
        "configured": "🟢 Configurado",
        "not_configured": "🔴 No configurado",
        "events_24h": "Eventos en las últimas 24 horas",
        "last_event": "Último evento",
        "last_email_delivered": "Último correo entregado",
        "configured_recipient": "Destinatario configurado",
        "events_period": "Período de eventos",
        "events_24_hours": "Últimas 24 horas",
        "events_7_days": "Últimos 7 días",
        "all_history": "Todo el historial",
        "notifications": "Notificaciones",
        "sent_plural": "Enviadas",
        "delivered_plural": "Entregadas",
        "waiting_plural": "En espera",
        "delivery_rate": "Tasa de entrega",
        "delivery_status_filter": "Estado de entrega",
        "recipient_filter": "Filtrar destinatario",
        "all": "Todos",
        "notification_label": "Notificación",
        "alert_label": "Alerta",
        "status_label": "Estado",
        "attempts_label": "Intentos",
        "recipient_label": "Destinatario",
        "health_error": (
            "No se pudo cargar el estado "
            "de las integraciones: {error}"
        ),
        "send_error": "Error al enviar la alerta: {error}",
    },
    "fr": {
        "section_caption": (
            "Alertes persistantes de budget, projection, "
            "jetons, échecs et latence."
        ),
        "evaluation_completed": "Évaluation terminée.",
        "detected": "Détectées",
        "saved": "Enregistrées",
        "duplicates": "Doublons",
        "critical": "Critiques",
        "high": "Élevées",
        "medium": "Moyennes",
        "open": "Ouvertes",
        "recommendation_label": "Recommandation",
        "code_label": "Code",
        "category_label": "Catégorie",
        "send_criteria_failed": (
            "L’alerte ne répond pas aux critères d’envoi."
        ),
        "database": "Base de données",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Connecté",
        "unavailable": "🔴 Indisponible",
        "configured": "🟢 Configuré",
        "not_configured": "🔴 Non configuré",
        "events_24h": "Événements des dernières 24 heures",
        "last_event": "Dernier événement",
        "last_email_delivered": "Dernier e-mail livré",
        "configured_recipient": "Destinataire configuré",
        "events_period": "Période des événements",
        "events_24_hours": "Dernières 24 heures",
        "events_7_days": "7 derniers jours",
        "all_history": "Tout l’historique",
        "notifications": "Notifications",
        "sent_plural": "Envoyées",
        "delivered_plural": "Livrées",
        "waiting_plural": "En attente",
        "delivery_rate": "Taux de livraison",
        "delivery_status_filter": "État de livraison",
        "recipient_filter": "Filtrer le destinataire",
        "all": "Tous",
        "notification_label": "Notification",
        "alert_label": "Alerte",
        "status_label": "État",
        "attempts_label": "Tentatives",
        "recipient_label": "Destinataire",
        "health_error": (
            "Impossible de charger l’état "
            "des intégrations : {error}"
        ),
        "send_error": "Échec de l’envoi de l’alerte : {error}",
    },
    "de": {
        "section_caption": (
            "Dauerhafte Warnungen für Budget, Prognose, "
            "Token, Fehler und Latenz."
        ),
        "evaluation_completed": "Auswertung abgeschlossen.",
        "detected": "Erkannt",
        "saved": "Gespeichert",
        "duplicates": "Duplikate",
        "critical": "Kritisch",
        "high": "Hoch",
        "medium": "Mittel",
        "open": "Offen",
        "recommendation_label": "Empfehlung",
        "code_label": "Code",
        "category_label": "Kategorie",
        "send_criteria_failed": (
            "Die Warnung erfüllt die Versandkriterien nicht."
        ),
        "database": "Datenbank",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Verbunden",
        "unavailable": "🔴 Nicht verfügbar",
        "configured": "🟢 Konfiguriert",
        "not_configured": "🔴 Nicht konfiguriert",
        "events_24h": "Ereignisse der letzten 24 Stunden",
        "last_event": "Letztes Ereignis",
        "last_email_delivered": "Letzte zugestellte E-Mail",
        "configured_recipient": "Konfigurierter Empfänger",
        "events_period": "Ereigniszeitraum",
        "events_24_hours": "Letzte 24 Stunden",
        "events_7_days": "Letzte 7 Tage",
        "all_history": "Gesamter Verlauf",
        "notifications": "Benachrichtigungen",
        "sent_plural": "Gesendet",
        "delivered_plural": "Zugestellt",
        "waiting_plural": "Ausstehend",
        "delivery_rate": "Zustellrate",
        "delivery_status_filter": "Zustellstatus",
        "recipient_filter": "Empfänger filtern",
        "all": "Alle",
        "notification_label": "Benachrichtigung",
        "alert_label": "Warnung",
        "status_label": "Status",
        "attempts_label": "Versuche",
        "recipient_label": "Empfänger",
        "health_error": (
            "Integrationsstatus konnte nicht geladen "
            "werden: {error}"
        ),
        "send_error": "Fehler beim Senden der Warnung: {error}",
    },
    "it": {
        "section_caption": (
            "Avvisi persistenti per budget, proiezione, "
            "token, errori e latenza."
        ),
        "evaluation_completed": "Valutazione completata.",
        "detected": "Rilevati",
        "saved": "Salvati",
        "duplicates": "Duplicati",
        "critical": "Critici",
        "high": "Alti",
        "medium": "Medi",
        "open": "Aperti",
        "recommendation_label": "Raccomandazione",
        "code_label": "Codice",
        "category_label": "Categoria",
        "send_criteria_failed": (
            "L’avviso non soddisfa i criteri di invio."
        ),
        "database": "Database",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Connesso",
        "unavailable": "🔴 Non disponibile",
        "configured": "🟢 Configurato",
        "not_configured": "🔴 Non configurato",
        "events_24h": "Eventi nelle ultime 24 ore",
        "last_event": "Ultimo evento",
        "last_email_delivered": "Ultima e-mail consegnata",
        "configured_recipient": "Destinatario configurato",
        "events_period": "Periodo degli eventi",
        "events_24_hours": "Ultime 24 ore",
        "events_7_days": "Ultimi 7 giorni",
        "all_history": "Tutta la cronologia",
        "notifications": "Notifiche",
        "sent_plural": "Inviate",
        "delivered_plural": "Consegnate",
        "waiting_plural": "In attesa",
        "delivery_rate": "Tasso di consegna",
        "delivery_status_filter": "Stato consegna",
        "recipient_filter": "Filtra destinatario",
        "all": "Tutti",
        "notification_label": "Notifica",
        "alert_label": "Avviso",
        "status_label": "Stato",
        "attempts_label": "Tentativi",
        "recipient_label": "Destinatario",
        "health_error": (
            "Impossibile caricare lo stato "
            "delle integrazioni: {error}"
        ),
        "send_error": "Invio dell’avviso non riuscito: {error}",
    },
    "ro": {
        "section_caption": (
            "Alerte persistente pentru buget, proiecție, "
            "tokenuri, erori și latență."
        ),
        "evaluation_completed": "Evaluare finalizată.",
        "detected": "Detectate",
        "saved": "Salvate",
        "duplicates": "Duplicate",
        "critical": "Critice",
        "high": "Ridicate",
        "medium": "Medii",
        "open": "Deschise",
        "recommendation_label": "Recomandare",
        "code_label": "Cod",
        "category_label": "Categorie",
        "send_criteria_failed": (
            "Alerta nu îndeplinește criteriile de trimitere."
        ),
        "database": "Bază de date",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Conectat",
        "unavailable": "🔴 Indisponibil",
        "configured": "🟢 Configurat",
        "not_configured": "🔴 Neconfigurat",
        "events_24h": "Evenimente în ultimele 24 de ore",
        "last_event": "Ultimul eveniment",
        "last_email_delivered": "Ultimul e-mail livrat",
        "configured_recipient": "Destinatar configurat",
        "events_period": "Perioada evenimentelor",
        "events_24_hours": "Ultimele 24 de ore",
        "events_7_days": "Ultimele 7 zile",
        "all_history": "Tot istoricul",
        "notifications": "Notificări",
        "sent_plural": "Trimise",
        "delivered_plural": "Livrate",
        "waiting_plural": "În așteptare",
        "delivery_rate": "Rată de livrare",
        "delivery_status_filter": "Starea livrării",
        "recipient_filter": "Filtrează destinatarul",
        "all": "Toate",
        "notification_label": "Notificare",
        "alert_label": "Alertă",
        "status_label": "Stare",
        "attempts_label": "Încercări",
        "recipient_label": "Destinatar",
        "health_error": (
            "Starea integrărilor nu a putut fi "
            "încărcată: {error}"
        ),
        "send_error": "Trimiterea alertei a eșuat: {error}",
    },
    "ua": {
        "section_caption": (
            "Постійні сповіщення щодо бюджету, прогнозу, "
            "токенів, помилок і затримки."
        ),
        "evaluation_completed": "Перевірку завершено.",
        "detected": "Виявлено",
        "saved": "Збережено",
        "duplicates": "Дублікати",
        "critical": "Критичні",
        "high": "Важливі",
        "medium": "Середні",
        "open": "Відкриті",
        "recommendation_label": "Рекомендація",
        "code_label": "Код",
        "category_label": "Категорія",
        "send_criteria_failed": (
            "Сповіщення не відповідає критеріям надсилання."
        ),
        "database": "База даних",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Підключено",
        "unavailable": "🔴 Недоступно",
        "configured": "🟢 Налаштовано",
        "not_configured": "🔴 Не налаштовано",
        "events_24h": "Події за останні 24 години",
        "last_event": "Остання подія",
        "last_email_delivered": "Останній доставлений лист",
        "configured_recipient": "Налаштований одержувач",
        "events_period": "Період подій",
        "events_24_hours": "Останні 24 години",
        "events_7_days": "Останні 7 днів",
        "all_history": "Уся історія",
        "notifications": "Сповіщення",
        "sent_plural": "Надіслані",
        "delivered_plural": "Доставлені",
        "waiting_plural": "Очікують",
        "delivery_rate": "Рівень доставки",
        "delivery_status_filter": "Статус доставки",
        "recipient_filter": "Фільтрувати одержувача",
        "all": "Усі",
        "notification_label": "Сповіщення",
        "alert_label": "Оповіщення",
        "status_label": "Статус",
        "attempts_label": "Спроби",
        "recipient_label": "Одержувач",
        "health_error": (
            "Не вдалося завантажити стан "
            "інтеграцій: {error}"
        ),
        "send_error": (
            "Не вдалося надіслати сповіщення: {error}"
        ),
    },
    "ru": {
        "section_caption": (
            "Постоянные оповещения о бюджете, прогнозе, "
            "токенах, ошибках и задержке."
        ),
        "evaluation_completed": "Проверка завершена.",
        "detected": "Обнаружено",
        "saved": "Сохранено",
        "duplicates": "Дубликаты",
        "critical": "Критические",
        "high": "Важные",
        "medium": "Средние",
        "open": "Открытые",
        "recommendation_label": "Рекомендация",
        "code_label": "Код",
        "category_label": "Категория",
        "send_criteria_failed": (
            "Оповещение не соответствует критериям отправки."
        ),
        "database": "База данных",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 Подключено",
        "unavailable": "🔴 Недоступно",
        "configured": "🟢 Настроено",
        "not_configured": "🔴 Не настроено",
        "events_24h": "События за последние 24 часа",
        "last_event": "Последнее событие",
        "last_email_delivered": "Последнее доставленное письмо",
        "configured_recipient": "Настроенный получатель",
        "events_period": "Период событий",
        "events_24_hours": "Последние 24 часа",
        "events_7_days": "Последние 7 дней",
        "all_history": "Вся история",
        "notifications": "Уведомления",
        "sent_plural": "Отправлены",
        "delivered_plural": "Доставлены",
        "waiting_plural": "Ожидают",
        "delivery_rate": "Процент доставки",
        "delivery_status_filter": "Статус доставки",
        "recipient_filter": "Фильтр получателя",
        "all": "Все",
        "notification_label": "Уведомление",
        "alert_label": "Оповещение",
        "status_label": "Статус",
        "attempts_label": "Попытки",
        "recipient_label": "Получатель",
        "health_error": (
            "Не удалось загрузить состояние "
            "интеграций: {error}"
        ),
        "send_error": (
            "Не удалось отправить оповещение: {error}"
        ),
    },
    "sa": {
        "section_caption": (
            "تنبيهات دائمة للميزانية والتوقعات والرموز "
            "والأخطاء وزمن الاستجابة."
        ),
        "evaluation_completed": "اكتمل التقييم.",
        "detected": "المكتشفة",
        "saved": "المحفوظة",
        "duplicates": "المكررة",
        "critical": "الحرجة",
        "high": "العالية",
        "medium": "المتوسطة",
        "open": "المفتوحة",
        "recommendation_label": "التوصية",
        "code_label": "الرمز",
        "category_label": "الفئة",
        "send_criteria_failed": (
            "لا يطابق التنبيه معايير الإرسال."
        ),
        "database": "قاعدة البيانات",
        "resend": "Resend",
        "webhook": "Webhook",
        "connected": "🟢 متصل",
        "unavailable": "🔴 غير متاح",
        "configured": "🟢 مهيأ",
        "not_configured": "🔴 غير مهيأ",
        "events_24h": "الأحداث خلال آخر 24 ساعة",
        "last_event": "آخر حدث",
        "last_email_delivered": "آخر بريد تم تسليمه",
        "configured_recipient": "المستلم المهيأ",
        "events_period": "فترة الأحداث",
        "events_24_hours": "آخر 24 ساعة",
        "events_7_days": "آخر 7 أيام",
        "all_history": "كل السجل",
        "notifications": "الإشعارات",
        "sent_plural": "المرسلة",
        "delivered_plural": "المسلّمة",
        "waiting_plural": "قيد الانتظار",
        "delivery_rate": "معدل التسليم",
        "delivery_status_filter": "حالة التسليم",
        "recipient_filter": "تصفية المستلم",
        "all": "الكل",
        "notification_label": "الإشعار",
        "alert_label": "التنبيه",
        "status_label": "الحالة",
        "attempts_label": "المحاولات",
        "recipient_label": "المستلم",
        "health_error": (
            "تعذر تحميل حالة عمليات التكامل: {error}"
        ),
        "send_error": "فشل إرسال التنبيه: {error}",
    },
}


LLM_ALERT_UNKNOWN_ERROR_TEXTS = {
    "pt": "erro desconhecido",
    "en_us": "unknown error",
    "es": "error desconocido",
    "fr": "erreur inconnue",
    "de": "unbekannter Fehler",
    "it": "errore sconosciuto",
    "ro": "eroare necunoscută",
    "ua": "невідома помилка",
    "ru": "неизвестная ошибка",
    "sa": "خطأ غير معروف",
}

for language_key, translated_text in (
    LLM_ALERT_UNKNOWN_ERROR_TEXTS.items()
):
    LLM_ALERT_SECTION_TEXTS.setdefault(
        language_key,
        {},
    )["unknown_error"] = translated_text


LLM_ALERT_SECTION_DYNAMIC_TEXTS["en_gb"] = (
    LLM_ALERT_SECTION_DYNAMIC_TEXTS["en_us"]
)

LLM_ALERT_SECTION_DYNAMIC_TEXTS["ch"] = (
    LLM_ALERT_SECTION_DYNAMIC_TEXTS["de"]
)

for language_key, dynamic_texts in (
    LLM_ALERT_SECTION_DYNAMIC_TEXTS.items()
):
    LLM_ALERT_SECTION_TEXTS.setdefault(
        language_key,
        {},
    ).update(dynamic_texts)




# LLM_COST_ALERT_VISUAL_I18N

# Complementos do catálogo de erro desconhecido.
LLM_ALERT_UNKNOWN_ERROR_TEXTS["en_gb"] = (
    LLM_ALERT_UNKNOWN_ERROR_TEXTS["en_us"]
)

# O código ch segue o alemão utilizado pelo projeto.
LLM_ALERT_UNKNOWN_ERROR_TEXTS["ch"] = (
    LLM_ALERT_UNKNOWN_ERROR_TEXTS["de"]
)


LLM_COST_ALERT_VISUAL_TEXTS = {
    "pt": {
        "alert_status": "Status dos alertas",
        "alert_limit": "Limite de alertas",
        "total": "Total",
        "low_plural": "Baixos",
        "open_option": "Aberto",
        "resolved_option": "Resolvido",
        "all_option": "Todos",
        "email_sent_plural": "E-mails enviados",
        "email_failures": "Falhas de e-mail",
        "status": "Status",
        "severity": "Severidade",
        "current_value": "Valor atual",
        "limit": "Limite",
        "unit": "Unidade",
        "created_at": "Criado em",
        "database": "Banco PostgreSQL",
        "email_alerts": "Alertas por e-mail",
        "enabled_plural": "🟢 Habilitados",
        "disabled_plural": "🟡 Desabilitados",
    },
    "en_us": {
        "alert_status": "Alert status",
        "alert_limit": "Alert limit",
        "total": "Total",
        "low_plural": "Low",
        "open_option": "Open",
        "resolved_option": "Resolved",
        "all_option": "All",
        "email_sent_plural": "Emails sent",
        "email_failures": "Email failures",
        "status": "Status",
        "severity": "Severity",
        "current_value": "Current value",
        "limit": "Limit",
        "unit": "Unit",
        "created_at": "Created at",
        "database": "PostgreSQL database",
        "email_alerts": "Email alerts",
        "enabled_plural": "🟢 Enabled",
        "disabled_plural": "🟡 Disabled",
    },
    "en_gb": {
        "alert_status": "Alert status",
        "alert_limit": "Alert limit",
        "total": "Total",
        "low_plural": "Low",
        "open_option": "Open",
        "resolved_option": "Resolved",
        "all_option": "All",
        "email_sent_plural": "Emails sent",
        "email_failures": "Email failures",
        "status": "Status",
        "severity": "Severity",
        "current_value": "Current value",
        "limit": "Limit",
        "unit": "Unit",
        "created_at": "Created at",
        "database": "PostgreSQL database",
        "email_alerts": "Email alerts",
        "enabled_plural": "🟢 Enabled",
        "disabled_plural": "🟡 Disabled",
    },
    "es": {
        "alert_status": "Estado de las alertas",
        "alert_limit": "Límite de alertas",
        "total": "Total",
        "low_plural": "Bajas",
        "open_option": "Abierta",
        "resolved_option": "Resuelta",
        "all_option": "Todas",
        "email_sent_plural": "Correos enviados",
        "email_failures": "Fallos de correo",
        "status": "Estado",
        "severity": "Severidad",
        "current_value": "Valor actual",
        "limit": "Límite",
        "unit": "Unidad",
        "created_at": "Creada el",
        "database": "Base de datos PostgreSQL",
        "email_alerts": "Alertas por correo",
        "enabled_plural": "🟢 Habilitadas",
        "disabled_plural": "🟡 Deshabilitadas",
    },
    "fr": {
        "alert_status": "État des alertes",
        "alert_limit": "Limite des alertes",
        "total": "Total",
        "low_plural": "Faibles",
        "open_option": "Ouverte",
        "resolved_option": "Résolue",
        "all_option": "Toutes",
        "email_sent_plural": "E-mails envoyés",
        "email_failures": "Échecs d’envoi",
        "status": "État",
        "severity": "Sévérité",
        "current_value": "Valeur actuelle",
        "limit": "Limite",
        "unit": "Unité",
        "created_at": "Créée le",
        "database": "Base PostgreSQL",
        "email_alerts": "Alertes par e-mail",
        "enabled_plural": "🟢 Activées",
        "disabled_plural": "🟡 Désactivées",
    },
    "de": {
        "alert_status": "Alarmstatus",
        "alert_limit": "Alarmlimit",
        "total": "Gesamt",
        "low_plural": "Niedrig",
        "open_option": "Offen",
        "resolved_option": "Gelöst",
        "all_option": "Alle",
        "email_sent_plural": "Gesendete E-Mails",
        "email_failures": "E-Mail-Fehler",
        "status": "Status",
        "severity": "Schweregrad",
        "current_value": "Aktueller Wert",
        "limit": "Grenzwert",
        "unit": "Einheit",
        "created_at": "Erstellt am",
        "database": "PostgreSQL-Datenbank",
        "email_alerts": "E-Mail-Alarme",
        "enabled_plural": "🟢 Aktiviert",
        "disabled_plural": "🟡 Deaktiviert",
    },
    "it": {
        "alert_status": "Stato degli avvisi",
        "alert_limit": "Limite degli avvisi",
        "total": "Totale",
        "low_plural": "Bassi",
        "open_option": "Aperto",
        "resolved_option": "Risolto",
        "all_option": "Tutti",
        "email_sent_plural": "E-mail inviate",
        "email_failures": "Errori e-mail",
        "status": "Stato",
        "severity": "Gravità",
        "current_value": "Valore attuale",
        "limit": "Limite",
        "unit": "Unità",
        "created_at": "Creato il",
        "database": "Database PostgreSQL",
        "email_alerts": "Avvisi e-mail",
        "enabled_plural": "🟢 Abilitati",
        "disabled_plural": "🟡 Disabilitati",
    },
    "ro": {
        "alert_status": "Starea alertelor",
        "alert_limit": "Limita alertelor",
        "total": "Total",
        "low_plural": "Scăzute",
        "open_option": "Deschisă",
        "resolved_option": "Rezolvată",
        "all_option": "Toate",
        "email_sent_plural": "E-mailuri trimise",
        "email_failures": "Erori de e-mail",
        "status": "Stare",
        "severity": "Severitate",
        "current_value": "Valoare actuală",
        "limit": "Limită",
        "unit": "Unitate",
        "created_at": "Creat la",
        "database": "Bază de date PostgreSQL",
        "email_alerts": "Alerte prin e-mail",
        "enabled_plural": "🟢 Activate",
        "disabled_plural": "🟡 Dezactivate",
    },
    "ua": {
        "alert_status": "Статус сповіщень",
        "alert_limit": "Ліміт сповіщень",
        "total": "Усього",
        "low_plural": "Низькі",
        "open_option": "Відкрите",
        "resolved_option": "Вирішене",
        "all_option": "Усі",
        "email_sent_plural": "Надіслані листи",
        "email_failures": "Помилки пошти",
        "status": "Статус",
        "severity": "Рівень",
        "current_value": "Поточне значення",
        "limit": "Ліміт",
        "unit": "Одиниця",
        "created_at": "Створено",
        "database": "База PostgreSQL",
        "email_alerts": "Сповіщення поштою",
        "enabled_plural": "🟢 Увімкнені",
        "disabled_plural": "🟡 Вимкнені",
    },
    "ru": {
        "alert_status": "Статус оповещений",
        "alert_limit": "Лимит оповещений",
        "total": "Всего",
        "low_plural": "Низкие",
        "open_option": "Открыто",
        "resolved_option": "Решено",
        "all_option": "Все",
        "email_sent_plural": "Отправленные письма",
        "email_failures": "Ошибки отправки",
        "status": "Статус",
        "severity": "Важность",
        "current_value": "Текущее значение",
        "limit": "Лимит",
        "unit": "Единица",
        "created_at": "Создано",
        "database": "База PostgreSQL",
        "email_alerts": "Оповещения по e-mail",
        "enabled_plural": "🟢 Включены",
        "disabled_plural": "🟡 Выключены",
    },
    "sa": {
        "alert_status": "حالة التنبيهات",
        "alert_limit": "حد التنبيهات",
        "total": "الإجمالي",
        "low_plural": "منخفضة",
        "open_option": "مفتوح",
        "resolved_option": "تم الحل",
        "all_option": "الكل",
        "email_sent_plural": "رسائل مرسلة",
        "email_failures": "أخطاء البريد",
        "status": "الحالة",
        "severity": "الخطورة",
        "current_value": "القيمة الحالية",
        "limit": "الحد",
        "unit": "الوحدة",
        "created_at": "تاريخ الإنشاء",
        "database": "قاعدة PostgreSQL",
        "email_alerts": "تنبيهات البريد",
        "enabled_plural": "🟢 مفعلة",
        "disabled_plural": "🟡 معطلة",
    },
}

LLM_COST_ALERT_VISUAL_TEXTS["ch"] = dict(
    LLM_COST_ALERT_VISUAL_TEXTS["de"]
)


def llm_cost_alert_visual_t(
    key: str,
    default: str | None = None,
) -> str:
    idioma = llm_table_lang()

    return LLM_COST_ALERT_VISUAL_TEXTS.get(
        idioma,
        LLM_COST_ALERT_VISUAL_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def formatar_status_filtro_alerta(
    value: str,
) -> str:
    mapping = {
        "aberto": "open_option",
        "resolvido": "resolved_option",
        "todos": "all_option",
    }

    return llm_cost_alert_visual_t(
        mapping.get(
            value,
            value,
        ),
        value,
    )


def llm_alert_section_t(
    key: str,
    default: str | None = None,
) -> str:
    idioma = llm_table_lang()

    return LLM_ALERT_SECTION_TEXTS.get(
        idioma,
        LLM_ALERT_SECTION_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )




# LLM_COST_ALERT_DYNAMIC_DISPLAY_I18N

def traduzir_status_alerta_visual(
    status: str,
) -> str:
    normalized = str(
        status or ""
    ).strip().lower()

    mapping = {
        "aberto": "open",
        "resolvido": "resolved",
        "fechado": "closed",
        "cancelado": "cancelled",
    }

    translation_key = mapping.get(
        normalized
    )

    if translation_key is None:
        return str(status)

    return llm_alert_t(
        translation_key,
        str(status),
    )


def traduzir_severidade_alerta_visual(
    severidade: str,
) -> str:
    normalized = str(
        severidade or ""
    ).strip().lower()

    mapping = {
        "informativa": "informational",
        "baixa": "low",
        "media": "medium",
        "média": "medium",
        "alta": "high",
        "critica": "critical",
        "crítica": "critical",
    }

    translation_key = mapping.get(
        normalized
    )

    if translation_key is None:
        return str(severidade)

    return llm_alert_t(
        translation_key,
        str(severidade),
    )



# LLM_COST_ALERT_CONTENT_DISPLAY_I18N

LLM_ALERT_CONTENT_TEXTS: dict[
    str,
    dict[str, dict[str, str]],
] = {
    "pt": {
        "orcamento_mensal": {
            "titulo": "Uso elevado do orçamento de LLM",
            "descricao": (
                "O consumo acumulado atingiu {percentual}% "
                "do orçamento mensal."
            ),
            "recomendacao": (
                "Revisar modelos, tamanho dos prompts, "
                "quantidade de chunks e cache."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Projeção mensal acima do esperado",
            "descricao": (
                "A projeção mensal de consumo está próxima "
                "ou acima do limite configurado."
            ),
            "recomendacao": (
                "Avaliar o uso de Gemini Flash-Lite, reduzir "
                "contexto e reutilizar resultados."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Chamadas de LLM com alta latência",
            "descricao": (
                "Foram detectadas {quantidade} chamada(s) "
                "acima de 30 segundos."
            ),
            "recomendacao": (
                "Verificar cold start, tamanho do prompt, "
                "rede e tempo de resposta do provedor."
            ),
            "categoria": "Desempenho",
        },
        "falhas_llm": {
            "titulo": "Falhas em chamadas de LLM",
            "descricao": (
                "Foram detectadas {quantidade} falha(s), "
                "equivalentes a {percentual}% das chamadas."
            ),
            "recomendacao": (
                "Analisar o tipo do erro, limites da API, "
                "credenciais e estratégia de fallback."
            ),
            "categoria": "Confiabilidade",
        },
        "tokens_elevados": {
            "titulo": "Média elevada de tokens por chamada",
            "descricao": (
                "A média de tokens por chamada atingiu "
                "{quantidade} tokens."
            ),
            "recomendacao": (
                "Reduzir histórico, prompt, chunks e "
                "documentos enviados ao modelo."
            ),
            "categoria": "Eficiência",
        },
    },
    "en_us": {
        "orcamento_mensal": {
            "titulo": "High LLM budget usage",
            "descricao": (
                "Accumulated usage reached {percentual}% "
                "of the monthly budget."
            ),
            "recomendacao": (
                "Review models, prompt sizes, chunk count, "
                "and caching."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Monthly projection above expectations",
            "descricao": (
                "The monthly usage projection is near or "
                "above the configured limit."
            ),
            "recomendacao": (
                "Consider Gemini Flash-Lite, reduce context, "
                "and reuse results."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "High-latency LLM calls",
            "descricao": (
                "{quantidade} call(s) exceeding 30 seconds "
                "were detected."
            ),
            "recomendacao": (
                "Check cold starts, prompt size, network, "
                "and provider response time."
            ),
            "categoria": "Performance",
        },
        "falhas_llm": {
            "titulo": "LLM call failures",
            "descricao": (
                "{quantidade} failure(s) were detected, "
                "representing {percentual}% of calls."
            ),
            "recomendacao": (
                "Review error types, API limits, credentials, "
                "and the fallback strategy."
            ),
            "categoria": "Reliability",
        },
        "tokens_elevados": {
            "titulo": "High average tokens per call",
            "descricao": (
                "Average token usage per call reached "
                "{quantidade} tokens."
            ),
            "recomendacao": (
                "Reduce history, prompts, chunks, and "
                "documents sent to the model."
            ),
            "categoria": "Efficiency",
        },
    },
    "en_gb": {
        "orcamento_mensal": {
            "titulo": "High LLM budget usage",
            "descricao": (
                "Accumulated usage reached {percentual}% "
                "of the monthly budget."
            ),
            "recomendacao": (
                "Review models, prompt sizes, chunk count, "
                "and caching."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Monthly projection above expectations",
            "descricao": (
                "The monthly usage projection is near or "
                "above the configured limit."
            ),
            "recomendacao": (
                "Consider Gemini Flash-Lite, reduce context, "
                "and reuse results."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "High-latency LLM calls",
            "descricao": (
                "{quantidade} call(s) exceeding 30 seconds "
                "were detected."
            ),
            "recomendacao": (
                "Check cold starts, prompt size, network, "
                "and provider response time."
            ),
            "categoria": "Performance",
        },
        "falhas_llm": {
            "titulo": "LLM call failures",
            "descricao": (
                "{quantidade} failure(s) were detected, "
                "representing {percentual}% of calls."
            ),
            "recomendacao": (
                "Review error types, API limits, credentials, "
                "and the fallback strategy."
            ),
            "categoria": "Reliability",
        },
        "tokens_elevados": {
            "titulo": "High average tokens per call",
            "descricao": (
                "Average token usage per call reached "
                "{quantidade} tokens."
            ),
            "recomendacao": (
                "Reduce history, prompts, chunks, and "
                "documents sent to the model."
            ),
            "categoria": "Efficiency",
        },
    },
    "es": {
        "orcamento_mensal": {
            "titulo": "Uso elevado del presupuesto de LLM",
            "descricao": (
                "El consumo acumulado alcanzó el {percentual}% "
                "del presupuesto mensual."
            ),
            "recomendacao": (
                "Revisar los modelos, el tamaño de los prompts, "
                "la cantidad de fragmentos y la caché."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Proyección mensual superior a lo esperado",
            "descricao": (
                "La proyección mensual de consumo está cerca "
                "o por encima del límite configurado."
            ),
            "recomendacao": (
                "Evaluar Gemini Flash-Lite, reducir el contexto "
                "y reutilizar resultados."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Llamadas de LLM con alta latencia",
            "descricao": (
                "Se detectaron {quantidade} llamada(s) de más "
                "de 30 segundos."
            ),
            "recomendacao": (
                "Comprobar el arranque en frío, el tamaño del "
                "prompt, la red y la respuesta del proveedor."
            ),
            "categoria": "Rendimiento",
        },
        "falhas_llm": {
            "titulo": "Fallos en llamadas de LLM",
            "descricao": (
                "Se detectaron {quantidade} fallo(s), equivalentes "
                "al {percentual}% de las llamadas."
            ),
            "recomendacao": (
                "Analizar los errores, límites de API, credenciales "
                "y la estrategia de respaldo."
            ),
            "categoria": "Confiabilidad",
        },
        "tokens_elevados": {
            "titulo": "Promedio elevado de tokens por llamada",
            "descricao": (
                "El promedio de tokens por llamada alcanzó "
                "{quantidade} tokens."
            ),
            "recomendacao": (
                "Reducir el historial, los prompts, los fragmentos "
                "y los documentos enviados al modelo."
            ),
            "categoria": "Eficiencia",
        },
    },
    "fr": {
        "orcamento_mensal": {
            "titulo": "Utilisation élevée du budget LLM",
            "descricao": (
                "La consommation cumulée a atteint {percentual}% "
                "du budget mensuel."
            ),
            "recomendacao": (
                "Vérifier les modèles, la taille des prompts, "
                "le nombre de segments et le cache."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Projection mensuelle supérieure aux attentes",
            "descricao": (
                "La projection mensuelle est proche ou supérieure "
                "à la limite configurée."
            ),
            "recomendacao": (
                "Envisager Gemini Flash-Lite, réduire le contexte "
                "et réutiliser les résultats."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Appels LLM à latence élevée",
            "descricao": (
                "{quantidade} appel(s) dépassant 30 secondes "
                "ont été détectés."
            ),
            "recomendacao": (
                "Vérifier le démarrage à froid, la taille du prompt, "
                "le réseau et le délai du fournisseur."
            ),
            "categoria": "Performance",
        },
        "falhas_llm": {
            "titulo": "Échecs des appels LLM",
            "descricao": (
                "{quantidade} échec(s) ont été détectés, soit "
                "{percentual}% des appels."
            ),
            "recomendacao": (
                "Analyser les erreurs, les limites de l’API, "
                "les identifiants et la stratégie de repli."
            ),
            "categoria": "Fiabilité",
        },
        "tokens_elevados": {
            "titulo": "Moyenne élevée de tokens par appel",
            "descricao": (
                "La moyenne de tokens par appel a atteint "
                "{quantidade} tokens."
            ),
            "recomendacao": (
                "Réduire l’historique, les prompts, les segments "
                "et les documents envoyés au modèle."
            ),
            "categoria": "Efficacité",
        },
    },
    "de": {
        "orcamento_mensal": {
            "titulo": "Hohe Nutzung des LLM-Budgets",
            "descricao": (
                "Die kumulierte Nutzung erreichte {percentual}% "
                "des Monatsbudgets."
            ),
            "recomendacao": (
                "Modelle, Promptgrößen, Chunk-Anzahl und Cache "
                "überprüfen."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Monatsprognose über den Erwartungen",
            "descricao": (
                "Die monatliche Verbrauchsprognose liegt nahe "
                "oder über dem konfigurierten Limit."
            ),
            "recomendacao": (
                "Gemini Flash-Lite prüfen, Kontext reduzieren "
                "und Ergebnisse wiederverwenden."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "LLM-Aufrufe mit hoher Latenz",
            "descricao": (
                "{quantidade} Aufruf(e) über 30 Sekunden "
                "wurden erkannt."
            ),
            "recomendacao": (
                "Kaltstarts, Promptgröße, Netzwerk und "
                "Antwortzeit des Anbieters prüfen."
            ),
            "categoria": "Leistung",
        },
        "falhas_llm": {
            "titulo": "Fehler bei LLM-Aufrufen",
            "descricao": (
                "{quantidade} Fehler wurden erkannt; dies "
                "entspricht {percentual}% der Aufrufe."
            ),
            "recomendacao": (
                "Fehlertypen, API-Limits, Zugangsdaten und "
                "Fallback-Strategie prüfen."
            ),
            "categoria": "Zuverlässigkeit",
        },
        "tokens_elevados": {
            "titulo": "Hoher Token-Durchschnitt pro Aufruf",
            "descricao": (
                "Der Token-Durchschnitt pro Aufruf erreichte "
                "{quantidade} Tokens."
            ),
            "recomendacao": (
                "Verlauf, Prompts, Chunks und an das Modell "
                "gesendete Dokumente reduzieren."
            ),
            "categoria": "Effizienz",
        },
    },
    "it": {
        "orcamento_mensal": {
            "titulo": "Utilizzo elevato del budget LLM",
            "descricao": (
                "Il consumo accumulato ha raggiunto il "
                "{percentual}% del budget mensile."
            ),
            "recomendacao": (
                "Rivedere modelli, dimensioni dei prompt, "
                "numero di chunk e cache."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Proiezione mensile superiore alle attese",
            "descricao": (
                "La proiezione mensile è vicina o superiore "
                "al limite configurato."
            ),
            "recomendacao": (
                "Valutare Gemini Flash-Lite, ridurre il contesto "
                "e riutilizzare i risultati."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Chiamate LLM ad alta latenza",
            "descricao": (
                "Sono state rilevate {quantidade} chiamata/e "
                "superiori a 30 secondi."
            ),
            "recomendacao": (
                "Verificare cold start, dimensione del prompt, "
                "rete e risposta del provider."
            ),
            "categoria": "Prestazioni",
        },
        "falhas_llm": {
            "titulo": "Errori nelle chiamate LLM",
            "descricao": (
                "Sono stati rilevati {quantidade} errore/i, pari "
                "al {percentual}% delle chiamate."
            ),
            "recomendacao": (
                "Analizzare errori, limiti API, credenziali "
                "e strategia di fallback."
            ),
            "categoria": "Affidabilità",
        },
        "tokens_elevados": {
            "titulo": "Media elevata di token per chiamata",
            "descricao": (
                "La media di token per chiamata ha raggiunto "
                "{quantidade} token."
            ),
            "recomendacao": (
                "Ridurre cronologia, prompt, chunk e documenti "
                "inviati al modello."
            ),
            "categoria": "Efficienza",
        },
    },
    "ro": {
        "orcamento_mensal": {
            "titulo": "Utilizare ridicată a bugetului LLM",
            "descricao": (
                "Consumul acumulat a atins {percentual}% "
                "din bugetul lunar."
            ),
            "recomendacao": (
                "Revizuiți modelele, dimensiunea prompturilor, "
                "numărul de fragmente și memoria cache."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Proiecție lunară peste așteptări",
            "descricao": (
                "Proiecția lunară este aproape sau peste "
                "limita configurată."
            ),
            "recomendacao": (
                "Evaluați Gemini Flash-Lite, reduceți contextul "
                "și reutilizați rezultatele."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Apeluri LLM cu latență ridicată",
            "descricao": (
                "Au fost detectate {quantidade} apel(uri) "
                "de peste 30 de secunde."
            ),
            "recomendacao": (
                "Verificați pornirea la rece, dimensiunea "
                "promptului, rețeaua și răspunsul furnizorului."
            ),
            "categoria": "Performanță",
        },
        "falhas_llm": {
            "titulo": "Eșecuri ale apelurilor LLM",
            "descricao": (
                "Au fost detectate {quantidade} eșec(uri), "
                "reprezentând {percentual}% din apeluri."
            ),
            "recomendacao": (
                "Analizați erorile, limitele API, acreditările "
                "și strategia de rezervă."
            ),
            "categoria": "Fiabilitate",
        },
        "tokens_elevados": {
            "titulo": "Medie ridicată de tokenuri pe apel",
            "descricao": (
                "Media de tokenuri pe apel a ajuns la "
                "{quantidade} tokenuri."
            ),
            "recomendacao": (
                "Reduceți istoricul, prompturile, fragmentele "
                "și documentele trimise modelului."
            ),
            "categoria": "Eficiență",
        },
    },
    "ua": {
        "orcamento_mensal": {
            "titulo": "Високе використання бюджету LLM",
            "descricao": (
                "Накопичене використання досягло {percentual}% "
                "місячного бюджету."
            ),
            "recomendacao": (
                "Перевірте моделі, розмір запитів, кількість "
                "фрагментів і кешування."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Місячний прогноз вищий за очікування",
            "descricao": (
                "Місячний прогноз використання наближається "
                "до встановленого ліміту або перевищує його."
            ),
            "recomendacao": (
                "Розгляньте Gemini Flash-Lite, скоротіть контекст "
                "і повторно використовуйте результати."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Виклики LLM із високою затримкою",
            "descricao": (
                "Виявлено {quantidade} виклик(ів), що тривали "
                "понад 30 секунд."
            ),
            "recomendacao": (
                "Перевірте холодний запуск, розмір запиту, "
                "мережу та час відповіді провайдера."
            ),
            "categoria": "Продуктивність",
        },
        "falhas_llm": {
            "titulo": "Помилки викликів LLM",
            "descricao": (
                "Виявлено {quantidade} помилку(ок), що становить "
                "{percentual}% усіх викликів."
            ),
            "recomendacao": (
                "Перевірте типи помилок, обмеження API, облікові "
                "дані та резервну стратегію."
            ),
            "categoria": "Надійність",
        },
        "tokens_elevados": {
            "titulo": "Висока середня кількість токенів",
            "descricao": (
                "Середня кількість токенів на виклик досягла "
                "{quantidade}."
            ),
            "recomendacao": (
                "Скоротіть історію, запити, фрагменти та "
                "документи, що надсилаються моделі."
            ),
            "categoria": "Ефективність",
        },
    },
    "ru": {
        "orcamento_mensal": {
            "titulo": "Высокое использование бюджета LLM",
            "descricao": (
                "Накопленное использование достигло {percentual}% "
                "месячного бюджета."
            ),
            "recomendacao": (
                "Проверьте модели, размер запросов, количество "
                "фрагментов и кеширование."
            ),
            "categoria": "FinOps",
        },
        "projecao_mensal": {
            "titulo": "Месячный прогноз выше ожидаемого",
            "descricao": (
                "Месячный прогноз использования близок к "
                "заданному лимиту или превышает его."
            ),
            "recomendacao": (
                "Рассмотрите Gemini Flash-Lite, сократите контекст "
                "и повторно используйте результаты."
            ),
            "categoria": "FinOps",
        },
        "chamadas_lentas": {
            "titulo": "Вызовы LLM с высокой задержкой",
            "descricao": (
                "Обнаружено вызовов длительностью более "
                "30 секунд: {quantidade}."
            ),
            "recomendacao": (
                "Проверьте холодный запуск, размер запроса, "
                "сеть и время ответа провайдера."
            ),
            "categoria": "Производительность",
        },
        "falhas_llm": {
            "titulo": "Ошибки вызовов LLM",
            "descricao": (
                "Обнаружено ошибок: {quantidade}; это "
                "{percentual}% всех вызовов."
            ),
            "recomendacao": (
                "Проверьте типы ошибок, лимиты API, учётные "
                "данные и стратегию резервирования."
            ),
            "categoria": "Надёжность",
        },
        "tokens_elevados": {
            "titulo": "Высокое среднее число токенов",
            "descricao": (
                "Среднее число токенов на вызов достигло "
                "{quantidade}."
            ),
            "recomendacao": (
                "Сократите историю, запросы, фрагменты и "
                "документы, отправляемые модели."
            ),
            "categoria": "Эффективность",
        },
    },
    "sa": {
        "orcamento_mensal": {
            "titulo": "استخدام مرتفع لميزانية نموذج اللغة",
            "descricao": (
                "بلغ الاستخدام التراكمي {percentual}% "
                "من الميزانية الشهرية."
            ),
            "recomendacao": (
                "راجع النماذج وأحجام المطالبات وعدد المقاطع "
                "واستخدام ذاكرة التخزين المؤقت."
            ),
            "categoria": "العمليات المالية",
        },
        "projecao_mensal": {
            "titulo": "التوقع الشهري أعلى من المتوقع",
            "descricao": (
                "توقع الاستخدام الشهري قريب من الحد المضبوط "
                "أو يتجاوزه."
            ),
            "recomendacao": (
                "قيّم استخدام Gemini Flash-Lite وقلل السياق "
                "وأعد استخدام النتائج."
            ),
            "categoria": "العمليات المالية",
        },
        "chamadas_lentas": {
            "titulo": "استدعاءات نموذج اللغة بزمن استجابة مرتفع",
            "descricao": (
                "تم اكتشاف {quantidade} استدعاء تجاوزت مدته "
                "30 ثانية."
            ),
            "recomendacao": (
                "تحقق من التشغيل البارد وحجم المطالبة والشبكة "
                "وزمن استجابة المزود."
            ),
            "categoria": "الأداء",
        },
        "falhas_llm": {
            "titulo": "فشل استدعاءات نموذج اللغة",
            "descricao": (
                "تم اكتشاف {quantidade} حالة فشل تمثل "
                "{percentual}% من الاستدعاءات."
            ),
            "recomendacao": (
                "حلل أنواع الأخطاء وحدود API وبيانات الاعتماد "
                "واستراتيجية الرجوع."
            ),
            "categoria": "الموثوقية",
        },
        "tokens_elevados": {
            "titulo": "متوسط مرتفع للرموز في كل استدعاء",
            "descricao": (
                "بلغ متوسط الرموز لكل استدعاء "
                "{quantidade} رمزاً."
            ),
            "recomendacao": (
                "قلل السجل والمطالبات والمقاطع والمستندات "
                "المرسلة إلى النموذج."
            ),
            "categoria": "الكفاءة",
        },
    },
}

LLM_ALERT_CONTENT_TEXTS["ch"] = {
    code: values.copy()
    for code, values
    in LLM_ALERT_CONTENT_TEXTS["de"].items()
}


def traduzir_conteudo_alerta_visual(
    alerta: Any,
) -> dict[str, str]:
    import re

    codigo = str(
        alerta.get(
            "codigo",
            "",
        )
    ).strip()

    original = {
        "titulo": str(
            alerta.get(
                "titulo",
                "Alerta",
            )
        ),
        "descricao": str(
            alerta.get(
                "descricao",
                "",
            )
        ),
        "recomendacao": str(
            alerta.get(
                "recomendacao",
                "",
            )
        ),
        "categoria": str(
            alerta.get(
                "categoria",
                "",
            )
        ),
    }

    idioma = llm_table_lang()

    idioma_catalogo = (
        idioma
        if idioma in LLM_ALERT_CONTENT_TEXTS
        else "en_us"
    )

    traducao = LLM_ALERT_CONTENT_TEXTS[
        idioma_catalogo
    ].get(
        codigo
    )

    if traducao is None:
        return original

    numeros = re.findall(
        r"\d+(?:[.,]\d+)?",
        original["descricao"],
    )

    quantidade = (
        numeros[0]
        if numeros
        else str(
            alerta.get(
                "valor_atual",
                0,
            )
        )
    )

    percentual = (
        numeros[1]
        if codigo == "falhas_llm"
        and len(numeros) > 1
        else numeros[0]
        if numeros
        else "0"
    )

    valores = {
        "quantidade": quantidade,
        "percentual": percentual,
    }

    return {
        "titulo": traducao["titulo"],
        "descricao": traducao[
            "descricao"
        ].format(
            **valores
        ),
        "recomendacao": traducao[
            "recomendacao"
        ],
        "categoria": traducao[
            "categoria"
        ],
    }

def render_alertas_llm_section(
    *,
    base_consumo: pd.DataFrame,
    finops: dict[str, Any],
) -> None:
    """
    Renderiza detecção, persistência e gestão de alertas.
    """
    try:
        from observability.llm_alerts import (
            carregar_alertas_llm,
            resolver_alerta_llm,
        )
    except ImportError:
        from src.observability.llm_alerts import (
            carregar_alertas_llm,
            resolver_alerta_llm,
        )

    try:
        from observability.llm_notifications import (
            avaliar_persistir_e_notificar_alertas,
            carregar_configuracao,
            carregar_notificacoes,
            notificar_alerta_email,
            reenviar_notificacao_email,
        )
    except ImportError:
        from src.observability.llm_notifications import (
            avaliar_persistir_e_notificar_alertas,
            carregar_configuracao,
            carregar_notificacoes,
            notificar_alerta_email,
            reenviar_notificacao_email,
        )

    st.divider()
    st.markdown(
        llm_alert_section_t("section_title")
    )

    st.caption(
        llm_alert_section_t("section_caption")
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1, 1, 2]
        )
    )

    status_filtro = controle_1.selectbox(
        llm_cost_alert_visual_t(
            "alert_status"
        ),
        options=[
            "aberto",
            "resolvido",
            "todos",
        ],
        index=0,
        format_func=formatar_status_filtro_alerta,
        key="llm_alert_status",
    )

    limite_alertas = controle_2.selectbox(
        llm_cost_alert_visual_t(
            "alert_limit"
        ),
        options=[
            50,
            100,
            250,
            500,
        ],
        index=1,
        key="llm_alert_limit",
    )

    with controle_3:
        st.write("")

        avaliar = st.button(
            llm_alert_section_t("evaluate_now"),
            use_container_width=True,
            key="llm_alert_evaluate",
        )

    if avaliar:
        resultado_avaliacao = (
            avaliar_persistir_e_notificar_alertas(
                base_consumo,
                finops,
            )
        )

        if resultado_avaliacao.get("ok"):
            st.success(
                f"{llm_alert_section_t('evaluation_completed')} "
                f"{llm_alert_section_t('detected')}: "
                f"{resultado_avaliacao.get('total_detectados', 0)} | "
                f"{llm_alert_section_t('saved')}: "
                f"{resultado_avaliacao.get('total_salvos', 0)} | "
                f"{llm_alert_section_t('duplicates')}: "
                f"{resultado_avaliacao.get('total_duplicados', 0)} | "
                f"{llm_cost_alert_visual_t('email_sent_plural')}: "
                f"{resultado_avaliacao.get('total_notificacoes_enviadas', 0)} | "
                f"{llm_cost_alert_visual_t('email_failures')}: "
                f"{resultado_avaliacao.get('total_notificacoes_falhas', 0)}"
            )
        else:
            st.error(
                llm_alert_section_t(
                    "evaluation_failed"
                )
            )

    status_consulta = (
        None
        if status_filtro == "todos"
        else status_filtro
    )

    resultado_alertas = carregar_alertas_llm(
        limite=int(
            limite_alertas
        ),
        status=status_consulta,
    )

    if not resultado_alertas.get("ok"):
        st.error(
            resultado_alertas.get(
                "message",
                llm_alert_section_t(
                    "load_failed"
                ),
            )
        )
        return

    alertas = resultado_alertas.get(
        "df"
    )

    if alertas is None or alertas.empty:
        st.info(
            llm_alert_section_t(
                "no_alerts"
            )
        )
        return

    contagem = (
        alertas["severidade"]
        .value_counts()
        .to_dict()
    )

    resumo_cols = st.columns(5)

    resumo_cols[0].metric(
        llm_cost_alert_visual_t(
            "total"
        ),
        len(alertas),
    )

    resumo_cols[1].metric(
        llm_alert_section_t("critical"),
        int(
            contagem.get(
                "critica",
                0,
            )
        ),
    )

    resumo_cols[2].metric(
        llm_alert_section_t("high"),
        int(
            contagem.get(
                "alta",
                0,
            )
        ),
    )

    resumo_cols[3].metric(
        llm_alert_section_t("medium"),
        int(
            contagem.get(
                "media",
                0,
            )
        ),
    )

    resumo_cols[4].metric(
        llm_cost_alert_visual_t(
            "low_plural"
        ),
        int(
            contagem.get(
                "baixa",
                0,
            )
        ),
    )

    simbolos = {
        "critica": "🔴",
        "alta": "🟠",
        "media": "🟡",
        "baixa": "🔵",
        "informativa": "ℹ️",
    }

    configuracao_email = carregar_configuracao()

    resultado_notificacoes = carregar_notificacoes(
        limite=1000
    )

    notificacoes_df = resultado_notificacoes.get(
        "df"
    )

    alertas_enviados: set[int] = set()

    if (
        notificacoes_df is not None
        and not notificacoes_df.empty
        and "alerta_id" in notificacoes_df.columns
        and "status" in notificacoes_df.columns
    ):
        enviados_df = notificacoes_df[
            notificacoes_df["status"] == "enviado"
        ]

        alertas_enviados = {
            int(alerta_id)
            for alerta_id in enviados_df[
                "alerta_id"
            ].dropna().tolist()
        }

    st.markdown(
        llm_alert_section_t("alerts_list")
    )

    if not configuracao_email.get(
        "habilitado"
    ):
        st.warning(
            "As notificações por e-mail estão "
            "desabilitadas no ambiente."
        )
    elif not configuracao_email.get(
        "destinatario"
    ):
        st.warning(
            "O destinatário dos alertas não está configurado."
        )
    elif not configuracao_email.get(
        "resend_configurado"
    ):
        st.warning(
            "A integração com o Resend não está configurada."
        )
    else:
        st.success(
            llm_alert_section_t(
                "email_enabled"
            )
        )

    for _, alerta in alertas.iterrows():
        severidade = str(
            alerta.get(
                "severidade",
                "informativa",
            )
        )

        status = str(
            alerta.get(
                "status",
                "aberto",
            )
        )

        simbolo = simbolos.get(
            severidade,
            "ℹ️",
        )

        conteudo_visual = (
            traduzir_conteudo_alerta_visual(
                alerta
            )
        )

        titulo = conteudo_visual[
            "titulo"
        ]

        with st.container(
            border=True
        ):
            cabecalho_1, cabecalho_2 = (
                st.columns(
                    [4, 1]
                )
            )

            cabecalho_1.markdown(
                f"### {simbolo} {titulo}"
            )

            cabecalho_2.metric(
                llm_cost_alert_visual_t(
                    "status"
                ),
                traduzir_status_alerta_visual(
                    status
                ),
            )

            st.markdown(
                conteudo_visual[
                    "descricao"
                ]
            )

            metrica_cols = st.columns(4)

            metrica_cols[0].metric(
                llm_cost_alert_visual_t(
                    "severity"
                ),
                traduzir_severidade_alerta_visual(
                    severidade
                ),
            )

            metrica_cols[1].metric(
                llm_cost_alert_visual_t(
                    "current_value"
                ),
                alerta.get(
                    "valor_atual",
                    0,
                ),
            )

            metrica_cols[2].metric(
                llm_cost_alert_visual_t(
                    "limit"
                ),
                alerta.get(
                    "valor_limite",
                    0,
                ),
            )

            metrica_cols[3].metric(
                llm_cost_alert_visual_t(
                    "unit"
                ),
                alerta.get(
                    "unidade",
                    "—",
                ),
            )

            st.info(
                f"{llm_alert_section_t('recommendation_label')}: "
                f"{conteudo_visual['recomendacao']}"
            )

            st.caption(
                f"{llm_alert_section_t('code_label')}: "
                f"{alerta.get('codigo', '')} | "
                f"{llm_alert_section_t('category_label')}: "
                f"{conteudo_visual['categoria']} | "
                f"{llm_cost_alert_visual_t('created_at')}: "
                f"{alerta.get('criado_em', '')}"
            )

            if status == "aberto":
                alerta_id = int(
                    alerta["id"]
                )

                pode_enviar_email = (
                    severidade
                    in {"alta", "critica"}
                    and configuracao_email.get(
                        "habilitado"
                    )
                    and bool(
                        configuracao_email.get(
                            "destinatario"
                        )
                    )
                    and configuracao_email.get(
                        "resend_configurado"
                    )
                )

                ja_enviado = (
                    alerta_id
                    in alertas_enviados
                )

                coluna_email, coluna_resolver = (
                    st.columns(2)
                )

                with coluna_email:
                    if ja_enviado:
                        st.success(
                            llm_alert_section_t("notification_sent")
                        )

                    elif severidade not in {
                        "alta",
                        "critica",
                    }:
                        st.info(
                            llm_alert_section_t(
                                "restricted_delivery"
                            )
                        )

                    elif st.button(
                        llm_alert_section_t(
                            "send_email"
                        ),
                        key=(
                            "send_llm_alert_email_"
                            f"{alerta_id}"
                        ),
                        use_container_width=True,
                        disabled=(
                            not pode_enviar_email
                        ),
                    ):
                        with st.spinner(
                            llm_alert_section_t(
                                "sending_alert"
                            )
                        ):
                            resultado_envio = (
                                notificar_alerta_email(
                                    alerta.to_dict()
                                )
                            )

                        if resultado_envio.get(
                            "enviado"
                        ):
                            st.success(
                                llm_alert_section_t(
                                    "alert_sent"
                                )
                            )
                            st.rerun()

                        elif resultado_envio.get(
                            "duplicado"
                        ):
                            st.info(
                                llm_alert_section_t(
                                    "already_sent"
                                )
                            )
                            st.rerun()

                        elif resultado_envio.get(
                            "ignorado"
                        ):
                            st.warning(
                                resultado_envio.get(
                                    "message",
                                    llm_alert_section_t(
                                        "send_criteria_failed"
                                    ),
                                )
                            )

                        else:
                            st.error(
                                llm_alert_section_t(
                                    "send_error"
                                ).format(
                                    error=resultado_envio.get(
                                        "message",
                                        llm_alert_section_t(
                                            "unknown_error"
                                        ),
                                    )
                                )
                            )

                with coluna_resolver:
                    if st.button(
                        llm_alert_section_t("resolve"),
                        key=(
                            f"resolve_llm_alert_"
                            f"{alerta_id}"
                        ),
                        use_container_width=True,
                    ):
                        resultado_resolucao = (
                            resolver_alerta_llm(
                                alerta_id,
                                resolvido_por=(
                                    "llm_cost_center"
                                ),
                            )
                        )

                        if resultado_resolucao.get(
                            "resolvido"
                        ):
                            st.success(
                                llm_alert_section_t(
                                    "resolved"
                                )
                            )
                            st.rerun()
                        else:
                            st.info(
                                resultado_resolucao.get(
                                    "message",
                                    llm_alert_section_t(
                                        "already_resolved"
                                    ),
                                )
                            )

    st.markdown(
        llm_alert_section_t("integration_health")
    )

    try:
        try:
            from observability.resend_webhook import (
                carregar_eventos_resend,
                carregar_saude_integracoes,
            )
        except ImportError:
            from src.observability.resend_webhook import (
                carregar_eventos_resend,
                carregar_saude_integracoes,
            )

        saude = carregar_saude_integracoes()

        saude_col_1, saude_col_2, saude_col_3, saude_col_4 = (
            st.columns(4)
        )

        saude_col_1.metric(
            llm_cost_alert_visual_t(
                "database"
            ),
            (
                llm_alert_section_t("connected")
                if saude.get("banco_conectado")
                else llm_alert_section_t("unavailable")
            ),
        )

        saude_col_2.metric(
            llm_alert_section_t("resend"),
            (
                llm_alert_section_t("configured")
                if saude.get("resend_configurado")
                else llm_alert_section_t("not_configured")
            ),
        )

        saude_col_3.metric(
            llm_alert_section_t("webhook"),
            (
                llm_alert_section_t("configured")
                if saude.get("webhook_configurado")
                else llm_alert_section_t("not_configured")
            ),
        )

        saude_col_4.metric(
            llm_cost_alert_visual_t(
                "email_alerts"
            ),
            (
                llm_cost_alert_visual_t(
                    "enabled_plural"
                )
                if saude.get(
                    "email_alertas_habilitado"
                )
                else llm_cost_alert_visual_t(
                    "disabled_plural"
                )
            ),
        )

        detalhe_1, detalhe_2, detalhe_3, detalhe_4 = (
            st.columns(4)
        )

        detalhe_1.metric(
            llm_alert_section_t("events_24h"),
            int(
                saude.get(
                    "eventos_webhook_24h",
                    0,
                )
                or 0
            ),
        )

        detalhe_2.metric(
            "Falhas de webhook em 24h",
            int(
                saude.get(
                    "falhas_webhook_24h",
                    0,
                )
                or 0
            ),
        )

        detalhe_3.metric(
            "E-mails entregues",
            int(
                saude.get(
                    "emails_entregues",
                    0,
                )
                or 0
            ),
        )

        detalhe_4.metric(
            "E-mails com falha",
            int(
                saude.get(
                    "emails_com_falha",
                    0,
                )
                or 0
            ),
        )

        with st.expander(
            llm_alert_section_t(
                "integration_details"
            ),
            expanded=False,
        ):
            st.write(
                {
                    llm_alert_section_t(
                        "last_event"
                    ): saude.get(
                        "ultimo_evento_tipo"
                    ),
                    "Evento recebido em": saude.get(
                        "ultimo_evento_recebido_em"
                    ),
                    "Evento processado": saude.get(
                        "ultimo_evento_processado"
                    ),
                    "Resultado": saude.get(
                        "ultimo_evento_resultado"
                    ),
                    llm_alert_section_t(
                        "last_email_delivered"
                    ): (
                        saude.get(
                            "ultimo_email_entregue_em"
                        )
                    ),
                    llm_alert_section_t(
                        "configured_recipient"
                    ): (
                        saude.get(
                            "destinatario_configurado"
                        )
                    ),
                }
            )

        if not saude.get("ok"):
            st.warning(
                saude.get(
                    "message",
                    "Saúde parcialmente indisponível.",
                )
            )

    except Exception as exc:
        st.warning(
            llm_alert_section_t(
                "health_error"
            ).format(
                error=exc
            )
        )

    st.markdown(
        llm_alert_section_t("webhook_events")
    )

    controle_evento_1, controle_evento_2 = (
        st.columns(2)
    )

    event_period_keys = [
        "events_24_hours",
        "events_7_days",
        "all_history",
    ]

    periodo_eventos = controle_evento_1.selectbox(
        llm_alert_section_t("events_period"),
        options=event_period_keys,
        format_func=llm_alert_section_t,
        key="resend_events_period",
    )

    limite_eventos = controle_evento_2.selectbox(
        llm_cost_page_t(
            "event_limit"
        ),
        options=[
            50,
            100,
            250,
            500,
        ],
        index=1,
        key="resend_events_limit",
    )

    horas_eventos = {
        "events_24_hours": 24,
        "events_7_days": 168,
        "all_history": None,
    }.get(periodo_eventos)

    resultado_eventos = carregar_eventos_resend(
        limite=limite_eventos,
        horas=horas_eventos,
    )

    if not resultado_eventos.get("ok"):
        st.warning(
            resultado_eventos.get(
                "message",
                "Eventos indisponíveis.",
            )
        )

    else:
        eventos_resend = pd.DataFrame(
            resultado_eventos.get(
                "eventos",
                [],
            )
        )

        if eventos_resend.empty:
            st.info(
                llm_alert_section_t(
                    "no_webhook_events"
                )
            )

        else:
            total_eventos = len(eventos_resend)

            total_processados = int(
                eventos_resend[
                    "processado"
                ]
                .fillna(False)
                .astype(bool)
                .sum()
            )

            total_falhas_eventos = int(
                (
                    eventos_resend[
                        "resultado"
                    ]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .eq("erro")
                    |
                    eventos_resend[
                        "processado"
                    ]
                    .fillna(False)
                    .eq(False)
                ).sum()
            )

            ultimo_evento = (
                eventos_resend.iloc[0][
                    "evento_tipo"
                ]
                if not eventos_resend.empty
                else "Nenhum"
            )

            evento_col_1, evento_col_2, evento_col_3, evento_col_4 = (
                st.columns(4)
            )

            evento_col_1.metric(
                "Total de eventos",
                total_eventos,
            )

            evento_col_2.metric(
                "Processados",
                total_processados,
            )

            evento_col_3.metric(
                "Falhas",
                total_falhas_eventos,
            )

            evento_col_4.metric(
                llm_alert_section_t("last_event"),
                str(ultimo_evento),
            )

            filtro_evento_1, filtro_evento_2 = (
                st.columns(2)
            )

            tipos_eventos = [
                "todos",
                *sorted(
                    eventos_resend[
                        "evento_tipo"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                ),
            ]

            tipo_evento_filtro = (
                filtro_evento_1.selectbox(
                    "Tipo do evento",
                    options=tipos_eventos,
                    key="resend_event_type_filter",
                )
            )

            resultados_eventos = [
                "todos",
                *sorted(
                    eventos_resend[
                        "resultado"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                ),
            ]

            resultado_evento_filtro = (
                filtro_evento_2.selectbox(
                    "Resultado",
                    options=resultados_eventos,
                    key=(
                        "resend_event_result_filter"
                    ),
                )
            )

            eventos_filtrados = (
                eventos_resend.copy()
            )

            if tipo_evento_filtro != "todos":
                eventos_filtrados = (
                    eventos_filtrados[
                        eventos_filtrados[
                            "evento_tipo"
                        ]
                        == tipo_evento_filtro
                    ]
                )

            if (
                resultado_evento_filtro
                != "todos"
            ):
                eventos_filtrados = (
                    eventos_filtrados[
                        eventos_filtrados[
                            "resultado"
                        ]
                        == resultado_evento_filtro
                    ]
                )

            eventos_filtrados[
                "processado_exibicao"
            ] = eventos_filtrados[
                "processado"
            ].apply(
                lambda valor: (
                    llm_resend_event_t("yes")
                    if bool(valor)
                    else llm_resend_event_t("no")
                )
            )

            colunas_eventos = [
                "id",
                "evento_tipo",
                "provider_message_id",
                "recebido_em",
                "processado_exibicao",
                "processado_em",
                "resultado",
                "erro_mensagem",
                "svix_id",
            ]

            tabela_eventos = (
                eventos_filtrados[
                    colunas_eventos
                ]
                .copy()
                .rename(
                    columns={
                        "id": "ID",
                        "evento_tipo": (
                            "Tipo do evento"
                        ),
                        "provider_message_id": (
                            "Message ID"
                        ),
                        "recebido_em": (
                            "Recebido em"
                        ),
                        "processado_exibicao": (
                            "Processado"
                        ),
                        "processado_em": (
                            "Processado em"
                        ),
                        "resultado": "Resultado",
                        "erro_mensagem": "Erro",
                        "svix_id": "Svix ID",
                    }
                )
            )

            if "Resultado" in tabela_eventos.columns:
                mapa_resultados = {
                    "ok": llm_resend_event_t(
                        "success"
                    ),
                    "sucesso": llm_resend_event_t(
                        "success"
                    ),
                    "processado": llm_resend_event_t(
                        "processed_value"
                    ),
                    "erro": llm_resend_event_t(
                        "error_value"
                    ),
                    "falha": llm_resend_event_t(
                        "failure"
                    ),
                    "pendente": llm_resend_event_t(
                        "pending"
                    ),
                    "ignorado": llm_resend_event_t(
                        "ignored"
                    ),
                }

                valores_resultado = (
                    tabela_eventos["Resultado"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                tabela_eventos["Resultado"] = (
                    valores_resultado
                    .map(mapa_resultados)
                    .fillna(
                        tabela_eventos[
                            "Resultado"
                        ].fillna(
                            llm_resend_event_t("no_result")
                        )
                    )
                )

            if "Erro" in tabela_eventos.columns:
                tabela_eventos["Erro"] = (
                    tabela_eventos["Erro"]
                    .fillna("—")
                    .replace(
                        {
                            "": "—",
                            "None": "—",
                            "nan": "—",
                        }
                    )
                )

            st.dataframe(
                estilizar_tabela_eventos_resend(
                    tabela_eventos
                ),
                use_container_width=True,
                hide_index=True,
                height=420,
                column_config={
                    "ID": (
                        st.column_config.NumberColumn(
                            "ID",
                            format="%d",
                            width="small",
                        )
                    ),
                    "Tipo do evento": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "event_type"
                            ),
                            help=llm_resend_event_t(
                                "event_help"
                            ),
                            width="large",
                        )
                    ),
                    "Message ID": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "message_id"
                            ),
                            width="large",
                        )
                    ),
                    "Recebido em": (
                        st.column_config.DatetimeColumn(
                            llm_resend_event_t(
                                "received_at"
                            ),
                            format=(
                                "DD/MM/YYYY HH:mm:ss"
                            ),
                            width="medium",
                        )
                    ),
                    "Processado": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "processed"
                            ),
                            width="small",
                        )
                    ),
                    "Processado em": (
                        st.column_config.DatetimeColumn(
                            llm_resend_event_t(
                                "processed_at"
                            ),
                            format=(
                                "DD/MM/YYYY HH:mm:ss"
                            ),
                            width="medium",
                        )
                    ),
                    "Resultado": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "result"
                            ),
                            width="medium",
                        )
                    ),
                    "Erro": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "error"
                            ),
                            width="large",
                        )
                    ),
                    "Svix ID": (
                        st.column_config.TextColumn(
                            llm_resend_event_t(
                                "svix_id"
                            ),
                            help=llm_resend_event_t(
                                "svix_help"
                            ),
                            width="large",
                        )
                    ),
                },
            )

            csv_eventos = (
                tabela_eventos.to_csv(
                    index=False
                ).encode("utf-8-sig")
            )

            st.download_button(
                llm_alert_section_t("export_webhook"),
                data=csv_eventos,
                file_name=(
                    "inna_resend_webhook_eventos.csv"
                ),
                mime="text/csv",
                use_container_width=True,
                key="resend_events_download",
            )

    st.markdown(
        llm_alert_section_t("notification_audit")
    )

    if not resultado_notificacoes.get("ok"):
        st.error(
            resultado_notificacoes.get(
                "message",
                llm_alert_section_t("notifications_load_failed"),
            )
        )

    elif (
        notificacoes_df is None
        or notificacoes_df.empty
    ):
        st.info(
            llm_alert_section_t(
                "no_notifications"
            )
        )

    else:
        auditoria_df = notificacoes_df.copy()

        auditoria_df["status_entrega"] = (
            auditoria_df["status_entrega"]
            .fillna("aguardando")
            .astype(str)
            .str.lower()
        )

        total_notificacoes = len(auditoria_df)

        total_enviadas = int(
            auditoria_df["status"]
            .astype(str)
            .str.lower()
            .eq("enviado")
            .sum()
        )

        total_entregues = int(
            auditoria_df["status_entrega"]
            .eq("entregue")
            .sum()
        )

        status_falha = {
            "falhou",
            "devolvido",
            "suprimido",
            "reclamacao",
        }

        total_falhas = int(
            auditoria_df["status_entrega"]
            .isin(status_falha)
            .sum()
        )

        total_aguardando = max(
            total_enviadas
            - total_entregues
            - total_falhas,
            0,
        )

        taxa_entrega = (
            total_entregues
            / total_enviadas
            * 100
            if total_enviadas
            else 0
        )

        metrica_1, metrica_2, metrica_3, metrica_4, metrica_5 = (
            st.columns(5)
        )

        metrica_1.metric(
            llm_alert_section_t("notifications"),
            total_notificacoes,
        )

        metrica_2.metric(
            llm_alert_section_t("sent_plural"),
            total_enviadas,
        )

        metrica_3.metric(
            llm_alert_section_t("delivered_plural"),
            total_entregues,
        )

        metrica_4.metric(
            llm_alert_section_t("waiting_plural"),
            total_aguardando,
        )

        metrica_5.metric(
            llm_alert_section_t("delivery_rate"),
            f"{taxa_entrega:.1f}%",
        )

        filtro_1, filtro_2 = st.columns(2)

        all_status_key = "__all__"

        opcoes_status = [
            all_status_key,
            *sorted(
                auditoria_df[
                    "status_entrega"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
        ]

        filtro_status_entrega = filtro_1.selectbox(
            llm_alert_section_t(
                "delivery_status_filter"
            ),
            options=opcoes_status,
            format_func=lambda value: (
                llm_alert_section_t("all")
                if value == all_status_key
                else traduzir_status_notificacao(value)
            ),
            key="llm_notification_delivery_status",
        )

        filtro_destinatario = filtro_2.text_input(
            llm_alert_section_t("recipient_filter"),
            key="llm_notification_recipient_filter",
        )

        filtrado_notificacoes = auditoria_df.copy()

        if filtro_status_entrega != all_status_key:
            filtrado_notificacoes = (
                filtrado_notificacoes[
                    filtrado_notificacoes[
                        "status_entrega"
                    ]
                    == filtro_status_entrega
                ]
            )

        if filtro_destinatario.strip():
            filtrado_notificacoes = (
                filtrado_notificacoes[
                    filtrado_notificacoes[
                        "destinatario_mascarado"
                    ]
                    .astype(str)
                    .str.contains(
                        filtro_destinatario.strip(),
                        case=False,
                        na=False,
                    )
                ]
            )

        icones_status = {
            "entregue": "🟢 Entregue",
            "enviado": "🔵 Enviado",
            "aguardando": "⚪ Aguardando",
            "atrasado": "🟡 Atrasado",
            "falhou": "🔴 Falhou",
            "devolvido": "🟠 Devolvido",
            "suprimido": "🟣 Suprimido",
            "reclamacao": "🔴 Reclamação",
            "aberto_email": "📬 Aberto",
            "clicado": "🔗 Clicado",
        }

        filtrado_notificacoes[
            "status_entrega_exibicao"
        ] = (
            filtrado_notificacoes[
                "status_entrega"
            ]
            .map(icones_status)
            .fillna(
                filtrado_notificacoes[
                    "status_entrega"
                ]
            )
        )

        colunas_notificacoes = [
            "id",
            "alerta_id",
            "status",
            "status_entrega_exibicao",
            "evento_provider",
            "destinatario_mascarado",
            "assunto",
            "tentativas",
            "provider_message_id",
            "criado_em",
            "enviado_em",
            "entregue_em",
            "devolvido_em",
            "webhook_recebido_em",
            "motivo_entrega",
            "erro_tipo",
            "erro_mensagem",
        ]

        colunas_notificacoes = [
            coluna
            for coluna in colunas_notificacoes
            if coluna
            in filtrado_notificacoes.columns
        ]

        tabela_notificacoes = (
            filtrado_notificacoes[
                colunas_notificacoes
            ].copy()
        )

        tabela_notificacoes = (
            tabela_notificacoes.rename(
                columns={
                    "id": "ID",
                    "alerta_id": "Alerta",
                    "status": "Status do envio",
                    "status_entrega_exibicao": (
                        "Status da entrega"
                    ),
                    "evento_provider": (
                        "Evento do Resend"
                    ),
                    "destinatario_mascarado": (
                        "Destinatário"
                    ),
                    "assunto": "Assunto",
                    "tentativas": "Tentativas",
                    "provider_message_id": (
                        "Message ID"
                    ),
                    "criado_em": "Criado em",
                    "enviado_em": "Enviado em",
                    "entregue_em": "Entregue em",
                    "devolvido_em": "Devolvido em",
                    "webhook_recebido_em": (
                        "Webhook recebido em"
                    ),
                    "motivo_entrega": (
                        "Motivo da entrega/falha"
                    ),
                    "erro_tipo": "Tipo do erro",
                    "erro_mensagem": (
                        "Mensagem de erro"
                    ),
                }
            )
        )

        if (
            "Status do envio"
            in tabela_notificacoes.columns
        ):
            tabela_notificacoes[
                "Status do envio"
            ] = (
                tabela_notificacoes[
                    "Status do envio"
                ]
                .fillna("aguardando")
                .astype(str)
                .str.lower()
                .map(
                    {
                        "enviado": llm_notification_t(
                            "sent"
                        ),
                        "aguardando": llm_notification_t(
                            "waiting"
                        ),
                        "falhou": llm_notification_t(
                            "failed"
                        ),
                        "cancelado": llm_notification_t(
                            "cancelled"
                        ),
                    }
                )
                .fillna(
                    llm_notification_t("unknown")
                )
            )

        if (
            "Status da entrega"
            in tabela_notificacoes.columns
        ):
            tabela_notificacoes[
                "Status da entrega"
            ] = tabela_notificacoes[
                "Status da entrega"
            ].map(
                traduzir_status_notificacao
            )

        for coluna_erro in (
            "Tipo do erro",
            "Mensagem de erro",
            "Motivo da entrega/falha",
        ):
            if (
                coluna_erro
                in tabela_notificacoes.columns
            ):
                tabela_notificacoes[
                    coluna_erro
                ] = (
                    tabela_notificacoes[
                        coluna_erro
                    ]
                    .fillna("—")
                    .replace(
                        {
                            "": "—",
                            "None": "—",
                            "nan": "—",
                        }
                    )
                )

        st.dataframe(
            estilizar_tabela_notificacoes_llm(
                tabela_notificacoes
            ),
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "ID": (
                    st.column_config.NumberColumn(
                        "ID",
                        format="%d",
                        width="small",
                    )
                ),
                "Alerta": (
                    st.column_config.NumberColumn(
                        llm_notification_t("alert"),
                        format="%d",
                        width="small",
                    )
                ),
                "Status do envio": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "send_status"
                        ),
                        width="medium",
                    )
                ),
                "Status da entrega": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "delivery_status"
                        ),
                        width="medium",
                    )
                ),
                "Evento do Resend": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "resend_event"
                        ),
                        width="medium",
                    )
                ),
                "Destinatário": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "recipient"
                        ),
                        help=llm_notification_t(
                            "recipient_help"
                        ),
                        width="large",
                    )
                ),
                "Assunto": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "subject"
                        ),
                        width="large",
                    )
                ),
                "Tentativas": (
                    st.column_config.ProgressColumn(
                        llm_notification_t(
                            "attempts"
                        ),
                        help=llm_notification_t(
                            "attempts_help"
                        ),
                        min_value=0,
                        max_value=3,
                        format="%d",
                        width="small",
                    )
                ),
                "Message ID": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "message_id"
                        ),
                        width="large",
                    )
                ),
                "Criado em": (
                    st.column_config.DatetimeColumn(
                        llm_notification_t(
                            "created_at"
                        ),
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium",
                    )
                ),
                "Enviado em": (
                    st.column_config.DatetimeColumn(
                        llm_notification_t(
                            "sent_at"
                        ),
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium",
                    )
                ),
                "Entregue em": (
                    st.column_config.DatetimeColumn(
                        llm_notification_t(
                            "delivered_at"
                        ),
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium",
                    )
                ),
                "Devolvido em": (
                    st.column_config.DatetimeColumn(
                        llm_notification_t(
                            "returned_at"
                        ),
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium",
                    )
                ),
                "Webhook recebido em": (
                    st.column_config.DatetimeColumn(
                        llm_notification_t(
                            "webhook_at"
                        ),
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium",
                    )
                ),
                "Motivo da entrega/falha": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "delivery_reason"
                        ),
                        width="large",
                    )
                ),
                "Tipo do erro": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "error_type"
                        ),
                        width="medium",
                    )
                ),
                "Mensagem de erro": (
                    st.column_config.TextColumn(
                        llm_notification_t(
                            "error_message"
                        ),
                        width="large",
                    )
                ),
            },
        )

        csv_notificacoes = (
            tabela_notificacoes.to_csv(
                index=False
            ).encode("utf-8-sig")
        )

        st.download_button(
            llm_alert_section_t("export_notifications"),
            data=csv_notificacoes,
            file_name=(
                "inna_llm_notificacoes.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key="llm_notification_download",
        )

    st.markdown(
        llm_alert_section_t("retry_section")
    )

    status_reenvio = {
        "falhou",
        "devolvido",
        "suprimido",
    }

    notificacoes_reenvio = (
        notificacoes_df.copy()
        if notificacoes_df is not None
        else None
    )

    if (
        notificacoes_reenvio is None
        or notificacoes_reenvio.empty
    ):
        st.info(
            llm_alert_section_t(
                "no_retry"
            )
        )

    else:
        notificacoes_reenvio[
            "status_entrega_normalizado"
        ] = (
            notificacoes_reenvio[
                "status_entrega"
            ]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        notificacoes_reenvio = (
            notificacoes_reenvio[
                (
                    notificacoes_reenvio[
                        "status_entrega_normalizado"
                    ].isin(status_reenvio)
                )
                & (
                    notificacoes_reenvio[
                        "tentativas"
                    ].fillna(0).astype(int) < 3
                )
            ]
        )

        if notificacoes_reenvio.empty:
            st.success(
                llm_alert_section_t(
                    "no_failed_retry"
                )
            )

        else:
            st.warning(
                llm_alert_section_t(
                    "retry_limit"
                )
            )

            for _, notificacao in (
                notificacoes_reenvio.iterrows()
            ):
                notificacao_id = int(
                    notificacao["id"]
                )

                col_info, col_acao = st.columns(
                    [4, 1]
                )

                with col_info:
                    st.write(
                        f"**{llm_alert_section_t('notification_label')} "
                        f"#{notificacao_id}** — "
                        f"{llm_alert_section_t('alert_label')} "
                        f"#{int(notificacao['alerta_id'])}"
                    )

                    st.caption(
                        f"{llm_alert_section_t('status_label')}: "
                        f"{traduzir_status_notificacao(notificacao.get('status_entrega'))} "
                        f"• {llm_alert_section_t('attempts_label')}: "
                        f"{int(notificacao.get('tentativas', 0))}/3 "
                        f"• {llm_alert_section_t('recipient_label')}: "
                        f"{notificacao.get('destinatario_mascarado')}"
                    )

                with col_acao:
                    if st.button(
                        llm_alert_section_t(
                            "retry"
                        ),
                        key=(
                            "retry_notification_"
                            f"{notificacao_id}"
                        ),
                        use_container_width=True,
                    ):
                        with st.spinner(
                            llm_alert_section_t(
                                "retrying"
                            )
                        ):
                            resultado_reenvio = (
                                reenviar_notificacao_email(
                                    notificacao_id=(
                                        notificacao_id
                                    ),
                                    max_tentativas=3,
                                )
                            )

                        if resultado_reenvio.get(
                            "ok"
                        ):
                            st.success(
                                resultado_reenvio.get(
                                    "message",
                                    llm_alert_section_t(
                                        "retry_success"
                                    ),
                                )
                            )
                            st.rerun()

                        else:
                            st.error(
                                resultado_reenvio.get(
                                    "message",
                                    llm_alert_section_t(
                                        "retry_failed"
                                    ),
                                )
                            )

    st.markdown(
        llm_alert_section_t("alerts_audit")
    )

    colunas = [
        "id",
        "criado_em",
        "atualizado_em",
        "codigo",
        "titulo",
        "categoria",
        "severidade",
        "status",
        "valor_atual",
        "valor_limite",
        "unidade",
        "modelo",
        "operacao",
        "resolvido_em",
        "resolvido_por",
    ]

    colunas = [
        coluna
        for coluna in colunas
        if coluna in alertas.columns
    ]

    tabela = alertas[
        colunas
    ].copy()

    tabela = tabela.rename(
        columns={
            "id": "ID",
            "criado_em": "Criado em",
            "atualizado_em": "Atualizado em",
            "codigo": "Código",
            "titulo": "Título",
            "categoria": "Categoria",
            "severidade": "Severidade",
            "status": "Status",
            "valor_atual": "Valor atual",
            "valor_limite": "Valor limite",
            "unidade": "Unidade",
            "modelo": "Modelo",
            "operacao": "Operação",
            "resolvido_em": "Resolvido em",
            "resolvido_por": "Resolvido por",
        }
    )

    if "Severidade" in tabela.columns:
        tabela["Severidade"] = (
            tabela["Severidade"]
            .fillna("informativa")
            .astype(str)
            .str.lower()
            .map(
                {
                    "informativa": llm_alert_t(
                        "informational"
                    ),
                    "baixa": llm_alert_t("low"),
                    "media": llm_alert_t("medium"),
                    "média": llm_alert_t("medium"),
                    "alta": llm_alert_t("high"),
                    "critica": llm_alert_t(
                        "critical"
                    ),
                    "crítica": llm_alert_t(
                        "critical"
                    ),
                }
            )
            .fillna(
                llm_alert_t("unclassified")
            )
        )

    if "Status" in tabela.columns:
        tabela["Status"] = (
            tabela["Status"]
            .fillna("aberto")
            .astype(str)
            .str.lower()
            .map(
                {
                    "aberto": llm_alert_t("open"),
                    "resolvido": llm_alert_t(
                        "resolved"
                    ),
                    "fechado": llm_alert_t(
                        "closed"
                    ),
                    "cancelado": llm_alert_t(
                        "cancelled"
                    ),
                }
            )
            .fillna(
                llm_alert_t("unknown")
            )
        )

    st.dataframe(
        estilizar_tabela_alertas_llm(
            tabela
        ),
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "ID": st.column_config.NumberColumn(
                "ID",
                format="%d",
                width="small",
            ),
            "Criado em": (
                st.column_config.DatetimeColumn(
                    llm_alert_t("created_at"),
                    format="DD/MM/YYYY HH:mm:ss",
                    width="medium",
                )
            ),
            "Atualizado em": (
                st.column_config.DatetimeColumn(
                    llm_alert_t("updated_at"),
                    format="DD/MM/YYYY HH:mm:ss",
                    width="medium",
                )
            ),
            "Título": st.column_config.TextColumn(
                llm_alert_t("title"),
                width="large",
            ),
            "Categoria": (
                st.column_config.TextColumn(
                    llm_alert_t("category"),
                    width="medium",
                )
            ),
            "Severidade": (
                st.column_config.TextColumn(
                    llm_alert_t("severity"),
                    width="medium",
                )
            ),
            "Status": st.column_config.TextColumn(
                llm_alert_t("status"),
                width="medium",
            ),
            "Valor atual": (
                st.column_config.NumberColumn(
                    llm_alert_t("current_value"),
                    format="%.4f",
                    width="small",
                )
            ),
            "Valor limite": (
                st.column_config.NumberColumn(
                    llm_alert_t("limit_value"),
                    format="%.4f",
                    width="small",
                )
            ),
            "Modelo": st.column_config.TextColumn(
                llm_table_t("model"),
                width="large",
            ),
            "Operação": (
                st.column_config.TextColumn(
                    llm_table_t("operation"),
                    width="large",
                )
            ),
            "Resolvido em": (
                st.column_config.DatetimeColumn(
                    llm_alert_t("resolved_at"),
                    format="DD/MM/YYYY HH:mm:ss",
                    width="medium",
                )
            ),
        },
    )

    csv = tabela.to_csv(
        index=False,
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        llm_alert_section_t("export_alerts"),
        data=csv,
        file_name="inna_llm_alertas.csv",
        mime="text/csv",
        use_container_width=True,
        key="llm_alert_download",
    )


LLM_COST_PAGE_TEXTS = {
    "pt": {
        "title": "💰 Central de Custos de IA",
        "caption": (
            "Tokens, custos estimados, duração, "
            "modelos e operações das chamadas "
            "de IA da INNA."
        ),
    },
    "en_us": {
        "title": "💰 AI Cost Center",
        "caption": (
            "Tokens, estimated costs, duration, "
            "models and operations from INNA's "
            "AI calls."
        ),
    },
    "en_gb": {
        "title": "💰 AI Cost Centre",
        "caption": (
            "Tokens, estimated costs, duration, "
            "models and operations from INNA's "
            "AI calls."
        ),
    },
    "es": {
        "title": "💰 Centro de Costos de IA",
        "caption": (
            "Tokens, costos estimados, duración, "
            "modelos y operaciones de las llamadas "
            "de IA de INNA."
        ),
    },
    "fr": {
        "title": "💰 Centre des coûts IA",
        "caption": (
            "Jetons, coûts estimés, durée, modèles "
            "et opérations des appels IA d’INNA."
        ),
    },
    "de": {
        "title": "💰 KI-Kostenzentrale",
        "caption": (
            "Token, geschätzte Kosten, Dauer, "
            "Modelle und Vorgänge der KI-Aufrufe "
            "von INNA."
        ),
    },
    "it": {
        "title": "💰 Centro costi IA",
        "caption": (
            "Token, costi stimati, durata, modelli "
            "e operazioni delle chiamate IA di INNA."
        ),
    },
    "ro": {
        "title": "💰 Centrul costurilor IA",
        "caption": (
            "Tokenuri, costuri estimate, durată, "
            "modele și operațiuni ale apelurilor "
            "IA INNA."
        ),
    },
    "ua": {
        "title": "💰 Центр витрат ШІ",
        "caption": (
            "Токени, орієнтовні витрати, тривалість, "
            "моделі та операції викликів ШІ INNA."
        ),
    },
    "ru": {
        "title": "💰 Центр затрат ИИ",
        "caption": (
            "Токены, расчетные затраты, длительность, "
            "модели и операции вызовов ИИ INNA."
        ),
    },
    "sa": {
        "title": (
            "💰 مركز تكاليف الذكاء الاصطناعي"
        ),
        "caption": (
            "الرموز والتكاليف التقديرية والمدة "
            "والنماذج والعمليات الخاصة باستدعاءات "
            "الذكاء الاصطناعي في INNA."
        ),
    },
}

LLM_COST_PAGE_TEXTS["ch"] = (
    LLM_COST_PAGE_TEXTS["de"]
)


LLM_COST_PAGE_EXTRA_TEXTS = {
    "pt": {
        "period": "Período",
        "period_1_day": "1 dia",
        "period_7_days": "7 dias",
        "period_30_days": "30 dias",
        "period_90_days": "90 dias",
        "period_all": "Todo o histórico",
        "event_limit": "Limite de eventos",
        "refresh": "🔄 Atualizar consumo",
        "load_error": "Não foi possível carregar o consumo.",
        "no_events": (
            "Nenhum evento de consumo de LLM foi "
            "encontrado no período."
        ),
        "models": "Modelos",
        "operations": "Operações",
        "overview": "## Visão geral",
        "calls": "Chamadas",
        "total_tokens": "Tokens totais",
        "input_tokens": "Tokens de entrada",
        "output_tokens": "Tokens de saída",
        "estimated_cost": "Custo estimado",
        "success_rate": "Taxa de sucesso",
        "average_duration": "Duração média",
        "slow_calls": "Chamadas acima de 30 s",
        "prices_not_configured": (
            "Os preços dos modelos ainda não foram configurados. "
            "Tokens e duração estão sendo registrados, mas o custo "
            "permanece zerado."
        ),
        "slow_calls_warning": (
            "Foram encontradas {count} chamada(s) com duração "
            "igual ou superior a 30 segundos."
        ),
        "finops_budget": "## 📊 FinOps e orçamento",
        "accumulated_cost": "Custo acumulado em BRL",
        "average_cost_call": "Custo médio por chamada",
        "monthly_projection": "Projeção mensal",
        "monthly_budget": "Orçamento mensal",
        "budget_usage": "Uso do orçamento",
        "estimated_balance": "Saldo estimado",
        "projection_warning": (
            "A projeção para o final do mês pode ultrapassar "
            "ou se aproximar do orçamento."
        ),
        "finops_recommendations": "Recomendações FinOps",
        "conversion_caption": (
            "A conversão utiliza a cotação configurada de "
            "R$ {rate:.4f} por US$ 1."
        ),
    },
    "en_us": {
        "period": "Period",
        "period_1_day": "1 day",
        "period_7_days": "7 days",
        "period_30_days": "30 days",
        "period_90_days": "90 days",
        "period_all": "All history",
        "event_limit": "Event limit",
        "refresh": "🔄 Refresh consumption",
        "load_error": "Could not load consumption data.",
        "no_events": (
            "No LLM consumption event was found "
            "for the selected period."
        ),
        "models": "Models",
        "operations": "Operations",
        "overview": "## Overview",
        "calls": "Calls",
        "total_tokens": "Total tokens",
        "input_tokens": "Input tokens",
        "output_tokens": "Output tokens",
        "estimated_cost": "Estimated cost",
        "success_rate": "Success rate",
        "average_duration": "Average duration",
        "slow_calls": "Calls over 30 s",
        "prices_not_configured": (
            "Model prices have not been configured yet. "
            "Tokens and duration are being recorded, but the "
            "cost remains zero."
        ),
        "slow_calls_warning": (
            "{count} call(s) lasting 30 seconds or more "
            "were found."
        ),
        "finops_budget": "## 📊 FinOps and budget",
        "accumulated_cost": "Accumulated cost in BRL",
        "average_cost_call": "Average cost per call",
        "monthly_projection": "Monthly projection",
        "monthly_budget": "Monthly budget",
        "budget_usage": "Budget usage",
        "estimated_balance": "Estimated balance",
        "projection_warning": (
            "The end-of-month projection may exceed or approach "
            "the budget."
        ),
        "finops_recommendations": "FinOps recommendations",
        "conversion_caption": (
            "Conversion uses the configured exchange rate of "
            "R$ {rate:.4f} per US$ 1."
        ),
    },
    "es": {
        "period": "Período",
        "period_1_day": "1 día",
        "period_7_days": "7 días",
        "period_30_days": "30 días",
        "period_90_days": "90 días",
        "period_all": "Todo el historial",
        "event_limit": "Límite de eventos",
        "refresh": "🔄 Actualizar consumo",
        "load_error": "No se pudo cargar el consumo.",
        "no_events": (
            "No se encontraron eventos de consumo de LLM "
            "en el período seleccionado."
        ),
        "models": "Modelos",
        "operations": "Operaciones",
        "overview": "## Vista general",
        "calls": "Llamadas",
        "total_tokens": "Tokens totales",
        "input_tokens": "Tokens de entrada",
        "output_tokens": "Tokens de salida",
        "estimated_cost": "Costo estimado",
        "success_rate": "Tasa de éxito",
        "average_duration": "Duración media",
        "slow_calls": "Llamadas superiores a 30 s",
        "prices_not_configured": (
            "Los precios de los modelos aún no están configurados. "
            "Se registran tokens y duración, pero el costo sigue "
            "siendo cero."
        ),
        "slow_calls_warning": (
            "Se encontraron {count} llamada(s) con una duración "
            "igual o superior a 30 segundos."
        ),
        "finops_budget": "## 📊 FinOps y presupuesto",
        "accumulated_cost": "Costo acumulado en BRL",
        "average_cost_call": "Costo medio por llamada",
        "monthly_projection": "Proyección mensual",
        "monthly_budget": "Presupuesto mensual",
        "budget_usage": "Uso del presupuesto",
        "estimated_balance": "Saldo estimado",
        "projection_warning": (
            "La proyección de fin de mes puede superar o "
            "aproximarse al presupuesto."
        ),
        "finops_recommendations": "Recomendaciones FinOps",
        "conversion_caption": (
            "La conversión utiliza el tipo configurado de "
            "R$ {rate:.4f} por US$ 1."
        ),
    },
    "fr": {
        "period": "Période",
        "period_1_day": "1 jour",
        "period_7_days": "7 jours",
        "period_30_days": "30 jours",
        "period_90_days": "90 jours",
        "period_all": "Tout l’historique",
        "event_limit": "Limite d’événements",
        "refresh": "🔄 Actualiser la consommation",
        "load_error": "Impossible de charger la consommation.",
        "no_events": (
            "Aucun événement de consommation LLM n’a été trouvé "
            "pour la période sélectionnée."
        ),
        "models": "Modèles",
        "operations": "Opérations",
        "overview": "## Vue d’ensemble",
        "calls": "Appels",
        "total_tokens": "Jetons totaux",
        "input_tokens": "Jetons d’entrée",
        "output_tokens": "Jetons de sortie",
        "estimated_cost": "Coût estimé",
        "success_rate": "Taux de réussite",
        "average_duration": "Durée moyenne",
        "slow_calls": "Appels de plus de 30 s",
        "prices_not_configured": (
            "Les prix des modèles ne sont pas encore configurés. "
            "Les jetons et la durée sont enregistrés, mais le coût "
            "reste nul."
        ),
        "slow_calls_warning": (
            "{count} appel(s) d’une durée supérieure ou égale "
            "à 30 secondes ont été détectés."
        ),
        "finops_budget": "## 📊 FinOps et budget",
        "accumulated_cost": "Coût cumulé en BRL",
        "average_cost_call": "Coût moyen par appel",
        "monthly_projection": "Projection mensuelle",
        "monthly_budget": "Budget mensuel",
        "budget_usage": "Utilisation du budget",
        "estimated_balance": "Solde estimé",
        "projection_warning": (
            "La projection de fin de mois peut dépasser ou "
            "approcher le budget."
        ),
        "finops_recommendations": "Recommandations FinOps",
        "conversion_caption": (
            "La conversion utilise le taux configuré de "
            "R$ {rate:.4f} pour US$ 1."
        ),
    },
    "de": {
        "period": "Zeitraum",
        "period_1_day": "1 Tag",
        "period_7_days": "7 Tage",
        "period_30_days": "30 Tage",
        "period_90_days": "90 Tage",
        "period_all": "Gesamter Verlauf",
        "event_limit": "Ereignislimit",
        "refresh": "🔄 Verbrauch aktualisieren",
        "load_error": "Verbrauchsdaten konnten nicht geladen werden.",
        "no_events": (
            "Für den ausgewählten Zeitraum wurden keine "
            "LLM-Verbrauchsereignisse gefunden."
        ),
        "models": "Modelle",
        "operations": "Vorgänge",
        "overview": "## Übersicht",
        "calls": "Aufrufe",
        "total_tokens": "Token gesamt",
        "input_tokens": "Eingabe-Token",
        "output_tokens": "Ausgabe-Token",
        "estimated_cost": "Geschätzte Kosten",
        "success_rate": "Erfolgsquote",
        "average_duration": "Durchschnittliche Dauer",
        "slow_calls": "Aufrufe über 30 s",
        "prices_not_configured": (
            "Die Modellpreise wurden noch nicht konfiguriert. "
            "Token und Dauer werden erfasst, die Kosten bleiben "
            "jedoch null."
        ),
        "slow_calls_warning": (
            "{count} Aufruf(e) mit einer Dauer von mindestens "
            "30 Sekunden wurden gefunden."
        ),
        "finops_budget": "## 📊 FinOps und Budget",
        "accumulated_cost": "Kumulierte Kosten in BRL",
        "average_cost_call": "Durchschnittskosten pro Aufruf",
        "monthly_projection": "Monatsprognose",
        "monthly_budget": "Monatsbudget",
        "budget_usage": "Budgetnutzung",
        "estimated_balance": "Geschätzter Saldo",
        "projection_warning": (
            "Die Monatsendprognose kann das Budget überschreiten "
            "oder sich ihm nähern."
        ),
        "finops_recommendations": "FinOps-Empfehlungen",
        "conversion_caption": (
            "Die Umrechnung verwendet den konfigurierten Kurs "
            "von R$ {rate:.4f} je US$ 1."
        ),
    },
    "it": {
        "period": "Periodo",
        "period_1_day": "1 giorno",
        "period_7_days": "7 giorni",
        "period_30_days": "30 giorni",
        "period_90_days": "90 giorni",
        "period_all": "Tutta la cronologia",
        "event_limit": "Limite eventi",
        "refresh": "🔄 Aggiorna consumo",
        "load_error": "Impossibile caricare i consumi.",
        "no_events": (
            "Nessun evento di consumo LLM trovato "
            "nel periodo selezionato."
        ),
        "models": "Modelli",
        "operations": "Operazioni",
        "overview": "## Panoramica",
        "calls": "Chiamate",
        "total_tokens": "Token totali",
        "input_tokens": "Token di input",
        "output_tokens": "Token di output",
        "estimated_cost": "Costo stimato",
        "success_rate": "Tasso di successo",
        "average_duration": "Durata media",
        "slow_calls": "Chiamate oltre 30 s",
        "prices_not_configured": (
            "I prezzi dei modelli non sono ancora configurati. "
            "Token e durata vengono registrati, ma il costo "
            "rimane zero."
        ),
        "slow_calls_warning": (
            "Sono state trovate {count} chiamata/e con durata "
            "uguale o superiore a 30 secondi."
        ),
        "finops_budget": "## 📊 FinOps e budget",
        "accumulated_cost": "Costo accumulato in BRL",
        "average_cost_call": "Costo medio per chiamata",
        "monthly_projection": "Proiezione mensile",
        "monthly_budget": "Budget mensile",
        "budget_usage": "Utilizzo del budget",
        "estimated_balance": "Saldo stimato",
        "projection_warning": (
            "La proiezione di fine mese può superare o "
            "avvicinarsi al budget."
        ),
        "finops_recommendations": "Raccomandazioni FinOps",
        "conversion_caption": (
            "La conversione utilizza il cambio configurato di "
            "R$ {rate:.4f} per US$ 1."
        ),
    },
    "ro": {
        "period": "Perioadă",
        "period_1_day": "1 zi",
        "period_7_days": "7 zile",
        "period_30_days": "30 de zile",
        "period_90_days": "90 de zile",
        "period_all": "Tot istoricul",
        "event_limit": "Limită de evenimente",
        "refresh": "🔄 Actualizează consumul",
        "load_error": "Consumul nu a putut fi încărcat.",
        "no_events": (
            "Nu a fost găsit niciun eveniment de consum LLM "
            "în perioada selectată."
        ),
        "models": "Modele",
        "operations": "Operațiuni",
        "overview": "## Prezentare generală",
        "calls": "Apeluri",
        "total_tokens": "Total tokenuri",
        "input_tokens": "Tokenuri de intrare",
        "output_tokens": "Tokenuri de ieșire",
        "estimated_cost": "Cost estimat",
        "success_rate": "Rată de succes",
        "average_duration": "Durată medie",
        "slow_calls": "Apeluri peste 30 s",
        "prices_not_configured": (
            "Prețurile modelelor nu au fost încă configurate. "
            "Tokenurile și durata sunt înregistrate, dar costul "
            "rămâne zero."
        ),
        "slow_calls_warning": (
            "Au fost găsite {count} apeluri cu durata de cel "
            "puțin 30 de secunde."
        ),
        "finops_budget": "## 📊 FinOps și buget",
        "accumulated_cost": "Cost acumulat în BRL",
        "average_cost_call": "Cost mediu per apel",
        "monthly_projection": "Proiecție lunară",
        "monthly_budget": "Buget lunar",
        "budget_usage": "Utilizarea bugetului",
        "estimated_balance": "Sold estimat",
        "projection_warning": (
            "Proiecția pentru sfârșitul lunii poate depăși "
            "sau se poate apropia de buget."
        ),
        "finops_recommendations": "Recomandări FinOps",
        "conversion_caption": (
            "Conversia utilizează cursul configurat de "
            "R$ {rate:.4f} pentru US$ 1."
        ),
    },
    "ua": {
        "period": "Період",
        "period_1_day": "1 день",
        "period_7_days": "7 днів",
        "period_30_days": "30 днів",
        "period_90_days": "90 днів",
        "period_all": "Уся історія",
        "event_limit": "Ліміт подій",
        "refresh": "🔄 Оновити споживання",
        "load_error": "Не вдалося завантажити споживання.",
        "no_events": (
            "За вибраний період не знайдено подій "
            "споживання LLM."
        ),
        "models": "Моделі",
        "operations": "Операції",
        "overview": "## Огляд",
        "calls": "Виклики",
        "total_tokens": "Усього токенів",
        "input_tokens": "Вхідні токени",
        "output_tokens": "Вихідні токени",
        "estimated_cost": "Орієнтовна вартість",
        "success_rate": "Рівень успішності",
        "average_duration": "Середня тривалість",
        "slow_calls": "Виклики понад 30 с",
        "prices_not_configured": (
            "Ціни моделей ще не налаштовані. Токени та "
            "тривалість записуються, але вартість залишається "
            "нульовою."
        ),
        "slow_calls_warning": (
            "Знайдено викликів тривалістю не менше "
            "30 секунд: {count}."
        ),
        "finops_budget": "## 📊 FinOps і бюджет",
        "accumulated_cost": "Накопичена вартість у BRL",
        "average_cost_call": "Середня вартість виклику",
        "monthly_projection": "Місячний прогноз",
        "monthly_budget": "Місячний бюджет",
        "budget_usage": "Використання бюджету",
        "estimated_balance": "Орієнтовний залишок",
        "projection_warning": (
            "Прогноз на кінець місяця може перевищити "
            "бюджет або наблизитися до нього."
        ),
        "finops_recommendations": "Рекомендації FinOps",
        "conversion_caption": (
            "Конвертація використовує налаштований курс "
            "R$ {rate:.4f} за US$ 1."
        ),
    },
    "ru": {
        "period": "Период",
        "period_1_day": "1 день",
        "period_7_days": "7 дней",
        "period_30_days": "30 дней",
        "period_90_days": "90 дней",
        "period_all": "Вся история",
        "event_limit": "Лимит событий",
        "refresh": "🔄 Обновить потребление",
        "load_error": "Не удалось загрузить данные потребления.",
        "no_events": (
            "За выбранный период события потребления "
            "LLM не найдены."
        ),
        "models": "Модели",
        "operations": "Операции",
        "overview": "## Обзор",
        "calls": "Вызовы",
        "total_tokens": "Всего токенов",
        "input_tokens": "Входные токены",
        "output_tokens": "Выходные токены",
        "estimated_cost": "Расчетная стоимость",
        "success_rate": "Процент успеха",
        "average_duration": "Средняя длительность",
        "slow_calls": "Вызовы свыше 30 с",
        "prices_not_configured": (
            "Цены моделей еще не настроены. Токены и "
            "длительность регистрируются, но стоимость "
            "остается нулевой."
        ),
        "slow_calls_warning": (
            "Найдено вызовов длительностью не менее "
            "30 секунд: {count}."
        ),
        "finops_budget": "## 📊 FinOps и бюджет",
        "accumulated_cost": "Накопленная стоимость в BRL",
        "average_cost_call": "Средняя стоимость вызова",
        "monthly_projection": "Месячный прогноз",
        "monthly_budget": "Месячный бюджет",
        "budget_usage": "Использование бюджета",
        "estimated_balance": "Расчетный остаток",
        "projection_warning": (
            "Прогноз на конец месяца может превысить "
            "бюджет или приблизиться к нему."
        ),
        "finops_recommendations": "Рекомендации FinOps",
        "conversion_caption": (
            "Конвертация использует настроенный курс "
            "R$ {rate:.4f} за US$ 1."
        ),
    },
    "sa": {
        "period": "الفترة",
        "period_1_day": "يوم واحد",
        "period_7_days": "7 أيام",
        "period_30_days": "30 يومًا",
        "period_90_days": "90 يومًا",
        "period_all": "كل السجل",
        "event_limit": "حد الأحداث",
        "refresh": "🔄 تحديث الاستهلاك",
        "load_error": "تعذر تحميل بيانات الاستهلاك.",
        "no_events": (
            "لم يتم العثور على أحداث استهلاك LLM "
            "في الفترة المحددة."
        ),
        "models": "النماذج",
        "operations": "العمليات",
        "overview": "## نظرة عامة",
        "calls": "الاستدعاءات",
        "total_tokens": "إجمالي الرموز",
        "input_tokens": "رموز الإدخال",
        "output_tokens": "رموز الإخراج",
        "estimated_cost": "التكلفة التقديرية",
        "success_rate": "معدل النجاح",
        "average_duration": "متوسط المدة",
        "slow_calls": "استدعاءات أطول من 30 ثانية",
        "prices_not_configured": (
            "لم يتم إعداد أسعار النماذج بعد. يتم تسجيل "
            "الرموز والمدة، لكن التكلفة ما زالت صفرًا."
        ),
        "slow_calls_warning": (
            "تم العثور على {count} استدعاء بمدة تساوي "
            "أو تتجاوز 30 ثانية."
        ),
        "finops_budget": "## 📊 العمليات المالية والميزانية",
        "accumulated_cost": "التكلفة المتراكمة بعملة BRL",
        "average_cost_call": "متوسط التكلفة لكل استدعاء",
        "monthly_projection": "التوقع الشهري",
        "monthly_budget": "الميزانية الشهرية",
        "budget_usage": "استخدام الميزانية",
        "estimated_balance": "الرصيد التقديري",
        "projection_warning": (
            "قد يتجاوز توقع نهاية الشهر الميزانية "
            "أو يقترب منها."
        ),
        "finops_recommendations": "توصيات FinOps",
        "conversion_caption": (
            "يستخدم التحويل السعر المضبوط وهو "
            "R$ {rate:.4f} لكل US$ 1."
        ),
    },
}

LLM_COST_PAGE_EXTRA_TEXTS["en_gb"] = (
    LLM_COST_PAGE_EXTRA_TEXTS["en_us"]
)
LLM_COST_PAGE_EXTRA_TEXTS["ch"] = (
    LLM_COST_PAGE_EXTRA_TEXTS["de"]
)

for language_key, extra_texts in (
    LLM_COST_PAGE_EXTRA_TEXTS.items()
):
    LLM_COST_PAGE_TEXTS.setdefault(
        language_key,
        {},
    ).update(extra_texts)



LLM_COST_PAGE_LOWER_TEXTS = {
    "pt": {
        "consumption_by_model": "## Consumo por modelo",
        "consumption_by_operation": "## Consumo por operação",
        "temporal_evolution": "## Evolução temporal",
        "tokens_per_hour": "### Tokens por hora",
        "average_duration_per_hour": (
            "### Duração média por hora"
        ),
        "calls_audit": "## Auditoria das chamadas",
        "consumed_tokens": "Tokens consumidos",
        "average_duration_seconds": (
            "Duração média (s)"
        ),
        "average_duration_hover": "Duração média",
        "operation_column": "Operação",
        "download_csv": "⬇️ Exportar consumo em CSV",
        "telemetry_privacy": (
            "🔒 Privacidade da telemetria"
        ),
        "telemetry_text": """
A telemetria registra apenas informações técnicas:

- modelo;
- quantidade de tokens;
- duração;
- operação;
- sucesso ou falha;
- custo estimado;
- identificadores técnicos opcionais.

O prompt, a pergunta do usuário e a resposta do Gemini
não são armazenados nesta tabela.
""",
    },
    "en_us": {
        "consumption_by_model": "## Consumption by model",
        "consumption_by_operation": (
            "## Consumption by operation"
        ),
        "temporal_evolution": "## Temporal evolution",
        "tokens_per_hour": "### Tokens per hour",
        "average_duration_per_hour": (
            "### Average duration per hour"
        ),
        "calls_audit": "## Call audit",
        "consumed_tokens": "Consumed tokens",
        "average_duration_seconds": (
            "Average duration (s)"
        ),
        "average_duration_hover": "Average duration",
        "operation_column": "Operation",
        "download_csv": "⬇️ Export consumption as CSV",
        "telemetry_privacy": "🔒 Telemetry privacy",
        "telemetry_text": """
Telemetry records technical information only:

- model;
- token count;
- duration;
- operation;
- success or failure;
- estimated cost;
- optional technical identifiers.

The prompt, the user's question, and Gemini's response
are not stored in this table.
""",
    },
    "es": {
        "consumption_by_model": "## Consumo por modelo",
        "consumption_by_operation": (
            "## Consumo por operación"
        ),
        "temporal_evolution": "## Evolución temporal",
        "tokens_per_hour": "### Tokens por hora",
        "average_duration_per_hour": (
            "### Duración media por hora"
        ),
        "calls_audit": "## Auditoría de llamadas",
        "consumed_tokens": "Tokens consumidos",
        "average_duration_seconds": (
            "Duración media (s)"
        ),
        "average_duration_hover": "Duración media",
        "operation_column": "Operación",
        "download_csv": "⬇️ Exportar consumo en CSV",
        "telemetry_privacy": (
            "🔒 Privacidad de la telemetría"
        ),
        "telemetry_text": """
La telemetría registra únicamente información técnica:

- modelo;
- cantidad de tokens;
- duración;
- operación;
- éxito o fallo;
- costo estimado;
- identificadores técnicos opcionales.

El prompt, la pregunta del usuario y la respuesta de Gemini
no se almacenan en esta tabla.
""",
    },
    "fr": {
        "consumption_by_model": (
            "## Consommation par modèle"
        ),
        "consumption_by_operation": (
            "## Consommation par opération"
        ),
        "temporal_evolution": "## Évolution temporelle",
        "tokens_per_hour": "### Jetons par heure",
        "average_duration_per_hour": (
            "### Durée moyenne par heure"
        ),
        "calls_audit": "## Audit des appels",
        "consumed_tokens": "Jetons consommés",
        "average_duration_seconds": (
            "Durée moyenne (s)"
        ),
        "average_duration_hover": "Durée moyenne",
        "operation_column": "Opération",
        "download_csv": (
            "⬇️ Exporter la consommation en CSV"
        ),
        "telemetry_privacy": (
            "🔒 Confidentialité de la télémétrie"
        ),
        "telemetry_text": """
La télémétrie enregistre uniquement des informations techniques :

- modèle ;
- nombre de jetons ;
- durée ;
- opération ;
- succès ou échec ;
- coût estimé ;
- identifiants techniques facultatifs.

Le prompt, la question de l’utilisateur et la réponse de Gemini
ne sont pas stockés dans ce tableau.
""",
    },
    "de": {
        "consumption_by_model": (
            "## Verbrauch nach Modell"
        ),
        "consumption_by_operation": (
            "## Verbrauch nach Vorgang"
        ),
        "temporal_evolution": "## Zeitliche Entwicklung",
        "tokens_per_hour": "### Token pro Stunde",
        "average_duration_per_hour": (
            "### Durchschnittliche Dauer pro Stunde"
        ),
        "calls_audit": "## Aufrufprüfung",
        "consumed_tokens": "Verbrauchte Token",
        "average_duration_seconds": (
            "Durchschnittliche Dauer (s)"
        ),
        "average_duration_hover": (
            "Durchschnittliche Dauer"
        ),
        "operation_column": "Vorgang",
        "download_csv": (
            "⬇️ Verbrauch als CSV exportieren"
        ),
        "telemetry_privacy": (
            "🔒 Datenschutz der Telemetrie"
        ),
        "telemetry_text": """
Die Telemetrie erfasst ausschließlich technische Informationen:

- Modell;
- Anzahl der Token;
- Dauer;
- Vorgang;
- Erfolg oder Fehler;
- geschätzte Kosten;
- optionale technische Kennungen.

Der Prompt, die Frage des Benutzers und die Antwort von Gemini
werden nicht in dieser Tabelle gespeichert.
""",
    },
    "it": {
        "consumption_by_model": (
            "## Consumo per modello"
        ),
        "consumption_by_operation": (
            "## Consumo per operazione"
        ),
        "temporal_evolution": "## Evoluzione temporale",
        "tokens_per_hour": "### Token per ora",
        "average_duration_per_hour": (
            "### Durata media per ora"
        ),
        "calls_audit": "## Audit delle chiamate",
        "consumed_tokens": "Token consumati",
        "average_duration_seconds": (
            "Durata media (s)"
        ),
        "average_duration_hover": "Durata media",
        "operation_column": "Operazione",
        "download_csv": (
            "⬇️ Esporta il consumo in CSV"
        ),
        "telemetry_privacy": (
            "🔒 Privacy della telemetria"
        ),
        "telemetry_text": """
La telemetria registra solo informazioni tecniche:

- modello;
- quantità di token;
- durata;
- operazione;
- successo o errore;
- costo stimato;
- identificatori tecnici facoltativi.

Il prompt, la domanda dell’utente e la risposta di Gemini
non vengono memorizzati in questa tabella.
""",
    },
    "ro": {
        "consumption_by_model": (
            "## Consum pe model"
        ),
        "consumption_by_operation": (
            "## Consum pe operațiune"
        ),
        "temporal_evolution": "## Evoluție temporală",
        "tokens_per_hour": "### Tokenuri pe oră",
        "average_duration_per_hour": (
            "### Durată medie pe oră"
        ),
        "calls_audit": "## Auditul apelurilor",
        "consumed_tokens": "Tokenuri consumate",
        "average_duration_seconds": (
            "Durată medie (s)"
        ),
        "average_duration_hover": "Durată medie",
        "operation_column": "Operațiune",
        "download_csv": "⬇️ Exportă consumul în CSV",
        "telemetry_privacy": (
            "🔒 Confidențialitatea telemetriei"
        ),
        "telemetry_text": """
Telemetria înregistrează numai informații tehnice:

- model;
- număr de tokenuri;
- durată;
- operațiune;
- succes sau eșec;
- cost estimat;
- identificatori tehnici opționali.

Promptul, întrebarea utilizatorului și răspunsul Gemini
nu sunt stocate în acest tabel.
""",
    },
    "ua": {
        "consumption_by_model": (
            "## Споживання за моделлю"
        ),
        "consumption_by_operation": (
            "## Споживання за операцією"
        ),
        "temporal_evolution": "## Часова динаміка",
        "tokens_per_hour": "### Токени за годину",
        "average_duration_per_hour": (
            "### Середня тривалість за годину"
        ),
        "calls_audit": "## Аудит викликів",
        "consumed_tokens": "Використані токени",
        "average_duration_seconds": (
            "Середня тривалість (с)"
        ),
        "average_duration_hover": (
            "Середня тривалість"
        ),
        "operation_column": "Операція",
        "download_csv": (
            "⬇️ Експортувати споживання у CSV"
        ),
        "telemetry_privacy": (
            "🔒 Конфіденційність телеметрії"
        ),
        "telemetry_text": """
Телеметрія записує лише технічну інформацію:

- модель;
- кількість токенів;
- тривалість;
- операція;
- успіх або помилка;
- орієнтовна вартість;
- необов’язкові технічні ідентифікатори.

Промпт, запитання користувача та відповідь Gemini
не зберігаються в цій таблиці.
""",
    },
    "ru": {
        "consumption_by_model": (
            "## Потребление по моделям"
        ),
        "consumption_by_operation": (
            "## Потребление по операциям"
        ),
        "temporal_evolution": "## Динамика во времени",
        "tokens_per_hour": "### Токены по часам",
        "average_duration_per_hour": (
            "### Средняя длительность по часам"
        ),
        "calls_audit": "## Аудит вызовов",
        "consumed_tokens": "Использованные токены",
        "average_duration_seconds": (
            "Средняя длительность (с)"
        ),
        "average_duration_hover": (
            "Средняя длительность"
        ),
        "operation_column": "Операция",
        "download_csv": (
            "⬇️ Экспортировать потребление в CSV"
        ),
        "telemetry_privacy": (
            "🔒 Конфиденциальность телеметрии"
        ),
        "telemetry_text": """
Телеметрия записывает только техническую информацию:

- модель;
- количество токенов;
- длительность;
- операция;
- успех или ошибка;
- расчетная стоимость;
- необязательные технические идентификаторы.

Промпт, вопрос пользователя и ответ Gemini
не сохраняются в этой таблице.
""",
    },
    "sa": {
        "consumption_by_model": (
            "## الاستهلاك حسب النموذج"
        ),
        "consumption_by_operation": (
            "## الاستهلاك حسب العملية"
        ),
        "temporal_evolution": "## التطور الزمني",
        "tokens_per_hour": "### الرموز لكل ساعة",
        "average_duration_per_hour": (
            "### متوسط المدة لكل ساعة"
        ),
        "calls_audit": "## تدقيق الاستدعاءات",
        "consumed_tokens": "الرموز المستهلكة",
        "average_duration_seconds": (
            "متوسط المدة (ث)"
        ),
        "average_duration_hover": "متوسط المدة",
        "operation_column": "العملية",
        "download_csv": (
            "⬇️ تصدير الاستهلاك بصيغة CSV"
        ),
        "telemetry_privacy": (
            "🔒 خصوصية القياس عن بعد"
        ),
        "telemetry_text": """
يسجل القياس عن بعد المعلومات التقنية فقط:

- النموذج؛
- عدد الرموز؛
- المدة؛
- العملية؛
- النجاح أو الفشل؛
- التكلفة التقديرية؛
- المعرفات التقنية الاختيارية.

لا يتم تخزين الموجه أو سؤال المستخدم أو إجابة Gemini
في هذا الجدول.
""",
    },
}

LLM_COST_PAGE_LOWER_TEXTS["en_gb"] = (
    LLM_COST_PAGE_LOWER_TEXTS["en_us"]
)

LLM_COST_PAGE_LOWER_TEXTS["ch"] = (
    LLM_COST_PAGE_LOWER_TEXTS["de"]
)

for language_key, lower_texts in (
    LLM_COST_PAGE_LOWER_TEXTS.items()
):
    LLM_COST_PAGE_TEXTS.setdefault(
        language_key,
        {},
    ).update(lower_texts)


# Ajuste final de terminologia nativa da seção de alertas.
LLM_ALERT_SECTION_TEXTS["it"].update(
    {
        "database": "Banca dati",
    }
)

LLM_ALERT_SECTION_DYNAMIC_TEXTS["it"].update(
    {
        "database": "Banca dati",
    }
)

# O código ch continua seguindo o alemão do projeto.
LLM_ALERT_SECTION_TEXTS["ch"] = dict(
    LLM_ALERT_SECTION_TEXTS["de"]
)

LLM_ALERT_SECTION_DYNAMIC_TEXTS["ch"] = dict(
    LLM_ALERT_SECTION_DYNAMIC_TEXTS["de"]
)


def llm_cost_page_t(
    key: str,
    default: str | None = None,
) -> str:
    """Traduz título e legenda da página."""
    idioma = llm_table_lang()

    return LLM_COST_PAGE_TEXTS.get(
        idioma,
        LLM_COST_PAGE_TEXTS["pt"],
    ).get(
        key,
        default or key,
    )


def render_llm_costs_page() -> None:
    """
    Renderiza o LLM Cost Center.
    """
    try:
        from observability.llm_costs import (
            carregar_consumo_llm,
        )
    except ImportError:
        from src.observability.llm_costs import (
            carregar_consumo_llm,
        )

    st.title(
        llm_cost_page_t("title")
    )

    st.caption(
        llm_cost_page_t("caption")
    )

    controle_1, controle_2, controle_3 = (
        st.columns(
            [1, 1, 2]
        )
    )

    period_keys = [
        "period_1_day",
        "period_7_days",
        "period_30_days",
        "period_90_days",
        "period_all",
    ]

    periodo_key = controle_1.selectbox(
        llm_cost_page_t("period"),
        options=period_keys,
        format_func=llm_cost_page_t,
        index=2,
        key="llm_cost_period",
    )

    limite = controle_2.selectbox(
        llm_cost_page_t("event_limit"),
        options=[
            100,
            250,
            500,
            1000,
            5000,
        ],
        index=3,
        key="llm_cost_limit",
    )

    with controle_3:
        st.write("")

        if st.button(
            llm_cost_page_t("refresh"),
            use_container_width=True,
            key="llm_cost_refresh",
        ):
            st.rerun()

    periodos = {
        "period_1_day": 1,
        "period_7_days": 7,
        "period_30_days": 30,
        "period_90_days": 90,
        "period_all": None,
    }

    resultado = carregar_consumo_llm(
        limite=int(limite),
        dias=periodos[periodo_key],
    )

    if not resultado.get("ok"):
        st.error(
            resultado.get(
                "message",
                llm_cost_page_t("load_error"),
            )
        )
        return

    base = preparar_consumo_exibicao(
        resultado.get("df")
    )

    if base.empty:
        st.info(
            llm_cost_page_t("no_events")
        )
        return

    modelos = sorted(
        base["modelo"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    operacoes = sorted(
        base["operacao"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    filtro_1, filtro_2 = st.columns(2)

    modelos_escolhidos = filtro_1.multiselect(
        llm_cost_page_t("models"),
        options=modelos,
        default=modelos,
        key="llm_cost_models",
    )

    operacoes_escolhidas = filtro_2.multiselect(
        llm_cost_page_t("operations"),
        options=operacoes,
        default=operacoes,
        key="llm_cost_operations",
    )

    filtrado = base[
        base["modelo"].isin(
            modelos_escolhidos
        )
        & base["operacao"].isin(
            operacoes_escolhidas
        )
    ].copy()

    resumo = resumir_consumo_llm(
        filtrado
    )

    st.markdown(
        llm_cost_page_t("overview")
    )

    linha_1 = st.columns(5)

    linha_1[0].metric(
        llm_cost_page_t("calls"),
        resumo["eventos"],
    )

    linha_1[1].metric(
        llm_cost_page_t("total_tokens"),
        f"{resumo['tokens_totais']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[2].metric(
        llm_cost_page_t("input_tokens"),
        f"{resumo['tokens_entrada']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[3].metric(
        llm_cost_page_t("output_tokens"),
        f"{resumo['tokens_saida']:,}".replace(
            ",",
            ".",
        ),
    )

    linha_1[4].metric(
        llm_cost_page_t("estimated_cost"),
        (
            f"US$ "
            f"{resumo['custo_total_usd']:.6f}"
        ),
    )

    linha_2 = st.columns(4)

    linha_2[0].metric(
        llm_cost_page_t("success_rate"),
        f"{resumo['taxa_sucesso']:.2f}%",
    )

    linha_2[1].metric(
        llm_cost_page_t("average_duration"),
        (
            f"{resumo['duracao_media_ms'] / 1000:.2f} s"
        ),
    )

    linha_2[2].metric(
        "P95",
        (
            f"{resumo['duracao_p95_ms'] / 1000:.2f} s"
        ),
    )

    chamadas_lentas = int(
        (
            filtrado["duracao_ms"]
            >= 30000
        ).sum()
    )

    linha_2[3].metric(
        llm_cost_page_t("slow_calls"),
        chamadas_lentas,
    )

    if resumo["custo_total_usd"] == 0:
        st.warning(
            llm_cost_page_t(
                "prices_not_configured"
            )
        )

    if chamadas_lentas > 0:
        st.warning(
            llm_cost_page_t(
                "slow_calls_warning"
            ).format(
                count=chamadas_lentas
            )
        )

    st.divider()
    st.markdown(
        llm_cost_page_t("finops_budget")
    )

    try:
        from observability.llm_finops import (
            analisar_finops_llm,
        )
    except ImportError:
        from src.observability.llm_finops import (
            analisar_finops_llm,
        )

    finops = analisar_finops_llm(
        filtrado
    )

    config_finops = finops[
        "configuracao"
    ]

    situacao = finops[
        "situacao_orcamento"
    ]

    situacao_projecao = finops[
        "situacao_projecao"
    ]

    finops_cols = st.columns(5)

    finops_cols[0].metric(
        llm_cost_page_t("accumulated_cost"),
        (
            f"R$ "
            f"{finops['custo_acumulado_brl']:.4f}"
        ),
    )

    finops_cols[1].metric(
        llm_cost_page_t("average_cost_call"),
        (
            f"R$ "
            f"{finops['custo_medio_chamada_brl']:.4f}"
        ),
    )

    finops_cols[2].metric(
        llm_cost_page_t("monthly_projection"),
        (
            f"R$ "
            f"{finops['projecao_mensal_brl']:.2f}"
        ),
    )

    finops_cols[3].metric(
        llm_cost_page_t("monthly_budget"),
        (
            f"R$ "
            f"{config_finops['orcamento_mensal_brl']:.2f}"
        ),
    )

    finops_cols[4].metric(
        llm_cost_page_t("budget_usage"),
        (
            f"{situacao['percentual_utilizado']:.2f}%"
        ),
    )

    percentual_barra = max(
        0.0,
        min(
            situacao[
                "percentual_utilizado"
            ] / 100,
            1.0,
        ),
    )

    st.progress(
        percentual_barra
    )

    mensagem_orcamento = (
        f"{situacao['icone']} "
        f"{situacao['classificacao']}. "
        f"{llm_cost_page_t('estimated_balance')}: US$ "
        f"{situacao['saldo']:.4f}."
    )

    if situacao["status"] in {
        "critico",
        "excedido",
    }:
        st.error(
            mensagem_orcamento
        )

    elif situacao["status"] == "alerta":
        st.warning(
            mensagem_orcamento
        )

    else:
        st.success(
            mensagem_orcamento
        )

    if situacao_projecao["status"] in {
        "critico",
        "excedido",
    }:
        st.warning(
            llm_cost_page_t(
                "projection_warning"
            )
        )

    with st.expander(
        llm_cost_page_t(
            "finops_recommendations"
        ),
        expanded=False,
    ):
        for recomendacao in finops[
            "recomendacoes"
        ]:
            st.markdown(
                f"- {recomendacao}"
            )

        st.caption(
            llm_cost_page_t(
                "conversion_caption"
            ).format(
                rate=config_finops[
                    "cotacao_usd_brl"
                ]
            )
        )

    render_alertas_llm_section(
        base_consumo=filtrado,
        finops=finops,
    )

    st.divider()
    st.markdown(
        llm_cost_page_t(
            "consumption_by_model"
        )
    )

    por_modelo = (
        filtrado.groupby(
            "modelo",
            as_index=False,
        )
        .agg(
            Chamadas=("id", "count"),
            Tokens=("tokens_totais", "sum"),
            Custo_USD=(
                "custo_total_usd",
                "sum",
            ),
            Duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
        )
    )

    por_modelo[
        "Duração média (s)"
    ] = (
        por_modelo[
            "Duracao_media_ms"
        ]
        / 1000
    ).round(2)

    coluna_modelo = llm_table_t("model")
    coluna_chamadas = llm_table_t("calls")
    coluna_tokens = llm_table_t("tokens")
    coluna_custo = llm_table_t("cost_usd")
    coluna_duracao = llm_table_t(
        "avg_duration"
    )

    tabela_modelos = (
        por_modelo[
            [
                "modelo",
                "Chamadas",
                "Tokens",
                "Custo_USD",
                "Duração média (s)",
            ]
        ]
        .sort_values(
            "Tokens",
            ascending=False,
        )
        .rename(
            columns={
                "modelo": coluna_modelo,
                "Chamadas": coluna_chamadas,
                "Tokens": coluna_tokens,
                "Custo_USD": coluna_custo,
                "Duração média (s)": (
                    coluna_duracao
                ),
            }
        )
        .reset_index(drop=True)
    )

    st.dataframe(
        estilizar_tabela_llm_costs(
            tabela_modelos
        ),
        use_container_width=True,
        hide_index=True,
        height=300,
        column_config={
            coluna_modelo: (
                st.column_config.TextColumn(
                    coluna_modelo,
                    help=llm_table_t(
                        "model_help"
                    ),
                    width="large",
                )
            ),
            coluna_chamadas: (
                st.column_config.NumberColumn(
                    coluna_chamadas,
                    help=llm_table_t(
                        "calls_help"
                    ),
                    format="%d",
                    width="small",
                )
            ),
            coluna_tokens: (
                st.column_config.ProgressColumn(
                    coluna_tokens,
                    help=llm_table_t(
                        "tokens_help"
                    ),
                    min_value=0,
                    max_value=max(
                        int(
                            tabela_modelos[
                                coluna_tokens
                            ].max()
                        ),
                        1,
                    ),
                    format="%d",
                    width="medium",
                )
            ),
            coluna_custo: (
                st.column_config.NumberColumn(
                    coluna_custo,
                    help=llm_table_t(
                        "cost_help"
                    ),
                    format="US$ %.6f",
                    width="medium",
                )
            ),
            coluna_duracao: (
                st.column_config.NumberColumn(
                    coluna_duracao,
                    help=llm_table_t(
                        "duration_help"
                    ),
                    format="%.2f s",
                    width="medium",
                )
            ),
        },
    )

    modelos_grafico = por_modelo.sort_values(
        "Tokens",
        ascending=True,
    ).copy()

    fig_modelos = px.bar(
        modelos_grafico,
        x="Tokens",
        y="modelo",
        orientation="h",
        text="Tokens",
        color="Tokens",
        color_continuous_scale=[
            "#172554",
            "#2563EB",
            "#38BDF8",
        ],
    )

    fig_modelos.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Tokens: %{x:,.0f}"
            "<extra></extra>"
        ),
    )

    fig_modelos.update_layout(
        xaxis_title=llm_cost_page_t(
            "consumed_tokens"
        ),
        yaxis_title=None,
        coloraxis_showscale=False,
        showlegend=False,
    )

    aplicar_tema_llm_cost_chart(
        fig_modelos,
        height=410,
    )

    st.plotly_chart(
        fig_modelos,
        width="stretch",
        key="llm_tokens_by_model_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.markdown(
        llm_cost_page_t(
            "consumption_by_operation"
        )
    )

    por_operacao = (
        filtrado.groupby(
            "operacao",
            as_index=False,
        )
        .agg(
            Chamadas=("id", "count"),
            Tokens=("tokens_totais", "sum"),
            Custo_USD=(
                "custo_total_usd",
                "sum",
            ),
            Duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
        )
    )

    por_operacao[
        "Duração média (s)"
    ] = (
        por_operacao[
            "Duracao_media_ms"
        ]
        / 1000
    ).round(2)

    coluna_operacao = llm_table_t("operation")
    coluna_chamadas = llm_table_t("calls")
    coluna_tokens = llm_table_t("tokens")
    coluna_custo = llm_table_t("cost_usd")
    coluna_duracao = llm_table_t(
        "avg_duration"
    )

    tabela_operacoes = (
        por_operacao[
            [
                "operacao",
                "Chamadas",
                "Tokens",
                "Custo_USD",
                "Duração média (s)",
            ]
        ]
        .sort_values(
            "Tokens",
            ascending=False,
        )
        .rename(
            columns={
                "operacao": coluna_operacao,
                "Chamadas": coluna_chamadas,
                "Tokens": coluna_tokens,
                "Custo_USD": coluna_custo,
                "Duração média (s)": (
                    coluna_duracao
                ),
            }
        )
        .reset_index(drop=True)
    )

    st.dataframe(
        estilizar_tabela_llm_costs(
            tabela_operacoes
        ),
        use_container_width=True,
        hide_index=True,
        height=330,
        column_config={
            coluna_operacao: (
                st.column_config.TextColumn(
                    coluna_operacao,
                    help=llm_table_t(
                        "operation_help"
                    ),
                    width="large",
                )
            ),
            coluna_chamadas: (
                st.column_config.NumberColumn(
                    coluna_chamadas,
                    help=llm_table_t(
                        "calls_help"
                    ),
                    format="%d",
                    width="small",
                )
            ),
            coluna_tokens: (
                st.column_config.ProgressColumn(
                    coluna_tokens,
                    help=llm_table_t(
                        "tokens_help"
                    ),
                    min_value=0,
                    max_value=max(
                        int(
                            tabela_operacoes[
                                coluna_tokens
                            ].max()
                        ),
                        1,
                    ),
                    format="%d",
                    width="medium",
                )
            ),
            coluna_custo: (
                st.column_config.NumberColumn(
                    coluna_custo,
                    help=llm_table_t(
                        "cost_help"
                    ),
                    format="US$ %.6f",
                    width="medium",
                )
            ),
            coluna_duracao: (
                st.column_config.NumberColumn(
                    coluna_duracao,
                    help=llm_table_t(
                        "duration_help"
                    ),
                    format="%.2f s",
                    width="medium",
                )
            ),
        },
    )

    st.divider()
    st.markdown(
        llm_cost_page_t(
            "temporal_evolution"
        )
    )

    temporal = filtrado.copy()

    temporal["data"] = (
        temporal["criado_em"]
        .dt.floor("h")
    )

    serie_tokens = (
        temporal.groupby(
            "data",
            as_index=False,
        )["tokens_totais"]
        .sum()
        .rename(
            columns={
                "data": "Data",
                "tokens_totais": "Tokens",
            }
        )
        .set_index("Data")
    )

    st.markdown(
        llm_cost_page_t(
            "tokens_per_hour"
        )
    )

    fig_tokens = px.line(
        serie_tokens.reset_index(),
        x="Data",
        y="Tokens",
        markers=True,
        color_discrete_sequence=[
            "#38BDF8",
        ],
    )

    fig_tokens.update_traces(
        line={
            "width": 3,
        },
        marker={
            "size": 8,
            "color": "#E0F2FE",
            "line": {
                "color": "#38BDF8",
                "width": 2,
            },
        },
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.16)",
        hovertemplate=(
            "<b>%{x|%d/%m/%Y %H:%M}</b><br>"
            "Tokens: %{y:,.0f}"
            "<extra></extra>"
        ),
    )

    fig_tokens.update_layout(
        xaxis_title=None,
        yaxis_title="Tokens",
        showlegend=False,
        hovermode="x unified",
    )

    aplicar_tema_llm_cost_chart(
        fig_tokens,
        height=420,
    )

    st.plotly_chart(
        fig_tokens,
        width="stretch",
        key="llm_tokens_by_hour_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    serie_duracao = (
        temporal.groupby(
            "data",
            as_index=False,
        )["duracao_ms"]
        .mean()
    )

    serie_duracao[
        "Duração média (s)"
    ] = (
        serie_duracao[
            "duracao_ms"
        ]
        / 1000
    )

    serie_duracao = (
        serie_duracao[
            [
                "data",
                "Duração média (s)",
            ]
        ]
        .rename(
            columns={
                "data": "Data",
            }
        )
        .set_index("Data")
    )

    st.markdown(
        llm_cost_page_t(
            "average_duration_per_hour"
        )
    )

    fig_duracao = px.line(
        serie_duracao.reset_index(),
        x="Data",
        y="Duração média (s)",
        markers=True,
        color_discrete_sequence=[
            "#A78BFA",
        ],
    )

    fig_duracao.update_traces(
        line={
            "width": 3,
        },
        marker={
            "size": 8,
            "color": "#F3E8FF",
            "line": {
                "color": "#A78BFA",
                "width": 2,
            },
        },
        hovertemplate=(
            "<b>%{x|%d/%m/%Y %H:%M}</b><br>"
            f"{llm_cost_page_t('average_duration_hover')}: "
            "%{y:.2f} s"
            "<extra></extra>"
        ),
    )

    fig_duracao.update_layout(
        xaxis_title=None,
        yaxis_title=llm_cost_page_t(
            "average_duration_seconds"
        ),
        showlegend=False,
        hovermode="x unified",
    )

    fig_duracao.update_yaxes(
        rangemode="tozero",
    )

    aplicar_tema_llm_cost_chart(
        fig_duracao,
        height=420,
    )

    st.plotly_chart(
        fig_duracao,
        width="stretch",
        key="llm_average_duration_by_hour_chart",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.divider()
    st.markdown(
        llm_cost_page_t(
            "calls_audit"
        )
    )

    tabela = filtrado[
        [
            "id",
            "criado_em",
            "provider",
            "modelo",
            "operacao",
            "origem",
            "usuario_id",
            "trace_id",
            "tokens_entrada",
            "tokens_saida",
            "tokens_totais",
            "custo_total_usd",
            "duracao_ms",
            "sucesso",
            "erro_tipo",
        ]
    ].copy()

    tabela[
        "duracao_segundos"
    ] = (
        tabela["duracao_ms"]
        / 1000
    ).round(3)

    tabela = tabela.drop(
        columns=["duracao_ms"]
    ).sort_values(
        "criado_em",
        ascending=False,
    )

    tabela = tabela.rename(
        columns={
            "id": "ID",
            "criado_em": "Data",
            "provider": "Provider",
            "modelo": "Modelo",
            "operacao": "Operação",
            "origem": "Origem",
            "usuario_id": "Usuário",
            "trace_id": "Trace",
            "tokens_entrada": "Tokens entrada",
            "tokens_saida": "Tokens saída",
            "tokens_totais": "Tokens totais",
            "custo_total_usd": "Custo USD",
            "sucesso": "Sucesso",
            "erro_tipo": "Tipo do erro",
            "duracao_segundos": "Duração (s)",
        }
    )

    tabela["Sucesso"] = tabela[
        "Sucesso"
    ].map(
        {
            True: llm_detail_t("success"),
            False: llm_detail_t("failure"),
        }
    ).fillna(
        llm_detail_t("no_data")
    )

    tabela["Tipo do erro"] = tabela[
        "Tipo do erro"
    ].fillna("—").replace(
        {
            "": "—",
            "None": "—",
            "nan": "—",
        }
    )

    st.dataframe(
        estilizar_tabela_detalhada_llm(
            tabela
        ),
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "ID": (
                st.column_config.NumberColumn(
                    "ID",
                    format="%d",
                    width="small",
                )
            ),
            "Data": (
                st.column_config.DatetimeColumn(
                    llm_detail_t("date"),
                    format="DD/MM/YYYY HH:mm:ss",
                    width="medium",
                )
            ),
            "Provider": (
                st.column_config.TextColumn(
                    llm_detail_t("provider"),
                    help=llm_detail_t(
                        "provider_help"
                    ),
                    width="medium",
                )
            ),
            "Modelo": (
                st.column_config.TextColumn(
                    llm_table_t("model"),
                    width="large",
                )
            ),
            "Operação": (
                st.column_config.TextColumn(
                    llm_cost_page_t(
                        "operation_column"
                    ),
                    width="large",
                )
            ),
            "Origem": (
                st.column_config.TextColumn(
                    llm_detail_t("origin"),
                    width="medium",
                )
            ),
            "Usuário": (
                st.column_config.TextColumn(
                    llm_detail_t("user"),
                    width="large",
                )
            ),
            "Trace": (
                st.column_config.TextColumn(
                    llm_detail_t("trace"),
                    help=llm_detail_t(
                        "trace_help"
                    ),
                    width="large",
                )
            ),
            "Tokens entrada": (
                st.column_config.NumberColumn(
                    llm_detail_t("input_tokens"),
                    format="%d",
                    width="small",
                )
            ),
            "Tokens saída": (
                st.column_config.NumberColumn(
                    llm_detail_t("output_tokens"),
                    format="%d",
                    width="small",
                )
            ),
            "Tokens totais": (
                st.column_config.NumberColumn(
                    llm_detail_t("total_tokens"),
                    format="%d",
                    width="small",
                )
            ),
            "Custo USD": (
                st.column_config.NumberColumn(
                    llm_detail_t("estimated_cost"),
                    format="US$ %.6f",
                    width="medium",
                )
            ),
            "Duração (s)": (
                st.column_config.NumberColumn(
                    llm_detail_t("duration"),
                    format="%.3f s",
                    width="small",
                )
            ),
            "Sucesso": (
                st.column_config.TextColumn(
                    llm_detail_t("result"),
                    width="medium",
                )
            ),
            "Tipo do erro": (
                st.column_config.TextColumn(
                    llm_detail_t("error_type"),
                    width="large",
                )
            ),
        },
    )


    csv = tabela.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        llm_cost_page_t(
            "download_csv"
        ),
        data=csv,
        file_name="inna_llm_consumo.csv",
        mime="text/csv",
        use_container_width=True,
        key="llm_cost_download",
    )

    with st.expander(
        llm_cost_page_t(
            "telemetry_privacy"
        ),
        expanded=False,
    ):
        st.markdown(
            llm_cost_page_t(
                "telemetry_text"
            )
        )


__all__ = [
    "render_alertas_llm_section",
    "preparar_consumo_exibicao",
    "resumir_consumo_llm",
    "render_llm_costs_page",
]

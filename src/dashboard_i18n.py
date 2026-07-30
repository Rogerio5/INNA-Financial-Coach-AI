from __future__ import annotations

import unicodedata
from collections.abc import Callable, Mapping, MutableMapping
from typing import Any, TypeVar

import pandas as pd
import streamlit as st

DEFAULT_LANGUAGE = "pt"

SUPPORTED_LANGUAGES: tuple[str, ...] = (
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

LANGUAGE_ALIASES: dict[str, str] = {
    "pt-br": "pt",
    "pt_br": "pt",
    "pt": "pt",
    "en": "en_us",
    "en-us": "en_us",
    "en_us": "en_us",
    "en-gb": "en_gb",
    "en_gb": "en_gb",
    "es-es": "es",
    "es_es": "es",
    "es": "es",
    "fr-fr": "fr",
    "fr_fr": "fr",
    "fr": "fr",
    "de-de": "de",
    "de_de": "de",
    "de": "de",
    "it-it": "it",
    "it_it": "it",
    "it": "it",
    "ro-ro": "ro",
    "ro_ro": "ro",
    "ro": "ro",
    "uk": "ua",
    "uk-ua": "ua",
    "uk_ua": "ua",
    "ua": "ua",
    "ru-ru": "ru",
    "ru_ru": "ru",
    "ru": "ru",
    "ar": "sa",
    "ar-sa": "sa",
    "ar_sa": "sa",
    "sa": "sa",
    "de-ch": "ch",
    "de_ch": "ch",
    "ch": "ch",
}

LANGUAGE_LABELS: dict[str, str] = {
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


def normalize_language(
    language: Any,
) -> str:
    """Converte códigos variados para o código canônico do dashboard."""
    if language is None:
        return DEFAULT_LANGUAGE

    normalized = (
        str(language)
        .strip()
        .lower()
        .replace(" ", "_")
    )

    canonical = LANGUAGE_ALIASES.get(
        normalized,
        normalized,
    )

    if canonical in SUPPORTED_LANGUAGES:
        return canonical

    return DEFAULT_LANGUAGE


def get_interface_language(
    session_state: Mapping[str, Any] | None = None,
) -> str:
    """
    Retorna exclusivamente o idioma da interface.

    O filtro de idioma dos dados não interfere nesta função.
    """
    state = (
        session_state
        if session_state is not None
        else st.session_state
    )

    return normalize_language(
        state.get(
            "dashboard_interface_lang",
            DEFAULT_LANGUAGE,
        )
    )


def get_data_language_filter(
    session_state: Mapping[str, Any] | None = None,
) -> str | None:
    """
    Retorna o filtro de idioma dos registros.

    Esta função é separada do idioma da interface.
    """
    state = (
        session_state
        if session_state is not None
        else st.session_state
    )

    value = state.get(
        "dashboard_filter_language"
    )

    if value in (
        None,
        "",
        "Todos",
        "All",
        "__all__",
    ):
        return None

    return str(value)


def resolve_language_texts(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    language: str | None = None,
) -> Mapping[str, str]:
    """
    Retorna o dicionário do idioma solicitado.

    Ordem de fallback:
    1. idioma selecionado;
    2. alias regional;
    3. português;
    4. dicionário vazio.
    """
    selected = normalize_language(
        language
        if language is not None
        else get_interface_language()
    )

    if selected in texts_by_language:
        return texts_by_language[selected]

    if selected == "en_gb" and "en_us" in texts_by_language:
        return texts_by_language["en_us"]

    if selected == "ch" and "de" in texts_by_language:
        return texts_by_language["de"]

    return texts_by_language.get(
        DEFAULT_LANGUAGE,
        {},
    )


def translate(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    key: str,
    *,
    language: str | None = None,
    default: str | None = None,
    strict: bool = False,
    **format_values: Any,
) -> str:
    """
    Traduz uma chave de interface com fallback seguro e formatação.

    Em modo strict, uma chave ausente gera KeyError para testes/auditoria.
    """
    selected = normalize_language(
        language
        if language is not None
        else get_interface_language()
    )

    selected_texts = resolve_language_texts(
        texts_by_language,
        selected,
    )

    portuguese_texts = texts_by_language.get(
        DEFAULT_LANGUAGE,
        {},
    )

    value = selected_texts.get(key)

    if value is None:
        value = portuguese_texts.get(key)

    if value is None:
        if strict:
            raise KeyError(
                f"Chave i18n ausente: "
                f"language={selected!r}, key={key!r}"
            )

        value = (
            default
            if default is not None
            else key
        )

    if not format_values:
        return str(value)

    try:
        return str(value).format(
            **format_values
        )
    except (
        KeyError,
        IndexError,
        ValueError,
    ):
        if strict:
            raise

        return str(value)


def build_translator(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
) -> Callable[..., str]:
    """Cria um tradutor específico para uma página."""

    def page_translate(
        key: str,
        default: str | None = None,
        *,
        language: str | None = None,
        strict: bool = False,
        **format_values: Any,
    ) -> str:
        return translate(
            texts_by_language,
            key,
            language=language,
            default=default,
            strict=strict,
            **format_values,
        )

    return page_translate


def normalized_value(
    value: Any,
) -> str:
    """Normaliza valores dinâmicos sem alterar o dado original."""
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    return (
        str(value)
        .strip()
        .casefold()
    )


VALUE_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "all": "Todos",
        "not_informed": "Não informado",
        "yes": "Sim",
        "no": "Não",
        "useful": "Útil",
        "not_useful": "Não útil",
        "success": "Sucesso",
        "failure": "Falha",
        "ignored": "Ignorado",
        "pending": "Pendente",
        "open": "Aberto",
        "resolved": "Resolvido",
        "active": "Ativo",
        "inactive": "Inativo",
        "available": "Disponível",
        "unavailable": "Indisponível",
        "configured": "Configurado",
        "not_configured": "Não configurado",
        "low": "Baixo",
        "medium": "Médio",
        "high": "Alto",
        "critical": "Crítico",
        "good": "Boa",
        "excellent": "Excelente",
    },
    "en_us": {
        "all": "All",
        "not_informed": "Not informed",
        "yes": "Yes",
        "no": "No",
        "useful": "Useful",
        "not_useful": "Not useful",
        "success": "Success",
        "failure": "Failure",
        "ignored": "Ignored",
        "pending": "Pending",
        "open": "Open",
        "resolved": "Resolved",
        "active": "Active",
        "inactive": "Inactive",
        "available": "Available",
        "unavailable": "Unavailable",
        "configured": "Configured",
        "not_configured": "Not configured",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
        "good": "Good",
        "excellent": "Excellent",
    },
    "es": {
        "all": "Todos",
        "not_informed": "No informado",
        "yes": "Sí",
        "no": "No",
        "useful": "Útil",
        "not_useful": "No útil",
        "success": "Éxito",
        "failure": "Fallo",
        "ignored": "Ignorado",
        "pending": "Pendiente",
        "open": "Abierto",
        "resolved": "Resuelto",
        "active": "Activo",
        "inactive": "Inactivo",
        "available": "Disponible",
        "unavailable": "No disponible",
        "configured": "Configurado",
        "not_configured": "No configurado",
        "low": "Bajo",
        "medium": "Medio",
        "high": "Alto",
        "critical": "Crítico",
        "good": "Buena",
        "excellent": "Excelente",
    },
    "fr": {
        "all": "Tous",
        "not_informed": "Non renseigné",
        "yes": "Oui",
        "no": "Non",
        "useful": "Utile",
        "not_useful": "Non utile",
        "success": "Succès",
        "failure": "Échec",
        "ignored": "Ignoré",
        "pending": "En attente",
        "open": "Ouvert",
        "resolved": "Résolu",
        "active": "Actif",
        "inactive": "Inactif",
        "available": "Disponible",
        "unavailable": "Indisponible",
        "configured": "Configuré",
        "not_configured": "Non configuré",
        "low": "Faible",
        "medium": "Moyen",
        "high": "Élevé",
        "critical": "Critique",
        "good": "Bonne",
        "excellent": "Excellente",
    },
    "de": {
        "all": "Alle",
        "not_informed": "Nicht angegeben",
        "yes": "Ja",
        "no": "Nein",
        "useful": "Nützlich",
        "not_useful": "Nicht nützlich",
        "success": "Erfolg",
        "failure": "Fehler",
        "ignored": "Ignoriert",
        "pending": "Ausstehend",
        "open": "Offen",
        "resolved": "Gelöst",
        "active": "Aktiv",
        "inactive": "Inaktiv",
        "available": "Verfügbar",
        "unavailable": "Nicht verfügbar",
        "configured": "Konfiguriert",
        "not_configured": "Nicht konfiguriert",
        "low": "Niedrig",
        "medium": "Mittel",
        "high": "Hoch",
        "critical": "Kritisch",
        "good": "Gut",
        "excellent": "Ausgezeichnet",
    },
    "it": {
        "all": "Tutti",
        "not_informed": "Non specificato",
        "yes": "Sì",
        "no": "No",
        "useful": "Utile",
        "not_useful": "Non utile",
        "success": "Successo",
        "failure": "Errore",
        "ignored": "Ignorato",
        "pending": "In sospeso",
        "open": "Aperto",
        "resolved": "Risolto",
        "active": "Attivo",
        "inactive": "Inattivo",
        "available": "Disponibile",
        "unavailable": "Non disponibile",
        "configured": "Configurato",
        "not_configured": "Non configurato",
        "low": "Basso",
        "medium": "Medio",
        "high": "Alto",
        "critical": "Critico",
        "good": "Buona",
        "excellent": "Eccellente",
    },
    "ro": {
        "all": "Toate",
        "not_informed": "Nespecificat",
        "yes": "Da",
        "no": "Nu",
        "useful": "Util",
        "not_useful": "Neutil",
        "success": "Succes",
        "failure": "Eșec",
        "ignored": "Ignorat",
        "pending": "În așteptare",
        "open": "Deschis",
        "resolved": "Rezolvat",
        "active": "Activ",
        "inactive": "Inactiv",
        "available": "Disponibil",
        "unavailable": "Indisponibil",
        "configured": "Configurat",
        "not_configured": "Neconfigurat",
        "low": "Scăzut",
        "medium": "Mediu",
        "high": "Ridicat",
        "critical": "Critic",
        "good": "Bună",
        "excellent": "Excelentă",
    },
    "ua": {
        "all": "Усі",
        "not_informed": "Не вказано",
        "yes": "Так",
        "no": "Ні",
        "useful": "Корисний",
        "not_useful": "Некорисний",
        "success": "Успіх",
        "failure": "Помилка",
        "ignored": "Проігноровано",
        "pending": "Очікує",
        "open": "Відкрито",
        "resolved": "Вирішено",
        "active": "Активний",
        "inactive": "Неактивний",
        "available": "Доступний",
        "unavailable": "Недоступний",
        "configured": "Налаштовано",
        "not_configured": "Не налаштовано",
        "low": "Низький",
        "medium": "Середній",
        "high": "Високий",
        "critical": "Критичний",
        "good": "Добрий",
        "excellent": "Відмінний",
    },
    "ru": {
        "all": "Все",
        "not_informed": "Не указано",
        "yes": "Да",
        "no": "Нет",
        "useful": "Полезный",
        "not_useful": "Неполезный",
        "success": "Успех",
        "failure": "Ошибка",
        "ignored": "Игнорировано",
        "pending": "Ожидает",
        "open": "Открыто",
        "resolved": "Решено",
        "active": "Активно",
        "inactive": "Неактивно",
        "available": "Доступно",
        "unavailable": "Недоступно",
        "configured": "Настроено",
        "not_configured": "Не настроено",
        "low": "Низкий",
        "medium": "Средний",
        "high": "Высокий",
        "critical": "Критический",
        "good": "Хорошая",
        "excellent": "Отличная",
    },
    "sa": {
        "all": "الكل",
        "not_informed": "غير محدد",
        "yes": "نعم",
        "no": "لا",
        "useful": "مفيد",
        "not_useful": "غير مفيد",
        "success": "نجاح",
        "failure": "فشل",
        "ignored": "تم التجاهل",
        "pending": "قيد الانتظار",
        "open": "مفتوح",
        "resolved": "تم الحل",
        "active": "نشط",
        "inactive": "غير نشط",
        "available": "متاح",
        "unavailable": "غير متاح",
        "configured": "تم الإعداد",
        "not_configured": "غير مهيأ",
        "low": "منخفض",
        "medium": "متوسط",
        "high": "مرتفع",
        "critical": "حرج",
        "good": "جيدة",
        "excellent": "ممتازة",
    },
}

VALUE_TEXTS["en_gb"] = VALUE_TEXTS["en_us"]
VALUE_TEXTS["ch"] = VALUE_TEXTS["de"]


def value_t(
    key: str,
    *,
    language: str | None = None,
    default: str | None = None,
) -> str:
    """Traduz um valor categórico canônico."""
    return translate(
        VALUE_TEXTS,
        key,
        language=language,
        default=default,
    )


USEFUL_TRUE_VALUES: frozenset[str] = frozenset({
    "true",
    "1",
    "sim",
    "yes",
    "y",
    "útil",
    "util",
    "useful",
    "utile",
    "nützlich",
})

USEFUL_FALSE_VALUES: frozenset[str] = frozenset({
    "false",
    "0",
    "não",
    "nao",
    "no",
    "n",
    "não útil",
    "nao util",
    "not useful",
    "non utile",
    "nicht nützlich",
})


def translate_useful(
    value: Any,
    *,
    language: str | None = None,
) -> str:
    """Converte booleanos e equivalentes em Útil/Não útil traduzido."""
    if value is None:
        return value_t(
            "not_informed",
            language=language,
        )

    try:
        if pd.isna(value):
            return value_t(
                "not_informed",
                language=language,
            )
    except (
        TypeError,
        ValueError,
    ):
        pass

    if isinstance(value, bool):
        return value_t(
            "useful" if value else "not_useful",
            language=language,
        )

    normalized = normalized_value(value)

    if normalized in USEFUL_TRUE_VALUES:
        return value_t(
            "useful",
            language=language,
        )

    if normalized in USEFUL_FALSE_VALUES:
        return value_t(
            "not_useful",
            language=language,
        )

    return str(value)


RISK_VALUE_KEYS: dict[str, str] = {
    "baixo": "low",
    "baixa": "low",
    "low": "low",
    "niedrig": "low",
    "médio": "medium",
    "medio": "medium",
    "média": "medium",
    "media": "medium",
    "medium": "medium",
    "mittel": "medium",
    "alto": "high",
    "alta": "high",
    "high": "high",
    "hoch": "high",
    "crítico": "critical",
    "critico": "critical",
    "critical": "critical",
    "kritisch": "critical",
}


def translate_risk(
    value: Any,
    *,
    language: str | None = None,
) -> str:
    """Traduz níveis de risco sem modificar o valor armazenado."""
    normalized = normalized_value(value)

    if not normalized:
        return value_t(
            "not_informed",
            language=language,
        )

    key = RISK_VALUE_KEYS.get(normalized)

    if key is None:
        return str(value)

    return value_t(
        key,
        language=language,
    )


STATUS_VALUE_KEYS: dict[str, str] = {
    "success": "success",
    "sucesso": "success",
    "successful": "success",
    "ok": "success",
    "failure": "failure",
    "failed": "failure",
    "falha": "failure",
    "erro": "failure",
    "error": "failure",
    "ignored": "ignored",
    "ignorado": "ignored",
    "pending": "pending",
    "pendente": "pending",
    "open": "open",
    "aberto": "open",
    "resolved": "resolved",
    "resolvido": "resolved",
    "active": "active",
    "ativo": "active",
    "inactive": "inactive",
    "inativo": "inactive",
    "available": "available",
    "disponível": "available",
    "disponivel": "available",
    "unavailable": "unavailable",
    "indisponível": "unavailable",
    "indisponivel": "unavailable",
    "configured": "configured",
    "configurado": "configured",
    "not configured": "not_configured",
    "não configurado": "not_configured",
    "nao configurado": "not_configured",
}


def translate_status(
    value: Any,
    *,
    language: str | None = None,
) -> str:
    """Traduz status recorrentes do dashboard."""
    normalized = normalized_value(value)

    if not normalized:
        return value_t(
            "not_informed",
            language=language,
        )

    key = STATUS_VALUE_KEYS.get(normalized)

    if key is None:
        return str(value)

    return value_t(
        key,
        language=language,
    )


T = TypeVar("T")


def translate_known_value(
    value: T,
    *,
    value_key_map: Mapping[str, str],
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    language: str | None = None,
) -> str:
    """
    Traduz um valor dinâmico conhecido.

    Valores técnicos desconhecidos são preservados.
    """
    normalized = normalized_value(value)

    if not normalized:
        return translate(
            texts_by_language,
            "not_informed",
            language=language,
            default=value_t(
                "not_informed",
                language=language,
            ),
        )

    translation_key = value_key_map.get(
        normalized
    )

    if translation_key is None:
        return str(value)

    return translate(
        texts_by_language,
        translation_key,
        language=language,
        default=str(value),
    )


def localize_dataframe(
    dataframe: pd.DataFrame,
    *,
    column_keys: Mapping[str, str] | None = None,
    column_texts: Mapping[
        str,
        Mapping[str, str],
    ] | None = None,
    value_transforms: Mapping[
        str,
        Callable[[Any], Any],
    ] | None = None,
    language: str | None = None,
) -> pd.DataFrame:
    """
    Cria uma cópia visual traduzida do DataFrame.

    Nunca altera as colunas ou os valores do DataFrame original.
    """
    localized = dataframe.copy(
        deep=True
    )

    if value_transforms:
        for column, transform in value_transforms.items():
            if column not in localized.columns:
                continue

            localized[column] = localized[
                column
            ].map(transform)

    if column_keys and column_texts:
        localized = localized.rename(
            columns={
                column: translate(
                    column_texts,
                    translation_key,
                    language=language,
                    default=column,
                )
                for column, translation_key
                in column_keys.items()
                if column in localized.columns
            }
        )

    return localized


def ensure_language_parity(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    *,
    reference_language: str = DEFAULT_LANGUAGE,
    supported_languages: tuple[
        str,
        ...
    ] = SUPPORTED_LANGUAGES,
) -> dict[
    str,
    dict[str, set[str]],
]:
    """
    Audita chaves ausentes e extras em cada idioma.

    Retorna apenas idiomas com divergência.
    """
    reference = set(
        texts_by_language.get(
            reference_language,
            {},
        )
    )

    divergences: dict[
        str,
        dict[str, set[str]],
    ] = {}

    for language in supported_languages:
        current = set(
            texts_by_language.get(
                language,
                {},
            )
        )

        missing = reference - current
        extra = current - reference

        if missing or extra:
            divergences[language] = {
                "missing": missing,
                "extra": extra,
            }

    return divergences


def fill_language_fallbacks(
    texts_by_language: MutableMapping[
        str,
        dict[str, str],
    ],
) -> None:
    """
    Preenche aliases regionais sem sobrescrever traduções próprias.
    """
    if "en_us" in texts_by_language:
        texts_by_language.setdefault(
            "en_gb",
            dict(texts_by_language["en_us"]),
        )

    if "de" in texts_by_language:
        texts_by_language.setdefault(
            "ch",
            dict(texts_by_language["de"]),
        )

MENU_PAGE_IDS: tuple[str, ...] = (
    "overview",
    "multichannel_events",
    "international_view",
    "diagnostics",
    "feedbacks",
    "evolution",
    "executive_reading",
    "agent_evaluation",
    "rag_observability",
    "tools_observability",
    "timeline_viewer",
    "tools_analytics",
    "health_center",
    "llmops_observability",
    "ai_cost_center",
    "document_upload",
    "user_memory",
    "export",
)


MENU_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "overview": "📌 Visão Geral",
        "multichannel_events": "🌐 Eventos Multicanal",
        "international_view": "🌎 Visão Internacional",
        "diagnostics": "👤 Diagnósticos",
        "feedbacks": "💬 Feedbacks",
        "evolution": "📈 Evolução",
        "executive_reading": "🧠 Leitura Executiva",
        "agent_evaluation": "🧪 Avaliação do Agente",
        "rag_observability": "📊 Observabilidade RAG",
        "tools_observability": "🛠️ Observabilidade das Tools",
        "timeline_viewer": "🧭 Visualizador de Timeline",
        "tools_analytics": "📊 Analytics das Tools",
        "health_center": "❤️ Central de Saúde",
        "llmops_observability": (
            "🛰️ Operações de IA e Observabilidade"
        ),
        "ai_cost_center": "💰 Central de Custos de IA",
        "document_upload": "📄 Upload de Documentos",
        "user_memory": "🧠 Memória do Usuário",
        "export": "📤 Exportar",
    },
    "en_us": {
        "overview": "📌 Overview",
        "multichannel_events": "🌐 Multichannel Events",
        "international_view": "🌎 International View",
        "diagnostics": "👤 Diagnostics",
        "feedbacks": "💬 Feedback",
        "evolution": "📈 Evolution",
        "executive_reading": "🧠 Executive Reading",
        "agent_evaluation": "🧪 Agent Evaluation",
        "rag_observability": "📊 RAG Observability",
        "tools_observability": "🛠️ Tools Observability",
        "timeline_viewer": "🧭 Timeline Viewer",
        "tools_analytics": "📊 Tools Analytics",
        "health_center": "❤️ Health Center",
        "llmops_observability": (
            "🛰️ AI Operations and Observability"
        ),
        "ai_cost_center": "💰 AI Cost Center",
        "document_upload": "📄 Document Upload",
        "user_memory": "🧠 User Memory",
        "export": "📤 Export",
    },
    "es": {
        "overview": "📌 Visión General",
        "multichannel_events": "🌐 Eventos Multicanal",
        "international_view": "🌎 Vista Internacional",
        "diagnostics": "👤 Diagnósticos",
        "feedbacks": "💬 Feedback",
        "evolution": "📈 Evolución",
        "executive_reading": "🧠 Lectura Ejecutiva",
        "agent_evaluation": "🧪 Evaluación del Agente",
        "rag_observability": "📊 Observabilidad RAG",
        "tools_observability": (
            "🛠️ Observabilidad de herramientas"
        ),
        "timeline_viewer": (
            "🧭 Visor de línea de tiempo"
        ),
        "tools_analytics": (
            "📊 Analítica de herramientas"
        ),
        "health_center": "❤️ Centro de Salud",
        "llmops_observability": (
            "🛰️ Operaciones de IA y Observabilidad"
        ),
        "ai_cost_center": "💰 Centro de Costos de IA",
        "document_upload": "📄 Carga de documentos",
        "user_memory": "🧠 Memoria del usuario",
        "export": "📤 Exportar",
    },
    "fr": {
        "overview": "📌 Vue d’ensemble",
        "multichannel_events": (
            "🌐 Événements multicanaux"
        ),
        "international_view": "🌎 Vue internationale",
        "diagnostics": "👤 Diagnostics",
        "feedbacks": "💬 Retours",
        "evolution": "📈 Évolution",
        "executive_reading": "🧠 Lecture exécutive",
        "agent_evaluation": (
            "🧪 Évaluation de l’agent"
        ),
        "rag_observability": "📊 Observabilité RAG",
        "tools_observability": (
            "🛠️ Observabilité des outils"
        ),
        "timeline_viewer": (
            "🧭 Visionneuse de chronologie"
        ),
        "tools_analytics": (
            "📊 Analyse des outils"
        ),
        "health_center": "❤️ Centre de santé",
        "llmops_observability": (
            "🛰️ Opérations IA et Observabilité"
        ),
        "ai_cost_center": "💰 Centre des coûts IA",
        "document_upload": (
            "📄 Téléversement de documents"
        ),
        "user_memory": "🧠 Mémoire utilisateur",
        "export": "📤 Exporter",
    },
    "de": {
        "overview": "📌 Übersicht",
        "multichannel_events": (
            "🌐 Mehrkanal-Ereignisse"
        ),
        "international_view": (
            "🌎 Internationale Ansicht"
        ),
        "diagnostics": "👤 Diagnosen",
        "feedbacks": "💬 Feedback",
        "evolution": "📈 Entwicklung",
        "executive_reading": (
            "🧠 Zusammenfassung"
        ),
        "agent_evaluation": "🧪 Agentenbewertung",
        "rag_observability": (
            "📊 RAG-Beobachtbarkeit"
        ),
        "tools_observability": (
            "🛠️ Werkzeugbeobachtung"
        ),
        "timeline_viewer": "🧭 Zeitachsenansicht",
        "tools_analytics": "📊 Werkzeuganalyse",
        "health_center": "❤️ Systemzustand",
        "llmops_observability": (
            "🛰️ KI-Betrieb und Beobachtbarkeit"
        ),
        "ai_cost_center": "💰 KI-Kostenzentrale",
        "document_upload": "📄 Dokumenten-Upload",
        "user_memory": "🧠 Benutzerspeicher",
        "export": "📤 Exportieren",
    },
    "it": {
        "overview": "📌 Panoramica",
        "multichannel_events": (
            "🌐 Eventi multicanale"
        ),
        "international_view": (
            "🌎 Vista internazionale"
        ),
        "diagnostics": "👤 Diagnostiche",
        "feedbacks": "💬 Feedback",
        "evolution": "📈 Evoluzione",
        "executive_reading": "🧠 Lettura esecutiva",
        "agent_evaluation": (
            "🧪 Valutazione agente"
        ),
        "rag_observability": "📊 Osservabilità RAG",
        "tools_observability": (
            "🛠️ Osservabilità degli strumenti"
        ),
        "timeline_viewer": (
            "🧭 Visualizzatore della timeline"
        ),
        "tools_analytics": (
            "📊 Analisi degli strumenti"
        ),
        "health_center": "❤️ Centro salute",
        "llmops_observability": (
            "🛰️ Operazioni IA e Osservabilità"
        ),
        "ai_cost_center": "💰 Centro costi IA",
        "document_upload": (
            "📄 Caricamento documenti"
        ),
        "user_memory": "🧠 Memoria utente",
        "export": "📤 Esporta",
    },
    "ro": {
        "overview": "📌 Prezentare generală",
        "multichannel_events": (
            "🌐 Evenimente multicanal"
        ),
        "international_view": (
            "🌎 Vizualizare internațională"
        ),
        "diagnostics": "👤 Diagnosticări",
        "feedbacks": "💬 Feedback",
        "evolution": "📈 Evoluție",
        "executive_reading": "🧠 Rezumat executiv",
        "agent_evaluation": (
            "🧪 Evaluarea agentului"
        ),
        "rag_observability": "📊 Observabilitate RAG",
        "tools_observability": (
            "🛠️ Observabilitatea instrumentelor"
        ),
        "timeline_viewer": (
            "🧭 Vizualizator cronologie"
        ),
        "tools_analytics": (
            "📊 Analiza instrumentelor"
        ),
        "health_center": "❤️ Centrul de sănătate",
        "llmops_observability": (
            "🛰️ Operațiuni IA și Observabilitate"
        ),
        "ai_cost_center": (
            "💰 Centrul costurilor IA"
        ),
        "document_upload": (
            "📄 Încărcare documente"
        ),
        "user_memory": "🧠 Memoria utilizatorului",
        "export": "📤 Exportă",
    },
    "ua": {
        "overview": "📌 Огляд",
        "multichannel_events": (
            "🌐 Багатоканальні події"
        ),
        "international_view": (
            "🌎 Міжнародний огляд"
        ),
        "diagnostics": "👤 Діагностики",
        "feedbacks": "💬 Відгуки",
        "evolution": "📈 Динаміка",
        "executive_reading": (
            "🧠 Виконавче резюме"
        ),
        "agent_evaluation": "🧪 Оцінка агента",
        "rag_observability": (
            "📊 Спостережуваність RAG"
        ),
        "tools_observability": (
            "🛠️ Спостережуваність інструментів"
        ),
        "timeline_viewer": (
            "🧭 Перегляд часової шкали"
        ),
        "tools_analytics": (
            "📊 Аналітика інструментів"
        ),
        "health_center": (
            "❤️ Центр стану системи"
        ),
        "llmops_observability": (
            "🛰️ Операції ШІ та спостережуваність"
        ),
        "ai_cost_center": "💰 Центр витрат ШІ",
        "document_upload": (
            "📄 Завантаження документів"
        ),
        "user_memory": "🧠 Пам’ять користувача",
        "export": "📤 Експорт",
    },
    "ru": {
        "overview": "📌 Обзор",
        "multichannel_events": (
            "🌐 Многоканальные события"
        ),
        "international_view": (
            "🌎 Международный обзор"
        ),
        "diagnostics": "👤 Диагностики",
        "feedbacks": "💬 Отзывы",
        "evolution": "📈 Динамика",
        "executive_reading": (
            "🧠 Исполнительное резюме"
        ),
        "agent_evaluation": "🧪 Оценка агента",
        "rag_observability": (
            "📊 Наблюдаемость RAG"
        ),
        "tools_observability": (
            "🛠️ Наблюдаемость инструментов"
        ),
        "timeline_viewer": (
            "🧭 Просмотр временной шкалы"
        ),
        "tools_analytics": (
            "📊 Аналитика инструментов"
        ),
        "health_center": (
            "❤️ Центр состояния системы"
        ),
        "llmops_observability": (
            "🛰️ Операции ИИ и наблюдаемость"
        ),
        "ai_cost_center": "💰 Центр затрат ИИ",
        "document_upload": (
            "📄 Загрузка документов"
        ),
        "user_memory": "🧠 Память пользователя",
        "export": "📤 Экспорт",
    },
    "sa": {
        "overview": "📌 نظرة عامة",
        "multichannel_events": (
            "🌐 أحداث متعددة القنوات"
        ),
        "international_view": "🌎 العرض الدولي",
        "diagnostics": "👤 التشخيصات",
        "feedbacks": "💬 الملاحظات",
        "evolution": "📈 التطور",
        "executive_reading": (
            "🧠 الملخص التنفيذي"
        ),
        "agent_evaluation": "🧪 تقييم الوكيل",
        "rag_observability": "📊 مراقبة RAG",
        "tools_observability": "🛠️ مراقبة الأدوات",
        "timeline_viewer": (
            "🧭 عارض المسار الزمني"
        ),
        "tools_analytics": "📊 تحليلات الأدوات",
        "health_center": "❤️ مركز صحة النظام",
        "llmops_observability": (
            "🛰️ عمليات الذكاء الاصطناعي والمراقبة"
        ),
        "ai_cost_center": (
            "💰 مركز تكاليف الذكاء الاصطناعي"
        ),
        "document_upload": "📄 تحميل المستندات",
        "user_memory": "🧠 ذاكرة المستخدم",
        "export": "📤 تصدير",
    },
}

MENU_TEXTS["en_gb"] = dict(
    MENU_TEXTS["en_us"]
)
MENU_TEXTS["en_gb"]["ai_cost_center"] = (
    "💰 AI Cost Centre"
)
MENU_TEXTS["en_gb"]["health_center"] = (
    "❤️ Health Centre"
)

MENU_TEXTS["ch"] = dict(
    MENU_TEXTS["de"]
)


LEGACY_MENU_PAGE_IDS: dict[str, str] = {
    "📌 Visão Geral": "overview",
    "🌐 Eventos Multicanal": "multichannel_events",
    "🌍 Visão Internacional": "international_view",
    "🌎 Visão Internacional": "international_view",
    "international_view": "international_view",
    "👤 Diagnósticos": "diagnostics",
    "diagnoses_page": "diagnostics",
    "💬 Feedbacks": "feedbacks",
    "feedback_page": "feedbacks",
    "📈 Evolução": "evolution",
    "evolution_page": "evolution",
    "🧠 Leitura Executiva": "executive_reading",
    "🧪 Avaliação do Agente": "agent_evaluation",
    "📊 Observabilidade RAG": "rag_observability",
    "🛠️ Observabilidade Tools": "tools_observability",
    "🧭 Timeline Viewer": "timeline_viewer",
    "📊 Analytics Tools": "tools_analytics",
    "❤️ Health Center": "health_center",
    "🛰️ LLMOps & Observabilidade": (
        "llmops_observability"
    ),
    "💰 LLM Cost Center": "ai_cost_center",
    "📄 Upload Documentos": "document_upload",
    "🧠 Memória Usuário": "user_memory",
    "📤 Exportar": "export",
}


for _menu_page_id in MENU_PAGE_IDS:
    LEGACY_MENU_PAGE_IDS.setdefault(
        _menu_page_id,
        _menu_page_id,
    )


def normalize_menu_page_id(
    value: Any,
) -> str:
    """
    Converte valores antigos do menu para IDs internos estáveis.

    Também reconhece rótulos traduzidos já exibidos aos usuários.
    """
    if value is None:
        return MENU_PAGE_IDS[0]

    raw_value = str(value).strip()

    if raw_value in MENU_PAGE_IDS:
        return raw_value

    legacy_page = LEGACY_MENU_PAGE_IDS.get(
        raw_value
    )

    if legacy_page is not None:
        return legacy_page

    for language_texts in MENU_TEXTS.values():
        for page_id, label in language_texts.items():
            if raw_value == label:
                return page_id

    return MENU_PAGE_IDS[0]


def menu_t(
    page_id: str,
    *,
    language: str | None = None,
) -> str:
    """Traduz somente o rótulo visual de uma página."""
    normalized_page_id = normalize_menu_page_id(
        page_id
    )

    return translate(
        MENU_TEXTS,
        normalized_page_id,
        language=language,
        default=normalized_page_id,
    )

MULTICHANNEL_UI_TEXTS: dict[str, dict[str, str]] = {
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
        "evaluation": "Avaliação",
        "comment": "Comentário",
        "feedbacks": "Feedbacks",
        "percentage": "Percentual",
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
        "evaluation": "Evaluation",
        "comment": "Comment",
        "feedbacks": "Feedback",
        "percentage": "Percentage",
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
        "feedback_received": "Feedback recibido",
        "telegram": "Telegram",
        "evaluation": "Evaluación",
        "comment": "Comentario",
        "feedbacks": "Feedback",
        "percentage": "Porcentaje",
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
        "evaluation": "Évaluation",
        "comment": "Commentaire",
        "feedbacks": "Retours",
        "percentage": "Pourcentage",
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
        "evaluation": "Bewertung",
        "comment": "Kommentar",
        "feedbacks": "Feedback",
        "percentage": "Prozentsatz",
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
        "evaluation": "Valutazione",
        "comment": "Commento",
        "feedbacks": "Feedback",
        "percentage": "Percentuale",
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
        "evaluation": "Evaluare",
        "comment": "Comentariu",
        "feedbacks": "Feedback",
        "percentage": "Procent",
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
        "evaluation": "Оцінка",
        "comment": "Коментар",
        "feedbacks": "Відгуки",
        "percentage": "Відсоток",
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
        "evaluation": "Оценка",
        "comment": "Комментарий",
        "feedbacks": "Отзывы",
        "percentage": "Процент",
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
        "evaluation": "التقييم",
        "comment": "التعليق",
        "feedbacks": "الملاحظات",
        "percentage": "النسبة المئوية",
        "not_informed": "غير محدد",
    },
}

MULTICHANNEL_UI_TEXTS["en_gb"] = dict(
    MULTICHANNEL_UI_TEXTS["en_us"]
)

MULTICHANNEL_UI_TEXTS["ch"] = dict(
    MULTICHANNEL_UI_TEXTS["de"]
)


CHANNEL_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "rag": "RAG",
        "web_app": "Aplicação web",
        "dashboard": "Dashboard",
        "pdf_download": "Download de PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "unknown": "Não informado",
    },
    "en_us": {
        "rag": "RAG",
        "web_app": "Web app",
        "dashboard": "Dashboard",
        "pdf_download": "PDF download",
        "telegram": "Telegram",
        "email": "Email",
        "unknown": "Not informed",
    },
    "es": {
        "rag": "RAG",
        "web_app": "Aplicación web",
        "dashboard": "Panel",
        "pdf_download": "Descarga de PDF",
        "telegram": "Telegram",
        "email": "Correo electrónico",
        "unknown": "No informado",
    },
    "fr": {
        "rag": "RAG",
        "web_app": "Application web",
        "dashboard": "Tableau de bord",
        "pdf_download": "Téléchargement PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "unknown": "Non renseigné",
    },
    "de": {
        "rag": "RAG",
        "web_app": "Webanwendung",
        "dashboard": "Dashboard",
        "pdf_download": "PDF-Download",
        "telegram": "Telegram",
        "email": "E-Mail",
        "unknown": "Nicht angegeben",
    },
    "it": {
        "rag": "RAG",
        "web_app": "Applicazione web",
        "dashboard": "Dashboard",
        "pdf_download": "Download PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "unknown": "Non specificato",
    },
    "ro": {
        "rag": "RAG",
        "web_app": "Aplicație web",
        "dashboard": "Panou",
        "pdf_download": "Descărcare PDF",
        "telegram": "Telegram",
        "email": "E-mail",
        "unknown": "Nespecificat",
    },
    "ua": {
        "rag": "RAG",
        "web_app": "Вебзастосунок",
        "dashboard": "Панель",
        "pdf_download": "Завантаження PDF",
        "telegram": "Telegram",
        "email": "Електронна пошта",
        "unknown": "Не вказано",
    },
    "ru": {
        "rag": "RAG",
        "web_app": "Веб-приложение",
        "dashboard": "Панель",
        "pdf_download": "Загрузка PDF",
        "telegram": "Telegram",
        "email": "Электронная почта",
        "unknown": "Не указано",
    },
    "sa": {
        "rag": "RAG",
        "web_app": "تطبيق الويب",
        "dashboard": "لوحة التحكم",
        "pdf_download": "تنزيل PDF",
        "telegram": "Telegram",
        "email": "البريد الإلكتروني",
        "unknown": "غير محدد",
    },
}

CHANNEL_TEXTS["en_gb"] = dict(
    CHANNEL_TEXTS["en_us"]
)

CHANNEL_TEXTS["ch"] = dict(
    CHANNEL_TEXTS["de"]
)


CHANNEL_VALUE_KEYS: dict[str, str] = {
    "rag": "rag",
    "web-app": "web_app",
    "web_app": "web_app",
    "web app": "web_app",
    "dashboard": "dashboard",
    "pdf-download": "pdf_download",
    "pdf_download": "pdf_download",
    "pdf download": "pdf_download",
    "telegram": "telegram",
    "email": "email",
    "e-mail": "email",
    "não informado": "unknown",
    "nao informado": "unknown",
    "not informed": "unknown",
    "unknown": "unknown",
    "none": "unknown",
    "null": "unknown",
    "nan": "unknown",
}


def multichannel_t(
    key: str,
    *,
    language: str | None = None,
    default: str | None = None,
) -> str:
    """Traduz textos visuais de eventos, funil e feedback."""
    return translate(
        MULTICHANNEL_UI_TEXTS,
        key,
        language=language,
        default=default,
    )


def translate_channel(
    value: Any,
    *,
    language: str | None = None,
) -> str:
    """
    Traduz canais conhecidos.

    Canais técnicos desconhecidos são preservados.
    """
    normalized = normalized_value(
        value
    )

    if not normalized:
        normalized = "unknown"

    channel_key = CHANNEL_VALUE_KEYS.get(
        normalized
    )

    if channel_key is None:
        return str(value)

    return translate(
        CHANNEL_TEXTS,
        channel_key,
        language=language,
        default=str(value),
    )


MULTICHANNEL_COLUMN_KEYS: dict[str, str] = {
    "id": "id",
    "data_hora": "date_time",
    "canal": "channel",
    "usuario": "user",
    "usuario_id": "user_id",
    "nome": "user",
    "idioma": "language",
    "moeda": "currency",
    "status": "status",
    "diagnostico_id": "diagnostic_id",
    "metadata": "metadata",
    "etapa": "stage",
    "quantidade": "quantity",
    "avaliacao": "evaluation",
    "comentario": "comment",
    "util": "evaluation",
}


def localize_multichannel_dataframe(
    dataframe: pd.DataFrame,
    *,
    language: str | None = None,
    translate_channel_values: bool = True,
    translate_feedback_values: bool = True,
    translate_status_values: bool = True,
) -> pd.DataFrame:
    """
    Cria uma tabela visual traduzida sem alterar o DataFrame original.
    """
    transforms: dict[
        str,
        Callable[[Any], Any],
    ] = {}

    if (
        translate_channel_values
        and "canal" in dataframe.columns
    ):
        transforms["canal"] = (
            lambda value: translate_channel(
                value,
                language=language,
            )
        )

    if (
        translate_feedback_values
        and "util" in dataframe.columns
    ):
        transforms["util"] = (
            lambda value: translate_useful(
                value,
                language=language,
            )
        )

    if (
        translate_status_values
        and "status" in dataframe.columns
    ):
        transforms["status"] = (
            lambda value: translate_status(
                value,
                language=language,
            )
        )

    return localize_dataframe(
        dataframe,
        column_keys=MULTICHANNEL_COLUMN_KEYS,
        column_texts=MULTICHANNEL_UI_TEXTS,
        value_transforms=transforms,
        language=language,
    )

def audit_page_language_pack(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    *,
    reference_language: str = DEFAULT_LANGUAGE,
    detect_english_fallbacks: bool = True,
) -> dict[str, dict[str, Any]]:
    """
    Audita uma página multilíngue.

    Detecta:
    - idiomas ausentes;
    - chaves ausentes;
    - chaves extras;
    - pacotes idênticos ao inglês;
    - valores vazios;
    - valores que retornaram a própria chave.
    """
    reference_texts = texts_by_language.get(
        reference_language,
        {},
    )

    reference_keys = set(
        reference_texts
    )

    english_texts = texts_by_language.get(
        "en_us",
        {},
    )

    report: dict[
        str,
        dict[str, Any],
    ] = {}

    for language in SUPPORTED_LANGUAGES:
        current_texts = texts_by_language.get(
            language
        )

        if current_texts is None:
            report[language] = {
                "missing_language": True,
                "missing": set(
                    reference_keys
                ),
                "extra": set(),
                "empty": set(),
                "key_fallback": set(),
                "same_as_english": False,
            }
            continue

        current_keys = set(
            current_texts
        )

        missing = (
            reference_keys
            - current_keys
        )

        extra = (
            current_keys
            - reference_keys
        )

        empty = {
            key
            for key, value
            in current_texts.items()
            if value is None
            or not str(value).strip()
        }

        key_fallback = {
            key
            for key, value
            in current_texts.items()
            if str(value).strip() == key
        }

        same_as_english = bool(
            detect_english_fallbacks
            and language
            not in {
                "en_us",
                "en_gb",
            }
            and english_texts
            and dict(current_texts)
            == dict(english_texts)
        )

        if (
            missing
            or extra
            or empty
            or key_fallback
            or same_as_english
        ):
            report[language] = {
                "missing_language": False,
                "missing": missing,
                "extra": extra,
                "empty": empty,
                "key_fallback": key_fallback,
                "same_as_english": (
                    same_as_english
                ),
            }

    return report


def merge_language_texts(
    base_texts: MutableMapping[
        str,
        dict[str, str],
    ],
    additions: Mapping[
        str,
        Mapping[str, str],
    ],
) -> None:
    """
    Mescla pacotes de tradução sem substituir o dicionário inteiro.

    Útil para páginas grandes divididas em vários blocos.
    """
    for language, texts in additions.items():
        normalized_language = (
            normalize_language(
                language
            )
        )

        base_texts.setdefault(
            normalized_language,
            {},
        ).update(
            {
                str(key): str(value)
                for key, value
                in texts.items()
            }
        )


def page_translate(
    texts_by_language: Mapping[
        str,
        Mapping[str, str],
    ],
    key: str,
    *,
    language: str | None = None,
    default: str | None = None,
    **format_values: Any,
) -> str:
    """
    Tradutor central para páginas grandes do dashboard.

    Usa apenas o idioma da interface e nunca o filtro
    de idioma dos registros.
    """
    return translate(
        texts_by_language,
        key,
        language=language,
        default=default,
        **format_values,
    )


# TOOLS_ANALYTICS_DYNAMIC_VALUES_I18N
#
# Traduções exclusivamente visuais para valores dinâmicos
# exibidos nas tabelas e nos gráficos de Tools Analytics.
# Os valores originais armazenados no banco não são alterados.

TOOLS_VALUE_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "tool.calculo_capacidade_semanal": (
            "Cálculo de capacidade semanal"
        ),
        "tool.simulacao_reserva": (
            "Simulação de formação de reserva"
        ),
        "intent.capacidade_semanal": (
            "Capacidade semanal"
        ),
        "intent.simulacao_reserva": (
            "Simulação de reserva"
        ),
        "origin.dashboard_rag": (
            "Dashboard RAG"
        ),
        "origin.teste_manual": (
            "Teste manual"
        ),
    },
    "en_us": {
        "tool.calculo_capacidade_semanal": (
            "Weekly capacity calculation"
        ),
        "tool.simulacao_reserva": (
            "Reserve building simulation"
        ),
        "intent.capacidade_semanal": (
            "Weekly capacity"
        ),
        "intent.simulacao_reserva": (
            "Reserve simulation"
        ),
        "origin.dashboard_rag": (
            "RAG dashboard"
        ),
        "origin.teste_manual": (
            "Manual test"
        ),
    },
    "en_gb": {
        "tool.calculo_capacidade_semanal": (
            "Weekly capacity calculation"
        ),
        "tool.simulacao_reserva": (
            "Reserve building simulation"
        ),
        "intent.capacidade_semanal": (
            "Weekly capacity"
        ),
        "intent.simulacao_reserva": (
            "Reserve simulation"
        ),
        "origin.dashboard_rag": (
            "RAG dashboard"
        ),
        "origin.teste_manual": (
            "Manual test"
        ),
    },
    "es": {
        "tool.calculo_capacidade_semanal": (
            "Cálculo de capacidad semanal"
        ),
        "tool.simulacao_reserva": (
            "Simulación de formación de reserva"
        ),
        "intent.capacidade_semanal": (
            "Capacidad semanal"
        ),
        "intent.simulacao_reserva": (
            "Simulación de reserva"
        ),
        "origin.dashboard_rag": (
            "Panel RAG"
        ),
        "origin.teste_manual": (
            "Prueba manual"
        ),
    },
    "fr": {
        "tool.calculo_capacidade_semanal": (
            "Calcul de capacité hebdomadaire"
        ),
        "tool.simulacao_reserva": (
            "Simulation de constitution de réserve"
        ),
        "intent.capacidade_semanal": (
            "Capacité hebdomadaire"
        ),
        "intent.simulacao_reserva": (
            "Simulation de réserve"
        ),
        "origin.dashboard_rag": (
            "Tableau de bord RAG"
        ),
        "origin.teste_manual": (
            "Test manuel"
        ),
    },
    "de": {
        "tool.calculo_capacidade_semanal": (
            "Wöchentliche Kapazitätsberechnung"
        ),
        "tool.simulacao_reserva": (
            "Simulation der Reservebildung"
        ),
        "intent.capacidade_semanal": (
            "Wöchentliche Kapazität"
        ),
        "intent.simulacao_reserva": (
            "Reservesimulation"
        ),
        "origin.dashboard_rag": (
            "RAG-Dashboard"
        ),
        "origin.teste_manual": (
            "Manueller Test"
        ),
    },
    "it": {
        "tool.calculo_capacidade_semanal": (
            "Calcolo della capacità settimanale"
        ),
        "tool.simulacao_reserva": (
            "Simulazione di creazione della riserva"
        ),
        "intent.capacidade_semanal": (
            "Capacità settimanale"
        ),
        "intent.simulacao_reserva": (
            "Simulazione della riserva"
        ),
        "origin.dashboard_rag": (
            "Dashboard RAG"
        ),
        "origin.teste_manual": (
            "Test manuale"
        ),
    },
    "ro": {
        "tool.calculo_capacidade_semanal": (
            "Calculul capacității săptămânale"
        ),
        "tool.simulacao_reserva": (
            "Simularea formării rezervei"
        ),
        "intent.capacidade_semanal": (
            "Capacitate săptămânală"
        ),
        "intent.simulacao_reserva": (
            "Simulare rezervă"
        ),
        "origin.dashboard_rag": (
            "Tablou RAG"
        ),
        "origin.teste_manual": (
            "Test manual"
        ),
    },
    "ua": {
        "tool.calculo_capacidade_semanal": (
            "Розрахунок тижневої потужності"
        ),
        "tool.simulacao_reserva": (
            "Симуляція формування резерву"
        ),
        "intent.capacidade_semanal": (
            "Тижнева потужність"
        ),
        "intent.simulacao_reserva": (
            "Симуляція резерву"
        ),
        "origin.dashboard_rag": (
            "RAG-панель"
        ),
        "origin.teste_manual": (
            "Ручний тест"
        ),
    },
    "ru": {
        "tool.calculo_capacidade_semanal": (
            "Еженедельный расчёт мощности"
        ),
        "tool.simulacao_reserva": (
            "Симуляция формирования резерва"
        ),
        "intent.capacidade_semanal": (
            "Еженедельная мощность"
        ),
        "intent.simulacao_reserva": (
            "Симуляция резерва"
        ),
        "origin.dashboard_rag": (
            "RAG-панель"
        ),
        "origin.teste_manual": (
            "Ручной тест"
        ),
    },
    "sa": {
        "tool.calculo_capacidade_semanal": (
            "حساب السعة الأسبوعية"
        ),
        "tool.simulacao_reserva": (
            "محاكاة تكوين الاحتياطي"
        ),
        "intent.capacidade_semanal": (
            "السعة الأسبوعية"
        ),
        "intent.simulacao_reserva": (
            "محاكاة الاحتياطي"
        ),
        "origin.dashboard_rag": (
            "لوحة RAG"
        ),
        "origin.teste_manual": (
            "اختبار يدوي"
        ),
    },
    "ch": {
        "tool.calculo_capacidade_semanal": (
            "Wöchentliche Kapazitätsberechnung"
        ),
        "tool.simulacao_reserva": (
            "Simulation der Reservebildung"
        ),
        "intent.capacidade_semanal": (
            "Wöchentliche Kapazität"
        ),
        "intent.simulacao_reserva": (
            "Reservesimulation"
        ),
        "origin.dashboard_rag": (
            "RAG-Dashboard"
        ),
        "origin.teste_manual": (
            "Manueller Test"
        ),
    },
}


def analytics_value_t(
    key: str,
    *,
    language: str = "pt",
    fallback: str | None = None,
) -> str:
    """
    Traduz um valor dinâmico somente para exibição.

    Quando não existe uma tradução cadastrada, preserva
    exatamente o valor técnico recebido.
    """
    idioma = str(
        language or "pt"
    ).strip().lower().replace(
        "-",
        "_",
    )

    aliases = {
        "pt_br": "pt",
        "en": "en_us",
        "uk": "ua",
        "ar": "sa",
    }

    idioma = aliases.get(
        idioma,
        idioma,
    )

    texts = TOOLS_VALUE_TEXTS.get(
        idioma,
        TOOLS_VALUE_TEXTS["pt"],
    )

    value = texts.get(key)

    if value is not None:
        return value

    if fallback is not None:
        return fallback

    return key




# TOOLS_ANALYTICS_DYNAMIC_TOOL_ALIASES
#
# Relaciona nomes técnicos e nomes amigáveis vindos
# da observabilidade ao mesmo identificador visual.

TOOLS_DYNAMIC_VALUE_ALIASES = {
    "calculo_capacidade_semanal": (
        "calculo_capacidade_semanal"
    ),
    "calculo_de_capacidade_semanal": (
        "calculo_capacidade_semanal"
    ),
    "simulacao_reserva": (
        "simulacao_reserva"
    ),
    "simulacao_de_reserva": (
        "simulacao_reserva"
    ),
    "simulacao_de_formacao_de_reserva": (
        "simulacao_reserva"
    ),
    "simulacao_formacao_reserva": (
        "simulacao_reserva"
    ),
}


def normalize_dynamic_value_key(
    value: object,
) -> str:
    """
    Normaliza um valor visual sem modificar o dado original.

    Exemplos:
    Cálculo de capacidade semanal
    -> calculo_de_capacidade_semanal

    simulacao_reserva
    -> simulacao_reserva
    """
    raw = str(
        value or ""
    ).strip().lower()

    normalized = unicodedata.normalize(
        "NFKD",
        raw,
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )

    cleaned = []

    previous_separator = False

    for character in without_accents:
        if character.isalnum():
            cleaned.append(character)
            previous_separator = False
            continue

        if not previous_separator:
            cleaned.append("_")
            previous_separator = True

    key = "".join(
        cleaned
    ).strip("_")

    return TOOLS_DYNAMIC_VALUE_ALIASES.get(
        key,
        key,
    )


def translate_tool_name(
    value: object,
    *,
    language: str = "pt",
) -> str:
    """
    Traduz visualmente o nome de uma Tool.

    Aceita tanto o código técnico quanto o nome
    amigável registrado na observabilidade.
    """
    raw = str(
        value or ""
    ).strip()

    normalized_key = normalize_dynamic_value_key(
        raw
    )

    return analytics_value_t(
        f"tool.{normalized_key}",
        language=language,
        fallback=raw,
    )


def translate_intention(
    value: object,
    *,
    language: str = "pt",
) -> str:
    """
    Traduz visualmente uma intenção.
    """
    raw = str(
        value or ""
    ).strip()

    return analytics_value_t(
        f"intent.{raw}",
        language=language,
        fallback=raw,
    )


def translate_origin(
    value: object,
    *,
    language: str = "pt",
) -> str:
    """
    Traduz visualmente uma origem.
    """
    raw = str(
        value or ""
    ).strip()

    return analytics_value_t(
        f"origin.{raw}",
        language=language,
        fallback=raw,
    )


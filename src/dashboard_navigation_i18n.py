"""
Traduções dos grupos principais da navegação da INNA AI Platform.
"""

from __future__ import annotations

from src.dashboard_navigation import (
    NAVIGATION_GROUP_IDS,
)

NAVIGATION_NAVIGATION_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "platform_area": "Área da plataforma",
        "area_pages": "Páginas da área",
    },
    "en_us": {
        "platform_area": "Platform area",
        "area_pages": "Area pages",
    },
    "es": {
        "platform_area": "Área de la plataforma",
        "area_pages": "Páginas del área",
    },
    "fr": {
        "platform_area": "Zone de la plateforme",
        "area_pages": "Pages de la zone",
    },
    "de": {
        "platform_area": "Plattformbereich",
        "area_pages": "Seiten des Bereichs",
    },
    "it": {
        "platform_area": "Area della piattaforma",
        "area_pages": "Pagine dell’area",
    },
    "ro": {
        "platform_area": "Zona platformei",
        "area_pages": "Paginile zonei",
    },
    "ua": {
        "platform_area": "Розділ платформи",
        "area_pages": "Сторінки розділу",
    },
    "ru": {
        "platform_area": "Раздел платформы",
        "area_pages": "Страницы раздела",
    },
    "sa": {
        "platform_area": "قسم المنصة",
        "area_pages": "صفحات القسم",
    },
}


NAVIGATION_NAVIGATION_TEXTS["en_gb"] = dict(NAVIGATION_NAVIGATION_TEXTS["en_us"])

NAVIGATION_NAVIGATION_TEXTS["ch"] = dict(NAVIGATION_NAVIGATION_TEXTS["de"])


def navigation_ui_t(
    key: str,
    language: str = "pt",
) -> str:
    """Traduz rótulos auxiliares da navegação."""

    selected_language = language if language in NAVIGATION_NAVIGATION_TEXTS else "pt"

    return NAVIGATION_NAVIGATION_TEXTS[selected_language].get(
        key,
        NAVIGATION_NAVIGATION_TEXTS["pt"].get(
            key,
            key,
        ),
    )


NAVIGATION_GROUP_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "overview": "🏠 Visão Geral",
        "financial_solutions": ("💰 Soluções Financeiras"),
        "enterprise_rag": "📚 Enterprise RAG",
        "ai_operations": ("⚙️ Operação e Governança de IA"),
        "tools_analytics": ("🛠️ Ferramentas e Analytics"),
        "administration": "🔐 Administração",
    },
    "en_us": {
        "overview": "🏠 Overview",
        "financial_solutions": ("💰 Financial Solutions"),
        "enterprise_rag": "📚 Enterprise RAG",
        "ai_operations": ("⚙️ AI Operations and Governance"),
        "tools_analytics": ("🛠️ Tools and Analytics"),
        "administration": "🔐 Administration",
    },
    "es": {
        "overview": "🏠 Vista general",
        "financial_solutions": ("💰 Soluciones financieras"),
        "enterprise_rag": "📚 RAG empresarial",
        "ai_operations": ("⚙️ Operación y gobernanza de IA"),
        "tools_analytics": ("🛠️ Herramientas y analítica"),
        "administration": "🔐 Administración",
    },
    "fr": {
        "overview": "🏠 Vue d’ensemble",
        "financial_solutions": ("💰 Solutions financières"),
        "enterprise_rag": "📚 RAG d’entreprise",
        "ai_operations": ("⚙️ Opérations et gouvernance IA"),
        "tools_analytics": ("🛠️ Outils et analytique"),
        "administration": "🔐 Administration",
    },
    "de": {
        "overview": "🏠 Übersicht",
        "financial_solutions": ("💰 Finanzlösungen"),
        "enterprise_rag": "📚 Enterprise RAG",
        "ai_operations": ("⚙️ KI-Betrieb und Governance"),
        "tools_analytics": ("🛠️ Werkzeuge und Analysen"),
        "administration": "🔐 Administration",
    },
    "it": {
        "overview": "🏠 Panoramica",
        "financial_solutions": ("💰 Soluzioni finanziarie"),
        "enterprise_rag": "📚 RAG aziendale",
        "ai_operations": ("⚙️ Operazioni e governance IA"),
        "tools_analytics": ("🛠️ Strumenti e analisi"),
        "administration": "🔐 Amministrazione",
    },
    "ro": {
        "overview": "🏠 Prezentare generală",
        "financial_solutions": ("💰 Soluții financiare"),
        "enterprise_rag": ("📚 RAG pentru întreprinderi"),
        "ai_operations": ("⚙️ Operațiuni și guvernanță IA"),
        "tools_analytics": ("🛠️ Instrumente și analiză"),
        "administration": "🔐 Administrare",
    },
    "ua": {
        "overview": "🏠 Загальний огляд",
        "financial_solutions": ("💰 Фінансові рішення"),
        "enterprise_rag": ("📚 Корпоративний RAG"),
        "ai_operations": ("⚙️ Операції та управління ШІ"),
        "tools_analytics": ("🛠️ Інструменти й аналітика"),
        "administration": "🔐 Адміністрування",
    },
    "ru": {
        "overview": "🏠 Общий обзор",
        "financial_solutions": ("💰 Финансовые решения"),
        "enterprise_rag": ("📚 Корпоративный RAG"),
        "ai_operations": ("⚙️ Операции и управление ИИ"),
        "tools_analytics": ("🛠️ Инструменты и аналитика"),
        "administration": "🔐 Администрирование",
    },
    "sa": {
        "overview": "🏠 نظرة عامة",
        "financial_solutions": ("💰 الحلول المالية"),
        "enterprise_rag": ("📚 نظام RAG للمؤسسات"),
        "ai_operations": ("⚙️ عمليات وحوكمة الذكاء الاصطناعي"),
        "tools_analytics": ("🛠️ الأدوات والتحليلات"),
        "administration": "🔐 الإدارة",
    },
}


PLATFORM_MODULES_GROUP_TEXTS: dict[
    str,
    str,
] = {
    "pt": "🧩 Módulos da Plataforma",
    "en_us": "🧩 Platform Modules",
    "es": "🧩 Módulos de la Plataforma",
    "fr": "🧩 Modules de la Plateforme",
    "de": "🧩 Plattformmodule",
    "it": "🧩 Moduli della Piattaforma",
    "ro": "🧩 Modulele Platformei",
    "ua": "🧩 Модулі Платформи",
    "ru": "🧩 Модули Платформы",
    "sa": "🧩 وحدات المنصة",
}


for _language, _label in PLATFORM_MODULES_GROUP_TEXTS.items():
    NAVIGATION_GROUP_TEXTS[_language]["platform_modules"] = _label


NAVIGATION_GROUP_TEXTS["en_gb"] = dict(NAVIGATION_GROUP_TEXTS["en_us"])

NAVIGATION_GROUP_TEXTS["ch"] = dict(NAVIGATION_GROUP_TEXTS["de"])


def navigation_group_t(
    group_id: str,
    language: str = "pt",
) -> str:
    """Traduz um grupo com fallback seguro."""

    selected_language = language if language in NAVIGATION_GROUP_TEXTS else "pt"

    language_texts = NAVIGATION_GROUP_TEXTS[selected_language]

    return language_texts.get(
        group_id,
        NAVIGATION_GROUP_TEXTS["pt"].get(
            group_id,
            group_id,
        ),
    )


def validate_navigation_group_texts() -> None:
    """Valida cobertura e conteúdo das traduções."""

    expected_group_ids = set(NAVIGATION_GROUP_IDS)

    for language, texts in NAVIGATION_GROUP_TEXTS.items():
        if set(texts) != expected_group_ids:
            raise ValueError(f"Contrato inválido de tradução: {language}")

        for group_id, label in texts.items():
            if not isinstance(label, str):
                raise TypeError(f"Rótulo inválido: {language}.{group_id}")

            if not label.strip():
                raise ValueError(f"Rótulo vazio: {language}.{group_id}")


validate_navigation_group_texts()

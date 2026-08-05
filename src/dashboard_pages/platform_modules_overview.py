"""
Componente da Visão Geral dos módulos da INNA AI Platform.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.dashboard_pages.platform_business_solution_details import (
    BUSINESS_SOLUTION_STATE_KEY,
    render_platform_business_solution_details,
)
from src.dashboard_pages.platform_sector_solution_details import (
    SECTOR_SOLUTION_STATE_KEY,
    render_platform_sector_solution_details,
)
from src.dashboard_pages.platform_technology_solution_details import (
    TECHNOLOGY_SOLUTION_STATE_KEY,
    render_platform_technology_solution_details,
)
from src.platform_business_solutions import (
    platform_business_solution,
)
from src.platform_modules import (
    PLATFORM_MODULES,
    PlatformModuleCategory,
    PlatformModuleStatus,
    TechnologyFamily,
)
from src.platform_modules_i18n import (
    platform_integration_type_t,
    platform_module_category_t,
    platform_module_status_t,
    platform_module_t,
    technology_family_t,
)
from src.platform_sector_solutions import (
    platform_sector_solution,
)
from src.platform_technology_solutions import (
    platform_technology_solution,
)


@dataclass(frozen=True, slots=True)
class PlatformModuleCard:
    """Dados visuais de um módulo da plataforma."""

    module_id: str
    title: str
    category: PlatformModuleCategory
    technology_family: TechnologyFamily | None
    technology_family_label: str | None
    status: str
    status_code: PlatformModuleStatus
    integration_type: str
    integration_label: str
    is_available: bool


OVERVIEW_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "title": "Módulos da INNA AI Platform",
        "caption": (
            "Soluções ativas, integrações em andamento "
            "e módulos planejados da plataforma."
        ),
        "integration": "Integração",
        "available": "Disponível",
        "unavailable": "Ainda não disponível",
    },
    "en_us": {
        "title": "INNA AI Platform Modules",
        "caption": (
            "Active solutions, integrations in progress and planned platform modules."
        ),
        "integration": "Integration",
        "available": "Available",
        "unavailable": "Not available yet",
    },
    "es": {
        "title": "Módulos de INNA AI Platform",
        "caption": (
            "Soluciones activas, integraciones en curso y módulos planificados."
        ),
        "integration": "Integración",
        "available": "Disponible",
        "unavailable": "Aún no disponible",
    },
    "fr": {
        "title": "Modules de la plateforme INNA AI",
        "caption": ("Solutions actives, intégrations en cours et modules planifiés."),
        "integration": "Intégration",
        "available": "Disponible",
        "unavailable": "Pas encore disponible",
    },
    "de": {
        "title": "Module der INNA AI Platform",
        "caption": (
            "Aktive Lösungen, laufende Integrationen und geplante Plattformmodule."
        ),
        "integration": "Integration",
        "available": "Verfügbar",
        "unavailable": "Noch nicht verfügbar",
    },
    "it": {
        "title": "Moduli della piattaforma INNA AI",
        "caption": ("Soluzioni attive, integrazioni in corso e moduli pianificati."),
        "integration": "Integrazione",
        "available": "Disponibile",
        "unavailable": "Non ancora disponibile",
    },
    "ro": {
        "title": "Modulele platformei INNA AI",
        "caption": ("Soluții active, integrări în desfășurare și module planificate."),
        "integration": "Integrare",
        "available": "Disponibil",
        "unavailable": "Încă indisponibil",
    },
    "ua": {
        "title": "Модулі платформи INNA AI",
        "caption": ("Активні рішення, поточні інтеграції та заплановані модулі."),
        "integration": "Інтеграція",
        "available": "Доступно",
        "unavailable": "Ще недоступно",
    },
    "ru": {
        "title": "Модули платформы INNA AI",
        "caption": ("Активные решения, текущие интеграции и запланированные модули."),
        "integration": "Интеграция",
        "available": "Доступно",
        "unavailable": "Пока недоступно",
    },
    "sa": {
        "title": "وحدات منصة INNA للذكاء الاصطناعي",
        "caption": ("الحلول النشطة وعمليات التكامل الجارية والوحدات المخطط لها."),
        "integration": "التكامل",
        "available": "متاح",
        "unavailable": "غير متاح بعد",
    },
}

OVERVIEW_TEXTS["en_gb"] = dict(OVERVIEW_TEXTS["en_us"])

OVERVIEW_TEXTS["ch"] = dict(OVERVIEW_TEXTS["de"])


def overview_t(
    key: str,
    language: str = "pt",
) -> str:
    """Traduz textos da seção de módulos."""

    selected_language = language if language in OVERVIEW_TEXTS else "pt"

    return OVERVIEW_TEXTS[selected_language].get(
        key,
        OVERVIEW_TEXTS["pt"].get(
            key,
            key,
        ),
    )


def build_platform_module_cards(
    language: str = "pt",
) -> tuple[PlatformModuleCard, ...]:
    """Prepara os cards com dados do registro central."""

    return tuple(
        PlatformModuleCard(
            module_id=module.module_id,
            title=platform_module_t(
                module.module_id,
                language,
            ),
            category=module.category,
            technology_family=module.technology_family,
            technology_family_label=(
                technology_family_t(
                    module.technology_family,
                    language,
                )
                if module.technology_family is not None
                else None
            ),
            status=platform_module_status_t(
                module.status,
                language,
            ),
            status_code=module.status,
            integration_type=module.integration_type,
            integration_label=platform_integration_type_t(
                module.integration_type,
                language,
            ),
            is_available=module.is_available,
        )
        for module in PLATFORM_MODULES
    )


def _render_module_card_grid(
    cards: tuple[PlatformModuleCard, ...],
    language: str,
) -> None:
    """Renderiza uma grade de cards em três colunas."""

    for start in range(
        0,
        len(cards),
        3,
    ):
        columns = st.columns(3)

        for column, card in zip(
            columns,
            cards[start : start + 3],
            strict=False,
        ):
            with column:
                with st.container(border=True):
                    st.markdown(f"**{card.title}**")

                    st.write(f"**{card.status}**")

                    st.caption(
                        f"{overview_t('integration', language)}: "
                        f"{card.integration_label}"
                    )

                    availability_key = (
                        "available" if card.is_available else "unavailable"
                    )

                    st.caption(
                        overview_t(
                            availability_key,
                            language,
                        )
                    )

                    sector_solution = platform_sector_solution(card.module_id)

                    if sector_solution is not None:
                        if st.button(
                            "Ver detalhes",
                            key=(f"open_sector_solution_{card.module_id}"),
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                TECHNOLOGY_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[SECTOR_SOLUTION_STATE_KEY] = card.module_id

                            st.rerun()

                    business_solution = platform_business_solution(card.module_id)

                    if business_solution is not None:
                        if st.button(
                            "Ver detalhes",
                            key=(f"open_business_solution_{card.module_id}"),
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                TECHNOLOGY_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[BUSINESS_SOLUTION_STATE_KEY] = (
                                card.module_id
                            )

                            st.rerun()

                    technology_solution = platform_technology_solution(card.module_id)

                    if technology_solution is not None:
                        if st.button(
                            "Ver detalhes",
                            key=(f"open_technology_solution_{card.module_id}"),
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[TECHNOLOGY_SOLUTION_STATE_KEY] = (
                                card.module_id
                            )

                            st.rerun()


def render_platform_modules_overview(
    language: str = "pt",
) -> None:
    """Renderiza o catálogo ou os detalhes especializados."""

    selected_technology_solution_id = st.session_state.get(
        TECHNOLOGY_SOLUTION_STATE_KEY
    )

    if selected_technology_solution_id:
        render_platform_technology_solution_details(
            selected_technology_solution_id,
            language,
        )
        return

    selected_business_solution_id = st.session_state.get(BUSINESS_SOLUTION_STATE_KEY)

    if selected_business_solution_id:
        render_platform_business_solution_details(
            selected_business_solution_id,
            language,
        )
        return

    selected_sector_solution_id = st.session_state.get(SECTOR_SOLUTION_STATE_KEY)

    if selected_sector_solution_id:
        render_platform_sector_solution_details(
            selected_sector_solution_id,
            language,
        )
        return

    st.subheader(overview_t("title", language))

    st.caption(overview_t("caption", language))

    cards = build_platform_module_cards(language)

    for category in PlatformModuleCategory:
        category_cards = tuple(card for card in cards if card.category is category)

        if not category_cards:
            continue

        st.markdown(f"### {platform_module_category_t(category, language)}")

        if category is PlatformModuleCategory.TECHNOLOGY_CORE:
            for family in TechnologyFamily:
                family_cards = tuple(
                    card for card in category_cards if card.technology_family is family
                )

                if not family_cards:
                    continue

                st.markdown(f"#### {technology_family_t(family, language)}")

                _render_module_card_grid(
                    family_cards,
                    language,
                )
        else:
            _render_module_card_grid(
                category_cards,
                language,
            )

        st.write("")

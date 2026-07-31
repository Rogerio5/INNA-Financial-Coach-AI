"""
Registro central da navegação modular da INNA AI Platform.

Este módulo organiza páginas reais do dashboard em grupos estáveis,
sem misturar traduções, renderização Streamlit ou regras de negócio.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.dashboard_i18n import MENU_PAGE_IDS


@dataclass(frozen=True, slots=True)
class NavigationGroup:
    """Grupo principal da navegação administrativa."""

    group_id: str
    icon: str
    default_page_id: str
    page_ids: tuple[str, ...]


NAVIGATION_GROUPS: tuple[NavigationGroup, ...] = (
    NavigationGroup(
        group_id="overview",
        icon="🏠",
        default_page_id="overview",
        page_ids=(
            "overview",
            "executive_reading",
            "evolution",
            "international_view",
        ),
    ),
    NavigationGroup(
        group_id="financial_solutions",
        icon="💰",
        default_page_id="diagnostics",
        page_ids=(
            "diagnostics",
            "feedbacks",
            "user_memory",
        ),
    ),
    NavigationGroup(
        group_id="enterprise_rag",
        icon="📚",
        default_page_id="document_upload",
        page_ids=(
            "document_upload",
            "rag_observability",
            "rag_evaluation_lab",
            "agent_evaluation",
        ),
    ),
    NavigationGroup(
        group_id="ai_operations",
        icon="⚙️",
        default_page_id="health_center",
        page_ids=(
            "health_center",
            "llmops_observability",
            "timeline_viewer",
            "ai_cost_center",
        ),
    ),
    NavigationGroup(
        group_id="tools_analytics",
        icon="🛠️",
        default_page_id="tools_observability",
        page_ids=(
            "tools_observability",
            "tools_analytics",
            "multichannel_events",
        ),
    ),
    NavigationGroup(
        group_id="administration",
        icon="🔐",
        default_page_id="export",
        page_ids=(
            "export",
        ),
    ),
)


NAVIGATION_GROUP_IDS: tuple[str, ...] = tuple(
    group.group_id
    for group in NAVIGATION_GROUPS
)


NAVIGATION_GROUP_BY_ID: dict[str, NavigationGroup] = {
    group.group_id: group
    for group in NAVIGATION_GROUPS
}


PAGE_TO_NAVIGATION_GROUP: dict[str, str] = {
    page_id: group.group_id
    for group in NAVIGATION_GROUPS
    for page_id in group.page_ids
}


def navigation_group_for_page(
    page_id: str,
) -> str:
    """Retorna o grupo da página ou o grupo inicial."""

    return PAGE_TO_NAVIGATION_GROUP.get(
        page_id,
        NAVIGATION_GROUPS[0].group_id,
    )


def pages_for_navigation_group(
    group_id: str,
) -> tuple[str, ...]:
    """Retorna as páginas de um grupo válido."""

    group = NAVIGATION_GROUP_BY_ID.get(group_id)

    if group is None:
        return NAVIGATION_GROUPS[0].page_ids

    return group.page_ids


def default_page_for_navigation_group(
    group_id: str,
) -> str:
    """Retorna a página inicial do grupo."""

    group = NAVIGATION_GROUP_BY_ID.get(group_id)

    if group is None:
        return NAVIGATION_GROUPS[0].default_page_id

    return group.default_page_id


def validate_navigation_registry() -> None:
    """Valida integridade, duplicidade e cobertura do registro."""

    registered_pages = [
        page_id
        for group in NAVIGATION_GROUPS
        for page_id in group.page_ids
    ]

    if len(registered_pages) != len(set(registered_pages)):
        raise ValueError(
            "Existem páginas duplicadas na navegação."
        )

    registered_page_set = set(registered_pages)
    menu_page_set = set(MENU_PAGE_IDS)

    missing_pages = menu_page_set - registered_page_set
    unknown_pages = registered_page_set - menu_page_set

    if missing_pages:
        raise ValueError(
            "Páginas sem grupo: "
            f"{sorted(missing_pages)}"
        )

    if unknown_pages:
        raise ValueError(
            "Páginas desconhecidas: "
            f"{sorted(unknown_pages)}"
        )

    for group in NAVIGATION_GROUPS:
        if group.default_page_id not in group.page_ids:
            raise ValueError(
                "Página padrão fora do grupo: "
                f"{group.group_id}"
            )


validate_navigation_registry()

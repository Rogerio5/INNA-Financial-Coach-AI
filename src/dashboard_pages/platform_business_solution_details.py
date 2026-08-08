"""Página de detalhes das soluções empresariais da INNA."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.platform_business_solutions import (
    BusinessCapability,
    PlatformBusinessSolution,
    platform_business_solution,
)
from src.platform_modules_i18n import platform_module_t

BUSINESS_SOLUTION_STATE_KEY = "selected_platform_business_solution_id"


DETAIL_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "back": "← Voltar ao catálogo",
        "status": "Status",
        "integration": "Integração",
        "planned": "Planejado",
        "hybrid": "Híbrida",
        "areas": "Áreas especializadas",
        "capabilities": "submódulos",
        "technologies": "Tecnologias conectadas",
        "not_found": "Solução empresarial não encontrada.",
    },
    "en_us": {
        "back": "← Back to catalog",
        "status": "Status",
        "integration": "Integration",
        "planned": "Planned",
        "hybrid": "Hybrid",
        "areas": "Specialized areas",
        "capabilities": "submodules",
        "technologies": "Connected technologies",
        "not_found": "Business solution not found.",
    },
    "es": {
        "back": "← Volver al catálogo",
        "status": "Estado",
        "integration": "Integración",
        "planned": "Planificado",
        "hybrid": "Híbrida",
        "areas": "Áreas especializadas",
        "capabilities": "submódulos",
        "technologies": "Tecnologías conectadas",
        "not_found": "Solución businessial no encontrada.",
    },
}


@dataclass(frozen=True, slots=True)
class BusinessCapabilityDetail:
    """Dados visuais de uma capacidade setorial."""

    capability_id: str
    title: str
    description: str
    technologies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BusinessAreaDetail:
    """Dados visuais de uma área setorial."""

    area_id: str
    title: str
    capabilities: tuple[BusinessCapabilityDetail, ...]


@dataclass(frozen=True, slots=True)
class BusinessSolutionDetail:
    """Dados completos para a página setorial."""

    solution_id: str
    title: str
    description: str
    status: str
    integration_type: str
    areas: tuple[BusinessAreaDetail, ...]

    @property
    def capability_count(self) -> int:
        """Quantidade de capacidades exibidas."""

        return sum(len(area.capabilities) for area in self.areas)


def detail_t(
    key: str,
    language: str = "pt",
) -> str:
    """Traduz textos da página de detalhes."""

    selected_language = language if language in DETAIL_TEXTS else "pt"

    return DETAIL_TEXTS[selected_language].get(
        key,
        DETAIL_TEXTS["pt"].get(
            key,
            key,
        ),
    )


def _build_capability_detail(
    capability: BusinessCapability,
    language: str,
) -> BusinessCapabilityDetail:
    """Converte uma capacidade para exibição."""

    technologies = tuple(
        platform_module_t(
            dependency,
            language,
        )
        for dependency in (capability.technology_dependencies)
    )

    return BusinessCapabilityDetail(
        capability_id=capability.capability_id,
        title=capability.title,
        description=capability.description,
        technologies=technologies,
    )


def build_business_solution_detail(
    solution: PlatformBusinessSolution,
    language: str = "pt",
) -> BusinessSolutionDetail:
    """Prepara os dados da solução empresarial."""

    return BusinessSolutionDetail(
        solution_id=solution.solution_id,
        title=f"{solution.icon} {solution.title}",
        description=solution.description,
        status=detail_t(
            solution.status.value,
            language,
        ),
        integration_type=detail_t(
            solution.integration_type,
            language,
        ),
        areas=tuple(
            BusinessAreaDetail(
                area_id=area.area_id,
                title=area.title,
                capabilities=tuple(
                    _build_capability_detail(
                        capability,
                        language,
                    )
                    for capability in area.capabilities
                ),
            )
            for area in solution.areas
        ),
    )


def clear_selected_business_solution() -> None:
    """Remove a solução selecionada da sessão."""

    st.session_state.pop(
        BUSINESS_SOLUTION_STATE_KEY,
        None,
    )


def render_platform_business_solution_details(
    solution_id: str,
    language: str = "pt",
) -> None:
    """Renderiza áreas e submódulos da solução."""

    solution = platform_business_solution(solution_id)

    if solution is None:
        st.error(
            detail_t(
                "not_found",
                language,
            )
        )
        return

    if st.button(
        detail_t(
            "back",
            language,
        ),
        key="business_solution_back_to_catalog",
    ):
        clear_selected_business_solution()
        st.rerun()

    detail = build_business_solution_detail(
        solution,
        language,
    )

    st.subheader(detail.title)
    st.write(detail.description)

    status_column, integration_column = st.columns(2)

    status_column.metric(
        detail_t(
            "status",
            language,
        ),
        detail.status,
    )

    integration_column.metric(
        detail_t(
            "integration",
            language,
        ),
        detail.integration_type,
    )

    st.markdown(f"### {detail_t('areas', language)}")

    for area in detail.areas:
        label = (
            f"{area.title} — "
            f"{len(area.capabilities)} "
            f"{detail_t('capabilities', language)}"
        )

        with st.expander(
            label,
            expanded=False,
        ):
            for capability in area.capabilities:
                with st.container(
                    border=True,
                ):
                    st.markdown(f"**{capability.title}**")

                    st.write(capability.description)

                    st.caption(
                        detail_t(
                            "technologies",
                            language,
                        )
                    )

                    for technology in capability.technologies:
                        st.markdown(f"- {technology}")

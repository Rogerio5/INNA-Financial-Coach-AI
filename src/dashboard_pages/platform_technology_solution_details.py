"""Página de detalhes das soluções tecnológicas da INNA."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.platform_modules_i18n import platform_module_t
from src.platform_technology_relationships import (
    technology_dependencies_for,
    technology_dependents_for,
)
from src.platform_technology_solutions import (
    PlatformTechnologySolution,
    TechnologyCapability,
    platform_technology_solution,
)

TECHNOLOGY_SOLUTION_STATE_KEY = "selected_platform_technology_solution_id"


DETAIL_TEXTS: dict[str, dict[str, str]] = {
    "pt": {
        "back": "← Voltar ao catálogo",
        "status": "Status",
        "integration": "Integração",
        "planned": "Planejado",
        "active": "Ativo",
        "hybrid": "Híbrida",
        "internal": "Interna",
        "areas": "Áreas especializadas",
        "capabilities": "submódulos",
        "technologies": "Tecnologias conectadas",
        "not_found": "Solução tecnológica não encontrada.",
    },
    "en_us": {
        "back": "← Back to catalog",
        "status": "Status",
        "integration": "Integration",
        "planned": "Planned",
        "active": "Active",
        "hybrid": "Hybrid",
        "internal": "Internal",
        "areas": "Specialized areas",
        "capabilities": "submodules",
        "technologies": "Connected technologies",
        "not_found": "Technology solution not found.",
    },
    "es": {
        "back": "← Volver al catálogo",
        "status": "Estado",
        "integration": "Integración",
        "planned": "Planificado",
        "active": "Activo",
        "hybrid": "Híbrida",
        "areas": "Áreas especializadas",
        "capabilities": "submódulos",
        "technologies": "Tecnologías conectadas",
        "not_found": "Solución tecnológica no encontrada.",
    },
}


@dataclass(frozen=True, slots=True)
class TechnologyCapabilityDetail:
    """Dados visuais de uma capacidade tecnológica."""

    capability_id: str
    title: str
    description: str
    technologies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TechnologyAreaDetail:
    """Dados visuais de uma área tecnológica."""

    area_id: str
    title: str
    capabilities: tuple[TechnologyCapabilityDetail, ...]


@dataclass(frozen=True, slots=True)
class TechnologySolutionDetail:
    """Dados completos para a página setorial."""

    solution_id: str
    title: str
    description: str
    status: str
    integration_type: str
    areas: tuple[TechnologyAreaDetail, ...]

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
    capability: TechnologyCapability,
    language: str,
) -> TechnologyCapabilityDetail:
    """Converte uma capacidade para exibição."""

    technologies = tuple(
        platform_module_t(
            dependency,
            language,
        )
        for dependency in (capability.technology_dependencies)
    )

    return TechnologyCapabilityDetail(
        capability_id=capability.capability_id,
        title=capability.title,
        description=capability.description,
        technologies=technologies,
    )


def build_technology_solution_detail(
    solution: PlatformTechnologySolution,
    language: str = "pt",
) -> TechnologySolutionDetail:
    """Prepara os dados da solução empresarial."""

    return TechnologySolutionDetail(
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
            TechnologyAreaDetail(
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


TECHNOLOGY_RELATIONSHIP_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "title": "Relacionamentos tecnológicos",
        "caption": (
            "Conexões geradas automaticamente pelas dependências dos submódulos."
        ),
        "uses": "Este módulo utiliza",
        "used_by": "Este módulo é utilizado por",
        "no_uses": "Nenhuma dependência tecnológica registrada.",
        "no_used_by": "Nenhum outro módulo utiliza esta tecnologia.",
    },
    "en_us": {
        "title": "Technology relationships",
        "caption": ("Connections generated automatically from submodule dependencies."),
        "uses": "This module uses",
        "used_by": "This module is used by",
        "no_uses": "No technology dependency is registered.",
        "no_used_by": "No other module uses this technology.",
    },
    "es": {
        "title": "Relaciones tecnológicas",
        "caption": (
            "Conexiones generadas automáticamente desde "
            "las dependencias de los submódulos."
        ),
        "uses": "Este módulo utiliza",
        "used_by": "Este módulo es utilizado por",
        "no_uses": "No hay dependencias tecnológicas registradas.",
        "no_used_by": "Ningún otro módulo utiliza esta tecnología.",
    },
}


def technology_relationship_t(
    key: str,
    language: str = "pt",
) -> str:
    """Traduz os textos dos relacionamentos tecnológicos."""

    normalized_language = "en_us" if language == "en_gb" else language

    language_texts = TECHNOLOGY_RELATIONSHIP_TEXTS.get(
        normalized_language,
        TECHNOLOGY_RELATIONSHIP_TEXTS["pt"],
    )

    return language_texts.get(
        key,
        TECHNOLOGY_RELATIONSHIP_TEXTS["pt"][key],
    )


def _technology_relationship_label(
    module_id: str,
    language: str,
) -> str:
    """Cria o rótulo de um módulo conectado."""

    specialized_solution = platform_technology_solution(module_id)

    if specialized_solution is not None:
        return f"{specialized_solution.icon} **{specialized_solution.title}**"

    return f"**{platform_module_t(module_id, language)}**"


def render_technology_relationship_summary(
    solution_id: str,
    language: str = "pt",
) -> None:
    """Mostra os relacionamentos nos dois sentidos."""

    dependencies = technology_dependencies_for(solution_id)

    dependents = technology_dependents_for(solution_id)

    st.divider()

    st.markdown(
        "### "
        + technology_relationship_t(
            "title",
            language,
        )
    )

    st.caption(
        technology_relationship_t(
            "caption",
            language,
        )
    )

    uses_column, used_by_column = st.columns(2)

    uses_column.markdown(
        "#### 🔗 "
        + technology_relationship_t(
            "uses",
            language,
        )
        + f" ({len(dependencies)})"
    )

    if dependencies:
        for dependency_id in dependencies:
            uses_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependency_id,
                    language,
                )
            )
    else:
        uses_column.caption(
            technology_relationship_t(
                "no_uses",
                language,
            )
        )

    used_by_column.markdown(
        "#### 🔄 "
        + technology_relationship_t(
            "used_by",
            language,
        )
        + f" ({len(dependents)})"
    )

    if dependents:
        for dependent_id in dependents:
            used_by_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependent_id,
                    language,
                )
            )
    else:
        used_by_column.caption(
            technology_relationship_t(
                "no_used_by",
                language,
            )
        )

    st.divider()


def clear_selected_technology_solution() -> None:
    """Remove a solução selecionada da sessão."""

    st.session_state.pop(
        TECHNOLOGY_SOLUTION_STATE_KEY,
        None,
    )


def render_platform_technology_solution_details(
    solution_id: str,
    language: str = "pt",
) -> None:
    """Renderiza áreas e submódulos da solução."""

    solution = platform_technology_solution(solution_id)

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
        key="technology_solution_back_to_catalog",
    ):
        clear_selected_technology_solution()
        st.rerun()

    detail = build_technology_solution_detail(
        solution,
        language,
    )

    st.subheader(detail.title)
    st.write(detail.description)

    render_technology_relationship_summary(
        solution.solution_id,
        language,
    )

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

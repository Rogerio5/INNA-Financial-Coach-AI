"""Índice bidirecional dos relacionamentos tecnológicos da INNA."""

from __future__ import annotations

from dataclasses import dataclass

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
    PLATFORM_TECHNOLOGY_SOLUTIONS,
)


@dataclass(frozen=True, slots=True)
class TechnologyRelationship:
    """Linha da tabela ponte entre dois módulos tecnológicos."""

    source_solution_id: str
    source_area_id: str
    source_capability_id: str
    target_solution_id: str


def _build_technology_relationships() -> tuple[
    TechnologyRelationship,
    ...,
]:
    """Cria uma linha para cada dependência de cada capacidade."""

    return tuple(
        TechnologyRelationship(
            source_solution_id=solution.solution_id,
            source_area_id=area.area_id,
            source_capability_id=capability.capability_id,
            target_solution_id=target_solution_id,
        )
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        for area in solution.areas
        for capability in area.capabilities
        for target_solution_id in (capability.technology_dependencies)
    )


PLATFORM_TECHNOLOGY_RELATIONSHIPS = _build_technology_relationships()


def _build_relationship_index(
    *,
    use_source: bool,
) -> dict[str, tuple[TechnologyRelationship, ...]]:
    """Agrupa relacionamentos por origem ou destino."""

    buckets: dict[
        str,
        list[TechnologyRelationship],
    ] = {}

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        relationship_id = (
            relationship.source_solution_id
            if use_source
            else relationship.target_solution_id
        )

        buckets.setdefault(
            relationship_id,
            [],
        ).append(relationship)

    return {
        relationship_id: tuple(relationships)
        for relationship_id, relationships in buckets.items()
    }


TECHNOLOGY_RELATIONSHIPS_BY_SOURCE = _build_relationship_index(
    use_source=True,
)

TECHNOLOGY_RELATIONSHIPS_BY_TARGET = _build_relationship_index(
    use_source=False,
)


def technology_relationships_from(
    solution_id: str,
) -> tuple[TechnologyRelationship, ...]:
    """Retorna as linhas em que o módulo aparece como origem."""

    return TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.get(
        solution_id,
        (),
    )


def technology_relationships_to(
    solution_id: str,
) -> tuple[TechnologyRelationship, ...]:
    """Retorna as linhas em que o módulo aparece como destino."""

    return TECHNOLOGY_RELATIONSHIPS_BY_TARGET.get(
        solution_id,
        (),
    )


def technology_dependencies_for(
    solution_id: str,
) -> tuple[str, ...]:
    """Retorna os IDs dos módulos utilizados pela solução."""

    return tuple(
        dict.fromkeys(
            relationship.target_solution_id
            for relationship in technology_relationships_from(solution_id)
        )
    )


def technology_dependents_for(
    solution_id: str,
) -> tuple[str, ...]:
    """Retorna os IDs dos módulos que utilizam a solução."""

    return tuple(
        dict.fromkeys(
            relationship.source_solution_id
            for relationship in technology_relationships_to(solution_id)
        )
    )


def validate_platform_technology_relationship_registry() -> None:
    """Valida a tabela ponte e os índices bidirecionais."""

    technology_solution_ids = set(PLATFORM_TECHNOLOGY_SOLUTION_BY_ID)

    platform_module_ids = set(PLATFORM_MODULE_BY_ID)

    capability_dependencies = {
        (
            solution.solution_id,
            area.area_id,
            capability.capability_id,
        ): set(capability.technology_dependencies)
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        for area in solution.areas
        for capability in area.capabilities
    }

    seen_relationships: set[tuple[str, str, str, str]] = set()

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        relationship_key = (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
            relationship.target_solution_id,
        )

        if relationship_key in seen_relationships:
            raise ValueError(
                f"Relacionamento tecnológico duplicado: {relationship_key}"
            )

        seen_relationships.add(relationship_key)

        if relationship.source_solution_id not in technology_solution_ids:
            raise ValueError(
                f"Módulo de origem não registrado: {relationship.source_solution_id}"
            )

        if relationship.target_solution_id not in platform_module_ids:
            raise ValueError(
                f"Módulo de destino não registrado: {relationship.target_solution_id}"
            )

        capability_key = (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
        )

        expected_dependencies = capability_dependencies.get(capability_key)

        if expected_dependencies is None:
            raise ValueError(f"Capacidade de origem não encontrada: {capability_key}")

        if relationship.target_solution_id not in expected_dependencies:
            raise ValueError(
                f"Destino ausente nas dependências da capacidade: {relationship_key}"
            )

        if relationship not in TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.get(
            relationship.source_solution_id,
            (),
        ):
            raise ValueError("Relacionamento ausente no índice de origem.")

        if relationship not in TECHNOLOGY_RELATIONSHIPS_BY_TARGET.get(
            relationship.target_solution_id,
            (),
        ):
            raise ValueError("Relacionamento ausente no índice de destino.")

    if not PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        raise ValueError("A tabela ponte tecnológica está vazia.")


validate_platform_technology_relationship_registry()

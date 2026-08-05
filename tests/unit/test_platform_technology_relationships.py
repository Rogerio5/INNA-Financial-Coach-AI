from pathlib import Path

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_relationships import (
    PLATFORM_TECHNOLOGY_RELATIONSHIPS,
    TECHNOLOGY_RELATIONSHIPS_BY_SOURCE,
    TECHNOLOGY_RELATIONSHIPS_BY_TARGET,
    technology_dependencies_for,
    technology_dependents_for,
    validate_platform_technology_relationship_registry,
)
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
)

DETAILS_PATH = Path("src/dashboard_pages/platform_technology_solution_details.py")


def test_technology_relationship_registry_is_valid():
    validate_platform_technology_relationship_registry()

    assert PLATFORM_TECHNOLOGY_RELATIONSHIPS


def test_technology_relationship_rows_are_unique():
    relationship_keys = {
        (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
            relationship.target_solution_id,
        )
        for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS
    }

    assert len(relationship_keys) == len(PLATFORM_TECHNOLOGY_RELATIONSHIPS)


def test_relationships_reference_registered_solutions():
    technology_solution_ids = set(PLATFORM_TECHNOLOGY_SOLUTION_BY_ID)

    platform_module_ids = set(PLATFORM_MODULE_BY_ID)

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        assert relationship.source_solution_id in technology_solution_ids

        assert relationship.target_solution_id in platform_module_ids


def test_directional_indexes_cover_every_relationship():
    source_total = sum(
        len(relationships)
        for relationships in (TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.values())
    )

    target_total = sum(
        len(relationships)
        for relationships in (TECHNOLOGY_RELATIONSHIPS_BY_TARGET.values())
    )

    expected_total = len(PLATFORM_TECHNOLOGY_RELATIONSHIPS)

    assert source_total == expected_total
    assert target_total == expected_total


def test_bidirectional_lookup_returns_connected_modules():
    relationship = PLATFORM_TECHNOLOGY_RELATIONSHIPS[0]

    dependency_ids = set(technology_dependencies_for(relationship.source_solution_id))

    dependent_ids = set(technology_dependents_for(relationship.target_solution_id))

    assert relationship.target_solution_id in dependency_ids

    assert relationship.source_solution_id in dependent_ids


def test_cross_category_targets_are_supported():
    technology_solution_ids = set(PLATFORM_TECHNOLOGY_SOLUTION_BY_ID)

    cross_category_target_ids = {
        relationship.target_solution_id
        for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS
        if (relationship.target_solution_id not in technology_solution_ids)
    }

    assert cross_category_target_ids
    assert "document_ai" in cross_category_target_ids


def test_details_page_contains_relationship_summary():
    source = DETAILS_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "render_technology_relationship_summary",
        "technology_dependencies_for",
        "technology_dependents_for",
        "Este módulo utiliza",
        "Este módulo é utilizado por",
    )

    for token in required_tokens:
        assert token in source

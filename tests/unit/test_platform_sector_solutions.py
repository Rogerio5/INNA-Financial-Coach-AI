from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_sector_solutions import (
    AGRIBUSINESS_SOLUTION,
    DENTISTRY_SOLUTION,
    HOSPITALS_CLINICS_SOLUTION,
    PET_SHOPS_VETERINARY_SOLUTION,
    PLATFORM_SECTOR_SOLUTIONS,
    RETAIL_STORES_SOLUTION,
    SUPERMARKETS_WHOLESALE_SOLUTION,
    TRANSPORT_MOBILITY_SOLUTION,
    SectorSolutionStatus,
    platform_sector_solution,
    validate_platform_sector_solution_registry,
)


def test_sector_solution_registry_is_valid():
    validate_platform_sector_solution_registry()


def test_specialized_sector_solutions_are_registered():
    assert len(PLATFORM_SECTOR_SOLUTIONS) == 7

    assert {solution.solution_id for solution in PLATFORM_SECTOR_SOLUTIONS} == {
        "mobility_transport_connected_vehicles",
        "agribusiness_smart_agriculture_bioeconomy",
        "pet_shops_veterinary_services",
        "supermarkets_wholesale",
        "retail_stores",
        "dentistry",
        "hospitals_clinics",
    }


def test_transport_solution_is_complete():
    assert TRANSPORT_MOBILITY_SOLUTION.status is SectorSolutionStatus.PLANNED
    assert TRANSPORT_MOBILITY_SOLUTION.integration_type == "hybrid"
    assert len(TRANSPORT_MOBILITY_SOLUTION.areas) == 6
    assert TRANSPORT_MOBILITY_SOLUTION.capability_count == 20


def test_agribusiness_solution_is_complete():
    assert AGRIBUSINESS_SOLUTION.status is SectorSolutionStatus.PLANNED
    assert AGRIBUSINESS_SOLUTION.integration_type == "hybrid"
    assert len(AGRIBUSINESS_SOLUTION.areas) == 8
    assert AGRIBUSINESS_SOLUTION.capability_count == 21


def test_all_capabilities_have_existing_dependencies():
    for solution in PLATFORM_SECTOR_SOLUTIONS:
        assert solution.technology_dependencies

        for area in solution.areas:
            assert area.capabilities

            for capability in area.capabilities:
                assert capability.technology_dependencies


def test_sector_solution_lookup():
    assert (
        platform_sector_solution("mobility_transport_connected_vehicles")
        is TRANSPORT_MOBILITY_SOLUTION
    )

    assert (
        platform_sector_solution("agribusiness_smart_agriculture_bioeconomy")
        is AGRIBUSINESS_SOLUTION
    )

    assert platform_sector_solution("unknown_solution") is None


def test_solution_ids_match_platform_cards():
    for solution in PLATFORM_SECTOR_SOLUTIONS:
        assert solution.solution_id in PLATFORM_MODULE_BY_ID


def test_pet_shop_solution_is_complete():
    assert len(PET_SHOPS_VETERINARY_SOLUTION.areas) == 6
    assert PET_SHOPS_VETERINARY_SOLUTION.capability_count == 15


def test_supermarket_solution_is_complete():
    assert len(SUPERMARKETS_WHOLESALE_SOLUTION.areas) == 7
    assert SUPERMARKETS_WHOLESALE_SOLUTION.capability_count == 15


def test_retail_solution_is_complete():
    assert RETAIL_STORES_SOLUTION.solution_id == "retail_stores"
    assert RETAIL_STORES_SOLUTION.status is SectorSolutionStatus.PLANNED
    assert RETAIL_STORES_SOLUTION.integration_type == "hybrid"
    assert len(RETAIL_STORES_SOLUTION.areas) == 6
    assert RETAIL_STORES_SOLUTION.capability_count == 15


def test_dentistry_solution_is_complete():
    assert DENTISTRY_SOLUTION.solution_id == "dentistry"
    assert DENTISTRY_SOLUTION.status is SectorSolutionStatus.PLANNED
    assert DENTISTRY_SOLUTION.integration_type == "hybrid"
    assert len(DENTISTRY_SOLUTION.areas) == 6
    assert DENTISTRY_SOLUTION.capability_count == 15


def test_hospitals_clinics_solution_is_complete():
    assert HOSPITALS_CLINICS_SOLUTION.solution_id == "hospitals_clinics"
    assert HOSPITALS_CLINICS_SOLUTION.status is SectorSolutionStatus.PLANNED
    assert HOSPITALS_CLINICS_SOLUTION.integration_type == "hybrid"
    assert len(HOSPITALS_CLINICS_SOLUTION.areas) == 8
    assert HOSPITALS_CLINICS_SOLUTION.capability_count == 20

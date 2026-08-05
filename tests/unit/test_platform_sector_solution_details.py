from src.dashboard_pages.platform_sector_solution_details import (
    build_sector_solution_detail,
    detail_t,
)
from src.platform_sector_solutions import (
    AGRIBUSINESS_SOLUTION,
    TRANSPORT_MOBILITY_SOLUTION,
)


def test_builds_transport_solution_details():
    detail = build_sector_solution_detail(
        TRANSPORT_MOBILITY_SOLUTION,
        "pt",
    )

    assert detail.solution_id == "mobility_transport_connected_vehicles"
    assert len(detail.areas) == 6
    assert detail.capability_count == 20
    assert detail.status == "Planejado"
    assert detail.integration_type == "Híbrida"


def test_builds_agribusiness_solution_details():
    detail = build_sector_solution_detail(
        AGRIBUSINESS_SOLUTION,
        "pt",
    )

    assert detail.solution_id == "agribusiness_smart_agriculture_bioeconomy"
    assert len(detail.areas) == 8
    assert detail.capability_count == 21


def test_capabilities_include_translated_technologies():
    detail = build_sector_solution_detail(
        TRANSPORT_MOBILITY_SOLUTION,
        "pt",
    )

    first_capability = detail.areas[0].capabilities[0]

    assert first_capability.technologies
    assert all(technology.strip() for technology in (first_capability.technologies))


def test_detail_text_falls_back_to_portuguese():
    assert (
        detail_t(
            "back",
            "unknown",
        )
        == "← Voltar ao catálogo"
    )

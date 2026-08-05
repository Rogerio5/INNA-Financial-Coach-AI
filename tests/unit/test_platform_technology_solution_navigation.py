from pathlib import Path

from src.dashboard_pages.platform_modules_overview import (
    build_platform_module_cards,
)
from src.dashboard_pages.platform_technology_solution_details import (
    TECHNOLOGY_SOLUTION_STATE_KEY,
    render_platform_technology_solution_details,
)
from src.platform_modules import PlatformModuleCategory
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTIONS,
    platform_technology_solution,
)

OVERVIEW_PATH = Path("src/dashboard_pages/platform_modules_overview.py")


def test_technology_detail_renderer_is_available():
    assert TECHNOLOGY_SOLUTION_STATE_KEY
    assert callable(render_platform_technology_solution_details)


def test_all_technology_solutions_match_technology_cards():
    technology_cards = tuple(
        card
        for card in build_platform_module_cards()
        if (card.category is PlatformModuleCategory.TECHNOLOGY_CORE)
    )

    technology_card_ids = {card.module_id for card in technology_cards}

    registered_solution_ids = {
        solution.solution_id for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    }

    assert len(technology_cards) == 56
    assert technology_card_ids == registered_solution_ids

    for solution_id in registered_solution_ids:
        assert platform_technology_solution(solution_id) is not None


def test_overview_contains_technology_navigation_flow():
    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "TECHNOLOGY_SOLUTION_STATE_KEY",
        "render_platform_technology_solution_details",
        "platform_technology_solution",
        "open_technology_solution_",
        "selected_technology_solution_id",
    )

    for token in required_tokens:
        assert token in source


def test_technology_registry_totals_remain_complete():
    assert len(PLATFORM_TECHNOLOGY_SOLUTIONS) == 56

    assert sum(len(solution.areas) for solution in PLATFORM_TECHNOLOGY_SOLUTIONS) == 392

    assert (
        sum(solution.capability_count for solution in PLATFORM_TECHNOLOGY_SOLUTIONS)
        == 1176
    )

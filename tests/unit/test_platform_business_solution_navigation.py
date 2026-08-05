from pathlib import Path

from src.dashboard_pages.platform_business_solution_details import (
    BUSINESS_SOLUTION_STATE_KEY,
    render_platform_business_solution_details,
)
from src.dashboard_pages.platform_modules_overview import (
    build_platform_module_cards,
)
from src.platform_business_solutions import (
    PLATFORM_BUSINESS_SOLUTIONS,
    platform_business_solution,
)
from src.platform_modules import PlatformModuleCategory

OVERVIEW_PATH = Path("src/dashboard_pages/platform_modules_overview.py")


def test_business_detail_renderer_is_available():
    assert BUSINESS_SOLUTION_STATE_KEY
    assert callable(render_platform_business_solution_details)


def test_all_business_solutions_match_business_cards():
    business_cards = tuple(
        card
        for card in build_platform_module_cards()
        if (card.category is PlatformModuleCategory.BUSINESS_SOLUTIONS)
    )

    business_card_ids = {card.module_id for card in business_cards}

    registered_solution_ids = {
        solution.solution_id for solution in PLATFORM_BUSINESS_SOLUTIONS
    }

    assert len(business_cards) == 12
    assert business_card_ids == registered_solution_ids

    for solution_id in registered_solution_ids:
        assert platform_business_solution(solution_id) is not None


def test_overview_contains_business_navigation_flow():
    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "BUSINESS_SOLUTION_STATE_KEY",
        "render_platform_business_solution_details",
        "platform_business_solution",
        "open_business_solution_",
        "selected_business_solution_id",
    )

    for token in required_tokens:
        assert token in source


def test_business_registry_totals_remain_complete():
    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 12

    assert sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS) == 72

    assert (
        sum(solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS)
        == 215
    )

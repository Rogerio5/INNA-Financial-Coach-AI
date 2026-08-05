from src.dashboard_i18n import MENU_PAGE_IDS
from src.dashboard_navigation import (
    NAVIGATION_GROUP_BY_ID,
    NAVIGATION_GROUP_IDS,
    NAVIGATION_GROUPS,
    PAGE_TO_NAVIGATION_GROUP,
    default_page_for_navigation_group,
    navigation_group_for_page,
    pages_for_navigation_group,
    validate_navigation_registry,
)


def test_navigation_registry_is_valid():
    validate_navigation_registry()


def test_all_menu_pages_are_registered_once():
    registered_pages = [
        page_id for group in NAVIGATION_GROUPS for page_id in group.page_ids
    ]

    assert len(registered_pages) == len(set(registered_pages))

    assert set(registered_pages) == set(MENU_PAGE_IDS)


def test_navigation_has_expected_groups():
    assert NAVIGATION_GROUP_IDS == (
        "overview",
        "platform_modules",
        "financial_solutions",
        "enterprise_rag",
        "ai_operations",
        "tools_analytics",
        "administration",
    )


def test_group_indexes_are_consistent():
    assert set(NAVIGATION_GROUP_BY_ID) == set(NAVIGATION_GROUP_IDS)

    assert set(PAGE_TO_NAVIGATION_GROUP) == set(MENU_PAGE_IDS)


def test_navigation_resolves_existing_page():
    assert navigation_group_for_page("rag_evaluation_lab") == "enterprise_rag"

    assert navigation_group_for_page("ai_cost_center") == "ai_operations"


def test_unknown_page_falls_back_to_overview():
    assert navigation_group_for_page("unknown_page") == "overview"


def test_group_returns_its_pages():
    assert pages_for_navigation_group("financial_solutions") == (
        "diagnostics",
        "feedbacks",
        "user_memory",
    )


def test_group_returns_default_page():
    assert default_page_for_navigation_group("enterprise_rag") == "document_upload"


def test_unknown_group_uses_safe_defaults():
    assert pages_for_navigation_group("unknown_group") == NAVIGATION_GROUPS[0].page_ids

    assert default_page_for_navigation_group("unknown_group") == "overview"

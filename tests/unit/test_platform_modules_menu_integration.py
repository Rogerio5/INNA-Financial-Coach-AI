from pathlib import Path

from src.dashboard_i18n import (
    MENU_PAGE_IDS,
    MENU_TEXTS,
)
from src.dashboard_navigation import (
    NAVIGATION_GROUP_BY_ID,
    navigation_group_for_page,
)
from src.dashboard_navigation_i18n import (
    NAVIGATION_GROUP_TEXTS,
)


def test_platform_modules_catalog_is_registered():
    assert "platform_modules_catalog" in MENU_PAGE_IDS


def test_platform_modules_has_dedicated_group():
    group = NAVIGATION_GROUP_BY_ID["platform_modules"]

    assert group.default_page_id == ("platform_modules_catalog")

    assert group.page_ids == (
        "platform_modules_catalog",
        "relationship_graph",
    )


def test_catalog_resolves_to_platform_modules_group():
    assert navigation_group_for_page("platform_modules_catalog") == "platform_modules"


def test_catalog_has_all_language_labels():
    for language, texts in MENU_TEXTS.items():
        assert "platform_modules_catalog" in texts, language


def test_group_has_all_language_labels():
    for language, texts in NAVIGATION_GROUP_TEXTS.items():
        assert "platform_modules" in texts, language


def test_dashboard_has_catalog_route():
    source = Path("src/dashboard.py").read_text(
        encoding="utf-8",
    )

    assert 'elif menu == "platform_modules_catalog":' in source


def test_overview_does_not_render_catalog():
    source = Path("src/dashboard.py").read_text(
        encoding="utf-8",
    )

    start = source.index("def render_overview(")

    end = source.index(
        "MULTICHANNEL_DISPLAY_TEXTS",
        start,
    )

    overview_source = source[start:end]

    assert "render_platform_modules_overview" not in overview_source

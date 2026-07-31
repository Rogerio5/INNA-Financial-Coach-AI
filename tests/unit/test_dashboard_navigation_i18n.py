from src.dashboard_navigation import (
    NAVIGATION_GROUP_IDS,
)
from src.dashboard_navigation_i18n import (
    NAVIGATION_GROUP_TEXTS,
    navigation_group_t,
    validate_navigation_group_texts,
)

LANGUAGES = {
    "pt",
    "en_us",
    "en_gb",
    "es",
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
    "ch",
}


def test_navigation_group_translations_are_valid():
    validate_navigation_group_texts()


def test_all_selector_languages_are_supported():
    assert set(
        NAVIGATION_GROUP_TEXTS
    ) == LANGUAGES


def test_all_languages_have_all_groups():
    expected = set(
        NAVIGATION_GROUP_IDS
    )

    for texts in NAVIGATION_GROUP_TEXTS.values():
        assert set(texts) == expected


def test_portuguese_group_labels_are_expected():
    assert navigation_group_t(
        "overview",
        "pt",
    ) == "🏠 Visão Geral"

    assert navigation_group_t(
        "financial_solutions",
        "pt",
    ) == "💰 Soluções Financeiras"

    assert navigation_group_t(
        "ai_operations",
        "pt",
    ) == "⚙️ Operação e Governança de IA"


def test_english_variants_are_supported():
    assert navigation_group_t(
        "overview",
        "en_us",
    ) == "🏠 Overview"

    assert (
        NAVIGATION_GROUP_TEXTS["en_gb"]
        == NAVIGATION_GROUP_TEXTS["en_us"]
    )


def test_ch_follows_german_contract():
    assert (
        NAVIGATION_GROUP_TEXTS["ch"]
        == NAVIGATION_GROUP_TEXTS["de"]
    )


def test_unknown_language_falls_back_to_portuguese():
    assert navigation_group_t(
        "administration",
        "unknown",
    ) == "🔐 Administração"


def test_unknown_group_returns_group_id():
    assert navigation_group_t(
        "unknown_group",
        "pt",
    ) == "unknown_group"

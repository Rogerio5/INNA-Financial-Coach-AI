from src.dashboard_navigation_i18n import (
    NAVIGATION_NAVIGATION_TEXTS,
    navigation_ui_t,
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

EXPECTED_KEYS = {
    "platform_area",
    "area_pages",
}


def test_navigation_ui_supports_all_languages():
    assert set(NAVIGATION_NAVIGATION_TEXTS) == LANGUAGES


def test_navigation_ui_has_complete_contract():
    for language, texts in NAVIGATION_NAVIGATION_TEXTS.items():
        assert set(texts) == EXPECTED_KEYS, language


def test_navigation_ui_texts_are_non_empty():
    for language, texts in NAVIGATION_NAVIGATION_TEXTS.items():
        for key, value in texts.items():
            assert isinstance(value, str), (
                language,
                key,
            )
            assert value.strip(), (
                language,
                key,
            )


def test_portuguese_navigation_labels():
    assert (
        navigation_ui_t(
            "platform_area",
            "pt",
        )
        == "Área da plataforma"
    )

    assert (
        navigation_ui_t(
            "area_pages",
            "pt",
        )
        == "Páginas da área"
    )


def test_english_variants_follow_contract():
    assert NAVIGATION_NAVIGATION_TEXTS["en_gb"] == NAVIGATION_NAVIGATION_TEXTS["en_us"]


def test_ch_follows_german():
    assert NAVIGATION_NAVIGATION_TEXTS["ch"] == NAVIGATION_NAVIGATION_TEXTS["de"]


def test_unknown_language_falls_back_to_portuguese():
    assert (
        navigation_ui_t(
            "platform_area",
            "unknown",
        )
        == "Área da plataforma"
    )


def test_unknown_key_returns_key():
    assert (
        navigation_ui_t(
            "unknown_key",
            "pt",
        )
        == "unknown_key"
    )

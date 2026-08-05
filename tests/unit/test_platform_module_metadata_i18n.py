from src.platform_modules import (
    PlatformModuleCategory,
)
from src.platform_modules_i18n import (
    PLATFORM_INTEGRATION_TYPE_TEXTS,
    PLATFORM_MODULE_CATEGORY_TEXTS,
    platform_integration_type_t,
    platform_module_category_t,
    validate_platform_module_metadata_translations,
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


def test_metadata_translations_are_valid():
    validate_platform_module_metadata_translations()


def test_metadata_supports_all_languages():
    assert set(PLATFORM_MODULE_CATEGORY_TEXTS) == LANGUAGES

    assert set(PLATFORM_INTEGRATION_TYPE_TEXTS) == LANGUAGES


def test_category_contract_is_complete():
    expected = set(PlatformModuleCategory)

    for texts in PLATFORM_MODULE_CATEGORY_TEXTS.values():
        assert set(texts) == expected


def test_integration_contract_is_complete():
    expected = {
        "internal",
        "api",
        "hybrid",
        "webhook",
    }

    for texts in PLATFORM_INTEGRATION_TYPE_TEXTS.values():
        assert set(texts) == expected


def test_portuguese_metadata_labels():
    assert (
        platform_module_category_t(
            PlatformModuleCategory.BUSINESS_SOLUTIONS,
            "pt",
        )
        == "Soluções de negócio"
    )

    assert (
        platform_module_category_t(
            PlatformModuleCategory.TECHNOLOGY_CORE,
            "pt",
        )
        == "Núcleo tecnológico"
    )

    assert (
        platform_module_category_t(
            PlatformModuleCategory.SECTOR_SOLUTIONS,
            "pt",
        )
        == "Soluções por setor"
    )

    assert (
        platform_integration_type_t(
            "internal",
            "pt",
        )
        == "Interna"
    )

    assert (
        platform_integration_type_t(
            "hybrid",
            "pt",
        )
        == "Híbrida"
    )


def test_english_variants_follow_contract():
    assert (
        PLATFORM_MODULE_CATEGORY_TEXTS["en_gb"]
        == PLATFORM_MODULE_CATEGORY_TEXTS["en_us"]
    )

    assert (
        PLATFORM_INTEGRATION_TYPE_TEXTS["en_gb"]
        == PLATFORM_INTEGRATION_TYPE_TEXTS["en_us"]
    )


def test_ch_follows_german():
    assert PLATFORM_MODULE_CATEGORY_TEXTS["ch"] == PLATFORM_MODULE_CATEGORY_TEXTS["de"]

    assert (
        PLATFORM_INTEGRATION_TYPE_TEXTS["ch"] == PLATFORM_INTEGRATION_TYPE_TEXTS["de"]
    )


def test_unknown_values_use_safe_fallbacks():
    assert (
        platform_module_category_t(
            PlatformModuleCategory.PLATFORM_ADMINISTRATION,
            "unknown",
        )
        == "Administração da plataforma"
    )

    assert (
        platform_integration_type_t(
            "custom_connector",
            "pt",
        )
        == "custom_connector"
    )

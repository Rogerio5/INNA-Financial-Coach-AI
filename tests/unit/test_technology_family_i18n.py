from src.platform_modules import TechnologyFamily
from src.platform_modules_i18n import (
    TECHNOLOGY_FAMILY_TEXTS,
    technology_family_t,
)

BASE_LANGUAGES = {
    "pt",
    "en_us",
    "es",
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
}


def test_all_technology_families_have_translations():
    for language in BASE_LANGUAGES:
        assert set(TECHNOLOGY_FAMILY_TEXTS[language]) == set(TechnologyFamily)

        assert all(
            TECHNOLOGY_FAMILY_TEXTS[language][family].strip()
            for family in TechnologyFamily
        )


def test_technology_family_language_aliases():
    assert TECHNOLOGY_FAMILY_TEXTS["en_gb"] == TECHNOLOGY_FAMILY_TEXTS["en_us"]
    assert TECHNOLOGY_FAMILY_TEXTS["ch"] == TECHNOLOGY_FAMILY_TEXTS["de"]


def test_technology_family_portuguese_labels():
    assert (
        technology_family_t(
            TechnologyFamily.AI_KNOWLEDGE_AGENTS,
            "pt",
        )
        == "🧠 IA, conhecimento e agentes"
    )

    assert (
        technology_family_t(
            TechnologyFamily.DATA_INTEGRATION_OPERATIONS,
            "pt",
        )
        == "🗄️ Dados, integração e operações"
    )

    assert technology_family_t(
        TechnologyFamily.SECURITY_PRIVACY_TRUST,
        "pt",
    ) == ("🔐 Segurança, privacidade e confiança digital")

    assert technology_family_t(
        TechnologyFamily.AI_EVALUATION_TRUST,
        "pt",
    ) == ("⚖️ Avaliação, qualidade e confiança em IA")


def test_unknown_language_falls_back_to_portuguese():
    family = TechnologyFamily.GEOSPATIAL_OBSERVATION

    assert technology_family_t(
        family,
        "unknown_language",
    ) == technology_family_t(
        family,
        "pt",
    )


def test_all_translated_labels_include_an_icon():
    for language in TECHNOLOGY_FAMILY_TEXTS:
        for label in TECHNOLOGY_FAMILY_TEXTS[language].values():
            assert label
            assert not label[0].isalnum()

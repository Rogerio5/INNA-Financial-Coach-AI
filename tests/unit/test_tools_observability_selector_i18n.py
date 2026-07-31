from src.dashboard_pages.tools_observability_page import (
    TOOLS_DYNAMIC_TEXTS,
    TOOLS_OBSERVABILITY_TEXTS,
)

EXPECTED_LANGUAGES = {
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


def test_tools_observability_languages_are_complete():
    assert set(
        TOOLS_OBSERVABILITY_TEXTS
    ) == EXPECTED_LANGUAGES

    expected_keys = set(
        TOOLS_OBSERVABILITY_TEXTS[
            "en_us"
        ]
    )

    for language in EXPECTED_LANGUAGES:
        assert set(
            TOOLS_OBSERVABILITY_TEXTS[
                language
            ]
        ) == expected_keys


def test_tools_observability_titles_follow_selector():
    assert (
        TOOLS_OBSERVABILITY_TEXTS[
            "pt"
        ]["page_title"]
        == (
            "🛠️ Centro de Operações — "
            "Ferramentas da INNA"
        )
    )

    assert (
        TOOLS_OBSERVABILITY_TEXTS[
            "es"
        ]["page_title"]
        == (
            "🛠️ Centro de Operaciones — "
            "Herramientas INNA"
        )
    )

    assert (
        TOOLS_OBSERVABILITY_TEXTS[
            "ru"
        ]["page_title"]
        == (
            "🛠️ Операционный центр — "
            "Инструменты INNA"
        )
    )


def test_minimum_and_maximum_labels_are_readable():
    for language in (
        "fr",
        "de",
        "ch",
    ):
        texts = (
            TOOLS_OBSERVABILITY_TEXTS[
                language
            ]
        )

        assert "_" not in texts[
            "minimum_ms"
        ]
        assert "_" not in texts[
            "maximum_ms"
        ]


def test_dynamic_contract_is_complete():
    expected_keys = set(
        TOOLS_DYNAMIC_TEXTS["en_us"]
    )

    for language in EXPECTED_LANGUAGES:
        assert set(
            TOOLS_DYNAMIC_TEXTS[
                language
            ]
        ) == expected_keys


def test_ch_follows_german_tools_texts():
    assert (
        TOOLS_OBSERVABILITY_TEXTS[
            "ch"
        ]
        == TOOLS_OBSERVABILITY_TEXTS[
            "de"
        ]
    )

    assert (
        TOOLS_DYNAMIC_TEXTS["ch"]
        == TOOLS_DYNAMIC_TEXTS["de"]
    )


def test_proper_technology_names_are_preserved():
    for language in EXPECTED_LANGUAGES:
        assert (
            TOOLS_DYNAMIC_TEXTS[
                language
            ]["postgresql_neon"]
            == "PostgreSQL / Neon"
        )

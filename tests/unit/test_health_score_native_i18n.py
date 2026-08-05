from src.dashboard_pages.health_score_page import (
    HEALTH_HISTORY_DYNAMIC_TEXTS,
    HEALTH_HISTORY_TEXTS,
    HEALTH_PAGE_MAIN_TEXTS,
    HEALTH_PAGE_TEXTS,
    HEALTH_RUNTIME_MESSAGE_TEXTS,
    HEALTH_TABLE_TEXTS,
    HEALTH_VALUE_TEXTS,
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

CATALOGS = {
    "pagina": HEALTH_PAGE_TEXTS,
    "pagina_principal": HEALTH_PAGE_MAIN_TEXTS,
    "tabela": HEALTH_TABLE_TEXTS,
    "valores": HEALTH_VALUE_TEXTS,
    "historico": HEALTH_HISTORY_TEXTS,
    "historico_dinamico": HEALTH_HISTORY_DYNAMIC_TEXTS,
    "mensagens_runtime": HEALTH_RUNTIME_MESSAGE_TEXTS,
}


def test_health_score_catalogs_have_all_languages():
    for catalog in CATALOGS.values():
        assert set(catalog) == LANGUAGES


def test_health_score_catalog_contracts_are_complete():
    for catalog_name, catalog in CATALOGS.items():
        expected_keys = set(catalog["en_us"])

        for language in LANGUAGES:
            assert set(catalog[language]) == expected_keys, (
                catalog_name,
                language,
            )


def test_health_score_texts_are_non_empty():
    for catalog_name, catalog in CATALOGS.items():
        for language, texts in catalog.items():
            for key, value in texts.items():
                assert isinstance(
                    value,
                    str,
                ), (
                    catalog_name,
                    language,
                    key,
                )

                assert value.strip(), (
                    catalog_name,
                    language,
                    key,
                )


def test_health_score_titles_follow_selector():
    expected_titles = {
        "pt": "❤️ Central de Saúde da INNA",
        "en_us": "❤️ INNA Health Center",
        "en_gb": "❤️ INNA Health Centre",
        "es": "❤️ Centro de Salud de INNA",
        "fr": "❤️ Centre de santé d’INNA",
        "de": "❤️ INNA-Systemzustand",
        "it": "❤️ Centro salute INNA",
        "ro": "❤️ Centrul de sănătate INNA",
        "ua": "❤️ Центр стану системи INNA",
        "ru": "❤️ Центр состояния системы INNA",
        "sa": "❤️ مركز صحة نظام INNA",
        "ch": "❤️ INNA-Systemzustand",
    }

    for language, expected in expected_titles.items():
        assert HEALTH_PAGE_TEXTS[language]["title"] == expected


def test_health_score_final_visible_labels():
    assert HEALTH_HISTORY_TEXTS["pt"]["snapshots"] == "Registros históricos"

    assert HEALTH_HISTORY_TEXTS["fr"]["snapshots"] == "Instantanés historiques"

    assert HEALTH_HISTORY_TEXTS["de"]["snapshots"] == "Historische Momentaufnahmen"

    assert HEALTH_RUNTIME_MESSAGE_TEXTS["pt"]["cold_starts"] == "Inicializações a frio"


def test_ch_follows_german_in_health_catalogs():
    for catalog_name, catalog in CATALOGS.items():
        assert catalog["ch"] == catalog["de"], catalog_name


def test_health_score_captions_are_localized():
    assert HEALTH_PAGE_TEXTS["pt"]["caption"] != HEALTH_PAGE_TEXTS["en_us"]["caption"]

    assert HEALTH_PAGE_TEXTS["ru"]["caption"] != HEALTH_PAGE_TEXTS["en_us"]["caption"]

    assert HEALTH_PAGE_TEXTS["sa"]["caption"] != HEALTH_PAGE_TEXTS["en_us"]["caption"]

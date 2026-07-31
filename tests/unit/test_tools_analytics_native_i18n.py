from src.dashboard_pages.tools_analytics_page import (
    TOOLS_ANALYTICS_ANOMALY_TEXTS,
    TOOLS_ANALYTICS_DISTRIBUTION_TEXTS,
    TOOLS_ANALYTICS_OVERVIEW_TEXTS,
    TOOLS_ANALYTICS_PERIOD_TEXTS,
    TOOLS_ANALYTICS_RANKING_TEXTS,
    TOOLS_ANALYTICS_TEMPORAL_TEXTS,
    TOOLS_ANALYTICS_TEXTS,
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

NATIVE_LANGUAGES = {
    "ro",
    "ua",
    "ru",
    "sa",
}

CATALOGS = {
    "principal": TOOLS_ANALYTICS_TEXTS,
    "periodos": TOOLS_ANALYTICS_PERIOD_TEXTS,
    "anomalias": TOOLS_ANALYTICS_ANOMALY_TEXTS,
    "ranking": TOOLS_ANALYTICS_RANKING_TEXTS,
    "distribuicao": TOOLS_ANALYTICS_DISTRIBUTION_TEXTS,
    "temporal": TOOLS_ANALYTICS_TEMPORAL_TEXTS,
    "visao_geral": TOOLS_ANALYTICS_OVERVIEW_TEXTS,
}

ALLOWED_IDENTICAL = {
    "tool",
    "total",
    "error",
    "status",
    "date",
    "question",
    "message",
    "modified_z_score",
    "gemini",
    "rag",
    "router",
    "p95",
}


def test_tools_analytics_catalogs_have_all_languages():
    for catalog in CATALOGS.values():
        assert set(catalog) == LANGUAGES


def test_tools_analytics_catalog_contracts_are_complete():
    for catalog_name, catalog in CATALOGS.items():
        expected_keys = set(
            catalog["en_us"]
        )

        for language in LANGUAGES:
            assert set(
                catalog[language]
            ) == expected_keys, (
                catalog_name,
                language,
            )


def test_tools_analytics_texts_are_non_empty():
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


def test_native_catalogs_do_not_inherit_english():
    inherited = []

    for catalog_name, catalog in CATALOGS.items():
        english = catalog["en_us"]

        for language in NATIVE_LANGUAGES:
            for key, english_value in english.items():
                if key in ALLOWED_IDENTICAL:
                    continue

                current_value = catalog[
                    language
                ][key]

                if (
                    current_value.strip()
                    == english_value.strip()
                ):
                    inherited.append(
                        (
                            catalog_name,
                            language,
                            key,
                        )
                    )

    assert inherited == []


def test_ch_follows_german_in_all_catalogs():
    for catalog_name, catalog in CATALOGS.items():
        assert (
            catalog["ch"]
            == catalog["de"]
        ), catalog_name


def test_final_french_and_german_labels():
    assert (
        TOOLS_ANALYTICS_TEXTS[
            "fr"
        ]["distributions"]
        == "## Répartitions"
    )

    assert (
        TOOLS_ANALYTICS_DISTRIBUTION_TEXTS[
            "fr"
        ]["intention"]
        == "Intention détectée"
    )

    for catalog in (
        TOOLS_ANALYTICS_TEXTS,
        TOOLS_ANALYTICS_RANKING_TEXTS,
    ):
        assert (
            catalog["de"]["minimum_ms"]
            == "Minimalwert (ms)"
        )
        assert (
            catalog["de"]["maximum_ms"]
            == "Maximalwert (ms)"
        )


def test_native_anomaly_sections_are_translated():
    expected_titles = {
        "it": "## 🚨 Rilevamento delle anomalie",
        "ro": "## 🚨 Detectarea anomaliilor",
        "ua": "## 🚨 Виявлення аномалій",
        "ru": "## 🚨 Обнаружение аномалий",
        "sa": "## 🚨 اكتشاف الحالات الشاذة",
    }

    for language, expected in expected_titles.items():
        assert (
            TOOLS_ANALYTICS_ANOMALY_TEXTS[
                language
            ]["anomaly_detection"]
            == expected
        )


def test_native_sections_have_expected_titles():
    assert (
        TOOLS_ANALYTICS_PERIOD_TEXTS[
            "ru"
        ]["period_comparison"]
        == "## Сравнение периодов"
    )

    assert (
        TOOLS_ANALYTICS_RANKING_TEXTS[
            "ua"
        ]["ranking_performance"]
        == (
            "## Рейтинг і продуктивність "
            "інструментів"
        )
    )

    assert (
        TOOLS_ANALYTICS_DISTRIBUTION_TEXTS[
            "sa"
        ]["distributions"]
        == "## التوزيعات"
    )

    assert (
        TOOLS_ANALYTICS_TEMPORAL_TEXTS[
            "ro"
        ]["temporal_evolution"]
        == "## Evoluție temporală"
    )

    assert (
        TOOLS_ANALYTICS_OVERVIEW_TEXTS[
            "ru"
        ]["analytic_overview"]
        == "## Аналитический обзор"
    )

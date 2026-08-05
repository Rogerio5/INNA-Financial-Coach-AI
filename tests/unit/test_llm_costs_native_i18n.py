from src.dashboard_pages.llm_costs_page import (
    LLM_ALERT_CONTENT_TEXTS,
    LLM_ALERT_SECTION_DYNAMIC_TEXTS,
    LLM_ALERT_SECTION_TEXTS,
    LLM_ALERT_TEXTS,
    LLM_ALERT_UNKNOWN_ERROR_TEXTS,
    LLM_COST_ALERT_VISUAL_TEXTS,
    LLM_COST_PAGE_EXTRA_TEXTS,
    LLM_COST_PAGE_LOWER_TEXTS,
    LLM_COST_PAGE_TEXTS,
    LLM_DETAIL_TEXTS,
    LLM_NOTIFICATION_TEXTS,
    LLM_RESEND_EVENT_TEXTS,
    LLM_TABLE_TEXTS,
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

DICT_CATALOGS = {
    "tabela": LLM_TABLE_TEXTS,
    "detalhes": LLM_DETAIL_TEXTS,
    "alertas": LLM_ALERT_TEXTS,
    "notificacoes": LLM_NOTIFICATION_TEXTS,
    "eventos_resend": LLM_RESEND_EVENT_TEXTS,
    "secao_alertas": LLM_ALERT_SECTION_TEXTS,
    "secao_alertas_dinamica": (LLM_ALERT_SECTION_DYNAMIC_TEXTS),
    "visual_alertas": LLM_COST_ALERT_VISUAL_TEXTS,
    "conteudo_alertas": LLM_ALERT_CONTENT_TEXTS,
    "pagina": LLM_COST_PAGE_TEXTS,
    "pagina_extra": LLM_COST_PAGE_EXTRA_TEXTS,
    "pagina_inferior": LLM_COST_PAGE_LOWER_TEXTS,
}


def test_llm_cost_catalogs_have_all_languages():
    for catalog in DICT_CATALOGS.values():
        assert set(catalog) == LANGUAGES

    assert set(LLM_ALERT_UNKNOWN_ERROR_TEXTS) == LANGUAGES


def test_llm_cost_catalog_contracts_are_complete():
    for catalog_name, catalog in DICT_CATALOGS.items():
        expected_keys = set(catalog["en_us"])

        for language in LANGUAGES:
            assert set(catalog[language]) == expected_keys, (
                catalog_name,
                language,
            )


def _assert_non_empty_translation_value(
    value,
    *,
    path,
):
    if isinstance(value, str):
        assert value.strip(), path
        return

    if isinstance(value, dict):
        assert value, path

        for key, nested_value in value.items():
            _assert_non_empty_translation_value(
                nested_value,
                path=(
                    *path,
                    key,
                ),
            )

        return

    raise AssertionError(
        (
            *path,
            type(value).__name__,
        )
    )


def test_llm_cost_catalog_texts_are_non_empty():
    for catalog_name, catalog in DICT_CATALOGS.items():
        for language, texts in catalog.items():
            for key, value in texts.items():
                _assert_non_empty_translation_value(
                    value,
                    path=(
                        catalog_name,
                        language,
                        key,
                    ),
                )


def test_unknown_error_catalog_is_complete():
    for language in LANGUAGES:
        value = LLM_ALERT_UNKNOWN_ERROR_TEXTS[language]

        assert isinstance(value, str)
        assert value.strip()

    assert (
        LLM_ALERT_UNKNOWN_ERROR_TEXTS["en_gb"] == LLM_ALERT_UNKNOWN_ERROR_TEXTS["en_us"]
    )

    assert LLM_ALERT_UNKNOWN_ERROR_TEXTS["ch"] == LLM_ALERT_UNKNOWN_ERROR_TEXTS["de"]


def test_llm_cost_titles_follow_selector():
    expected_titles = {
        "pt": "💰 Central de Custos de IA",
        "en_us": "💰 AI Cost Center",
        "en_gb": "💰 AI Cost Centre",
        "es": "💰 Centro de Costos de IA",
        "fr": "💰 Centre des coûts IA",
        "de": "💰 KI-Kostenzentrale",
        "it": "💰 Centro costi IA",
        "ro": "💰 Centrul costurilor IA",
        "ua": "💰 Центр витрат ШІ",
        "ru": "💰 Центр затрат ИИ",
        "sa": ("💰 مركز تكاليف الذكاء الاصطناعي"),
        "ch": "💰 KI-Kostenzentrale",
    }

    for language, expected in expected_titles.items():
        assert LLM_COST_PAGE_TEXTS[language]["title"] == expected


def test_llm_cost_captions_are_localized():
    english_caption = LLM_COST_PAGE_TEXTS["en_us"]["caption"]

    for language in {
        "pt",
        "es",
        "fr",
        "de",
        "it",
        "ro",
        "ua",
        "ru",
        "sa",
    }:
        assert LLM_COST_PAGE_TEXTS[language]["caption"] != english_caption


def test_ch_follows_german_in_llm_cost_catalogs():
    for catalog_name, catalog in DICT_CATALOGS.items():
        assert catalog["ch"] == catalog["de"], catalog_name


def test_italian_database_label_is_native():
    assert LLM_ALERT_SECTION_TEXTS["it"]["database"] == "Banca dati"

    assert LLM_ALERT_SECTION_DYNAMIC_TEXTS["it"]["database"] == "Banca dati"


def test_protected_technical_terms_are_preserved():
    assert LLM_TABLE_TEXTS["pt"]["cost_usd"] == "Custo (USD)"

    assert LLM_DETAIL_TEXTS["pt"]["trace"] == "Trace"

    assert LLM_NOTIFICATION_TEXTS["pt"]["message_id"] == "Message ID"

    assert LLM_RESEND_EVENT_TEXTS["pt"]["svix_id"] == "Svix ID"

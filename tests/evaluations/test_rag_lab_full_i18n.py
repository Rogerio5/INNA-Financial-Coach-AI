from src.dashboard_pages.rag_evaluation_lab_page import (
    RAG_LAB_TEXTS,
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

def test_rag_lab_has_all_supported_languages():
    assert set(RAG_LAB_TEXTS) == EXPECTED_LANGUAGES

def test_every_language_has_complete_translation_contract():
    reference_keys = set(
        RAG_LAB_TEXTS["pt"]
    )

    for language in sorted(
        EXPECTED_LANGUAGES
    ):
        language_keys = set(
            RAG_LAB_TEXTS[language]
        )

        assert language_keys == reference_keys, (
            f"{language}: "
            f"missing={sorted(reference_keys - language_keys)}, "
            f"extra={sorted(language_keys - reference_keys)}"
        )

def test_every_translation_is_non_empty():
    for language, texts in (
        RAG_LAB_TEXTS.items()
    ):
        for key, value in texts.items():
            assert isinstance(value, str)
            assert value.strip(), (
                f"{language}.{key} está vazio"
            )

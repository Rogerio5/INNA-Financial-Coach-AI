from src.dashboard_pages.technical_labels_i18n import (
    TECHNICAL_LABELS,
    technical_label,
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

EXPECTED_KEYS = {
    "gemini",
    "fallback",
    "reranker",
    "embedding",
    "quality_gate",
    "tracing",
    "trace",
    "tokens",
    "token",
    "cache",
    "latency",
    "observability",
    "retrieval",
    "hybrid",
}


def test_all_languages_are_available():
    assert set(
        TECHNICAL_LABELS
    ) == EXPECTED_LANGUAGES


def test_all_languages_have_complete_contract():
    for language in EXPECTED_LANGUAGES:
        assert set(
            TECHNICAL_LABELS[
                language
            ]
        ) == EXPECTED_KEYS


def test_all_labels_are_non_empty():
    for texts in TECHNICAL_LABELS.values():
        for value in texts.values():
            assert isinstance(
                value,
                str,
            )
            assert value.strip()


def test_russian_labels_keep_technical_terms():
    assert technical_label(
        "ru",
        "fallback",
    ) == "Резервный режим (Fallback)"

    assert technical_label(
        "ru",
        "gemini",
    ) == "Модель Gemini"


def test_ch_follows_german_contract():
    assert (
        TECHNICAL_LABELS["ch"]
        == TECHNICAL_LABELS["de"]
    )


def test_unknown_language_uses_portuguese():
    assert technical_label(
        "unknown",
        "latency",
    ) == "Latência"


def test_unknown_key_is_preserved():
    assert technical_label(
        "pt",
        "unknown_term",
    ) == "unknown_term"

from src.evaluation.dashboard import (
    LLMOPS_TEXTS,
    llmops_t,
)

NON_ENGLISH_LANGUAGES = (
    "pt",
    "es",
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
    "ch",
)

ALLOWED_IDENTICAL = {
    "rag_triad_title",
    "branches",
    "local",
    "region",
    "service",
    "date",
}


def test_llmops_has_no_unexpected_english_inheritance():
    english = LLMOPS_TEXTS["en_us"]

    inherited: list[tuple[str, str, str]] = []

    for language in NON_ENGLISH_LANGUAGES:
        texts = LLMOPS_TEXTS[language]

        for key, english_value in english.items():
            if key in ALLOWED_IDENTICAL:
                continue

            current_value = texts.get(key)

            if (
                isinstance(english_value, str)
                and isinstance(current_value, str)
                and current_value.strip() == english_value.strip()
            ):
                inherited.append(
                    (
                        language,
                        key,
                        current_value,
                    )
                )

    assert inherited == []


def test_quality_gate_dictionary_uses_catalog():
    assert LLMOPS_TEXTS["pt"]["quality_gate"] == "Portão de qualidade (Quality Gate)"

    assert LLMOPS_TEXTS["ru"]["quality_gate"] == "Контроль качества (Quality Gate)"

    assert LLMOPS_TEXTS["de"]["quality_gate"] == "Qualitätsprüfung (Quality Gate)"


def test_ch_continues_following_german():
    assert LLMOPS_TEXTS["ch"]["quality_gate"] == LLMOPS_TEXTS["de"]["quality_gate"]


def test_llmops_translation_function_uses_catalog(
    monkeypatch,
):
    monkeypatch.setattr(
        "src.evaluation.dashboard.llmops_lang",
        lambda: "es",
    )

    assert llmops_t("quality_gate") == ("Puerta de calidad (Quality Gate)")

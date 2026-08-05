from src.dashboard_pages.timeline_viewer_page import (
    TIMELINE_DYNAMIC_TEXTS,
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


def test_timeline_dynamic_languages_are_complete():
    assert set(TIMELINE_DYNAMIC_TEXTS) == LANGUAGES

    expected_keys = set(TIMELINE_DYNAMIC_TEXTS["en_us"])

    expected_steps = set(TIMELINE_DYNAMIC_TEXTS["en_us"]["steps"])

    for language in LANGUAGES:
        texts = TIMELINE_DYNAMIC_TEXTS[language]

        assert set(texts) == expected_keys
        assert set(texts["steps"]) == expected_steps


def test_timeline_dynamic_texts_are_non_empty():
    for texts in TIMELINE_DYNAMIC_TEXTS.values():
        for key, value in texts.items():
            if key == "steps":
                for step_value in value.values():
                    assert isinstance(
                        step_value,
                        str,
                    )
                    assert step_value.strip()

                continue

            assert isinstance(
                value,
                str,
            )
            assert value.strip()


def test_non_english_dynamic_texts_do_not_inherit_english():
    english = TIMELINE_DYNAMIC_TEXTS["en_us"]

    inherited = []

    for language in LANGUAGES - {
        "en_us",
        "en_gb",
    }:
        texts = TIMELINE_DYNAMIC_TEXTS[language]

        for key, english_value in english.items():
            if key == "steps":
                continue

            if texts[key].strip() == english_value.strip():
                inherited.append(
                    (
                        language,
                        key,
                    )
                )

        for step_key, english_value in english["steps"].items():
            if texts["steps"][step_key].strip() == english_value.strip():
                inherited.append(
                    (
                        language,
                        f"steps.{step_key}",
                    )
                )

    assert inherited == []


def test_ch_dynamic_texts_follow_german():
    assert TIMELINE_DYNAMIC_TEXTS["ch"] == TIMELINE_DYNAMIC_TEXTS["de"]

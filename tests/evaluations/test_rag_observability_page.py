from pathlib import Path

import pandas as pd

from src.dashboard_pages.rag_observability_i18n import (
    RAG_OBSERVABILITY_TEXTS,
)
from src.dashboard_pages.rag_observability_page import (
    render_rag_observability_page,
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


def test_has_all_supported_languages():
    assert set(
        RAG_OBSERVABILITY_TEXTS
    ) == EXPECTED_LANGUAGES


def test_all_languages_have_complete_contract():
    reference_keys = set(
        RAG_OBSERVABILITY_TEXTS["pt"]
    )

    for language in EXPECTED_LANGUAGES:
        assert set(
            RAG_OBSERVABILITY_TEXTS[
                language
            ]
        ) == reference_keys


def test_every_translation_is_non_empty():
    for language, texts in (
        RAG_OBSERVABILITY_TEXTS.items()
    ):
        for key, value in texts.items():
            assert isinstance(
                value,
                str,
            )

            assert value.strip(), (
                f"{language}.{key}"
            )


def test_renderer_is_available():
    assert callable(
        render_rag_observability_page
    )


def test_empty_dataframe_is_supported():
    frame = pd.DataFrame()

    assert frame.empty is True


def test_page_has_no_simulated_data_markers():
    path = Path(
        "src/dashboard_pages/"
        "rag_observability_page.py"
    )

    source = path.read_text(
        encoding="utf-8",
    ).lower()

    forbidden_markers = (
        "mock data",
        "fake data",
        "simulated data",
        "dados fictícios",
        "dados simulados",
    )

    for marker in forbidden_markers:
        assert marker not in source

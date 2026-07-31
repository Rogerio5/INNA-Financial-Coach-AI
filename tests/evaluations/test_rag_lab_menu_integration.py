from pathlib import Path

import pytest

from src import dashboard_i18n
from src.dashboard_pages.rag_evaluation_lab_page import (
    render_rag_evaluation_lab_page,
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


def test_rag_lab_is_registered_between_llmops_and_costs():
    page_ids = dashboard_i18n.MENU_PAGE_IDS

    rag_lab_index = page_ids.index(
        "rag_evaluation_lab"
    )

    assert page_ids[
        rag_lab_index - 1
    ] == "llmops_observability"

    assert page_ids[
        rag_lab_index + 1
    ] == "ai_cost_center"


@pytest.mark.parametrize(
    "language",
    sorted(EXPECTED_LANGUAGES),
)
def test_rag_lab_has_menu_translation(
    language: str,
):
    language_texts = (
        dashboard_i18n.MENU_TEXTS[
            language
        ]
    )

    assert (
        language_texts[
            "rag_evaluation_lab"
        ]
    )

    translated = dashboard_i18n.menu_t(
        "rag_evaluation_lab",
        language=language,
    )

    assert translated == (
        language_texts[
            "rag_evaluation_lab"
        ]
    )

    assert "RAG" in translated


@pytest.mark.parametrize(
    "language",
    sorted(EXPECTED_LANGUAGES),
)
def test_translated_rag_lab_label_is_normalized(
    language: str,
):
    label = dashboard_i18n.menu_t(
        "rag_evaluation_lab",
        language=language,
    )

    assert (
        dashboard_i18n
        .normalize_menu_page_id(label)
        == "rag_evaluation_lab"
    )


def test_internal_rag_lab_id_is_normalized():
    assert (
        dashboard_i18n
        .normalize_menu_page_id(
            "rag_evaluation_lab"
        )
        == "rag_evaluation_lab"
    )


def test_rag_lab_page_renderer_is_importable():
    assert callable(
        render_rag_evaluation_lab_page
    )


def test_dashboard_contains_rag_lab_route():
    source = Path(
        "src/dashboard.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        'elif menu == "rag_evaluation_lab":'
        in source
    )

    assert (
        "render_rag_evaluation_lab_page()"
        in source
    )

    assert (
        source.index(
            'elif menu == "rag_evaluation_lab":'
        )
        < source.index(
            'elif menu == "ai_cost_center":'
        )
    )

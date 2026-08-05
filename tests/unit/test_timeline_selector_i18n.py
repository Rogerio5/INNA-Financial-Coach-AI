from src.dashboard_pages.timeline_viewer_page import (
    TIMELINE_TEXTS,
)


def test_timeline_titles_follow_selector():
    expected = {
        "pt": ("🧭 Linha do tempo das execuções — INNA"),
        "en_us": ("🧭 Execution timeline — INNA"),
        "en_gb": ("🧭 Execution timeline — INNA"),
        "es": ("🧭 Línea de tiempo de las ejecuciones — INNA"),
        "fr": ("🧭 Chronologie des exécutions — INNA"),
        "de": ("🧭 Zeitachse der Ausführungen — INNA"),
        "it": ("🧭 Cronologia delle esecuzioni — INNA"),
        "ro": ("🧭 Cronologia execuțiilor — INNA"),
        "ua": ("🧭 Хронологія виконань — INNA"),
        "ru": ("🧭 Хронология выполнений — INNA"),
        "sa": ("🧭 المخطط الزمني لعمليات التنفيذ — INNA"),
        "ch": ("🧭 Zeitachse der Ausführungen — INNA"),
    }

    for language, title in expected.items():
        assert TIMELINE_TEXTS[language]["page_title"] == title


def test_timeline_languages_keep_complete_contract():
    expected_keys = set(TIMELINE_TEXTS["en_us"])

    for language, texts in TIMELINE_TEXTS.items():
        assert set(texts) == expected_keys, language


def test_ch_follows_german_timeline():
    assert TIMELINE_TEXTS["ch"] == TIMELINE_TEXTS["de"]


def test_native_visible_labels_are_applied():
    assert TIMELINE_TEXTS["pt"]["status"] == "Situação"
    assert TIMELINE_TEXTS["pt"]["linear"] == "Escala linear"
    assert TIMELINE_TEXTS["fr"]["question"] == "### Question posée"
    assert TIMELINE_TEXTS["de"]["start"] == "Beginn"

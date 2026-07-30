from __future__ import annotations

import pandas as pd
import pytest

from src.dashboard_i18n import (
    SUPPORTED_LANGUAGES,
    VALUE_TEXTS,
    build_translator,
    ensure_language_parity,
    get_data_language_filter,
    get_interface_language,
    localize_dataframe,
    normalize_language,
    translate,
    translate_risk,
    translate_status,
    translate_useful,
    value_t,
)


def test_supported_languages_are_complete() -> None:
    assert SUPPORTED_LANGUAGES == (
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
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("pt-BR", "pt"),
        ("en-US", "en_us"),
        ("en-GB", "en_gb"),
        ("uk-UA", "ua"),
        ("ar-SA", "sa"),
        ("de-CH", "ch"),
        ("invalid-language", "pt"),
        (None, "pt"),
    ],
)
def test_normalize_language(
    raw: object,
    expected: str,
) -> None:
    assert normalize_language(raw) == expected


def test_interface_language_is_independent_from_data_filter() -> None:
    state = {
        "dashboard_interface_lang": "ru",
        "dashboard_filter_language": "pt",
    }

    assert get_interface_language(state) == "ru"
    assert get_data_language_filter(state) == "pt"


def test_all_data_filter_returns_none() -> None:
    state = {
        "dashboard_filter_language": "Todos",
    }

    assert get_data_language_filter(state) is None


def test_translate_uses_selected_language() -> None:
    texts = {
        "pt": {
            "title": "Título",
        },
        "ru": {
            "title": "Заголовок",
        },
    }

    assert (
        translate(
            texts,
            "title",
            language="ru",
        )
        == "Заголовок"
    )


def test_translate_formats_values() -> None:
    texts = {
        "pt": {
            "events": "{count} eventos",
        },
        "en_us": {
            "events": "{count} events",
        },
    }

    assert (
        translate(
            texts,
            "events",
            language="en_us",
            count=12,
        )
        == "12 events"
    )


def test_translate_strict_rejects_missing_key() -> None:
    with pytest.raises(KeyError):
        translate(
            {
                "pt": {},
            },
            "missing",
            strict=True,
        )


def test_build_translator() -> None:
    page_t = build_translator(
        {
            "pt": {
                "title": "Página",
            },
            "it": {
                "title": "Pagina",
            },
        }
    )

    assert (
        page_t(
            "title",
            language="it",
        )
        == "Pagina"
    )


@pytest.mark.parametrize(
    ("language", "truthy", "falsy"),
    [
        ("pt", "Útil", "Não útil"),
        ("en_us", "Useful", "Not useful"),
        ("ru", "Полезный", "Неполезный"),
        ("sa", "مفيد", "غير مفيد"),
        ("de", "Nützlich", "Nicht nützlich"),
    ],
)
def test_translate_useful(
    language: str,
    truthy: str,
    falsy: str,
) -> None:
    assert (
        translate_useful(
            True,
            language=language,
        )
        == truthy
    )

    assert (
        translate_useful(
            "false",
            language=language,
        )
        == falsy
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("pt", "Médio"),
        ("en_us", "Medium"),
        ("ru", "Средний"),
        ("sa", "متوسط"),
        ("it", "Medio"),
    ],
)
def test_translate_risk(
    language: str,
    expected: str,
) -> None:
    assert (
        translate_risk(
            "Médio",
            language=language,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("pt", "Sucesso"),
        ("en_us", "Success"),
        ("ru", "Успех"),
        ("sa", "نجاح"),
    ],
)
def test_translate_status(
    language: str,
    expected: str,
) -> None:
    assert (
        translate_status(
            "success",
            language=language,
        )
        == expected
    )


def test_localize_dataframe_does_not_change_original() -> None:
    original = pd.DataFrame(
        {
            "util": [
                True,
                False,
            ],
            "quantidade": [
                4,
                1,
            ],
        }
    )

    column_texts = {
        "pt": {
            "evaluation": "Avaliação",
            "quantity": "Quantidade",
        },
        "ru": {
            "evaluation": "Оценка",
            "quantity": "Количество",
        },
    }

    localized = localize_dataframe(
        original,
        column_keys={
            "util": "evaluation",
            "quantidade": "quantity",
        },
        column_texts=column_texts,
        value_transforms={
            "util": lambda value: (
                translate_useful(
                    value,
                    language="ru",
                )
            ),
        },
        language="ru",
    )

    assert list(original.columns) == [
        "util",
        "quantidade",
    ]

    assert original["util"].tolist() == [
        True,
        False,
    ]

    assert list(localized.columns) == [
        "Оценка",
        "Количество",
    ]

    assert localized["Оценка"].tolist() == [
        "Полезный",
        "Неполезный",
    ]


def test_value_texts_have_language_parity() -> None:
    assert (
        ensure_language_parity(
            VALUE_TEXTS
        )
        == {}
    )


def test_value_t_uses_regional_aliases() -> None:
    assert (
        value_t(
            "success",
            language="en_gb",
        )
        == "Success"
    )

    assert (
        value_t(
            "configured",
            language="ch",
        )
        == "Konfiguriert"
    )

def test_menu_page_ids_are_stable() -> None:
    from src.dashboard_i18n import (
        MENU_PAGE_IDS,
    )

    assert MENU_PAGE_IDS == (
        "overview",
        "multichannel_events",
        "international_view",
        "diagnostics",
        "feedbacks",
        "evolution",
        "executive_reading",
        "agent_evaluation",
        "rag_observability",
        "tools_observability",
        "timeline_viewer",
        "tools_analytics",
        "health_center",
        "llmops_observability",
        "ai_cost_center",
        "document_upload",
        "user_memory",
        "export",
    )


def test_menu_texts_have_language_parity() -> None:
    from src.dashboard_i18n import (
        MENU_TEXTS,
        ensure_language_parity,
    )

    assert (
        ensure_language_parity(
            MENU_TEXTS
        )
        == {}
    )


@pytest.mark.parametrize(
    ("language", "page_id", "expected"),
    [
        (
            "pt",
            "user_memory",
            "🧠 Memória do Usuário",
        ),
        (
            "en_us",
            "document_upload",
            "📄 Document Upload",
        ),
        (
            "it",
            "tools_observability",
            "🛠️ Osservabilità degli strumenti",
        ),
        (
            "ru",
            "timeline_viewer",
            "🧭 Просмотр временной шкалы",
        ),
        (
            "sa",
            "ai_cost_center",
            "💰 مركز تكاليف الذكاء الاصطناعي",
        ),
    ],
)
def test_menu_t(
    language: str,
    page_id: str,
    expected: str,
) -> None:
    from src.dashboard_i18n import (
        menu_t,
    )

    assert (
        menu_t(
            page_id,
            language=language,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("legacy_value", "expected"),
    [
        (
            "📌 Visão Geral",
            "overview",
        ),
        (
            "🛠️ Observabilidade Tools",
            "tools_observability",
        ),
        (
            "🧭 Timeline Viewer",
            "timeline_viewer",
        ),
        (
            "📄 Upload Documentos",
            "document_upload",
        ),
        (
            "🧠 Memória Usuário",
            "user_memory",
        ),
        (
            "🧠 Memoria utente",
            "user_memory",
        ),
        (
            "🧠 Память пользователя",
            "user_memory",
        ),
        (
            "🧠 ذاكرة المستخدم",
            "user_memory",
        ),
        (
            "invalid-page",
            "overview",
        ),
    ],
)
def test_normalize_menu_page_id(
    legacy_value: str,
    expected: str,
) -> None:
    from src.dashboard_i18n import (
        normalize_menu_page_id,
    )

    assert (
        normalize_menu_page_id(
            legacy_value
        )
        == expected
    )

def test_multichannel_texts_have_language_parity() -> None:
    from src.dashboard_i18n import (
        MULTICHANNEL_UI_TEXTS,
        ensure_language_parity,
    )

    assert (
        ensure_language_parity(
            MULTICHANNEL_UI_TEXTS
        )
        == {}
    )


def test_channel_texts_have_language_parity() -> None:
    from src.dashboard_i18n import (
        CHANNEL_TEXTS,
        ensure_language_parity,
    )

    assert (
        ensure_language_parity(
            CHANNEL_TEXTS
        )
        == {}
    )


@pytest.mark.parametrize(
    ("language", "raw_channel", "expected"),
    [
        (
            "pt",
            "web-app",
            "Aplicação web",
        ),
        (
            "en_us",
            "pdf-download",
            "PDF download",
        ),
        (
            "es",
            "dashboard",
            "Panel",
        ),
        (
            "fr",
            "web-app",
            "Application web",
        ),
        (
            "de",
            "email",
            "E-Mail",
        ),
        (
            "it",
            "pdf-download",
            "Download PDF",
        ),
        (
            "ro",
            "dashboard",
            "Panou",
        ),
        (
            "ua",
            "web-app",
            "Вебзастосунок",
        ),
        (
            "ru",
            "pdf-download",
            "Загрузка PDF",
        ),
        (
            "sa",
            "dashboard",
            "لوحة التحكم",
        ),
        (
            "en_gb",
            "email",
            "Email",
        ),
        (
            "ch",
            "web-app",
            "Webanwendung",
        ),
    ],
)
def test_translate_channel_in_all_languages(
    language: str,
    raw_channel: str,
    expected: str,
) -> None:
    from src.dashboard_i18n import (
        translate_channel,
    )

    assert (
        translate_channel(
            raw_channel,
            language=language,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("language", "stage_key", "expected"),
    [
        (
            "pt",
            "diagnostic_generated",
            "Diagnóstico gerado",
        ),
        (
            "en_us",
            "pdf_downloaded",
            "PDF downloaded",
        ),
        (
            "es",
            "email_sent",
            "Correo enviado",
        ),
        (
            "fr",
            "feedback_received",
            "Retour reçu",
        ),
        (
            "de",
            "diagnostic_generated",
            "Diagnose erstellt",
        ),
        (
            "it",
            "pdf_downloaded",
            "PDF scaricato",
        ),
        (
            "ro",
            "email_sent",
            "E-mail trimis",
        ),
        (
            "ua",
            "feedback_received",
            "Відгук отримано",
        ),
        (
            "ru",
            "diagnostic_generated",
            "Диагностика создана",
        ),
        (
            "sa",
            "pdf_downloaded",
            "تم تنزيل PDF",
        ),
    ],
)
def test_multichannel_funnel_stages(
    language: str,
    stage_key: str,
    expected: str,
) -> None:
    from src.dashboard_i18n import (
        multichannel_t,
    )

    assert (
        multichannel_t(
            stage_key,
            language=language,
        )
        == expected
    )


def test_localize_multichannel_dataframe() -> None:
    import pandas as pd

    from src.dashboard_i18n import (
        localize_multichannel_dataframe,
    )

    original = pd.DataFrame(
        {
            "canal": [
                "web-app",
                "pdf-download",
            ],
            "status": [
                "success",
                "failure",
            ],
            "util": [
                True,
                False,
            ],
            "quantidade": [
                4,
                1,
            ],
        }
    )

    localized = (
        localize_multichannel_dataframe(
            original,
            language="ru",
        )
    )

    assert list(original.columns) == [
        "canal",
        "status",
        "util",
        "quantidade",
    ]

    assert original["util"].tolist() == [
        True,
        False,
    ]

    assert localized[
        "Канал"
    ].tolist() == [
        "Веб-приложение",
        "Загрузка PDF",
    ]

    assert localized[
        "Статус"
    ].tolist() == [
        "Успех",
        "Ошибка",
    ]

    assert localized[
        "Оценка"
    ].tolist() == [
        "Полезный",
        "Неполезный",
    ]

    assert localized[
        "Количество"
    ].tolist() == [
        4,
        1,
    ]


@pytest.mark.parametrize(
    ("language", "truthy", "falsy"),
    [
        (
            "pt",
            "Útil",
            "Não útil",
        ),
        (
            "en_us",
            "Useful",
            "Not useful",
        ),
        (
            "en_gb",
            "Useful",
            "Not useful",
        ),
        (
            "es",
            "Útil",
            "No útil",
        ),
        (
            "fr",
            "Utile",
            "Non utile",
        ),
        (
            "de",
            "Nützlich",
            "Nicht nützlich",
        ),
        (
            "it",
            "Utile",
            "Non utile",
        ),
        (
            "ro",
            "Util",
            "Neutil",
        ),
        (
            "ua",
            "Корисний",
            "Некорисний",
        ),
        (
            "ru",
            "Полезный",
            "Неполезный",
        ),
        (
            "sa",
            "مفيد",
            "غير مفيد",
        ),
        (
            "ch",
            "Nützlich",
            "Nicht nützlich",
        ),
    ],
)
def test_true_false_are_never_exposed_visually(
    language: str,
    truthy: str,
    falsy: str,
) -> None:
    from src.dashboard_i18n import (
        translate_useful,
    )

    translated_true = translate_useful(
        "true",
        language=language,
    )

    translated_false = translate_useful(
        "false",
        language=language,
    )

    assert translated_true == truthy
    assert translated_false == falsy

    assert translated_true.casefold() != "true"
    assert translated_false.casefold() != "false"

def test_audit_page_language_pack_detects_english_fallback() -> None:
    from src.dashboard_i18n import (
        audit_page_language_pack,
    )

    texts = {
        "pt": {
            "title": "Título",
            "button": "Salvar",
        },
        "en_us": {
            "title": "Title",
            "button": "Save",
        },
        "ru": {
            "title": "Title",
            "button": "Save",
        },
    }

    report = audit_page_language_pack(
        texts
    )

    assert (
        report["ru"][
            "same_as_english"
        ]
        is True
    )


def test_audit_page_language_pack_detects_missing_keys() -> None:
    from src.dashboard_i18n import (
        audit_page_language_pack,
    )

    texts = {
        "pt": {
            "title": "Título",
            "button": "Salvar",
        },
        "en_us": {
            "title": "Title",
            "button": "Save",
        },
        "it": {
            "title": "Titolo",
        },
    }

    report = audit_page_language_pack(
        texts
    )

    assert report["it"]["missing"] == {
        "button",
    }


def test_merge_language_texts_preserves_existing_values() -> None:
    from src.dashboard_i18n import (
        merge_language_texts,
    )

    texts = {
        "pt": {
            "title": "Título",
        },
    }

    merge_language_texts(
        texts,
        {
            "pt": {
                "button": "Salvar",
            },
            "ru": {
                "title": "Заголовок",
                "button": "Сохранить",
            },
        },
    )

    assert texts["pt"] == {
        "title": "Título",
        "button": "Salvar",
    }

    assert texts["ru"] == {
        "title": "Заголовок",
        "button": "Сохранить",
    }


def test_page_translate_uses_interface_language() -> None:
    from src.dashboard_i18n import (
        page_translate,
    )

    texts = {
        "pt": {
            "message": (
                "Memória de {user_id} carregada."
            ),
        },
        "ru": {
            "message": (
                "Память пользователя "
                "{user_id} загружена."
            ),
        },
    }

    result = page_translate(
        texts,
        "message",
        language="ru",
        user_id="demo_user",
    )

    assert result == (
        "Память пользователя "
        "demo_user загружена."
    )

def test_block_4b_native_page_translations() -> None:
    import src.dashboard as dashboard
    from src.dashboard_i18n import (
        audit_page_language_pack,
    )

    upload_report = audit_page_language_pack(
        dashboard.UPLOAD_RAG_TEXTS
    )

    memory_report = audit_page_language_pack(
        dashboard.MEMORY_PAGE_TEXTS
    )

    for language in (
        "ro",
        "ua",
        "ru",
        "sa",
    ):
        assert (
            upload_report.get(
                language,
                {},
            ).get(
                "same_as_english",
                False,
            )
            is False
        )

    for language in (
        "it",
        "ro",
        "ua",
        "ru",
        "sa",
    ):
        assert (
            memory_report.get(
                language,
                {},
            ).get(
                "same_as_english",
                False,
            )
            is False
        )


def test_block_4b_russian_page_titles() -> None:
    import src.dashboard as dashboard

    assert (
        dashboard.UPLOAD_RAG_TEXTS[
            "ru"
        ]["title"]
        == "## 📄 Загрузка документов в базу RAG"
    )

    assert (
        dashboard.MEMORY_PAGE_TEXTS[
            "ru"
        ]["title"]
        == "## 🧠 Память Пользователя — INNA"
    )


def test_block_4b_arabic_page_titles() -> None:
    import src.dashboard as dashboard

    assert (
        dashboard.UPLOAD_RAG_TEXTS[
            "sa"
        ]["title"]
        == "## 📄 تحميل المستندات إلى قاعدة RAG"
    )

    assert (
        dashboard.MEMORY_PAGE_TEXTS[
            "sa"
        ]["title"]
        == "## 🧠 ذاكرة المستخدم — INNA"
    )


def test_block_4b_memory_placeholders() -> None:
    import src.dashboard as dashboard

    for language in (
        "it",
        "ro",
        "ua",
        "ru",
        "sa",
    ):
        assert (
            "{user_id}"
            in dashboard.MEMORY_PAGE_TEXTS[
                language
            ]["memory_loaded"]
        )

        assert (
            "{user_id}"
            in dashboard.MEMORY_PAGE_TEXTS[
                language
            ]["memory_not_found"]
        )

def test_tools_analytics_language_packs_are_independent() -> None:
    from src.dashboard_pages.tools_analytics_page import (
        TOOLS_ANALYTICS_TEXTS,
    )

    languages = (
        "en_us",
        "en_gb",
        "ro",
        "ua",
        "ru",
        "sa",
    )

    object_ids = {
        id(
            TOOLS_ANALYTICS_TEXTS[
                language
            ]
        )
        for language in languages
    }

    assert len(object_ids) == len(
        languages
    )


def test_tools_analytics_translator_uses_interface_language(
    monkeypatch,
) -> None:
    import src.dashboard_pages.tools_analytics_page as page

    monkeypatch.setattr(
        page.st,
        "session_state",
        {
            "dashboard_interface_lang": "ru",
        },
    )

    assert (
        page.tools_analytics_lang()
        == "ru"
    )

    assert (
        page.tools_analytics_t(
            "title"
        )
        == page.TOOLS_ANALYTICS_TEXTS[
            "ru"
        ]["title"]
    )


def test_tools_analytics_language_audit_structure() -> None:
    from src.dashboard_pages.tools_analytics_page import (
        audit_tools_analytics_language_packs,
    )

    report = (
        audit_tools_analytics_language_packs()
    )

    assert set(report) == {
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

    for details in report.values():
        assert "total" in details
        assert "missing" in details
        assert "extra" in details
        assert "empty" in details
        assert "same_as_english" in details
        assert "object_id" in details

def test_tools_analytics_italian_anomaly_translations() -> None:
    from src.dashboard_pages.tools_analytics_page import (
        TOOLS_ANALYTICS_TEXTS,
    )

    texts = TOOLS_ANALYTICS_TEXTS[
        "it"
    ]

    expected = {
        "anomaly_detection": (
            "## 🚨 Rilevamento delle anomalie"
        ),
        "detected_anomalies": (
            "Anomalie rilevate"
        ),
        "highest_severity": (
            "Gravità massima"
        ),
        "critical": "Critiche",
        "high": "Elevate",
        "medium": "Medie",
        "low": "Basse",
        "detected_alerts": (
            "### Avvisi rilevati"
        ),
        "severity": "Gravità",
        "metric": "Metrica",
        "recommendation": (
            "Raccomandazione"
        ),
        "how_detection_works": (
            "Come funziona il rilevamento"
        ),
    }

    for key, value in expected.items():
        assert texts[key] == value


def test_tools_analytics_native_languages_are_not_english() -> None:
    from src.dashboard_pages.tools_analytics_page import (
        audit_tools_analytics_language_packs,
    )

    report = (
        audit_tools_analytics_language_packs()
    )

    for language in (
        "it",
        "ro",
        "ua",
        "ru",
        "sa",
    ):
        assert (
            report[language][
                "same_as_english"
            ]
            is False
        )

def test_tools_analytics_visual_labels_are_translated() -> None:
    from src.dashboard_pages.tools_analytics_page import (
        TOOLS_ANALYTICS_TEXTS,
    )

    expected = {
        "pt": (
            "Valor atual",
            "Referência",
        ),
        "en_us": (
            "Current value",
            "Reference",
        ),
        "es": (
            "Valor actual",
            "Referencia",
        ),
        "fr": (
            "Valeur actuelle",
            "Référence",
        ),
        "de": (
            "Aktueller Wert",
            "Referenz",
        ),
        "it": (
            "Valore attuale",
            "Riferimento",
        ),
        "ro": (
            "Valoare actuală",
            "Referință",
        ),
        "ua": (
            "Поточне значення",
            "Орієнтир",
        ),
        "ru": (
            "Текущее значение",
            "Ориентир",
        ),
        "sa": (
            "القيمة الحالية",
            "القيمة المرجعية",
        ),
    }

    for language, values in expected.items():
        assert (
            TOOLS_ANALYTICS_TEXTS[
                language
            ]["current_value"]
            == values[0]
        )

        assert (
            TOOLS_ANALYTICS_TEXTS[
                language
            ]["reference"]
            == values[1]
        )


def test_tools_analytics_has_no_fixed_portuguese_metric_labels(
) -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/tools_analytics_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'st.metric("Valor atual"' not in source
    assert 'st.metric("Referência"' not in source

def test_tools_dynamic_values_are_localized() -> None:
    from src.dashboard_i18n import (
        translate_intention,
        translate_origin,
        translate_tool_name,
    )

    assert (
        translate_tool_name(
            "calculo_capacidade_semanal",
            language="ru",
        )
        == "Еженедельный расчёт мощности"
    )

    assert (
        translate_intention(
            "simulacao_reserva",
            language="ru",
        )
        == "Симуляция резерва"
    )

    assert (
        translate_origin(
            "dashboard_rag",
            language="ru",
        )
        == "RAG-панель"
    )


def test_tools_dynamic_values_preserve_unknown_codes() -> None:
    from src.dashboard_i18n import (
        translate_intention,
        translate_origin,
        translate_tool_name,
    )

    assert (
        translate_tool_name(
            "nova_tool_financeira",
            language="ru",
        )
        == "nova_tool_financeira"
    )

    assert (
        translate_intention(
            "nova_intencao",
            language="ru",
        )
        == "nova_intencao"
    )

    assert (
        translate_origin(
            "nova_origem",
            language="ru",
        )
        == "nova_origem"
    )


def test_tools_dynamic_values_normalize_language_aliases() -> None:
    from src.dashboard_i18n import (
        translate_intention,
        translate_origin,
        translate_tool_name,
    )

    assert (
        translate_tool_name(
            "calculo_capacidade_semanal",
            language="pt-BR",
        )
        == "Cálculo de capacidade semanal"
    )

    assert (
        translate_intention(
            "capacidade_semanal",
            language="uk",
        )
        == "Тижнева потужність"
    )

    assert (
        translate_origin(
            "teste_manual",
            language="ar",
        )
        == "اختبار يدوي"
    )


def test_tools_dynamic_language_dictionaries_are_independent() -> None:
    from src.dashboard_i18n import (
        TOOLS_VALUE_TEXTS,
    )

    dictionary_ids = [
        id(texts)
        for texts in TOOLS_VALUE_TEXTS.values()
    ]

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )

    assert len(TOOLS_VALUE_TEXTS) == 12

    for texts in TOOLS_VALUE_TEXTS.values():
        assert len(texts) == 6
        assert all(
            str(value).strip()
            for value in texts.values()
        )

def test_tools_dynamic_friendly_names_are_localized() -> None:
    from src.dashboard_i18n import (
        translate_tool_name,
    )

    assert (
        translate_tool_name(
            "Cálculo de capacidade semanal",
            language="ru",
        )
        == "Еженедельный расчёт мощности"
    )

    assert (
        translate_tool_name(
            "Simulação de formação de reserva",
            language="ru",
        )
        == "Симуляция формирования резерва"
    )


def test_tools_dynamic_friendly_names_work_in_other_languages() -> None:
    from src.dashboard_i18n import (
        translate_tool_name,
    )

    assert (
        translate_tool_name(
            "Cálculo de capacidade semanal",
            language="en_us",
        )
        == "Weekly capacity calculation"
    )

    assert (
        translate_tool_name(
            "Simulação de formação de reserva",
            language="es",
        )
        == "Simulación de formación de reserva"
    )


def test_tools_dynamic_name_normalization() -> None:
    from src.dashboard_i18n import (
        normalize_dynamic_value_key,
    )

    assert (
        normalize_dynamic_value_key(
            "Cálculo de capacidade semanal"
        )
        == "calculo_capacidade_semanal"
    )

    assert (
        normalize_dynamic_value_key(
            "Simulação de formação de reserva"
        )
        == "simulacao_reserva"
    )

    assert (
        normalize_dynamic_value_key(
            "calculo_capacidade_semanal"
        )
        == "calculo_capacidade_semanal"
    )

def test_tools_temporal_table_headers_use_i18n() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/tools_analytics_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        '"criado_em": tools_analytics_t('
        in source
    )

    assert (
        '"execucoes": tools_analytics_t('
        in source
    )

    assert (
        '"sucessos": tools_analytics_t('
        in source
    )

    assert (
        '"falhas": tools_analytics_t('
        in source
    )

    assert (
        '"duracao_media_ms": tools_analytics_t('
        in source
    )

    assert (
        '"confianca_media": tools_analytics_t('
        in source
    )

    assert (
        '"usuarios_ativos": tools_analytics_t('
        in source
    )

    assert (
        "st.dataframe(\n"
        "            tabela_temporal,"
        in source
    )

def test_health_main_panel_uses_interface_i18n() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/health_score_page.py"
    ).read_text(
        encoding="utf-8"
    )

    required_calls = {
        'health_page_t("tools_events")',
        'health_page_t("analysed_traces")',
        'health_page_t("refresh")',
        'health_page_t("global_health")',
        'health_page_t("classification")',
        'health_page_t("strongest_component")',
        'health_page_t("priority_component")',
        'health_page_t("component_scores")',
        'health_page_t("view_penalties")',
        'health_page_t("no_penalty")',
        '"priority_recommendations"',
    }

    for call in required_calls:
        assert call in source


def test_health_main_panel_language_catalog_is_complete() -> None:
    from src.dashboard_pages.health_score_page import (
        HEALTH_PAGE_MAIN_TEXTS,
    )

    expected_languages = {
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

    assert set(
        HEALTH_PAGE_MAIN_TEXTS
    ) == expected_languages

    reference = set(
        HEALTH_PAGE_MAIN_TEXTS["pt"]
    )

    dictionary_ids = []

    for texts in HEALTH_PAGE_MAIN_TEXTS.values():
        assert set(texts) == reference
        assert all(
            str(value).strip()
            for value in texts.values()
        )

        dictionary_ids.append(
            id(texts)
        )

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )

def test_health_history_catalog_is_complete() -> None:
    from src.dashboard_pages.health_score_page import (
        HEALTH_HISTORY_TEXTS,
    )

    expected_languages = {
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

    assert set(
        HEALTH_HISTORY_TEXTS
    ) == expected_languages

    reference = set(
        HEALTH_HISTORY_TEXTS["pt"]
    )

    dictionary_ids = []

    for texts in HEALTH_HISTORY_TEXTS.values():
        assert set(texts) == reference
        assert all(
            str(value).strip()
            for value in texts.values()
        )

        dictionary_ids.append(
            id(texts)
        )

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )


def test_health_history_uses_stable_period_values() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/health_score_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'health_history_t("period")' in source
    assert 'health_history_t("period_all")' in source
    assert "dias_selecionados = periodo_label" in source
    assert "dias=dias_selecionados" in source

def test_health_history_dynamic_catalog_is_complete() -> None:
    from src.dashboard_pages.health_score_page import (
        HEALTH_HISTORY_DYNAMIC_TEXTS,
    )

    expected_languages = {
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

    assert set(
        HEALTH_HISTORY_DYNAMIC_TEXTS
    ) == expected_languages

    reference = set(
        HEALTH_HISTORY_DYNAMIC_TEXTS["pt"]
    )

    dictionary_ids = []

    for texts in HEALTH_HISTORY_DYNAMIC_TEXTS.values():
        assert set(texts) == reference
        assert all(
            str(value).strip()
            for value in texts.values()
        )

        dictionary_ids.append(
            id(texts)
        )

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )


def test_health_history_dynamic_visuals_use_i18n() -> None:
    import ast
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/health_score_page.py"
    ).read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    translated_dynamic_keys = set()
    translated_table_keys = set()
    trend_translation_connected = False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            function_name = node.func.id
        else:
            continue

        if (
            function_name
            == "traduzir_tendencia_historico_health"
        ):
            trend_translation_connected = True

        if not node.args:
            continue

        first_argument = node.args[0]

        if not isinstance(
            first_argument,
            ast.Constant,
        ):
            continue

        if not isinstance(
            first_argument.value,
            str,
        ):
            continue

        if function_name == "health_history_dynamic_t":
            translated_dynamic_keys.add(
                first_argument.value
            )

        if function_name == "health_table_t":
            translated_table_keys.add(
                first_argument.value
            )

    assert {
        "save_error",
        "duplicate_snapshot",
        "snapshot_saved",
        "load_error",
        "empty_history",
        "minimum_snapshots",
    }.issubset(
        translated_dynamic_keys
    )

    assert {
        "tools",
        "memory",
        "infrastructure",
    }.issubset(
        translated_table_keys
    )

    assert trend_translation_connected

def test_health_runtime_messages_catalog_is_complete() -> None:
    from src.dashboard_pages.health_score_page import (
        HEALTH_RUNTIME_MESSAGE_TEXTS,
    )

    expected_languages = {
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

    assert set(
        HEALTH_RUNTIME_MESSAGE_TEXTS
    ) == expected_languages

    reference = set(
        HEALTH_RUNTIME_MESSAGE_TEXTS["pt"]
    )

    dictionary_ids = []

    for texts in HEALTH_RUNTIME_MESSAGE_TEXTS.values():
        assert set(texts) == reference
        assert all(
            str(value).strip()
            for value in texts.values()
        )

        dictionary_ids.append(
            id(texts)
        )

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )


def test_health_runtime_penalty_translation_preserves_value(
    monkeypatch,
) -> None:
    from src.dashboard_pages import health_score_page

    monkeypatch.setitem(
        health_score_page.st.session_state,
        "dashboard_interface_lang",
        "ru",
    )

    translated = (
        health_score_page.traduzir_penalidade_health(
            "Taxa de sucesso: -12.5"
        )
    )

    assert translated.startswith(
        "Доля успешных выполнений"
    )
    assert translated.endswith(
        ": -12.5"
    )


def test_health_runtime_recommendation_translates_component(
    monkeypatch,
) -> None:
    from src.dashboard_pages import health_score_page

    monkeypatch.setitem(
        health_score_page.st.session_state,
        "dashboard_interface_lang",
        "ru",
    )

    translated = (
        health_score_page.traduzir_recomendacao_health(
            "Priorizar melhorias no componente memoria, "
            "atualmente com score 72.5/100."
        )
    )

    assert "Память" in translated
    assert "72.5/100" in translated

def test_health_score_render_has_no_remaining_portuguese_visual_literals(
) -> None:
    import ast
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/health_score_page.py"
    ).read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    target = next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "render_health_score_page"
        )
    )

    forbidden = {
        (
            "A INNA apresenta componentes que "
            "precisam de atenção."
        ),
        (
            "A saúde global está crítica. Priorize os "
            "componentes com menor score."
        ),
        "## Recomendações prioritárias",
    }

    literals = {
        node.value
        for node in ast.walk(target)
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        )
    }

    assert forbidden.isdisjoint(
        literals
    )

    calls = [
        node
        for node in ast.walk(target)
        if isinstance(node, ast.Call)
    ]

    translated_keys = set()

    for call in calls:
        if not isinstance(
            call.func,
            ast.Name,
        ):
            continue

        if call.func.id != "health_page_t":
            continue

        if not call.args:
            continue

        argument = call.args[0]

        if (
            isinstance(argument, ast.Constant)
            and isinstance(argument.value, str)
        ):
            translated_keys.add(
                argument.value
            )

    assert {
        "attention_message",
        "critical_message",
        "priority_recommendations",
        "component",
    }.issubset(
        translated_keys
    )

def test_llmops_native_infrastructure_catalog_is_complete(
) -> None:
    from src.evaluation.dashboard import (
        LLMOPS_INFRA_TEXTS,
    )

    expected_languages = {
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

    assert set(
        LLMOPS_INFRA_TEXTS
    ) == expected_languages

    reference_keys = set(
        LLMOPS_INFRA_TEXTS["pt"]
    )

    for texts in LLMOPS_INFRA_TEXTS.values():
        assert set(texts) == reference_keys
        assert all(
            str(value).strip()
            for value in texts.values()
        )


def test_llmops_russian_infrastructure_is_not_english(
) -> None:
    from src.evaluation.dashboard import (
        LLMOPS_INFRA_TEXTS,
    )

    russian = LLMOPS_INFRA_TEXTS["ru"]
    english = LLMOPS_INFRA_TEXTS["en_us"]

    keys = {
        "infrastructure_title",
        "general_status",
        "available",
        "active",
        "execution",
        "local",
        "infrastructure_details",
    }

    for key in keys:
        assert russian[key] != english[key]

    assert (
        russian["infrastructure_title"]
        == "Инфраструктура и наблюдаемость"
    )

def test_llm_cost_alert_visual_catalog_is_complete() -> None:
    from src.dashboard_pages.llm_costs_page import (
        LLM_COST_ALERT_VISUAL_TEXTS,
    )

    expected_languages = {
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

    assert set(
        LLM_COST_ALERT_VISUAL_TEXTS
    ) == expected_languages

    reference = set(
        LLM_COST_ALERT_VISUAL_TEXTS["pt"]
    )

    dictionary_ids = []

    for texts in LLM_COST_ALERT_VISUAL_TEXTS.values():
        assert set(texts) == reference
        assert all(
            str(value).strip()
            for value in texts.values()
        )

        dictionary_ids.append(
            id(texts)
        )

    assert len(dictionary_ids) == len(
        set(dictionary_ids)
    )


def test_llm_alert_filter_uses_stable_internal_values() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/llm_costs_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'options=[\n            "aberto",' in source
    assert '"resolvido",' in source
    assert '"todos",' in source
    assert (
        "format_func=formatar_status_filtro_alerta"
        in source
    )

def test_llm_cost_alert_dynamic_visuals_are_localized() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/llm_costs_page.py"
    ).read_text(
        encoding="utf-8"
    )

    start = source.index(
        "def render_alertas_llm_section("
    )

    end = source.index(
        "\ndef llm_cost_page_t(",
        start,
    )

    render_source = source[
        start:end
    ]

    forbidden_visuals = {
        '"Nenhum alerta encontrado para o filtro atual."',
        '"Status",\n                status.title()',
        '"Severidade",\n                severidade.title()',
        """metrica_cols[1].metric(
                "Valor atual",""",
        '"Criado em: "',
        '"📧 Enviar alerta por e-mail"',
        '"Enviando alerta..."',
        '"Alerta enviado por e-mail."',
        '"Alerta resolvido."',
    }

    for visual in forbidden_visuals:
        assert visual not in render_source

    assert (
        "traduzir_status_alerta_visual"
        in render_source
    )

    assert (
        "traduzir_severidade_alerta_visual"
        in render_source
    )


def test_llm_cost_alert_dynamic_helpers_preserve_unknown_values(
) -> None:
    from src.dashboard_pages.llm_costs_page import (
        traduzir_severidade_alerta_visual,
        traduzir_status_alerta_visual,
    )

    assert (
        traduzir_status_alerta_visual(
            "custom_status"
        )
        == "custom_status"
    )

    assert (
        traduzir_severidade_alerta_visual(
            "custom_severity"
        )
        == "custom_severity"
    )

def test_llm_cost_remaining_messages_are_localized() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/llm_costs_page.py"
    ).read_text(
        encoding="utf-8"
    )

    start = source.index(
        "def render_alertas_llm_section("
    )

    end = source.index(
        "\ndef llm_cost_page_t(",
        start,
    )

    render_source = source[
        start:end
    ]

    forbidden = {
        '"Notificações por e-mail habilitadas. "',
        '"Detalhes técnicos das integrações"',
        """limite_eventos = controle_evento_2.selectbox(
        "Limite de eventos",""",
        '"Nenhum evento do webhook "',
        '"Nenhuma notificação registrada."',
        '"Nenhuma notificação disponível "',
        '"Não existem notificações "',
        '"O reenvio é limitado a três "',
        '"🔄 Reenviar"',
        '"Reenviando notificação..."',
        '"Notificação reenviada."',
        '"Falha no reenvio."',
    }

    for text in forbidden:
        assert text not in render_source

    required_calls = {
        'llm_alert_section_t(\n                "email_enabled"',
        'llm_alert_section_t(\n                "integration_details"',
        'llm_alert_section_t(\n                    "no_webhook_events"',
        'llm_alert_section_t(\n                "no_notifications"',
        'llm_alert_section_t(\n                "no_retry"',
        'llm_alert_section_t(\n                    "no_failed_retry"',
        'llm_alert_section_t(\n                    "retry_limit"',
    }

    for call in required_calls:
        assert call in render_source

def test_llm_alert_dynamic_content_display_i18n() -> None:
    from pathlib import Path

    source = Path(
        "src/dashboard_pages/llm_costs_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "# LLM_COST_ALERT_CONTENT_DISPLAY_I18N"
        in source
    )

    for language in {
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
    }:
        if language == "ch":
            assert (
                'LLM_ALERT_CONTENT_TEXTS["ch"]'
                in source
            )
        else:
            assert f'    "{language}": {{' in source

    for code in {
        "orcamento_mensal",
        "projecao_mensal",
        "chamadas_lentas",
        "falhas_llm",
        "tokens_elevados",
    }:
        assert source.count(
            f'        "{code}": {{'
        ) >= 11

    start = source.index(
        "def render_alertas_llm_section("
    )

    end = source.index(
        "\ndef llm_cost_page_t(",
        start,
    )

    render_source = source[
        start:end
    ]

    assert (
        "traduzir_conteudo_alerta_visual("
        in render_source
    )

    assert (
        'conteudo_visual[\n            "titulo"\n        ]'
        in render_source
    )

    assert (
        'conteudo_visual[\n                    "descricao"\n                ]'
        in render_source
    )

    assert (
        'f"{conteudo_visual[\'recomendacao\']}"'
        in render_source
    )

    assert (
        'f"{conteudo_visual[\'categoria\']} | "'
        in render_source
    )


# BLOCK_7A_UPLOAD_RAG_I18N_REGRESSION_TESTS


def _load_effective_upload_rag_catalogs():
    from pathlib import Path

    dashboard_source = Path(
        "src/dashboard.py"
    ).read_text(
        encoding="utf-8"
    )

    start = dashboard_source.index(
        "UPLOAD_RAG_TEXTS = {"
    )

    end = dashboard_source.index(
        "\ndef upload_rag_t(",
        start,
    )

    namespace = {}

    exec(
        compile(
            dashboard_source[start:end],
            "upload_rag_i18n_test_catalogs",
            "exec",
        ),
        namespace,
    )

    return namespace


def test_block_7a_upload_rag_native_catalog_coverage():
    catalogs = _load_effective_upload_rag_catalogs()

    catalog_names = (
        "UPLOAD_RAG_DOCUMENT_TEXTS",
        "UPLOAD_RAG_EMBEDDING_TEXTS",
        "UPLOAD_RAG_FINAL_RESPONSE_TEXTS",
        "UPLOAD_RAG_SOURCE_TEXTS",
        "UPLOAD_RAG_RUNTIME_VISUAL_TEXTS",
    )

    languages = (
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
    )

    for catalog_name in catalog_names:
        catalog = catalogs[catalog_name]
        expected_keys = set(
            catalog["en_us"]
        )

        for language in languages:
            assert language in catalog, (
                f"{catalog_name}: catálogo ausente "
                f"para {language}"
            )

            values = catalog[language]

            assert set(values) == expected_keys, (
                f"{catalog_name}/{language}: "
                "cobertura de chaves divergente"
            )

            assert all(
                str(value).strip()
                for value in values.values()
            ), (
                f"{catalog_name}/{language}: "
                "valor vazio encontrado"
            )


def test_block_7a_upload_rag_native_texts_not_overwritten():
    catalogs = _load_effective_upload_rag_catalogs()

    strict_languages = (
        "it",
        "ro",
        "ua",
        "ru",
        "sa",
    )

    allowed_equal_to_english = {
        (
            "UPLOAD_RAG_EMBEDDING_TEXTS",
            "it",
            "chunk",
        ),
        (
            "UPLOAD_RAG_EMBEDDING_TEXTS",
            "ro",
            "manual_mode",
        ),
        (
            "UPLOAD_RAG_SOURCE_TEXTS",
            "ro",
            "document",
        ),
    }

    for catalog_name in (
        "UPLOAD_RAG_DOCUMENT_TEXTS",
        "UPLOAD_RAG_EMBEDDING_TEXTS",
        "UPLOAD_RAG_FINAL_RESPONSE_TEXTS",
        "UPLOAD_RAG_SOURCE_TEXTS",
        "UPLOAD_RAG_RUNTIME_VISUAL_TEXTS",
    ):
        catalog = catalogs[catalog_name]
        english = catalog["en_us"]

        for language in strict_languages:
            values = catalog[language]

            unexpected_reuse = {
                key
                for key, english_value
                in english.items()
                if (
                    values.get(key) == english_value
                    and (
                        catalog_name,
                        language,
                        key,
                    )
                    not in allowed_equal_to_english
                )
            }

            assert not unexpected_reuse, (
                f"{catalog_name}/{language}: "
                "textos ingleses inesperados: "
                f"{sorted(unexpected_reuse)}"
            )


def test_block_7a_upload_rag_language_dictionaries_are_isolated():
    catalogs = _load_effective_upload_rag_catalogs()

    upload_texts = catalogs[
        "UPLOAD_RAG_TEXTS"
    ]

    isolated_languages = (
        "ro",
        "ua",
        "ru",
        "sa",
    )

    for language in isolated_languages:
        assert (
            upload_texts[language]
            is not upload_texts["en_us"]
        )

    for index, language in enumerate(
        isolated_languages
    ):
        for other_language in (
            isolated_languages[
                index + 1:
            ]
        ):
            assert (
                upload_texts[language]
                is not upload_texts[
                    other_language
                ]
            )

    assert (
        upload_texts["ch"]
        is not upload_texts["de"]
    )


def test_block_7a_upload_rag_source_native_languages():
    catalogs = _load_effective_upload_rag_catalogs()

    source_texts = catalogs[
        "UPLOAD_RAG_SOURCE_TEXTS"
    ]

    assert (
        source_texts["ro"]["sources_used"]
        == "#### 📚 Surse utilizate de INNA"
    )
    assert (
        source_texts["ua"]["source"]
        == "Джерело"
    )
    assert (
        source_texts["ru"]["source"]
        == "Источник"
    )
    assert (
        source_texts["sa"]["source"]
        == "المصدر"
    )


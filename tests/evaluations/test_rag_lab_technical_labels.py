import src.dashboard_pages.rag_evaluation_lab_page as rag_lab_page


def test_rag_lab_uses_russian_technical_labels(
    monkeypatch,
):
    monkeypatch.setattr(
        rag_lab_page,
        "_rag_lab_language",
        lambda: "ru",
    )

    assert rag_lab_page.rag_lab_t(
        "quality_gate"
    ) == (
        "Контроль качества "
        "(Quality Gate)"
    )

    assert rag_lab_page.rag_lab_t(
        "reranker"
    ) == (
        "Переранжировщик "
        "(Reranker)"
    )

    assert rag_lab_page.rag_lab_t(
        "embedding"
    ) == (
        "Векторное представление "
        "(Embedding)"
    )

    assert rag_lab_page.rag_lab_t(
        "latency"
    ) == "Задержка"

    assert rag_lab_page.rag_lab_t(
        "tokens"
    ) == (
        "Единицы обработки "
        "(Tokens)"
    )


def test_rag_lab_uses_portuguese_technical_labels(
    monkeypatch,
):
    monkeypatch.setattr(
        rag_lab_page,
        "_rag_lab_language",
        lambda: "pt",
    )

    assert rag_lab_page.rag_lab_t(
        "quality_gate"
    ) == (
        "Portão de qualidade "
        "(Quality Gate)"
    )

    assert rag_lab_page.rag_lab_t(
        "hybrid"
    ) == (
        "Busca híbrida "
        "(Hybrid)"
    )


def test_rag_lab_keeps_normal_translations(
    monkeypatch,
):
    monkeypatch.setattr(
        rag_lab_page,
        "_rag_lab_language",
        lambda: "pt",
    )

    assert rag_lab_page.rag_lab_t(
        "title"
    ) == (
        rag_lab_page.RAG_LAB_TEXTS[
            "pt"
        ]["title"]
    )

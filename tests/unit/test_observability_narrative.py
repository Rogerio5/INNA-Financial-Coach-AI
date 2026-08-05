import pandas as pd

from src.observability.narrative import (
    classificar_saude_operacional,
    gerar_insights_operacionais,
    gerar_texto_narrativa,
)


def dataframe_saudavel():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "criado_em": "2026-07-14T07:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": "analisar_orcamento",
                "tool_label": "Análise do orçamento",
                "intencao": "analise_orcamento",
                "origem": "dashboard_rag",
                "executada": True,
                "sucesso": True,
                "confianca": 0.95,
                "duracao_ms": 100.0,
            },
            {
                "id": 2,
                "criado_em": "2026-07-14T08:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": "analisar_orcamento",
                "tool_label": "Análise do orçamento",
                "intencao": "analise_orcamento",
                "origem": "dashboard_rag",
                "executada": True,
                "sucesso": True,
                "confianca": 0.90,
                "duracao_ms": 200.0,
            },
        ]
    )


def dataframe_com_problemas():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "criado_em": "2026-07-14T07:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": None,
                "tool_label": None,
                "intencao": None,
                "origem": "dashboard_rag",
                "executada": False,
                "sucesso": False,
                "confianca": 0.50,
                "duracao_ms": 8000.0,
            },
            {
                "id": 2,
                "criado_em": "2026-07-14T08:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": "analisar_divida",
                "tool_label": "Análise de dívida",
                "intencao": "analise_divida",
                "origem": "dashboard_rag",
                "executada": True,
                "sucesso": False,
                "confianca": 0.60,
                "duracao_ms": 10000.0,
            },
        ]
    )


def test_saude_excelente():
    resultado = classificar_saude_operacional(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        p95_ms=1000,
    )

    assert resultado["score"] == 100.0
    assert resultado["classificacao"] == "Excelente"


def test_saude_com_penalidades():
    resultado = classificar_saude_operacional(
        taxa_sucesso=80,
        confianca_media=60,
        percentual_sem_tool=50,
        p95_ms=10000,
    )

    assert resultado["score"] < 70
    assert resultado["status"] == "critico"


def test_insights_saudaveis():
    resultado = gerar_insights_operacionais(dataframe_saudavel())

    assert resultado["ok"] is True
    assert resultado["tem_dados"] is True
    assert resultado["metricas"]["taxa_sucesso_percentual"] == 100.0

    assert len(resultado["destaques"]) > 0


def test_insights_com_alertas():
    resultado = gerar_insights_operacionais(dataframe_com_problemas())

    assert resultado["tem_dados"] is True
    assert len(resultado["alertas"]) > 0
    assert len(resultado["recomendacoes"]) > 0
    assert resultado["saude"]["score"] < 100


def test_insights_sem_dados():
    resultado = gerar_insights_operacionais(pd.DataFrame())

    assert resultado["tem_dados"] is False
    assert resultado["saude"]["score"] == 0.0


def test_gerar_texto_narrativa():
    insights = gerar_insights_operacionais(dataframe_saudavel())

    texto = gerar_texto_narrativa(insights)

    assert "Resumo operacional automático" in texto
    assert "Destaques" in texto
    assert "Recomendações" in texto


def test_operational_narrative_accepts_interface_language() -> None:
    resultado = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    assert resultado["ok"] is True
    assert resultado["tem_dados"] is True
    assert resultado["idioma"] == "ru"


def test_operational_narrative_defaults_to_portuguese() -> None:
    resultado = gerar_insights_operacionais(dataframe_saudavel())

    assert resultado["idioma"] == "pt"


def test_operational_narrative_normalizes_language() -> None:
    resultado = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma=" RU ",
    )

    assert resultado["idioma"] == "ru"


def test_operational_narrative_empty_result_keeps_language() -> None:
    resultado = gerar_insights_operacionais(
        pd.DataFrame(),
        idioma="sa",
    )

    assert resultado["tem_dados"] is False
    assert resultado["idioma"] == "sa"


def test_health_classification_accepts_language() -> None:
    resultado = classificar_saude_operacional(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        p95_ms=1000,
        idioma="en_us",
    )

    assert resultado["score"] == 100.0


def test_markdown_narrative_accepts_language() -> None:
    insights = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    texto = gerar_texto_narrativa(
        insights,
        idioma="ru",
    )

    assert isinstance(texto, str)
    assert texto


def test_operational_narrative_language_catalog() -> None:
    from src.observability.narrative import (
        NARRATIVE_TEXTS,
    )

    assert set(NARRATIVE_TEXTS) == {
        "pt",
        "en_us",
        "en_gb",
        "ru",
    }

    reference = set(NARRATIVE_TEXTS["pt"])

    for texts in NARRATIVE_TEXTS.values():
        assert set(texts) == reference
        assert all(str(value).strip() for value in texts.values())


def test_normalizar_idioma_narrativa() -> None:
    from src.observability.narrative import (
        normalizar_idioma_narrativa,
    )

    assert normalizar_idioma_narrativa("pt-BR") == "pt"

    assert normalizar_idioma_narrativa(" RU ") == "ru"

    assert normalizar_idioma_narrativa("en-GB") == "en_gb"

    assert normalizar_idioma_narrativa("ro") == "en_us"


def test_narrative_t_uses_requested_language() -> None:
    from src.observability.narrative import (
        narrative_t,
    )

    assert (
        narrative_t(
            "health_excellent",
            idioma="pt",
        )
        == "Excelente"
    )

    assert (
        narrative_t(
            "health_excellent",
            idioma="en_us",
        )
        == "Excellent"
    )

    assert (
        narrative_t(
            "health_excellent",
            idioma="ru",
        )
        == "Отличное"
    )


def test_narrative_language_dictionaries_are_independent() -> None:
    from src.observability.narrative import (
        NARRATIVE_TEXTS,
    )

    dictionary_ids = [id(texts) for texts in NARRATIVE_TEXTS.values()]

    assert len(dictionary_ids) == len(set(dictionary_ids))


def test_operational_health_classification_is_localized() -> None:
    portuguese = classificar_saude_operacional(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        p95_ms=1000,
        idioma="pt",
    )

    english = classificar_saude_operacional(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        p95_ms=1000,
        idioma="en_us",
    )

    russian = classificar_saude_operacional(
        taxa_sucesso=100,
        confianca_media=95,
        percentual_sem_tool=0,
        p95_ms=1000,
        idioma="ru",
    )

    assert portuguese["classificacao"] == "Excelente"
    assert english["classificacao"] == "Excellent"
    assert russian["classificacao"] == "Отличное"

    assert portuguese["status"] == "saudavel"
    assert english["status"] == "saudavel"
    assert russian["status"] == "saudavel"


def test_operational_empty_state_is_localized() -> None:
    english = gerar_insights_operacionais(
        pd.DataFrame(),
        idioma="en_us",
    )

    russian = gerar_insights_operacionais(
        pd.DataFrame(),
        idioma="ru",
    )

    assert english["titulo"] == "There is not enough data yet."

    assert english["saude"]["classificacao"] == "No data"

    assert russian["titulo"] == "Данных пока недостаточно."

    assert russian["saude"]["classificacao"] == "Нет данных"


def test_operational_summary_title_is_localized() -> None:
    english = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="en_us",
    )

    russian = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    assert english["titulo"] == "Automatic operational summary"

    assert russian["titulo"] == "Автоматическая операционная сводка"


def test_markdown_narrative_titles_are_localized() -> None:
    insights = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    markdown = gerar_texto_narrativa(
        insights,
        idioma="ru",
    )

    assert "### Сильные стороны" in markdown
    assert "### Рекомендации" in markdown
    assert "### Destaques" not in markdown
    assert "### Recomendações" not in markdown


def test_russian_dynamic_operational_narrative() -> None:
    resultado = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    assert resultado["idioma"] == "ru"

    assert "Проанализировано выполнений" in resultado["resumo_executivo"]

    assert "Уровень успешных выполнений" in resultado["resumo_executivo"]

    assert "Router" in resultado["resumo_executivo"]

    assert resultado["destaques"]
    assert resultado["recomendacoes"]

    combined = " ".join(
        [
            resultado["resumo_executivo"],
            *resultado["destaques"],
            *resultado["alertas"],
            *resultado["recomendacoes"],
        ]
    )

    assert "Foram analisadas" not in combined

    assert "A taxa de sucesso" not in combined

    assert "Todas as execuções" not in combined

    assert "Continuar monitorando" not in combined


def test_russian_dynamic_narrative_preserves_tool_name() -> None:
    resultado = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="ru",
    )

    tool = resultado["metricas"]["tool_mais_usada"]

    assert tool is not None

    tool_name = tool["nome"]

    combined = " ".join(
        [
            resultado["resumo_executivo"],
            *resultado["destaques"],
        ]
    )

    assert tool_name in combined


def test_portuguese_dynamic_narrative_remains_compatible() -> None:
    resultado = gerar_insights_operacionais(
        dataframe_saudavel(),
        idioma="pt",
    )

    assert "Foram analisadas" in resultado["resumo_executivo"]

    assert resultado["saude"]["classificacao"] == "Excelente"

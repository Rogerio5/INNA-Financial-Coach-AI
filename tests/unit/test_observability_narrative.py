import pandas as pd

from src.observability.narrative import (
    classificar_saude_operacional,
    gerar_insights_operacionais,
    gerar_texto_narrativa,
)


def dataframe_saudavel():
    return pd.DataFrame([
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
    ])


def dataframe_com_problemas():
    return pd.DataFrame([
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
    ])


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
    resultado = gerar_insights_operacionais(
        dataframe_saudavel()
    )

    assert resultado["ok"] is True
    assert resultado["tem_dados"] is True
    assert (
        resultado["metricas"][
            "taxa_sucesso_percentual"
        ]
        == 100.0
    )

    assert len(
        resultado["destaques"]
    ) > 0


def test_insights_com_alertas():
    resultado = gerar_insights_operacionais(
        dataframe_com_problemas()
    )

    assert resultado["tem_dados"] is True
    assert len(resultado["alertas"]) > 0
    assert len(resultado["recomendacoes"]) > 0
    assert resultado["saude"]["score"] < 100


def test_insights_sem_dados():
    resultado = gerar_insights_operacionais(
        pd.DataFrame()
    )

    assert resultado["tem_dados"] is False
    assert resultado["saude"]["score"] == 0.0


def test_gerar_texto_narrativa():
    insights = gerar_insights_operacionais(
        dataframe_saudavel()
    )

    texto = gerar_texto_narrativa(
        insights
    )

    assert "Resumo operacional automático" in texto
    assert "Destaques" in texto
    assert "Recomendações" in texto

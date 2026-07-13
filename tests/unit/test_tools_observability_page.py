import pandas as pd

from src.dashboard_pages.tools_observability_page import (
    calcular_taxa_sucesso,
    preparar_eventos_exibicao,
    preparar_ranking_tools,
    preparar_serie_temporal,
    render_metricas_executivas,
)


def dataframe_teste():
    return pd.DataFrame([
        {
            "id": 1,
            "criado_em": "2026-07-13T03:00:00Z",
            "usuario_id": "demo_user",
            "pergunta": "Quanto sobra?",
            "tool_nome": "analisar_orcamento",
            "tool_label": "Análise do orçamento mensal",
            "intencao": "analise_orcamento",
            "confianca": 0.95,
            "executada": True,
            "sucesso": True,
            "duracao_ms": 0.20,
            "origem": "dashboard_rag",
            "mensagem": "Executada.",
            "erro": None,
        },
        {
            "id": 2,
            "criado_em": "2026-07-13T04:00:00Z",
            "usuario_id": "demo_user",
            "pergunta": "Quanto sobra?",
            "tool_nome": "analisar_orcamento",
            "tool_label": "Análise do orçamento mensal",
            "intencao": "analise_orcamento",
            "confianca": 0.90,
            "executada": True,
            "sucesso": False,
            "duracao_ms": 0.40,
            "origem": "dashboard_rag",
            "mensagem": "Falha.",
            "erro": "Erro simulado",
        },
    ])


def test_calcular_taxa_sucesso():
    assert calcular_taxa_sucesso(
        8,
        10,
    ) == 80.0


def test_taxa_sem_execucoes():
    assert calcular_taxa_sucesso(
        0,
        0,
    ) == 0.0


def test_ranking_com_performance():
    ranking = preparar_ranking_tools(
        dataframe_teste()
    )

    item = ranking.iloc[0]

    assert (
        item["Ferramenta"]
        == "Análise do orçamento mensal"
    )
    assert item["Execuções"] == 2
    assert item["Sucessos"] == 1
    assert item["Falhas"] == 1
    assert item["Média_ms"] == 0.3
    assert item["Mínimo_ms"] == 0.2
    assert item["Máximo_ms"] == 0.4
    assert item["Taxa de sucesso (%)"] == 50.0


def test_serie_temporal_por_hora():
    serie = preparar_serie_temporal(
        dataframe_teste(),
        "Hora",
    )

    assert len(serie) == 2
    assert serie["Execuções"].sum() == 2
    assert serie["Sucessos"].sum() == 1


def test_serie_temporal_por_dia():
    serie = preparar_serie_temporal(
        dataframe_teste(),
        "Dia",
    )

    assert len(serie) == 1
    assert serie.iloc[0]["Execuções"] == 2
    assert serie.iloc[0]["Sucessos"] == 1


def test_eventos_exibicao_tem_pergunta():
    tabela = preparar_eventos_exibicao(
        dataframe_teste()
    )

    assert "Pergunta" in tabela.columns
    assert "Ferramenta" in tabela.columns
    assert "Status" in tabela.columns
    assert "Confiança" in tabela.columns
    assert "Duração" in tabela.columns

    assert tabela.iloc[0]["Pergunta"] == "Quanto sobra?"
    assert tabela.iloc[0]["Confiança"] == "95%"
    assert tabela.iloc[0]["Status"] == "Sucesso"


def test_ranking_vazio():
    ranking = preparar_ranking_tools(
        pd.DataFrame()
    )

    assert ranking.empty


def test_serie_temporal_vazia():
    serie = preparar_serie_temporal(
        pd.DataFrame(),
        "Hora",
    )

    assert serie.empty


def test_eventos_exibicao_vazio():
    tabela = preparar_eventos_exibicao(
        pd.DataFrame()
    )

    assert tabela.empty

def test_componente_metricas_executivas_disponivel():
    assert callable(
        render_metricas_executivas
    )


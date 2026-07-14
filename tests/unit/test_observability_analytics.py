from datetime import datetime, timezone

import pandas as pd

from src.observability.analytics import (
    calcular_distribuicao_coluna,
    calcular_execucoes_sem_tool,
    calcular_percentis,
    calcular_ranking_tools,
    calcular_serie_temporal_analytics,
    comparar_periodos,
)


AGORA = datetime(
    2026,
    7,
    13,
    20,
    0,
    tzinfo=timezone.utc,
)


def dataframe_teste():
    return pd.DataFrame([
        {
            "id": 1,
            "criado_em": "2026-07-13T19:00:00Z",
            "usuario_id": "demo_user",
            "tool_nome": "analisar_orcamento",
            "tool_label": "Análise do orçamento",
            "intencao": "analise_orcamento",
            "origem": "dashboard_rag",
            "executada": True,
            "sucesso": True,
            "confianca": 0.95,
            "duracao_ms": 10.0,
        },
        {
            "id": 2,
            "criado_em": "2026-07-13T18:00:00Z",
            "usuario_id": "demo_user",
            "tool_nome": "analisar_orcamento",
            "tool_label": "Análise do orçamento",
            "intencao": "analise_orcamento",
            "origem": "dashboard_rag",
            "executada": True,
            "sucesso": False,
            "confianca": 0.85,
            "duracao_ms": 20.0,
        },
        {
            "id": 3,
            "criado_em": "2026-07-12T19:00:00Z",
            "usuario_id": "outro_user",
            "tool_nome": (
                "calcular_capacidade_semanal"
            ),
            "tool_label": (
                "Capacidade semanal"
            ),
            "intencao": "capacidade_semanal",
            "origem": "teste_manual",
            "executada": True,
            "sucesso": True,
            "confianca": 0.75,
            "duracao_ms": 30.0,
        },
        {
            "id": 4,
            "criado_em": "2026-07-11T19:00:00Z",
            "usuario_id": "sem_tool_user",
            "tool_nome": None,
            "tool_label": None,
            "intencao": None,
            "origem": "dashboard_rag",
            "executada": False,
            "sucesso": False,
            "confianca": None,
            "duracao_ms": None,
        },
    ])


def test_calcular_percentis():
    resultado = calcular_percentis(
        [10, 20, 30, 40]
    )

    assert resultado["p50"] == 25.0
    assert resultado["p95"] == 38.5
    assert resultado["p99"] == 39.7


def test_ranking_tools():
    ranking = calcular_ranking_tools(
        dataframe_teste()
    )

    primeira = ranking.iloc[0]

    assert (
        primeira["ferramenta"]
        == "Análise do orçamento"
    )

    assert primeira["execucoes"] == 2
    assert primeira["sucessos"] == 1
    assert primeira["falhas"] == 1
    assert (
        primeira[
            "taxa_sucesso_percentual"
        ]
        == 50.0
    )

    assert primeira["p50_ms"] == 15.0


def test_distribuicao_intencao():
    distribuicao = (
        calcular_distribuicao_coluna(
            dataframe_teste(),
            "intencao",
        )
    )

    item = distribuicao[
        distribuicao["intencao"]
        == "analise_orcamento"
    ].iloc[0]

    assert item["total"] == 2
    assert item["percentual"] == 50.0


def test_execucoes_sem_tool():
    resultado = calcular_execucoes_sem_tool(
        dataframe_teste()
    )

    assert resultado["total"] == 1
    assert resultado["percentual"] == 25.0


def test_serie_temporal_diaria():
    serie = calcular_serie_temporal_analytics(
        dataframe_teste(),
        "D",
    )

    assert serie["execucoes"].sum() == 4
    assert serie["sucessos"].sum() == 2


def test_comparar_periodos():
    resultado = comparar_periodos(
        dataframe_teste(),
        agora=AGORA,
        horas=24,
    )

    assert (
        resultado["periodo_atual"][
            "execucoes"
        ]
        == 2
    )

    assert (
        resultado["periodo_anterior"][
            "execucoes"
        ]
        == 1
    )

    assert (
        resultado[
            "variacao_execucoes_percentual"
        ]
        == 100.0
    )


def test_analytics_vazio():
    assert calcular_ranking_tools(
        pd.DataFrame()
    ).empty

    assert calcular_serie_temporal_analytics(
        pd.DataFrame(),
        "D",
    ).empty

from datetime import datetime, timezone

import pandas as pd

from src.observability.metrics import (
    calcular_metricas_executivas,
    calcular_percentil_95,
    calcular_taxa_sucesso,
    identificar_tool_mais_utilizada,
)


AGORA = datetime(
    2026,
    7,
    13,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def dataframe_teste():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "criado_em": "2026-07-13T10:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": "analisar_orcamento",
                "tool_label": ("Análise do orçamento mensal"),
                "executada": True,
                "sucesso": True,
                "confianca": 0.95,
                "duracao_ms": 10.0,
            },
            {
                "id": 2,
                "criado_em": "2026-07-13T11:00:00Z",
                "usuario_id": "demo_user",
                "tool_nome": ("calcular_capacidade_semanal"),
                "tool_label": ("Cálculo de capacidade semanal"),
                "executada": True,
                "sucesso": True,
                "confianca": 0.85,
                "duracao_ms": 20.0,
            },
            {
                "id": 3,
                "criado_em": "2026-07-12T15:00:00Z",
                "usuario_id": "outro_user",
                "tool_nome": "analisar_orcamento",
                "tool_label": ("Análise do orçamento mensal"),
                "executada": True,
                "sucesso": False,
                "confianca": 0.75,
                "duracao_ms": 30.0,
            },
            {
                "id": 4,
                "criado_em": "2026-07-10T15:00:00Z",
                "usuario_id": None,
                "tool_nome": None,
                "tool_label": None,
                "executada": False,
                "sucesso": False,
                "confianca": None,
                "duracao_ms": None,
            },
        ]
    )


def test_calcular_taxa_sucesso():
    assert (
        calcular_taxa_sucesso(
            9,
            10,
        )
        == 90.0
    )


def test_calcular_taxa_sem_execucoes():
    assert (
        calcular_taxa_sucesso(
            0,
            0,
        )
        == 0.0
    )


def test_calcular_percentil_95():
    resultado = calcular_percentil_95([10, 20, 30])

    assert resultado == 29.0


def test_identificar_tool_mais_utilizada():
    resultado = identificar_tool_mais_utilizada(dataframe_teste())

    assert resultado["nome"] == "Análise do orçamento mensal"

    assert resultado["total"] == 2


def test_metricas_executivas():
    metricas = calcular_metricas_executivas(
        dataframe_teste(),
        agora=AGORA,
    )

    assert metricas["total_eventos"] == 4
    assert metricas["total_execucoes"] == 3
    assert metricas["total_sucesso"] == 2
    assert metricas["total_falhas"] == 1

    assert metricas["taxa_sucesso_percentual"] == 66.67

    assert metricas["usuarios_ativos"] == 2
    assert metricas["execucoes_hoje"] == 2

    assert metricas["execucoes_ultimas_24h"] == 3

    assert metricas["confianca_media_percentual"] == 85.0

    assert metricas["duracao_media_ms"] == 20.0
    assert metricas["duracao_minima_ms"] == 10.0
    assert metricas["duracao_maxima_ms"] == 30.0
    assert metricas["duracao_p95_ms"] == 29.0


def test_metricas_dataframe_vazio():
    metricas = calcular_metricas_executivas(
        pd.DataFrame(),
        agora=AGORA,
    )

    assert metricas["total_eventos"] == 0
    assert metricas["total_execucoes"] == 0
    assert metricas["usuarios_ativos"] == 0
    assert metricas["duracao_p95_ms"] == 0.0


def test_metricas_com_datas_invalidas():
    df = dataframe_teste()

    df.loc[0, "criado_em"] = "data-invalida"

    metricas = calcular_metricas_executivas(
        df,
        agora=AGORA,
    )

    assert metricas["total_eventos"] == 4
    assert metricas["execucoes_hoje"] == 1

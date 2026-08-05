from datetime import datetime, timezone

import pandas as pd

from src.observability.anomalies import (
    calcular_mad,
    detectar_anomalias_operacionais,
    detectar_outliers_mad,
)


AGORA = datetime(
    2026,
    7,
    14,
    12,
    0,
    tzinfo=timezone.utc,
)


def dataframe_estavel():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "criado_em": "2026-07-14T10:00:00Z",
                "usuario_id": "demo",
                "tool_nome": "orcamento",
                "tool_label": "Orçamento",
                "sucesso": True,
                "executada": True,
                "confianca": 0.90,
                "duracao_ms": 100.0,
            },
            {
                "id": 2,
                "criado_em": "2026-07-13T10:00:00Z",
                "usuario_id": "demo",
                "tool_nome": "orcamento",
                "tool_label": "Orçamento",
                "sucesso": True,
                "executada": True,
                "confianca": 0.90,
                "duracao_ms": 100.0,
            },
            {
                "id": 3,
                "criado_em": "2026-07-12T10:00:00Z",
                "usuario_id": "demo",
                "tool_nome": "orcamento",
                "tool_label": "Orçamento",
                "sucesso": True,
                "executada": True,
                "confianca": 0.90,
                "duracao_ms": 110.0,
            },
        ]
    )


def dataframe_anomalo():
    registros = []

    for indice in range(10):
        registros.append(
            {
                "id": indice + 1,
                "criado_em": (f"2026-07-13T{indice:02d}:00:00Z"),
                "usuario_id": "baseline",
                "tool_nome": "orcamento",
                "tool_label": "Orçamento",
                "sucesso": True,
                "executada": True,
                "confianca": 0.95,
                "duracao_ms": 100.0 + indice,
            }
        )

    registros.extend(
        [
            {
                "id": 20,
                "criado_em": "2026-07-14T10:00:00Z",
                "usuario_id": "atual",
                "tool_nome": None,
                "tool_label": None,
                "sucesso": False,
                "executada": False,
                "confianca": 0.50,
                "duracao_ms": 10000.0,
            },
            {
                "id": 21,
                "criado_em": "2026-07-14T11:00:00Z",
                "usuario_id": "atual",
                "tool_nome": None,
                "tool_label": None,
                "sucesso": False,
                "executada": False,
                "confianca": 0.55,
                "duracao_ms": 30000.0,
            },
        ]
    )

    return pd.DataFrame(registros)


def test_calcular_mad():
    assert calcular_mad([10, 10, 11, 12, 100]) == 1.0


def test_detectar_outlier_mad():
    resultado = detectar_outliers_mad([10, 10, 11, 12, 100])

    assert len(resultado) == 1
    assert resultado.iloc[0]["valor"] == 100


def test_sem_outlier_com_mad_zero():
    resultado = detectar_outliers_mad([10, 10, 10, 10])

    assert resultado.empty


def test_anomalias_sem_dados():
    resultado = detectar_anomalias_operacionais(
        pd.DataFrame(),
        agora=AGORA,
    )

    assert resultado["tem_dados"] is False
    assert resultado["total_anomalias"] == 0


def test_ambiente_estavel_sem_alerta_critico():
    resultado = detectar_anomalias_operacionais(
        dataframe_estavel(),
        agora=AGORA,
    )

    codigos = {item["codigo"] for item in resultado["anomalias"]}

    assert "aumento_taxa_falhas" not in codigos
    assert "queda_confianca_router" not in codigos


def test_detectar_multiplas_anomalias():
    resultado = detectar_anomalias_operacionais(
        dataframe_anomalo(),
        agora=AGORA,
        horas_periodo_atual=24,
        horas_linha_base=48,
    )

    codigos = {item["codigo"] for item in resultado["anomalias"]}

    assert "aumento_taxa_falhas" in codigos
    assert "queda_confianca_router" in codigos
    assert "degradacao_p95" in codigos
    assert "aumento_sem_tool" in codigos

    assert resultado["total_anomalias"] >= 4
    assert resultado["maior_severidade"] in {
        "alta",
        "critica",
    }

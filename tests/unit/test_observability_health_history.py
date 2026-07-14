import pandas as pd

from src.observability.health_history import (
    calcular_tendencia_health,
    preparar_snapshot,
)


def criar_resultado():
    return {
        "health": {
            "score_global": 97.8,
            "classificacao": "Excelente",
            "status": "saudavel",
            "componente_mais_forte": "memoria",
            "componente_mais_fraco": "timeline",
            "componentes": {
                "tools": {
                    "score": 97.0,
                },
                "rag": {
                    "score": 97.3,
                },
                "memoria": {
                    "score": 100.0,
                },
                "infraestrutura": {
                    "score": 100.0,
                },
                "timeline": {
                    "score": 90.7,
                },
                "performance": {
                    "score": 100.0,
                },
            },
        },
        "metricas": {
            "tools": {
                "total_eventos": 3,
            },
        },
        "anomalias": {
            "total_anomalias": 1,
        },
        "erros_coleta": [],
    }


def test_preparar_snapshot():
    snapshot = preparar_snapshot(
        criar_resultado(),
        origem="teste",
    )

    assert snapshot["score_global"] == 97.8
    assert snapshot["score_tools"] == 97.0
    assert snapshot["score_rag"] == 97.3
    assert snapshot["score_timeline"] == 90.7
    assert snapshot["total_anomalias"] == 1
    assert snapshot["origem"] == "teste"


def test_tendencia_sem_dados():
    resultado = calcular_tendencia_health(
        pd.DataFrame()
    )

    assert resultado["tem_comparacao"] is False


def test_tendencia_melhora():
    df = pd.DataFrame([
        {
            "criado_em": "2026-07-14T11:00:00Z",
            "score_global": 98.0,
        },
        {
            "criado_em": "2026-07-14T10:00:00Z",
            "score_global": 95.0,
        },
    ])

    resultado = calcular_tendencia_health(df)

    assert resultado["tem_comparacao"] is True
    assert resultado["delta"] == 3.0
    assert resultado["direcao"] == "melhora"


def test_tendencia_piora():
    df = pd.DataFrame([
        {
            "criado_em": "2026-07-14T11:00:00Z",
            "score_global": 90.0,
        },
        {
            "criado_em": "2026-07-14T10:00:00Z",
            "score_global": 95.0,
        },
    ])

    resultado = calcular_tendencia_health(df)

    assert resultado["delta"] == -5.0
    assert resultado["direcao"] == "piora"


def test_tendencia_estavel():
    df = pd.DataFrame([
        {
            "criado_em": "2026-07-14T11:00:00Z",
            "score_global": 97.8,
        },
        {
            "criado_em": "2026-07-14T10:00:00Z",
            "score_global": 97.8,
        },
    ])

    resultado = calcular_tendencia_health(df)

    assert resultado["delta"] == 0.0
    assert resultado["direcao"] == "estavel"

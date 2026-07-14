import pandas as pd

from src.dashboard_pages.tools_analytics_page import (
    formatar_delta_percentual,
    preparar_ranking_exibicao,
    render_anomalias_operacionais,
)


def test_formatar_delta_positivo():
    assert formatar_delta_percentual(
        25
    ) == "+25.00%"


def test_formatar_delta_negativo():
    assert formatar_delta_percentual(
        -10
    ) == "-10.00%"


def test_preparar_ranking_exibicao():
    ranking = pd.DataFrame([
        {
            "ferramenta": "Análise do orçamento",
            "execucoes": 10,
            "sucessos": 9,
            "falhas": 1,
            "taxa_sucesso_percentual": 90.0,
            "confianca_media_percentual": 85.0,
            "duracao_media_ms": 10.0,
            "duracao_minima_ms": 5.0,
            "duracao_maxima_ms": 20.0,
            "p50_ms": 9.0,
            "p95_ms": 18.0,
            "p99_ms": 19.6,
        }
    ])

    tabela = preparar_ranking_exibicao(
        ranking
    )

    assert "Ferramenta" in tabela.columns
    assert "P95 (ms)" in tabela.columns
    assert tabela.iloc[0]["Execuções"] == 10


def test_ranking_exibicao_vazio():
    tabela = preparar_ranking_exibicao(
        pd.DataFrame()
    )

    assert tabela.empty

def test_componente_anomalias_disponivel():
    assert callable(
        render_anomalias_operacionais
    )


import pandas as pd

from src.dashboard_pages.llm_costs_page import (
    preparar_consumo_exibicao,
    resumir_consumo_llm,
)


def criar_dataframe():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "criado_em": "2026-07-14T10:00:00Z",
                "modelo": "gemini-2.5-flash",
                "operacao": "rag_answer",
                "tokens_entrada": 1000,
                "tokens_saida": 200,
                "tokens_totais": 1200,
                "custo_entrada_usd": 0.001,
                "custo_saida_usd": 0.002,
                "custo_total_usd": 0.003,
                "duracao_ms": 5000,
                "sucesso": True,
            },
            {
                "id": 2,
                "criado_em": "2026-07-14T11:00:00Z",
                "modelo": "gemini-2.5-flash",
                "operacao": "rag_answer",
                "tokens_entrada": 500,
                "tokens_saida": 100,
                "tokens_totais": 600,
                "custo_entrada_usd": 0.0005,
                "custo_saida_usd": 0.001,
                "custo_total_usd": 0.0015,
                "duracao_ms": 10000,
                "sucesso": False,
            },
        ]
    )


def test_preparar_consumo():
    resultado = preparar_consumo_exibicao(criar_dataframe())

    assert len(resultado) == 2
    assert resultado["tokens_totais"].sum() == 1800


def test_resumir_consumo():
    resultado = resumir_consumo_llm(criar_dataframe())

    assert resultado["eventos"] == 2
    assert resultado["tokens_totais"] == 1800
    assert resultado["tokens_entrada"] == 1500
    assert resultado["tokens_saida"] == 300
    assert resultado["custo_total_usd"] == 0.0045
    assert resultado["taxa_sucesso"] == 50.0
    assert resultado["duracao_media_ms"] == 7500.0


def test_resumir_consumo_vazio():
    resultado = resumir_consumo_llm(pd.DataFrame())

    assert resultado["eventos"] == 0
    assert resultado["tokens_totais"] == 0
    assert resultado["custo_total_usd"] == 0.0

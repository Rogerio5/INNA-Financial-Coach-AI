from datetime import datetime, timezone

import pandas as pd

from src.observability.llm_finops import (
    analisar_finops_llm,
    calcular_projecao_mensal,
    classificar_orcamento,
    converter_usd_para_brl,
)


def test_converter_usd_para_brl():
    assert (
        converter_usd_para_brl(
            2.0,
            5.5,
        )
        == 11.0
    )


def test_classificar_orcamento_saudavel():
    resultado = classificar_orcamento(
        custo_atual=5,
        orcamento=10,
    )

    assert resultado["status"] == "saudavel"
    assert resultado["percentual_utilizado"] == 50.0


def test_classificar_orcamento_critico():
    resultado = classificar_orcamento(
        custo_atual=9.5,
        orcamento=10,
    )

    assert resultado["status"] == "critico"


def test_classificar_orcamento_excedido():
    resultado = classificar_orcamento(
        custo_atual=12,
        orcamento=10,
    )

    assert resultado["status"] == "excedido"
    assert resultado["saldo"] == 0.0


def test_projecao_mensal():
    resultado = calcular_projecao_mensal(
        custo_acumulado=14,
        agora=datetime(
            2026,
            7,
            14,
            tzinfo=timezone.utc,
        ),
    )

    assert resultado["media_diaria"] == 1.0
    assert resultado["projecao_mensal"] == 31.0


def test_analisar_finops():
    df = pd.DataFrame(
        [
            {
                "custo_total_usd": 0.002,
                "tokens_totais": 3000,
            },
            {
                "custo_total_usd": 0.003,
                "tokens_totais": 4000,
            },
        ]
    )

    resultado = analisar_finops_llm(
        df,
        agora=datetime(
            2026,
            7,
            14,
            tzinfo=timezone.utc,
        ),
    )

    assert resultado["total_chamadas"] == 2
    assert resultado["tokens_totais"] == 7000
    assert resultado["custo_acumulado_usd"] == 0.005

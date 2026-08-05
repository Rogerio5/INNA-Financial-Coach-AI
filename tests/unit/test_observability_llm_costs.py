from types import SimpleNamespace

from src.observability.llm_costs import (
    calcular_custo_estimado,
    extrair_tokens_resposta,
    normalizar_modelo,
)


def test_normalizar_modelo():
    assert normalizar_modelo("Gemini-2.5-Flash") == "gemini_2_5_flash"


def test_calcular_custo_estimado():
    resultado = calcular_custo_estimado(
        tokens_entrada=1_000_000,
        tokens_saida=500_000,
        preco_entrada_usd_por_1m=0.50,
        preco_saida_usd_por_1m=2.00,
    )

    assert resultado["custo_entrada_usd"] == 0.5

    assert resultado["custo_saida_usd"] == 1.0

    assert resultado["custo_total_usd"] == 1.5


def test_custo_com_tokens_negativos():
    resultado = calcular_custo_estimado(
        tokens_entrada=-100,
        tokens_saida=-50,
        preco_entrada_usd_por_1m=1,
        preco_saida_usd_por_1m=1,
    )

    assert resultado["custo_total_usd"] == 0.0


def test_extrair_tokens_objeto():
    resposta = SimpleNamespace(
        usage_metadata=SimpleNamespace(
            prompt_token_count=100,
            candidates_token_count=50,
            total_token_count=150,
        )
    )

    resultado = extrair_tokens_resposta(resposta)

    assert resultado == {
        "tokens_entrada": 100,
        "tokens_saida": 50,
        "tokens_totais": 150,
    }


def test_extrair_tokens_dicionario():
    resposta = {
        "usage_metadata": {
            "prompt_token_count": 80,
            "candidates_token_count": 20,
        }
    }

    resultado = extrair_tokens_resposta(resposta)

    assert resultado["tokens_totais"] == 100


def test_extrair_tokens_sem_metadata():
    resultado = extrair_tokens_resposta(object())

    assert resultado["tokens_totais"] == 0

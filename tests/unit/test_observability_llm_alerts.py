import pandas as pd

from src.observability.llm_alerts import (
    detectar_alertas_llm,
)


def finops_saudavel():
    return {
        "situacao_orcamento": {
            "status": "saudavel",
            "percentual_utilizado": 20,
        },
        "situacao_projecao": {
            "status": "saudavel",
        },
        "configuracao": {
            "orcamento_mensal_usd": 10,
        },
        "custo_acumulado_usd": 2,
        "projecao_mensal_usd": 3,
    }


def test_sem_alertas():
    df = pd.DataFrame(
        [
            {
                "duracao_ms": 5000,
                "tokens_totais": 2000,
                "sucesso": True,
            }
        ]
    )

    resultado = detectar_alertas_llm(
        df,
        finops_saudavel(),
    )

    assert resultado == []


def test_detectar_chamada_lenta():
    df = pd.DataFrame(
        [
            {
                "duracao_ms": 173000,
                "tokens_totais": 3000,
                "sucesso": True,
            }
        ]
    )

    resultado = detectar_alertas_llm(
        df,
        finops_saudavel(),
    )

    codigos = {item["codigo"] for item in resultado}

    assert "chamadas_lentas" in codigos


def test_detectar_falha():
    df = pd.DataFrame(
        [
            {
                "duracao_ms": 5000,
                "tokens_totais": 3000,
                "sucesso": False,
            }
        ]
    )

    resultado = detectar_alertas_llm(
        df,
        finops_saudavel(),
    )

    assert resultado[0]["codigo"] == "falhas_llm"


def test_detectar_orcamento():
    finops = finops_saudavel()

    finops["situacao_orcamento"] = {
        "status": "critico",
        "percentual_utilizado": 95,
    }

    resultado = detectar_alertas_llm(
        pd.DataFrame(),
        finops,
    )

    assert resultado[0]["codigo"] == "orcamento_mensal"


def test_detectar_tokens_elevados():
    df = pd.DataFrame(
        [
            {
                "duracao_ms": 1000,
                "tokens_totais": 15000,
                "sucesso": True,
            }
        ]
    )

    resultado = detectar_alertas_llm(
        df,
        finops_saudavel(),
    )

    codigos = {item["codigo"] for item in resultado}

    assert "tokens_elevados" in codigos

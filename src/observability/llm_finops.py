"""
FinOps de IA da INNA.

Responsabilidades:
- conversão estimada USD/BRL;
- acompanhamento de orçamento;
- projeção mensal;
- custo médio por chamada;
- classificação de consumo;
- recomendações determinísticas.

A cotação e os limites são configurados no ambiente.
"""

from __future__ import annotations

import os
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv(
        dotenv_path=Path(".env"),
        override=False,
    )
except Exception:
    pass


def _ler_float_ambiente(
    nome: str,
    padrao: float,
) -> float:
    """
    Lê número positivo do ambiente.
    """
    valor = os.getenv(
        nome,
        str(padrao),
    )

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        numero = float(padrao)

    return max(numero, 0.0)


def carregar_configuracao_finops() -> dict[str, float]:
    """
    Carrega parâmetros financeiros do ambiente.
    """
    cotacao = _ler_float_ambiente(
        "LLM_USD_BRL_RATE",
        0.0,
    )

    orcamento_usd = _ler_float_ambiente(
        "LLM_MONTHLY_BUDGET_USD",
        0.0,
    )

    orcamento_brl = _ler_float_ambiente(
        "LLM_MONTHLY_BUDGET_BRL",
        orcamento_usd * cotacao,
    )

    alerta = _ler_float_ambiente(
        "LLM_BUDGET_WARNING_PERCENT",
        70.0,
    )

    critico = _ler_float_ambiente(
        "LLM_BUDGET_CRITICAL_PERCENT",
        90.0,
    )

    return {
        "cotacao_usd_brl": cotacao,
        "orcamento_mensal_usd": orcamento_usd,
        "orcamento_mensal_brl": orcamento_brl,
        "alerta_percentual": min(
            alerta,
            100.0,
        ),
        "critico_percentual": min(
            max(critico, alerta),
            100.0,
        ),
    }


def converter_usd_para_brl(
    valor_usd: float,
    cotacao_usd_brl: float,
) -> float:
    """
    Converte custo em dólar para reais.
    """
    return round(
        max(float(valor_usd or 0), 0.0) * max(float(cotacao_usd_brl or 0), 0.0),
        8,
    )


def classificar_orcamento(
    *,
    custo_atual: float,
    orcamento: float,
    alerta_percentual: float = 70.0,
    critico_percentual: float = 90.0,
) -> dict[str, Any]:
    """
    Classifica a utilização do orçamento.
    """
    custo = max(float(custo_atual or 0), 0.0)
    limite = max(float(orcamento or 0), 0.0)

    if limite <= 0:
        return {
            "percentual_utilizado": 0.0,
            "saldo": 0.0,
            "status": "sem_orcamento",
            "classificacao": "Sem orçamento",
            "icone": "⚪",
        }

    percentual = round(
        (custo / limite) * 100,
        2,
    )

    saldo = round(
        max(limite - custo, 0.0),
        8,
    )

    if percentual >= 100:
        status = "excedido"
        classificacao = "Orçamento excedido"
        icone = "🔴"

    elif percentual >= critico_percentual:
        status = "critico"
        classificacao = "Consumo crítico"
        icone = "🔴"

    elif percentual >= alerta_percentual:
        status = "alerta"
        classificacao = "Próximo do limite"
        icone = "🟠"

    else:
        status = "saudavel"
        classificacao = "Dentro do orçamento"
        icone = "🟢"

    return {
        "percentual_utilizado": percentual,
        "saldo": saldo,
        "status": status,
        "classificacao": classificacao,
        "icone": icone,
    }


def calcular_projecao_mensal(
    *,
    custo_acumulado: float,
    agora: datetime | None = None,
) -> dict[str, float | int]:
    """
    Projeta o custo até o final do mês.

    Usa a média diária observada no mês atual.
    """
    referencia = agora or datetime.now(timezone.utc)

    dias_mes = monthrange(
        referencia.year,
        referencia.month,
    )[1]

    dia_atual = max(
        int(referencia.day),
        1,
    )

    custo = max(
        float(custo_acumulado or 0),
        0.0,
    )

    media_diaria = custo / dia_atual

    projecao = media_diaria * dias_mes

    return {
        "dia_atual": dia_atual,
        "dias_no_mes": dias_mes,
        "media_diaria": round(
            media_diaria,
            8,
        ),
        "projecao_mensal": round(
            projecao,
            8,
        ),
    }


def analisar_finops_llm(
    df: pd.DataFrame | None,
    *,
    agora: datetime | None = None,
) -> dict[str, Any]:
    """
    Consolida consumo, orçamento e projeção mensal.
    """
    configuracao = carregar_configuracao_finops()

    if df is None or df.empty:
        custo_usd = 0.0
        total_chamadas = 0
        tokens_totais = 0
    else:
        base = df.copy()

        custo_usd = float(
            pd.to_numeric(
                base.get(
                    "custo_total_usd",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        total_chamadas = len(base)

        tokens_totais = int(
            pd.to_numeric(
                base.get(
                    "tokens_totais",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

    cotacao = configuracao["cotacao_usd_brl"]

    custo_brl = converter_usd_para_brl(
        custo_usd,
        cotacao,
    )

    custo_medio_usd = custo_usd / total_chamadas if total_chamadas > 0 else 0.0

    custo_medio_brl = custo_brl / total_chamadas if total_chamadas > 0 else 0.0

    projecao_usd = calcular_projecao_mensal(
        custo_acumulado=custo_usd,
        agora=agora,
    )

    projecao_brl = converter_usd_para_brl(
        projecao_usd["projecao_mensal"],
        cotacao,
    )

    situacao_usd = classificar_orcamento(
        custo_atual=custo_usd,
        orcamento=configuracao["orcamento_mensal_usd"],
        alerta_percentual=configuracao["alerta_percentual"],
        critico_percentual=configuracao["critico_percentual"],
    )

    projecao_orcamento = classificar_orcamento(
        custo_atual=projecao_usd["projecao_mensal"],
        orcamento=configuracao["orcamento_mensal_usd"],
        alerta_percentual=configuracao["alerta_percentual"],
        critico_percentual=configuracao["critico_percentual"],
    )

    recomendacoes = []

    if projecao_orcamento["status"] in {
        "critico",
        "excedido",
    }:
        recomendacoes.append(
            "A projeção mensal está próxima ou acima do "
            "orçamento. Avalie modelos mais econômicos, "
            "redução de contexto e cache de respostas."
        )

    if total_chamadas > 0 and (tokens_totais / total_chamadas) > 10000:
        recomendacoes.append(
            "A média de tokens por chamada está elevada. "
            "Revise tamanho do prompt, chunks e histórico."
        )

    if not recomendacoes:
        recomendacoes.append(
            "O consumo está controlado. Continue acompanhando "
            "tokens por chamada e projeção mensal."
        )

    return {
        "configuracao": configuracao,
        "total_chamadas": total_chamadas,
        "tokens_totais": tokens_totais,
        "custo_acumulado_usd": round(
            custo_usd,
            8,
        ),
        "custo_acumulado_brl": round(
            custo_brl,
            8,
        ),
        "custo_medio_chamada_usd": round(
            custo_medio_usd,
            8,
        ),
        "custo_medio_chamada_brl": round(
            custo_medio_brl,
            8,
        ),
        "projecao_mensal_usd": projecao_usd["projecao_mensal"],
        "projecao_mensal_brl": projecao_brl,
        "media_diaria_usd": projecao_usd["media_diaria"],
        "situacao_orcamento": situacao_usd,
        "situacao_projecao": projecao_orcamento,
        "recomendacoes": recomendacoes,
    }


__all__ = [
    "carregar_configuracao_finops",
    "converter_usd_para_brl",
    "classificar_orcamento",
    "calcular_projecao_mensal",
    "analisar_finops_llm",
]

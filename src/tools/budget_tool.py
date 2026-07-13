"""
Ferramenta de análise básica de orçamento da INNA.

Não faz recomendação financeira.
Retorna cálculos objetivos e indicadores educativos.
"""

from __future__ import annotations

from typing import Any


def _valor_nao_negativo(valor: Any, nome: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{nome} deve ser um valor numérico."
        ) from exc

    if numero < 0:
        raise ValueError(
            f"{nome} não pode ser negativo."
        )

    return numero


def analisar_orcamento(
    renda_mensal: float,
    gastos_mensais: float,
    *,
    dividas_mensais: float = 0.0,
    gastos_incluem_dividas: bool = True,
) -> dict:
    """
    Calcula o saldo e o comprometimento da renda.

    Quando gastos_incluem_dividas=True, os gastos mensais são
    tratados como o total já comprometido no mês.

    Quando gastos_incluem_dividas=False, as parcelas de dívidas
    são acrescentadas separadamente aos gastos mensais.
    """
    renda = _valor_nao_negativo(
        renda_mensal,
        "renda_mensal",
    )

    gastos = _valor_nao_negativo(
        gastos_mensais,
        "gastos_mensais",
    )

    dividas = _valor_nao_negativo(
        dividas_mensais,
        "dividas_mensais",
    )

    incluem_dividas = bool(
        gastos_incluem_dividas
    )

    if incluem_dividas:
        parcelas_adicionais = 0.0
        despesas_totais = gastos
        base_calculo = (
            "Os gastos mensais já incluem parcelas "
            "e compromissos com dívidas."
        )
    else:
        parcelas_adicionais = dividas
        despesas_totais = gastos + dividas
        base_calculo = (
            "As parcelas de dívidas foram acrescentadas "
            "separadamente aos gastos mensais."
        )

    saldo = renda - despesas_totais

    comprometimento = (
        (despesas_totais / renda) * 100
        if renda > 0
        else 0.0
    )

    if renda == 0 and despesas_totais > 0:
        situacao = "sem_renda_informada"
    elif saldo < 0:
        situacao = "deficit"
    elif saldo == 0:
        situacao = "equilibrio_sem_margem"
    else:
        situacao = "saldo_positivo"

    return {
        "renda_mensal": round(renda, 2),
        "gastos_mensais": round(gastos, 2),
        "dividas_mensais_informadas": round(
            dividas,
            2,
        ),
        "gastos_incluem_dividas": incluem_dividas,
        "parcelas_adicionais_consideradas": round(
            parcelas_adicionais,
            2,
        ),
        "despesas_totais": round(
            despesas_totais,
            2,
        ),
        "saldo_mensal": round(saldo, 2),
        "renda_comprometida_percentual": round(
            comprometimento,
            2,
        ),
        "situacao": situacao,
        "tem_saldo_positivo": saldo > 0,
        "base_calculo": base_calculo,
    }


__all__ = [
    "analisar_orcamento",
]

"""
Simulações financeiras determinísticas da INNA.
"""

from __future__ import annotations

import math
from typing import Any


def _numero(valor: Any, nome: str) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{nome} deve ser numérico.") from exc


def simular_parcelamento_sem_juros(
    valor_total: float,
    quantidade_parcelas: int,
) -> dict:
    total = _numero(
        valor_total,
        "valor_total",
    )

    parcelas = int(quantidade_parcelas)

    if total < 0:
        raise ValueError("valor_total não pode ser negativo.")

    if parcelas <= 0:
        raise ValueError("quantidade_parcelas deve ser maior que zero.")

    valor_parcela = total / parcelas

    return {
        "valor_total": round(total, 2),
        "quantidade_parcelas": parcelas,
        "valor_parcela": round(
            valor_parcela,
            2,
        ),
        "possui_juros": False,
    }


def simular_meta_por_aporte(
    meta_total: float,
    aporte_mensal: float,
    *,
    saldo_inicial: float = 0.0,
) -> dict:
    meta = _numero(
        meta_total,
        "meta_total",
    )

    aporte = _numero(
        aporte_mensal,
        "aporte_mensal",
    )

    inicial = _numero(
        saldo_inicial,
        "saldo_inicial",
    )

    if meta < 0 or aporte < 0 or inicial < 0:
        raise ValueError("Os valores não podem ser negativos.")

    restante = max(
        meta - inicial,
        0.0,
    )

    if restante == 0:
        meses = 0
    elif aporte == 0:
        meses = None
    else:
        meses = math.ceil(restante / aporte)

    return {
        "meta_total": round(meta, 2),
        "saldo_inicial": round(inicial, 2),
        "aporte_mensal": round(aporte, 2),
        "valor_restante": round(restante, 2),
        "meses_estimados": meses,
        "considera_rendimento": False,
    }


__all__ = [
    "simular_parcelamento_sem_juros",
    "simular_meta_por_aporte",
]

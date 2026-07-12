"""
Ferramentas educativas relacionadas à reserva financeira.
"""

from __future__ import annotations

import math
from typing import Any


def _valor_nao_negativo(valor: Any, nome: str) -> float:
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{nome} deve ser numérico."
        ) from exc

    if numero < 0:
        raise ValueError(
            f"{nome} não pode ser negativo."
        )

    return numero


def calcular_capacidade_semanal(
    valor_mensal: float,
    *,
    semanas_por_mes: float = 4.0,
) -> dict:
    """
    Converte uma capacidade mensal em referência semanal.
    """
    mensal = _valor_nao_negativo(
        valor_mensal,
        "valor_mensal",
    )

    semanas = float(semanas_por_mes)

    if semanas <= 0:
        raise ValueError(
            "semanas_por_mes deve ser maior que zero."
        )

    semanal = mensal / semanas

    return {
        "valor_mensal": round(mensal, 2),
        "semanas_por_mes": semanas,
        "valor_semanal_estimado": round(
            semanal,
            2,
        ),
    }


def simular_formacao_reserva(
    valor_mensal: float,
    meta_total: float,
    *,
    valor_inicial: float = 0.0,
) -> dict:
    """
    Estima o tempo para atingir uma meta sem considerar rendimento.
    """
    mensal = _valor_nao_negativo(
        valor_mensal,
        "valor_mensal",
    )

    meta = _valor_nao_negativo(
        meta_total,
        "meta_total",
    )

    inicial = _valor_nao_negativo(
        valor_inicial,
        "valor_inicial",
    )

    restante = max(meta - inicial, 0.0)

    if restante == 0:
        meses = 0
        status = "meta_atingida"
    elif mensal == 0:
        meses = None
        status = "sem_aporte_mensal"
    else:
        meses = math.ceil(restante / mensal)
        status = "estimativa_disponivel"

    return {
        "meta_total": round(meta, 2),
        "valor_inicial": round(inicial, 2),
        "valor_restante": round(restante, 2),
        "valor_mensal": round(mensal, 2),
        "meses_estimados": meses,
        "status": status,
        "considera_rendimento": False,
    }


__all__ = [
    "calcular_capacidade_semanal",
    "simular_formacao_reserva",
]

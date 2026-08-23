"""
Cálculo da evolução financeira da memória da INNA.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def copiar_memoria(memoria: dict | None) -> dict:
    """
    Preserva o estado anterior para comparação.
    """
    if memoria is None:
        return {}

    return deepcopy(memoria)


def _para_float(valor: Any):
    if valor is None:
        return None

    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def calcular_evolucao_memoria(
    memoria_anterior: dict | None,
    memoria_nova: dict | None,
) -> dict:
    """
    Compara a memória anterior e a nova memória.

    Campos analisados:
    - renda mensal;
    - gastos mensais;
    - capacidade de guardar.
    """
    memoria_anterior = memoria_anterior or {}
    memoria_nova = memoria_nova or {}

    campos = {
        "renda_mensal": "Renda mensal",
        "gastos_mensais": "Gastos mensais",
        "valor_reserva": "Capacidade de guardar",
    }

    evolucoes = []

    for campo, label in campos.items():
        antes = _para_float(
            memoria_anterior.get(campo)
        )

        depois = _para_float(
            memoria_nova.get(campo)
        )

        if antes is None or depois is None:
            continue

        diferenca = depois - antes

        if abs(diferenca) < 0.000001:
            continue

        percentual = None

        if antes != 0:
            percentual = (diferenca / antes) * 100

        evolucoes.append({
            "campo": campo,
            "label": label,
            "antes": antes,
            "depois": depois,
            "diferenca": diferenca,
            "percentual": percentual,
            "tipo": (
                "aumento"
                if diferenca > 0
                else "redução"
            ),
        })

    if not evolucoes:
        return {
            "tem_evolucao": False,
            "resumo": "Nenhuma evolução financeira detectada.",
            "evolucoes": [],
        }

    partes = []

    for item in evolucoes:
        sinal = "+" if item["diferenca"] > 0 else ""

        partes.append(
            f'{item["label"]}: '
            f'{item["antes"]:.2f} -> '
            f'{item["depois"]:.2f} '
            f'({sinal}{item["diferenca"]:.2f})'
        )

    return {
        "tem_evolucao": True,
        "resumo": "; ".join(partes),
        "evolucoes": evolucoes,
    }

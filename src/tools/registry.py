"""
Registro central das ferramentas da INNA.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .budget_tool import (
    analisar_orcamento,
)
from .debt_tool import (
    analisar_divida_educativamente,
)
from .reserve_tool import (
    calcular_capacidade_semanal,
    simular_formacao_reserva,
)
from .simulation_tool import (
    simular_meta_por_aporte,
    simular_parcelamento_sem_juros,
)


TOOLS: dict[str, Callable[..., dict]] = {
    "analisar_orcamento": analisar_orcamento,
    "calcular_capacidade_semanal": calcular_capacidade_semanal,
    "simular_formacao_reserva": simular_formacao_reserva,
    "analisar_divida_educativamente": analisar_divida_educativamente,
    "simular_parcelamento_sem_juros": simular_parcelamento_sem_juros,
    "simular_meta_por_aporte": simular_meta_por_aporte,
}


TOOL_LABELS = {
    "analisar_orcamento": "Análise do orçamento mensal",
    "calcular_capacidade_semanal": "Cálculo de capacidade semanal",
    "simular_formacao_reserva": "Simulação de formação de reserva",
    "analisar_divida_educativamente": "Análise educativa de dívida",
    "simular_parcelamento_sem_juros": "Simulação de parcelamento sem juros",
    "simular_meta_por_aporte": "Simulação de meta por aporte",
}


TOOL_DESCRIPTIONS = {
    "analisar_orcamento": (
        "Calcula despesas totais, saldo mensal e percentual "
        "de comprometimento da renda."
    ),
    "calcular_capacidade_semanal": (
        "Converte um valor mensal em referência semanal."
    ),
    "simular_formacao_reserva": (
        "Estima quantos meses seriam necessários para atingir "
        "uma meta sem considerar rendimento."
    ),
    "analisar_divida_educativamente": (
        "Organiza dados de uma dívida, identifica informações "
        "ausentes e apresenta critérios educativos."
    ),
    "simular_parcelamento_sem_juros": (
        "Calcula o valor de parcelas iguais sem juros."
    ),
    "simular_meta_por_aporte": (
        "Estima o tempo para alcançar uma meta com aportes mensais."
    ),
}


def listar_tools() -> list[dict[str, str]]:
    return [
        {
            "nome": nome,
            "label": TOOL_LABELS.get(
                nome,
                nome,
            ),
            "descricao": TOOL_DESCRIPTIONS.get(
                nome,
                "",
            ),
        }
        for nome in sorted(TOOLS)
    ]


def executar_tool(
    nome: str,
    argumentos: dict[str, Any] | None = None,
) -> dict:
    """
    Executa uma ferramenta registrada.
    """
    if nome not in TOOLS:
        return {
            "ok": False,
            "tool": nome,
            "message": "Ferramenta não encontrada.",
            "resultado": None,
        }

    argumentos = argumentos or {}

    try:
        resultado = TOOLS[nome](
            **argumentos
        )

        return {
            "ok": True,
            "tool": nome,
            "message": "Ferramenta executada com sucesso.",
            "resultado": resultado,
        }

    except Exception as exc:
        return {
            "ok": False,
            "tool": nome,
            "message": str(exc),
            "resultado": None,
        }


__all__ = [
    "TOOLS",
    "TOOL_LABELS",
    "TOOL_DESCRIPTIONS",
    "listar_tools",
    "executar_tool",
]

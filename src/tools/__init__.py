"""
Ferramentas financeiras determinísticas da INNA.
"""

from src.tools.budget_tool import analisar_orcamento
from src.tools.debt_tool import analisar_divida_educativamente
from src.tools.registry import executar_tool, listar_tools
from src.tools.reserve_tool import (
    calcular_capacidade_semanal,
    simular_formacao_reserva,
)
from src.tools.router import (
    identificar_intencao_tool,
    montar_argumentos_tool,
    normalizar_texto,
    rotear_tool,
)
from src.tools.simulation_tool import (
    simular_meta_por_aporte,
    simular_parcelamento_sem_juros,
)

__all__ = [
    "analisar_orcamento",
    "analisar_divida_educativamente",
    "calcular_capacidade_semanal",
    "simular_formacao_reserva",
    "simular_meta_por_aporte",
    "simular_parcelamento_sem_juros",
    "executar_tool",
    "listar_tools",
    "rotear_tool",
    "montar_argumentos_tool",
    "identificar_intencao_tool",
    "normalizar_texto",
]

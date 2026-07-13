"""
Ferramentas financeiras determinísticas da INNA.
"""

from .budget_tool import analisar_orcamento
from .debt_tool import analisar_divida_educativamente
from .registry import executar_tool, listar_tools
from .reserve_tool import (
    calcular_capacidade_semanal,
    simular_formacao_reserva,
)
from .orchestrator import (
    executar_tools_para_pergunta,
    montar_bloco_tools_prompt,
    preparar_contexto_memoria_tools,
    processar_pergunta_com_tools,
)
from .router import (
    identificar_intencao_tool,
    montar_argumentos_tool,
    normalizar_texto,
    rotear_tool,
)
from .simulation_tool import (
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
    "processar_pergunta_com_tools",
    "montar_bloco_tools_prompt",
    "executar_tools_para_pergunta",
    "preparar_contexto_memoria_tools",
    "rotear_tool",
    "montar_argumentos_tool",
    "identificar_intencao_tool",
    "normalizar_texto",
]

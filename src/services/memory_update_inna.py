"""
Adaptador de compatibilidade da memória da INNA.

As implementações reais foram movidas para:

- services.memory.extractor
- services.memory.evolution
"""

try:
    from services.memory.extractor import (
        normalizar_valor_financeiro,
        extrair_memoria_da_mensagem_inna,
        mesclar_memoria_existente,
    )
    from services.memory.evolution import (
        copiar_memoria,
        calcular_evolucao_memoria,
    )
except ImportError:
    from src.services.memory.extractor import (
        normalizar_valor_financeiro,
        extrair_memoria_da_mensagem_inna,
        mesclar_memoria_existente,
    )
    from src.services.memory.evolution import (
        copiar_memoria,
        calcular_evolucao_memoria,
    )


_normalizar_valor = normalizar_valor_financeiro


__all__ = [
    "normalizar_valor_financeiro",
    "_normalizar_valor",
    "extrair_memoria_da_mensagem_inna",
    "mesclar_memoria_existente",
    "copiar_memoria",
    "calcular_evolucao_memoria",
]

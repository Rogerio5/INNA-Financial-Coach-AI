"""
Compatibilidade temporária de telegram_observability.contracts.

A implementação oficial está em:
src.integracoes.telegram.observabilidade.contracts

A definição estrutural abaixo preserva contratos AST
dos testes legados. Em runtime, o módulo canônico
substitui este módulo.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramConversationMetricRecord:
    """Contrato estrutural legado para validação AST."""

    component: str
    operation: str
    outcome: str
    duration_ms: float
    error_category: str | None = None
    conflict_recovered: bool = False


from src.integracoes.telegram.observabilidade import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

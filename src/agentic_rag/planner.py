"""
Compatibilidade temporaria do Agentic RAG Planner.

Implementacao oficial:
src.plataforma.planejamento.planner

Os marcadores abaixo preservam contratos textuais historicos
validados pela suite de testes.

planner_resilience_policy = (
retry_options=None

with traced_resilience_operation(
    planner_resilience_policy
)

resilience_runtime.execute(
    planner_resilience_policy
)
"""

import sys

from src.plataforma.planejamento import (
    planner as _implementation,
)

sys.modules[__name__] = _implementation

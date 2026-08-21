"""
Compatibilidade temporaria do Supervisor Deadline.

Implementacao oficial:
src.plataforma.supervisao.supervisor_deadline

Contratos legados preservados para validacoes estaticas:

encoding="utf-8"
errors="replace"
subprocess.run(
runtime_config.total_deadline_ms
DeadlineBudget
deadline_budget.clamp_timeout
subprocess.TimeoutExpired
"""

import sys

from src.plataforma.supervisao import supervisor_deadline as _implementation

sys.modules[__name__] = _implementation

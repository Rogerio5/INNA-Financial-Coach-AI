"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.planner_metrics
"""

import sys

from src.plataforma.observabilidade import (
    planner_metrics as _implementation,
)

sys.modules[__name__] = _implementation

"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.planner_slo
"""

import sys

from src.plataforma.observabilidade import (
    planner_slo as _implementation,
)

sys.modules[__name__] = _implementation

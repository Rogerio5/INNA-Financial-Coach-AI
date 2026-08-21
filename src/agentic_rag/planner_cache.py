"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.planejamento.planner_cache
"""

import sys

from src.plataforma.planejamento import (
    planner_cache as _implementation,
)

sys.modules[__name__] = _implementation

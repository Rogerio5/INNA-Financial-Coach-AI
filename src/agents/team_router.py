"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.roteamento.team_router
"""

import sys

from src.plataforma.roteamento import team_router as _implementation

sys.modules[__name__] = _implementation

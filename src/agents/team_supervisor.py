"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.roteamento.team_supervisor
"""

import sys

from src.plataforma.roteamento import team_supervisor as _implementation

sys.modules[__name__] = _implementation

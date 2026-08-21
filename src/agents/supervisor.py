"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.supervisor
"""

import sys

from src.plataforma.supervisao import supervisor as _implementation

sys.modules[__name__] = _implementation

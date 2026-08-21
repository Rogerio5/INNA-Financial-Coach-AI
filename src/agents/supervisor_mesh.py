"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.supervisor_mesh
"""

import sys

from src.plataforma.supervisao import supervisor_mesh as _implementation

sys.modules[__name__] = _implementation

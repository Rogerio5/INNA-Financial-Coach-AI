"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.supervisor_mesh_node
"""

import sys

from src.plataforma.supervisao import supervisor_mesh_node as _implementation

sys.modules[__name__] = _implementation

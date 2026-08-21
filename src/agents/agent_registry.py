"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.registro.agent_registry
"""

import sys

from src.plataforma.registro import agent_registry as _implementation

sys.modules[__name__] = _implementation

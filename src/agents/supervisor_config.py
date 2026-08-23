"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.supervisao.supervisor_config
"""

import sys

from src.plataforma.supervisao import supervisor_config as _implementation

sys.modules[__name__] = _implementation

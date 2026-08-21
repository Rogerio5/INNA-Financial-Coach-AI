"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.health
"""

import sys

from src.plataforma.observabilidade import (
    health as _implementation,
)

sys.modules[__name__] = _implementation

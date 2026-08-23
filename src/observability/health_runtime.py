"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.health_runtime
"""

import sys

from src.plataforma.observabilidade import (
    health_runtime as _implementation,
)

sys.modules[__name__] = _implementation

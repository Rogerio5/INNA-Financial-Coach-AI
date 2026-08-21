"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.neon_runtime
"""

import sys

from src.plataforma.observabilidade import (
    neon_runtime as _implementation,
)

sys.modules[__name__] = _implementation

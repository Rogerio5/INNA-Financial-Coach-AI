"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.metrics
"""

import sys

from src.plataforma.observabilidade import (
    metrics as _implementation,
)

sys.modules[__name__] = _implementation

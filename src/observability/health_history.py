"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.health_history
"""

import sys

from src.plataforma.observabilidade import (
    health_history as _implementation,
)

sys.modules[__name__] = _implementation

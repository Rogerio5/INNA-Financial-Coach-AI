"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.infrastructure_health
"""

import sys

from src.plataforma.observabilidade import (
    infrastructure_health as _implementation,
)

sys.modules[__name__] = _implementation

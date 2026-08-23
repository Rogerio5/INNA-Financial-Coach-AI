"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.analytics
"""

import sys

from src.plataforma.observabilidade import (
    analytics as _implementation,
)

sys.modules[__name__] = _implementation

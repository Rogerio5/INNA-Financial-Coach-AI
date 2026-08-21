"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.narrative
"""

import sys

from src.plataforma.observabilidade import (
    narrative as _implementation,
)

sys.modules[__name__] = _implementation

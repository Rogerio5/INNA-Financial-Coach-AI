"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.observabilidade.timeline
"""

import sys

from src.plataforma.observabilidade import (
    timeline as _implementation,
)

sys.modules[__name__] = _implementation

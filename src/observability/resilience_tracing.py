"""
Compatibilidade temporaria.

Implementacao oficial:
src.resilience.tracing
"""

import sys

from src.resilience import tracing as _implementation

sys.modules[__name__] = _implementation

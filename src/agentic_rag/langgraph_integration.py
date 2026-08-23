"""
Compatibilidade temporaria.

Implementacao oficial:
src.plataforma.gateway.agentic_rag
"""

import sys

from src.plataforma.gateway import (
    agentic_rag as _implementation,
)

sys.modules[__name__] = _implementation

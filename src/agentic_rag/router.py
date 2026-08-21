"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.router
"""

import sys

from src.compartilhado.rag.agentic import (
    router as _implementation,
)

sys.modules[__name__] = _implementation

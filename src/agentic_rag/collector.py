"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.collector
"""

import sys

from src.compartilhado.rag.agentic import (
    collector as _implementation,
)

sys.modules[__name__] = _implementation

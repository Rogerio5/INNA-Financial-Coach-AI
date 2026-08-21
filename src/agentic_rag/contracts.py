"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.contracts
"""

import sys

from src.compartilhado.rag.agentic import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.sufficiency
"""

import sys

from src.compartilhado.rag.agentic import (
    sufficiency as _implementation,
)

sys.modules[__name__] = _implementation

"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.evidence
"""

import sys

from src.compartilhado.rag.agentic import (
    evidence as _implementation,
)

sys.modules[__name__] = _implementation

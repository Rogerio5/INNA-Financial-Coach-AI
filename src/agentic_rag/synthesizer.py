"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.agentic.synthesizer
"""

import sys

from src.compartilhado.rag.agentic import (
    synthesizer as _implementation,
)

sys.modules[__name__] = _implementation

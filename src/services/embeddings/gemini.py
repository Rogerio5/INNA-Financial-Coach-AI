"""Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.embeddings.gemini
"""

import sys

from src.compartilhado.rag.embeddings import (
    gemini as _implementation,
)

sys.modules[__name__] = _implementation

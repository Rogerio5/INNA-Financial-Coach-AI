"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.chunking
"""

import sys

from src.compartilhado.rag import chunking as _implementation

sys.modules[__name__] = _implementation

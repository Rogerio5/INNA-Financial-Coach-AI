"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.retrieval
"""

import sys

from src.compartilhado.rag import retrieval as _implementation

sys.modules[__name__] = _implementation

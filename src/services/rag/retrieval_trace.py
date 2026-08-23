"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.retrieval_trace
"""

import sys

from src.compartilhado.rag import retrieval_trace as _implementation

sys.modules[__name__] = _implementation

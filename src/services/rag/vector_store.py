"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.persistencia.vector_store
"""

import sys

from src.compartilhado.rag.persistencia import vector_store as _implementation

sys.modules[__name__] = _implementation

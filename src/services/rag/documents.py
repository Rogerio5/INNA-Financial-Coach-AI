"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.documents
"""

import sys

from src.compartilhado.rag import documents as _implementation

sys.modules[__name__] = _implementation

"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.auto_merging
"""

import sys

from src.compartilhado.rag import auto_merging as _implementation

sys.modules[__name__] = _implementation

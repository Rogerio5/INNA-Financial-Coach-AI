"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.security
"""

import sys

from src.compartilhado.rag import security as _implementation

sys.modules[__name__] = _implementation

"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.versioning
"""

import sys

from src.compartilhado.rag import versioning as _implementation

sys.modules[__name__] = _implementation

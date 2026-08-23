"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.sentence_window
"""

import sys

from src.compartilhado.rag import sentence_window as _implementation

sys.modules[__name__] = _implementation

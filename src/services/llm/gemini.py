"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.llm.gemini
"""

import sys

from src.compartilhado.llm import gemini as _implementation

sys.modules[__name__] = _implementation

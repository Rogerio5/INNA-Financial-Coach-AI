"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.llm.model_registry
"""

import sys

from src.compartilhado.llm import model_registry as _implementation

sys.modules[__name__] = _implementation

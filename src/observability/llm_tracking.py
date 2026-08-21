"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.llm.tracking
"""

import sys

from src.compartilhado.observabilidade.llm import (
    tracking as _implementation,
)

sys.modules[__name__] = _implementation

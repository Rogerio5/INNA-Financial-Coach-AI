"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.llm.costs
"""

import sys

from src.compartilhado.observabilidade.llm import (
    costs as _implementation,
)

sys.modules[__name__] = _implementation

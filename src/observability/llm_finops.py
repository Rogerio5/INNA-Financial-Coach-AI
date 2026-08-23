"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.llm.finops
"""

import sys

from src.compartilhado.observabilidade.llm import (
    finops as _implementation,
)

sys.modules[__name__] = _implementation

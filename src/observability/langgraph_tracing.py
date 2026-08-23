"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.observabilidade.langgraph_tracing
"""

import sys

from src.compartilhado.observabilidade import (
    langgraph_tracing as _implementation,
)

sys.modules[__name__] = _implementation

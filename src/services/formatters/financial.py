"""Compatibilidade temporaria.

Implementacao oficial:
src.modulos.financeiro.nucleo.formatters
"""

import sys

from src.modulos.financeiro.nucleo import (
    formatters as _implementation,
)

sys.modules[__name__] = _implementation

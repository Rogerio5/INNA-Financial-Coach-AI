"""
Compatibilidade temporaria.

Implementacao oficial:
src.modulos.financeiro.nucleo.financial_semantic_memory
"""

import sys

from src.modulos.financeiro.nucleo import financial_semantic_memory as _implementation

sys.modules[__name__] = _implementation

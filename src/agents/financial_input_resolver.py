"""
Compatibilidade temporaria.

Implementacao oficial:
src.modulos.financeiro.nucleo.financial_input_resolver
"""

import sys

from src.modulos.financeiro.nucleo import financial_input_resolver as _implementation

sys.modules[__name__] = _implementation

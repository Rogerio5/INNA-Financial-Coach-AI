"""
Compatibilidade temporaria.

O modulo foi migrado para:
src.modulos.financeiro.nucleo.financial_history_flow

Este arquivo mantem o caminho legado apontando para
o mesmo objeto de modulo, preservando monkeypatches,
testes e imports existentes.
"""

import sys

from src.modulos.financeiro.nucleo import financial_history_flow as _implementation

sys.modules[__name__] = _implementation

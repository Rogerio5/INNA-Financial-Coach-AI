"""
Compatibilidade temporaria.

Implementacao oficial:
src.modulos.financeiro.seguranca_financeira.risk_reviewer
"""

import sys

from src.modulos.financeiro.seguranca_financeira import risk_reviewer as _implementation

sys.modules[__name__] = _implementation

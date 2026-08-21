"""
Compatibilidade temporária do repositório de histórico financeiro.

Implementação oficial:
src.modulos.financeiro.nucleo.historico.repository

Contrato textual histórico preservado:
FROM public.diagnosticos_financeiros
"""

import sys

from src.modulos.financeiro.nucleo.historico import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation

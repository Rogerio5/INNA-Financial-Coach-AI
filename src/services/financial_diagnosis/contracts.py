"""Compatibilidade temporária para contracts do diagnóstico financeiro."""

import sys

from src.modulos.financeiro.nucleo.diagnostico import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para service do diagnóstico financeiro."""

import sys

from src.modulos.financeiro.nucleo.diagnostico import (
    service as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para repository do diagnóstico financeiro."""

import sys

from src.modulos.financeiro.nucleo.diagnostico import (
    repository as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para src.agents.report_flow."""

import sys

from src.modulos.financeiro.nucleo import (
    report_flow as _implementation,
)

sys.modules[__name__] = _implementation

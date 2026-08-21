"""Compatibilidade temporaria para src.agent_tools.financial_tools."""

import sys

from src.compartilhado.agent_tools import (
    financial_tools as _implementation,
)

sys.modules[__name__] = _implementation

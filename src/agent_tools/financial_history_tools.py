"""Compatibilidade temporaria para src.agent_tools.financial_history_tools."""

import sys

from src.compartilhado.agent_tools import (
    financial_history_tools as _implementation,
)

sys.modules[__name__] = _implementation

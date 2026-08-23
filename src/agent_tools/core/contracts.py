"""Compatibilidade temporaria para src.agent_tools.core.contracts."""

import sys

from src.compartilhado.agent_tools.core import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

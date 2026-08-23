"""Compatibilidade temporaria para src.agent_tools.communication_tools."""

import sys

from src.compartilhado.agent_tools import (
    communication_tools as _implementation,
)

sys.modules[__name__] = _implementation

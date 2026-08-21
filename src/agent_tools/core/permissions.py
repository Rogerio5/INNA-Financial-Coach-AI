"""Compatibilidade temporaria para src.agent_tools.core.permissions."""

import sys

from src.compartilhado.agent_tools.core import (
    permissions as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporaria para src.agent_tools.core.registry."""

import sys

from src.compartilhado.agent_tools.core import (
    registry as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para src.agents.handoff_coordinator_node."""

import sys

from src.plataforma.supervisao import (
    handoff_coordinator_node as _implementation,
)

sys.modules[__name__] = _implementation

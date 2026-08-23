"""Compatibilidade temporária para src.agents.handoff."""

import sys

from src.plataforma.supervisao import (
    handoff as _implementation,
)

sys.modules[__name__] = _implementation

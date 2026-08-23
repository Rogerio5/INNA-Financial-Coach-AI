"""Compatibilidade temporária para src.agents.state."""

import sys

from src.plataforma.orquestracao import (
    state as _implementation,
)

sys.modules[__name__] = _implementation

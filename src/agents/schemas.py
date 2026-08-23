"""Compatibilidade temporária para src.agents.schemas."""

import sys

from src.plataforma.orquestracao import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

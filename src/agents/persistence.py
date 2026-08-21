"""Compatibilidade temporária para src.agents.persistence."""

import sys

from src.compartilhado.memoria import (
    checkpoint as _implementation,
)

sys.modules[__name__] = _implementation

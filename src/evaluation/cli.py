"""Compatibilidade temporária para src.evaluation.cli."""

import sys

from src.interfaces.avaliacao import (
    cli as _implementation,
)

sys.modules[__name__] = _implementation

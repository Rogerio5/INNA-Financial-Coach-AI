"""Compatibilidade temporária para src.evaluation.dashboard."""

import sys

from src.interfaces.avaliacao import (
    dashboard as _implementation,
)

sys.modules[__name__] = _implementation

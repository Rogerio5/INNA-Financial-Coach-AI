"""Compatibilidade temporária para src.evaluation.adapters."""

import sys

from src.compartilhado.avaliacao import (
    adapters as _implementation,
)

sys.modules[__name__] = _implementation

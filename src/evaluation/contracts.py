"""Compatibilidade temporária para src.evaluation.contracts."""

import sys

from src.compartilhado.avaliacao import (
    contracts as _implementation,
)

sys.modules[__name__] = _implementation

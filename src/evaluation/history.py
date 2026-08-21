"""Compatibilidade temporária para src.evaluation.history."""

import sys

from src.compartilhado.avaliacao import (
    history as _implementation,
)

sys.modules[__name__] = _implementation

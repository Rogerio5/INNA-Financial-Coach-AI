"""Compatibilidade temporária para src.evaluation.baseline."""

import sys

from src.compartilhado.avaliacao import (
    baseline as _implementation,
)

sys.modules[__name__] = _implementation

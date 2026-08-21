"""Compatibilidade temporária para src.evaluation.comparison."""

import sys

from src.compartilhado.avaliacao import (
    comparison as _implementation,
)

sys.modules[__name__] = _implementation

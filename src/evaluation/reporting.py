"""Compatibilidade temporária para src.evaluation.reporting."""

import sys

from src.compartilhado.avaliacao import (
    reporting as _implementation,
)

sys.modules[__name__] = _implementation

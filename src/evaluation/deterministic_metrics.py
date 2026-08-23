"""Compatibilidade temporária para src.evaluation.deterministic_metrics."""

import sys

from src.compartilhado.avaliacao import (
    deterministic_metrics as _implementation,
)

sys.modules[__name__] = _implementation

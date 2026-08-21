"""Compatibilidade temporária para src.evaluation.deepeval_metrics."""

import sys

from src.compartilhado.avaliacao import (
    deepeval_metrics as _implementation,
)

sys.modules[__name__] = _implementation

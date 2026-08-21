"""Compatibilidade temporária para src.evaluation.final_regression.runner."""

import sys

from src.compartilhado.avaliacao.final_regression import (
    runner as _implementation,
)

sys.modules[__name__] = _implementation

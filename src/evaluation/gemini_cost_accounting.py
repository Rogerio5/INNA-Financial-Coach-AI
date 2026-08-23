"""Compatibilidade temporária para src.evaluation.gemini_cost_accounting."""

import sys

from src.compartilhado.avaliacao import (
    gemini_cost_accounting as _implementation,
)

sys.modules[__name__] = _implementation

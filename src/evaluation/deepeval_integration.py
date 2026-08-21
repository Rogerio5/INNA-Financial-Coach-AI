"""Compatibilidade temporária para src.evaluation.deepeval_integration."""

import sys

from src.compartilhado.avaliacao import (
    deepeval_integration as _implementation,
)

sys.modules[__name__] = _implementation

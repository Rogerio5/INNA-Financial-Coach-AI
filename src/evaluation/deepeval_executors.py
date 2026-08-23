"""Compatibilidade temporária para src.evaluation.deepeval_executors."""

import sys

from src.compartilhado.avaliacao import (
    deepeval_executors as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para src.evaluation.deepeval_runner."""

import sys

from src.compartilhado.avaliacao import (
    deepeval_runner as _implementation,
)

sys.modules[__name__] = _implementation

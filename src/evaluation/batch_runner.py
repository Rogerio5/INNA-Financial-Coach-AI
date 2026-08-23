"""Compatibilidade temporária para src.evaluation.batch_runner."""

import sys

from src.compartilhado.avaliacao import (
    batch_runner as _implementation,
)

sys.modules[__name__] = _implementation

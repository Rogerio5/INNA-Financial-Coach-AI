"""Compatibilidade temporária para src.evaluation.deterministic_executors."""

import sys

from src.compartilhado.avaliacao import (
    deterministic_executors as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para src.evaluation.datasets."""

import sys

from src.compartilhado.avaliacao import (
    datasets as _implementation,
)

sys.modules[__name__] = _implementation

"""Compatibilidade temporária para src.evaluation.quality_gate."""

import sys

from src.compartilhado.avaliacao import (
    quality_gate as _implementation,
)

sys.modules[__name__] = _implementation

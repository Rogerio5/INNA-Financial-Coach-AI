"""Compatibilidade temporária para src.evaluation.rag_lab_comparison."""

import sys

from src.compartilhado.avaliacao import (
    rag_lab_comparison as _implementation,
)

sys.modules[__name__] = _implementation

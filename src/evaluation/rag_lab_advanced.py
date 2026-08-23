"""Compatibilidade temporária para src.evaluation.rag_lab_advanced."""

import sys

from src.compartilhado.avaliacao import (
    rag_lab_advanced as _implementation,
)

sys.modules[__name__] = _implementation

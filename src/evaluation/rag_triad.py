"""Compatibilidade temporária para src.evaluation.rag_triad."""

import sys

from src.compartilhado.avaliacao import (
    rag_triad as _implementation,
)

sys.modules[__name__] = _implementation

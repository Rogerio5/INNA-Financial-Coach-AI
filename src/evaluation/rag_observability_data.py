"""Compatibilidade temporária para src.evaluation.rag_observability_data."""

import sys

from src.compartilhado.avaliacao import (
    rag_observability_data as _implementation,
)

sys.modules[__name__] = _implementation

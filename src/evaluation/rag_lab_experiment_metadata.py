"""Compatibilidade temporária para src.evaluation.rag_lab_experiment_metadata."""

import sys

from src.compartilhado.avaliacao import (
    rag_lab_experiment_metadata as _implementation,
)

sys.modules[__name__] = _implementation

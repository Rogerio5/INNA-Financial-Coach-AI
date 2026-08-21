"""Compatibilidade temporária para src.evaluation.rag_lab_dashboard_data."""

import sys

from src.compartilhado.avaliacao import (
    rag_lab_dashboard_data as _implementation,
)

sys.modules[__name__] = _implementation

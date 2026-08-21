"""Compatibilidade temporária para src.evaluation.dashboard_data."""

import sys

from src.compartilhado.avaliacao import (
    dashboard_data as _implementation,
)

sys.modules[__name__] = _implementation

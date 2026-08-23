"""Compatibilidade temporária para src.evaluation.offline_dashboard.data."""

import sys

from src.interfaces.avaliacao.offline_dashboard import (
    data as _implementation,
)

sys.modules[__name__] = _implementation

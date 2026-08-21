"""Compatibilidade temporária para src.evaluation.offline_dashboard.app."""

import sys

from src.interfaces.avaliacao.offline_dashboard import (
    app as _implementation,
)

sys.modules[__name__] = _implementation

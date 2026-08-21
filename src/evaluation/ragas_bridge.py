"""Compatibilidade temporária para src.evaluation.ragas_bridge."""

import sys

from src.compartilhado.avaliacao import (
    ragas_bridge as _implementation,
)

sys.modules[__name__] = _implementation

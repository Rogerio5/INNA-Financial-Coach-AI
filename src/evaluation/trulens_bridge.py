"""Compatibilidade temporária para src.evaluation.trulens_bridge."""

import sys

from src.compartilhado.avaliacao import (
    trulens_bridge as _implementation,
)

sys.modules[__name__] = _implementation

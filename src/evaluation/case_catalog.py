"""Compatibilidade temporária para src.evaluation.case_catalog."""

import sys

from src.compartilhado.avaliacao import (
    case_catalog as _implementation,
)

sys.modules[__name__] = _implementation

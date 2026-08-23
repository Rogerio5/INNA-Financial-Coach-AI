"""Compatibilidade temporária para src.evaluation.privacy."""

import sys

from src.compartilhado.avaliacao import (
    privacy as _implementation,
)

sys.modules[__name__] = _implementation

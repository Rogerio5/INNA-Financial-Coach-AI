"""Compatibilidade temporaria para src.resilience.classification."""

import sys

from src.compartilhado.resilience import (
    classification as _implementation,
)

sys.modules[__name__] = _implementation
